####-- LIST OF GROUP FUNCTIONS -- ####
#1. CAMERA POPPOUT DISPLAY
#3. PIXEL COUNT + ROI GENERATION
#4. CAMERA DISPLAY & CONTROL GUI
#5. CAMERA CONNECTIONS
#6. CAMERA GUI FUNCTIONS (HIKVISION)

import os
from os import path
import sys
import time
from datetime import datetime

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import pathlib
import re

from Tk_MsgBox.custom_msgbox import Ask_Msgbox, Info_Msgbox, Error_Msgbox, Warning_Msgbox

from Tk_Custom_Widget.tk_custom_toplvl import CustomToplvl
from Tk_Custom_Widget.tk_custom_combobox import CustomBox

from PIL import ImageTk, Image, ImageDraw, ImageFont
import numpy as np
import cv2
import imageio

import imutils
from functools import partial
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from matplotlib.figure import Figure 
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import inspect
import ctypes
from ctypes import *

import threading
import msvcrt

from os_create_folder import open_save_folder
import image_resize

from ScrolledCanvas import ScrolledCanvas

from custom_zoom_class import CanvasImage
from tool_tip import CreateToolTip

from intvalidate import int_validate
code_PATH = os.getcwd()

sys.path.append(code_PATH + '\\MVS-Python\\MvImport')
from MvCameraControl_class import *

def time_convert(sec):
    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60
    return "{:02d}:{:02d}:{:02d}".format(int(hours),int(mins), int(round(sec)) )

def tk_float_verify(tk_widget, tk_var, min_val, max_val, revert_val, revert_bool = False):
    _type = None
    try:
        float(tk_var.get())
        _type = 'float'
    except Exception:
        if tk_var.get() == '':
            tk_var.set(revert_val)
        else:
            _type = None

    if _type == 'float':
        if float(tk_var.get()) < min_val:
            if revert_bool == True:
                tk_var.set(revert_val)
                tk_widget.icursor(tk.END)
            else:
                tk_var.set(min_val)
                tk_widget.icursor(tk.END)

        elif float(tk_var.get()) > max_val:

            if revert_bool == True:
                tk_var.set(revert_val)
                tk_widget.icursor(tk.END)
            else:
                tk_var.set(max_val)
                # print('max_val: ', max_val, tk_var.get())
                tk_widget.icursor(tk.END)
    
    if len(str(tk_var.get()).split('.')) > 1 and (str(tk_var.get()).split('.'))[0] == '':
        #e.g. if numbers are 00.1 or .1, it will become 0.1
        tk_var.set(float(tk_var.get()))
    else:
        pass

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
                    P_partition = P.split('.')
                    # print((P_partition[0]).split('0')[0])
                    if True == check_leading_zeros_decimal(P_partition[0]):
                        return False

                    elif False == check_leading_zeros_decimal(P_partition[0]):
                        if len(P_partition) > 1 and len(P_partition[1]) > int(decimal_places):
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

def check_leading_zeros_decimal(str_decimal):
    if type(str_decimal) == str:
        try:
            decimal = int(str_decimal)
            processed_decimal_str = str(decimal)

            if len(str_decimal) > len(processed_decimal_str):
                # print(str_decimal, processed_decimal_str, True)
                return True
            else:
                # print(str_decimal, processed_decimal_str, False)
                return False

        except:
            return False
            raise ValueError("Input argument error. Please input 'int'-type numbers or 'str'-type numbers.")
    else:
        return False
        raise ValueError("Input argument error. Please input 'str'-type numbers.")

def grp_widget_bind_focus(*widgets):#On Left Mouse Click the Widget is Focused
    for widget in widgets:
        widget.bind("<1>", lambda event: widget.focus_set())

def focusout_func(widget, val):
    if widget.get() == '':
        widget.insert(0, str(val))
    else:
        pass

def widget_enable(*widgets):
    for widget in widgets:
        try:
            widget['state'] = 'normal'
        except AttributeError:
            pass

def widget_disable(*widgets):
    for widget in widgets:
        try:
            widget['state'] = 'disabled'
        except AttributeError:
            pass

def clear_display_func(*canvas_widgets):
    for widget in canvas_widgets:
        widget.delete('all')

def Async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def Stop_thread(thread):
    Async_raise(thread.ident, SystemExit)

