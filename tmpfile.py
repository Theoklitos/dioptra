#!/usr/bin/python

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



# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time, os
import cv2

#
import subprocess as sp
import numpy

width = 1920
height = 1080

FFMPEG_BIN = "ffmpeg"

ffmpeg_cmd = [FFMPEG_BIN,
	#global
	'-y',
	'-loglevel', 'info',
	#input
	#'-s','1920x1080',
	#'-pix_fmt', 'bgr24',
	#'-vcodec', 'rawvideo',
	'-i', '/dev/video0',
	#output
	#'-vcodec', 'libx264',
	'-an','-sn',              	# disable audio processing
	'-i', 'image2pipe.mp4']
#pipe = sp.Popen(ffmpeg_cmd, stdout=sp.PIPE) #, bufsize=10

import socket
import time
import picamera

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('wb')
try:
    camera.start_recording(connection, format='h264')
    camera.wait_recording(60)
    camera.stop_recording()
finally:
    connection.close()
    server_socket.close()


#cap = cv2.VideoCapture("/dev/video0")
#while(cap.isOpened()):
#	ret, frame = cap.read()
#	print(frame)
#	cv2.namedWindow("window",cv2.WND_PROP_FULLSCREEN)
#	cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
#	cv2.imshow('window',frame)
#	if cv2.waitKey(30) & 0xFF == ord('q'):
#		break

#ffmpeg_cmd_2 = [ FFMPEG_BIN,
#			#'-loglevel', 'error',
#			'-i', '-',
#			'-vcodec', 'rawvideo',
#			#'-s','800x480',
#			#'-r', '30',					# FPS
#			'-pix_fmt', 'bgr24',      	# opencv requires bgr24 pixel format.
#			'-an','-sn',              	# disable audio processing
#			'-f', 'image2pipe', 'pipe:two']
#pipe2 = sp.Popen(ffmpeg_cmd_2, stdin=sp.PIPE, stdout=sp.PIPE)

#output = sp.Popen(ffmpeg_cmd_2, stdin=sp.PIPE, stdout=sp.PIPE, stderr=None)
# In silent mode self.__process = sp.Popen(cmd, stdin=sp.PIPE, stdout=self.__DEVNULL, stderr=sp.STDOUT)


#while True:
	#in_bytes = pipe.stdout.read(width * height * 3)
	#if not in_bytes:
	#	break
	#in_frame = numpy.frombuffer(in_bytes,numpy.uint8).reshape([height,width,3])
	#cv2.imshow('a',in_frame)
	#cv2.waitKey(1)
	#os.write(1, image.tostring())
	#pipe2.stdin.write(in_frame.tostring())

#pipe.stdout.close()
#pipe.stdout.flush()
#pipe2.stdout.flush()
#cv2.destroyAllWindows()






#=================================== ANOTHER PROCESS
#reads from named pipe and shows on screen


#=================================== ANOTHER PROCESS
#reads from named pipe and saves to file
