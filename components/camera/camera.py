from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
import picamera
import threading
import logging
# import ffmpeg
import time
from .output import CustomCameraOutput


class Camera(subscriber):
    """Represents the actual, physical camera. Can control its functionality it e.g. doing physical or digital zoom"""
    def __init__(self, bus, screen_properties):
        self.camera = picamera.PiCamera()
        self.screen_properties = screen_properties
        self.camera.resolution = screen_properties['resolution']
        self.camera.rotation = 270
        self.camera.brightness = 60
        self.zoom_factor = 1.0
        self.adjustment = (0, 0)
        self.fps = 0
        self.frame_count = [0]
        bus.register_consumer(self, 'command:zoom')
        bus.register_consumer(self, 'command:adjust')
        bus.register_consumer(self, 'command:photo')
        bus.register_consumer(self, 'command:video')
        bus.register_consumer(self, 'command:termination')
        self.bus = bus
        self.output = CustomCameraOutput(bus, screen_properties['resolution'], self.frame_count)

    def start_camera(self):
        recording_thread = threading.Thread(target=self._start_recording, args=(self.camera,), name='camera-recorder')
        recording_thread.start()
        fps_thread = threading.Thread(target=self._start_counting_fps, args=(self.frame_count, self.bus),
                                      name='fps-counter', daemon=True)
        fps_thread.start()

    def process(self, event):
        topic = event.get_topic()
        data = event.get_data()
        if topic == 'command:termination':
            self.camera.stop_recording()
            self.output.should_terminate = True
            logging.debug("Camera stopped.")
        elif topic == 'command:zoom':
            zoom_type = data['type']
            if zoom_type == 'digital':
                self.digital_zoom(data['direction'])
        elif topic == 'command:adjust':
            self.adjust(data['direction'])
        elif topic == 'command:photo':
            self.take_photo()

    def adjust(self, direction, step=0.01):
        if self.zoom_factor == 1.0:
            return
        # the self.adjustment variable holds the 'human readable' version of the offset
        # the actual offset is applied to the self.camera.zoom in a weird way, because the lens is rotated
        new_x = self.adjustment[0]
        new_y = self.adjustment[1]
        new_camera_x = self.camera.zoom[0]
        new_camera_y = self.camera.zoom[1]
        if direction == 'up':
            new_y = new_y + step
            new_camera_x = self.camera.zoom[0] - step
        elif direction == 'down':
            new_y = new_y - step
            new_camera_x = self.camera.zoom[0] + step
        if direction == 'left':
            new_x = new_x + step
            new_camera_y = self.camera.zoom[1] - step
        elif direction == 'right':
            new_x = new_x - step
            new_camera_y = self.camera.zoom[1] + step
        self.adjustment = (round(new_x, 2), round(new_y, 2))
        self.camera.zoom = (new_camera_x, new_camera_y, self.camera.zoom[2], self.camera.zoom[3])
        self.bus.post(event('command:notification', {'message': str(self.adjustment)}))
        self.bus.post(event('event:adjust', {'value': self.adjustment}))

    def digital_zoom(self, direction, step=0.1):
        if direction == 'in':
            self.zoom_factor = self.zoom_factor+step
        if direction == 'out' and self.zoom_factor > 1:
            self.zoom_factor = self.zoom_factor-step
        zoomed_percentage = (1 / self.zoom_factor)
        offset = (1 - zoomed_percentage) / 2
        # apply any existing adjustment and set the zoom
        adjusted_offset_x = offset-self.adjustment[1]
        adjusted_offset_y = offset-self.adjustment[0]
        self.camera.zoom = (adjusted_offset_x, adjusted_offset_y, zoomed_percentage, zoomed_percentage)
        self.bus.post(event('event:zoom', {'type': 'digital', 'value': round(self.zoom_factor, 1)}))

    def take_photo(self):
        # https://picamera.readthedocs.io/en/release-1.13/recipes1.html#capturing-to-a-pil-image
        filename = time.strftime('%Y_%m_%d-%H_%M_%S.jpg')
        self.camera.capture(filename, resize=(1980, 1080))
        # self.camera.stop_recording()
        # self.camera.resolution = (1920,1088)
        # self.camera.capture(filename)
        # self.camera.resolution = (800,480)
        # self.camera.start_recording(self.output,format='bgr')
        self.bus.post(event('command:notification',{'message':'Photo saved as {}'.format(filename)}))

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

    def _start_recording(self, camera):
        """The 'main' method, where the picamera video record method is invoked"""
        time.sleep(1)  # warmup
        camera.start_recording(self.output, format='bgr')
        try:
            while True:
                camera.wait_recording(1)
        except Exception as e:
            if not self.output.should_terminate:
                logging.exception('Exception on main camera handler!')
        finally:
            logging.debug("Camera recording thread terminated.")
            # maybe this shouldn't be done here, but its simpler than creating a whole new class
            self.bus.shutdown()
            logging.debug("Event bus shutdown.")

    def _start_counting_fps(self, frame_count, bus):
        while True:
            starting_time = time.time()
            time.sleep(1.0 - ((time.time() - starting_time) % 1.0))
            fps = frame_count[0]
            frame_count[0] = 0
            bus.post(event('event:fps', {'value': fps}))
