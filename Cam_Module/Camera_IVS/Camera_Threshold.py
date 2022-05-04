import tkinter as tk
from tkinter.font import Font

from PIL import ImageTk, Image, ImageDraw, ImageFont
import os 
from os import path

from datetime import datetime

from tkinter import ttk
import numpy as np
import cv2
import re

from tesserocr import get_languages
from tesserocr import PyTessBaseAPI, PSM, OEM, RIL
import tesserocr

import threading

from functools import partial
from imageio import imread
import imutils

from Tk_MsgBox.custom_msgbox import Ask_Msgbox, Info_Msgbox, Error_Msgbox, Warning_Msgbox

from misc_module.os_create_folder import create_save_folder
from misc_module.TMS_file_save import cv_img_save, pil_img_save, PDF_img_save, PDF_img_list_save, np_to_PIL
from misc_module.tool_tip import CreateToolTip

from Tk_Custom_Widget.custom_zoom_class import CanvasImage

def validate_int_entry(d, P, S, only_positive = 'False'):
    # valid percent substitutions (from the Tk entry man page)
    # note: you only have to register the ones you need; this
    # example registers them all for illustrative purposes
    #
    # %d = Type of action (1=insert, 0=delete, -1 for others)
    # %i = index of char string to be inserted/deleted, or -1
    # %P = value of the entry if the edit is allowed
    # %s = value of entry prior to editing
    # %S = the text string being inserted or deleted, if any
    # %v = the type of validation that is currently set
    # %V = the type of validation that triggered the callback
    #      (key, focusin, focusout, forced)
    # %W = the tk name of the widget
    #print(only_positive, type(only_positive))
    if only_positive == 'False':
        if d == '1':
            if S == '-' and P == '-':
                return True 
            if P == '-0':
                return False
            if len(P) > 1 and (P.split('0')[0]) == '':
                return False
            else:
                try:
                    int(P)
                    return True
                except:
                    if P == '':
                        return True
                    else:
                        return False
        elif d == '0':
            return True

    elif only_positive == 'True':
        if d == '1':
            if len(P) > 1 and (P.split('0')[0]) == '':
                return False
            else:
                try:
                    int(P)
                    return True
                except:
                    if P == '':
                        return True
                    else:
                        return False
        elif d == '0':
            return True

def validate_float_entry(d, P, S, decimal_places = None):
    # valid percent substitutions (from the Tk entry man page)
    # note: you only have to register the ones you need; this
    # example registers them all for illustrative purposes
    #
    # %d = Type of action (1=insert, 0=delete, -1 for others)
    # %i = index of char string to be inserted/deleted, or -1
    # %P = value of the entry if the edit is allowed
    # %s = value of entry prior to editing
    # %S = the text string being inserted or deleted, if any
    # %v = the type of validation that is currently set
    # %V = the type of validation that triggered the callback
    #      (key, focusin, focusout, forced)
    # %W = the tk name of the widget
    #print(decimal_places, type(decimal_places)) #decimal_places
    try:
        int(decimal_places)
        if int(decimal_places) == 0: #decimal places cannot be 0
            decimal_places = None
    except (ValueError, TypeError):
        decimal_places = None
    #print('decimal_places: ',decimal_places)
    if decimal_places is None:
        if d == '1':
            try:
                #print(P)
                float(P)
                if float(P) >= 0 and S != '-': 
                    if len(P.split('.')) > 1 and len(P.split('.')[1]) > 2: #Default decimal places is 2
                        return False
                    return True
                else:
                    return False
            except ValueError:
                if not P:
                    return True
                else:
                    return False
        # elif d =='0':
        #     if i == '0' and P != '' and (P.split('.'))[0] == '': #Prevent user from deleting the 1st and only digit in front of a decimal point
        #         return False
        #     return True
        else:
            return True

    elif decimal_places is not None: #float check with significant figure check
        if d == '1':
            try:
                float(P)
                if float(P) >= 0 and S != '-':
                    if len(P.split('.')) > 1 and len(P.split('.')[1]) > int(decimal_places):
                        return False
                    return True
                else:
                    return False
            except ValueError:
                if not P:
                    return True
                else:
                    return False
        else:
            return True

def focusout_func(widget, val):
    if widget.get() == '':
        widget.insert(0, str(val))
    else:
        pass

