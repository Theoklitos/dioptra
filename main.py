from components.camera import Camera
from geeteventbus.eventbus import eventbus
from components.screen_properties import properties as screen_properties

bus = eventbus()



camera = Camera(screen_properties,bus)
camera.start_camera()
