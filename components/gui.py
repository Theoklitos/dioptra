from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from .crosshairs import Version1Crosshair
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from threading import Timer
import numpy, time, cv2

class Gui(subscriber):
    """?"""
    def __init__(self,bus,resolution,version):
        self.crosshair = Version1Crosshair(resolution) #hardcode this specific crosshair for now
        self.resolution = resolution
        self.gui_text = {'version':version}
        bus.register_consumer(self,'command:notification')
        bus.register_consumer(self,'event:fps')
        self.bus = bus

    def process(self,event):
        topic = event.get_topic()
        data = event.get_data()
        should_post_update = False
        if(topic == 'event:fps'):
            self.gui_text['fps'] = data['value']
            should_post_update = True

        if(should_post_update):
            self.generate_image_and_post_it()

    def generate_image_and_post_it(self):
        """?"""
        image = Image.new("RGB",self.resolution,color=(1,1,1))
        draw = ImageDraw.Draw(image)
        self.crosshair.drawCrosshair(draw)

        #other class
        draw.rectangle((0,20,100,50),outline='black',fill='black')
        draw.text((0,0),time.strftime('%x %X'),color='white')
        draw.text((0,20),'FPS: {:d} [V{}]'.format(self.gui_text['fps'],self.gui_text['version']),color='white')

        #PIL generates RGB images but openCV needs BGR ones
        numpy_array = numpy.asarray(image,dtype=numpy.uint8)
        numpy_array_bgr = cv2.cvtColor(numpy_array, cv2.COLOR_RGB2BGR)
        self.bus.post(event('command:gui_update',numpy_array_bgr))
