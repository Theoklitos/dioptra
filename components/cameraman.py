from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from datetime import datetime
from PIL import Image
import os, subprocess

class Cameraman(subscriber):
    """More like camerabot :P Handles video recording and taking photos"""

    def __init__(self,bus,camera):
        self.camera = camera
        self.bus = bus
        self.last_crosshair_number = 1
        self.is_recording = False
        self.last_filename_used = None
        bus.register_consumer(self, 'video')
        bus.register_consumer(self, 'photo')
        bus.register_consumer(self, 'status_update')

    def _run_ffmpeg_command(self):
        """Post-processing. This will add the crosshair as an overlay to the video."""
        returncode = subprocess.call([
            'ffmpeg',
            '-i','temp.h264','-i','crosshairs/crosshair{0}.png'.format(self.last_crosshair_number),
            '-probesize','10M',
            '-filter_complex',
            'overlay=420:0',
            '-pix_fmt',
            'yuv420p',
            '-c:a','copy','videos/{0}'.format(self.last_filename_used)
        ])

    def take_photo_with_overlay(self):
        if(self.is_recording):
            return
        self.is_recording = True
        self.bus.post(event('status_update',{'type':'photo','value':'start'}))
        self.bus.post(event('notification','Taking photo, please wait...'))
        filename = datetime.now().strftime('%d-%b-%Y_%H.%M.%S.png')
        temp_filename = 'temp.png'
        self.camera.capture(temp_filename)
        self.bus.post(event('notification','Done. Processing...'))
        photo = Image.open(temp_filename)
        crosshair_image = self.get_crosshair_image().resize((1080,1140))
        photo.paste(crosshair_image,(420,0),crosshair_image)
        photo.save('photos/{0}'.format(filename),"PNG")
        self.bus.post(event('status_update',{'type':'photo','value':'end'}))
        self.bus.post(event('notification','Photo saved as {0}'.format(filename)))
        os.remove(temp_filename)
        self.is_recording = False

    def start_recording_video(self):
        if(self.is_recording):
            return
        self.is_recording = True
        video_filename = datetime.now().strftime('%d-%b-%Y_%H.%M.%S.mp4')
        self.last_filename_used = video_filename
        self.bus.post(event('status_update',{'type':'video','value':'start'}))
        self.bus.post(event('notification','Recording video...'))
        self.camera.start_recording('temp.h264',resize=(1920, 1080))

    def stop_recording_video_and_save_with_overlay(self):
        self.camera.stop_recording()
        self.bus.post(event('status_update',{'type':'video','value':'recording_stopped'}))
        self.bus.post(event('notification','Done. Processing, please wait...'))
        self._run_ffmpeg_command()
        #os.remove('temp.h264')
        self.is_recording = False
        self.bus.post(event('status_update',{'type':'video','value':'end'}))
        self.bus.post(event('notification','Video saved as {0}'.format(self.last_filename_used)))

    def process(self,event):
        type = event.get_topic()
        data = event.get_data()
        if(type=='video'):
            if(data=='start'):
                self.start_recording_video()
            elif(data=='end'):
                self.stop_recording_video_and_save_with_overlay()
        elif(type=='photo'):
            self.take_photo_with_overlay()
        elif(type=='status_update' and data['type']=='crosshair'):
            self.last_crosshair_number = data['value']

    def get_crosshair_image(self):
        return Image.open('crosshairs/crosshair' + str(self.last_crosshair_number) + '.png')
