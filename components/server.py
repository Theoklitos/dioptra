from flask import Response
from flask import Flask
from flask import render_template
import threading
import cv2

outputFrame = []

app = Flask(__name__)

def generate():
    while True:
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(outputFrame) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	return Response(generate(),mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/")
def index():
	#return render_template("index.html")
    return "HELLO!"

def setFrame(frame):
    global outputFrame
    (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
    outputFrame = encodedImage

def shit():
    app.run(host='0.0.0.0',port=8000,use_reloader=False,debug=False)

threading.Thread(target=shit).start()
