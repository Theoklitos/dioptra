from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
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
        bus.register_consumer(self, 'status_updates')
        self._update_overlay()

    def refresh_time(self):
        now = datetime.now()
        timestamp_readable = now.strftime("%d-%b-%Y (%H:%M:%S)") #https://strftime.org/
        #self.camera.annotate_background = picamera.Color('black')
        #self.camera.annotate_text = timestamp_readable

    def process(self,event):
        type = event.get_data()['type']
        value = event.get_data()['value']
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
