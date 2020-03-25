#!/usr/bin/python

from geeteventbus.eventbus import eventbus
from components.viewport import Viewport
from components.user_input import UserInput
from components.crosshair import Crosshair
from components.buttons import Buttons
from components.gui_text import GuiText
from components.cameraman import Cameraman
import sys, traceback, picamera

WIDTH = 1920
HEIGHT = 1140
RESOLUTION = (WIDTH, HEIGHT)

try:
    camera = picamera.PiCamera()
    bus = eventbus()
    user_input = UserInput(bus)
    Viewport(bus,camera,RESOLUTION)
    Crosshair(bus,camera,RESOLUTION)
    Buttons(bus,camera)
    gui_text = GuiText(bus,camera)
    Cameraman(bus,camera)

    while True:
        gui_text.refresh_time()
        pass

except KeyboardInterrupt:
    print("User terminated the app.")
except Exception as e:
    print("Catstrophic exception!")
    traceback.print_exc(file=sys.stdout)
finally:
    user_input.touch_listener.stop()
    user_input.keyboard_listener.stop()
    camera.stop_preview()
