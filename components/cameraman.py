from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from datetime import datetime
from PIL import Image
import os

class Cameraman(subscriber):
    """More like camerabot :P Handles video recording and taking photos"""

    def __init__(self,bus,camera,crosshair):
        self.camera = camera
        self.bus = bus
        self.crosshair = crosshair
        self.is_recording = False
        self.last_filename_used = None
        bus.register_consumer(self, 'video')
        bus.register_consumer(self, 'photo')

    def _run_ffmpeg_command(self):
        """Post-processing. This will add the crosshair as an overlay to the video."""
        #script = 'ffmpeg -i {0}.h264 -i crosshair5.png -filter_complex "overlay=200:0:enable='between(t,0,20)'" -pix_fmt yuv420p -c:a copy overlay.mp4
        pass

    def take_photo_with_overlay(self):
        if(self.is_recording):
            return
        self.is_recording = True
        self.bus.post(event('status_update','photo:start'))
        filename = datetime.now().strftime('%d-%b-%Y_%H.%M.%S.png')
        temp_filename = 'temp.png'
        self.camera.capture(temp_filename)
        photo = Image.open(temp_filename)
        crosshair_image = self.crosshair.get_crosshair_image().resize((1080,1140))
        photo.paste(crosshair_image,(420,0),crosshair_image)
        photo.save('photos/{0}'.format(filename),"PNG")
        self.bus.post(event('status_update','photo:end'))
        self.bus.post(event('notification','Photo saved as {0}'.format(filename)))
        os.remove(temp_filename)
        self.is_recording = False

    def start_recording_video(self):
        if(self.is_recording):
            return
        self.is_recording = True
        video_filename = '%d-%b-%Y_%H-%M-%S.h264'
        self.last_filename_used = video_filename
        self.bus.post(event('status_update','video:start'))
        self.camera.start_recording('%d-%b-%Y_%H-%M-%S.h264')

    def stop_recording_video_and_save_with_overlay(self):
        camera.stop_recording()
        self._run_ffmpeg_command()
        self.is_recording = False
        self.bus.post(event('status_update','video:end'))
        self.bus.post(event('notification','Video saved as {0}'.format(self.last_filename_used)))

    def process(self,event):
        type = event.get_topic()
        if(type=='video'):
            self.start_recording_video()
        elif(type=='photo'):
            self.take_photo_with_overlay()
