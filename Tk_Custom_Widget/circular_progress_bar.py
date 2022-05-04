try:
    import Tkinter as tk
    import tkFont
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    import tkinter.font as tkFont
    import tkinter.ttk as ttk
import numpy as np
import re

def round_float(value, place = 2):
    value = float(value)
    return float(f'{value:.{place}f}')

def str_float(value, place = 2):
    value = float(value)
    return f'{value:.{place}f}'

class CircularProgressbar(tk.Canvas):
    def __init__(self, master, pbar_w = 12, percent = 0, start_ang=90, full_extent=360, *args, **kwargs):
        tk.Canvas.__init__(self, master, *args, **kwargs)

        self.custom_font = tkFont.Font(family="Helvetica", size=12, weight='bold')

        self.__custom_tag = re.sub(".!", "", str(self))
        bindtags = list(self.bindtags())
        index = bindtags.index(".")
        bindtags.insert(index, self.__custom_tag)
        self.bindtags(tuple(bindtags))

        self.bind_class(self.__custom_tag, "<Configure>", self.resize_event)
        # print(self.bindtags())
        self.pbar_w = pbar_w

        self.x0, self.y0 = 0 + self.pbar_w, 0 + self.pbar_w
        self.x1, self.y1 = 0 - self.pbar_w, 0 - self.pbar_w
        self.tx, self.ty = 0 / 2, 0 / 2

        self.start_ang, self.full_extent = start_ang, full_extent
        self.percent = percent
        # # draw static bar outline
        w2 = self.pbar_w / 2
        self.oval_id1 = self.create_oval(self.x0-w2, self.y0-w2,
                                                self.x1+w2, self.y1+w2, outline = 'blue') #outline = 'black'
        self.oval_id2 = self.create_oval(self.x0+w2, self.y0+w2,
                                                self.x1-w2, self.y1-w2, outline = 'blue') #outline = 'black'

        self.extent = np.multiply(np.divide(self.percent, 100), 360) #negative extent is clockwise, positive is anti-clockwise
        if self.extent > 0 and self.extent % 360 == 0:
            self.extent = 359

        self.arc_id = self.create_arc(self.x0, self.y0, self.x1, self.y1,
                                             start=self.start_ang, extent= -(self.extent),
                                             width=self.pbar_w, outline = 'blue', style='arc') #outline = 'orange'
        str_percent = str_float(self.percent, 2)
        self.label_id = self.create_text(self.tx, self.ty, text='{} %'.format(str_percent),
                                                font=self.custom_font)


    def resize_event(self, event):
        # print("resize_event")
        w     = event.width
        h     = event.height
        if w > h:
            x0 = w/2 - h/2
            x1 = w/2 + h/2
            y0 = 0
            y1 = h

        elif w < h:
            x0 = 0
            x1 = w
            y0 = h/2 - w/2
            y1 = h/2 + w/2
            print(x0, y0, x1, y1)
        else:
            x0 = y0 = 0
            x1 = w
            y1 = h
        
        self.x0 = x0 + self.pbar_w
        self.y0 = y0 + self.pbar_w

        self.x1 = x1 - self.pbar_w
        self.y1 = y1 - self.pbar_w
        self.tx, self.ty = w / 2, h / 2
        w2 = self.pbar_w / 2

        self.coords(self.oval_id1, self.x0-w2, self.y0-w2, self.x1+w2, self.y1+w2)
        self.coords(self.oval_id2, self.x0+w2, self.y0+w2, self.x1-w2, self.y1-w2)
        self.coords(self.arc_id  , self.x0, self.y0, self.x1, self.y1)
        self.coords(self.label_id, self.tx, self.ty)


    def update_bar(self, percent):
        self.percent = percent
        self.extent = np.multiply(np.divide(self.percent, 100), 360) #negative extent is clockwise, positive is anti-clockwise
        if self.extent > 0 and self.extent % 360 == 0:
            self.extent = 359

        str_percent = str_float(self.percent, 2)
        self.itemconfig(self.arc_id, extent = -(self.extent))
        self.itemconfig(self.label_id, text = '{} %'.format(str_percent))
