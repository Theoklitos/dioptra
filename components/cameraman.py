from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from datetime import datetime

class Cameraman(subscriber):
    """More like camerabot. Handles video recording and taking photos"""

    def __init__(self,bus,camera):
        self.camera = camera
        self.bus = bus
        bus.register_consumer(self, 'video')
        bus.register_consumer(self, 'photo')

    def process(self,event):
        type = event.get_topic()
        if(type=='video'):
            pass
        elif(type=='photo'):
            filename = datetime.now().strftime("%d-%b-%Y_%H:%M:%S.jpg")
            self.camera.capture(filename)
