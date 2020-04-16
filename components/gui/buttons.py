from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from PIL import Image
from .layout_type import LayoutType

class ButtonLayout1(subscriber):
    """Draws the buttons and switches between the different button overlays.
    Unfortunately, this is hardcoded for 800x480."""
    def __init__(self,bus):
        self.type = LayoutType.Standard
        self.bus = bus

    def draw_button_layout(self,image):
        if(self.type == LayoutType.Standard):
            self._draw_standard_layout(image)
        elif(self.type == LayoutType.Options):
            self._draw_options_layout(image)

    def _draw_standard_layout(self,image):
        """The initial, default layout with only three buttons"""
        zoom_in_image = Image.open('icons/zoom_in.png')
        image.paste(zoom_in_image, (700, 25), zoom_in_image)
        zoom_out_image = Image.open('icons/zoom_out.png')
        image.paste(zoom_out_image, (700, 125), zoom_out_image)
        options_image = Image.open('icons/options.png')
        image.paste(options_image, (700, 225), options_image)

    def _draw_options_layout(self,image):
        """The layout that overlays all the controls for recording, adjusting etc"""
        back_image = Image.open('icons/back.png')
        image.paste(back_image, (700, 25), back_image)
        crosshair_image = Image.open('icons/crosshair_change.png')
        image.paste(crosshair_image, (700, 125), crosshair_image)
        video_image = Image.open('icons/video.png')
        image.paste(video_image, (700, 225), video_image)
        photo_image = Image.open('icons/photo.png')
        image.paste(photo_image, (700, 325), photo_image)
        # adjustment
        up_image = Image.open('icons/up.png')
        image.paste(up_image, (360, 15), up_image)
        down_image = Image.open('icons/down.png')
        image.paste(down_image, (360, 388), down_image)
        left_image = Image.open('icons/left.png')
        image.paste(left_image, (173, 195), left_image)
        right_image = Image.open('icons/right.png')
        image.paste(right_image, (555, 190), right_image)

    def show_photo_in_progress_layout(self):
        """When a picture is being taken"""
        pad = Image.new('RGBA', (640,384,))
        crosshair_image = Image.open('icons/crosshair_change.png')
        pad.paste(crosshair_image, (550, 105), crosshair_image)
        video_image = Image.open('icons/video.png')
        pad.paste(video_image, (550, 200), video_image)
        photo_image = Image.open('icons/photo_in_progress.png')
        pad.paste(photo_image, (550, 295), photo_image)
        up_image = Image.open('icons/up.png')
        pad.paste(up_image, (280, 10), up_image)
        down_image = Image.open('icons/down.png')
        pad.paste(down_image, (280, 295), down_image)
        left_image = Image.open('icons/left.png')
        pad.paste(left_image, (135, 154), left_image)
        right_image = Image.open('icons/right.png')
        pad.paste(right_image, (425, 154), right_image)
        if(self.options_overlay):
            self.options_overlay.update(pad.tobytes())
        else:
            options_overlay = self.camera.add_overlay(pad.tobytes(), pad.size, layer=4)
            self.options_overlay = options_overlay

    def show_video_recording_in_progress_layout(self):
        """When a video is being recorded"""
        pad = Image.new('RGBA', (640,384,))
        ok_image = Image.open('icons/ok.png')
        pad.paste(ok_image, (550, 10), ok_image)
        recording_in_progress_image = Image.open('icons/recording_in_progress.png')
        pad.paste(recording_in_progress_image, (550, 200), recording_in_progress_image)
        self.camera.remove_overlay(self.options_overlay)
        self.options_overlay = None
        if(self.video_recording_overlay):
            self.camera.remove_overlay(self.video_recording_overlay)
            self.video_recording_overlay = None
        video_recording_overlay = self.camera.add_overlay(pad.tobytes(), pad.size, layer=4)
        self.video_recording_overlay = video_recording_overlay

    def process2(self,event):
        topic = event.get_topic()
        data = event.get_data()
        if(topic=='touch'):
            self._check_if_button_was_touched(data)
        elif(topic=='status_update'):
            type = data['type']
            value = data['value']
            if(type=='photo' and value =='start'):
                self.show_photo_in_progress_layout()
            elif(type=='photo' and value =='end'):
                self.show_options_layout()
            elif(type=='video' and value =='start'):
                self.show_video_recording_in_progress_layout()
            elif(type=='video' and value =='end'):
                self.show_options_layout()
        elif(topic=='layout'):
            if(data=='options'):
                self.show_options_layout()
            elif(data=='standard'):
                self.show_standard_layout()

    def _is_point_within(self,x,y,area):
        return (x > area[0] and x < area[1]) & (y > area[2] and y < area[3])

    def handle_touch(self,coordinates):
        x = coordinates[0]
        y = coordinates[1]
        if(self.type == LayoutType.Standard):
            if self._is_point_within(x,y,(710,790,40,110)):
                self.bus.post(event('command:zoom',{'type':'digital','direction':'in'}))
            elif self._is_point_within(x,y,(710,790,145,215)):
                self.bus.post(event('command:zoom',{'type':'digital','direction':'out'}))
            elif self._is_point_within(x,y,(710,790,240,310)):
                self.bus.post(event('command:layout_change',{'type':None,'value':LayoutType.Standard}))
        elif(self.type == LayoutType.Options):
            if self._is_point_within(x,y,(700,790,30,110)):
                self.show_standard_layout()
            elif self._is_point_within(x,y,(700,790,145,230)):
                self.bus.post(event('crosshair','next'))
            elif self._is_point_within(x,y,(700,790,260,350)):
                self.bus.post(event('video','start')) # these are commands, not events. status_updates are the events
            elif self._is_point_within(x,y,(700,790,375,470)):
                self.bus.post(event('photo','start'))
            elif self._is_point_within(x,y,(350,450,30,110)):
                self.bus.post(event('adjust','up'))
            elif self._is_point_within(x,y,(350,450,380,460)):
                self.bus.post(event('adjust','down'))
            elif self._is_point_within(x,y,(160,260,200,300)):
                self.bus.post(event('adjust','left'))
            elif self._is_point_within(x,y,(540,640,200,300)):
                self.bus.post(event('adjust','right'))
        elif(self.type == LayoutType.Recording):
            if self._is_point_within(x,y,(700,790,30,110)):
                self.bus.post(event('video','end')) # again, this is a command. The status update (event) comes later
