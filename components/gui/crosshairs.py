from abc import ABC, abstractmethod
from PIL import ImageDraw


def get_all_crosshairs(resolution):
    return [
        Version1Crosshair(resolution)
    ]


class Crosshair(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def draw_crosshair(self,draw,pixel_drop=0):
        """This will be called by the GUI in order to render the crosshairs"""
        pass


class Version1Crosshair(Crosshair):
    def __init__(self, resolution):
        self.resolution = resolution
        super(Version1Crosshair, self).__init__()

    def draw_crosshair(self, image, pixel_bullet_drop=0):
        draw = ImageDraw.Draw(image)
        main_color = 'black'
        secondary_color = 'red'

        # calculations for the circle
        diameter = (95 * self.resolution[1]) / 100
        radius = diameter / 2
        x_midpoint = self.resolution[0]/2
        y_midpoint = self.resolution[1]/2
        x1 = x_midpoint - (diameter / 2)
        y1 = y_midpoint - (diameter / 2)
        x2 = x1 + diameter
        y2 = y1 + diameter

        # left lines
        end_of_line_x = x1+(diameter/3)
        draw.line((x1, y_midpoint, end_of_line_x, y_midpoint), fill=main_color, width=2)
        thick_line_padding = diameter / 30
        thick_line_length = diameter / 10
        draw.line((x1+thick_line_padding, y_midpoint, end_of_line_x-thick_line_length, y_midpoint),
                  fill=main_color, width=4)
        for offset in [0, 1]:
            draw.line((end_of_line_x+thick_line_padding+(offset*thick_line_padding*1.5), y_midpoint,
                      end_of_line_x + (thick_line_padding*2)+(offset*thick_line_padding*1.5), y_midpoint),
                      fill=main_color, width=2)

        # right lines
        start_of_line_x = x2-(diameter/3)
        draw.line((x2, y_midpoint, start_of_line_x, y_midpoint), fill=main_color, width=2)
        draw.line((x2-thick_line_padding, y_midpoint, start_of_line_x+thick_line_length, y_midpoint),
                  fill=main_color, width=4)
        for offset in [0, 1]:
            draw.line((start_of_line_x-thick_line_padding-(offset*thick_line_padding*1.5), y_midpoint,
                      start_of_line_x-(thick_line_padding*2)-(offset*thick_line_padding*1.5), y_midpoint),
                      fill=main_color, width=2)

        # this is the part that should mpve up/down based on bullet drop:
        # line
        tip_of_line_y = y_midpoint + pixel_bullet_drop
        draw.line((x_midpoint, tip_of_line_y, x_midpoint, y_midpoint+radius), fill=secondary_color, width=1)
        # triangle
        triangle_side_length = diameter / 50
        draw.line((x_midpoint, tip_of_line_y, x_midpoint-triangle_side_length, tip_of_line_y+triangle_side_length),
                  fill=secondary_color, width=1)
        draw.line((x_midpoint, tip_of_line_y, x_midpoint+triangle_side_length, tip_of_line_y+triangle_side_length),
                  fill=secondary_color, width=1)

        # bottom fixed line
        draw.line((x_midpoint, y2, x_midpoint, y2-thick_line_padding), fill=main_color, width=2)
        draw.line((x_midpoint, y2-thick_line_padding, x_midpoint, y2-(diameter/3)+thick_line_length),
                  fill=main_color, width=4)

        # circle
        draw.ellipse((x1, y1, x2, y2), fill=None, outline=main_color, width=3)
