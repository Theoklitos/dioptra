camera = None

def initialize():
    pass

def start_recording():
    pass
#ffmpeg -i my_video.h264 -i crosshair5.png -filter_complex "overlay=200:0:enable='between(t,0,20)'" -pix_fmt yuv420p -c:a copy overlay.mp4
