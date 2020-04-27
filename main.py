from components.camera.camera import Camera
from geeteventbus.eventbus import eventbus
import logging, os, subprocess, threading
from components.gui.gui import Gui
from components.user_input import UserInput

logging.getLogger("PIL").setLevel(logging.WARNING)
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s (%(threadName)-s)[%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

VERSION = 1.2
screen_properties = {
    'resolution':(800,480),
    'ppmm':9.2 #pixels per milimeter, based on your screen's ppi
}

if __name__ == '__main__':
    bus = eventbus()
    camera = Camera(bus,screen_properties)
    UserInput(bus)
    Gui(bus,screen_properties['resolution'],VERSION)
    camera.start_camera()
