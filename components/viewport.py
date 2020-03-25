from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from time import sleep

magnification_level_zooms = {
    1: (0.05, 0.05, 0.9, 0.9),
    2: (0.25, 0.25, 0.5, 0.5),
    3: (0.375, 0.375, 0.25, 0.25),
    4: (0.4375, 0.4375, 0.125, 0.125),
    5: (0.46875, 0.46875, 0.0625, 0.0625)
}

class Viewport(subscriber):
    """Represents the (part of the) image that the user sees. Responsible for zooming and adjusting."""
    def __init__(self,bus,camera,resolution):
        self.camera = camera
        camera.resolution = resolution
        camera.brightness = 60
        camera.rotation = 270
        camera.start_preview()
        sleep(1)
        self.bus = bus
        self.magnification_level = 1
        camera.zoom = magnification_level_zooms[self.magnification_level]
        bus.register_consumer(self, 'zoom')
        bus.register_consumer(self, 'adjust')

    def process(self, event):
        topic = event.get_topic()
        data = event.get_data()
        if(topic=='zoom'):
            self.zoom(data)
        elif(topic=='adjusta'):
            self.adjust(data)

    def zoom(self, direction):
        if(direction == 'in'):
            if(self.magnification_level == 5):
                return
            self.magnification_level = self.magnification_level + 1
        elif(direction == 'out'):
            if(self.magnification_level == 1):
                return
            self.magnification_level = self.magnification_level - 1
        self.camera.zoom = magnification_level_zooms[self.magnification_level]
        if(self.magnification_level == 1): value = '1x'
        if(self.magnification_level == 2): value = '2x'
        if(self.magnification_level == 3): value = '4x'
        if(self.magnification_level == 4): value = '8x'
        if(self.magnification_level == 5): value = '16x'
        self.bus.post(event('status_updates',{'type':'magnification_level','value':value}))

    def adjust(self, direction):
        print('adj ' + direction)
