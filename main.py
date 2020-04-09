from components.camera import Camera
from geeteventbus.eventbus import eventbus
import logging
from components.gui import Gui

logging.getLogger("PIL").setLevel(logging.WARNING)
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s (%(threadName)-s)[%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

VERSION = 1.1
screen_properties = {
    'resolution':(800,480),
    'ppmm':9.2 #pixels per milimeter, based on your screen's ppi
}

if(__name__ == "__main__"):
    #unclutter -idle 0 HIDE MOUSE
    bus = eventbus()
    camera = Camera(bus,screen_properties)
    Gui(bus,screen_properties['resolution'],VERSION)
    camera.start_camera()
