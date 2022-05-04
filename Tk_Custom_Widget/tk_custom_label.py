import tkinter as tk
from functools import partial

class WrappingLabel(tk.Label):
    '''a type of Label that automatically adjusts the wrap to the size'''
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        # self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))
        self.bind('<Configure>', partial(self.__auto_resize))

    def __auto_resize(self, event):
        # print('label width: ', self.winfo_width())
        width = event.width - 6 ## padding of 6
        if width > 0:
            self.config(wraplength = width)
        else:
            self.config(wraplength = None)
            