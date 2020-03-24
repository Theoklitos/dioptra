from time import sleep

magnification_level_zooms = {
    1: (0.05, 0.05, 0.9, 0.9),
    2: (0.25, 0.25, 0.5, 0.5),
    3: (0.375, 0.375, 0.25, 0.25),
    4: (0.4375, 0.4375, 0.125, 0.125),
    5: (0.46875, 0.46875, 0.0625, 0.0625)
}

camera = None
magnification_level = 1
viewport = None
offset = (0,0)

def _set_viewport(new_viewport):
    global viewport
    viewport = new_viewport
    camera.zoom = new_viewport

def _update_viewport():
    base_zoom = magnification_level_zooms[magnification_level]
    camera.zoom = base_zoom

def initialize(initalized_camera, width, height):
    global camera
    camera = initalized_camera
    camera.resolution = (width, height)
    #camera.framerate = 24
    camera.brightness = 60
    camera.rotation = 270
    camera.start_preview()
    camera.annotate_text = 'Centering...'
    sleep(1)
    _update_viewport()

def move_up():
    global offset
    offset[1] = offset[1] + 1
    print(offset)

def move_down():
    pass

def zoom_in():
    global magnification_level
    if magnification_level != 5:
        magnification_level = magnification_level + 1
        _update_viewport()

def zoom_out():
    global magnification_level
    if magnification_level != 1:
        magnification_level = magnification_level - 1
        _update_viewport()
