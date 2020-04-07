from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
import picamera, time, cv2, threading


import numpy
from PIL import Image, ImageDraw, ImageFont

import subprocess

from flask_opencv_streamer.streamer import Streamer

magnification_levels = {
    1: [(0.05, 0.05, 0.9, 0.9),0.01,'1.1x'],
    2: [(0.25, 0.25, 0.5, 0.5),0.01,'2x'],
    3: [(0.375, 0.375, 0.25, 0.25),0.01,'4x'],
    4: [(0.4375, 0.4375, 0.125, 0.125),0.01,'8x'],
    5: [(0.46875, 0.46875, 0.0625, 0.0625),0.01,'16x']
}

class CustomCameraOutput():
    """
    This is a custom picamera output, see https://picamera.readthedocs.io/en/release-1.12/recipes2.html#custom-outputs.
    This is the core of the video pipeline and what it basically handles the raw frame processing via its write() method
    """
    def __init__(self,bus,screen_properties,frame_count):
        self.resolution = resolution
        self._is_recording = False
        self._is_streaming = False
        self.streamer = Streamer(8000, False)
        self.streamer.start_streaming()

    def write(self,raw):
        frame = numpy.frombuffer(raw,numpy.uint8).reshape([self.resolution[1],self.resolution[0],3])
        numpy_frame = numpy.copy(frame)
        numpy_frame = self._draw_gui(numpy_frame)
        self._display_frame(numpy_frame)
        self.streamer.update_frame(numpy_frame)
        if(self._is_recording):
            self.pipe.stdin.write(numpy_frame.tostring())
        if(self._is_streaming):
            pass

    def _display_frame(self,frame):
        cv2.namedWindow('main',cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("main",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow('main',frame)
        if cv2.waitKey(30) == ord('q'):
            exit(0) #TODO no!!

    def _draw_gui(self,frame):
        #(x1, y1, x2, y2)

        #check if should re-draw
        #1st is y, 2nd is x, not sure what 3rd is
        frame[int(self.resolution[1]/2),:,:] = 0xff
        frame[:,int(self.resolution[0]/2),:] = 0xff
        image = Image.fromarray(frame,'RGB')

        draw = ImageDraw.Draw(image)

        #draw.rectangle(((0, 0), (100, 100)), fill="black")
        diameter = 450
        x_midpoint = self.resolution[0]/2
        y_midpoint = self.resolution[1]/2

        x1 = x_midpoint - (diameter / 2)
        y1 = y_midpoint - (diameter / 2)
        x2 = x1 + diameter
        y2 = y1 + diameter

        draw.ellipse((x1, y1, x2, y2),fill=None,outline='white',width=2)

        return numpy.asarray(image,dtype=numpy.uint8)

    def flush(self):
        pass
        #print('%d bytes would have been written' % self.size)

class Camera(subscriber):
    """Represents the actual, physical camera and its controls e.g. doing digital zoom"""
    def __init__(self,bus,screen_properties):
        self.camera = picamera.PiCamera()
        self.screen_properties = screen_properties
        self.camera.resolution = screen_properties.resolution
        self.camera.rotation = 270
        self.camera.brightness = 50
        self.magnification_level = 1.0
        self.fps = 0
        self.frame_count = 0
        self.output = CustomCameraOutput(bus,screen_properties,frame_count)
        bus.register_consumer(self,'command:zoom')
        bus.register_consumer(self,'command:adjust')
        bus.register_consumer(self,'command:termination')
        self.bus = bus

    def start_camera(self):
        recording_thread = threading.Thread(target=_start_recording,args=(self.camera,))
        recording_thread.start()
        fps_thread = threading.Thread(target=_start_counting_fps,args=(self.frame_count,self.fps))
        fps_thread.start()

    def process(self,event):
        pass

    def digital_zoom(self,direction):
        pass

    def start_recording_video(self):
        #print('{}x{}'.format(self.camera.resolution[0],self.camera.resolution[1]))
        ffmpeg_cmd = [ 'ffmpeg',
        			#'-loglevel', 'error',
                    '-f','rawvideo',
                    '-pix_fmt','bgr24',
                    '-s','800x480',
        			'-i', '-',
        			#'-r', '30',
        			'-an','-sn',              	# disable audio processing
        			'shit.avi']
        self.output.pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.output._is_recording = True

    def stop_recording_video(self):
        self.is_recording = False
        self.output.pipe.stdout.flush()
        self.output.pipe.stdout.close()

    def start_stream(self):
        self.output._is_streaming = True

    def _start_recording(camera):
        time.sleep(1) #warmup
        camera.start_recording(self.output,format='bgr')
        try:
            while True:
        		camera.camera.wait_recording(1)
        except KeyboardInterrupt:
        	print('KeyboardInterrupt')
            camera.camera.stop_recording()

    def _start_counting_fps(frame_count,bus):
        starting_time=time.time()
        while True:
            time.sleep(1.0 - ((time.time() - starting_time) % 1.0))
            fps = frame_count
            frame_count = 0
            bus.post(event('event:fps',{'type':'fps','value':'{}}'.format(fps)}))
