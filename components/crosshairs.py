from abc import ABC, abstractmethod

class Crosshair(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def drawCrosshair(self,draw,pixel_drop=0):
        """This will be called by the GUI in order to render the crosshairs"""
        pass

class Version1Crosshair(Crosshair):
    def __init__(self,resolution):
        self.resolution = resolution

    def drawCrosshair(self,draw,pixel_bullet_drop=20):
        main_color='black'
        secondary_color='red'
        #calculations for the circle
        diameter = (95 * self.resolution[1]) / 100
        radius = diameter / 2
        x_midpoint = self.resolution[0]/2
        y_midpoint = self.resolution[1]/2
        x1 = x_midpoint - (diameter / 2)
        y1 = y_midpoint - (diameter / 2)
        x2 = x1 + diameter
        y2 = y1 + diameter
        #left line
        draw.line((x1,y_midpoint,x1+(diameter/3),y_midpoint),fill=main_color,width=4)
        #right line
        draw.line((x2,y_midpoint,x2-(diameter/3),y_midpoint),fill=main_color,width=4)

        #moving part!
        #line
        tip_of_line_y = y_midpoint + pixel_bullet_drop
        draw.line((x_midpoint,tip_of_line_y,x_midpoint,y_midpoint+radius),fill='red',width=2)
        #triangle
        triangle_side_length = diameter / 20
        draw.line((x_midpoint,tip_of_line_y,x_midpoint-triangle_side_length,tip_of_line_y+triangle_side_length),fill='red',width=2)
        draw.line((x_midpoint,tip_of_line_y,x_midpoint+triangle_side_length,tip_of_line_y+triangle_side_length),fill='red',width=2)

        #bottom fixed line
        draw.line((x_midpoint,y2,x_midpoint,y2-(diameter/3)),fill=main_color,width=4)
        #circle
        draw.ellipse((x1, y1, x2, y2),fill=None,outline=main_color,width=4)



crosshairs = [
    Version1Crosshair(None)
]
