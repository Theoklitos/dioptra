from PIL import ImageFont, ImageDraw
from threading import Timer
from .buttons import ButtonLayout1
from .layout_type import LayoutType
import time


class Layout1:
    def __init__(self, resolution, bus):
        self.resolution = resolution
        self.buttons = ButtonLayout1(bus)
        self.timer = None
        self.notification = None
        self.type = LayoutType.Standard

    def draw_layout(self, image, gui_text):
        """Main method that draws everything. This is hardcoded to 800x480."""
        draw = ImageDraw.Draw(image)
        resolution = self.resolution
        draw.font = ImageFont.truetype('usr/share/fonts/truetype/freefont/FreeSans.ttf', 14)
        # black text background
        text_background_height = 67
        if self.type != LayoutType.Standard:
            text_background_height = 86
        draw.rectangle((0, 0, 141, text_background_height), outline='black', fill='black')
        # time
        draw.text((5, 5), time.strftime('%x %H:%M:%S'), color='white')
        # main info panel
        draw.text((5, 25), 'Magnification: {}'.format(self._format_magnification_text(gui_text['magnification'])),
                  color='white')
        draw.text((5, 45), 'Range: ?', color='white')
        if self.type != LayoutType.Standard:
            # fps/debug stuff
            draw.rectangle((resolution[0]-101, 458, resolution[0], 480), outline='black', fill='black')
            draw.text((resolution[0]-96, 458), 'FPS: {:d} [V{}]'.format(gui_text['fps'], gui_text['version']),
                      color='white')
            # adjustment stuff
            adjustment_x = gui_text['adjustment'][0]
            adjustment_y = gui_text['adjustment'][1]
            draw.text((5, 65), 'Adjustment: {},{}'.format(adjustment_x, adjustment_y), color='white')
        # notifications
        if self.notification is not None:
            length = (len(self.notification) * 7.1) 
            draw.rectangle((0, 455, 10+length, 480), outline='black', fill='black')
            draw.text((5, 458), self.notification, color='white')
        # and the buttons
        self.buttons.draw_button_layout(image)

    def set_type(self, layout_type):
        self.type = layout_type
        self.buttons.type = layout_type

    def handle_touch(self, touch):
        self.show_notification(touch)
        self.buttons.handle_touch(touch)

    def show_notification(self, message):
        self.notification = str(message)
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        self.timer = Timer(4, self._clear_notification)
        self.timer.start()

    def _clear_notification(self):
        self.notification = None
        self.timer.cancel()

    def _format_magnification_text(self, text):
        if text == '?':
            return text
        else:
            return str(text) + 'x'
