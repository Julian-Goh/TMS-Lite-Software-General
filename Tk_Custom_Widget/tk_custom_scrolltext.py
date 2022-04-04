import tkinter as tk
from tkinter import ttk
import numpy as np
from Tk_Custom_Widget.tk_custom_text import CustomText

class CustomScrollText(tk.Frame):
    def __init__(self, master, scroll_canvas_class = None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.scroll_canvas_class = scroll_canvas_class

        self.frame_w = 1
        self.resize_event_w = 1
        
        self.frame_h = 1
        self.resize_event_h = 1

        if 'width' in kwargs:
            self.frame_w = kwargs['width']
            self.resize_event_w = kwargs['width'] #During init we set this equal to frame_w

        if 'height' in kwargs:
            self.frame_h = kwargs['height']
            self.resize_event_h = kwargs['height'] #During init we set this equal to frame_h

        self.txt_frame = tk.Frame(self, width = self.frame_w, height = self.frame_h)
        self.txt_frame.place(relx = 0, rely = 0, anchor='nw')
        self.bind("<Configure>", self.on_resize) #auto resize self.txt_frame

        # self.tk_txt = CustomSingleText(self.txt_frame, font = 'Helvetica 10', maxundo = -1, wrap = tk.WORD, relief = tk.GROOVE
        #     , undo = True
        #     , autoseparators=True)

        # self.tk_txt = tk.Text(self.txt_frame, font = 'Helvetica 10', maxundo = -1, wrap = tk.WORD, relief = tk.GROOVE)
        
        self.tk_str_var = tk.StringVar()
        self.tk_txt = CustomText(self.txt_frame, font = 'Helvetica 10', maxundo = -1, wrap = tk.WORD, relief = tk.GROOVE
            , undo = True
            , autoseparators=True
            , textvariable = self.tk_str_var)

        self.tk_scrolly = tk.Scrollbar(self, command= self.tk_txt.yview)

        self.tk_txt.place(relx=0, rely=0, relheight=1, relwidth=1, width = -16, anchor = 'nw')
        self.tk_scrolly.place(relx=1, rely=0, relheight=1, anchor='ne')

        self.tk_txt.configure(yscrollcommand= self.tk_scrolly.set)

        if self.scroll_canvas_class is not None:
            try:
                self.tk_txt.bind('<Enter>', self._bound_to_mousewheel)
                self.tk_txt.bind('<Leave>', self.scroll_canvas_class._bound_to_mousewheel)
            except Exception:
                pass

    def on_resize(self, event):
        # print('self.frame_w, self.frame_h: ', self.frame_w, self.frame_h)
        # print('event.width, event.height: ', event.width, event.height)
        self.resize_event_h = int(event.height)
        self.resize_event_w = int(event.width)

        if self.frame_h <= self.resize_event_h:
            self.txt_frame['height'] = self.resize_event_h

        elif self.frame_h > self.resize_event_h:
            self.txt_frame['height'] = self.frame_h

        if self.frame_w <= self.resize_event_w:
            self.txt_frame['width'] = self.resize_event_w

        elif self.frame_w > self.resize_event_w:
            self.txt_frame['width'] = self.frame_w

    def insert_readonly(self, *_args):
        self.tk_txt['state'] = 'normal'
        self.tk_txt.insert(*_args)
        self.tk_txt['state'] = 'disable'

    def delete_txt(self):
        # print("self.tk_txt['state']: ", self.tk_txt['state'])
        if self.tk_txt['state'] == 'normal':
            self.tk_txt.delete('1.0', tk.END)

        elif self.tk_txt['state'] == 'disabled':
            self.tk_txt['state'] = 'normal'
            # print("self.tk_txt['state']: ", self.tk_txt['state'])
            self.tk_txt.delete('1.0', tk.END)
            self.tk_txt['state'] = 'disable'
        
        # print('Delete TextBox')

    def _bound_to_mousewheel(self,event):
        #print('Enter')
        self.tk_txt.bind_all("<MouseWheel>", self._on_mousewheel)   

    def _unbound_to_mousewheel(self, event):
        #print('Leave')
        self.tk_txt.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.tk_txt.yview_scroll(int(-1*(event.delta/120)), "units")