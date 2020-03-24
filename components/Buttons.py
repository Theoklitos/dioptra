import picamera
from pynput import mouse
from PIL import Image, ImageDraw, ImageFont
import time
from datetime import datetime

from . import Crosshair
from . import Viewport
from . import Recorder

camera = None
last_touch_timestamp = 0
zoom_in_overlay = None
zoom_out_overlay = None

def on_touch(x, y, button, pressed):
    global last_touch_timestamp
    now = time.time()
    if ((now - last_touch_timestamp) < 0.7): #throttle
        return
    else:
        last_touch_timestamp = time.time()

    camera.annotate_background = picamera.Color('black')
    #camera.annotate_text = camera.annotate_text + " (event at + " + str(x) + ',' + str(y) + ")"
    readable_time = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)");
    camera.annotate_text = readable_time + ", Battery 51%, Magnification: 8x, " + 100 * " " + " Distance: 132m (event at + " + str(x) + ',' + str(y) + ")"

    if is_point_within(x,y,(700,790,30,110)):
        Viewport.zoom_in()
    elif is_point_within(x,y,(700,790,145,230)):
        Viewport.zoom_out()
    elif is_point_within(x,y,(700,770,260,350)):
        Crosshair.next_crosshair()
    elif is_point_within(x,y,(700,770,380,450)):
        Recorder.start_recording()

def initialize(initialized_camera):
    global camera
    camera = initialized_camera
    listener = mouse.Listener(on_move=None, on_click=on_touch)
    listener.start()

    #256/256 Large
    #640/384 Medium?
    #736/480 Small
    pad = Image.new('RGBA', (
        640,
        384,
        ))

    zoom_in_image = Image.open('icons/zoom_in.png')
    pad.paste(zoom_in_image, (550, 10), zoom_in_image)
    zoom_out_image = Image.open('icons/zoom_out.png')
    pad.paste(zoom_out_image, (550, 105), zoom_out_image)
    crosshair_change_image = Image.open('icons/crosshair_change.png')
    pad.paste(crosshair_change_image, (550, 200), crosshair_change_image)
    crosshair_change_image = Image.open('icons/video.png')
    pad.paste(crosshair_change_image, (550, 295), crosshair_change_image)

    crosshair_change_image = Image.open('icons/adjust.png')
    pad.paste(crosshair_change_image, (15, 200), crosshair_change_image)
    crosshair_change_image = Image.open('icons/photo.png')
    pad.paste(crosshair_change_image, (15, 295), crosshair_change_image)

    zoom_in_overlay = camera.add_overlay(pad.tobytes(), pad.size)
    zoom_in_overlay.layer = 3

    #draw.text((50, 50), "BRA BRA!", (255, 255, 255))

def is_point_within(x,y,area):
    return (x > area[0] and x < area[1]) & (y > area[2] and y < area[3])
