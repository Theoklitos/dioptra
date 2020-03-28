from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from ast import literal_eval as make_tuple

CONFIG_FILE = 'dioptra-config.txt'

class FileReader(subscriber):
    """Reads and writes configurations to disk"""
    def __init__(self,bus):
        self.bus = bus
        self.bus.register_consumer(self, 'status_update')

    def loadConfigFromFile(self):
        config_file = open(CONFIG_FILE, 'r')
        lines = config_file.readlines()
        magnification_level = int(lines[0].strip())
        self.latest_magnification_level = magnification_level
        crosshair_number = int(lines[1].strip())
        self.latest_crosshair_number = crosshair_number
        adjustment = make_tuple(lines[2].strip())
        self.latest_adjustment = adjustment
        self.bus.post(event('zoom',magnification_level))
        self.bus.post(event('crosshair',crosshair_number))
        self.bus.post(event('adjust',adjustment))
        config_file.close()

    def process(self,event):
        should_write = False
        type = event.get_data()['type']
        value = event.get_data()['value']
        if(type=='magnification_level'):
            self.latest_magnification_level = value['number']
            self.latest_adjustment = (value['x'],value['y'])
            should_write = True
        elif(type=='adjustment'):
            self.latest_adjustment = (value[0],value[1])
            should_write = True
        elif(type=='crosshair'):
            self.latest_crosshair_number = value
            should_write = True
        if(should_write):
            self.saveToFile()

    def saveToFile(self):
        config_file = open(CONFIG_FILE, 'w')
        config_file.write(str(self.latest_magnification_level) + "\n")
        config_file.write(str(self.latest_crosshair_number) + "\n")
        config_file.write(str(self.latest_adjustment))
        config_file.close()
