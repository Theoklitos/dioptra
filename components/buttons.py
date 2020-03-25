from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from PIL import Image
import picamera

class Buttons(subscriber):
    """Draws the buttons and switches between the different button overlays"""

    def __init__(self,bus,camera):
        self.camera = camera
        self.bus = bus
        self.timestamp_of_last_touch = 0
        self.standard_overlay = None
        self.options_overlay = None
        bus.register_consumer(self, 'touch')
        bus.register_consumer(self, 'status_update')
        #self.show_standard_layout()
        self.show_options_layout()

    def show_standard_layout(self):
        """The initial, default layout with only three buttons"""
        #256/256 Large, 640/384 Medium, 736/480 Small - icon sizes
        pad = Image.new('RGBA', (640,384,))
        zoom_in_image = Image.open('icons/zoom_in.png')
        pad.paste(zoom_in_image, (550, 10), zoom_in_image)
        zoom_out_image = Image.open('icons/zoom_out.png')
        pad.paste(zoom_out_image, (550, 105), zoom_out_image)
        options_image = Image.open('icons/options.png')
        pad.paste(options_image, (550, 200), options_image)
        if(self.options_overlay):
            self.camera.remove_overlay(self.options_overlay)
            self.options_overlay = None
        standard_overlay = self.camera.add_overlay(pad.tobytes(), pad.size, layer=4)
        self.standard_overlay = standard_overlay

    def show_options_layout(self):
        """The secondary layout with buttons that provide secondary functionality"""
        pad = Image.new('RGBA', (640,384,))
        ok_image = Image.open('icons/ok.png')
        pad.paste(ok_image, (550, 10), ok_image)
        crosshair_image = Image.open('icons/crosshair_change.png')
        pad.paste(crosshair_image, (550, 105), crosshair_image)
        video_image = Image.open('icons/video.png')
        pad.paste(video_image, (550, 200), video_image)
        photo_image = Image.open('icons/photo.png')
        pad.paste(photo_image, (550, 295), photo_image)
        up_image = Image.open('icons/up.png')
        pad.paste(up_image, (280, 10), up_image)
        down_image = Image.open('icons/down.png')
        pad.paste(down_image, (280, 295), down_image)
        left_image = Image.open('icons/left.png')
        pad.paste(left_image, (135, 154), left_image)
        right_image = Image.open('icons/right.png')
        pad.paste(right_image, (425, 154), right_image)
        if(self.standard_overlay):
            self.camera.remove_overlay(self.standard_overlay)
            self.standard_overlay = None
        options_overlay = self.camera.add_overlay(pad.tobytes(), pad.size, layer=4)
        self.options_overlay = options_overlay

    def show_photo_in_progress_layout(self):
        """When a picture is being taken"""
        pad = Image.new('RGBA', (640,384,))
        ok_image = Image.open('icons/ok.png')
        pad.paste(ok_image, (550, 10), ok_image)
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
        if(self.standard_overlay):
            self.camera.remove_overlay(self.standard_overlay)
            self.standard_overlay = None
        options_overlay = self.camera.add_overlay(pad.tobytes(), pad.size, layer=4)
        self.options_overlay = options_overlay

    def show_vide_in_progress_layout(self):
        """When a video is being recorded"""
        pass

    def process(self,event):
        topic = event.get_topic()
        data = event.get_data()
        if(topic=='touch'):
            self._check_if_button_was_touched(data)
        elif(topic=='status_update'):
            if(data=='photo:start'):
                self.show_photo_in_progress_layout()
            elif(data=='photo:end'):
                self.show_options_layout()
            if(data=='video:start'):
                pass
            elif(data=='video:end'):
                pass

    def _is_point_within(self,x,y,area):
        return (x > area[0] and x < area[1]) & (y > area[2] and y < area[3])

    def _check_if_button_was_touched(self,coordinates):
        x = coordinates[0]
        y = coordinates[1]
        self.camera.annotate_text = '(' + str(x) + ',' + str(y) + ')'
        if(self.standard_overlay):
            if self._is_point_within(x,y,(700,790,30,110)):
                self.bus.post(event('zoom','in'))
            elif self._is_point_within(x,y,(700,790,145,230)):
                self.bus.post(event('zoom','out'))
            elif self._is_point_within(x,y,(700,770,260,350)):
                self.show_options_layout()
        elif(self.options_overlay):
            if self._is_point_within(x,y,(700,790,30,110)):
                self.show_standard_layout()
            elif self._is_point_within(x,y,(700,790,145,230)):
                self.bus.post(event('crosshair','next'))
            elif self._is_point_within(x,y,(700,790,260,350)):
                self.bus.post(event('video','start')) # these are commands, not events. status_updates are the events
            elif self._is_point_within(x,y,(700,790,375,470)):
                self.bus.post(event('photo','start'))
