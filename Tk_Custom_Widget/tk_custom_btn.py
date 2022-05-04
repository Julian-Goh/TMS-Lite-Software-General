import tkinter as tk
from functools import partial
class WrappingButton(tk.Button):
    def __init__(self, master, **kwargs):
        tk.Button.__init__(self, master, **kwargs)
        # self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))
        self.bind('<Configure>', partial(self.__auto_resize))

    def __auto_resize(self, event):
        # print('btn width: ', self.winfo_width(), event.width)
        width = event.width - 6 ## padding of 6
        if width > 0:
            self.config(wraplength = width)
        else:
            self.config(wraplength = None)
        