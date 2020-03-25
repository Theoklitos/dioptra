from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from datetime import datetime
from PIL import Image

class Cameraman(subscriber):
    """More like camerabot. Handles video recording and taking photos"""

    def __init__(self,bus,camera,crosshair):
        self.camera = camera
        self.bus = bus
        self.crosshair = crosshair
        bus.register_consumer(self, 'video')
        bus.register_consumer(self, 'photo')

    def process(self,event):
        type = event.get_topic()
        if(type=='video'):
            pass
        elif(type=='photo'):
            filename = datetime.now().strftime("%d-%b-%Y_%H:%M:%S.png")
            self.camera.capture(filename)
            photo = Image.open(filename)
            crosshair_image = self.crosshair.get_crosshair_image().resize((1080,1140))
            #photo = photo.convert("RGBA")
            #crosshair_image = crosshair_image.convert("RGBA")
            #new_img = Image.blend(photo, crosshair_image, 0.5)
            #photo.paste(crosshair_image, ((1920-1080)/2, (1140-1080)/2, crosshair_image)
            photo.paste(crosshair_image, (((1920-1080)/2),0), crosshair_image)
            photo.save(filename,"PNG")
            print(crosshair_image.size)
            print(datetime.now().strftime("%d-%b-%Y_%H:%M:%S.png"))
