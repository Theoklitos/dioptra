#!/usr/bin/python

#good ones:
#sudo apt install mesa-common-dev
#pip3 install git+https://github.com/kivy/kivy.git@master

import picamera
from time import sleep

from components import Viewport
from components import Crosshair
from components import Text
from components import Buttons

WIDTH = 1920
HEIGHT = 1140

try:
    camera = picamera.PiCamera()

    Viewport.initialize(camera, WIDTH, HEIGHT)
    Crosshair.initialize(camera, WIDTH, HEIGHT)
    Text.initialize(camera, WIDTH)
    Buttons.initialize(camera)

    while True:
        #Text.refresh_time()
        pass

except Exception as e:
    print(str(e))
