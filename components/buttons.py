from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from PIL import Image
import picamera, time

class Buttons(subscriber):
    """Draws the buttons and switches between the different button overlays"""

    def __init__(self,bus,camera):
        self.camera = camera
        self.bus = bus
        self.timestamp_of_last_touch = 0
        self.standard_overlay = None
        self.options_overlay = None
        bus.register_consumer(self, 'touch')
        self.show_standard_layout()

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
        standard_overlay = self.camera.add_overlay(pad.tobytes(), pad.size, layer=3)
        self.standard_overlay = standard_overlay

    def show_options_layout(self):
        """The secondary layout with buttons that provide secondary functionality"""
        pad = Image.new('RGBA', (640,384,))
        ok_image = Image.open('icons/ok.png')
        pad.paste(ok_image, (550, 10), ok_image)
        up_image = Image.open('icons/up.png')
        pad.paste(up_image, (250, 10), up_image)
        down_image = Image.open('icons/down.png')
        pad.paste(up_image, (250, 410), down_image)
        #down_image = Image.open('icons/down.png')
        #pad.paste(up_image, (250, 410), down_image)
        right_image = Image.open('icons/right.png')
        pad.paste(right_image, (450, 200), right_image)
        if(self.standard_overlay):
            self.camera.remove_overlay(self.standard_overlay)
            self.standard_overlay = None
        options_overlay = self.camera.add_overlay(pad.tobytes(), pad.size, layer=3)
        self.options_overlay = options_overlay

    def process(self,event):
        #if(self._should_throttle()):
        #    return
        self._check_if_button_was_touched(event.get_data())

    def _should_throttle(self):
        now = time.time()
        if ((now - self.timestamp_of_last_touch) < 0.7): #throttle
            return True
        else:
            self.timestamp_of_last_touch = now
            return False

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
                self.show_standard_layout() #self.bus.post(event('crosshair','next'))
