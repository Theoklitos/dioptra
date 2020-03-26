#!/usr/bin/python

from geeteventbus.eventbus import eventbus
from components.viewport import Viewport
from components.user_input import UserInput
from components.crosshair import Crosshair
from components.buttons import Buttons
from components.gui_text import GuiText
from components.cameraman import Cameraman
from components.file_reader import FileReader
import sys, traceback, picamera, subprocess

WIDTH = 1920
HEIGHT = 1140
RESOLUTION = (WIDTH, HEIGHT)

from time import sleep

try:
    camera = picamera.PiCamera()
    bus = eventbus()
    user_input = UserInput(bus)
    Viewport(bus,camera,RESOLUTION)
    crosshair = Crosshair(bus,camera,RESOLUTION)
    Buttons(bus,camera)
    gui_text = GuiText(bus,camera)
    Cameraman(bus,camera)

    filereader = FileReader(bus)
    filereader.loadConfigFromFile()

    #gui_text.show_notification_for_seconds('This is a fucking test bra', 3)
    #gui_text.show_notification_for_seconds('Photo saved as 25-Mar-2020_15.46.54.png', 3)
    #returncode = subprocess.call([
    #    'ffmpeg',
    #    '-i','temp.h264','-i','crosshairs/crosshair5.png',
    #    '-filter_complex',
    #    'overlay=420:0:enable=\'between(t,0,20)\'',
    #    '-pix_fmt',
    #    'yuv420p',
    #    '-c:a','copy','manual.mp4'
    #])

    while True:
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
    filereader.saveToFile()