class Camera_Threshold(tk.Frame):
    def __init__(self, master, master_scroll_class
        , custom_zoom_class
        , tk_img_format_sel
        , window_icon = None, inspect_icon = None
        , help_icon = None
        , fit_to_display_icon = None
        , add_icon = None, minus_icon = None
        , toggle_ON_btn_img = None
        , toggle_OFF_btn_img = None
        , **kwargs):

        self.sel_ori_btn = self.sel_R_btn = self.sel_G_btn = self.sel_B_btn = None
        if 'sel_ori_btn' in kwargs:
            self.sel_ori_btn = kwargs['sel_ori_btn']
            del kwargs['sel_ori_btn']

        if 'sel_R_btn' in kwargs:
            self.sel_R_btn = kwargs['sel_R_btn']
            del kwargs['sel_R_btn']

        if 'sel_G_btn' in kwargs:
            self.sel_G_btn = kwargs['sel_G_btn']
            del kwargs['sel_G_btn']

        if 'sel_B_btn' in kwargs:
            self.sel_B_btn = kwargs['sel_B_btn']
            del kwargs['sel_B_btn']

        # print(self.sel_ori_btn, self.sel_R_btn, self.sel_G_btn, self.sel_B_btn)
        tk.Frame.__init__(self, master, highlightthickness = 0, **kwargs)
        self.master_scroll_class = master_scroll_class
        self.master = master
        self.custom_zoom_class = custom_zoom_class
        self.tk_img_format_sel = tk_img_format_sel

        if isinstance(self.custom_zoom_class, CanvasImage) == False:
            raise TypeError("Please ensure that 'custom_zoom_class' is a CanvasImage class")

        self.window_icon = window_icon
        self.inspect_icon = inspect_icon
        self.help_icon = help_icon
        self.fit_to_display_icon = fit_to_display_icon
        self.add_icon = add_icon
        self.minus_icon = minus_icon
        self.toggle_ON_btn_img = toggle_ON_btn_img
        self.toggle_OFF_btn_img = toggle_OFF_btn_img

        self.__th_mode_str = 'simple' #'simple' or 'double'
        self.pixel_format = 'rgb' #'rgb' or 'mono'

        self.ivs_th_param = np.empty((4,), dtype = object)
        self.ivs_th_param[0] = np.array([0, 0, 255], dtype = np.uint8) #Mono: simple th, double th lower, double th upper
        self.ivs_th_param[1] = np.array([0, 0, 255], dtype = np.uint8) #Red: simple th, double th lower, double th upper
        self.ivs_th_param[2] = np.array([0, 0, 255], dtype = np.uint8) #Green: simple th, double th lower, double th upper
        self.ivs_th_param[3] = np.array([0, 0, 255], dtype = np.uint8) #Blue: simple th, double th lower, double th upper

        self.ctrl_panel_widget()
        self.np_arr_threshold_load()

        self.ivs_save_bool = False
        self.custom_save_bool = False

        self.ivs_msgbox_handle = None
        self.ivs_save_flag = False
        self.ivs_save_folder = None

        self.__custom_save_folder = None
        self.__custom_save_name = None
        self.__custom_save_overwrite = False

        self.__save_dir = os.path.join(os.environ['USERPROFILE'],  "TMS_Saved_Images")

    def np_arr_threshold_load(self):
        for i, tk_var in enumerate(self.mono_th_var_list):
            tk_var.set(self.ivs_th_param[0][i])

        for i, tk_var in enumerate(self.R_th_var_list):
            tk_var.set(self.ivs_th_param[1][i])

        for i, tk_var in enumerate(self.G_th_var_list):
            tk_var.set(self.ivs_th_param[2][i])

        for i, tk_var in enumerate(self.B_th_var_list):
            tk_var.set(self.ivs_th_param[3][i])


    def resize_font(self, event, parent, tk_font, min_size, max_size):
        print(event, tk_font.metrics())

    def validate_spinbox_callback(self, tk_spinbox = None, only_positive = True, *args, **kwargs):
        if isinstance(tk_spinbox, tk.Spinbox) == True:
            tk_spinbox['validate']='key'
            tk_spinbox['vcmd']=(tk_spinbox.register(validate_int_entry), '%d', '%P', '%S', only_positive)

    def del_lead_zero(self, event, tk_spinbox):
        if str(tk_spinbox.get()) == '0':
            tk_spinbox.selection_clear()
            tk_spinbox.focus_set()
            tk_spinbox.selection('range', 0, tk.END)

    def spinbox_focusout_callback(self, event, tk_spinbox, tk_var):
        if str(tk_spinbox.get()) == '':
            tk_spinbox.insert(0, tk_var.get())

    def simple_th_func(self, tk_var, tk_spinbox, th_type = 'mono'):
        if th_type == 'mono':
            self.ivs_th_param[0][0] = int(tk_var.get())
            if isinstance(self.sel_ori_btn, tk.Button):
                self.sel_ori_btn.invoke()

        elif th_type == 'red':
            self.ivs_th_param[1][0] = int(tk_var.get())
            if isinstance(self.sel_R_btn, tk.Button):
                self.sel_R_btn.invoke()

        elif th_type == 'green':
            self.ivs_th_param[2][0] = int(tk_var.get())
            if isinstance(self.sel_G_btn, tk.Button):
                self.sel_G_btn.invoke()

        elif th_type == 'blue':
            self.ivs_th_param[3][0] = int(tk_var.get())
            if isinstance(self.sel_B_btn, tk.Button):
                self.sel_B_btn.invoke()

        self.validate_spinbox_callback(tk_spinbox = tk_spinbox, only_positive = True)

    def simple_th_panel_init(self, master, label_name, w, h, th_type = 'mono'
        , th_value = 0):

        frame = tk.Frame(master, width = w, height = h, highlightthickness = 1, highlightbackground = 'black')
        #frame.place(x=0,y=300)

        main_lb = tk.Label(frame, text = label_name, font = 'Helvetica 11')

        sub_lb_1 = tk.Label(frame, text = 'Threshold:', font = 'Helvetica 11', justify = tk.LEFT, width = 8)

        int_var_1 = tk.IntVar(value = th_value)
        scale_1 = tk.Scale(frame, from_= 0, to= 255, resolution = 1, variable= int_var_1, orient='horizontal', showvalue=1)

        spinbox_1 = tk.Spinbox(master = frame, width = 5, textvariable = int_var_1, from_=0, to= 255, increment = 1
            , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        
        self.validate_spinbox_callback(tk_spinbox = spinbox_1)
        int_var_1.trace('w', lambda var_name, var_index, operation: self.simple_th_func(tk_spinbox = spinbox_1, tk_var = int_var_1, th_type = th_type))

        spinbox_1.bind('<KeyPress>', partial(self.del_lead_zero, tk_spinbox = spinbox_1))
        spinbox_1.bind('<FocusOut>', partial(self.spinbox_focusout_callback, tk_spinbox = spinbox_1, tk_var = int_var_1))

        main_lb.place(x=0 ,y=0, anchor = 'nw')

        sub_lb_1.place(x=0, y=49, anchor = 'nw')
        scale_1.place(x=75, y = 30, relwidth = 1, width = -75 - 80, anchor = 'nw')
        spinbox_1.place(x=-15, y = 47, relx = 1, anchor = 'ne')

        return frame, int_var_1, scale_1

    def double_th_func(self, tk_var, tk_spinbox, np_index = 1, th_type = 'mono'):
        ### np_index: 1 or 2 depending on custom_zoom_class.ivs_th_param target.
        param_index = min(2, max(np_index, 1))
        if th_type == 'mono':
            self.ivs_th_param[0][param_index] = int(tk_var.get())
            if isinstance(self.sel_ori_btn, tk.Button):
                self.sel_ori_btn.invoke()

        elif th_type == 'red':
            self.ivs_th_param[1][param_index] = int(tk_var.get())
            if isinstance(self.sel_R_btn, tk.Button):
                self.sel_R_btn.invoke()

        elif th_type == 'green':
            self.ivs_th_param[2][param_index] = int(tk_var.get())
            if isinstance(self.sel_G_btn, tk.Button):
                self.sel_G_btn.invoke()

        elif th_type == 'blue':
            self.ivs_th_param[3][param_index] = int(tk_var.get())
            if isinstance(self.sel_B_btn, tk.Button):
                self.sel_B_btn.invoke()

        self.validate_spinbox_callback(tk_spinbox = tk_spinbox, only_positive = True)


    def double_th_panel_init(self, master, label_name, w, h, th_type = 'mono'
        , th_lo_value = 0, th_hi_value = 255):

        frame = tk.Frame(master, width = w, height = h, highlightthickness = 1, highlightbackground = 'black')

        main_lb = tk.Label(frame, text = label_name, font = 'Helvetica 11')

        sub_lb_1 = tk.Label(frame, text = 'Threshold\n(Lower):', font = 'Helvetica 11', justify = tk.LEFT, width = 8)
        sub_lb_2 = tk.Label(frame, text = 'Threshold\n(Upper):', font = 'Helvetica 11', justify = tk.LEFT, width = 8)

        int_var_1 = tk.IntVar(value = th_lo_value)
        scale_1 = tk.Scale(frame, from_= 0, to= 255, resolution = 1, length = 150, variable= int_var_1, orient='horizontal', showvalue=1)

        spinbox_1 = tk.Spinbox(master = frame, width = 5, textvariable = int_var_1, from_=0, to= 255, increment = 1
            , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        
        self.validate_spinbox_callback(tk_spinbox = spinbox_1)
        int_var_1.trace('w', lambda var_name, var_index, operation: self.double_th_func(tk_spinbox = spinbox_1, tk_var = int_var_1, th_type = th_type, np_index = 1))

        spinbox_1.bind('<KeyPress>', partial(self.del_lead_zero, tk_spinbox = spinbox_1))
        spinbox_1.bind('<FocusOut>', partial(self.spinbox_focusout_callback, tk_spinbox = spinbox_1, tk_var = int_var_1))

        int_var_2 = tk.IntVar(value = th_hi_value)
        scale_2 = tk.Scale(frame, from_= 0, to= 255, resolution = 1, length = 150, variable= int_var_2, orient='horizontal', showvalue=1)

        spinbox_2 = tk.Spinbox(master = frame, width = 5, textvariable = int_var_2, from_=0, to= 255, increment = 1
            , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        
        self.validate_spinbox_callback(tk_spinbox = spinbox_2)
        int_var_2.trace('w', lambda var_name, var_index, operation: self.double_th_func(tk_spinbox = spinbox_2, tk_var = int_var_2, th_type = th_type, np_index = 2))

        spinbox_2.bind('<KeyPress>', partial(self.del_lead_zero, tk_spinbox = spinbox_2))
        spinbox_2.bind('<FocusOut>', partial(self.spinbox_focusout_callback, tk_spinbox = spinbox_2, tk_var = int_var_2))

        main_lb.place(x=0 ,y=0, anchor = 'nw')
        
        sub_lb_1.place(x=0, y=32, anchor = 'nw')
        scale_1.place(x=75, y = 30, relwidth = 1, width = -75 - 80, anchor = 'nw')
        spinbox_1.place(x=-15, y = 47, relx = 1, anchor = 'ne')


        sub_lb_2.place(x=0, y=77)
        scale_2.place(x=75, y = 75, relwidth = 1, width = -75 - 80, anchor = 'nw')
        spinbox_2.place(x=-15, y = 92, relx = 1, anchor = 'ne')

        return frame, int_var_1, int_var_2, scale_1, scale_2

    def pixel_format_switch(self, format_str = 'rgb'):
        if format_str == 'rgb':
            self.mono_th_fr_1.place_forget()
            self.R_th_fr_1.place(x=20, y = 20, relwidth = 1, width = -40, anchor = 'nw')
            self.G_th_fr_1.place(x=20, y = 160, relwidth = 1, width = -40, anchor = 'nw')
            self.B_th_fr_1.place(x=20, y = 300, relwidth = 1, width = -40, anchor = 'nw')

            self.mono_th_fr_2.place_forget()
            self.R_th_fr_2.place(x=20, y = 20, relwidth = 1, width = -40, anchor = 'nw')
            self.G_th_fr_2.place(x=20, y = 160, relwidth = 1, width = -40, anchor = 'nw')
            self.B_th_fr_2.place(x=20, y = 300, relwidth = 1, width = -40, anchor = 'nw')

            self.pixel_format = format_str

        elif format_str == 'mono':
            self.mono_th_fr_1.place(x=20, y = 20, relwidth = 1, width = -40, anchor = 'nw')
            self.R_th_fr_1.place_forget()
            self.G_th_fr_1.place_forget()
            self.B_th_fr_1.place_forget()

            self.mono_th_fr_2.place(x=20, y = 20, relwidth = 1, width = -40, anchor = 'nw')
            self.R_th_fr_2.place_forget()
            self.G_th_fr_2.place_forget()
            self.B_th_fr_2.place_forget()

            self.pixel_format = format_str

    def th_mode_select(self):
        # print(str(self.th_mode_var.get()), str(self.__th_mode_str))
        if str(self.th_mode_var.get()) != str(self.__th_mode_str):
            self.__th_mode_str = str(self.th_mode_var.get())
            if self.__th_mode_str == 'simple':
                self.single_th_fr.place(x = 0, y = 60, relx = 0, rely = 0, relwidth = 1, relheight = 1, width = 0, height = -60, anchor = 'nw')
                self.double_th_fr.place_forget()

            elif self.__th_mode_str == 'double':
                self.single_th_fr.place_forget()
                self.double_th_fr.place(x = 0, y = 60, relx = 0, rely = 0, relwidth = 1, relheight = 1, width = 0, height = -60, anchor = 'nw')

    def get_th_mode(self):
        return self.__th_mode_str

    def ctrl_panel_widget(self):
        self.radio_btn_fr = tk.Frame(self, bg = 'SystemButtonFace')
        self.radio_btn_fr['height'] = 60
        self.radio_btn_fr.place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 1, width = 0, anchor = 'nw')

        radiobtn_font = Font(self.radio_btn_fr, family="Helvetica", size= 12)

        # self.radio_btn_fr.bind('<Configure>', partial(self.resize_font, parent = self.radio_btn_fr
        #     , tk_font = radiobtn_font, min_size = 11, max_size = 14))

        self.th_mode_var = tk.StringVar(value = self.__th_mode_str)
        # self.simple_th_btn = tk.Radiobutton(self.radio_btn_fr, text='Simple\nThreshold', justify = tk.LEFT
        #     , variable=self.th_mode_var, value='simple'
        #     , font = radiobtn_font) 
        self.simple_th_btn = tk.Radiobutton(self.radio_btn_fr, text='Simple\nThreshold', justify = tk.LEFT
            , font = radiobtn_font
            , variable=self.th_mode_var, value='simple'
            , indicatoron = 0
            , selectcolor = 'SystemButtonFace'
            , disabledforeground = 'SystemButtonFace'
            , image=self.toggle_OFF_btn_img, selectimage=self.toggle_ON_btn_img, compound = tk.LEFT, bd = 0)

        self.simple_th_btn['command'] = self.th_mode_select
        self.simple_th_btn.place(x = 20, y = 0, relx = 0, rely = 0, relheight = 1, height = 0, anchor = 'nw')

        # self.double_th_btn = tk.Radiobutton(self.radio_btn_fr, text='Double\nThreshold', justify = tk.LEFT
        #     , variable=self.th_mode_var, value='double'
        #     , font = radiobtn_font)
        self.double_th_btn = tk.Radiobutton(self.radio_btn_fr, text='Double\nThreshold', justify = tk.LEFT
            , font = radiobtn_font
            , variable=self.th_mode_var, value='double'
            , indicatoron = 0
            , selectcolor = 'SystemButtonFace'
            , disabledforeground = 'SystemButtonFace'
            , image=self.toggle_OFF_btn_img, selectimage=self.toggle_ON_btn_img, compound = tk.LEFT, bd = 0)

        self.double_th_btn['command'] = self.th_mode_select
        self.double_th_btn.place(x = 20, y = 0, relx = 0.5, rely = 0, relheight = 1, height = 0, anchor = 'nw')


        self.single_th_fr = tk.Frame(self, bg = 'SystemButtonFace')
        self.single_th_fr.place(x = 0, y = 60, relx = 0, rely = 0, relwidth = 1, relheight = 1, width = 0, height = -60, anchor = 'nw')

        self.double_th_fr = tk.Frame(self, bg = 'SystemButtonFace')
        # self.double_th_fr.place(x = 0, y = 60, relx = 0, rely = 0, relwidth = 1, relheight = 1, width = 0, height = -60, anchor = 'nw')

        (self.mono_th_fr_1, self.mono_var_th, self.mono_scl_th) = self.simple_th_panel_init(self.single_th_fr, 'Monochrome', 270, 120, th_type = 'mono')

        (self.R_th_fr_1, self.R_var_th, self.R_scl_th) = self.simple_th_panel_init(self.single_th_fr, 'Red Channel', 270, 120, th_type = 'red')

        (self.G_th_fr_1, self.G_var_th, self.G_scl_th) = self.simple_th_panel_init(self.single_th_fr, 'Green Channel', 270, 120, th_type = 'green')

        (self.B_th_fr_1, self.B_var_th, self.B_scl_th) = self.simple_th_panel_init(self.single_th_fr, 'Blue Channel', 270, 120, th_type = 'blue')

        self.R_th_fr_1.place(x=20, y = 20, relwidth = 1, width = -40, anchor = 'nw')
        self.G_th_fr_1.place(x=20, y = 160, relwidth = 1, width = -40, anchor = 'nw')
        self.B_th_fr_1.place(x=20, y = 300, relwidth = 1, width = -40, anchor = 'nw')

        (self.mono_th_fr_2, self.mono_var_th_lo, self.mono_var_th_hi,
            self.mono_scl_th_lo, self.mono_scl_th_hi) = self.double_th_panel_init(self.double_th_fr, 'Monochrome', 270, 120, th_type = 'mono')

        (self.R_th_fr_2, self.R_var_th_lo, self.R_var_th_hi,
            self.R_scl_th_lo, self.R_scl_th_hi) = self.double_th_panel_init(self.double_th_fr, 'Red Channel', 270, 120, th_type = 'red')

        (self.G_th_fr_2, self.G_var_th_lo, self.G_var_th_hi,
            self.G_scl_th_lo, self.G_scl_th_hi) = self.double_th_panel_init(self.double_th_fr, 'Green Channel', 270, 120, th_type = 'green')

        (self.B_th_fr_2, self.B_var_th_lo, self.B_var_th_hi,
            self.B_scl_th_lo, self.B_scl_th_hi) = self.double_th_panel_init(self.double_th_fr, 'Blue Channel', 270, 120, th_type = 'blue')

        self.R_th_fr_2.place(x=20, y = 20, relwidth = 1, width = -40, anchor = 'nw')
        self.G_th_fr_2.place(x=20, y = 160, relwidth = 1, width = -40, anchor = 'nw')
        self.B_th_fr_2.place(x=20, y = 300, relwidth = 1, width = -40, anchor = 'nw')

        self.mono_th_var_list = [self.mono_var_th, self.mono_var_th_lo, self.mono_var_th_hi]
        self.R_th_var_list = [self.R_var_th, self.R_var_th_lo, self.R_var_th_hi]
        self.G_th_var_list = [self.G_var_th, self.G_var_th_lo, self.G_var_th_hi]
        self.B_th_var_list = [self.B_var_th, self.B_var_th_lo, self.B_var_th_hi]


    ############### '''IVS PROCESS + CAMERA'''

    def IVS_threshold_func(self, numArray, popout_var_mode):
        disp_flag = True
        if len(numArray.shape) == 3:
            if self.__th_mode_str == 'simple':
                bin_img_R = cv2.inRange(numArray[:,:, 0], int(self.ivs_th_param[1][0]), 255)
                bin_img_G = cv2.inRange(numArray[:,:, 1], int(self.ivs_th_param[2][0]), 255)
                bin_img_B = cv2.inRange(numArray[:,:, 2], int(self.ivs_th_param[3][0]), 255)

            elif self.__th_mode_str == 'double':
                bin_img_R = cv2.inRange(numArray[:,:, 0], int(self.ivs_th_param[1][1]), int(self.ivs_th_param[1][2]))
                bin_img_G = cv2.inRange(numArray[:,:, 1], int(self.ivs_th_param[2][1]), int(self.ivs_th_param[2][2]))
                bin_img_B = cv2.inRange(numArray[:,:, 2], int(self.ivs_th_param[3][1]), int(self.ivs_th_param[3][2]))

                if int(self.ivs_th_param[1][1]) == int(self.ivs_th_param[1][2]):
                    bin_img_R[:] = 0

                if int(self.ivs_th_param[2][1]) == int(self.ivs_th_param[2][2]):
                    bin_img_G[:] = 0

                if int(self.ivs_th_param[3][1]) == int(self.ivs_th_param[3][2]):
                    bin_img_B[:] = 0

            else:
                disp_flag = False
                self.custom_zoom_class.canvas_clear(init = False)
                self.clear_ivs_save_msg_box()

            if disp_flag == True:
                if popout_var_mode == 'original':
                    self.custom_zoom_class.canvas_default_load(img = numArray
                        , fit_to_display_bool = True
                        , display_width = self.custom_zoom_class.imframe.winfo_width()
                        , display_height = self.custom_zoom_class.imframe.winfo_height()
                        , hist_img_src = numArray)

                elif popout_var_mode == 'red':
                    self.custom_zoom_class.canvas_default_load(img = bin_img_R
                        , fit_to_display_bool = True
                        , display_width = self.custom_zoom_class.imframe.winfo_width()
                        , display_height = self.custom_zoom_class.imframe.winfo_height()
                        , hist_img_src = numArray)

                elif popout_var_mode == 'green':
                    self.custom_zoom_class.canvas_default_load(img = bin_img_G
                        , fit_to_display_bool = True
                        , display_width = self.custom_zoom_class.imframe.winfo_width()
                        , display_height = self.custom_zoom_class.imframe.winfo_height()
                        , hist_img_src = numArray)

                elif popout_var_mode == 'blue':
                    self.custom_zoom_class.canvas_default_load(img = bin_img_B
                        , fit_to_display_bool = True
                        , display_width = self.custom_zoom_class.imframe.winfo_width()
                        , display_height = self.custom_zoom_class.imframe.winfo_height()
                        , hist_img_src = numArray)

                self.IVS_save_func(numArray, bin_img_R = bin_img_R, bin_img_G = bin_img_G, bin_img_B = bin_img_B)

        elif len(numArray.shape) == 2:
            if self.__th_mode_str == 'simple':
                bin_img_mono = cv2.inRange(numArray, int(self.ivs_th_param[0][0]), 255)

            elif self.__th_mode_str == 'double':
                bin_img_mono = cv2.inRange(numArray, int(self.ivs_th_param[0][1]), int(self.ivs_th_param[0][2]))

                if int(self.ivs_th_param[0][1]) == int(self.ivs_th_param[0][2]):
                    bin_img_mono[:] = 0

            else:
                disp_flag = False
                self.custom_zoom_class.canvas_clear(init = False)
                self.clear_ivs_save_msg_box()

            if disp_flag == True:
                self.custom_zoom_class.canvas_default_load(img = bin_img_mono
                    , fit_to_display_bool = True
                    , display_width = self.custom_zoom_class.imframe.winfo_width()
                    , display_height = self.custom_zoom_class.imframe.winfo_height()
                    , hist_img_src = numArray)

                self.IVS_save_func(numArray, bin_img_mono = bin_img_mono)

    def __validate_bin_img(self, np_arr):
        if isinstance(np_arr, np.ndarray) == True and len(np_arr.shape) == 2:
            if np_arr.dtype is np.dtype(np.uint8):
                return True
            else:
                return False
        else:
            return False

    def set_custom_save_param(self, folder_name, file_name, overwrite_bool = False):
        self.__custom_save_folder = str(folder_name)
        self.__custom_save_name = str(file_name)
        self.__custom_save_overwrite = overwrite_bool

    def IVS_save_func(self, numArray, **kwargs):
        save_err = False
        img_type = None

        bin_img_R = bin_img_G = bin_img_B = bin_img_mono = None
        if isinstance(numArray, np.ndarray) == True and len(numArray.shape) == 3:
            if 'bin_img_R' in kwargs:
                bin_img_R = kwargs['bin_img_R']
            if 'bin_img_G' in kwargs:
                bin_img_G = kwargs['bin_img_G']
            if 'bin_img_B' in kwargs:
                bin_img_B = kwargs['bin_img_B']

            if True == self.__validate_bin_img(bin_img_R) and True == self.__validate_bin_img(bin_img_G) and True == self.__validate_bin_img(bin_img_B):
                img_type = 'rgb'
                save_err = False
            else:
                save_err = True

        elif isinstance(numArray, np.ndarray) == True and len(numArray.shape) == 2:
            if 'bin_img_mono' in kwargs:
                bin_img_mono = kwargs['bin_img_mono']
            if True == self.__validate_bin_img(bin_img_mono):
                img_type = 'mono'
                save_err = False
            else:
                save_err = True

        else:
            save_err = True

        if save_err == True:
            img_type = None
            self.ivs_save_bool = False
            self.custom_save_bool = False
            self.ivs_save_folder = None
            self.clear_ivs_save_msg_box()

        elif save_err == False:
            if self.ivs_save_bool == True and self.custom_save_bool == False:
                if img_type == 'rgb':
                    ''' User must use self.set_custom_save_param before this section of the code to run '''
                    img_format = self.tk_img_format_sel.get()
                    time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                    save_folder = create_save_folder(folder_dir = self.__save_dir)
                    sub_folder = create_save_folder(save_folder + '\\IVS-Threshold--' + time_id, duplicate = True)
                    
                    if str(img_format) == '.pdf':
                        _, id_index = PDF_img_save(sub_folder, numArray, 'Colour', ch_split_bool = False)
                        PDF_img_save(sub_folder, numArray[:,:,0], 'Red-Ch' + '--id{}'.format(id_index), ch_split_bool = False, overwrite = True)
                        PDF_img_save(sub_folder, numArray[:,:,1], 'Green-Ch' + '--id{}'.format(id_index), ch_split_bool = False, overwrite = True)
                        PDF_img_save(sub_folder, numArray[:,:,2], 'Blue-Ch' + '--id{}'.format(id_index), ch_split_bool = False, overwrite = True)

                        if self.__th_mode_str == 'simple':
                            PDF_img_save(sub_folder, bin_img_R
                                , 'Red-Th-({})'.format(self.ivs_th_param[1][0]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                            PDF_img_save(sub_folder, bin_img_G
                                , 'Green-Th-({})'.format(self.ivs_th_param[2][0]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                            PDF_img_save(sub_folder, bin_img_B
                                , 'Blue-Th-({})'.format(self.ivs_th_param[3][0]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                        elif self.__th_mode_str == 'double':
                            PDF_img_save(sub_folder, bin_img_R
                                , 'Red-Th-({}-{})'.format(self.ivs_th_param[1][1], self.ivs_th_param[1][2]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                            PDF_img_save(sub_folder, bin_img_G
                                , 'Green-Th-({}-{})'.format(self.ivs_th_param[2][1], self.ivs_th_param[2][2]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                            PDF_img_save(sub_folder, bin_img_B
                                , 'Blue-Th-({}-{})'.format(self.ivs_th_param[3][1], self.ivs_th_param[3][2]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                    else:
                        _, id_index = cv_img_save(sub_folder, numArray, 'Colour', str(img_format))
                        cv_img_save(sub_folder, numArray[:,:,0], 'Red-Ch' + '--id{}'.format(id_index), str(img_format), overwrite = True)
                        cv_img_save(sub_folder, numArray[:,:,1], 'Green-Ch' + '--id{}'.format(id_index), str(img_format), overwrite = True)
                        cv_img_save(sub_folder, numArray[:,:,2], 'Blue-Ch' + '--id{}'.format(id_index), str(img_format), overwrite = True)

                        if self.__th_mode_str == 'simple':
                            cv_img_save(sub_folder, bin_img_R
                                , 'Red-Th-({})'.format(self.ivs_th_param[1][0]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                            cv_img_save(sub_folder, bin_img_G
                                , 'Green-Th-({})'.format(self.ivs_th_param[2][0]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                            cv_img_save(sub_folder, bin_img_B
                                , 'Blue-Th-({})'.format(self.ivs_th_param[3][0]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                        elif self.__th_mode_str == 'double':
                            cv_img_save(sub_folder, bin_img_R
                                , 'Red-Th-({}-{})'.format(self.ivs_th_param[1][1], self.ivs_th_param[1][2]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                            cv_img_save(sub_folder, bin_img_G
                                , 'Green-Th-({}-{})'.format(self.ivs_th_param[2][1], self.ivs_th_param[2][2]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                            cv_img_save(sub_folder, bin_img_B
                                , 'Blue-Th-({}-{})'.format(self.ivs_th_param[3][1], self.ivs_th_param[3][2]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                    self.ivs_save_folder = sub_folder
                    self.ivs_save_flag = True

                elif img_type == 'mono':
                    img_format = self.tk_img_format_sel.get()
                    time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                    save_folder = create_save_folder(folder_dir = self.__save_dir)
                    sub_folder = create_save_folder(save_folder + '\\IVS-Threshold--' + time_id, duplicate = True)
                    
                    if str(img_format) == '.pdf':
                        _, id_index = PDF_img_save(sub_folder, numArray, 'Mono', ch_split_bool = False)

                        if self.__th_mode_str == 'simple':
                            PDF_img_save(sub_folder, bin_img_mono
                                , 'Mono-Th-({})'.format(self.ivs_th_param[0][0]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                        elif self.__th_mode_str == 'double':
                            PDF_img_save(sub_folder, bin_img_mono
                                , 'Mono-Th-({}-{})'.format(self.ivs_th_param[0][1], self.ivs_th_param[0][2]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                    else:
                        _, id_index = cv_img_save(sub_folder, numArray, 'Mono', str(img_format))

                        if self.__th_mode_str == 'simple':
                            cv_img_save(sub_folder, bin_img_mono
                                , 'Mono-Th-({})'.format(self.ivs_th_param[0][0]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                        elif self.__th_mode_str == 'double':
                            cv_img_save(sub_folder, bin_img_mono
                                , 'Mono-Th-({}-{})'.format(self.ivs_th_param[0][1], self.ivs_th_param[0][2]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)
                    
                    self.ivs_save_folder = sub_folder
                    self.ivs_save_flag = True

                else:
                    self.ivs_save_folder = None
                    self.clear_ivs_save_msg_box()

                self.ivs_save_bool = False


            elif self.ivs_save_bool == False and self.custom_save_bool == True:
                if img_type == 'rgb':
                    img_format = self.tk_img_format_sel.get()
                    sub_folder = str(self.__custom_save_folder)
                    file_name = str(self.__custom_save_name)

                    if str(img_format) == '.pdf':
                        _, id_index = PDF_img_save(sub_folder, numArray, file_name
                            , ch_split_bool = False
                            , kw_str = "(Colour)"
                            , overwrite = self.__custom_save_overwrite)

                        PDF_img_save(sub_folder, numArray[:,:,0]
                            , file_name + '-(Red-Ch)' + '--id{}'.format(id_index)
                            , ch_split_bool = False, overwrite = True)
                        PDF_img_save(sub_folder, numArray[:,:,1]
                            , file_name + '-(Green-Ch)' + '--id{}'.format(id_index)
                            , ch_split_bool = False, overwrite = True)
                        PDF_img_save(sub_folder, numArray[:,:,2]
                            , file_name + '-(Blue-Ch)' + '--id{}'.format(id_index)
                            , ch_split_bool = False, overwrite = True)

                        if self.__th_mode_str == 'simple':
                            PDF_img_save(sub_folder, bin_img_R
                                , file_name + '-(Red-Th-{})'.format(self.ivs_th_param[1][0]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                            PDF_img_save(sub_folder, bin_img_G
                                , file_name + '-(Green-Th-{})'.format(self.ivs_th_param[2][0]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                            PDF_img_save(sub_folder, bin_img_B
                                , file_name + '-(Blue-Th-{})'.format(self.ivs_th_param[3][0]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                        elif self.__th_mode_str == 'double':
                            PDF_img_save(sub_folder, bin_img_R
                                , file_name + '-(Red-Th-{}-{})'.format(self.ivs_th_param[1][1], self.ivs_th_param[1][2]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                            PDF_img_save(sub_folder, bin_img_G
                                , file_name + '-(Green-Th-{}-{})'.format(self.ivs_th_param[2][1], self.ivs_th_param[2][2]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                            PDF_img_save(sub_folder, bin_img_B
                                , file_name + '-(Blue-Th-{}-{})'.format(self.ivs_th_param[3][1], self.ivs_th_param[3][2]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                    else:
                        _, id_index = cv_img_save(sub_folder, numArray, file_name
                            , str(img_format)
                            , kw_str = "(Colour)"
                            , overwrite = self.__custom_save_overwrite)

                        cv_img_save(sub_folder, numArray[:,:,0]
                            , file_name + '-(Red-Ch)' + '--id{}'.format(id_index)
                            , str(img_format), overwrite = True)

                        cv_img_save(sub_folder, numArray[:,:,1]
                            , file_name + '-(Green-Ch)' + '--id{}'.format(id_index)
                            , str(img_format), overwrite = True)

                        cv_img_save(sub_folder, numArray[:,:,2]
                            , file_name + '-(Blue-Ch)' + '--id{}'.format(id_index)
                            , str(img_format), overwrite = True)

                        if self.__th_mode_str == 'simple':
                            cv_img_save(sub_folder, bin_img_R
                                , file_name + '-(Red-Th-{})'.format(self.ivs_th_param[1][0]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                            cv_img_save(sub_folder, bin_img_G
                                , file_name + '-(Green-Th-{})'.format(self.ivs_th_param[2][0]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                            cv_img_save(sub_folder, bin_img_B
                                , file_name + '-(Blue-Th-{})'.format(self.ivs_th_param[3][0]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                        elif self.__th_mode_str == 'double':
                            cv_img_save(sub_folder, bin_img_R
                                , file_name + '-(Red-Th-{}-{})'.format(self.ivs_th_param[1][1], self.ivs_th_param[1][2]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                            cv_img_save(sub_folder, bin_img_G
                                , file_name + '-(Green-Th-{}-{})'.format(self.ivs_th_param[2][1], self.ivs_th_param[2][2]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                            cv_img_save(sub_folder, bin_img_B
                                , file_name + '-(Blue-Th-{}-{})'.format(self.ivs_th_param[3][1], self.ivs_th_param[3][2]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                    self.ivs_save_folder = sub_folder
                    self.ivs_save_flag = True

                elif img_type == 'mono':
                    img_format = self.tk_img_format_sel.get()
                    sub_folder = self.__custom_save_folder
                    file_name = self.__custom_save_name
                    if str(img_format) == '.pdf':
                        _, id_index = PDF_img_save(sub_folder, numArray, file_name
                            , ch_split_bool = False
                            , kw_str = "(Mono)"
                            , overwrite = self.__custom_save_overwrite)

                        if self.__th_mode_str == 'simple':
                            PDF_img_save(sub_folder, bin_img_mono
                                , file_name + '-(Mono-Th-{})'.format(self.ivs_th_param[0][0]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                        elif self.__th_mode_str == 'double':
                            PDF_img_save(sub_folder, bin_img_mono
                                , file_name + '-(Mono-Th-{}-{})'.format(self.ivs_th_param[0][1], self.ivs_th_param[0][2]) + '--id{}'.format(id_index)
                                , ch_split_bool = False, overwrite = True)

                    else:
                        _, id_index = cv_img_save(sub_folder, numArray, file_name
                            , str(img_format)
                            , kw_str = "(Mono)"
                            , overwrite = self.__custom_save_overwrite)

                        if self.__th_mode_str == 'simple':
                            cv_img_save(sub_folder, bin_img_mono
                                , file_name + '-(Mono-Th-{})'.format(self.ivs_th_param[0][0]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                        elif self.__th_mode_str == 'double':
                            cv_img_save(sub_folder, bin_img_mono
                                , file_name + '-(Mono-Th-{}-{})'.format(self.ivs_th_param[0][1], self.ivs_th_param[0][2]) + '--id{}'.format(id_index)
                                , str(img_format), overwrite = True)

                    self.ivs_save_folder = sub_folder
                    self.ivs_save_flag = True

                else:
                    self.ivs_save_folder = None
                    self.clear_ivs_save_msg_box()

                self.custom_save_bool = False


    def ivs_save_msg_box(self):
        if self.ivs_save_flag == True:
            self.clear_ivs_save_msg_box()
            # print('IVS Save Msgbox Finished...')
            Info_Msgbox(message = 'Save IVS Image Success!' + '\n\n' + str(self.ivs_save_folder), title = 'IVS Save'
                , font = 'Helvetica 10', width = 400, height = 180)

        elif self.ivs_save_flag == False:
            self.ivs_msgbox_handle = self.after(100, self.ivs_save_msg_box)

    def clear_ivs_save_msg_box(self):
        if self.ivs_msgbox_handle is not None:
            self.after_cancel(self.ivs_msgbox_handle)
            del self.ivs_msgbox_handle
            self.ivs_msgbox_handle = None
            self.ivs_save_flag = False