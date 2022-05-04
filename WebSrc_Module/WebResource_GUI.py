import os
from os import path

import tkinter as tk

from Tk_MsgBox.custom_msgbox import Ask_Msgbox, Info_Msgbox, Error_Msgbox, Warning_Msgbox

from misc_module.image_resize import img_resize_dim, opencv_img_resize, pil_img_resize, open_pil_img
from misc_module.tk_img_module import *

import subprocess

from PIL import ImageTk, Image
import numpy as np
from functools import partial

class ResponsiveBtn(tk.Button):
    def __init__(self, master=None, **kwargs):
        tk.Button.__init__(self, master, **kwargs)
        bindings = {
                    '<FocusIn>': {'default':'active'},    # for Keyboard focus
                    '<FocusOut>': {'default': 'normal'},  
                    '<Enter>': {'state': 'active'},       # for Mouse focus
                    '<Leave>': {'state': 'normal'}
                    }
        for k, v in bindings.items():
            self.bind(k, lambda e, kwarg=v: e.widget.config(**kwarg))

class WebResource_GUI(tk.Frame):
    def __init__(self, parent, scroll_canvas_class, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.scroll_canvas_class = scroll_canvas_class

        pixel = tk.PhotoImage(width=1, height=1)

        self.curr_place_y = 10

        self.math_theme_pil  = open_pil_img(os.getcwd(), img_folder = "TMS Icon", img_file = "math_theme.png")
        self.light_theme_pil = open_pil_img(os.getcwd(), img_folder = "TMS Icon", img_file = "light_bulb_theme(2).jpg")

        self.grid_columnconfigure(index = 0, weight = 1)
        self.grid_rowconfigure(index = 0, weight = 1, uniform = 'default')
        self.grid_rowconfigure(index = 1, weight = 1, uniform = 'default')

        self.resource_btn1 = ResponsiveBtn(self, relief = tk.GROOVE, font = 'Helvetica 34', image = pixel, compound = 'center'
            , text = 'Common\nImage\nEquation', justify = tk.CENTER
            , activebackground = 'light goldenrod' #'light cyan'
            , highlightthickness = 5
            , highlightcolor = 'orange') #'dodger blue'
        self.resource_btn1.image = pixel
        self.resource_btn1['height'] = 300
        self.resource_btn1.bind('<Enter>', partial(self.btn_focus, tk_btn = self.resource_btn1))
        self.resource_btn1.bind('<Configure>', partial(self.btn_img_resize, tk_btn = self.resource_btn1, pil_img = self.math_theme_pil))

        self.resource_btn1['command'] = partial(self.open_web_resource, file_name = "TMS - R&D Library.pdf")
        self.resource_btn1.focus_set()
        self.resource_btn1.grid(column = 0, row = 0, rowspan = 1, columnspan = 1, padx = (5,5), pady = (10,1), sticky = 'nswe')

        self.resource_btn1.update_idletasks()

        self.curr_place_y = self.curr_place_y + (self.resource_btn1.winfo_height() + 20)


        self.resource_btn2 = ResponsiveBtn(self, relief = tk.GROOVE, font = 'Helvetica 34', image = pixel, compound = 'center'
            , text = 'Lab\nLighting', justify = tk.CENTER
            , activebackground = 'light goldenrod'
            , highlightthickness = 5
            , highlightcolor = 'orange')
        self.resource_btn2.image = pixel
        self.resource_btn2['height'] = 300
        self.resource_btn2.bind('<Enter>', partial(self.btn_focus, tk_btn = self.resource_btn2))
        self.resource_btn2.bind('<Configure>', partial(self.btn_img_resize, tk_btn = self.resource_btn2, pil_img = self.light_theme_pil ))

        self.resource_btn2['command'] = partial(self.open_web_resource, file_name = "Lab-Ligthing-Penang-11.2.22(latest).pdf")
        self.resource_btn2.focus_set()
        self.resource_btn2.grid(column = 0, row = 1, rowspan = 1, columnspan = 1, padx = (5,5), pady = (10,10), sticky = 'nswe')
        
        self.resource_btn2.update_idletasks()

        self.curr_place_y = self.curr_place_y + (self.resource_btn2.winfo_height() + 20)

        self.scroll_canvas_class.resize_frame(height = self.curr_place_y)

    def btn_focus(self, event, tk_btn):
        tk_btn['state'] = 'active'
        tk_btn.focus_set()

    def btn_img_resize(self, event, tk_btn, pil_img):
        tk_img_insert(tk_btn, pil_img, img_width = event.width, img_height = event.height, pil_filter = Image.BILINEAR)

    def open_web_resource(self, file_name = "TMS - R&D Library.pdf"):
        err_flag = False
        # folder_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\\TMS_Web_Resources"
        master_dir  = os.path.dirname(os.path.dirname(__file__))
        # print(master_dir)
        folder_path = master_dir + "\\TMS_Web_Resources"

        file_path = folder_path + "\\" + file_name
        
        if path.isfile(file_path) == True:
            err_flag = False
            
            proc_obj = subprocess.Popen(['explorer', file_path]
                , stdout = subprocess.PIPE ## To show output values
                , stderr = subprocess.STDOUT ## To hide err values
                )

        elif path.isfile(file_path) == False:
            err_flag = True

        if err_flag == True:
            Error_Msgbox(message = 'Corresponding File Does Not Exist!', title = 'Error Web Resource(s)'
                , font = 'Helvetica 11', message_anchor = 'c')
            