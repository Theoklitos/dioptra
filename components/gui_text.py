from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from threading import Timer
import picamera

class GuiText(subscriber):
    """This is the view, the part of the GUI that displays information about the scope e.g. the magnification level"""
    def __init__(self,bus,camera):
        self.camera = camera
        self.bus = bus
        self.data = {
            'magnification_level': 'x1',
            'range': '?',
            'adjustment': '(0,0)'
        }
        self.text_overlay = None
        self.notification_overlay = None
        bus.register_consumer(self, 'status_update')
        bus.register_consumer(self, 'notification')
        self._update_overlay()

    def _remove_notification_overlay(self):
        self.camera.remove_overlay(self.notification_overlay)
        self.notification_overlay = None

    def show_notification_for_seconds(self,text,seconds):
        notification_image = Image.new("RGBA", (512, 320))
        draw = ImageDraw.Draw(notification_image)
        draw.rectangle((2,280,370,302),outline='black',fill='black')
        draw.font = ImageFont.truetype('usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 18)
        draw.text((5,280),text,(255, 255, 255))
        if(self.notification_overlay):
            self.notification_overlay.update(notification_image.tobytes())
        else:
            self.notification_overlay = self.camera.add_overlay(notification_image.tobytes(),layer=6,size=notification_image.size)
        timer = Timer(float(seconds), self._remove_notification_overlay)
        timer.start()

    def process(self,event):
        topic = event.get_topic()
        data = event.get_data()
        if(topic=='notification'):
            self.show_notification_for_seconds(data, 3)
        elif(topic=='status_update'):
            type = data['type']
            value = data['value']
            if(type=='magnification_level'):
                self.data['magnification_level'] = value
            elif(type=='range'):
                self.data['range'] = value
            elif(type=='adjustment'):
                self.data['adjustment'] = value
            self._update_overlay()

    def _update_overlay(self):
        gui_text_image = Image.new("RGBA", (512, 320))
        draw = ImageDraw.Draw(gui_text_image)
        draw.rectangle((1,13,85,69),outline='black',fill='black')
        draw.font = ImageFont.truetype('usr/share/fonts/truetype/freefont/FreeSans.ttf', 14)
        draw.multiline_text((5,15),'Zoom: {0}'.format(self.data['magnification_level']),(255, 255, 255))
        draw.multiline_text((5,32),'Range: {0}'.format(self.data['range']),(255, 255, 255))
        draw.multiline_text((5,49),'Adj: {0}'.format(self.data['adjustment']),(255, 255, 255))
        if(self.text_overlay):
            self.text_overlay.update(gui_text_image.tobytes())
        else:
            self.text_overlay = self.camera.add_overlay(gui_text_image.tobytes(),layer=4,size=gui_text_image.size)