class Hikvision_GUI(tk.Frame):
    def __init__(self, master, scroll_canvas, obj_cam
        , cam_conn_status, cam_connect_class
        , tms_logo_2 = None, cam_disconnect_img = None
        , toggle_ON_button_img = None, toggle_OFF_button_img = None, img_flip_icon = None, record_start_icon = None, record_stop_icon = None
        , save_icon = None, popout_icon = None, info_icon = None, fit_to_display_icon = None, setting_icon = None, window_icon = None
        , inspect_icon= None, help_icon = None, add_icon = None, minus_icon = None
        , close_icon = None, video_cam_icon = None, refresh_icon = None, folder_impil = None, **kwargs):

        tk.Frame.__init__(self, master, **kwargs)
        
        self.save_img_format_list = ['.bmp', '.png', '.jpg', '.jpeg','.tiff', '.pdf']

        self.master = master

        self.scroll_canvas = scroll_canvas

        self.obj_cam_operation = obj_cam
        self.cam_conn_status = cam_conn_status

        self.cam_connect_class = cam_connect_class
        # self.stop_auto_enum_func = stop_auto_enum_func
        # self.cam_connect_btn_state = cam_connect_btn_state

        self.tms_logo_2 = tms_logo_2
        
        self.cam_disconnect_img = cam_disconnect_img
        self.toggle_ON_button_img = toggle_ON_button_img
        self.toggle_OFF_button_img = toggle_OFF_button_img
        
        self.img_flip_icon = img_flip_icon
        self.record_start_icon = record_start_icon
        self.record_stop_icon = record_stop_icon
        self.popout_icon = popout_icon
        self.save_icon = save_icon
        self.info_icon = info_icon
        self.fit_to_display_icon = fit_to_display_icon
        self.setting_icon = setting_icon
        self.window_icon = window_icon

        self.window_icon = window_icon
        self.inspect_icon = inspect_icon
        self.help_icon = help_icon
        self.add_icon = add_icon
        self.minus_icon = minus_icon
        self.close_icon = close_icon

        self.video_cam_icon = video_cam_icon
        self.refresh_icon = refresh_icon

        self.folder_icon = None
        if isinstance(folder_impil, Image.Image) == True:
            folder_impil = image_resize.pil_img_resize(folder_impil, img_width = 26, img_height = 26)
            self.folder_icon = ImageTk.PhotoImage(folder_impil)

        self.__save_dir = os.path.join(os.environ['USERPROFILE'],  "TMS_Saved_Images")
        self.__save_curr_dir = os.path.join(os.environ['USERPROFILE'],  "TMS_Saved_Images")

        self.imsave_msgbox_handle = None
        self.__start_grab = False

        ################################################
        self.popout_status = False
        self.popout_var_mode = 'original'

        self.cam_popout_disp = None
        self.cam_display_rgb = None
        self.cam_display_R = None
        self.cam_display_G = None
        self.cam_display_B = None

        self.set_custom_save_bool = tk.IntVar(value = 0)

        self.capture_img_status = tk.IntVar()
        self.capture_img_status.set(0)

        self.auto_graph_status = tk.IntVar()
        self.auto_graph_status.set(1)

        self.curr_roi_mode = None
        self.curr_graph_view = None

        self.hist_x_index = []
        for i in range(256):
            self.hist_x_index.append(i)

        self.auto_hist_update_handle = None
        self.auto_hist_init = False

        self.auto_profile_update_handle = None
        self.auto_profile_init = False

        self.revert_val_gain = self.revert_val_exposure = self.revert_val_framerate = False
        self.revert_val_brightness = False
        self.revert_val_red_ratio = self.revert_val_green_ratio = self.revert_val_blue_ratio = False
        self.revert_val_black_lvl = False
        self.revert_val_sharpness = False

        self.auto_gain_toggle = self.auto_exposure_toggle = self.framerate_toggle = False
        self.auto_white_toggle = False
        self.black_lvl_toggle = False
        self.sharpness_toggle = False
        self._pause_auto_toggle = False

        self.cam_display_width = 300
        self.cam_display_height = 250

        self.flip_img_bool = False

        self.auto_exposure_handle = None
        self.auto_gain_handle = None
        self.auto_white_handle = None

        self.cam_mode_str = 'continuous'
        self.cam_param_float = np.zeros((3), dtype=np.float32)
        #param_float index--> 0:exposure, 1:gain, 2:frame rate
        self.cam_param_int = np.zeros((6), dtype=np.uint16)
        self.cam_param_int[1] = self.cam_param_int[2] = self.cam_param_int[3] = 1
        #param_int index--> 0: brightness, 1: R-ch, 2: G-ch, 3: B-ch, 4: black level, 5: sharpness

        self.cam_sq_frame_cache = None
        self.tk_sq_disp_list = []


        self.record_bool = False
        self.record_msgbox_handle = None #used in tkinter thread to check for Msgbox

        self.rec_setting_param = np.zeros((3), dtype = np.object)
        self.rec_setting_param[1] = float(1) #Video Size
        self.rec_setting_param[2] = '' #Pixel Format
        self.rec_vid_size_list = []
        size = 10
        for _ in range(0,19):
            resize_option = str(size) + '%'
            self.rec_vid_size_list.append(resize_option)
            size = size + 5
        del size, resize_option

        self.main_frame = self

        self.btn_normal_cam_mode = tk.Button(self.main_frame, relief = tk.GROOVE, text = 'Normal Camera Mode')
        self.btn_normal_cam_mode['width'] = 17
        self.btn_normal_cam_mode['command'] = self.select_GUI_1

        self.btn_SQ_cam_mode = tk.Button(self.main_frame, relief = tk.GROOVE, text = 'SQ Camera Mode')
        self.btn_SQ_cam_mode['width'] = 17
        self.btn_SQ_cam_mode['command'] = self.select_GUI_2

        self.GUI_sel_btn_state(self.btn_normal_cam_mode, self.btn_SQ_cam_mode)

        self.btn_normal_cam_mode.place(x=0,y=0)
        self.btn_SQ_cam_mode.place(x = 140 + 10, y=0)

        self.popout_disp_tk_status = tk.StringVar() # 'Popout Live Display: Inactive' or 'Popout Live Display: Active'
        self.popout_disp_tk_label = tk.Label(self.main_frame, textvariable = self.popout_disp_tk_status, font = 'Helvetica 10 bold italic', fg = 'white')
        self.popout_disp_tk_label['bg'] = 'red'
        self.popout_disp_tk_label.place(x=0, y = 30)
        self.popout_disp_tk_status.set('Popout Live Display: Inactive')

        self.__display_mode = 'normal' ## Mode: 'normal', 'sq'
        self.__gui_size_mode = 0 ##Mode: 0: default size, 1: large size

        self.camera_display_GUI_1()
        self.camera_display_GUI_2()
        self.camera_control_GUI()
        #################################################################################################################################################
        self.cam_popout_gen()
        self.graph_popout_gen()
        self.record_setting_popout_gen()
        self.SQ_fr_popout_gen()

        self.cam_top_widget_place()

        self.select_GUI_1()

        self.camera_control_state()

    def gui_bbox_event(self, event):
        # print(event, self.__display_mode)
        ## widget.place_info()## Retrieve all the place information of a widget (e.g. x, y, relx, rely, relwidth, relheight, etc.)
        ## <------------------ edit-18-3-2022 (Test 2)------------------------------------>
        if event.width < 1410:
            mode = 0
            if mode != self.__gui_size_mode:
                self.__gui_size_mode = 0
                self.gui_resize_func()

        elif 1410 <= event.width:
            mode = 1
            if mode != self.__gui_size_mode:
                self.__gui_size_mode = 1
                self.gui_resize_func()

    def gui_resize_func(self):
        if self.__gui_size_mode == 0:
            self.scroll_canvas.resize_frame(width = 950)
            if self.__display_mode == 'normal':
                self.cam_disp_prnt.place_forget()
                self.cam_disp_prnt.place(x=0, y = 30+25, relwidth = 1, width = -312-10-15, relheight =1, height = -30-25-15, anchor = 'nw')
            elif self.__display_mode == 'sq':
                self.cam_disp_sq_prnt.place_forget()
                self.cam_disp_sq_prnt.place(x=0, y = 30+25, relwidth = 1, width = -312-10-15
                    , relheight =1, height = -30-25-15, anchor = 'nw')
            self.cam_ctrl_frame.place_forget()
            self.cam_ctrl_frame.place(x = -15, y = 30 + 25, relx = 1, rely = 0, relheight = 1, height = -(30+25)-15, anchor = 'ne')

        elif self.__gui_size_mode == 1:
            self.scroll_canvas.resize_frame(width = 1410 + 312 + 15)
            if self.__display_mode == 'normal':
                self.cam_disp_prnt.place_forget()
                self.cam_disp_prnt.place(x=0, y = 30+25, width = 1400, relheight =1, height = -30-25-15, anchor = 'nw')
            elif self.__display_mode == 'sq':
                self.cam_disp_sq_prnt.place_forget()
                self.cam_disp_sq_prnt.place(x=0, y = 30+25, width = 1400, relheight =1, height = -30-25-15, anchor = 'nw')
            self.cam_ctrl_frame.place_forget()
            self.cam_ctrl_frame.place(x = 1400 + 10, y = 30 + 25, relx = 0, rely = 0, relheight = 1, height = -(30+25)-15, relwidth = 1, width = -1400 - 10 - 15,anchor = 'nw')


    def widget_bind_focus(self, widget):
        widget.bind("<1>", lambda event: self.focus_set_func(widget))

    def focus_set_func(self, widget):
        widget.focus_set()
        self.main_frame.focus_set()

    def GUI_sel_btn_state(self, active_button, inactive_button1 = None):
        orig_colour_bg = 'snow2'
        active_button['disabledforeground'] = 'white'
        active_button['activeforeground'] = 'white'
        active_button['fg'] = 'white'
        active_button['activebackground'] = 'blue'
        active_button['bg'] = 'blue'
        active_button['font'] = 'Helvetica 10 bold'

        if isinstance(inactive_button1, tk.Button):
            inactive_button1['disabledforeground'] = 'gray'
            inactive_button1['activeforeground'] = 'black'
            inactive_button1['fg'] = 'black'
            inactive_button1['activebackground'] = orig_colour_bg
            inactive_button1['bg'] = orig_colour_bg
            inactive_button1['font'] = 'Helvetica 10'

    
    def cam_top_widget_place(self):
        self.popout_btn_gen()
        self.flip_btn_gen()
        self.record_btn_gen()

        x_place = lambda index: -10 - np.multiply(25+5, index)
        ## x_place is the x-coordinates of top widget (from the right). index is the index of the widget placement based on how many existing widget(s).
        ## E.g. Normal_cam_popout_btn is the 1st widget from the right, followed by flip_btn_1.

        self.Normal_cam_popout_btn.place(x = x_place(0), y= 0, relx = 1, rely = 0, anchor = 'ne')
        self.SQ_cam_popout_btn.place(x = x_place(0), y= 0, relx = 0.5, rely = 0, anchor = 'ne')
        self.SQ_fr_popout_btn.place(x = x_place(0), y= 0, relx = 1, rely = 0, anchor = 'ne')

        self.flip_btn_1.place(x = x_place(1), y= 2, relx = 1, rely = 0, anchor = 'ne')
        self.flip_btn_2.place(x = x_place(1), y= 2, relx = 0.5, rely = 0, anchor = 'ne')

        self.record_setting_btn.place(x = x_place(2), y= 2, relx = 1, rely = 0, anchor = 'ne')
        self.record_btn_1.place(x = x_place(3), y= 2, relx = 1, rely = 0, anchor = 'ne')

        self.time_lapse_label.place(x = x_place(4), y = 1, relx = 1, rely = 0, anchor = 'ne')

    def popout_btn_gen(self):
        #print(self.popout_icon)
        _master = self.cam_disp_prnt #self.main_frame
        self.Normal_cam_popout_btn = tk.Button(_master, relief = tk.GROOVE, bd =0 , image = self.popout_icon, bg = 'white')
        CreateToolTip(self.Normal_cam_popout_btn, 'Camera Pop-out Display'
            , 0, -22, width = 145, height = 20)

        self.Normal_cam_popout_btn['command'] = self.cam_popout_open

        self.SQ_cam_popout_btn = tk.Button(self.cam_disp_sq_prnt, relief = tk.GROOVE, bd =0 , image = self.popout_icon, bg = 'white')
        CreateToolTip(self.SQ_cam_popout_btn, 'Camera Pop-out Display'
            , 0, -22, width = 145, height = 20)

        self.SQ_cam_popout_btn['command'] = self.cam_popout_open

        self.SQ_fr_popout_btn = tk.Button(self.cam_disp_sq_prnt, relief = tk.GROOVE, bd =0 , image = self.popout_icon, bg = 'white')
        CreateToolTip(self.SQ_fr_popout_btn, 'Frame Pop-out Display'
            , 0, -22, width = 135, height = 20)

        self.SQ_fr_popout_btn['command'] = self.SQ_fr_popout_open

    def flip_btn_gen(self):
        _master = self.cam_disp_prnt #self.main_frame

        self.flip_btn_1 = tk.Button(_master, relief = tk.GROOVE, bd =0 , image = self.img_flip_icon, bg = 'white')
        CreateToolTip(self.flip_btn_1, 'Flip Image by 180' + chr(176)
            , 0, -22, width = 115, height = 20)
        self.flip_btn_1['command'] = self.flip_img_display

        self.flip_btn_2 = tk.Button(self.cam_disp_sq_prnt, relief = tk.GROOVE, bd =0 , image = self.img_flip_icon, bg = 'white')
        CreateToolTip(self.flip_btn_2, 'Flip Image by 180' + chr(176)
            , 0, -22, width = 115, height = 20)
        self.flip_btn_2['command'] = self.flip_img_display

    def record_btn_gen(self):
        _master = self.cam_disp_prnt #self.main_frame

        self.time_lapse_var = tk.StringVar()
        self.time_lapse_label = tk.Label(_master, textvariable = self.time_lapse_var, bg = 'white', font = 'Helvetica 11', anchor = 'e')
        self.time_lapse_var.set('')

        self.record_btn_1 = tk.Button(_master, relief = tk.GROOVE, bd =0 , bg = 'white')
        self.record_btn_1['image'] = self.record_start_icon

        CreateToolTip(self.record_btn_1, 'Record Video'
            , 0, -22, width = 80, height = 20)
        self.record_btn_1['command'] = self.record_start_func

        self.record_setting_btn = tk.Button(_master, relief = tk.GROOVE, bd =0 , bg = 'white')
        self.record_setting_btn['image'] = self.video_cam_icon

        CreateToolTip(self.record_setting_btn, 'Video Settings'
            , 0, -22, width = 88, height = 20)
        self.record_setting_btn['command'] = self.record_setting_open

    ###############################################################################################
    #1. CAMERA POPPOUT DISPLAY
    def check_cam_popout_disp(self):
        if False == self.cam_popout_toplvl.check_open():
            self.popout_disp_tk_status.set('Popout Live Display: Inactive')
            self.popout_disp_tk_label['bg'] = 'red'
        else:
            self.popout_disp_tk_status.set('Popout Live Display: Active')
            self.popout_disp_tk_label['bg'] = 'forest green'

    def cam_popout_gen(self):
        self.cam_popout_toplvl = CustomToplvl(self.main_frame, toplvl_title = 'Camera Display', min_w = 750, min_h = 600
            , icon_img = self.window_icon
            , bg = 'white'
            , topmost_bool = True
            , width = 750, height = 600)

        self.cam_popout_toplvl.protocol("WM_DELETE_WINDOW", self.cam_popout_close)
        self.cam_popout_init()

    def cam_popout_open(self):
        self.popout_status = True
        if False == self.cam_popout_toplvl.check_open():
            _toplvl = self.cam_popout_toplvl
            _toplvl.open()
            # print(_toplvl.winfo_width(), _toplvl.winfo_height())
            _toplvl_W = 750
            _toplvl_H = 600
            _toplvl.minsize(width = _toplvl_W, height = _toplvl_H)
            screen_width = _toplvl.winfo_screenwidth()
            screen_height = _toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (_toplvl_W/2))
            y_coordinate = int((screen_height/2) - (_toplvl_H/2))
            _toplvl.geometry("{}x{}+{}+{}".format(_toplvl_W, _toplvl_H, x_coordinate, y_coordinate))
            
            self.check_cam_popout_disp()

            self.sel_ori_btn.invoke()
            if self.__start_grab == False:
                self.cam_popout_disp.canvas_clear(init = True)
        else:
            self.cam_popout_toplvl.show()
        

    def popout_fit_to_display_func(self):
        try:
            # self.cam_popout_disp.fit_to_display(self.cam_popout_toplvl.winfo_width(),self.cam_popout_toplvl.winfo_height()-30-30-30)
            self.cam_popout_disp.fit_to_display(disp_W = self.cam_popout_disp.imframe.winfo_width(), disp_H = self.cam_popout_disp.imframe.winfo_height())
        except (AttributeError, tk.TclError):
            pass

    def popout_ch_sel_btn_gen(self):
        self.sel_ori_btn = tk.Button(self.cam_popout_toplvl, relief = tk.GROOVE, text = 'Original', font = 'Helvetica 10')
        self.sel_R_btn = tk.Button(self.cam_popout_toplvl, relief = tk.GROOVE, text = 'Red Channel', font = 'Helvetica 10')
        self.sel_G_btn = tk.Button(self.cam_popout_toplvl, relief = tk.GROOVE, text = 'Green Channel', font = 'Helvetica 10')
        self.sel_B_btn = tk.Button(self.cam_popout_toplvl, relief = tk.GROOVE, text = 'Blue Channel', font = 'Helvetica 10')

        self.sel_ori_btn['bg'] = 'snow4'
        self.sel_ori_btn['fg'] = 'white'
        self.sel_ori_btn['font'] = 'Helvetica 10 bold'

        self.sel_ori_btn['width'] = 12
        self.sel_R_btn['width'] = 12
        self.sel_G_btn['width'] = 12
        self.sel_B_btn['width'] = 12

        self.sel_ori_btn['command'] = lambda: self.popout_sel_btn_click('original', self.sel_ori_btn,
            self.sel_R_btn, self.sel_G_btn, self.sel_B_btn)

        self.sel_R_btn['command'] = lambda: self.popout_sel_btn_click('red', self.sel_R_btn, 
            self.sel_G_btn, self.sel_B_btn, self.sel_ori_btn)

        self.sel_G_btn['command'] = lambda: self.popout_sel_btn_click('green', self.sel_G_btn, 
            self.sel_B_btn, self.sel_ori_btn, self.sel_R_btn)

        self.sel_B_btn['command'] = lambda: self.popout_sel_btn_click('blue', self.sel_B_btn,
            self.sel_ori_btn, self.sel_R_btn, self.sel_G_btn)
        
        self.sel_ori_btn.place(x=0,y=0)
        self.sel_R_btn.place(x= 110, y=0)
        self.sel_G_btn.place(x= 220, y=0)
        self.sel_B_btn.place(x= 330, y=0)

    def popout_sel_btn_click(self, str_mode, master_btn ,*arg_btn):
        if str_mode == 'original':
            master_btn['bg'] = 'snow4'
        elif str_mode == 'red':
            master_btn['bg'] = 'red'
        elif str_mode == 'blue':
            master_btn['bg'] = 'blue'
        elif str_mode == 'green':
            master_btn['bg'] = 'green'

        master_btn['fg'] = 'white'
        master_btn['font'] = 'Helvetica 10 bold'

        for btn in arg_btn:
            btn['bg'] = 'SystemButtonFace'
            btn['fg'] = 'black'
            btn['font'] = 'Helvetica 10'

        self.popout_var_mode = str_mode

    def cam_popout_close(self):
        ### Close Popout Toplevel
        self.cam_popout_toplvl.close()
        ### Update Popout Status on Camera GUI
        self.check_cam_popout_disp()

        ### Reset Popout widget status
        self.popout_status = False
        self.popout_var_mode = 'original'

        ### Reset ROI status & widget(s)
        self.curr_roi_mode = None
        self.roi_status_var.set(0)
        self.roi_type_combobox.current(0)
        self.roi_type_combobox['state'] = 'disable'

        ### Reset Custom Zoom Img Display & ROI status
        self.cam_popout_disp.ROI_disable()
        self.cam_popout_disp.canvas_clear(init = True)

        ### Reset & Close Graph Popout & stop Graphs Tkinter Thread
        self.auto_graph_status.set(1)
        self.graph_popout_close()

    def cam_popout_init(self):
        clear_display_func(self.cam_display_rgb, self.cam_display_R, self.cam_display_G, self.cam_display_B, self.cam_disp_sq_live)
        self.popout_ch_sel_btn_gen()
        self.popout_save_btn = tk.Button(self.cam_popout_toplvl, relief = tk.GROOVE, image = self.save_icon, borderwidth=0)
        CreateToolTip(self.popout_save_btn, 'Save Image'
            , 0, -22, width = 75, height = 20)
        self.popout_save_btn.place(x= 450, y=5)
        self.popout_save_btn['command'] = self.img_save_func

        if self.cam_conn_status == False:
            self.popout_save_btn['state'] = 'disable'
        elif self.cam_conn_status == True:
            self.popout_save_btn['state'] = 'normal'

        self.cam_popout_disp = CanvasImage(self.cam_popout_toplvl)
        self.cam_popout_disp.place(x=0, y=30+30+30, relwidth = 1, relheight = 1
            , width = 0, height = -(30+30+30), anchor = 'nw')

        self.roi_status_var = tk.IntVar()
        self.roi_checkbtn = tk.Checkbutton(self.cam_popout_toplvl, text='ROI Enable', variable = self.roi_status_var, width = 8
            , onvalue=1, offvalue=0, highlightthickness = 0)#, bg = 'white')
        self.roi_checkbtn['command'] = self.roi_checkbtn_click
        self.roi_checkbtn.place(x=10,y=30)

        self.roi_type_list = ['BOX', 'LINE']
        self.roi_type_combobox = CustomBox(self.cam_popout_toplvl, values=self.roi_type_list, width=10, state='readonly', font = 'Helvetica 10')
        self.roi_type_combobox.unbind_class("TCombobox", "<MouseWheel>")
        self.roi_type_combobox.bind('<<ComboboxSelected>>', self.roi_type_sel)
        self.roi_type_combobox.current(0)
        self.roi_type_combobox['state'] = 'disable'
        self.roi_type_combobox.place(x=100, y=32)

        self.pixel_count_btn = tk.Button(self.cam_popout_toplvl, text = 'Pixel Count', relief = tk.GROOVE, font = 'Helvetica 10')
        self.pixel_count_btn['command'] = self.graph_popout_open
        self.pixel_count_btn.place(x=200, y=0+30)

        self.fit_to_display_btn = tk.Button(self.cam_popout_toplvl, relief = tk.GROOVE, image = self.fit_to_display_icon, borderwidth=0)
        self.fit_to_display_btn['command'] = lambda: self.cam_popout_disp.fit_to_display(disp_W = self.cam_popout_disp.imframe.winfo_width(), disp_H = self.cam_popout_disp.imframe.winfo_height())
        CreateToolTip(self.fit_to_display_btn, 'Fit-to-Screen'
            , 30, 0, width = 80, height = 20)
        self.fit_to_display_btn.place(x=480, y=3)

        unit_pixel = tk.PhotoImage(width=1, height=1)

        graph_update_mode_checkbtn = tk.Checkbutton(self.cam_popout_toplvl, text='Auto-Update Pixel Count'
            , variable = self.auto_graph_status, onvalue=1, offvalue=0, font = 'Helvetica 10')


        graph_update_mode_checkbtn['command'] = self.graph_update_mode
        graph_update_mode_checkbtn.place(x=290, y=0+30)

        self.popout_set_custom_save_btn = tk.Checkbutton(self.cam_popout_toplvl, text='Custom Save'
            , variable = self.set_custom_save_bool, onvalue=1, offvalue=0, anchor = 'nw'
            , justify = tk.LEFT, image = unit_pixel, compound = tk.CENTER)
        self.popout_set_custom_save_btn.image = unit_pixel
        self.popout_set_custom_save_btn['command'] = self.set_custom_save
        self.popout_set_custom_save_btn.place(x=520,y=0)

        self.popout_capture_img_btn = tk.Checkbutton(self.cam_popout_toplvl, text='Freeze Image'
            , variable = self.capture_img_status, onvalue=1, offvalue=0, anchor = 'nw'
            , justify = tk.LEFT, image = unit_pixel, compound = tk.CENTER)
        self.popout_capture_img_btn.image = unit_pixel
        self.popout_capture_img_btn.place(x=520,y=25)

        self.popout_set_custom_save_btn.update_idletasks()
        self.popout_capture_img_btn.update_idletasks()

        set_width = max(self.popout_set_custom_save_btn.winfo_width(), self.popout_capture_img_btn.winfo_width())
        self.popout_set_custom_save_btn['width'] = set_width - 28
        self.popout_capture_img_btn['width'] = set_width - 28
        del set_width


        self.help_widget = tk.Label(self.cam_popout_toplvl, bg = 'white', image = self.help_icon)
        CreateToolTip(self.help_widget, '1. LEFT-CLICK Mouse & Drag\n   to Move Image inside Image Display.\n' +
                                        '2. RIGHT-CLICK Mouse & Drag\n   to Draw ROI Box (with ROI enabled).\n' +
                                        '3. MOUSEWHEEL-UP to Zoom In.\n' +
                                        '4. MOUSEWHEEL-DOWN to Zoom Out.'
                    ,30, 0, width = 240, height = 100)
        self.help_widget.place(relx=1, x = -35, y = 30+30, anchor = 'nw')

    def popout_cam_disp_func(self, numArray):
        #print(self.popout_status)
        if True == self.cam_popout_toplvl.check_open():
            if len(numArray.shape) == 3:
                if self.popout_var_mode == 'original':
                    self.cam_popout_disp.canvas_default_load(img = numArray
                        , fit_to_display_bool = True
                        , display_width = self.cam_popout_disp.imframe.winfo_width()
                        , display_height = self.cam_popout_disp.imframe.winfo_height())

                elif self.popout_var_mode == 'red':
                    self.cam_popout_disp.canvas_default_load(img = numArray, local_img_split = True, ch_index = 0
                        , fit_to_display_bool = True
                        , display_width = self.cam_popout_disp.imframe.winfo_width()
                        , display_height = self.cam_popout_disp.imframe.winfo_height())

                elif self.popout_var_mode == 'green':
                    self.cam_popout_disp.canvas_default_load(img = numArray, local_img_split = True, ch_index = 1
                        , fit_to_display_bool = True
                        , display_width = self.cam_popout_disp.imframe.winfo_width()
                        , display_height = self.cam_popout_disp.imframe.winfo_height())

                elif self.popout_var_mode == 'blue':
                    self.cam_popout_disp.canvas_default_load(img = numArray, local_img_split = True, ch_index = 2
                        , fit_to_display_bool = True
                        , display_width = self.cam_popout_disp.imframe.winfo_width()
                        , display_height = self.cam_popout_disp.imframe.winfo_height())

            elif len(numArray.shape) == 2:
                self.cam_popout_disp.canvas_default_load(img = numArray
                    , fit_to_display_bool = True
                    , display_width = self.cam_popout_disp.imframe.winfo_width()
                    , display_height = self.cam_popout_disp.imframe.winfo_height())

        else:
            self.cam_popout_disp.canvas_clear(init = True)

    def roi_checkbtn_click(self):
        if self.roi_status_var.get() == 0:
            self.roi_type_combobox['state'] = 'disable'
            self.cam_popout_disp.ROI_disable()
            self.curr_roi_mode = None
            self.histogram_stop_auto_update()
            self.profile_stop_auto_update()

        elif self.roi_status_var.get() == 1:
            self.roi_type_combobox['state'] = 'readonly'
            self.roi_type_sel()

    def roi_type_sel(self,event = None):
        if self.roi_type_combobox.get() == self.roi_type_list[0]: #BOX
            if self.roi_type_combobox.get() != self.curr_roi_mode:
                self.curr_roi_mode = self.roi_type_combobox.get()
                self.cam_popout_disp.ROI_disable()

                _enable_status = self.cam_popout_disp.ROI_box_enable('Camera') #If Pop-out Display is Empty (No Image(s)) ROI Tool Cannot be Enabled

                if _enable_status == True:
                    if True == self.graph_popout_toplvl.check_open():
                        self.hist_clear_all()
                        self.profile_clear_all()
                        self.hist_view_btn.invoke()
                        self.profile_view_btn['state'] = 'disable'

                elif _enable_status == False:
                    self.curr_roi_mode = None
                    self.roi_status_var.set(0)
                    self.roi_type_combobox['state'] = 'disable'


        elif self.roi_type_combobox.get() == self.roi_type_list[1]: #LINE
            if self.roi_type_combobox.get() != self.curr_roi_mode:
                self.curr_roi_mode = self.roi_type_combobox.get()
                self.cam_popout_disp.ROI_disable()

                _enable_status = self.cam_popout_disp.ROI_line_enable('Camera') #If Pop-out Display is Empty (No Image(s)) ROI Tool Cannot be Enabled
                
                if _enable_status == True:
                    if True == self.graph_popout_toplvl.check_open():
                        self.hist_clear_all()
                        self.profile_clear_all()
                        self.profile_view_btn['state'] = 'normal'      

                elif _enable_status == False:
                    self.curr_roi_mode = None
                    self.roi_status_var.set(0)
                    self.roi_type_combobox['state'] = 'disable'

    def popout_ch_sel_btn_state(self, rgb_bool):
        if rgb_bool == True:
            widget_enable(self.sel_ori_btn, self.sel_R_btn, self.sel_G_btn, self.sel_B_btn)
        elif rgb_bool == False:
            widget_enable(self.sel_ori_btn)
            widget_disable(self.sel_R_btn, self.sel_G_btn, self.sel_B_btn)
            self.sel_ori_btn.invoke()

    ###############################################################################################
    #3. PIXEL COUNT + ROI GENERATION
    def graph_popout_gen(self):
        self.graph_popout_toplvl = CustomToplvl(self.main_frame, toplvl_title = 'Pixel Count Graph', min_w = 700, min_h = 600
            , icon_img = self.window_icon
            , bg = 'white'
            , topmost_bool = True
            , width = 700, height = 600)

        self.graph_popout_toplvl.protocol("WM_DELETE_WINDOW", self.graph_popout_close)
        self.graph_display_init()

    def graph_popout_open(self):
        if False == self.graph_popout_toplvl.check_open():
            _toplvl = self.graph_popout_toplvl
            _toplvl.open()
            screen_width = _toplvl.winfo_screenwidth()
            screen_height = _toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (_toplvl.winfo_width()/2))
            y_coordinate = int((screen_height/2) - (_toplvl.winfo_height()/2))
            _toplvl.geometry("{}x{}+{}+{}".format(_toplvl.winfo_width(), _toplvl.winfo_height(), x_coordinate, y_coordinate))

            self.hist_view_btn.invoke()
            #CHECKING THE PROFILE VIEW BUTTON STATUS     
            if self.roi_status_var.get() ==1 and self.roi_type_combobox.get() == self.roi_type_list[1]:
                self.profile_view_btn['state'] = 'normal'
            else:
                self.profile_view_btn['state'] = 'disable'
        else:
            self.graph_popout_toplvl.show()

    def graph_popout_close(self):
        self.histogram_stop_auto_update()
        self.profile_stop_auto_update()
        
        self.curr_graph_view = None
        
        self.graph_popout_toplvl.close()

        self.hist_scroll_class.scroll_reset()
        self.profile_scroll_class.scroll_reset()

        self.canvas_fr_hist_mono.place_forget()
        self.canvas_fr_hist_R.place_forget()
        self.canvas_fr_hist_G.place_forget()
        self.canvas_fr_hist_B.place_forget()

        self.toolbar_fr_hist_mono.place_forget()
        self.toolbar_fr_hist_R.place_forget()
        self.toolbar_fr_hist_G.place_forget()
        self.toolbar_fr_hist_B.place_forget()

        self.canvas_fr_profile_mono.place_forget()
        self.canvas_fr_profile_R.place_forget()
        self.canvas_fr_profile_G.place_forget()
        self.canvas_fr_profile_B.place_forget()

        self.toolbar_fr_profile_mono.place_forget()
        self.toolbar_fr_profile_R.place_forget()
        self.toolbar_fr_profile_G.place_forget()
        self.toolbar_fr_profile_B.place_forget()

    def graph_display_init(self):
        self.hist_scroll_class = ScrolledCanvas(master = self.graph_popout_toplvl, frame_w = 700, frame_h = 2300, 
            canvas_x = 0, canvas_y = 0 + 30, window_bg = 'white', canvas_bg='white', canvas_highlightthickness = 0)
        #self.hist_scroll_class.rmb_all_func()

        self.profile_scroll_class = ScrolledCanvas(master = self.graph_popout_toplvl, frame_w = 700, frame_h = 2300, 
            canvas_x = 0, canvas_y = 0 + 30, window_bg = 'white', canvas_bg='white', canvas_highlightthickness = 0)
        #self.profile_scroll_class.forget_all_func()

        self.hist_view_btn = tk.Button(self.graph_popout_toplvl, relief = tk.GROOVE, text = 'Histogram', font = 'Helvetica 10', width = 12)
        # self.hist_view_btn['command'] = lambda: self.graph_view_sel('histogram', self.hist_view_btn, self.profile_view_btn)
        self.hist_view_btn.place(x =0, y=0)

        self.profile_view_btn = tk.Button(self.graph_popout_toplvl, relief = tk.GROOVE, text = 'Profile', font = 'Helvetica 10', width = 12)
        # self.profile_view_btn['command'] = lambda: self.graph_view_sel('profile', self.profile_view_btn, self.hist_view_btn)
        self.profile_view_btn.place(x = 115, y=0)

        self.hist_view_btn['command'] = partial(self.graph_view_sel, 'histogram', self.hist_view_btn, self.profile_view_btn)
        self.profile_view_btn['command'] = partial(self.graph_view_sel, 'profile', self.profile_view_btn, self.hist_view_btn)

        graph_update_mode_checkbtn = tk.Checkbutton(self.graph_popout_toplvl, text='Auto-Update Pixel Count', variable = self.auto_graph_status, onvalue=1, offvalue=0, font = 'Helvetica 10')
        graph_update_mode_checkbtn['command'] = self.graph_update_mode
        graph_update_mode_checkbtn.place(x=230, y=1)

        self.hist_display_init()

        self.profile_display_init()


    def graph_view_sel(self, str_mode, master_btn, *arg_btn):
        if str_mode == 'histogram':
            if self.curr_graph_view != str_mode:
                self.profile_scroll_class.forget_all_func()
                self.hist_scroll_class.rmb_all_func()

                if self.cam_popout_disp is not None:
                    self.profile_stop_auto_update()
                    if self.cam_popout_disp.roi_line_exist == True and self.cam_popout_disp.roi_bbox_exist == False:
                        self.histogram_auto_update()
                    elif self.cam_popout_disp.roi_bbox_exist == True and self.cam_popout_disp.roi_line_exist == False:
                        self.histogram_auto_update()
                    else:
                        self.histogram_stop_auto_update()

                self.curr_graph_view = str_mode

                master_btn['bg'] = 'snow4'
                master_btn['fg'] = 'white'
                master_btn['font'] = 'Helvetica 10 bold'
                for btn in arg_btn:
                    btn['bg'] = 'SystemButtonFace'
                    btn['fg'] = 'black'
                    btn['font'] = 'Helvetica 10'

        elif str_mode == 'profile':
            if self.curr_graph_view != str_mode:
                self.profile_scroll_class.rmb_all_func()
                self.hist_scroll_class.forget_all_func()

                if self.cam_popout_disp is not None:
                    self.histogram_stop_auto_update()
                    if self.cam_popout_disp.roi_line_exist == True and self.cam_popout_disp.roi_bbox_exist == False:
                        self.profile_auto_update()
                    else:
                        self.profile_stop_auto_update()

                self.curr_graph_view = str_mode

                master_btn['bg'] = 'snow4'
                master_btn['fg'] = 'white'
                master_btn['font'] = 'Helvetica 10 bold'
                for btn in arg_btn:
                    btn['bg'] = 'SystemButtonFace'
                    btn['fg'] = 'black'
                    btn['font'] = 'Helvetica 10'

    def hist_display_init(self):
        self.hist_scroll_class.frame_h = 800
        self.hist_scroll_class.window_fr['height'] = 800
        self.hist_fig_mono = Figure(figsize = (7,7))

        self.plot_hist_mono = self.hist_fig_mono.add_subplot(111)
        self.plot_hist_mono.clear()
        self.hist_fig_mono.suptitle('Monochrome', fontsize=18)
        self.plot_hist_mono.set_ylabel('Pixel Count', fontsize=16)
        self.plot_hist_mono.set_xlabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_hist_mono = tk.Frame(self.hist_scroll_class.window_fr, height = 800 - 100, bg = 'white')

        self.hist_canvas_mono = FigureCanvasTkAgg(self.hist_fig_mono, master = self.canvas_fr_hist_mono)
        self.hist_canvas_mono.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_hist_mono = tk.Frame(self.hist_scroll_class.window_fr, height = 35, bg = 'white')
        self.toolbar_hist_mono = tkagg.NavigationToolbar2Tk(self.hist_canvas_mono, self.toolbar_fr_hist_mono)
        self.toolbar_hist_mono.update_idletasks()

        self.ax_plt_hist_mono = self.plot_hist_mono.plot([], [], color="grey")
        ##########################################################################################################################
        # self.hist_scroll_class.frame_h = 2300
        # self.hist_scroll_class.window_fr['height'] = 2300
        self.hist_fig_R = Figure(figsize = (7,7))
        self.plot_hist_R = self.hist_fig_R.add_subplot(111)
        self.plot_hist_R.clear()
        self.hist_fig_R.suptitle('Red Channel', fontsize=18)
        self.plot_hist_R.set_ylabel('Pixel Count', fontsize=16)
        self.plot_hist_R.set_xlabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_hist_R = tk.Frame(self.hist_scroll_class.window_fr, height = 800 - 100, bg = 'white')

        self.hist_canvas_R = FigureCanvasTkAgg(self.hist_fig_R, master = self.canvas_fr_hist_R)
        self.hist_canvas_R.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_hist_R = tk.Frame(self.hist_scroll_class.window_fr, height = 35, bg = 'white')
        self.toolbar_hist_R = tkagg.NavigationToolbar2Tk(self.hist_canvas_R, self.toolbar_fr_hist_R)
        self.toolbar_hist_R.update_idletasks()

        self.ax_plt_hist_R = self.plot_hist_R.plot([], [], color="red")

        ##########################################################################################################################
        self.hist_fig_G = Figure(figsize = (7,7))
        self.plot_hist_G = self.hist_fig_G.add_subplot(111)
        self.plot_hist_G.clear()
        self.hist_fig_G.suptitle('Green Channel', fontsize=18)
        self.plot_hist_G.set_ylabel('Pixel Count', fontsize=16)
        self.plot_hist_G.set_xlabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_hist_G = tk.Frame(self.hist_scroll_class.window_fr, height = 800 - 100, bg = 'white')

        self.hist_canvas_G = FigureCanvasTkAgg(self.hist_fig_G, master = self.canvas_fr_hist_G)
        self.hist_canvas_G.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_hist_G = tk.Frame(self.hist_scroll_class.window_fr, height = 35, bg = 'white')
        self.toolbar_hist_G = tkagg.NavigationToolbar2Tk(self.hist_canvas_G, self.toolbar_fr_hist_G)
        self.toolbar_hist_G.update_idletasks()

        self.ax_plt_hist_G = self.plot_hist_G.plot([], [], color="green")
        ##########################################################################################################################

        self.hist_fig_B = Figure(figsize = (7,7))
        self.plot_hist_B = self.hist_fig_B.add_subplot(111)
        self.plot_hist_B.clear()
        self.hist_fig_B.suptitle('Blue Channel', fontsize=18)
        self.plot_hist_B.set_ylabel('Pixel Count', fontsize=16)
        self.plot_hist_B.set_xlabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_hist_B = tk.Frame(self.hist_scroll_class.window_fr, height = 800 - 100, bg = 'white')

        self.hist_canvas_B = FigureCanvasTkAgg(self.hist_fig_B, master = self.canvas_fr_hist_B)
        self.hist_canvas_B.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_hist_B = tk.Frame(self.hist_scroll_class.window_fr, height = 35, bg = 'white')
        self.toolbar_hist_B = tkagg.NavigationToolbar2Tk(self.hist_canvas_B, self.toolbar_fr_hist_B)
        self.toolbar_hist_B.update_idletasks()

        self.ax_plt_hist_B = self.plot_hist_B.plot([], [], color="blue")

        # self.canvas_fr_hist_mono.place(x = 0, y = 0, relwidth = 1)
        # self.canvas_fr_hist_R.place(x = 0, y = 0, relwidth = 1)
        # self.canvas_fr_hist_G.place(x = 0, y = 750, relwidth = 1)
        # self.canvas_fr_hist_B.place(x = 0, y = 1500, relwidth = 1)

        # self.toolbar_fr_hist_mono.place(relx = 0.1, y = 700, relwidth = 0.8)
        # self.toolbar_fr_hist_R.place(relx = 0.1, y = 700, relwidth = 0.8)
        # self.toolbar_fr_hist_G.place(relx = 0.1, y = 1450, relwidth = 0.8)
        # self.toolbar_fr_hist_B.place(relx = 0.1, y = 2200, relwidth = 0.8)

    def profile_display_init(self):
        self.profile_scroll_class.frame_h = 800
        self.profile_scroll_class.window_fr['height'] = 800
        self.profile_fig_mono = Figure(figsize = (7,7))

        self.plot_profile_mono = self.profile_fig_mono.add_subplot(111)
        self.plot_profile_mono.clear()
        self.profile_fig_mono.suptitle('Monochrome', fontsize=18)
        self.plot_profile_mono.set_ylabel('Pixel Count', fontsize=16)

        self.canvas_fr_profile_mono = tk.Frame(self.profile_scroll_class.window_fr, height = 800 - 100, bg = 'white')

        self.profile_canvas_mono = FigureCanvasTkAgg(self.profile_fig_mono, master = self.canvas_fr_profile_mono)
        self.profile_canvas_mono.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_profile_mono = tk.Frame(self.profile_scroll_class.window_fr, height = 35, bg = 'white')
        self.toolbar_profile_mono = tkagg.NavigationToolbar2Tk(self.profile_canvas_mono, self.toolbar_fr_profile_mono)
        self.toolbar_profile_mono.update_idletasks()

        self.ax_plt_profile_mono = self.plot_profile_mono.plot([], [], color="grey")
        ##########################################################################################################################

        # self.profile_scroll_class.frame_h = 2300
        # self.profile_scroll_class.window_fr['height'] = 2300
        self.profile_fig_R = Figure(figsize = (7,7))
        self.plot_profile_R = self.profile_fig_R.add_subplot(111)
        self.plot_profile_R.clear()
        self.profile_fig_R.suptitle('Red Channel', fontsize=18)
        self.plot_profile_R.set_ylabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_profile_R = tk.Frame(self.profile_scroll_class.window_fr, height = 800 - 100, bg = 'white')

        self.profile_canvas_R = FigureCanvasTkAgg(self.profile_fig_R, master = self.canvas_fr_profile_R)
        self.profile_canvas_R.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_profile_R = tk.Frame(self.profile_scroll_class.window_fr, height = 35, bg = 'white')
        self.toolbar_profile_R = tkagg.NavigationToolbar2Tk(self.profile_canvas_R, self.toolbar_fr_profile_R)
        self.toolbar_profile_R.update_idletasks()

        self.ax_plt_profile_R = self.plot_profile_R.plot([], [], color="red")
        ##########################################################################################################################

        self.profile_fig_G = Figure(figsize = (7,7))
        self.plot_profile_G = self.profile_fig_G.add_subplot(111)
        self.plot_profile_G.clear()
        self.profile_fig_G.suptitle('Green Channel', fontsize=18)
        self.plot_profile_G.set_ylabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_profile_G = tk.Frame(self.profile_scroll_class.window_fr, height = 800 - 100, bg = 'white')

        self.profile_canvas_G = FigureCanvasTkAgg(self.profile_fig_G, master = self.canvas_fr_profile_G)
        self.profile_canvas_G.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_profile_G = tk.Frame(self.profile_scroll_class.window_fr, height = 35, bg = 'white')
        self.toolbar_profile_G = tkagg.NavigationToolbar2Tk(self.profile_canvas_G, self.toolbar_fr_profile_G)
        self.toolbar_profile_G.update_idletasks()

        self.ax_plt_profile_G = self.plot_profile_G.plot([], [], color="green")
        ##########################################################################################################################

        self.profile_fig_B = Figure(figsize = (7,7))
        self.plot_profile_B = self.profile_fig_B.add_subplot(111)
        self.plot_profile_B.clear()
        self.profile_fig_B.suptitle('Blue Channel', fontsize=18)
        self.plot_profile_B.set_ylabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_profile_B = tk.Frame(self.profile_scroll_class.window_fr, height = 800 - 100, bg = 'white')

        self.profile_canvas_B = FigureCanvasTkAgg(self.profile_fig_B, master = self.canvas_fr_profile_B)
        self.profile_canvas_B.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_profile_B = tk.Frame(self.profile_scroll_class.window_fr, height = 35, bg = 'white')
        self.toolbar_profile_B = tkagg.NavigationToolbar2Tk(self.profile_canvas_B, self.toolbar_fr_profile_B)
        self.toolbar_profile_B.update_idletasks()

        self.ax_plt_profile_B = self.plot_profile_B.plot([], [], color="blue")
        ##########################################################################################################################

        # self.canvas_fr_profile_mono.place(x = 0, y = 0, relwidth = 1)
        # self.canvas_fr_profile_R.place(x = 0, y = 0, relwidth = 1)
        # self.canvas_fr_profile_G.place(x = 0, y = 750, relwidth = 1)
        # self.canvas_fr_profile_B.place(x = 0, y = 1500, relwidth = 1)

        # self.toolbar_fr_profile_mono.place(relx = 0.1, y = 700, relwidth = 0.8)
        # self.toolbar_fr_profile_R.place(relx = 0.1, y = 700, relwidth = 0.8)
        # self.toolbar_fr_profile_G.place(relx = 0.1, y = 1450, relwidth = 0.8)
        # self.toolbar_fr_profile_B.place(relx = 0.1, y = 2200, relwidth = 0.8)

    def graph_draw_clear(self, fig_obj, canvas_tkagg, color = 'grey'):
        fig_obj.clear()
        canvas_tkagg.draw()
        return fig_obj.plot([], [], color = color)

    def hist_clear_all(self):
        self.ax_plt_hist_mono = self.graph_draw_clear(fig_obj = self.plot_hist_mono
            , canvas_tkagg = self.hist_canvas_mono, color = 'grey')
        self.ax_plt_hist_R = self.graph_draw_clear(fig_obj = self.plot_hist_R
            , canvas_tkagg = self.hist_canvas_R, color = 'red')
        self.ax_plt_hist_G = self.graph_draw_clear(fig_obj = self.plot_hist_G
            , canvas_tkagg = self.hist_canvas_G, color = 'green')
        self.ax_plt_hist_B = self.graph_draw_clear(fig_obj = self.plot_hist_B
            , canvas_tkagg = self.hist_canvas_B, color = 'blue')

    def profile_clear_all(self):
        self.ax_plt_profile_mono = self.graph_draw_clear(fig_obj = self.plot_profile_mono
            , canvas_tkagg = self.profile_canvas_mono, color = 'grey')
        self.ax_plt_profile_R = self.graph_draw_clear(fig_obj = self.plot_profile_R
            , canvas_tkagg = self.profile_canvas_R, color = 'red')
        self.ax_plt_profile_G = self.graph_draw_clear(fig_obj = self.plot_profile_G
            , canvas_tkagg = self.profile_canvas_G, color = 'green')
        self.ax_plt_profile_B = self.graph_draw_clear(fig_obj = self.plot_profile_B
            , canvas_tkagg = self.profile_canvas_B, color = 'blue')

    def graph_update_mode(self):
        if self.auto_graph_status.get() == 1:
            if self.curr_graph_view == 'histogram':
                self.histogram_auto_update()
            elif self.curr_graph_view == 'profile':
                self.profile_auto_update()
            pass
        elif self.auto_graph_status.get() == 0:
            self.profile_stop_auto_update()
            self.histogram_stop_auto_update()
            pass

    def hist_display_load(self):
        # print('auto_update: Histogram')
        # print('-----------------------')
        graph_data = None
        if self.cam_popout_disp.roi_bbox_exist ==  True:
            graph_data = self.cam_popout_disp.ROI_box_pixel_update()

        elif self.cam_popout_disp.roi_line_exist ==  True:
            (_, _, _, _, _, graph_data) = self.cam_popout_disp.ROI_line_pixel_update()

        if graph_data is not None:
            if len(graph_data) == 1:
                if self.auto_hist_init == False:
                    self.hist_scroll_class.frame_h = 800
                    self.hist_scroll_class.window_fr['height'] = 800
                    self.auto_hist_init = True

                self.graph_histogram_mono(graph_data[0])

            elif len(graph_data) == 3:
                if self.auto_hist_init == False:
                    self.hist_scroll_class.frame_h = 2300
                    self.hist_scroll_class.window_fr['height'] = 2300
                    self.auto_hist_init = True

                self.graph_histogram_R(graph_data[0])
                self.graph_histogram_G(graph_data[1])
                self.graph_histogram_B(graph_data[2])

    def histogram_auto_update(self):
        if True == self.graph_popout_toplvl.check_open():
            _loop_interval = 300 #450

            if self.auto_graph_status.get() == 1:
                self.auto_hist_update_handle = self.graph_popout_toplvl.custom_after(_loop_interval, self.histogram_auto_update)
            elif self.auto_graph_status.get() == 0:
                self.auto_hist_update_handle = None

            self.hist_display_load()

    def histogram_stop_auto_update(self):
        if self.auto_hist_update_handle is not None:
            self.graph_popout_toplvl.after_cancel(self.auto_hist_update_handle)
            del self.auto_hist_update_handle
            self.auto_hist_update_handle = None
            self.auto_hist_init = False

    def profile_display_load(self):
        # print('auto update: Profile')
        # print('-----------------------')
        if self.cam_popout_disp.roi_line_exist ==  True:
            (profile_data_index, profile_data_mono, profile_data_R
                , profile_data_G, profile_data_B, _) = self.cam_popout_disp.ROI_line_pixel_update()

            if len(profile_data_mono) > 0 and (len(profile_data_R) == 0 and len(profile_data_G) == 0 and len(profile_data_B) == 0):
                if self.auto_profile_init == False:
                    self.profile_scroll_class.frame_h = 800
                    self.profile_scroll_class.window_fr['height'] = 800
                    self.auto_profile_init = True

                self.graph_pixel_profile(profile_data_index, profile_data_mono, 'mono')

            elif len(profile_data_mono) == 0 and (len(profile_data_R) > 0 and len(profile_data_G) > 0 and len(profile_data_B) > 0):
                if self.auto_profile_init == False:
                    self.profile_scroll_class.frame_h = 2300
                    self.profile_scroll_class.window_fr['height'] = 2300
                    self.auto_profile_init = True

                self.graph_pixel_profile(profile_data_index, profile_data_R, 'red')
                self.graph_pixel_profile(profile_data_index, profile_data_G, 'green')
                self.graph_pixel_profile(profile_data_index, profile_data_B, 'blue')


    def profile_auto_update(self):
        if True == self.graph_popout_toplvl.check_open():
            _loop_interval = 300 #450

            if self.auto_graph_status.get() == 1:
                self.auto_profile_update_handle = self.graph_popout_toplvl.custom_after(_loop_interval, self.profile_auto_update)
            elif self.auto_graph_status.get() == 0:
                self.auto_profile_update_handle = None

            self.profile_display_load()

    def profile_stop_auto_update(self):
        if self.auto_profile_update_handle is not None:
            self.graph_popout_toplvl.after_cancel(self.auto_profile_update_handle)
            del self.auto_profile_update_handle
            self.auto_profile_update_handle = None
            self.auto_profile_init = False

    def graph_pixel_profile(self, data_1, data_2, str_img_type):
        if True == self.graph_popout_toplvl.check_open():
            _graph_spacing_x = int(round( np.multiply(np.max(data_1), 0.025) )) + 1
            _graph_spacing_y = int(round( np.multiply(np.max(data_2), 0.025) )) + 1

            if str_img_type == 'mono':
                _bool_canvas = bool(self.canvas_fr_profile_mono.winfo_ismapped())
                _bool_toolbar = bool(self.toolbar_fr_profile_mono.winfo_ismapped())

                if _bool_canvas == False:
                    self.canvas_fr_profile_mono.place(x = 0, y = 0, relwidth = 1)
                elif _bool_canvas == True:
                    pass
                if _bool_toolbar == False:
                    self.toolbar_fr_profile_mono.place(relx = 0.1, y = 700, relwidth = 0.8)
                elif _bool_toolbar == True:
                    pass

                self.ax_plt_profile_mono[0].set_data(data_1, data_2)

                self.plot_profile_mono.set_xlim(xmin=0-_graph_spacing_x, xmax=np.max(data_1)+_graph_spacing_x)
                self.plot_profile_mono.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(data_2)+_graph_spacing_y)
                self.profile_canvas_mono.draw()

            elif str_img_type == 'red':
                _bool_canvas = bool(self.canvas_fr_profile_R.winfo_ismapped())
                _bool_toolbar = bool(self.toolbar_fr_profile_R.winfo_ismapped())
                if _bool_canvas == False:
                    self.canvas_fr_profile_R.place(x = 0, y = 0, relwidth = 1)
                elif _bool_canvas == True:
                    pass
                if _bool_toolbar == False:
                    self.toolbar_fr_profile_R.place(relx = 0.1, y = 700, relwidth = 0.8)
                elif _bool_toolbar == True:
                    pass

                self.ax_plt_profile_R[0].set_data(data_1, data_2)

                self.plot_profile_R.set_xlim(xmin=0-_graph_spacing_x, xmax=np.max(data_1)+_graph_spacing_x)
                self.plot_profile_R.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(data_2)+_graph_spacing_y)
                self.profile_canvas_R.draw()

            elif str_img_type == 'green':
                _bool_canvas = bool(self.canvas_fr_profile_G.winfo_ismapped())
                _bool_toolbar = bool(self.toolbar_fr_profile_G.winfo_ismapped())
                if _bool_canvas == False:
                    self.canvas_fr_profile_G.place(x = 0, y = 750, relwidth = 1)
                elif _bool_canvas == True:
                    pass
                if _bool_toolbar == False:
                    self.toolbar_fr_profile_G.place(relx = 0.1, y = 1450, relwidth = 0.8)
                elif _bool_toolbar == True:
                    pass

                self.ax_plt_profile_G[0].set_data(data_1, data_2)

                self.plot_profile_G.set_xlim(xmin=0-_graph_spacing_x, xmax=np.max(data_1)+_graph_spacing_x)
                self.plot_profile_G.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(data_2)+_graph_spacing_y)
                self.profile_canvas_G.draw()

            elif str_img_type == 'blue':
                _bool_canvas = bool(self.canvas_fr_profile_B.winfo_ismapped())
                _bool_toolbar = bool(self.toolbar_fr_profile_B.winfo_ismapped())
                if _bool_canvas == False:
                    self.canvas_fr_profile_B.place(x = 0, y = 1500, relwidth = 1)
                elif _bool_canvas == True:
                    pass
                if _bool_toolbar == False:
                    self.toolbar_fr_profile_B.place(relx = 0.1, y = 2200, relwidth = 0.8)
                elif _bool_toolbar == True:
                    pass

                self.ax_plt_profile_B[0].set_data(data_1, data_2)

                self.plot_profile_B.set_xlim(xmin=0-_graph_spacing_x, xmax=np.max(data_1)+_graph_spacing_x)
                self.plot_profile_B.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(data_2)+_graph_spacing_y)
                self.profile_canvas_B.draw()

    def graph_histogram_mono(self, pixel_info = None):
        if True == self.graph_popout_toplvl.check_open():
            _bool_canvas = bool(self.canvas_fr_hist_mono.winfo_ismapped())
            _bool_toolbar = bool(self.toolbar_fr_hist_mono.winfo_ismapped())

            if _bool_canvas == False:
                self.canvas_fr_hist_mono.place(x = 0, y = 0, relwidth = 1)
            elif _bool_canvas == True:
                pass

            if _bool_toolbar == False:
                self.toolbar_fr_hist_mono.place(relx = 0.1, y = 700, relwidth = 0.8)
            elif _bool_toolbar == True:
                pass

            if pixel_info is not None and (isinstance(pixel_info, np.ndarray)) == True and pixel_info.shape[0] == 256 and pixel_info.shape[1] == 1:
                self.ax_plt_hist_mono[0].set_data(self.hist_x_index, pixel_info)

                _graph_spacing_x = int(round( np.multiply(np.max(self.hist_x_index), 0.025) )) + 1
                _graph_spacing_y = int(round( np.multiply(np.max(pixel_info), 0.025) )) + 1

                self.plot_hist_mono.set_xlim(xmin=0-_graph_spacing_x, xmax=255+_graph_spacing_x)
                self.plot_hist_mono.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(pixel_info)+_graph_spacing_y)
                self.hist_canvas_mono.draw()


    def graph_histogram_R(self, pixel_info = None):
        if True == self.graph_popout_toplvl.check_open():
            _bool_canvas = bool(self.canvas_fr_hist_R.winfo_ismapped())
            _bool_toolbar = bool(self.toolbar_fr_hist_R.winfo_ismapped())

            if _bool_canvas == False:
                self.canvas_fr_hist_R.place(x = 0, y = 0, relwidth = 1)
            elif _bool_canvas == True:
                pass

            if _bool_toolbar == False:
                self.toolbar_fr_hist_R.place(relx = 0.1, y = 700, relwidth = 0.8)
            elif _bool_toolbar == True:
                pass

            if pixel_info is not None and (isinstance(pixel_info, np.ndarray)) == True and pixel_info.shape[0] == 256 and pixel_info.shape[1] == 1:
                self.ax_plt_hist_R[0].set_data(self.hist_x_index, pixel_info)

                _graph_spacing_x = int(round( np.multiply(np.max(self.hist_x_index), 0.025) )) + 1
                _graph_spacing_y = int(round( np.multiply(np.max(pixel_info), 0.025) )) + 1

                self.plot_hist_R.set_xlim(xmin=0-_graph_spacing_x, xmax=255+_graph_spacing_x)
                self.plot_hist_R.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(pixel_info)+_graph_spacing_y)
                self.hist_canvas_R.draw()

    def graph_histogram_G(self, pixel_info = None):
        if True == self.graph_popout_toplvl.check_open():
            _bool_canvas = bool(self.canvas_fr_hist_G.winfo_ismapped())
            _bool_toolbar = bool(self.toolbar_fr_hist_G.winfo_ismapped())

            if _bool_canvas == False:
                self.canvas_fr_hist_G.place(x = 0, y = 750, relwidth = 1)
            elif _bool_canvas == True:
                pass

            if _bool_toolbar == False:
                self.toolbar_fr_hist_G.place(relx = 0.1, y = 1450, relwidth = 0.8)
            elif _bool_toolbar == True:
                pass
            
            if pixel_info is not None and (isinstance(pixel_info, np.ndarray)) == True and pixel_info.shape[0] == 256 and pixel_info.shape[1] == 1:
                self.ax_plt_hist_G[0].set_data(self.hist_x_index, pixel_info)

                _graph_spacing_x = int(round( np.multiply(np.max(self.hist_x_index), 0.025) )) + 1
                _graph_spacing_y = int(round( np.multiply(np.max(pixel_info), 0.025) )) + 1

                self.plot_hist_G.set_xlim(xmin=0-_graph_spacing_x, xmax=255+_graph_spacing_x)
                self.plot_hist_G.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(pixel_info)+_graph_spacing_y)
                self.hist_canvas_G.draw()

    def graph_histogram_B(self, pixel_info = None):
        if True == self.graph_popout_toplvl.check_open():
            _bool_canvas = bool(self.canvas_fr_hist_B.winfo_ismapped())
            _bool_toolbar = bool(self.toolbar_fr_hist_B.winfo_ismapped())

            if _bool_canvas == False:
                self.canvas_fr_hist_B.place(x = 0, y = 1500, relwidth = 1)
            elif _bool_canvas == True:
                pass

            if _bool_toolbar == False:
                self.toolbar_fr_hist_B.place(relx = 0.1, y = 2200, relwidth = 0.8)
            elif _bool_toolbar == True:
                pass

            if pixel_info is not None and (isinstance(pixel_info, np.ndarray)) == True and pixel_info.shape[0] == 256 and pixel_info.shape[1] == 1:
                self.ax_plt_hist_B[0].set_data(self.hist_x_index, pixel_info)

                _graph_spacing_x = int(round( np.multiply(np.max(self.hist_x_index), 0.025) )) + 1
                _graph_spacing_y = int(round( np.multiply(np.max(pixel_info), 0.025) )) + 1

                self.plot_hist_B.set_xlim(xmin=0-_graph_spacing_x, xmax=255+_graph_spacing_x)
                self.plot_hist_B.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(pixel_info)+_graph_spacing_y)
                self.hist_canvas_B.draw()

    ###############################################################################################
    #4. CAMERA DISPLAY & CONTROL GUI
    def select_GUI_1(self):
        # self.cam_disp_prnt.place(x=0, y = 30+25, anchor = 'nw')
        self.__display_mode = 'normal'
        self.gui_resize_func()

        self.cam_disp_sq_prnt.place_forget()
        self.GUI_sel_btn_state(self.btn_normal_cam_mode, self.btn_SQ_cam_mode)

        # self.btn_save_img.place(x=20, y=30)
        self.btn_save_img.place(x = -125, relx = 0.5
            , y = 30, rely = 0
            , anchor = 'nw')
        # self.set_custom_save_checkbtn.place(x=20, y = 60)
        self.set_custom_save_checkbtn.place(x = -130, relx = 0.5
            , y = 60, rely = 0
            , anchor = 'nw')
        # self.trigger_auto_save_checkbtn.place(x=20, y = 60 + 25)
        self.trigger_auto_save_checkbtn.place(x = -130, relx = 0.5
            , y = 85, rely = 0
            , anchor = 'nw')

        self.SQ_auto_save_checkbtn.place_forget()

        self.btn_save_sq.place_forget()

        self.check_cam_popout_disp()

    def select_GUI_2(self):
        self.__display_mode = 'sq'
        # self.cam_disp_sq_prnt.place(x=0, y=30+25)
        self.gui_resize_func()
        self.cam_disp_prnt.place_forget()
        self.GUI_sel_btn_state(self.btn_SQ_cam_mode, self.btn_normal_cam_mode)

        self.btn_save_img.place_forget()
        self.set_custom_save_checkbtn.place_forget()
        self.trigger_auto_save_checkbtn.place_forget()
        # self.SQ_auto_save_checkbtn.place(x=20, y = 60)
        self.SQ_auto_save_checkbtn.place(x = -130, relx = 0.5
            , y = 85, rely = 0
            , anchor = 'nw')

        # self.btn_save_sq.place(x=20, y=30)
        self.btn_save_sq.place(x = -125, relx = 0.5
            , y = 30, rely = 0
            , anchor = 'nw')

        self.check_cam_popout_disp()

    def flip_img_display(self):
        if self.flip_img_bool == False:
            self.flip_img_bool = True
        elif  self.flip_img_bool == True:
            self.flip_img_bool = False

        #print(self.flip_img_bool)

    def record_msg_box(self):
        if self.cam_conn_status == True:
            if self.obj_cam_operation.record_complete_flag == False and self.obj_cam_operation.record_warning_flag == False:
                self.record_msgbox_handle = self.cam_ctrl_frame.after(100, self.record_msg_box)

            else:
                if self.obj_cam_operation.record_complete_flag == True:
                    self.clear_record_msg_box()

                    Info_Msgbox(message = 'Video Record Complete!' + '\n\n' + str(self.obj_cam_operation.video_file), title = 'Video Record'
                        , font = 'Helvetica 10', width = 400)

                elif self.obj_cam_operation.record_warning_flag == True:
                    self.clear_record_msg_box()

                    Warning_Msgbox(message = 'Memory Usage reached 80%! Stopping Video Recording...'
                        + '\n\n' + 'Options for Longer Video Recording: '
                        + '\n' + 'a) Try reducing Video Resolution in the Video Setting.'
                        + '\n' + 'b) Set Camera to Monochrome Mode.'
                        + '\n' + 'c) Reduce Camera Framerate.', title = 'Memory Usage Warning', width = 400, height = 200)

        else:
            ##Just to flush out any left-over tkinter thread
            self.clear_record_msg_box()

    def clear_record_msg_box(self):
        if self.record_msgbox_handle is not None:
            self.cam_ctrl_frame.after_cancel(self.record_msgbox_handle)
            del self.record_msgbox_handle
            self.record_msgbox_handle = None
            self.obj_cam_operation.record_complete_flag = False
            self.obj_cam_operation.record_warning_flag = False

    def record_setting_popout_gen(self):
        self.record_setting_toplvl = CustomToplvl(self.cam_disp_prnt, toplvl_title = 'Video Control Settings', min_w = 300, min_h = 185
            , icon_img = self.window_icon
            , bg = 'white'
            , topmost_bool = False
            , width = 300, height = 185)

        self.record_setting_toplvl.resizable(0,0)

        self.record_setting_toplvl.protocol("WM_DELETE_WINDOW", self.record_setting_close)
        self.record_setting_init()

    def record_setting_open(self):
        if False == self.record_setting_toplvl.check_open():
            _toplvl = self.record_setting_toplvl
            _toplvl.open()
            screen_width = _toplvl.winfo_screenwidth()
            screen_height = _toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (_toplvl.winfo_width()/2))
            y_coordinate = int((screen_height/2) - (_toplvl.winfo_height()/2))
            _toplvl.geometry("{}x{}+{}+{}".format(_toplvl.winfo_width(), _toplvl.winfo_height(), x_coordinate, y_coordinate))

        else:
            self.record_setting_toplvl.show()

    def record_setting_close(self):
        self.record_setting_reset()
        self.record_setting_toplvl.close()

    def record_setting_init(self):
        _parent = self.record_setting_toplvl

        rec_label_framerate = tk.Label(_parent, bg = 'white', font = 'Helvetica 11', text = '1) Frame Rate:')
        self.rec_framerate_str = tk.StringVar()
        self.rec_entry_framerate = tk.Spinbox(_parent, textvariable = self.rec_framerate_str, font = 'Helvetica 11', highlightbackground="black", highlightthickness=1, width = 7, from_=1, to =1000)
        self.rec_framerate_str.set(self.rec_setting_param[0])


        self.rec_entry_framerate['validate']='key'
        self.rec_entry_framerate['vcmd']=(self.rec_entry_framerate.register(validate_float_entry),'%d', '%P', '%S', 2)
        self.rec_entry_framerate.bind('<Return>', lambda event: 
            self.record_framerate_callback(self.rec_entry_framerate, self.rec_framerate_str, 1, 1000, self.rec_setting_param[0], revert_bool = False))

        self.rec_entry_framerate.bind('<Tab>', lambda event: 
            self.record_framerate_callback(self.rec_entry_framerate, self.rec_framerate_str, 1, 1000, self.rec_setting_param[0], revert_bool = False))

        self.rec_entry_framerate.bind('<FocusOut>', lambda event: 
            self.record_framerate_callback(self.rec_entry_framerate, self.rec_framerate_str, 1, 1000, self.rec_setting_param[0], revert_bool = False))

        self.rec_entry_framerate.bind('<KeyRelease>', lambda event: 
            self.record_setting_focus_callback(data_type = 'framerate', event = event))

        self.rec_entry_framerate['command'] = lambda: self.record_framerate_callback(self.rec_entry_framerate, self.rec_framerate_str, 1, 1000, self.cam_param_float[2], revert_bool = False)

        self.rec_entry_framerate.bind('<FocusIn>', lambda event: self.record_setting_focus_callback)

        rec_label_framerate.place(x=5, y = 20)
        self.rec_entry_framerate.place(x=130, y = 20)

        #######################################################################################################################
        rec_label_vid_size = tk.Label(_parent, bg = 'white', font = 'Helvetica 11', text = '2) Video Size:')
        self.rec_vid_size_sel = CustomBox(_parent, values=self.rec_vid_size_list, width=6, state='readonly', font = 'Helvetica 11')
        self.rec_vid_size_sel.unbind_class("TCombobox", "<MouseWheel>")
        self.rec_vid_size_sel.bind('<<ComboboxSelected>>', lambda event: self.record_setting_focus_callback(data_type = 'vid_size'))

        if self.rec_setting_param[1] is None:
            self.rec_vid_size_sel.current(self.rec_vid_size_list.index('100%'))
            self.rec_setting_param[1] = np.divide(int( str(self.rec_vid_size_sel.get().strip('%')) ), 100)

        elif self.rec_setting_param[1] is not None:
            _vid_resize_str = str( int( np.multiply(self.rec_setting_param[1], 100) ) ) + '%'
            try:
                self.rec_vid_size_sel.current(self.rec_vid_size_list.index(_vid_resize_str))
            except ValueError:
                self.rec_vid_size_sel.current(self.rec_vid_size_list.index('100%'))
                self.rec_setting_param[1] = np.divide(int( str(self.rec_vid_size_sel.get().strip('%')) ), 100)

        rec_label_vid_size.place(x=5,  y=55)
        self.rec_vid_size_sel.place(x=130, y=55)

        #######################################################################################################################
        rec_label_pixel_format = tk.Label(_parent, bg = 'white', font = 'Helvetica 11', text = '3) Pixel Format:')
        self.rec_pixel_format_sel = CustomBox(_parent, values=self.pixel_format_list, width=15, state='readonly', font = 'Helvetica 11')
        self.rec_pixel_format_sel.unbind_class("TCombobox", "<MouseWheel>")
        self.rec_pixel_format_sel.bind('<<ComboboxSelected>>', lambda event: self.record_setting_focus_callback(data_type = 'pixel_format'))
        try:
            self.rec_pixel_format_sel.current(self.pixel_format_list.index(self.pixel_format_combobox.get()))
        except ValueError:
            self.rec_pixel_format_sel.set('')

        self.rec_setting_param[2] = self.rec_pixel_format_sel.get()

        rec_label_pixel_format.place(x=5,  y=90)
        self.rec_pixel_format_sel.place(x=130, y=90)

        #######################################################################################################################
        self.rec_noti_var = tk.StringVar()
        rec_noti_label = tk.Label(_parent, bg = 'white', font = 'Helvetica 10 bold italic', textvariable = self.rec_noti_var, justify = tk.CENTER)
        self.rec_noti_var.set('')

        rec_noti_label.place(x = 130, y = 140-5, anchor = 'ne')

        self.rec_reset_btn = tk.Button(_parent, relief = tk.GROOVE, width = 22, height = 22)
        self.rec_reset_btn['image'] = self.refresh_icon
        self.rec_reset_btn['command'] = self.record_setting_reset

        CreateToolTip(self.rec_reset_btn, 'Reset Video Settings'
            , 0, 30, width = 130, height = 20)

        self.rec_reset_btn.place(x = 135, y = 140)

        self.rec_execute_btn = tk.Button(_parent, relief = tk.GROOVE, width = 12, text = 'Apply Changes', font = 'Helvetica 11', highlightthickness = 0)
        self.rec_execute_btn['command'] = self.record_setting_execute
        self.rec_execute_btn.place(x=170,y = 140)

    def record_framerate_callback(self, tk_widget, tk_var, min_val, max_val, revert_val, revert_bool = False, event = None):
        tk_float_verify(tk_widget, tk_var, min_val, max_val, revert_val, revert_bool = revert_bool)
        # print(self.rec_setting_param)

    def record_setting_focus_callback(self, data_type, event = None):
        if data_type == 'framerate':
            try:
                framerate = float(self.rec_framerate_str.get())
                if framerate != self.rec_setting_param[0]:
                    self.rec_execute_btn['bg'] = 'gold'
                    self.rec_execute_btn['font'] = 'Helvetica 11 bold'

                elif framerate == self.rec_setting_param[0]:
                    self.rec_execute_btn['bg'] = 'SystemButtonFace'
                    self.rec_execute_btn['font'] = 'Helvetica 11'
            except ValueError:
                pass

        elif data_type == 'vid_size':
            vid_size = np.divide(int( str(self.rec_vid_size_sel.get().strip('%')) ), 100)
            if vid_size != self.rec_setting_param[1]:
                self.rec_execute_btn['bg'] = 'gold'
                self.rec_execute_btn['font'] = 'Helvetica 11 bold'

            elif vid_size == self.rec_setting_param[1]:
                self.rec_execute_btn['bg'] = 'SystemButtonFace'
                self.rec_execute_btn['font'] = 'Helvetica 11'

        elif data_type == 'pixel_format':
            pixel_format = str(self.rec_pixel_format_sel.get())
            if pixel_format != self.rec_setting_param[2]:
                self.rec_execute_btn['bg'] = 'gold'
                self.rec_execute_btn['font'] = 'Helvetica 11 bold'

            elif pixel_format == self.rec_setting_param[2]:
                self.rec_execute_btn['bg'] = 'SystemButtonFace'
                self.rec_execute_btn['font'] = 'Helvetica 11'

        self.rec_noti_var.set('')
        # print(event)

    def record_setting_reset(self):
        self.rec_framerate_str.set(self.rec_setting_param[0])

        vid_size_str = str(int(np.multiply(self.rec_setting_param[1], 100)) )+ '%'

        self.rec_vid_size_sel.current(self.rec_vid_size_list.index(vid_size_str))

        if self.rec_setting_param[2] == '':
            self.rec_pixel_format_sel.set('')
        try:
            self.rec_pixel_format_sel.current(self.pixel_format_list.index(self.rec_setting_param[2]))
        except ValueError:
            pass

        self.rec_execute_btn['bg'] = 'SystemButtonFace'
        self.rec_execute_btn['font'] = 'Helvetica 11'
        self.rec_noti_var.set('')

    def record_set_framerate(self):
        tk_float_verify(tk_widget = self.rec_entry_framerate
            , tk_var = self.rec_framerate_str, min_val = 1, max_val = 1000
            , revert_val = self.rec_setting_param[0], revert_bool = False)

        if self.rec_setting_param[0] != float(self.rec_framerate_str.get()):
            self.obj_cam_operation.frame_rate = float(self.rec_framerate_str.get())
            self.obj_cam_operation.Set_parameter_framerate(self.obj_cam_operation.frame_rate)
            if self.revert_val_framerate == False:
                #print('self.revert_val_framerate: False')
                self.cam_param_float[2] = self.obj_cam_operation.frame_rate
                self.framerate_str.set(self.cam_param_float[2])
                self.rec_setting_param[0] = self.obj_cam_operation.frame_rate

            elif self.revert_val_framerate == True:
                #print('self.revert_val_framerate: True')
                self.framerate_str.set(self.cam_param_float[2])
                self.rec_framerate_str.set(self.rec_setting_param[0])
                self.revert_val_framerate = False

    def record_setting_execute(self):
        now = datetime.now()
        dt_string = now.strftime("%H:%M:%S")
        self.rec_noti_var.set('Applied changes\n' + '(' + dt_string + ')')
        self.rec_execute_btn['bg'] = 'SystemButtonFace'
        self.rec_execute_btn['font'] = 'Helvetica 11'

        if self.cam_conn_status == True:
            #Video Recording Param: Input FrameRate
            if self.framerate_toggle == False:
                self.enable_framerate()
                if self.framerate_toggle == True:
                    self.record_set_framerate()

            elif self.framerate_toggle == True:
                self.record_set_framerate()

            #Video Recording Param: Input Pixel Format
            if self.obj_cam_operation.b_start_grabbing == True:
                if self.rec_setting_param[2] != str(self.rec_pixel_format_sel.get()):
                    self.stop_grabbing()
                    self.pixel_format_combobox.current(self.pixel_format_list.index(self.rec_pixel_format_sel.get()))

                    self.pixel_format_sel(pixel_format_str = str(self.rec_pixel_format_sel.get()))
                    self.rec_pixel_format_sel.current(self.pixel_format_list.index(self.pixel_format_combobox.get()))
                    self.rec_setting_param[2] = str(self.rec_pixel_format_sel.get())
                    self.start_grabbing()

            elif self.obj_cam_operation.b_start_grabbing == False:
                if self.rec_setting_param[2] != str(self.rec_pixel_format_sel.get()):
                    self.pixel_format_combobox.current(self.pixel_format_list.index(self.rec_pixel_format_sel.get()))
                    self.pixel_format_sel(pixel_format_str = str(self.rec_pixel_format_sel.get()))
                    self.rec_pixel_format_sel.current(self.pixel_format_list.index(self.pixel_format_combobox.get()))
                    self.rec_setting_param[2] = str(self.rec_pixel_format_sel.get())

        elif self.cam_conn_status == False:
            self.framerate_str.set(self.cam_param_float[2])
            self.rec_framerate_str.set(self.rec_setting_param[0])

            try:
                self.rec_pixel_format_sel.current(self.pixel_format_list.index(self.rec_setting_param[2]))
            except ValueError:
                self.rec_pixel_format_sel.set('')

            self.revert_val_framerate = False

        self.rec_setting_param[1] = np.divide(int( str(self.rec_vid_size_sel.get().strip('%')) ), 100)
        # print(self.rec_setting_param)

        pass

    def record_start_func(self):
        ask_msgbox = Ask_Msgbox('Do you want to record a video?'
            , parent = self.master, title = 'Video Record', message_anchor = 'w')
        
        if ask_msgbox.ask_result() == True:
            self.record_bool = True
            #print('RECORD!', self.record_bool)
            self.record_setting_btn['state'] = 'disable'
            self.record_setting_close()

            self.obj_cam_operation.record_warning_flag = False
            self.obj_cam_operation.record_complete_flag = False

            self.record_msg_box()

            self.record_btn_1['image'] = self.record_stop_icon
            self.record_btn_1['command'] = self.record_stop_func
            self.time_lapse_var.set('00:00:00')

        else:
            self.record_bool = False
            
            if True == self.record_setting_toplvl.check_open():
                self.record_setting_toplvl.custom_lift()

    def record_stop_func(self):
        self.record_bool = False
        self.obj_cam_operation.record_init = False
        self.time_lapse_var.set(time_convert(self.obj_cam_operation.elapse_time))

        self.record_btn_1['image'] = self.record_start_icon
        self.record_btn_1['command'] = self.record_start_func
        #print('STOPPED!', self.record_bool)

    def clear_display_GUI_1(self):
        clear_display_func(self.cam_display_R, self.cam_display_G, self.cam_display_B, self.cam_display_rgb)

    def clear_display_GUI_2(self):
        for tk_disp in self.tk_sq_disp_list:
            clear_display_func(tk_disp)

    def cam_display_place_GUI_1(self):
        # print(self.obj_cam_operation.Pixel_Format_Mono(self.pixel_format_combobox.get()), self.obj_cam_operation.Pixel_Format_Color(self.pixel_format_combobox.get()))
        if True == self.obj_cam_operation.Pixel_Format_Mono(self.pixel_format_combobox.get()):
            # self.ori_disp_label.place(x = 0, y = 0+30)
            self.ori_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
            self.R_disp_label.place_forget()
            self.G_disp_label.place_forget()
            self.B_disp_label.place_forget()

            self.cam_display_rgb.place(x = 0, y = 25, relx = 0, rely = 0, relwidth = 1, relheight = 1, height = -25, anchor = 'nw')
            self.cam_display_R.place_forget()
            self.cam_display_G.place_forget()
            self.cam_display_B.place_forget()

        elif True == self.obj_cam_operation.Pixel_Format_Color(self.pixel_format_combobox.get()):
            self.ori_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
            self.R_disp_label.place(x = 2, y = 0, relx = 0.5, rely = 0, anchor = 'nw')
            self.G_disp_label.place(x = 0, y = 0, relx = 0, rely = 0.5, anchor = 'nw')
            self.B_disp_label.place(x = 2, y = 0, relx = 0.5, rely = 0.5, anchor = 'nw')

            self.cam_display_rgb.place(x = 0, y = 25, relx = 0, rely = 0
                , relwidth = 0.5, width = -2
                , relheight = 0.5, height = -25
                , anchor = 'nw')
            self.cam_display_R.place(x = 2, y = 25, relx = 0.5, rely = 0
                , relwidth = 0.5, width = -2
                , relheight = 0.5, height = -25
                , anchor = 'nw')
            self.cam_display_G.place(x = 0, y = 25, relx = 0, rely = 0.5
                , relwidth = 0.5, width = -2
                , relheight = 0.5, height = -25
                , anchor = 'nw')
            self.cam_display_B.place(x = 2, y = 25, relx = 0.5, rely = 0.5
                , relwidth = 0.5, width = -2
                , relheight = 0.5, height = -25
                , anchor = 'nw')

        else:
            self.ori_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
            self.R_disp_label.place(x = 2, y = 0, relx = 0.5, rely = 0, anchor = 'nw')
            self.G_disp_label.place(x = 0, y = 0, relx = 0, rely = 0.5, anchor = 'nw')
            self.B_disp_label.place(x = 2, y = 0, relx = 0.5, rely = 0.5, anchor = 'nw')

            self.cam_display_rgb.place(x = 0, y = 25, relx = 0, rely = 0
                , relwidth = 0.5, width = -2
                , relheight = 0.5, height = -25
                , anchor = 'nw')
            self.cam_display_R.place(x = 2, y = 25, relx = 0.5, rely = 0
                , relwidth = 0.5, width = -2
                , relheight = 0.5, height = -25
                , anchor = 'nw')
            self.cam_display_G.place(x = 0, y = 25, relx = 0, rely = 0.5
                , relwidth = 0.5, width = -2
                , relheight = 0.5, height = -25
                , anchor = 'nw')
            self.cam_display_B.place(x = 2, y = 25, relx = 0.5, rely = 0.5
                , relwidth = 0.5, width = -2
                , relheight = 0.5, height = -25
                , anchor = 'nw')

    def cam_display_forget_GUI_1(self):
        self.ori_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
        self.R_disp_label.place(x = 5, y = 0, relx = 0.5, rely = 0, anchor = 'nw')
        self.G_disp_label.place(x = 0, y = 0, relx = 0, rely = 0.5, anchor = 'nw')
        self.B_disp_label.place(x = 5, y = 0, relx = 0.5, rely = 0.5, anchor = 'nw')

        self.cam_display_rgb.place_forget()
        self.cam_display_R.place_forget()
        self.cam_display_G.place_forget()
        self.cam_display_B.place_forget()

    def camera_display_GUI_1(self):
        self.cam_disp_prnt = tk.Frame(self.main_frame)
        self.cam_disp_prnt['bg'] = 'white'

        self.cam_disp_subprnt = tk.Frame(self.cam_disp_prnt)
        self.cam_disp_subprnt['bg'] = 'white'
        self.cam_disp_subprnt.place(x=0, y=30, relwidth = 1, relheight = 1, height = -30, anchor = 'nw')
        sub_parent = self.cam_disp_subprnt

        self.ori_disp_label = tk.Label(sub_parent, text = 'Original Image', font = 'Helvetica 12 bold', bg = 'snow3', fg = 'black')

        self.R_disp_label = tk.Label(sub_parent, text = 'Red Channel', font = 'Helvetica 12 bold', bg = 'red', fg = 'white')

        self.G_disp_label = tk.Label(sub_parent, text = 'Green Channel', font = 'Helvetica 12 bold', bg = 'green', fg = 'white')

        self.B_disp_label = tk.Label(sub_parent, text = 'Blue Channel', font = 'Helvetica 12 bold', bg = 'blue', fg = 'white')

        self.ori_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
        self.R_disp_label.place(x = 2, y = 0, relx = 0.5, rely = 0, anchor = 'nw')
        self.G_disp_label.place(x = 0, y = 0, relx = 0, rely = 0.5, anchor = 'nw')
        self.B_disp_label.place(x = 2, y = 0, relx = 0.5, rely = 0.5, anchor = 'nw')

        self.dummy_canvas_rgb = tk.Canvas(sub_parent, width = self.cam_display_width, height = self.cam_display_height, bg = 'snow3', highlightthickness = 0)
        self.dummy_canvas_R = tk.Canvas(sub_parent, width = self.cam_display_width, height = self.cam_display_height, bg = 'red', highlightthickness = 0)
        self.dummy_canvas_G = tk.Canvas(sub_parent, width = self.cam_display_width, height = self.cam_display_height, bg = 'green', highlightthickness = 0)
        self.dummy_canvas_B = tk.Canvas(sub_parent, width = self.cam_display_width, height = self.cam_display_height, bg = 'blue', highlightthickness = 0)

        self.cam_display_rgb = tk.Canvas(sub_parent, width = self.cam_display_width, height = self.cam_display_height, bg = 'snow3', highlightthickness = 0)
        self.cam_display_R = tk.Canvas(sub_parent, width = self.cam_display_width, height = self.cam_display_height, bg = 'red', highlightthickness = 0)
        self.cam_display_G = tk.Canvas(sub_parent, width = self.cam_display_width, height = self.cam_display_height, bg = 'green', highlightthickness = 0)
        self.cam_display_B = tk.Canvas(sub_parent, width = self.cam_display_width, height = self.cam_display_height, bg = 'blue', highlightthickness = 0)

        self.dummy_canvas_rgb.bind('<Configure>', lambda e: self.camera_disconnect_disp(event = e, tk_canvas = self.dummy_canvas_rgb))
        self.dummy_canvas_R.bind('<Configure>', lambda e: self.camera_disconnect_disp(event = e, tk_canvas = self.dummy_canvas_R))
        self.dummy_canvas_G.bind('<Configure>', lambda e: self.camera_disconnect_disp(event = e, tk_canvas = self.dummy_canvas_G))
        self.dummy_canvas_B.bind('<Configure>', lambda e: self.camera_disconnect_disp(event = e, tk_canvas = self.dummy_canvas_B))

        self.dummy_canvas_rgb.place(x = 0, y = 25, relx = 0, rely = 0
            , relwidth = 0.5, width = -2
            , relheight = 0.5, height = -25
            , anchor = 'nw')
        self.dummy_canvas_R.place(x = 2, y = 25, relx = 0.5, rely = 0
            , relwidth = 0.5, width = -2
            , relheight = 0.5, height = -25
            , anchor = 'nw')
        self.dummy_canvas_G.place(x = 0, y = 25, relx = 0, rely = 0.5
            , relwidth = 0.5, width = -2
            , relheight = 0.5, height = -25
            , anchor = 'nw')
        self.dummy_canvas_B.place(x = 2, y = 25, relx = 0.5, rely = 0.5
            , relwidth = 0.5, width = -2
            , relheight = 0.5, height = -25
            , anchor = 'nw')

    def gen_cam_sq_disp_canvas(self, master, label_text, label_bg, label_fg,
        canvas_width, canvas_height, canvas_bg, ordinal_index):
        #First widget placement, ordinal index = 0!!
        label_x = 0
        label_y = 0 + np.multiply((canvas_height+25+5), ordinal_index)

        canvas_x = 0
        canvas_y = 0 + 25 + np.multiply((canvas_height + 25+5), ordinal_index)

        label_widget = tk.Label(master, text = label_text, font = 'Helvetica 12 bold', bg = label_bg, fg = label_fg)
        # label_widget.place(x=label_x, y=label_y)

        canvas_widget = tk.Canvas(master, width = canvas_width, height = canvas_height, bg = canvas_bg, highlightthickness = 0)
        # canvas_widget.place(x=canvas_x, y=canvas_y)

        label_widget.place(x=label_x, y = label_y)
        canvas_widget.place(x=canvas_x, y=canvas_y, relwidth = 1)

        return label_widget, canvas_widget

    def custom_scroll_inner_bound(self, event, disp_scroll_class):
        # print(event.type)
        # print(dir(event))
        # disp_scroll_class.canvas.bind_all("<MouseWheel>", lambda event: self.custom_inner_scrolly(event, disp_scroll_class))
        disp_scroll_class.canvas.bind_all("<MouseWheel>", partial(self.custom_inner_scrolly, disp_scroll_class = disp_scroll_class))

    def custom_inner_scrolly(self, event, disp_scroll_class):
        # print(event)
        if disp_scroll_class.scrolly_lock == False:
            y0_inner = float(disp_scroll_class.canvas.yview()[0])
            y1_inner = float(disp_scroll_class.canvas.yview()[1])
            disp_scroll_class.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            # print('custom_inner_scrolly: ',event.delta)
            # print(y0_inner, y1_inner)
            if 0 <= y1_inner < 1:
                if y0_inner == 0: #inner scroll: Start point
                    if event.delta > 0: #scroll up
                        self.scroll_canvas.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            elif y1_inner == 1:
                if 0<= y0_inner < 1: #inner scroll: End point
                    if event.delta < 0: #scroll down
                        self.scroll_canvas.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def custom_mouse_enter_SQ_disp(self, event, disp_scroll_class, scroll_hbar = True):
        if scroll_hbar == True:
            disp_scroll_class.rmb_all_func(scroll_x = False, scroll_y = True)

        disp_scroll_class.canvas.bind('<Enter>', lambda e: None)
        disp_scroll_class.canvas.bind('<Leave>', lambda e: None)
        self.custom_scroll_inner_bound(event, disp_scroll_class)

    def custom_mouse_leave_SQ_disp(self, event, disp_scroll_class, scroll_hbar = False):
        if scroll_hbar == False:
            disp_scroll_class.rmb_all_func(scroll_x = False, scroll_y = False)

        self.scroll_canvas._bound_to_mousewheel(event)

    def camera_display_GUI_2(self):
        # self.cam_disp_sq_prnt = tk.Frame(self.main_frame, width = self.cam_display_width + self.cam_display_width + 10
        #     , height = self.cam_display_height + self.cam_display_height + 50, bg= 'white')
        self.cam_disp_sq_prnt = tk.Frame(self.main_frame)
        self.cam_disp_sq_prnt['bg'] = 'white'

        self.cam_disp_sq_subprnt_1 = tk.Frame(self.cam_disp_sq_prnt)
        self.cam_disp_sq_subprnt_1['bg'] = 'white'
        self.cam_disp_sq_subprnt_1.place(x = 0, y = 25, relx = 0, rely = 0, relwidth = 0.5, width = -2, relheight = 1, height = -25, anchor = 'nw')

        self.cam_disp_sq_subprnt_2 = tk.Frame(self.cam_disp_sq_prnt)
        self.cam_disp_sq_subprnt_2['bg'] = 'white'
        self.cam_disp_sq_subprnt_2.place(x = 2, y = 25, relx = 0.5, rely = 0, relwidth = 0.5, width = -2, relheight = 1, height = -25, anchor = 'nw')

        self.cam_disp_sq_subprnt_2.bind('<Configure>', self.cam_sq_disp_resize)

        self.SQ_frame_scroll_display = ScrolledCanvas(master = self.cam_disp_sq_subprnt_2, frame_w = self.cam_display_width, frame_h = 2800 + 1700, 
            canvas_x = 0, canvas_y = 0, window_bg = 'white', canvas_highlightthickness = 0)

        self.SQ_frame_scroll_display.rmb_all_func(scroll_x = False, scroll_y = False) #To Place the Scroll Canvas

        # self.SQ_frame_scroll_display.canvas.bind('<Enter>', lambda event: self.custom_scroll_inner_bound(event, self.SQ_frame_scroll_display))
        # self.SQ_frame_scroll_display.canvas.bind('<Leave>', self.scroll_canvas._bound_to_mousewheel)

        self.cam_disp_sq_subprnt_2.bind('<Enter>', lambda event: self.custom_mouse_enter_SQ_disp(event, self.SQ_frame_scroll_display, scroll_hbar = True))
        self.cam_disp_sq_subprnt_2.bind('<Leave>', lambda event: self.custom_mouse_leave_SQ_disp(event, self.SQ_frame_scroll_display, scroll_hbar = False))

        self.dummy_canvas_sq_live = tk.Canvas(self.cam_disp_sq_subprnt_1, width = self.cam_display_width, height = self.cam_display_height, bg = 'snow3', highlightthickness = 0)
        self.dummy_canvas_sq_live.place(x = 0, y = 25, relx = 0, rely = 0, relwidth = 1, relheight = 0.5, height = -25, anchor = 'nw')

        self.cam_lb_sq_live = tk.Label(self.cam_disp_sq_subprnt_1, text = 'Live Frame', font = 'Helvetica 12 bold', bg = 'snow3', fg = 'black')
        self.cam_disp_sq_live = tk.Canvas(self.cam_disp_sq_subprnt_1, width = self.cam_display_width, height = self.cam_display_height, bg = 'snow3', highlightthickness = 0)
        self.cam_lb_sq_live.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
        self.cam_disp_sq_live.place(x = 0, y = 25, relx = 0, rely = 0, relwidth = 1, relheight = 0.5, height = -25, anchor = 'nw')

        self.tk_cam_sq_widget_list = []
        for i in range(0, 16):
            lb_name = 'Frame ' + str(i)
            parent = self.SQ_frame_scroll_display.window_fr
            lb_bg = canvas_bg = 'snow3'
            lb_fg = 'black'

            tk_lb, tk_disp = self.gen_cam_sq_disp_canvas(parent, lb_name, lb_bg, lb_fg,
                self.cam_display_width, self.cam_display_height, canvas_bg, int(i))

            self.tk_sq_disp_list.append(tk_disp)
            self.tk_cam_sq_widget_list.append((tk_lb, tk_disp))

    def cam_sq_disp_resize(self, event):
        resize_h = (event.height * 0.5) - 25
        for ordinal_index, widgets in enumerate(self.tk_cam_sq_widget_list):
            label_x = 0
            label_y = 0 + np.multiply((resize_h + 25 + 5), ordinal_index)

            canvas_x = 0
            canvas_y = 0 + 25 + np.multiply((resize_h + 25 + 5), ordinal_index)
            
            widgets[1]['height'] = resize_h

            widgets[0].place(x=label_x, y = label_y)
            widgets[1].place(x=canvas_x, y=canvas_y, relwidth = 1)

        self.SQ_frame_scroll_display.resize_frame(height = canvas_y + resize_h)

    
    def SQ_fr_popout_gen(self):
        self.SQ_fr_popout_toplvl = CustomToplvl(self.main_frame, toplvl_title = 'SQ Frame Display', min_w = 700, min_h = 500
            , icon_img = self.window_icon
            , bg = 'white'
            , topmost_bool = True
            , width = 700, height = 500)

        self.SQ_fr_popout_init()

    def SQ_fr_popout_open(self):
        if False == self.SQ_fr_popout_toplvl.check_open():
            _toplvl = self.SQ_fr_popout_toplvl
            _toplvl.open()
            screen_width = _toplvl.winfo_screenwidth()
            screen_height = _toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (_toplvl.winfo_width()/2))
            y_coordinate = int((screen_height/2) - (_toplvl.winfo_height()/2))
            _toplvl.geometry("{}x{}+{}+{}".format(_toplvl.winfo_width(), _toplvl.winfo_height(), x_coordinate, y_coordinate))

            if True == self.SQ_Connection_Bool():
                from main_GUI import main_GUI
                _light_class = main_GUI.class_light_conn
                self.SQ_fr_popout_load_list(sq_frame_img_list = _light_class.light_interface.sq_frame_img_list)
                self.SQ_fr_popout_disp_func(sq_frame_img_list = _light_class.light_interface.sq_frame_img_list)
                self.SQ_popout_fit_to_display_func()
                self.SQ_fr_sel.bind('<<ComboboxSelected>>', lambda event: self.SQ_fr_popout_disp_func(sq_frame_img_list = _light_class.light_interface.sq_frame_img_list))

            elif False == self.SQ_Connection_Bool():
                self.SQ_fr_popout_load_list(sq_frame_img_list = self.cam_sq_frame_cache)
                self.SQ_fr_popout_disp_func(sq_frame_img_list = self.cam_sq_frame_cache)
                self.SQ_popout_fit_to_display_func()
                self.SQ_fr_sel.bind('<<ComboboxSelected>>', lambda event: self.SQ_fr_popout_disp_func(sq_frame_img_list = self.cam_sq_frame_cache))

        else:
            self.SQ_fr_popout_toplvl.show()


    def SQ_fr_popout_close(self):
        self.SQ_fr_popout_toplvl.close()

    def SQ_popout_fit_to_display_func(self):
        try:
            self.SQ_fr_popout_disp.fit_to_display(self.SQ_fr_popout_toplvl.winfo_width(),self.SQ_fr_popout_toplvl.winfo_height()-30)
        except (AttributeError, tk.TclError):
            pass

    def SQ_fr_popout_init(self):
        tk.Label(self.SQ_fr_popout_toplvl, text = 'Frame No. Display:', font = 'Helvetica 10', bg = 'white').place(x=5, y=0)
        # self.SQ_fr_sel = ttk.Combobox(self.SQ_fr_popout_toplvl, width=15, state='readonly', font = 'Helvetica 10')
        self.SQ_fr_sel = CustomBox(self.SQ_fr_popout_toplvl, width=13, state='readonly', font = 'Helvetica 12')
        self.SQ_fr_sel.unbind_class("TCombobox", "<MouseWheel>")
        self.SQ_fr_sel.place(x=130, y=1)

        self.SQ_curr_disp_fr = 0

        self.SQ_fr_popout_disp = CanvasImage(self.SQ_fr_popout_toplvl)
        self.SQ_fr_popout_disp.place(x=0, y=30, relwidth = 1, relheight = 1, anchor = 'nw')

        self.SQ_fit_to_display_btn = tk.Button(self.SQ_fr_popout_toplvl, relief = tk.GROOVE, image = self.fit_to_display_icon, borderwidth=0)
        self.SQ_fit_to_display_btn['command'] = lambda: self.SQ_fr_popout_disp.fit_to_display(self.SQ_fr_popout_toplvl.winfo_width(), self.SQ_fr_popout_toplvl.winfo_height()-30-30-30)
        CreateToolTip(self.SQ_fit_to_display_btn, 'Fit-to-Screen'
            , 30, 0)
        self.SQ_fit_to_display_btn.place(x=280, y=0)

    ####################################################################################################################
    #THE SQ LOAD LIST AND DISP FUNC V1. IN V1, DISPLAY HAPPENS WHEN SQ FRAME LIST REACHED MAXIMUM NO. OF FRAME.

    def SQ_fr_popout_load_list(self, sq_frame_img_list = None):
        if True == self.SQ_fr_popout_toplvl.check_open():
            frame_num = 0
            if sq_frame_img_list is not None and type(sq_frame_img_list) == list:
                frame_num = len(sq_frame_img_list)
            
            index_num = 0
            str_frame_list = []
            if frame_num == 0:
                pass
            elif frame_num > 0:
                for _ in range(frame_num):
                    index_num = index_num + 1
                    str_frame = 'Frame ' + str(index_num)
                    str_frame_list.append(str_frame)

            self.SQ_fr_sel['values']= str_frame_list
            if len(str_frame_list) > 0:
                # self.SQ_fr_sel.current(0)
                if frame_num < self.SQ_curr_disp_fr + 1:
                    self.SQ_fr_sel.current(frame_num - 1)
                else:
                    self.SQ_fr_sel.current(self.SQ_curr_disp_fr)


    def SQ_fr_popout_disp_func(self, event=None, sq_frame_img_list = None):
        if True == self.SQ_fr_popout_toplvl.check_open():
            frame_num = 0

            if sq_frame_img_list is not None and type(sq_frame_img_list) == list:
                frame_num = len(sq_frame_img_list)

            if frame_num > 0 and ( sq_frame_img_list is not None and type(sq_frame_img_list) == list ):
                #print(int(str(self.SQ_fr_sel.get()).strip('Frame ')))
                self.cam_sq_frame_cache = sq_frame_img_list.copy()

                if self.SQ_fr_popout_disp.loaded_img is None:
                    load_bool = False
                    self.SQ_curr_disp_fr = 0

                    try:
                        self.SQ_fr_popout_disp.loaded_img = sq_frame_img_list[ int(str(self.SQ_fr_sel.get()).strip('Frame ')) - 1]
                        load_bool = True
                        self.SQ_curr_disp_fr = int(str(self.SQ_fr_sel.get()).strip('Frame ')) - 1

                    except IndexError:
                        load_bool = False
                    
                    if load_bool == True:
                        self.SQ_fr_popout_disp.canvas_init_load()
                        self.SQ_popout_fit_to_display_func()

                elif self.SQ_fr_popout_disp.loaded_img is not None:
                    load_bool = False
                    self.SQ_curr_disp_fr = 0

                    try:
                        self.SQ_fr_popout_disp.loaded_img = sq_frame_img_list[ int(str(self.SQ_fr_sel.get()).strip('Frame ')) - 1]
                        load_bool = True
                        self.SQ_curr_disp_fr = int(str(self.SQ_fr_sel.get()).strip('Frame ')) - 1

                    except IndexError:
                        load_bool = False
                    
                    if load_bool == True:
                        self.SQ_fr_popout_disp.canvas_reload()
                    
                if self.SQ_fr_popout_toplvl.wm_state() == 'normal':
                    self.SQ_fr_popout_toplvl.attributes('-topmost', 'true')
                    self.SQ_fr_popout_toplvl.lift()


    ####################################################################################################################
    def SQ_Connection_Bool(self):
        try:
            from main_GUI import main_GUI
            _light_class = main_GUI.class_light_conn
        except Exception:
            _light_class = None

        if _light_class is not None:
            if (_light_class.firmware_model_sel == 'SQ' and _light_class.light_conn_status == True) \
            or (_light_class.firmware_model_sel == 'LC20' and _light_class.light_conn_status == True):
                return True
            else:
                return False

        else:
            return False

    
    def cam_ctrl_frame_resize(self, event, default_h):
        if event.height > default_h:
            cam_ctrl_fr_H = 0
            h_per_frame = int(np.divide(event.height - default_h, 3))

            self.cam_frame_1['height'] = 150 + h_per_frame
            self.cam_frame_2['height'] = 90 + 30 + h_per_frame
            self.cam_frame_3['height'] = 348 + 100 + 70 + h_per_frame

            self.cam_frame_1.place(x = 5, y = cam_ctrl_fr_H + 5, relx = 0, rely = 0, relwidth = 1, width = -10, anchor = 'nw')
            self.cam_frame_1.update_idletasks()
            cam_ctrl_fr_H = cam_ctrl_fr_H + 5 + self.cam_frame_1.winfo_height()

            self.cam_frame_2.place(x = 5, y = cam_ctrl_fr_H + 5, relx = 0, rely = 0, relwidth = 1, width = -10, anchor = 'nw')
            self.cam_frame_2.update_idletasks()
            cam_ctrl_fr_H = cam_ctrl_fr_H + 5 + self.cam_frame_2.winfo_height()

            self.cam_frame_3.place(x = 5, y = cam_ctrl_fr_H + 5, relx = 0, rely = 0, relwidth = 1, width = -10, anchor = 'nw')
            self.cam_frame_3.update_idletasks()
            cam_ctrl_fr_H = cam_ctrl_fr_H + 5 + self.cam_frame_3.winfo_height()

        else:
            cam_ctrl_fr_H = 0
            self.cam_frame_1['height'] = 150
            self.cam_frame_2['height'] = 90 + 30
            self.cam_frame_3['height'] = 348 + 100 + 70

            self.cam_frame_1.place(x = 5, y = cam_ctrl_fr_H + 5, relx = 0, rely = 0, relwidth = 1, width = -10, anchor = 'nw')
            self.cam_frame_1.update_idletasks()
            cam_ctrl_fr_H = cam_ctrl_fr_H + 5 + self.cam_frame_1.winfo_height()

            self.cam_frame_2.place(x = 5, y = cam_ctrl_fr_H + 5, relx = 0, rely = 0, relwidth = 1, width = -10, anchor = 'nw')
            self.cam_frame_2.update_idletasks()
            cam_ctrl_fr_H = cam_ctrl_fr_H + 5 + self.cam_frame_2.winfo_height()

            self.cam_frame_3.place(x = 5, y = cam_ctrl_fr_H + 5, relx = 0, rely = 0, relwidth = 1, width = -10, anchor = 'nw')
            self.cam_frame_3.update_idletasks()
            cam_ctrl_fr_H = cam_ctrl_fr_H + 5 + self.cam_frame_3.winfo_height()


    def camera_control_GUI(self):
        bg_color = 'SteelBlue1' #'DarkSlateGray2'
        cam_ctrl_fr_H = 0

        self.cam_ctrl_frame = tk.Frame(self.main_frame, bg = bg_color, highlightbackground = 'navy', highlightthickness=1)
        self.cam_ctrl_frame['width'] = 312
        self.cam_ctrl_frame.place(x = -15, y = 30 + 25, relx = 1, rely = 0, relheight = 1, height = -(30+25)-15, anchor = 'ne') ## During init-phase, the cam_ctrl_frame place value(s) are set this way.

        ### self.cam_frame_1: Frame_1 is the Main Camera Controls
        self.cam_frame_1 = tk.Frame(self.cam_ctrl_frame, highlightthickness=0)
        self.cam_frame_1['height'] = 150
        
        ### self.cam_frame_2: Frame_2 is the Save Camera Controls
        self.cam_frame_2 = tk.Frame(self.cam_ctrl_frame, highlightthickness=0)
        self.cam_frame_2['height'] = 90 + 30

        ### self.cam_frame_3: Frame_3 is the Exposure etc Camera Controls
        self.cam_frame_3 = tk.Frame(self.cam_ctrl_frame, highlightthickness=0)
        self.cam_frame_3['height'] = 348 + 100 + 70


        self.cam_frame_1.place(x = 5, y = cam_ctrl_fr_H + 5, relx = 0, rely = 0, relwidth = 1, width = -10, anchor = 'nw')
        self.cam_frame_1.update_idletasks()
        cam_ctrl_fr_H = cam_ctrl_fr_H + 5 + self.cam_frame_1.winfo_height()

        self.cam_frame_2.place(x = 5, y = cam_ctrl_fr_H + 5, relx = 0, rely = 0, relwidth = 1, width = -10, anchor = 'nw')
        self.cam_frame_2.update_idletasks()
        cam_ctrl_fr_H = cam_ctrl_fr_H + 5 + self.cam_frame_2.winfo_height()

        self.cam_frame_3.place(x = 5, y = cam_ctrl_fr_H + 5, relx = 0, rely = 0, relwidth = 1, width = -10, anchor = 'nw')
        self.cam_frame_3.update_idletasks()
        cam_ctrl_fr_H = cam_ctrl_fr_H + 5 + self.cam_frame_3.winfo_height()

        self.cam_ctrl_frame['height'] = cam_ctrl_fr_H + 7

        if isinstance(self.scroll_canvas, ScrolledCanvas) == True:
            if self.scroll_canvas.get_frame_size()[1] < self.cam_ctrl_frame['height'] + self.cam_ctrl_frame.winfo_y() + 15:
                self.scroll_canvas.resize_frame(height = self.cam_ctrl_frame['height'] + self.cam_ctrl_frame.winfo_y() + 15)

        self.cam_ctrl_frame.bind('<Configure>', partial(self.cam_ctrl_frame_resize, default_h = self.cam_ctrl_frame['height']))
        ###################################################################################################################################################

        self.cam_mode_var = tk.StringVar(value = self.cam_mode_str)
        
        # tk.Label(self.cam_frame_1, text = 'Trigger Source: ', font = 'Helvetica 10').place(x = 5 , y = 100)
        tk.Label(self.cam_frame_1, text = 'Trigger Source: ', font = 'Helvetica 10').place(x = -135, relx = 0.5
            , y = 100, rely = 0
            , anchor = 'nw')

        self.triggercheck_val = tk.IntVar()
        self.checkbtn_trigger_src = tk.Checkbutton(self.cam_frame_1, text='Internal Trigger', variable = self.triggercheck_val, onvalue=1, offvalue=0, highlightthickness = 0)
        self.checkbtn_trigger_src['command'] = self.trigger_src_func
        self.widget_bind_focus(self.checkbtn_trigger_src)
        # self.checkbtn_trigger_src.place(x=5 ,y=90+33)
        self.checkbtn_trigger_src.place(x = -130, relx = 0.5
            , y = 122, rely = 0
            , anchor = 'nw')

        self.checkbtn_trigger_src['state'] = 'disable'

        # self.trigger_src_list = ['LINE0', 'LINE1', 'LINE2', 'LINE3', 'COUNTER0', 'SOFTWARE']
        # self.trigger_src_select = CustomBox(self.cam_frame_1, values=self.trigger_src_list, width=15, state='readonly', font = 'Helvetica 10')
        # self.trigger_src_select.unbind_class("TCombobox", "<MouseWheel>")
        # self.trigger_src_select.bind('<<ComboboxSelected>>', self.trigger_src_func)
        # self.trigger_src_select.current(0)
        # self.trigger_src_select.place(x=5, y=90+33)

        self.btn_trigger_once = tk.Button(self.cam_frame_1, text='Trigger Once', width=15, height=1, relief = tk.GROOVE)
        self.btn_trigger_once['command'] = self.trigger_once
        self.widget_bind_focus(self.btn_trigger_once)
        self.btn_trigger_once['state'] = 'disable'
        # self.btn_trigger_once.place(x=150 + 15, y=90+30)
        self.btn_trigger_once.place(x = -118, relx = 0.9
            , y = 118, rely = 0
            , anchor = 'nw')


        tk.Label(self.cam_frame_1, text = 'Main Controls: ', font = 'Helvetica 11 bold').place(x=0, y=0)
        self.radio_continuous = tk.Radiobutton(self.cam_frame_1, text='Continuous',variable = self.cam_mode_var, value='continuous',width=15, height=1)
        self.radio_continuous['command'] = self.set_triggermode
        self.widget_bind_focus(self.radio_continuous)
        # self.radio_continuous.place(x=5 + 15,y=5 + 25)
        self.radio_continuous.place(x = -130, relx = 0.5
            , y = 30, rely = 0
            , anchor = 'nw')

        self.radio_trigger = tk.Radiobutton(self.cam_frame_1, text='Trigger Mode',variable = self.cam_mode_var, value='triggermode',width=15, height=1)
        self.radio_trigger['command'] = self.set_triggermode
        self.widget_bind_focus(self.radio_trigger)
        # self.radio_trigger.place(x=145 + 15,y=5 +25)
        self.radio_trigger.place(x = -138, relx = 0.9
            , y = 30, rely = 0
            , anchor = 'nw')

        # self.btn_start_grabbing = tk.Button(self.cam_frame_1, text='START', width=5, height=1, relief = tk.GROOVE,
        #     activebackground = 'forest green', bg = 'green3', activeforeground = 'white', fg = 'white', font = 'Helvetica 12 bold')
        # self.btn_stop_grabbing = tk.Button(self.cam_frame_1, text='STOP', width=5, height=1, relief = tk.GROOVE,
        #     activebackground = 'red3', bg = 'red', activeforeground = 'white', fg = 'white', font = 'Helvetica 12 bold')
        
        # self.btn_start_grabbing['command'] = self.start_grabbing
        # self.btn_stop_grabbing['command'] = self.stop_grabbing
        # self.btn_start_grabbing.place(x=35 + 15, y=40+25)
        # self.btn_stop_grabbing.place(x=175 + 15, y=40+25)

        self.btn_grab_frame = tk.Button(self.cam_frame_1, text='START', width=6, height=1, relief = tk.GROOVE,
            activebackground = 'forest green', bg = 'green3', activeforeground = 'white', fg = 'white', font = 'Helvetica 12 bold')
        # self.btn_grab_frame['command'] = self.start_grabbing
        self.grab_btn_init_state(self.btn_grab_frame, self.start_grabbing)

        self.widget_bind_focus(self.btn_grab_frame)
        # self.btn_grab_frame.place(x=35 + 15, y=40+25)
        self.btn_grab_frame.place(x = -40, relx = 0.5
            , y = 60, rely = 0
            , anchor = 'ne')

        self.capture_img_checkbtn = tk.Checkbutton(self.cam_frame_1, text='Freeze Image', variable = self.capture_img_status, onvalue=1, offvalue=0)
        # self.capture_img_checkbtn.place(x=176,y=40+25)
        self.capture_img_checkbtn.place(x = -122, relx = 0.9
            , y = 60, rely = 0
            , anchor = 'nw')
        ###############################################################################################################################
        
        tk.Label(self.cam_frame_2, text = 'Save Images: ', font = 'Helvetica 11 bold').place(x=0, y=0)

        self.btn_save_sq = tk.Button(self.cam_frame_2, text='Save SQ Frame', width=15, height=1, relief = tk.GROOVE)
        self.btn_save_sq['command'] = self.sq_frame_save
        self.widget_bind_focus(self.btn_save_sq)

        self.btn_save_img = tk.Button(self.cam_frame_2, text='Save Image', width=15, height=1, relief = tk.GROOVE)
        self.btn_save_img['command'] = self.img_save_func
        self.widget_bind_focus(self.btn_save_img)

        self.label_save_img_format = tk.Label(self.cam_frame_2, text = 'Image Format: ', font = 'Helvetica 10')
        self.save_img_format_sel = CustomBox(self.cam_frame_2, values=self.save_img_format_list, width=5, state='readonly', font = 'Helvetica 11')
        self.save_img_format_sel.unbind_class("TCombobox", "<MouseWheel>")
        self.save_img_format_sel.current(0)
        # self.label_save_img_format.place(x=160,  y=5)
        # self.save_img_format_sel.place(x=160, y=30)
        self.label_save_img_format.place(x = -98, relx = 0.9
            , y = 5, rely = 0
            , anchor = 'nw')
        self.save_img_format_sel.place(x = -98, relx = 0.9
            , y = 30, rely = 0
            , anchor = 'nw')

        self.set_custom_save_checkbtn = tk.Checkbutton(self.cam_frame_2, text='Custom Save', variable = self.set_custom_save_bool, onvalue=1, offvalue=0)
        self.set_custom_save_checkbtn['command'] = self.set_custom_save

        self.trigger_auto_save_bool = tk.IntVar(value = 0)
        self.trigger_auto_save_checkbtn = tk.Checkbutton(self.cam_frame_2, text='Trigger Mode Auto Save', variable = self.trigger_auto_save_bool, onvalue=1, offvalue=0)
        self.trigger_auto_save_checkbtn['command'] = self.set_trigger_autosave

        self.folder_dir_btn = tk.Button(self.cam_frame_2, relief = tk.GROOVE)#, width = 2, height = 1)
        self.folder_dir_btn['bg'] = 'gold'
        self.folder_dir_btn['command'] = partial(open_save_folder, folder_path = os.path.join(os.environ['USERPROFILE'],  "TMS_Saved_Images"), create_bool = True)
        self.folder_dir_btn['image'] = self.folder_icon
        CreateToolTip(self.folder_dir_btn, 'Open Save Folder'
            , 32, -5, font = 'Tahoma 11')

        self.folder_dir_btn.place(x = -85, relx = 0.9
            , y = 75, rely = 0
            , anchor = 'nw')

        self.SQ_auto_save_bool = tk.IntVar(value = 0)
        self.SQ_auto_save_checkbtn = tk.Checkbutton(self.cam_frame_2, text='SQ Frame(s) Auto Save', variable = self.SQ_auto_save_bool, onvalue=1, offvalue=0)
        self.SQ_auto_save_checkbtn['command'] = self.set_SQ_autosave
        #self.SQ_auto_save_checkbtn.place(x=20,y=60)

        ###############################################################################################################################
        shift_x = 10
        tk.Label(self.cam_frame_3, text = 'Camera Parameters: ', font = 'Helvetica 11 bold').place(x=0, y=0)

        label_framerate = tk.Label(self.cam_frame_3, text='Frame Rate', width=12, anchor = 'e')
        info_framerate = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_framerate, 'Frame Rate: \n' + 'Set an upper limit for the frame rate\n(FPS) at which frames are captured.'+ \
            '\n\n'+ 'Min: 1\nMax: 1000'
            , -220, -40, width = 220, height = 105)

        self.framerate_str = tk.StringVar()
        #self.entry_framerate = tk.Entry(self.cam_frame_3, textvariable = self.framerate_str, highlightbackground="black", highlightthickness=1, width = 9)
        self.entry_framerate = tk.Spinbox(self.cam_frame_3, textvariable = self.framerate_str, highlightbackground="black", highlightthickness=1, width = 7, from_=1, to =1000)
        self.framerate_str.set(self.cam_param_float[2])

        self.entry_framerate['validate']='key'
        self.entry_framerate['vcmd']=(self.entry_framerate.register(validate_float_entry),'%d', '%P', '%S', 2)
        self.entry_framerate.bind('<Return>', self.set_parameter_framerate)
        self.entry_framerate.bind('<Tab>', self.set_parameter_framerate)
        self.entry_framerate.bind('<FocusOut>', self.set_parameter_framerate)
        self.entry_framerate['command'] = self.set_parameter_framerate

        label_framerate_enable = tk.Label(self.cam_frame_3, text = 'Frame Rate Enable', anchor = 'e')
        self.btn_enable_framerate = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_enable_framerate['command'] = self.enable_framerate
        self.widget_bind_focus(self.btn_enable_framerate)

        info_framerate.place(x = -140, relx = 0.5, y = 90, rely = 0, anchor = 'nw')
        label_framerate.place(x = 0, relx = 0.5, y = 90, rely = 0, anchor = 'ne')
        label_framerate_enable.place(x = 0, relx = 0.5, y = 65, rely = 0, anchor = 'ne')
        self.entry_framerate.place(x = 10, relx = 0.5, y = 90, rely = 0, width = -40, relwidth = 0.5, anchor = 'nw')
        self.btn_enable_framerate.place(x = 10, relx = 0.5, y = 60, rely = 0, anchor = 'nw')

        ###############################################################################################################################
        label_exposure = tk.Label(self.cam_frame_3, text='Exposure Time', width=12, anchor = 'e')
        info_exposure = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_exposure, 'Exposure: \n' + 'Specify how long the image sensor\nis exposed to the light during image\n'+ \
            'acquisition.' +'\n\n'+ 'Min: 28\nMax: 1,000,000'
            , -220, -40, width = 220, height = 120)
        self.exposure_str = tk.StringVar()
        #self.entry_exposure = tk.Entry(self.cam_frame_3, textvariable = self.exposure_str, highlightbackground="black", highlightthickness=1, width = 9)
        self.entry_exposure = tk.Spinbox(self.cam_frame_3, textvariable = self.exposure_str, highlightbackground="black", highlightthickness=1, width = 7, from_=28, to =1000000, increment= 1000)
        self.exposure_str.set(self.cam_param_float[0])

        self.entry_exposure['validate']='key'
        self.entry_exposure['vcmd']=(self.entry_exposure.register(validate_float_entry), '%d', '%P', '%S', 2)
        self.entry_exposure.bind('<Return>', self.set_parameter_exposure)
        self.entry_exposure.bind('<Tab>', self.set_parameter_exposure)
        self.entry_exposure.bind('<FocusOut>', self.set_parameter_exposure)
        self.entry_exposure['command'] = self.set_parameter_exposure

        label_auto_exposure = tk.Label(self.cam_frame_3, text = 'Auto Exposure', width = 12, anchor = 'e')
        self.btn_auto_exposure = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_auto_exposure['command'] = self.set_auto_exposure
        self.widget_bind_focus(self.btn_auto_exposure)

        info_exposure.place(x = -140, relx = 0.5, y = 145, rely = 0, anchor = 'nw')
        label_exposure.place(x = 0, relx = 0.5, y = 145, rely = 0, anchor = 'ne')
        label_auto_exposure.place(x = 0, relx = 0.5, y = 120, rely = 0, anchor = 'ne')
        self.entry_exposure.place(x = 10, relx = 0.5, y = 145, rely = 0, width = -40, relwidth = 0.5, anchor = 'nw')
        self.btn_auto_exposure.place(x = 10, relx = 0.5, y = 115, rely = 0, anchor = 'nw')

        ###############################################################################################################################
        label_gain = tk.Label(self.cam_frame_3, text='Gain', width=12, anchor = 'e')
        info_gain = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_gain, 'Gain: \n' + 'Set an amplification factor applied to\nthe video signal so as to increase\n'+ \
            'the brightness of the image output\n'+ 'by the camera.' +'\n\n'+ 'Min: 0\nMax: 15.0062'
            , -220, -40, width = 220, height = 140)

        self.gain_str = tk.StringVar()
        # self.entry_gain = tk.Entry(self.cam_frame_3, textvariable = self.gain_str, highlightbackground="black", highlightthickness=1, width = 9)
        self.entry_gain = tk.Spinbox(self.cam_frame_3, textvariable = self.gain_str, highlightbackground="black", highlightthickness=1, width = 7, from_=0, to =15.0026)
        self.gain_str.set(self.cam_param_float[1])

        self.entry_gain['validate']='key'
        self.entry_gain['vcmd']=(self.entry_gain.register(validate_float_entry), '%d', '%P', '%S', 4)
        self.entry_gain.bind('<Return>', self.set_parameter_gain)
        self.entry_gain.bind('<Tab>', self.set_parameter_gain)
        self.entry_gain.bind('<FocusOut>', self.set_parameter_gain)
        self.entry_gain['command'] = self.set_parameter_gain

        label_auto_gain = tk.Label(self.cam_frame_3, text = 'Auto Gain', width = 12, anchor = 'e')
        self.btn_auto_gain = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_auto_gain['command'] = self.set_auto_gain
        self.widget_bind_focus(self.btn_auto_gain)

        info_gain.place(x = -140, relx = 0.5, y = 200, rely = 0, anchor = 'nw')
        label_gain.place(x = 0, relx = 0.5, y = 200, rely = 0, anchor = 'ne')
        label_auto_gain.place(x = 0, relx = 0.5, y = 175, rely = 0, anchor = 'ne')
        self.entry_gain.place(x = 10, relx = 0.5, y = 200, rely = 0, width = -40, relwidth = 0.5, anchor = 'nw')
        self.btn_auto_gain.place(x = 10, relx = 0.5, y = 170, rely = 0, anchor = 'nw')
        ###############################################################################################################################
        label_brightness = tk.Label(self.cam_frame_3, text='Brightness', width=12, anchor = 'e')
        info_brightness = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_brightness, 'Brightness: \n' + 'Sets the selected Brightness control.' + \
            '\n\n' + 'Min: 0\nMax: 255'
            , -220, -30, width = 220, height = 90)

        self.brightness_str = tk.StringVar()
        #self.entry_brightness = tk.Entry(self.cam_frame_3, textvariable = self.brightness_str, highlightbackground="black", highlightthickness=1, width = 9)
        self.entry_brightness = tk.Spinbox(self.cam_frame_3, textvariable = self.brightness_str, highlightbackground="black", highlightthickness=1, width = 7, from_=0, to= 255)
        int_validate(self.entry_brightness, limits = (0,255))
        self.brightness_str.set(self.cam_param_int[0])

        self.entry_brightness.bind('<Return>', self.set_parameter_brightness)
        self.entry_brightness.bind('<Tab>', self.set_parameter_brightness)
        self.entry_brightness.bind('<FocusOut>', self.set_parameter_brightness)
        self.entry_brightness['command'] = self.set_parameter_brightness

        self.entry_brightness['state'] = 'disable'

        info_brightness.place(x = -140, relx = 0.5, y = 230, rely = 0, anchor = 'nw')
        label_brightness.place(x = 0, relx = 0.5, y = 230, rely = 0, anchor = 'ne')
        self.entry_brightness.place(x = 10, relx = 0.5, y = 230, rely = 0, width = -40, relwidth = 0.5, anchor = 'nw')
        ###############################################################################################################################
        label_auto_white = tk.Label(self.cam_frame_3, text = 'Auto White Balance', anchor = 'e')

        self.btn_auto_white = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_auto_white['command'] = self.set_auto_white
        self.widget_bind_focus(self.btn_auto_white)

        
        self.balance_ratio_lb_tag = tk.Frame(self.cam_frame_3, width = 100, height = 72)
        self.balance_ratio_param = tk.Frame(self.cam_frame_3, width = 60, height = 72)

        label_balance_ratio = tk.Label(self.balance_ratio_lb_tag, text = 'Balance Ratio', anchor = 'e')

        info_balance_ratio = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_balance_ratio, 'Balance Ratio: \n' + 'Gamma correction of pixel intensity,\nwhich helps optimizing the brightness\n'+ \
            'of acquired images for displaying\n'+ 'on a monitor.' +'\n\n'+ 'Min: 1\nMax: 4095'
            , -220, -40, width = 220, height = 140)

        red_tag = tk.Frame(self.balance_ratio_lb_tag, width = 20, height = 20, bg = 'red')
        green_tag = tk.Frame(self.balance_ratio_lb_tag, width = 20, height = 20, bg = 'green')
        blue_tag = tk.Frame(self.balance_ratio_lb_tag, width = 20, height = 20, bg = 'blue')

        label_balance_ratio.place(x=0, y= 25)
        red_tag.place(x=80,y=0)
        green_tag.place(x=80,y=25)
        blue_tag.place(x=80,y=50)

        self.red_ratio_str = tk.StringVar()
        self.green_ratio_str = tk.StringVar()
        self.blue_ratio_str = tk.StringVar()
        self.entry_red_ratio = tk.Spinbox(self.balance_ratio_param, textvariable = self.red_ratio_str, highlightbackground="black", highlightthickness=1, width = 7, from_=1, to= 4095)
        self.entry_red_ratio.bind('<Return>', self.set_parameter_red_ratio)
        self.entry_red_ratio.bind('<Tab>', self.set_parameter_red_ratio)
        self.entry_red_ratio.bind('<FocusOut>', self.set_parameter_red_ratio)
        self.entry_red_ratio['command'] = self.set_parameter_red_ratio

        self.entry_green_ratio = tk.Spinbox(self.balance_ratio_param, textvariable = self.green_ratio_str, highlightbackground="black", highlightthickness=1, width = 7, from_=1, to= 4095)
        self.entry_green_ratio.bind('<Return>', self.set_parameter_green_ratio)
        self.entry_green_ratio.bind('<Tab>', self.set_parameter_green_ratio)
        self.entry_green_ratio.bind('<FocusOut>', self.set_parameter_green_ratio)
        self.entry_green_ratio['command'] = self.set_parameter_green_ratio

        self.entry_blue_ratio = tk.Spinbox(self.balance_ratio_param, textvariable = self.blue_ratio_str, highlightbackground="black", highlightthickness=1, width = 7, from_=1, to= 4095)
        self.entry_blue_ratio.bind('<Return>', self.set_parameter_blue_ratio)
        self.entry_blue_ratio.bind('<Tab>', self.set_parameter_blue_ratio)
        self.entry_blue_ratio.bind('<FocusOut>', self.set_parameter_blue_ratio)
        self.entry_blue_ratio['command'] = self.set_parameter_blue_ratio

        self.red_ratio_str.set(self.cam_param_int[1])
        self.green_ratio_str.set(self.cam_param_int[2])
        self.blue_ratio_str.set(self.cam_param_int[3])
        int_validate(self.entry_red_ratio, limits = (1,4095))
        int_validate(self.entry_green_ratio, limits = (1,4095))
        int_validate(self.entry_blue_ratio, limits = (1,4095))

        self.entry_red_ratio.place(x=0, y=0, relwidth = 1, anchor = 'nw')
        self.entry_green_ratio.place(x=0, y=25, relwidth = 1, anchor = 'nw')
        self.entry_blue_ratio.place(x=0, y=50, relwidth = 1, anchor = 'nw')

        info_balance_ratio.place(x = -140, relx = 0.5, y = 308, rely = 0, anchor = 'nw')
        label_auto_white.place(x = 0, relx = 0.5, y = 258, rely = 0, anchor = 'ne')
        self.btn_auto_white.place(x = 10, relx = 0.5, y = 253, rely = 0, anchor = 'nw')
        self.balance_ratio_lb_tag.place(x = 0, relx = 0.5, y = 283, rely = 0, anchor = 'ne')
        self.balance_ratio_param.place(x = 10, relx = 0.5, y = 283, rely = 0, width = -40, relwidth = 0.5, anchor = 'nw')
        
        ###############################################################################################################################
        label_black_lvl = tk.Label(self.cam_frame_3, text='Black Level', width=12, anchor = 'e')
        info_black_lvl = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_black_lvl, 'Black Level: \n' + 'Analog black level in percent.\n\n'+ 'Min: 0\nMax: 4095'
            , -180, -20, width = 180, height = 90)

        self.black_lvl_str = tk.StringVar()
        self.entry_black_lvl = tk.Spinbox(self.cam_frame_3, textvariable = self.black_lvl_str, highlightbackground="black", highlightthickness=1, width = 7, from_=0, to =4095)
        self.black_lvl_str.set(self.cam_param_int[4])
        int_validate(self.entry_black_lvl, limits = (0,4095))
        self.entry_black_lvl.bind('<Return>', self.set_parameter_black_lvl)
        self.entry_black_lvl.bind('<Tab>', self.set_parameter_black_lvl)
        self.entry_black_lvl.bind('<FocusOut>', self.set_parameter_black_lvl)
        self.entry_black_lvl['command'] = self.set_parameter_black_lvl

        label_black_lvl_enable = tk.Label(self.cam_frame_3, text = 'Black Level Enable', anchor = 'e')
        self.btn_enable_black_lvl = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_enable_black_lvl['command'] = self.enable_black_lvl
        self.widget_bind_focus(self.btn_enable_black_lvl)

        info_black_lvl.place(x = -140, relx = 0.5, y = 393, rely = 0, anchor = 'nw')
        label_black_lvl.place(x = 0, relx = 0.5, y = 393, rely = 0, anchor = 'ne')
        label_black_lvl_enable.place(x = 0, relx = 0.5, y = 368, rely = 0, anchor = 'ne')
        self.entry_black_lvl.place(x = 10, relx = 0.5, y = 393, rely = 0, width = -40, relwidth = 0.5, anchor = 'nw')
        self.btn_enable_black_lvl.place(x = 10, relx = 0.5, y = 363, rely = 0, anchor = 'nw')

        ###############################################################################################################################
        label_sharpness = tk.Label(self.cam_frame_3, text='Sharpness', width=12, anchor = 'e')
        info_sharpness = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_sharpness, 'Sharpness: \n' + 'The larger the Sharpness value,\n' + \
            'the more distinct the contours\n' + 'of the image objects will be.\n' + \
            'This is especially useful in applications\n' + 'where cameras must correctly identify\n' +\
            'numbers, letters or characters.\n\n'+ 'Min: 0\nMax: 100'
            , -230, -75, width = 230, height = 170)

        self.sharpness_str = tk.StringVar()
        self.entry_sharpness = tk.Spinbox(self.cam_frame_3, textvariable = self.sharpness_str, highlightbackground="black", highlightthickness=1, width = 7, from_=0, to =100)
        self.sharpness_str.set(self.cam_param_int[5])
        int_validate(self.entry_sharpness, limits = (0,100))
        self.entry_sharpness.bind('<Return>', self.set_parameter_sharpness)
        self.entry_sharpness.bind('<Tab>', self.set_parameter_sharpness)
        self.entry_sharpness.bind('<FocusOut>', self.set_parameter_sharpness)
        self.entry_sharpness['command'] = self.set_parameter_sharpness

        label_sharpness_enable = tk.Label(self.cam_frame_3, text = 'Sharpness Enable', anchor = 'e')
        self.btn_enable_sharpness = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_enable_sharpness['command'] = self.enable_sharpness
        self.widget_bind_focus(self.btn_enable_sharpness)

        info_sharpness.place(x = -140, relx = 0.5, y = 448, rely = 0, anchor = 'nw')
        label_sharpness.place(x = 0, relx = 0.5, y = 448, rely = 0, anchor = 'ne')
        label_sharpness_enable.place(x = 0, relx = 0.5, y = 423, rely = 0, anchor = 'ne')
        self.entry_sharpness.place(x = 10, relx = 0.5, y = 448, rely = 0, width = -40, relwidth = 0.5, anchor = 'nw')
        self.btn_enable_sharpness.place(x = 10, relx = 0.5, y = 418, rely = 0, anchor = 'nw')
        ###############################################################################################################################

        self.btn_get_parameter = tk.Button(self.cam_frame_3, text='Read Parameter', width=15, height=1, relief = tk.GROOVE)
        self.btn_get_parameter['command'] = self.get_parameter
        self.widget_bind_focus(self.btn_get_parameter)
        self.btn_get_parameter.place(x = -10, relx = 0.5, y = 485, rely = 0, anchor = 'ne')

        self.btn_set_parameter = tk.Button(self.cam_frame_3, text='Set Parameter', width=15, height=1, relief = tk.GROOVE)
        self.btn_set_parameter['command'] = self.set_parameter
        self.widget_bind_focus(self.btn_set_parameter)
        self.btn_set_parameter.place(x = 10, relx = 0.5, y = 485, rely = 0, anchor = 'nw')
        ###############################################################################################################################

        label_pixel_format = tk.Label(self.cam_frame_3, text = 'Pixel Format', width=12, anchor = 'e')
        info_pixel_format = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_pixel_format, 'Pixel Format: \n' + 'Format of the pixel data.'
            , -150, 0, width = 150, height = 40)

        self.pixel_format_list = ["Mono 8", "Mono 10", "Mono 10 Packed", "Mono 12", "Mono 12 Packed", "RGB 8", "BGR 8", "YUV 422 (YUYV) Packed", "YUV 422 Packed", "Bayer RG 8", "Bayer RG 10", "Bayer RG 10 Packed", "Bayer RG 12", "Bayer RG 12 Packed"]
        # self.pixel_format_combobox = CustomBox(self.cam_frame_3, width=15, state='readonly', font = 'Helvetica 11')
        self.pixel_format_combobox = CustomBox(self.cam_frame_3, state='readonly', font = 'Helvetica 11')
        self.pixel_format_combobox['values'] = self.pixel_format_list
        self.pixel_format_combobox.unbind_class("TCombobox", "<MouseWheel>")
        self.pixel_format_combobox.bind('<<ComboboxSelected>>', lambda event: self.pixel_format_sel(event = event))

        info_pixel_format.place(x = -140, relx = 0.5, y = 30, rely = 0, anchor = 'nw')
        label_pixel_format.place(x = 0, relx = 0.5, y = 30, rely = 0, anchor = 'ne')
        self.pixel_format_combobox.place(x = 10, relx = 0.5, y = 30, rely = 0, width = -40, relwidth = 0.5, anchor = 'nw')
    
    def grab_btn_state(self, btn, func):
        if btn['text'] == 'START':
            btn['text'] = 'STOP'
            btn['activebackground'] = 'red3'
            btn['bg'] = 'red'
            btn['activeforeground'] = 'white'
            btn['fg'] = 'white'
            btn['command'] = func

        elif btn['text'] == 'STOP':
            btn['text'] = 'START'
            btn['activebackground'] = 'forest green'
            btn['bg'] = 'green3'
            btn['activeforeground'] = 'white'
            btn['fg'] = 'white'
            btn['command'] = func

    def grab_btn_init_state(self, btn, func):
        btn['text'] = 'START'
        btn['activebackground'] = 'forest green'
        btn['bg'] = 'green3'
        btn['activeforeground'] = 'white'
        btn['fg'] = 'white'
        btn['command'] = func


    def camera_control_state(self):
        if self.cam_conn_status == False:
            widget_disable(self.radio_continuous, self.radio_trigger, self.btn_grab_frame #self.btn_start_grabbing, self.btn_stop_grabbing
                , self.btn_get_parameter, self.btn_set_parameter
                , self.btn_auto_gain, self.btn_auto_exposure, self.btn_enable_framerate
                , self.entry_gain, self.entry_exposure, self.entry_framerate
                , self.capture_img_checkbtn)

            widget_disable(self.flip_btn_1, self.flip_btn_2
                , self.Normal_cam_popout_btn
                , self.SQ_cam_popout_btn
                , self.SQ_fr_popout_btn)

            widget_disable(self.btn_auto_white, self.entry_red_ratio, self.entry_green_ratio, self.entry_blue_ratio)
            widget_disable(self.btn_enable_black_lvl, self.entry_black_lvl)
            widget_disable(self.btn_enable_sharpness, self.entry_sharpness)
            widget_disable(self.btn_save_sq)

            widget_disable(self.btn_normal_cam_mode
                , self.btn_SQ_cam_mode
                )

            #self.trigger_src_select['state'] = 'disable'
            
            self.btn_trigger_once['state'] = 'disable'
            self.checkbtn_trigger_src['state'] = 'disable'
            self.entry_brightness['state'] = 'disable'
            self.pixel_format_combobox['state'] = 'disable'

            self.set_custom_save_checkbtn['state'] = 'disable'
            self.trigger_auto_save_checkbtn['state'] = 'disable'

            self.SQ_auto_save_checkbtn['state'] = 'disable'

            self.btn_save_img['state'] = 'disable'
            self.save_img_format_sel['state'] = 'disable'

            self.record_btn_1['state'] = 'disable'

            self.triggercheck_val.set(0)
            self.cam_mode_str = 'continuous'
            self.cam_mode_var.set(self.cam_mode_str)
            self.capture_img_status.set(0)
            self.set_custom_save_bool.set(0)
            self.set_custom_save()
            self.trigger_auto_save_bool.set(0)
            self.SQ_auto_save_bool.set(0)


            # self.time_lapse_label.place_forget()
            self.time_lapse_var.set('')
            widget_disable(self.record_setting_btn)

        elif self.cam_conn_status == True:
            widget_enable(self.radio_continuous, self.radio_trigger, self.btn_grab_frame #self.btn_start_grabbing, self.btn_stop_grabbing
                , self.btn_get_parameter, self.btn_set_parameter
                , self.btn_auto_gain, self.btn_auto_exposure, self.btn_enable_framerate
                , self.entry_gain, self.entry_exposure, self.entry_framerate
                , self.capture_img_checkbtn)

            widget_enable(self.flip_btn_1, self.flip_btn_2
                , self.Normal_cam_popout_btn
                , self.SQ_cam_popout_btn
                , self.SQ_fr_popout_btn)

            widget_enable(self.btn_save_sq)
            # widget_enable(self.btn_auto_white)
            widget_enable(self.btn_enable_black_lvl)
            widget_enable(self.btn_enable_sharpness)

            widget_enable(self.btn_normal_cam_mode
                , self.btn_SQ_cam_mode
                )

            self.pixel_format_combobox['state'] = 'readonly'

            self.set_custom_save_checkbtn['state'] = 'normal'

            self.btn_save_img['state'] = 'normal'
            self.save_img_format_sel['state'] = 'readonly'

            self.record_btn_1['state'] = 'normal'
            #self.trigger_src_select['state'] = 'readonly'
            #self.btn_trigger_once['state'] = 'normal'
            #self.checkbtn_trigger_src['state'] = 'normal'

            self.btn_auto_exposure, self.entry_exposure = self.camera_toggle_button_state(self.auto_exposure_toggle, self.btn_auto_exposure, 
                self.toggle_ON_button_img, self.toggle_OFF_button_img, self.entry_exposure)

            self.btn_auto_gain, self.entry_gain = self.camera_toggle_button_state(self.auto_gain_toggle, self.btn_auto_gain, 
                self.toggle_ON_button_img, self.toggle_OFF_button_img, self.entry_gain)

            self.btn_enable_framerate, self.entry_framerate = self.camera_toggle_button_state(self.framerate_toggle, self.btn_enable_framerate, 
                self.toggle_ON_button_img, self.toggle_OFF_button_img, self.entry_framerate, 'framerate')

            # self.white_balance_btn_state()
            self.black_lvl_btn_state()
            self.sharpness_btn_state()
            self.camera_brightness_entry_state()

            # self.time_lapse_label.place(x = -10-25-5-25-5-25-5-25-5, y = 1, relx = 1, rely = 0, anchor = 'ne')
            self.time_lapse_var.set('')
            widget_enable(self.record_setting_btn)

    def camera_toggle_button_state(self, auto_toggle_status, auto_button, img_button_ON, img_button_OFF, 
        entry_box, toggle_type = None):
        if auto_toggle_status == True:
            auto_button['image'] = img_button_ON

            if toggle_type == 'framerate':
                try:
                    entry_box['state'] = 'normal'
                except:
                    pass
            else:
                try:
                    entry_box['state'] = 'disabled'
                except:
                    pass

        elif auto_toggle_status == False:
            auto_button['image'] = img_button_OFF
            if toggle_type == 'framerate':
                try:
                    entry_box['state'] = 'disabled'
                except:
                    pass
            else:
                try:
                    entry_box['state'] = 'normal'
                except:
                    pass

        return auto_button, entry_box

    def camera_brightness_entry_state(self):
        if self.auto_gain_toggle == True or self.auto_exposure_toggle == True:
            self.entry_brightness['state'] = 'normal'
        else:
            self.entry_brightness['state'] = 'disable'

    def white_balance_btn_state(self):
        if self.auto_white_toggle == True:
            self.btn_auto_white['image'] = self.toggle_ON_button_img
            self.entry_red_ratio['state'] = 'disable'
            self.entry_green_ratio['state'] = 'disable'
            self.entry_blue_ratio['state'] = 'disable'

        elif self.auto_white_toggle == False:
            self.btn_auto_white['image'] = self.toggle_OFF_button_img
            self.entry_red_ratio['state'] = 'normal'
            self.entry_green_ratio['state'] = 'normal'
            self.entry_blue_ratio['state'] = 'normal'

    def black_lvl_btn_state(self):
        if self.black_lvl_toggle == True:
            self.btn_enable_black_lvl['image'] = self.toggle_ON_button_img
            self.entry_black_lvl['state'] = 'normal'

        elif self.black_lvl_toggle == False:
            self.btn_enable_black_lvl['image'] = self.toggle_OFF_button_img
            self.entry_black_lvl['state'] = 'disable'

    def sharpness_btn_state(self):
        if self.sharpness_toggle == True:
            self.btn_enable_sharpness['image'] = self.toggle_ON_button_img
            self.entry_sharpness['state'] = 'normal'

        elif self.sharpness_toggle == False:
            self.btn_enable_sharpness['image'] = self.toggle_OFF_button_img
            self.entry_sharpness['state'] = 'disable'


    def camera_disconnect_disp(self, event, tk_canvas):
        # print(event.width, event.height)
        tk_canvas.delete('img')
        tk_canvas.create_image(event.width/2, event.height/2, image=self.cam_disconnect_img, anchor='center', tags='img')
        tk_canvas.image = self.cam_disconnect_img

    ###############################################################################################
    #6. CAMERA GUI FUNCTIONS (HIKVISION)
    def open_device(self, hikvision_devList, nSelCamIndex = 0):
        if True == self.cam_conn_status:
            Info_Msgbox(message = 'Camera is Running!', font = 'Helvetica 10', message_anchor = 'w')
            return

        if len(hikvision_devList) > 0:
            err_flag = False
            try:
                ret = self.obj_cam_operation.Open_device(hikvision_devList[int(nSelCamIndex)])
            
            except Exception as e:
                err_flag = True
                print('Hikvision Open Device Error: ', e)
                self.cam_conn_status = False

            if err_flag == False:
                if  0!= ret:
                    self.cam_conn_status = False
                else:
                    self.cam_connect_class.cam_connection_toplvl.destroy()
                    self.cam_connect_class.CAM_stop_checkforUpdates()
                    # self.CAM_stop_checkforUpdates(self.main_frame)

                    self.cam_conn_status = True
                    self._pause_auto_toggle = False
                    self.cam_mode_str = 'continuous'
                    self.cam_mode_var.set(self.cam_mode_str)
                    self.trigger_src_func()

                    self.popout_save_btn['state'] = 'normal'

                    self.get_parameter_exposure()
                    self.get_parameter_gain()
                    self.get_parameter_framerate()
                    self.get_parameter_brightness()
                    self.get_parameter_white()

                    self.get_parameter_black_lvl()
                    self.get_parameter_sharpness()

                    self.obj_cam_operation.Normal_Mode_display_clear()
                    self.obj_cam_operation.SQ_Mode_display_clear()

                    self.rec_setting_param[2] = self.pixel_format_combobox.get()

                    try:
                        self.rec_pixel_format_sel.current(self.pixel_format_list.index(self.pixel_format_combobox.get()))
                    except (AttributeError, tk.TclError):
                        pass

    # ch:开始取流 | en:Start grab image
    def start_grabbing(self):
        self.cam_display_place_GUI_1()

        self.cam_disp_sq_live.place(x = 0, y = 25, relx = 0, rely = 0, relwidth = 1, relheight = 0.5, height = -25, anchor = 'nw')

        ret = self.obj_cam_operation.Start_grabbing()
        if ret == 0:
            self.__start_grab = True
            self.grab_btn_state(self.btn_grab_frame, self.stop_grabbing)
            self.pixel_format_combobox['state'] = 'disable'
            
        else:
            self.__start_grab = False
            self.cam_display_forget_GUI_1()

    # ch:停止取流 | en:Stop grab image
    def stop_grabbing(self):
        self.__start_grab = False
        try:
            self.obj_cam_operation.Stop_grabbing()
        except AttributeError:
            pass
        #self.start_grab_status = False

        self.cam_display_forget_GUI_1()

        self.cam_disp_sq_live.place_forget()
        self.cam_popout_close()
        self.grab_btn_state(self.btn_grab_frame, self.start_grabbing)
        self.pixel_format_combobox['state'] = 'readonly'

    # ch:关闭设备 | Close device
    def cam_disconnect(self):
        if self.obj_cam_operation.record_init == True:
            ask_msgbox = Ask_Msgbox('Video Recording Is Still in Progress!\nDisconnecting now will not generate a Video.\n\nQuit anyways?'
                , parent = self.master, title = 'Warning', width = 400, mode = 'warning')
            if ask_msgbox.ask_result() == True:
                self.close_device()
            else:
                pass
        else:
            self.close_device()

    def close_device(self):
        try:
            self.obj_cam_operation.Stop_grabbing()
        except AttributeError:
            pass

        self.btn_normal_cam_mode.invoke()

        self.cam_display_forget_GUI_1()

        self.cam_disp_sq_live.place_forget()

        self.clear_display_GUI_2()
        
        self.cam_popout_close()

        try:
            self.popout_save_btn['state'] = 'disable'
        except Exception:
            pass

        try:
            self.SQ_fr_popout_toplvl.destroy()
        except (AttributeError, tk.TclError):
            pass

        self.record_setting_close()

        del self.cam_sq_frame_cache
        self.cam_sq_frame_cache = None
        ##############################################################################
        self.grab_btn_init_state(self.btn_grab_frame, self.start_grabbing)

        self.cam_conn_status = False
        self._pause_auto_toggle = False

        self.__start_grab = False
        # self.cam_connect_class.cam_connect_btn_state()

        self.clear_img_save_msg_box()
        self.clear_record_msg_box()

        self.stop_auto_toggle_parameter()

        self.record_stop_func()
        self.time_lapse_var.set('')

        try:
            self.obj_cam_operation.Close_device()
        except Exception:
            pass

    def cam_quit_func(self):
        try:
            self.obj_cam_operation.Stop_grabbing()
        except AttributeError:
            pass

        try:
            self.obj_cam_operation.Close_device()
        except AttributeError:
            pass

    #ch:设置触发模式 | en:set trigger mode
    def set_triggermode(self):
        # strMode = self.cam_mode_var.get()
        # print(strMode)
        # print(self.cam_mode_str)
        if self.cam_mode_var.get() == 'continuous':
            if self.cam_mode_str != self.cam_mode_var.get():
                self.cam_mode_str = self.cam_mode_var.get()
                self.btn_save_img['state'] = 'normal'
                
                self.capture_img_checkbtn['state'] = 'normal'
                self.popout_capture_img_btn['state'] = 'normal'

                self.checkbtn_trigger_src['state'] = 'disable'
                self.btn_trigger_once['state'] = 'disable'

                self.set_custom_save_checkbtn['state'] = 'normal'
                self.trigger_auto_save_checkbtn['state'] = 'disable'

                self.SQ_auto_save_checkbtn['state'] = 'disable'

                self.trigger_auto_save_bool.set(0)
                self.SQ_auto_save_bool.set(0)

                if self.obj_cam_operation.video_write_thread is None:
                    self.record_btn_1['state'] = 'normal'

                self.obj_cam_operation.Set_trigger_mode(self.cam_mode_str)

        elif self.cam_mode_var.get() == 'triggermode':
            #print('triggermode')
            if self.cam_mode_str != self.cam_mode_var.get():
                self.obj_cam_operation.sq_frame_save_list *= 0

                ### UPDATE 18-8-2021
                self.obj_cam_operation.ext_sq_fr_init = False

                self.cam_sq_frame_cache = None

                self.cam_mode_str = self.cam_mode_var.get()
                self.obj_cam_operation.b_save = False

                self.btn_save_img['state'] = 'normal'

                self.capture_img_checkbtn['state'] = 'disable'
                self.popout_capture_img_btn['state'] = 'disable'
                self.capture_img_status.set(0)

                self.set_custom_save_checkbtn['state'] = 'normal'

                self.checkbtn_trigger_src['state'] = 'normal'
                self.trigger_src_func()

                self.trigger_auto_save_checkbtn['state'] = 'normal'

                self.SQ_auto_save_checkbtn['state'] = 'normal'
                
                self.record_btn_1['state'] = 'disable'

                self.clear_display_GUI_2()
                #print('Frame Display Cleared...')
                if self.record_bool == True:
                    self.record_stop_func()
                    self.obj_cam_operation.record_init = False

                self.obj_cam_operation.Set_trigger_mode(self.cam_mode_str)

    def set_trigger_autosave(self):
        #print(self.trigger_auto_save_bool.get(), self.SQ_auto_save_bool.get())
        if self.trigger_auto_save_bool.get() == 1:
            self.popout_save_btn['state'] = 'disable'
            self.btn_save_img['state'] = 'disable'
            self.set_custom_save_bool.set(0)
            self.set_custom_save()
            self.set_custom_save_checkbtn['state'] = 'disable'
            self.popout_set_custom_save_btn['state'] = 'disable'

            if self.SQ_auto_save_bool.get() == 1:
                self.SQ_auto_save_bool.set(0)

        elif self.trigger_auto_save_bool.get() == 0:
            self.popout_save_btn['state'] = 'normal'
            self.btn_save_img['state'] = 'normal'
            self.set_custom_save_checkbtn['state'] = 'normal'
            self.popout_set_custom_save_btn['state'] = 'normal'

    def set_SQ_autosave(self):
        #print(self.trigger_auto_save_bool.get(), self.SQ_auto_save_bool.get())
        if self.SQ_auto_save_bool.get() == 1:
            if self.trigger_auto_save_bool.get() == 1:
                self.trigger_auto_save_bool.set(0)
                self.set_trigger_autosave()

    def trigger_src_func(self, event = None):
        if self.triggercheck_val.get() == 0:
            strSrc = 'LINE0'
            self.btn_trigger_once['state'] = 'disable'

        elif self.triggercheck_val.get() == 1:
            strSrc = 'SOFTWARE'
            self.btn_trigger_once['state'] = 'normal'

        self.obj_cam_operation.Trigger_Source(strSrc)

    #ch:设置触发命令 | en:set trigger software
    def trigger_once(self):
        #nCommand = self.triggercheck_val.get()
        #self.obj_cam_operation.Trigger_once(nCommand)
        self.obj_cam_operation.Trigger_once()

    def sq_frame_save(self):
        self.obj_cam_operation.Save_SQ_Frame()


    def set_custom_save(self):
        if self.set_custom_save_bool.get() == 1:
            self.popout_save_btn['command'] = self.custom_img_save_func
            self.btn_save_img['command'] = self.custom_img_save_func

        elif self.set_custom_save_bool.get() == 0:
            self.popout_save_btn['command'] = self.img_save_func
            self.btn_save_img['command'] = self.img_save_func

    def img_save_func(self):
        if True == self.obj_cam_operation.check_cam_frame():
            self.obj_cam_operation.custom_b_save = False
            self.obj_cam_operation.b_save = True
            self.obj_cam_operation.img_save_flag = False
            self.obj_cam_operation.img_save_folder = None
            self.img_save_msg_box()

            if self.obj_cam_operation.trigger_mode == True:
                self.obj_cam_operation.Trigger_Mode_Save()

    def custom_img_save_func(self):
        if True == self.obj_cam_operation.check_cam_frame():
            if True == self.cam_popout_toplvl.check_open():
                self.cam_popout_toplvl.withdraw()
            err_flag = False
            # print(self.save_img_format_sel.get())
            file_im_format = [(str(self.save_img_format_sel.get()).upper() + ' file', '*' + str(self.save_img_format_sel.get()))]

            # f = filedialog.asksaveasfilename(initialdir = self.__save_curr_dir, defaultextension = file_im_format, filetypes = file_im_format, confirmoverwrite=False)
            f = filedialog.asksaveasfilename(initialdir = self.__save_curr_dir, defaultextension = file_im_format, filetypes = file_im_format)
            
            if True == self.cam_popout_toplvl.check_open():
                self.cam_popout_toplvl.show()
            if f is '': # asksaveasfile return `None` if dialog closed with "cancel".
                return

            file_extension = os.path.splitext(f)[-1]

            if not(file_extension in self.save_img_format_list):
                err_flag = True
                Error_Msgbox(message = 'Save Image Function Does Not Support File Extension ' + '(*' + file_extension + ')'
                    , title = 'Error Image Save'
                    , font = 'Helvetica 11', message_anchor = 'c')

            elif (file_extension in self.save_img_format_list):
                if file_extension != str(self.save_img_format_sel.get()):
                    err_flag = True
                    Error_Msgbox(message = 'Different Image Format Detected!' + '(*' + file_extension + ')'
                        + '\n\nTo Save in a different Image Format, please select the desired format before saving!'
                    , title = 'Error Image Save'
                    , font = 'Helvetica 11', message_anchor = 'c', width = 300, height = 200)

            if err_flag == False:
                file_name = os.path.basename(os.path.splitext(f)[0])
                folder_name = str((pathlib.Path(f)).parent)
                # print(file_name)
                # print(file_extension)
                # print(os.path.exists(f))
                self.__save_curr_dir = folder_name

                if (os.path.exists(f)) == True:
                    self.obj_cam_operation.set_custom_save_param(folder_name, file_name, overwrite_bool = True)
                else:
                    self.obj_cam_operation.set_custom_save_param(folder_name, file_name, overwrite_bool = False)

                self.obj_cam_operation.custom_b_save = True
                self.obj_cam_operation.b_save = False
                self.obj_cam_operation.img_save_flag = False
                self.obj_cam_operation.img_save_folder = None
                self.img_save_msg_box()

                if self.obj_cam_operation.trigger_mode == True:
                    self.obj_cam_operation.Trigger_Mode_Save()
            

    def img_save_msg_box(self):
        if self.cam_conn_status == True:
            ##Important note... self.__img_save_flag value cannot be accessed even if changed.
            # print(self.obj_cam_operation.img_save_flag)
            # print('Image Save Msgbox Loop...')
            if self.obj_cam_operation.img_save_flag == True:
                self.clear_img_save_msg_box()
                # print('Image Save Msgbox Finished...')
                Info_Msgbox(message = 'Save Image Success!' + '\n\n' + str(self.obj_cam_operation.img_save_folder), title = 'Image Save'
                    , font = 'Helvetica 10', width = 400, height = 180)

            elif self.obj_cam_operation.img_save_flag == False:
                self.imsave_msgbox_handle = self.cam_ctrl_frame.after(100, self.img_save_msg_box)

        else:
            ##Just to flush out any left-over tkinter thread
            self.clear_img_save_msg_box()

    def clear_img_save_msg_box(self):
        if self.imsave_msgbox_handle is not None:
            self.cam_ctrl_frame.after_cancel(self.imsave_msgbox_handle)
            del self.imsave_msgbox_handle
            self.imsave_msgbox_handle = None
            self.obj_cam_operation.img_save_flag = False

    def get_parameter(self,event=None):
        self.obj_cam_operation.Get_parameter_framerate()
        self.obj_cam_operation.Get_parameter_exposure()
        self.obj_cam_operation.Get_parameter_gain()
        self.obj_cam_operation.Get_parameter_brightness()
        self.obj_cam_operation.Get_parameter_white()
        self.obj_cam_operation.Get_parameter_black_lvl()
        self.obj_cam_operation.Get_parameter_sharpness()

        self.cam_param_float[0] = self.obj_cam_operation.exposure_time
        self.cam_param_float[1] = self.obj_cam_operation.gain
        self.cam_param_float[2] = self.obj_cam_operation.frame_rate

        self.cam_param_int[0] = self.obj_cam_operation.brightness
        self.cam_param_int[1] = self.obj_cam_operation.red_ratio
        self.cam_param_int[2] = self.obj_cam_operation.green_ratio
        self.cam_param_int[3] = self.obj_cam_operation.blue_ratio
        self.cam_param_int[4] = self.obj_cam_operation.black_lvl
        self.cam_param_int[5] = self.obj_cam_operation.sharpness

        self.exposure_str.set(self.cam_param_float[0])
        self.gain_str.set(self.cam_param_float[1])
        self.framerate_str.set(self.cam_param_float[2])

        self.brightness_str.set(self.cam_param_int[0])
        self.red_ratio_str.set(self.cam_param_int[1])
        self.green_ratio_str.set(self.cam_param_int[2])
        self.blue_ratio_str.set(self.cam_param_int[3])
        self.black_lvl_str.set(self.cam_param_int[4])
        self.sharpness_str.set(self.cam_param_int[5])

        int_validate(self.entry_brightness, limits=(0,255))
        int_validate(self.entry_red_ratio, limits=(1,4095))
        int_validate(self.entry_green_ratio, limits=(1,4095))
        int_validate(self.entry_blue_ratio, limits=(1,4095))
        int_validate(self.entry_black_lvl, limits=(0,4095))
        int_validate(self.entry_sharpness, limits=(0,100))

        
    def start_auto_toggle_parameter(self):
        self.get_parameter_exposure()
        self.get_parameter_gain()
        self.get_parameter_white()
        # print('self.auto_exposure_toggle: ',self.auto_exposure_toggle)
        # print('self.auto_gain_toggle: ',self.auto_gain_toggle)
        # print('self.auto_white_toggle: ',self.auto_white_toggle)

    def stop_auto_toggle_parameter(self):
        self.stop_auto_exposure()
        self.stop_auto_gain()
        self.stop_auto_white()

    def unpause_auto_toggle_parameter(self):
        self._pause_auto_toggle = False
        self.get_parameter_exposure()
        self.get_parameter_gain()
        self.get_parameter_white()

    def pause_auto_toggle_parameter(self):
        self._pause_auto_toggle = True
        self.stop_auto_exposure()
        self.stop_auto_gain()
        self.stop_auto_white()

    def get_parameter_exposure(self,event=None):
        if self.cam_conn_status == True:
            if self.auto_exposure_toggle == True:
                self.auto_exposure_handle = self.cam_ctrl_frame.after(300, self.get_parameter_exposure)

            elif self.auto_exposure_toggle == False:
                self.stop_auto_exposure()
            try:
                self.obj_cam_operation.Get_parameter_exposure()
                self.cam_param_float[0] = self.obj_cam_operation.exposure_time
            except AttributeError:
                pass
        else:
            pass
        #print(self.cam_param_float[0])
        self.exposure_str.set(self.cam_param_float[0])

    def get_parameter_gain(self,event=None):
        if self.cam_conn_status == True:
            if self.auto_gain_toggle == True:
                self.auto_gain_handle = self.cam_ctrl_frame.after(300, self.get_parameter_gain)

            elif self.auto_gain_toggle == False:
                self.stop_auto_gain()
            try:
                self.obj_cam_operation.Get_parameter_gain()
                self.cam_param_float[1] = self.obj_cam_operation.gain
            except AttributeError:
                pass
        else:
            pass
        self.gain_str.set(self.cam_param_float[1])

    def get_parameter_white(self,event=None):
        # print(self.auto_white_toggle)
        if self.cam_conn_status == True:
            if self.auto_white_toggle == True:
                self.auto_white_handle = self.cam_ctrl_frame.after(300, self.get_parameter_white)

            elif self.auto_white_toggle == False:
                self.stop_auto_white()
            try:
                self.obj_cam_operation.Get_parameter_white()
                self.cam_param_int[1] = self.obj_cam_operation.red_ratio
                self.cam_param_int[2] = self.obj_cam_operation.green_ratio
                self.cam_param_int[3] = self.obj_cam_operation.blue_ratio

            except Exception: #as e: #AttributeError:
                # print(e)
                pass
        else:
            pass
        # print(self.cam_param_int)
        self.red_ratio_str.set(self.cam_param_int[1])
        self.green_ratio_str.set(self.cam_param_int[2])
        self.blue_ratio_str.set(self.cam_param_int[3])
        int_validate(self.entry_red_ratio, limits=(1,4095))
        int_validate(self.entry_green_ratio, limits=(1,4095))
        int_validate(self.entry_blue_ratio, limits=(1,4095))

    def get_parameter_framerate(self,event=None):
        self.obj_cam_operation.Get_parameter_framerate()
        self.cam_param_float[2] = self.obj_cam_operation.frame_rate
        self.framerate_str.set(self.cam_param_float[2])

        self.rec_setting_param[0] = self.obj_cam_operation.frame_rate
        try:
            self.rec_framerate_str.set(self.rec_setting_param[0])
        except(AttributeError, tk.TclError):
            pass

    def get_parameter_brightness(self, event=None):
        self.obj_cam_operation.Get_parameter_brightness()
        self.cam_param_int[0] = self.obj_cam_operation.brightness
        #print('self.cam_param_int[0]: ',self.cam_param_int[0])
        self.brightness_str.set(self.cam_param_int[0])
        int_validate(self.entry_brightness, limits=(0,255))

    def get_parameter_black_lvl(self, event=None):
        self.obj_cam_operation.Get_parameter_black_lvl()
        self.cam_param_int[4] = self.obj_cam_operation.black_lvl
        #print('self.cam_param_int[4]: ',self.cam_param_int[4])
        self.black_lvl_str.set(self.cam_param_int[4])
        int_validate(self.entry_black_lvl, limits=(0,4095))

    def get_parameter_sharpness(self, event=None):
        self.obj_cam_operation.Get_parameter_sharpness()
        self.cam_param_int[5] = self.obj_cam_operation.sharpness
        #print('self.cam_param_int[5]: ',self.cam_param_int[5])
        self.sharpness_str.set(self.cam_param_int[5])
        int_validate(self.entry_sharpness, limits=(0,100))

    def set_parameter(self,event=None):
        self.set_parameter_framerate()
        if self.auto_exposure_toggle == False:
            self.set_parameter_exposure()
        if self.auto_gain_toggle == False:
            self.set_parameter_gain()
        self.set_parameter_brightness()
        if self.auto_white_toggle == False:
            self.set_parameter_red_ratio()
            self.set_parameter_green_ratio()
            self.set_parameter_blue_ratio()
        self.set_parameter_black_lvl()
        self.set_parameter_sharpness()

    def set_parameter_exposure(self,event=None):
        if self.cam_conn_status == True:
            # tk_float_verify(self.exposure_str, self.cam_param_float[0])
            tk_float_verify(self.entry_exposure, self.exposure_str, 28, 1000000, self.cam_param_float[0], revert_bool = False)

            self.obj_cam_operation.exposure_time = float(self.entry_exposure.get())
            self.obj_cam_operation.Set_parameter_exposure(self.obj_cam_operation.exposure_time)

            if self.revert_val_exposure == False:
                #print('self.revert_val_exposure: False')
                self.cam_param_float[0] = self.obj_cam_operation.exposure_time

            elif self.revert_val_exposure == True:
                #print('self.revert_val_exposure: True')
                self.exposure_str.set(self.cam_param_float[0])
                self.revert_val_exposure = False
        else:
            self.exposure_str.set(self.cam_param_float[0])
            self.revert_val_exposure = False

    def set_parameter_gain(self,event=None):
        if self.cam_conn_status == True:
            # tk_float_verify(self.gain_str, self.cam_param_float[1])
            tk_float_verify(self.entry_gain, self.gain_str, 0, 15.0062, self.cam_param_float[1], revert_bool = False)

            self.obj_cam_operation.gain = float(self.entry_gain.get())
            self.obj_cam_operation.Set_parameter_gain(self.obj_cam_operation.gain)

            if self.revert_val_gain == False:
                #print('self.revert_val_gain: False')
                self.cam_param_float[1] = self.obj_cam_operation.gain

            elif self.revert_val_gain == True:
                #print('self.revert_val_gain: True')
                self.gain_str.set(self.cam_param_float[1])
                self.revert_val_gain = False
        else:
            self.gain_str.set(self.cam_param_float[1])
            self.revert_val_gain = False

    def set_parameter_framerate(self,event=None):
        if self.cam_conn_status == True:
            # tk_float_verify(self.framerate_str,self.cam_param_float[2])
            tk_float_verify(self.entry_framerate, self.framerate_str, 1, 1000, self.cam_param_float[2], revert_bool = False)

            self.obj_cam_operation.frame_rate = float(self.entry_framerate.get())
            self.obj_cam_operation.Set_parameter_framerate(self.obj_cam_operation.frame_rate)

            if self.revert_val_framerate == False:
                #print('self.revert_val_framerate: False')
                self.cam_param_float[2] = self.obj_cam_operation.frame_rate
                try:
                    self.rec_setting_param[0] = self.obj_cam_operation.frame_rate
                    self.rec_framerate_str.set(self.rec_setting_param[0])
                except (AttributeError, tk.TclError):
                    pass

            elif self.revert_val_framerate == True:
                #print('self.revert_val_framerate: True')
                self.framerate_str.set(self.cam_param_float[2])
                try:
                    self.rec_framerate_str.set(self.rec_setting_param[0])
                except (AttributeError, tk.TclError):
                    pass
                self.revert_val_framerate = False
        else:
            self.framerate_str.set(self.cam_param_float[2])
            try:
                self.rec_framerate_str.set(self.rec_setting_param[0])
            except (AttributeError, tk.TclError):
                pass
            self.revert_val_framerate = False

    def set_parameter_brightness(self, event = None):
        if self.cam_conn_status == True:
            if self.brightness_str.get() == '':
                self.brightness_str.set(self.cam_param_int[0])
            int_validate(self.entry_brightness, limits=(0,255))

            self.obj_cam_operation.brightness = int(self.entry_brightness.get())
            self.obj_cam_operation.Set_parameter_brightness(self.obj_cam_operation.brightness)

            if self.revert_val_brightness == False:
                self.cam_param_int[0] = self.obj_cam_operation.brightness
            elif self.revert_val_brightness == True:
                self.brightness_str.set(self.cam_param_int[0])
                int_validate(self.entry_brightness, limits=(0,255))
                self.revert_val_brightness = False

        else:
            self.brightness_str.set(self.cam_param_int[0])
            int_validate(self.entry_brightness, limits=(0,255))
            self.revert_val_brightness = False

    def set_parameter_red_ratio(self, event = None):
        if self.cam_conn_status == True:
            if self.red_ratio_str.get() == '':
                self.red_ratio_str.set(self.cam_param_int[1])
            int_validate(self.entry_red_ratio, limits=(1,4095))

            self.obj_cam_operation.red_ratio = int(self.entry_red_ratio.get())
            self.obj_cam_operation.Set_parameter_red_ratio(self.obj_cam_operation.red_ratio)

            if self.revert_val_red_ratio == False:
                self.cam_param_int[1] = self.obj_cam_operation.red_ratio
            elif self.revert_val_red_ratio == True:
                self.red_ratio_str.set(self.cam_param_int[1])
                int_validate(self.entry_red_ratio, limits=(1,4095))
                self.revert_val_red_ratio = False

        else:
            self.red_ratio_str.set(self.cam_param_int[1])
            int_validate(self.entry_red_ratio, limits=(1,4095))
            self.revert_val_red_ratio = False

    def set_parameter_green_ratio(self, event = None):
        if self.cam_conn_status == True:
            if self.green_ratio_str.get() == '':
                self.green_ratio_str.set(self.cam_param_int[2])
            int_validate(self.entry_green_ratio, limits=(1,4095))

            self.obj_cam_operation.green_ratio = int(self.entry_green_ratio.get())
            self.obj_cam_operation.Set_parameter_green_ratio(self.obj_cam_operation.green_ratio)

            if self.revert_val_green_ratio == False:
                self.cam_param_int[2] = self.obj_cam_operation.green_ratio
            elif self.revert_val_green_ratio == True:
                self.green_ratio_str.set(self.cam_param_int[2])
                int_validate(self.entry_green_ratio, limits=(1,4095))
                self.revert_val_green_ratio = False

        else:
            self.green_ratio_str.set(self.cam_param_int[2])
            int_validate(self.entry_green_ratio, limits=(1,4095))
            self.revert_val_green_ratio = False

    def set_parameter_blue_ratio(self, event = None):
        if self.cam_conn_status == True:
            if self.blue_ratio_str.get() == '':
                self.blue_ratio_str.set(self.cam_param_int[3])
            int_validate(self.entry_blue_ratio, limits=(1,4095))

            self.obj_cam_operation.blue_ratio = int(self.entry_blue_ratio.get())
            self.obj_cam_operation.Set_parameter_blue_ratio(self.obj_cam_operation.blue_ratio)

            if self.revert_val_blue_ratio == False:
                self.cam_param_int[3] = self.obj_cam_operation.blue_ratio
            elif self.revert_val_blue_ratio == True:
                self.blue_ratio_str.set(self.cam_param_int[3])
                int_validate(self.entry_blue_ratio, limits=(1,4095))
                self.revert_val_blue_ratio = False

        else:
            self.blue_ratio_str.set(self.cam_param_int[3])
            int_validate(self.entry_blue_ratio, limits=(1,4095))
            self.revert_val_blue_ratio = False

    def set_parameter_black_lvl(self, event = None):
        if self.cam_conn_status == True:
            if self.black_lvl_str.get() == '':
                self.black_lvl_str.set(self.cam_param_int[4])
            int_validate(self.entry_black_lvl, limits=(0,4095))
            self.obj_cam_operation.black_lvl = int(self.entry_black_lvl.get())
            self.obj_cam_operation.Set_parameter_black_lvl(self.obj_cam_operation.black_lvl)

            if self.revert_val_black_lvl == False:
                self.cam_param_int[4] = self.obj_cam_operation.black_lvl

            elif self.revert_val_black_lvl == True:
                self.black_lvl_str.set(self.cam_param_int[4])
                self.revert_val_black_lvl = False
        else:
            self.black_lvl_str.set(self.cam_param_int[4])
            int_validate(self.entry_black_lvl, limits=(0,4095))
            self.revert_val_black_lvl = False

    def set_parameter_sharpness(self, event = None):
        if self.cam_conn_status == True:
            if self.sharpness_str.get() == '':
                self.sharpness_str.set(self.cam_param_int[5])
            int_validate(self.entry_sharpness, limits=(0,100))
            self.obj_cam_operation.sharpness = int(self.entry_sharpness.get())
            self.obj_cam_operation.Set_parameter_sharpness(self.obj_cam_operation.sharpness)

            if self.revert_val_sharpness == False:
                self.cam_param_int[5] = self.obj_cam_operation.sharpness

            elif self.revert_val_sharpness == True:
                self.sharpness_str.set(self.cam_param_int[5])
                self.revert_val_sharpness = False
        else:
            self.sharpness_str.set(self.cam_param_int[5])
            int_validate(self.entry_sharpness, limits=(0,100))
            self.revert_val_sharpness = False

    def set_auto_exposure(self,event = None):
        self.obj_cam_operation.Auto_Exposure()
        self.get_parameter_exposure()
        self.camera_brightness_entry_state()
        self.get_parameter_brightness()

    def set_auto_gain(self,event = None):
        self.obj_cam_operation.Auto_Gain()
        self.get_parameter_gain()
        self.camera_brightness_entry_state()
        self.get_parameter_brightness()

    def set_auto_white(self, event = None):
        self.obj_cam_operation.Auto_White()
        self.get_parameter_white()

    def stop_auto_exposure(self):
        if self.auto_exposure_handle is not None:
            self.cam_ctrl_frame.after_cancel(self.auto_exposure_handle)
            del self.auto_exposure_handle
            self.auto_exposure_handle = None
            # print('Auto Exposure Stopped...')

    def stop_auto_gain(self):
        if self.auto_gain_handle is not None:
            self.cam_ctrl_frame.after_cancel(self.auto_gain_handle)
            del self.auto_gain_handle
            self.auto_gain_handle = None
            # print('Auto Gain Stopped...')

    def stop_auto_white(self):
        if self.auto_white_handle is not None:
            self.cam_ctrl_frame.after_cancel(self.auto_white_handle)
            del self.auto_white_handle
            self.auto_white_handle = None

    def enable_framerate(self,event = None):
        self.obj_cam_operation.Enable_Framerate()

    def enable_black_lvl(self, event = None):
        self.obj_cam_operation.Enable_Blacklevel()

    def enable_sharpness(self, event = None):
        self.obj_cam_operation.Enable_Sharpness()

    def get_pixel_format(self, hex_int):
        # print('get_pixel_format: ',hex_int)
        pixel_str_id = self.obj_cam_operation.Pixel_Format_Str_ID(hex_int)
        if isinstance(pixel_str_id, str) == True:
            self.pixel_format_combobox.current(self.pixel_format_list.index(pixel_str_id))

            if self.obj_cam_operation.Pixel_Format_Mono(pixel_str_id) == True:
                self.popout_ch_sel_btn_state(rgb_bool = False)


            elif self.obj_cam_operation.Pixel_Format_Color(pixel_str_id) == True:
                self.popout_ch_sel_btn_state(rgb_bool = True)


    def pixel_format_sel(self, event = None, pixel_format_str = None):
        # print(event)
        hex_id = None
        _pixel_format = None
        if event is not None and pixel_format_str is None:
            _pixel_format = self.pixel_format_combobox.get()

        elif event is None and pixel_format_str is not None and type(pixel_format_str) == str:
            _pixel_format = pixel_format_str

        if _pixel_format is not None and type(_pixel_format) == str:
            if _pixel_format == "Mono 8":
                hex_id = 0x01080001
            elif _pixel_format == "Mono 10":
                hex_id = 0x01100003
            elif _pixel_format == "Mono 10 Packed":
                hex_id = 0x010C0004
            elif _pixel_format == "Mono 12":
                hex_id = 0x01100005
            elif _pixel_format == "Mono 12 Packed":
                hex_id = 0x010C0006
            elif _pixel_format == "RGB 8":
                hex_id = 0x02180014
            elif _pixel_format == "BGR 8":
                hex_id = 0x02180015
            elif _pixel_format == "YUV 422 (YUYV) Packed":
                hex_id = 0x02100032
            elif _pixel_format == "YUV 422 Packed":
                hex_id = 0x0210001F
            elif _pixel_format == "Bayer RG 8":
                hex_id = 0x01080009
            elif _pixel_format == "Bayer RG 10":
                hex_id = 0x0110000d
            elif _pixel_format == "Bayer RG 10 Packed":
                hex_id = 0x010C0027
            elif _pixel_format == "Bayer RG 12":
                hex_id = 0x01100011
            elif _pixel_format == "Bayer RG 12 Packed":
                hex_id = 0x010C002B

        if hex_id is not None:
            ret_flag = self.obj_cam_operation.Set_Pixel_Format(hex_id)
            if ret_flag == 0:

                if self.obj_cam_operation.Pixel_Format_Mono(_pixel_format) == True:
                    self.popout_ch_sel_btn_state(rgb_bool = False)

                elif self.obj_cam_operation.Pixel_Format_Color(_pixel_format) == True:
                    self.popout_ch_sel_btn_state(rgb_bool = True)
