from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from PIL import Image
import numpy
import cv2
from ..gui.crosshairs import get_all_crosshairs
from .layouts import Layout1


class Gui(subscriber):
    """Represents whatever the user sees. Can update itself by listening to events.
    Will push its (updated) state to the camera output so that it can be displayed.
    """
    def __init__(self, bus, resolution, version):
        self.crosshairs = get_all_crosshairs(resolution)
        self.layout = Layout1(resolution, bus)
        self.resolution = resolution
        self.gui_text = {'version': version, 'magnification': '?', 'distance': '?', 'adjustment': (0.0, 0.0)}
        bus.register_consumer(self, 'command:notification')
        bus.register_consumer(self, 'command:layout_change')
        bus.register_consumer(self, 'event:adjust')
        bus.register_consumer(self, 'event:zoom')
        bus.register_consumer(self, 'event:fps')
        bus.register_consumer(self, 'touch')
        self.bus = bus

    def process(self, event):
        topic = event.get_topic()
        data = event.get_data()
        should_publish_event = False
        if topic == 'touch':
            self.layout.handle_touch(data)
        elif topic == 'command:notification':
            self.layout.show_notification(data['message'])
        elif topic == 'command:layout_change':
            self.layout.set_type(data['value'])
            should_publish_event = True
        elif topic == 'event:zoom':
            self.gui_text['magnification'] = data['value']
            should_publish_event = True
        elif topic == 'event:adjust':
            self.gui_text['adjustment'] = data['value']
            should_publish_event = True
        elif topic == 'event:fps':
            self.gui_text['fps'] = data['value']
            should_publish_event = True
        if should_publish_event:
            self.generate_image_and_publish_event()

    def generate_image_and_publish_event(self):
        """This will publish the new (updated) gui as an event. This will be read by the custom camera output class."""
        image = Image.new("RGB", self.resolution, color=(1, 1, 1))
        self.crosshairs[0].draw_crosshair(image)
        self.layout.draw_layout(image, self.gui_text)
        # PIL generates RGB images but openCV needs BGR ones, so we convert it first
        numpy_array = numpy.asarray(image, dtype=numpy.uint8)
        numpy_array_bgr = cv2.cvtColor(numpy_array, cv2.COLOR_RGB2BGR)
        self.bus.post(event('command:gui_update', numpy_array_bgr))
