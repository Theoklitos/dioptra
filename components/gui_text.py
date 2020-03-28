from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from threading import Timer
import picamera, sys, traceback

class GuiText(subscriber):
    """This is the view, the part of the GUI that displays information about the scope e.g. the magnification level"""
    def __init__(self,bus,camera):
        self.camera = camera
        self.bus = bus
        self.data = {
            'magnification_level': '?',
            'range': '?',
            'x': '?',
            'y': '?'
        }
        self.text_overlay = None
        self.notification_overlay = None
        self.timer = None
        self.should_show_coords = False
        bus.register_consumer(self, 'status_update')
        bus.register_consumer(self, 'notification')
        self._update_overlay()

    def _remove_notification_overlay(self):
        try:
            self.camera.remove_overlay(self.notification_overlay)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
        finally:
            self.notification_overlay = None

    def show_notification_for_seconds(self,text,seconds):
        notification_image = Image.new("RGBA", (512, 320))
        draw = ImageDraw.Draw(notification_image)
        # text background hackery!
        #print("(gui_text.py) Text '" + text + "' has length: " + str(len(text)))
        if(len(text) == 18 or len(text) == 19):
            background_width = 180
        else:
            background_width = (len(text)*10)-20
        draw.rectangle((2,280,background_width,302),outline='black',fill='black') #370 initial
        draw.font = ImageFont.truetype('usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 18)
        draw.text((5,280),text,(255, 255, 255))
        if(self.notification_overlay):
            self.notification_overlay.update(notification_image.tobytes())
        else:
            self.notification_overlay = self.camera.add_overlay(notification_image.tobytes(),layer=6,size=notification_image.size)
        if(self.timer and self.timer.is_alive()):
            self.timer.cancel()
        self.timer = Timer(float(seconds), self._remove_notification_overlay)
        self.timer.start()

    def process(self,event):
        topic = event.get_topic()
        data = event.get_data()
        if(topic=='notification'):
            self.show_notification_for_seconds(data, 3)
        elif(topic=='status_update'):
            type = data['type']
            value = data['value']
            if(type=='magnification_level'):
                self.data['magnification_level'] = value['human_readable_value']
                self.data['x'] = value['x']
                self.data['y'] = value['y']
            elif(type=='range'):
                self.data['range'] = value
            elif(type=='adjustment'):
                self.data['x'] = value[0]
                self.data['y'] = value[1]
            elif(type=='layout' and value=='options'):
                self.should_show_coords = True
            elif(type=='layout' and value=='standard'):
                self.should_show_coords = False
            self._update_overlay()

    def _update_overlay(self):
        gui_text_image = Image.new("RGBA", (512, 320 - 16))
        draw = ImageDraw.Draw(gui_text_image)
        if(self.should_show_coords):
            background_height = 80
        else:
            background_height = 43
        background_width = 115
        if(self.data['magnification_level'] == '16x'):
            background_width = 124
        draw.rectangle((0,0,background_width,background_height),outline='black',fill='black')
        draw.font = ImageFont.truetype('usr/share/fonts/truetype/freefont/FreeSans.ttf', 14)
        draw.multiline_text((5,5),'Magnification: {0}'.format(self.data['magnification_level']),(255, 255, 255))
        draw.multiline_text((5,23),'Range: {0}'.format(self.data['range']),(255, 255, 255))
        if(self.should_show_coords):
            draw.multiline_text((5,41),'X: {0}'.format(self.data['x']),(255, 255, 255))
            draw.multiline_text((5,59),'Y: {0}'.format(self.data['y']),(255, 255, 255))
        if(self.text_overlay):
            self.text_overlay.update(gui_text_image.tobytes())
        else:
            self.text_overlay = self.camera.add_overlay(gui_text_image.tobytes(),layer=4,size=gui_text_image.size,alpha=128)
