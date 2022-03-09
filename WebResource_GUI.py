import os
from os import path

import tkinter as tk
from tkinter import ttk

from Tk_MsgBox.custom_msgbox import Ask_Msgbox, Info_Msgbox, Error_Msgbox, Warning_Msgbox

import subprocess

from PIL import ImageTk, Image
import numpy as np
from functools import partial

def _icon_load_resize(img_PATH, img_folder, img_file, img_scale = 0, img_width = 0, img_height = 0,
    img_conv = None, pil_filter = Image.BILINEAR):
    # pil_filter, Image.: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
    img = Image.open(img_PATH + "\\" + img_folder + "\\" + img_file)
    if img_conv is not None:
        try:
            img = img.convert("RGBA")
        except Exception:
            pass
    #print(img_file, img.mode)

    if img_scale !=0 and (img_width == 0 and img_height == 0):
        resize_w = round( np.multiply(img.size[0], img_scale) )
        resize_h = round( np.multiply(img.size[1], img_scale) )

        resize_img = img.resize((resize_w, resize_h), pil_filter)

        img_tk = ImageTk.PhotoImage(resize_img)
        return img_tk, img

    if img_scale ==0 and (img_width != 0 and img_height != 0):
        resize_img = img.resize((img_width, img_height), pil_filter)
        img_tk = ImageTk.PhotoImage(resize_img)
        return img_tk, img

    else:
        return None, img

def impil_resize(impil, img_scale = 0, img_width = 0, img_height = 0, pil_filter = Image.BILINEAR):
    # pil_filter, Image.: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
    if img_scale !=0:
        resize_w = round( np.multiply(impil.size[0], img_scale) )
        resize_h = round( np.multiply(impil.size[1], img_scale) )

        resize_img = impil.resize((resize_w, resize_h), pil_filter)
        return resize_img

    elif img_scale ==0 and (img_width != 0 and img_height != 0):
        resize_img = impil.resize((img_width, img_height), pil_filter)
        return resize_img
    else:
        raise AttributeError("Please pass value(s) for 'img_scale' OR ('img_width' and 'img_height'). If 'img_scale' is not given"+ 
            ", then resize process will use ('img_width' and 'img_height'). Otherwise, 'img_scale' is the defaulted priority.")

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

        _, self.math_theme_pil = _icon_load_resize(os.getcwd(), img_folder = "TMS Icon", img_file = "math_theme.png")
        _, self.light_theme_pil = _icon_load_resize(os.getcwd(), img_folder = "TMS Icon", img_file = "light_bulb_theme(2).jpg")

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
        self.resource_btn1.place(x = 15, y = self.curr_place_y, relx = 0, rely = 0, relwidth = 1, width = -30 - 20, anchor = 'nw')
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
        self.resource_btn2.place(x = 15, y = self.curr_place_y, relx = 0, rely = 0, relwidth = 1, width = -30 - 20, anchor = 'nw')
        self.resource_btn2.update_idletasks()

        self.curr_place_y = self.curr_place_y + (self.resource_btn2.winfo_height() + 20)

        self.scroll_canvas_class.resize_frame(height = self.curr_place_y)

    def btn_focus(self, event, tk_btn):
        tk_btn['state'] = 'active'
        tk_btn.focus_set()

    def btn_img_resize(self, event, tk_btn, pil_img):
        pil_img = impil_resize(pil_img, img_width = tk_btn.winfo_width(), img_height = tk_btn.winfo_height(), pil_filter = Image.BILINEAR)
        tk_img = ImageTk.PhotoImage(pil_img)
        tk_btn['image'] = tk_img
        tk_btn.image = tk_img

    def open_web_resource(self, file_name = "TMS - R&D Library.pdf"):
        err_flag = False
        folder_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\\TMS_Web_Resources"
        
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