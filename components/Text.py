from datetime import datetime

camera = None
width = None

def initialize(initialized_camera, screen_width):
    global camera
    camera = initialized_camera
    global width
    width = screen_width

def refresh_time():
    now = datetime.now()
    timestamp_readable = now.strftime("%d-%b-%Y (%H:%M:%S)") #https://strftime.org/
    _align_left(timestamp_readable)

def _align_left(text):
    spaces = width - len(text)
    camera.annotate_text = text + (95 * ' ')
