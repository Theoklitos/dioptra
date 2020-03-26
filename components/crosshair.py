from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from PIL import Image


#https://www.hiclipart.com/free-transparent-background-png-clipart-bxtmb
#https://www.pngguru.com/search?png=scope

class Crosshair(subscriber):
    """Self-explanatory"""

    def __init__(self,bus,camera,resolution):
        self.camera = camera
        self.bus = bus
        self.crosshair_overlay = None
        self.crosshair_number = 1
        bus.register_consumer(self, 'crosshair')        

    def process(self,event):
        topic = event.get_topic()
        data = event.get_data()
        if(data == 'next'):
            new_crosshair_number = self.crosshair_number + 1
            if(new_crosshair_number > 6):
                new_crosshair_number = 1
        else:
            new_crosshair_number = data
        self.set_crosshair(new_crosshair_number)

    def get_crosshair_image(self):
        return Image.open('crosshairs/crosshair' + str(self.crosshair_number) + '.png')

    def set_crosshair(self,number):
        img = Image.open('crosshairs/crosshair' + str(number) + '.png')
        pad = Image.new('RGBA', (
            ((img.size[0] + 31) // 32) * 32,
            ((img.size[1] + 15) // 16) * 16,
        ))
        pad.paste(img, (0, 0), img)
        if(self.crosshair_overlay):
            self.camera.remove_overlay(self.crosshair_overlay)
        self.crosshair_overlay = self.camera.add_overlay(pad.tobytes(), layer=3, size=img.size)
        self.crosshair_number = number
        self.bus.post(event('status_update',{'type':'crosshair','value':self.crosshair_number}))
