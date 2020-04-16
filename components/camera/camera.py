from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
import picamera, time, cv2, threading, numpy, logging
import traceback, sys
from PIL import Image, ImageDraw, ImageFont
from .output import CustomCameraOutput

magnification_levels = {
    1: [(0.05, 0.05, 0.9, 0.9),0.01,'1.2x'],
    2: [(0.25, 0.25, 0.5, 0.5),0.01,'2x'],
    3: [(0.375, 0.375, 0.25, 0.25),0.01,'4x'],
    4: [(0.4375, 0.4375, 0.125, 0.125),0.01,'8x'],
    5: [(0.46875, 0.46875, 0.0625, 0.0625),0.01,'16x']
}

class Camera(subscriber):
    """Represents the actual, physical camera. Can control its functionality it e.g. doing physical or digital zoom"""
    def __init__(self,bus,screen_properties):
        self.camera = picamera.PiCamera()
        self.screen_properties = screen_properties
        self.camera.resolution = screen_properties['resolution']
        self.camera.framerate = 30
        self.camera.rotation = 270
        self.camera.brightness = 60
        self.zoom_factor = 1.0
        self.fps = 0
        self.frame_count = [0]
        bus.register_consumer(self,'command:zoom')
        bus.register_consumer(self,'command:adjust')
        bus.register_consumer(self,'command:termination')
        self.bus = bus
        self.output = CustomCameraOutput(bus,screen_properties['resolution'],self.frame_count)

    def start_camera(self):
        recording_thread = threading.Thread(target=self._start_recording,args=(self.camera,),name='camera-recorder')
        recording_thread.start()
        fps_thread = threading.Thread(target=self._start_counting_fps,args=(self.frame_count,self.bus),name='fps-counter',daemon=True)
        fps_thread.start()

    def process(self,event):
        topic = event.get_topic()
        data = event.get_data()
        if(topic == 'command:termination'):
            self.camera.stop_recording()
            self.output._should_terminate = True
            logging.debug("Camera stopped.")
        if(topic == 'command:zoom'):
            type = data['type']
            if(type == 'digital'):
                self.digital_zoom(data['direction'])

    def digital_zoom(self,direction,step=0.1):
        if(direction == 'in'):
            self.zoom_factor = self.zoom_factor+step
        if(direction == 'out' and self.zoom_factor > 1):
            self.zoom_factor = self.zoom_factor-step
            #check for out of bounds offset. zooming out might throw it out of screen
        zoomed_percentage = (1 / self.zoom_factor)
        offset = (1 - zoomed_percentage) / 2
        self.camera.zoom = (offset, offset, zoomed_percentage, zoomed_percentage)
        self.bus.post(event('event:zoom',{'type':'digital','value':round(self.zoom_factor,1)}))

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
