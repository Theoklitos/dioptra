from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
import picamera, time, cv2, threading, numpy, logging
import traceback, sys
from PIL import Image, ImageDraw, ImageFont
import timeit
from flask_opencv_streamer.streamer import Streamer

from .crosshairs import Version1Crosshair

magnification_levels = {
    1: [(0.05, 0.05, 0.9, 0.9),0.01,'1.2x'],
    2: [(0.25, 0.25, 0.5, 0.5),0.01,'2x'],
    3: [(0.375, 0.375, 0.25, 0.25),0.01,'4x'],
    4: [(0.4375, 0.4375, 0.125, 0.125),0.01,'8x'],
    5: [(0.46875, 0.46875, 0.0625, 0.0625),0.01,'16x']
}

class CustomCameraOutput(subscriber):
    """
    This is a custom picamera output, see https://picamera.readthedocs.io/en/release-1.13/recipes2.html#custom-outputs.
    This is the core of the video pipeline and what it basically handles the raw frame processing via its write() method
    """
    def __init__(self,bus,resolution,frame_count):
        self.resolution = resolution
        self.frame_count = frame_count
        self._is_recording = False
        self._is_streaming = False
        self.gui_numpy_array = None
        self._should_terminate = False
        self.streamer = Streamer(8000,False)
        bus.register_consumer(self,'command:gui_update')
        self.bus = bus
        #self.streamer.start_streaming() #TODO remove

    def process(self,event):
        topic = event.get_topic()
        if(topic == 'command:gui_update'):
            data = event.get_data()
            self.gui_numpy_array = data

    def write(self,raw):
        start_time = timeit.default_timer()
        frame = numpy.frombuffer(raw,numpy.uint8).reshape([self.resolution[1],self.resolution[0],3])
        if(self.gui_numpy_array is not None):
            frame = numpy.where(self.gui_numpy_array == 1, frame, self.gui_numpy_array)
        self._display_frame(frame)
        #self.streamer.update_frame(frame)
        self.frame_count[0] = self.frame_count[0] + 1
        end_time = timeit.default_timer();
        #print("write: " + str(round(end_time-start_time,3)*1000))

    def flush(self):
        cv2.destroyAllWindows()

    def _display_frame(self,frame):
        start_time = timeit.default_timer();
        if(self._should_terminate):
            return
        cv2.namedWindow('main',cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("main",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow('main',frame)
        if(cv2.waitKey(30) == 27):
            cv2.destroyAllWindows()
            self.bus.post(event('command:termination',{}))
        end_time = timeit.default_timer();
        #print("display: " + str(round(end_time-start_time,3)*1000))

class Camera(subscriber):
    """Represents the actual, physical camera. Can control its functionality it e.g. doing physical or digital zoom"""
    def __init__(self,bus,screen_properties):
        self.camera = picamera.PiCamera()
        self.screen_properties = screen_properties
        self.camera.resolution = screen_properties['resolution']
        self.camera.rotation = 270
        self.camera.brightness = 50
        self.magnification_level = 1.0
        self.fps = 0
        self.frame_count = [0]
        self.output = CustomCameraOutput(bus,screen_properties['resolution'],self.frame_count)
        bus.register_consumer(self,'command:zoom')
        bus.register_consumer(self,'command:adjust')
        bus.register_consumer(self,'command:termination')
        self.bus = bus

    def start_camera(self):
        recording_thread = threading.Thread(target=self._start_recording,args=(self.camera,),name='camera-recorder')
        recording_thread.start()
        fps_thread = threading.Thread(target=self._start_counting_fps,args=(self.frame_count,self.bus),name='fps-counter',daemon=True)
        fps_thread.start()

    def process(self,event):
        topic = event.get_topic()
        if(topic == 'command:termination'):
            self.camera.stop_recording()
            self.output._should_terminate = True
            logging.debug("Camera stopped.")

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
        #self.output.pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.output._is_recording = True

    def stop_recording_video(self):
        self.is_recording = False
        self.output.pipe.stdout.flush()
        self.output.pipe.stdout.close()

    def start_stream(self):
        self.output._is_streaming = True

    def _start_recording(self,camera):
        time.sleep(1) #warmup
        camera.start_recording(self.output,format='bgr')
        try:
            while True:
                camera.wait_recording(1)
        except Exception as e:
            if(not self.output._should_terminate):
                logging.exception('Exception on main camera handler!')
        finally:
            logging.debug("Camera recording thread terminated.")
            # maybe this shouldn't be done here, but its simpler than creating a whole new class
            self.bus.shutdown()
            logging.debug("Event bus shutdown.")

    def _start_counting_fps(self,frame_count,bus):
        while True:
            starting_time=time.time()
            time.sleep(1.0 - ((time.time() - starting_time) % 1.0))
            fps = frame_count[0]
            frame_count[0] = 0
            bus.post(event('event:fps',{'value':fps}))
        logging.debug("FPS thread terminated.")
