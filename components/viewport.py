from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from time import sleep
import picamera

magnification_levels = {
    1: [(0.05, 0.05, 0.9, 0.9),0.01,'1x'],
    2: [(0.25, 0.25, 0.5, 0.5),0.01,'2x'],
    3: [(0.375, 0.375, 0.25, 0.25),0.01,'4x'],
    4: [(0.4375, 0.4375, 0.125, 0.125),0.01,'8x'],
    5: [(0.46875, 0.46875, 0.0625, 0.0625),0.01,'16x']
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
        camera.zoom = magnification_levels[self.magnification_level][0]
        self.adjustement = (0,0)
        bus.register_consumer(self, 'zoom')
        bus.register_consumer(self, 'adjust')

    def process(self, event):
        topic = event.get_topic()
        data = event.get_data()
        if(topic=='zoom'):
            self.zoom(data)
        elif(topic=='adjust'):
            self.adjust(data)

    def zoom(self, type):
        original_level = self.magnification_level
        if(isinstance(type,int)):
            self.magnification_level = type
        elif(type == 'in'):
            if(self.magnification_level == 5):
                return
            self.magnification_level = self.magnification_level + 1
        elif(type == 'out'):
            if(self.magnification_level == 1):
                return
            self.magnification_level = self.magnification_level - 1

        # we first need to adjust for exising adjustments
        base_level = magnification_levels[original_level][0]
        current_level = self.camera.zoom
        deviation = (round(base_level[0],3) - round(current_level[0],3),round(base_level[1],3) - round(current_level[1],3))
        #print("Deviation: " + str(deviation))
        new_level = magnification_levels[self.magnification_level][0]
        adjusted_new_level = (round(new_level[0],3) - deviation[0],round(new_level[1],3) - deviation[1],new_level[2],new_level[3])
        #print("Adjusted new level: " + str(adjusted_new_level))
        self.camera.zoom = adjusted_new_level
        human_readable_value = magnification_levels[self.magnification_level][2]
        self.bus.post(event('status_update',{'type':'magnification_level','value':
            {'human_readable_value':human_readable_value,'number':self.magnification_level,'x':round(self.camera.zoom[0],3),'y':round(self.camera.zoom[1],3)}
        }))

    def adjust(self, type):
        step = magnification_levels[self.magnification_level][1]
        zoom = self.camera.zoom
        new_zoom = None
        tolerance = magnification_levels[self.magnification_level][0][0] * 2
        if(isinstance(type,tuple)):
            new_zoom = (type[0],type[1],zoom[2],zoom[3])
        elif(type=='up'):
            new_zoom = (zoom[0]-step,zoom[1],zoom[2],zoom[3])
        elif(type=='down'):
            new_zoom = (zoom[0]+step,zoom[1],zoom[2],zoom[3])
            if(new_zoom[0]>tolerance):
                return
        elif(type=='left'):
            new_zoom = (zoom[0],zoom[1]-step,zoom[2],zoom[3])
        elif(type=='right'):
            new_zoom = (zoom[0],zoom[1]+step,zoom[2],zoom[3])
            if(new_zoom[1]>tolerance):
                return
        self.camera.zoom = new_zoom
        self.adjustement = (round(self.camera.zoom[0],3), round(self.camera.zoom[1],3))
        self.bus.post(event('status_update',{'type':'adjustment','value':self.adjustement}))
