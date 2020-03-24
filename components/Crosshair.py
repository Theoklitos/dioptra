from PIL import Image
from time import sleep

#https://www.hiclipart.com/free-transparent-background-png-clipart-bxtmb
#https://www.pngguru.com/search?png=scope

camera = None
overlay = None
crosshair_number = 0

def initialize(initalized_camera, width, height):
    global camera
    camera = initalized_camera
    camera.annotate_text = ''
    set_crosshair(1)

def set_crosshair(number):
    img = Image.open('crosshairs/crosshair' + str(number) + '.png')
    pad = Image.new('RGBA', (
        ((img.size[0] + 31) // 32) * 32,
        ((img.size[1] + 15) // 16) * 16,
        ))
    pad.paste(img, (0, 0), img)
    global overlay
    if overlay:
        camera.remove_overlay(overlay)
    overlay = camera.add_overlay(pad.tobytes(), layer=3, size=img.size)
    global crosshair_number
    crosshair_number = number

def next_crosshair():
    new_crosshair_number = None
    if crosshair_number == 5:
        new_crosshair_number = 1
    else:
        new_crosshair_number = crosshair_number + 1
    set_crosshair(new_crosshair_number)
