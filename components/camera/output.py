from geeteventbus.subscriber import subscriber
from geeteventbus.event import event
from flask_opencv_streamer.streamer import Streamer
import cv2
import timeit
import numpy


class CustomCameraOutput(subscriber):
    """
    This is a custom picamera output, see https://picamera.readthedocs.io/en/release-1.13/recipes2.html#custom-outputs.
    This is the core of the video pipeline and what it basically handles the raw frame processing via its write() method
    """
    def __init__(self, bus, resolution, frame_count):
        self.resolution = resolution
        self.frame_count = frame_count
        self._is_recording = False
        self._is_streaming = False
        self.gui_numpy_array = None
        self._should_terminate = False
        self.streamer = Streamer(8000, False)
        bus.register_consumer(self, 'command:gui_update')
        self.bus = bus
        # self.streamer.start_streaming() # do this manually/custom

    def process(self, event):
        topic = event.get_topic()
        if topic == 'command:gui_update':
            data = event.get_data()
            self.gui_numpy_array = data

    def write(self, raw):
        # start_time = timeit.default_timer()
        frame = numpy.frombuffer(raw, numpy.uint8).reshape([self.resolution[1], self.resolution[0], 3])
        if self.gui_numpy_array is not None:
            frame = numpy.where(self.gui_numpy_array == 1, frame, self.gui_numpy_array)
        self._display_frame(frame)
        # self.streamer.update_frame(frame)
        self.frame_count[0] = self.frame_count[0] + 1
        # end_time = timeit.default_timer();
        # print("write: " + str(round(end_time-start_time,3)*1000))

    def flush(self):
        cv2.destroyAllWindows()

    def _display_frame(self, frame):
        start_time = timeit.default_timer()
        if self._should_terminate:
            return
        cv2.namedWindow('main', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("main", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('main', frame)
        if cv2.waitKey(1) == 27:
            cv2.destroyAllWindows()
            self.bus.post(event('command:termination', {}))
        end_time = timeit.default_timer()
        # print("display: " + str(round(end_time-start_time,3)*1000))


class PhotoCameraOutput(subscriber):
    def __init__(self):
        pass

    def write(self, raw):
        pass
