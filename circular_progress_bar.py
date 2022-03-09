try:
    import Tkinter as tk
    import tkFont
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    import tkinter.font as tkFont
    import tkinter.ttk as ttk
import numpy as np
class CircularProgressbar(object):
    def __init__(self, canvas, x0, y0, x1, y1, intensity_percent, width=2, start_ang=90, full_extent=360):
        self.custom_font = tkFont.Font(family="Helvetica", size=12, weight='bold')
        self.canvas = canvas
        self.x0, self.y0, self.x1, self.y1 = x0+width, y0+width, x1-width, y1-width
        self.tx, self.ty = (x1-x0) / 2, (y1-y0) / 2
        self.width = width
        self.start_ang, self.full_extent = start_ang, full_extent
        self.intensity_percent = intensity_percent
        # draw static bar outline
        w2 = width / 2
        self.oval_id1 = self.canvas.create_oval(self.x0-w2, self.y0-w2,
                                                self.x1+w2, self.y1+w2, outline = 'blue') #outline = 'black'
        self.oval_id2 = self.canvas.create_oval(self.x0+w2, self.y0+w2,
                                                self.x1-w2, self.y1-w2, outline = 'blue') #outline = 'black'
        #self.running = False
        self.extent = np.multiply(np.divide(self.intensity_percent, 100), 360) #negative extent is clockwise, positive is anti-clockwise
        if self.extent == 360:
            self.extent = 359

        self.arc_id = self.canvas.create_arc(self.x0, self.y0, self.x1, self.y1,
                                             start=self.start_ang, extent= -(self.extent),
                                             width=self.width, outline = 'blue', style='arc') #outline = 'orange'
        
        self.label_id = self.canvas.create_text(self.tx, self.ty, text=str(self.intensity_percent) + ' %',
                                                font=self.custom_font)