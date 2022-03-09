####-- LIST OF GROUP FUNCTIONS -- ####
#1. CAMERA POPPOUT DISPLAY
#2. PIXEL COUNT + ROI GENERATION
#3. CAMERA DISPLAY & CONTROL GUI
#4. CREVIS FUNCTION

import os
from os import path
import sys

import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
# from tkinter import filedialog

from PIL import ImageTk, Image, ImageDraw, ImageFont
import numpy as np
import cv2
import imutils

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

from ScrolledCanvas import ScrolledCanvas

from custom_zoom_class import CanvasImage
from tool_tip import CreateToolTip

from crevis_library import CrevisCamera
from crevis_operation import Crevis_Operation

from intvalidate import int_validate
code_PATH = os.getcwd()

sys.path.append(code_PATH + '\\MVS-Python\\MvImport')
from MvCameraControl_class import *

def create_save_folder():
    PATH = os.getcwd()
    create_folder = PATH + r'\TMS_Saved_Images'
    #print(create_folder)
    print
    if path.exists(create_folder):
        #print ('File already exists')
        pass
    else:
        os.mkdir(create_folder)
        #print ('File created')
    return create_folder

def pil_padding_constant(pil_img, pad_left = 0, pad_top = 0, pad_right = 0, pad_btm = 0):
    np_img = np.array(pil_img)
    pad_left, pad_top, pad_right, pad_btm = abs(pad_left), abs(pad_top), abs(pad_right), abs(pad_btm)

    if len(np_img.shape) > 2:
        if np_img.shape[2] == 3:
            np_img = cv2.copyMakeBorder(np_img,
            left = pad_left, top = pad_top, right = pad_right, bottom = pad_btm,
            borderType = cv2.BORDER_CONSTANT, value=[255, 255, 255])

        elif np_img.shape[2] == 4:
            np_img = cv2.cvtColor(np_img, cv2.COLOR_BGRA2BGR)
            np_img = cv2.copyMakeBorder(np_img,
            left = pad_left, top = pad_top, right = pad_right, bottom = pad_btm,
            borderType = cv2.BORDER_CONSTANT, value=[255, 255, 255])

    else:
        np_img = cv2.copyMakeBorder(np_img,
        left = pad_left, top = pad_top, right = pad_right, bottom = pad_btm,
        borderType = cv2.BORDER_CONSTANT, value=[255])

    pil_img = Image.fromarray(np_img)
    return pil_img

def pil_img_save(folder, img_pil, img_name, img_format):
    index = 0
    loop = True
    while loop == True:
        img_path = folder + '\\'+ img_name + '_' + str(index) + img_format
        if (path.exists(img_path)) == True:
            index = index + 1
        elif (path.exists(img_path)) == False:
            loop = False

    img_arr = np.array(img_pil)
    if len(img_arr.shape) == 3:
        img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
    cv2.imwrite(img_path, img_arr)

def tk_float_verify_v0(tk_var, previous_val = None):
    try:
        #VERIFY THE TKINTER ENTRY or SPINBOX: MAKE SURE IT IS NOT EMPTY and is a VALID FLOAT NUMBER
        float(tk_var.get())
    except ValueError:
        if previous_val is not None:
            tk_var.set(previous_val)
        else:
            #print('pass')
            pass
    if len(str(tk_var.get()).split('.')) > 1 and (str(tk_var.get()).split('.'))[0] == '':
        #e.g. if numbers are 00.1 or .1, it will become 0.1
        tk_var.set(float(tk_var.get()))
    else:
        pass

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


def validate_int_entry(d, P, S, positive_bool = 'False'):
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
    # print(positive_bool, type(positive_bool))
    if positive_bool == 'False':
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

    elif positive_bool == 'True':
        if d == '1':
            if len(P) > 1 and (P.split('0')[0]) == '':
                return False
            else:
                try:
                    int(P)
                    if int(P) < 0: #ONLY POSITIVE VALUES ACCEPTED
                        return False
                    else:
                        return True
                except:
                    if P == '':
                        return True
                    else:
                        return False
        elif d == '0':
            return True

def int_validate_register(tk_widget, positive_bool):
    tk_widget['validate']='key'
    tk_widget['vcmd']=(tk_widget.register(validate_int_entry), '%d', '%P', '%S', positive_bool)

def int_validate_limit(tk_widget, tk_var, min_val, max_val, revert_val, revert_bool = False):
    _type = None
    try:
        int(tk_var.get())
        _type = 'int'
    except Exception:
        if tk_var.get() == '':
            tk_var.set(revert_val)
        else:
            _type = None
    if _type == 'int':
        if int(tk_var.get()) < min_val:
            if revert_bool == True:
                tk_var.set(revert_val)
                tk_widget.icursor(tk.END)
            else:
                tk_var.set(min_val)
                tk_widget.icursor(tk.END)

        elif int(tk_var.get()) > max_val:
            if revert_bool == True:
                tk_var.set(revert_val)
                tk_widget.icursor(tk.END)
            else:
                tk_var.set(max_val)
                tk_widget.icursor(tk.END)
                

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

def display_func(display, ref_img, w, h, resize_status = True):
    #img_resize = imutils.resize(ref_img, width = w)
    if resize_status == True:
        img_resize = imutils.resize(ref_img, height = h)
        img_PIL = Image.fromarray(img_resize)
    elif resize_status == False:
        img_PIL = Image.fromarray(ref_img)

    img_tk = ImageTk.PhotoImage(img_PIL)
    display.create_image(w/2, h/2, image=img_tk, anchor='center', tags='img')
    display.image = img_tk

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

# class Crevis_GUI():
#   def __init__(self, crevis_pylib, crevis_operation):
#       self.crevis_pylib = crevis_pylib
#       self.crevis_operation = crevis_operation


class Crevis_GUI(tk.Frame):
    def __init__(self, master, scroll_canvas, crevis_pylib, crevis_operation
        , cam_conn_status, cam_connect_class
        , tms_logo_2 = None, cam_disconnect_img = None
        , toggle_ON_button_img = None, toggle_OFF_button_img = None, img_flip_icon = None, record_start_icon = None, record_stop_icon = None
        , save_icon = None, popout_icon = None, info_icon = None, fit_to_display_icon = None, setting_icon = None, window_icon = None
        , inspect_icon= None, help_icon = None, add_icon = None, minus_icon = None
        , close_icon = None, **kwargs):

        tk.Frame.__init__(self, master, **kwargs)

        self.master = master
        self.scroll_canvas = scroll_canvas

        self.cam_conn_status = cam_conn_status

        self.cam_connect_class = cam_connect_class
        # self.stop_auto_enum_func = stop_auto_enum_func
        # self.cam_connect_btn_state = cam_connect_btn_state

        self.crevis_pylib = crevis_pylib
        self.crevis_operation = crevis_operation

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
        
        ################################################
        self.popout_status = False
        self.popout_var_mode = 'original'

        self.cam_popout_disp = None
        self.cam_display_rgb = None
        self.cam_display_R = None
        self.cam_display_G = None
        self.cam_display_B = None

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
        self.revert_val_red_ratio = self.revert_val_green_ratio = self.revert_val_blue_ratio = False
        self.revert_val_black_lvl = False

        self.auto_gain_toggle = self.auto_exposure_toggle = self.framerate_toggle = False
        self.auto_white_toggle = False
        self.black_lvl_toggle = False

        self.cam_display_width = 300
        self.cam_display_height = 250

        self.flip_img_bool = False

        self.record_bool = False

        self.auto_exposure_handle = None
        self.auto_gain_handle = None
        self.auto_white_handle = None

        self.cam_mode_str = 'continuous'
        self.cam_param_float = np.zeros((3), dtype=np.float32)
        #param_float index--> 0:exposure, 1:gain, 2:frame rate
        self.cam_param_gain = np.zeros((1), dtype = np.uint8)


        self.cam_param_int = np.zeros((6), dtype=np.uint16)
        self.cam_param_int[1] = self.cam_param_int[2] = self.cam_param_int[3] = 1
        #param_int index-->1: R-ch, 2: G-ch, 3: B-ch, 4: black level

        self.crevis_mode_str = 'continuous'

        self.cam_sq_frame_cache = None
        self.tk_sq_disp_list = []

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


        self.camera_display_GUI_1()
        self.camera_display_GUI_2()
        self.camera_control_GUI()
        self.flip_btn_gen()
        self.record_btn_gen()

        self.popout_button_generate()

        self.select_GUI_1()

        self.camera_control_state()

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

        if inactive_button1 != None:
            inactive_button1['disabledforeground'] = 'gray'
            inactive_button1['activeforeground'] = 'black'
            inactive_button1['fg'] = 'black'
            inactive_button1['activebackground'] = orig_colour_bg
            inactive_button1['bg'] = orig_colour_bg
            inactive_button1['font'] = 'Helvetica 10'

    ###############################################################################################
    #1. CAMERA POPPOUT DISPLAY
    def popout_button_generate(self):
        #print(self.popout_icon)
        _master = self.cam_display_fr_1 #self.main_frame
        self.Normal_cam_popout_btn = tk.Button(_master, relief = tk.GROOVE, bd =0 , image = self.popout_icon, bg = 'white')
        CreateToolTip(self.Normal_cam_popout_btn, 'Camera Pop-out Display'
            , 0, -22, width = 145, height = 20)

        self.Normal_cam_popout_btn['command'] = lambda: self.cam_popout_gen(toplvl_W = 700, toplvl_H = 500 + 50, toplvl_title = 'Camera Display')

        self.SQ_cam_popout_btn = tk.Button(self.cam_display_fr_2, relief = tk.GROOVE, bd =0 , image = self.popout_icon, bg = 'white')
        CreateToolTip(self.SQ_cam_popout_btn, 'Camera Pop-out Display'
            , 0, -22, width = 145, height = 20)

        self.SQ_cam_popout_btn['command'] = lambda: self.cam_popout_gen(toplvl_W = 700, toplvl_H = 500 + 50, toplvl_title = 'Camera Display')

        self.SQ_fr_popout_btn = tk.Button(self.cam_display_fr_2, relief = tk.GROOVE, bd =0 , image = self.popout_icon, bg = 'white')
        CreateToolTip(self.SQ_fr_popout_btn, 'Frame Pop-out Display'
            , 0, -22, width = 135, height = 20)

        self.SQ_fr_popout_btn['command'] = lambda: self.SQ_fr_popout_gen(toplvl_W = 700, toplvl_H = 500, toplvl_title = 'SQ Frame Display')

        self.Normal_cam_popout_btn.place(x = self.cam_display_width + self.cam_display_width - 20, y= 0)
        self.SQ_cam_popout_btn.place(x = self.cam_display_width - 20, y= 0)
        self.SQ_fr_popout_btn.place(x = self.cam_display_width + self.cam_display_width - 10, y= 0)

    def check_cam_popout_disp(self):
        try:
            #raise AttributeError('AttributeError supposed to handle.')
            check_bool = tk.Toplevel.winfo_exists(self.cam_popout_toplvl)
            if check_bool == 0:
                self.popout_disp_tk_status.set('Popout Live Display: Inactive')
                self.popout_disp_tk_label['bg'] = 'red'

            elif check_bool == 1:
                self.popout_disp_tk_status.set('Popout Live Display: Active')
                self.popout_disp_tk_label['bg'] = 'forest green'

        except AttributeError:
            self.popout_disp_tk_status.set('Popout Live Display: Inactive')
            self.popout_disp_tk_label['bg'] = 'red'

    def cam_popout_gen(self, toplvl_W, toplvl_H, toplvl_title):
        #print('previous', self.popout_status)
        self.popout_status = True
        #print('after', self.popout_status)
        try:
            #raise AttributeError('AttributeError supposed to handle.')
            check_bool = tk.Toplevel.winfo_exists(self.cam_popout_toplvl)
            
            if check_bool == 0:
                self.cam_popout_toplvl = tk.Toplevel(self.main_frame, width = toplvl_W, height = toplvl_H)

                self.cam_popout_toplvl['bg'] = 'white'
                self.cam_popout_toplvl.title(toplvl_title)
                self.cam_popout_toplvl.minsize(width=toplvl_W, height=toplvl_H)

                screen_width = self.cam_popout_toplvl.winfo_screenwidth()
                screen_height = self.cam_popout_toplvl.winfo_screenheight()
                x_coordinate = int((screen_width/2) - (toplvl_W/2))
                y_coordinate = int((screen_height/2) - (toplvl_H/2))
                self.cam_popout_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))

                self.cam_popout_toplvl.protocol("WM_DELETE_WINDOW", self.cam_popout_close)
                # self.cam_popout_toplvl.bind('<Map>', lambda event: self.popout_topmost_false( toplvl_widget = self.cam_popout_toplvl) )
                # self.cam_popout_toplvl.attributes('-topmost',True)
                try:
                    self.cam_popout_toplvl.iconphoto(False, self.window_icon)
                except Exception:
                    pass

                self.cam_popout_init()
                
                if self.crevis_operation is not None:
                    if self.crevis_operation.numArray is not None:
                        self.popout_cam_disp_func(self.crevis_operation.numArray)
                        self.popout_fit_to_display_func()
            else:
                self.cam_popout_toplvl.deiconify()
                self.cam_popout_toplvl.lift()
                pass

        except (AttributeError, tk.TclError):
            self.cam_popout_toplvl = tk.Toplevel(self.main_frame, width = toplvl_W, height = toplvl_H)

            self.cam_popout_toplvl['bg'] = 'white'
            self.cam_popout_toplvl.title(toplvl_title)
            self.cam_popout_toplvl.minsize(width=toplvl_W, height=toplvl_H)

            screen_width = self.cam_popout_toplvl.winfo_screenwidth()
            screen_height = self.cam_popout_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (toplvl_W/2))
            y_coordinate = int((screen_height/2) - (toplvl_H/2))
            self.cam_popout_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
            self.cam_popout_toplvl.protocol("WM_DELETE_WINDOW", self.cam_popout_close)
            # self.cam_popout_toplvl.bind('<Map>', lambda event: self.popout_topmost_false(toplvl_widget =self.cam_popout_toplvl) )
            # self.cam_popout_toplvl.attributes('-topmost',True)
            try:
                self.cam_popout_toplvl.iconphoto(False, self.window_icon)
            except Exception:
                pass

            self.cam_popout_init()

            if self.crevis_operation is not None:
                if self.crevis_operation.numArray is not None:
                    self.popout_cam_disp_func(self.crevis_operation.numArray)
                    self.popout_fit_to_display_func()

    def popout_fit_to_display_func(self):
        try:
            self.cam_popout_disp.fit_to_display(self.cam_popout_toplvl.winfo_width(),self.cam_popout_toplvl.winfo_height()-30-30-30)
        except (AttributeError, tk.TclError):
            pass

    def popout_sel_btn_gen(self):
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
        self.popout_status = False
        self.popout_var_mode = 'original'
        self.curr_roi_mode = None

        try:
            self.cam_popout_disp.ROI_disable()
        except (AttributeError, tk.TclError):
            pass
        try:
            self.cam_popout_toplvl.destroy()
        except (AttributeError, tk.TclError):
            pass

        self.graph_popout_close()

        if self.crevis_operation is not None:
            if self.crevis_operation.numArray is not None:
                self.crevis_operation.All_Mode_Cam_Disp()

        self.check_cam_popout_disp()

    def cam_popout_init(self):
        self.check_cam_popout_disp()

        try:
            check_bool = tk.Toplevel.winfo_exists(self.cam_popout_toplvl)
            if check_bool == 0:
                pass
            else:
                clear_display_func(self.cam_display_rgb, self.cam_display_R, self.cam_display_G, self.cam_display_B, self.cam_disp_current_frame)
                self.popout_sel_btn_gen()
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
                self.cam_popout_disp.place(x=0, y=30+30+30, relwidth = 1, relheight = 1, anchor = 'nw')


                self.roi_status_var = tk.IntVar()
                self.roi_checkbtn = tk.Checkbutton(self.cam_popout_toplvl, text='ROI Enable', variable = self.roi_status_var, width = 8
                    , onvalue=1, offvalue=0, highlightthickness = 0)#, bg = 'white')
                self.roi_checkbtn['command'] = self.roi_checkbtn_click
                self.roi_checkbtn.place(x=10,y=30)

                self.roi_type_list = ['BOX', 'LINE']
                self.cam_popout_toplvl.option_add('*TCombobox*Listbox.font', ('Helvetica', '10'))
                self.roi_type_combobox = ttk.Combobox(self.cam_popout_toplvl, values=self.roi_type_list, width=10, state='readonly', font = 'Helvetica 10')
                self.roi_type_combobox.unbind_class("TCombobox", "<MouseWheel>")
                self.roi_type_combobox.bind('<<ComboboxSelected>>', self.roi_type_sel)
                self.roi_type_combobox.current(0)
                self.roi_type_combobox['state'] = 'disable'
                self.roi_type_combobox.place(x=100, y=32)

                self.pixel_count_btn = tk.Button(self.cam_popout_toplvl, text = 'Pixel Count', relief = tk.GROOVE, font = 'Helvetica 10')
                self.pixel_count_btn['command'] = lambda: self.graph_popout(toplvl_W = 700, toplvl_H = 500, toplvl_title = 'Pixel Count Graph')
                self.pixel_count_btn.place(x=200, y=0+30)

                self.fit_to_display_btn = tk.Button(self.cam_popout_toplvl, relief = tk.GROOVE, image = self.fit_to_display_icon, borderwidth=0)
                self.fit_to_display_btn['command'] = lambda: self.cam_popout_disp.fit_to_display(self.cam_popout_toplvl.winfo_width(),self.cam_popout_toplvl.winfo_height()-30-30-30)
                CreateToolTip(self.fit_to_display_btn, 'Fit-to-Screen'
                    , 30, 0, width = 80, height = 20)
                self.fit_to_display_btn.place(x=480, y=3)

                graph_update_mode_checkbtn = tk.Checkbutton(self.cam_popout_toplvl, text='Auto-Update Pixel Count', variable = self.auto_graph_status, onvalue=1, offvalue=0, font = 'Helvetica 10')
                graph_update_mode_checkbtn['command'] = self.graph_update_mode
                graph_update_mode_checkbtn.place(x=290, y=0+30)

                self.help_widget = tk.Label(self.cam_popout_toplvl, bg = 'white', image = self.help_icon)
                CreateToolTip(self.help_widget, '1. LEFT-CLICK Mouse & Drag\n   to Move Image inside Image Display.\n' +
                                                '2. RIGHT-CLICK Mouse & Drag\n   to Draw ROI Box (with ROI enabled).\n' +
                                                '3. MOUSEWHEEL-UP to Zoom In.\n' +
                                                '4. MOUSEWHEEL-DOWN to Zoom Out.'
                            ,30, 0, width = 240, height = 100)
                self.help_widget.place(relx=1, x = -35, y = 30+30, anchor = 'nw')

                self.cam_popout_toplvl.deiconify()
                self.cam_popout_toplvl.lift()
        except (AttributeError, tk.TclError):
            pass

    def popout_cam_disp_func(self, numArray):
        #print(self.popout_status)
        try:
            check_bool = tk.Toplevel.winfo_exists(self.cam_popout_toplvl)
            if check_bool == 0:
                pass
            else:
                if self.cam_popout_disp.loaded_img is None:
                    #print(self.cam_popout_disp.loaded_img)
                    #print('init')
                    self.cam_popout_disp.loaded_img = numArray
                    # self.cam_popout_disp.canvas_init_load()
                    if numArray is not None and (isinstance(numArray, np.ndarray)) == True:
                        if len(numArray.shape) == 3:
                            if self.popout_var_mode == 'original':
                                self.cam_popout_disp.canvas_init_load()
                            elif self.popout_var_mode == 'red':
                                self.cam_popout_disp.canvas_init_load(local_img_split = True, ch_index = 0)
                            elif self.popout_var_mode == 'green':
                                self.cam_popout_disp.canvas_init_load(local_img_split = True, ch_index = 1)
                            elif self.popout_var_mode == 'blue':
                                self.cam_popout_disp.canvas_init_load(local_img_split = True, ch_index = 2)

                        else:
                            self.cam_popout_disp.canvas_init_load()

                elif self.cam_popout_disp.loaded_img is not None:
                    #print('reload')
                    #print(self.cam_popout_disp.loaded_img)
                    self.cam_popout_disp.loaded_img = numArray
                    # self.cam_popout_disp.canvas_reload()
                    if numArray is not None and (isinstance(numArray, np.ndarray)) == True:
                        if len(numArray.shape) == 3:
                            if self.popout_var_mode == 'original':
                                self.cam_popout_disp.canvas_reload()

                            elif self.popout_var_mode == 'red':
                                self.cam_popout_disp.canvas_reload(local_img_split = True, ch_index = 0)
                            elif self.popout_var_mode == 'green':
                                self.cam_popout_disp.canvas_reload(local_img_split = True, ch_index = 1)
                            elif self.popout_var_mode == 'blue':
                                self.cam_popout_disp.canvas_reload(local_img_split = True, ch_index = 2)

                        else:
                            self.cam_popout_disp.canvas_reload()

                # if self.cam_popout_toplvl.wm_state() == 'normal':
                #     self.cam_popout_toplvl.lift()
                #     # self.cam_popout_toplvl.attributes('-topmost',True)
                #     # self.cam_popout_toplvl.after_idle(self.cam_popout_toplvl.attributes,'-topmost',False)

        except (AttributeError, tk.TclError):
            pass


    def roi_checkbtn_click(self):
        if self.roi_status_var.get() == 0:
            self.roi_type_combobox['state'] = 'disable'
            self.cam_popout_disp.ROI_disable()
            self.curr_roi_mode = None
            self.histogram_stop_auto_update()
            self.profile_stop_auto_update()

            try:
                self.profile_view_btn['state'] = 'disable'
            except (AttributeError, tk.TclError):
                pass

        elif self.roi_status_var.get() == 1:
            self.roi_type_combobox['state'] = 'readonly'
            self.roi_type_sel()

    def roi_type_sel(self,event = None):
        if self.roi_type_combobox.get() == self.roi_type_list[0]: #BOX
            if self.roi_type_combobox.get() != self.curr_roi_mode:
                self.curr_roi_mode = self.roi_type_combobox.get()
                self.cam_popout_disp.ROI_disable()

                _enable_status = self.cam_popout_disp.ROI_box_enable('Camera')

                if _enable_status == True:
                    try:
                        self.profile_view_btn['state'] = 'disable'
                    except (AttributeError, tk.TclError):
                        pass

                    try:
                        self.hist_view_btn.invoke()
                    except (AttributeError, tk.TclError):
                        pass

                elif _enable_status == False:
                    self.curr_roi_mode = None
                    self.roi_status_var.set(0)
                    self.roi_type_combobox['state'] = 'disable'

        elif self.roi_type_combobox.get() == self.roi_type_list[1]: #LINE
            if self.roi_type_combobox.get() != self.curr_roi_mode:
                self.curr_roi_mode = self.roi_type_combobox.get()
                self.cam_popout_disp.ROI_disable()

                _enable_status = self.cam_popout_disp.ROI_line_enable('Camera')
                
                if _enable_status == True:
                    try:
                        self.profile_view_btn['state'] = 'normal'
                    except (AttributeError, tk.TclError):
                        pass

                    try:
                        self.hist_view_btn.invoke()
                    except (AttributeError, tk.TclError):
                        pass

                elif _enable_status == False:
                    self.curr_roi_mode = None
                    self.roi_status_var.set(0)
                    self.roi_type_combobox['state'] = 'disable'

    ###############################################################################################
    #2. PIXEL COUNT + ROI GENERATION
    def popout_topmost_false(self, toplvl_widget):
        toplvl_widget.attributes('-topmost', 'False')

    def graph_popout(self, toplvl_W, toplvl_H, toplvl_title):
        try:
            #raise AttributeError('AttributeError supposed to handle.')
            check_bool = tk.Toplevel.winfo_exists(self.graph_popout_toplvl)
            
            if check_bool == 0:
                self.graph_popout_toplvl = tk.Toplevel(self.main_frame, width = toplvl_W, height = toplvl_H)

                self.graph_popout_toplvl['bg'] = 'white'
                self.graph_popout_toplvl.title(toplvl_title)
                screen_width = self.graph_popout_toplvl.winfo_screenwidth()
                screen_height = self.graph_popout_toplvl.winfo_screenheight()
                x_coordinate = int((screen_width/2) - (toplvl_W/2))
                y_coordinate = int((screen_height/2) - (toplvl_H/2))
                self.graph_popout_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
                self.graph_popout_toplvl.bind('<Map>', lambda event: self.popout_topmost_false( toplvl_widget = self.graph_popout_toplvl) )
                self.graph_popout_toplvl.protocol("WM_DELETE_WINDOW", self.graph_popout_close)

                try:
                    self.graph_popout_toplvl.iconphoto(False, self.window_icon)
                except Exception:
                    pass

                self.graph_display_init()
            else:
                #print('exist')
                self.graph_popout_toplvl.deiconify()
                self.graph_popout_toplvl.lift()
                pass

        except AttributeError:
            #print('AttributeError caught')
            self.graph_popout_toplvl = tk.Toplevel(self.main_frame, width = toplvl_W, height = toplvl_H)

            self.graph_popout_toplvl['bg'] = 'white'
            self.graph_popout_toplvl.title(toplvl_title)
            screen_width = self.graph_popout_toplvl.winfo_screenwidth()
            screen_height = self.graph_popout_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (toplvl_W/2))
            y_coordinate = int((screen_height/2) - (toplvl_H/2))
            self.graph_popout_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
            self.graph_popout_toplvl.bind('<Map>', lambda event: self.popout_topmost_false( toplvl_widget = self.graph_popout_toplvl) )
            self.graph_popout_toplvl.protocol("WM_DELETE_WINDOW", self.graph_popout_close)

            try:
                self.graph_popout_toplvl.iconphoto(False, self.window_icon)
            except Exception:
                pass

            self.graph_display_init()
    
    def graph_popout_close(self):
        self.histogram_stop_auto_update()
        self.profile_stop_auto_update()
        
        self.curr_graph_view = None
        try:
            self.graph_popout_toplvl.destroy()
        except (AttributeError, tk.TclError):
            pass

    def graph_display_init(self):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.graph_popout_toplvl)
            if check_bool == 0:
                pass
            else:
                #print(self.cam_popout_disp.roi_line_exist)
                self.hist_scroll_class = ScrolledCanvas(master = self.graph_popout_toplvl, frame_w = 700, frame_h = 2300, 
                    canvas_x = 0, canvas_y = 0 + 30, window_bg = 'white', canvas_bg='white', canvas_highlightthickness = 0)
                #self.hist_scroll_class.rmb_all_func()

                self.profile_scroll_class = ScrolledCanvas(master = self.graph_popout_toplvl, frame_w = 700, frame_h = 2300, 
                    canvas_x = 0, canvas_y = 0 + 30, window_bg = 'white', canvas_bg='white', canvas_highlightthickness = 0)
                #self.profile_scroll_class.forget_all_func()

                self.hist_view_btn = tk.Button(self.graph_popout_toplvl, relief = tk.GROOVE, text = 'Histogram', font = 'Helvetica 10', width = 12)
                self.hist_view_btn['command'] = lambda: self.graph_view_sel('histogram', self.hist_view_btn, self.profile_view_btn)
                self.hist_view_btn.place(x =0, y=0)

                self.profile_view_btn = tk.Button(self.graph_popout_toplvl, relief = tk.GROOVE, text = 'Profile', font = 'Helvetica 10', width = 12)
                self.profile_view_btn['command'] = lambda: self.graph_view_sel('profile', self.profile_view_btn, self.hist_view_btn)
                self.profile_view_btn.place(x = 115, y=0)

                graph_update_mode_checkbtn = tk.Checkbutton(self.graph_popout_toplvl, text='Auto-Update Pixel Count', variable = self.auto_graph_status, onvalue=1, offvalue=0, font = 'Helvetica 10')
                graph_update_mode_checkbtn['command'] = self.graph_update_mode
                graph_update_mode_checkbtn.place(x=230, y=1)

                self.hist_display_init()

                self.profile_display_init()

                self.hist_view_btn.invoke()
                #CHECKING THE PROFILE VIEW BUTTON STATUS     
                try:
                    check_bool = tk.Toplevel.winfo_exists(self.cam_popout_toplvl)
                    if check_bool == 0:
                        pass
                    else:
                        if self.roi_status_var.get() ==1 and self.roi_type_combobox.get() == self.roi_type_list[1]:
                            self.profile_view_btn['state'] = 'normal'
                        else:
                            self.profile_view_btn['state'] = 'disable'
                except (AttributeError, tk.TclError):
                    self.profile_view_btn['state'] = 'disable'
                    pass

        except Exception:
            pass

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
        # print(self.crevis_operation)
        self.hist_scroll_class.frame_h = 800
        self.hist_scroll_class.window_fr['height'] = 800
        self.hist_fig_mono = Figure(figsize = (7,7))

        self.plot_hist_mono = self.hist_fig_mono.add_subplot(111)
        self.plot_hist_mono.clear()
        self.hist_fig_mono.suptitle('Monochrome', fontsize=18)
        self.plot_hist_mono.set_ylabel('Pixel Count', fontsize=16)
        self.plot_hist_mono.set_xlabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_hist_mono = tk.Frame(self.hist_scroll_class.window_fr, height = 800 - 100, bg = 'white')
        # self.canvas_fr_hist_mono.place(x = 0, y = 0, relwidth = 1)

        self.hist_canvas_mono = FigureCanvasTkAgg(self.hist_fig_mono, master = self.canvas_fr_hist_mono)
        self.hist_canvas_mono.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_hist_mono = tk.Frame(self.hist_scroll_class.window_fr, height = 35, bg = 'white')
        # self.toolbar_fr_hist_mono.place(relx = 0.1, y = 700, relwidth = 0.8)
        self.toolbar_hist_mono = tkagg.NavigationToolbar2Tk(self.hist_canvas_mono, self.toolbar_fr_hist_mono)
        self.toolbar_hist_mono.update()

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
        # self.canvas_fr_hist_R.place(x = 0, y = 0, relwidth = 1)

        self.hist_canvas_R = FigureCanvasTkAgg(self.hist_fig_R, master = self.canvas_fr_hist_R)
        self.hist_canvas_R.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_hist_R = tk.Frame(self.hist_scroll_class.window_fr, height = 35, bg = 'white')
        # self.toolbar_fr_hist_R.place(relx = 0.1, y = 700, relwidth = 0.8)
        self.toolbar_hist_R = tkagg.NavigationToolbar2Tk(self.hist_canvas_R, self.toolbar_fr_hist_R)
        self.toolbar_hist_R.update()

        self.ax_plt_hist_R = self.plot_hist_R.plot([], [], color="red")

        ##########################################################################################################################
        self.hist_fig_G = Figure(figsize = (7,7))
        self.plot_hist_G = self.hist_fig_G.add_subplot(111)
        self.plot_hist_G.clear()
        self.hist_fig_G.suptitle('Green Channel', fontsize=18)
        self.plot_hist_G.set_ylabel('Pixel Count', fontsize=16)
        self.plot_hist_G.set_xlabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_hist_G = tk.Frame(self.hist_scroll_class.window_fr, height = 800 - 100, bg = 'white')
        # self.canvas_fr_hist_G.place(x = 0, y = 750, relwidth = 1)

        self.hist_canvas_G = FigureCanvasTkAgg(self.hist_fig_G, master = self.canvas_fr_hist_G)
        self.hist_canvas_G.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_hist_G = tk.Frame(self.hist_scroll_class.window_fr, height = 35, bg = 'white')
        # self.toolbar_fr_hist_G.place(relx = 0.1, y = 1450, relwidth = 0.8)
        self.toolbar_hist_G = tkagg.NavigationToolbar2Tk(self.hist_canvas_G, self.toolbar_fr_hist_G)
        self.toolbar_hist_G.update()

        self.ax_plt_hist_G = self.plot_hist_G.plot([], [], color="green")
        ##########################################################################################################################

        self.hist_fig_B = Figure(figsize = (7,7))
        self.plot_hist_B = self.hist_fig_B.add_subplot(111)
        self.plot_hist_B.clear()
        self.hist_fig_B.suptitle('Blue Channel', fontsize=18)
        self.plot_hist_B.set_ylabel('Pixel Count', fontsize=16)
        self.plot_hist_B.set_xlabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_hist_B = tk.Frame(self.hist_scroll_class.window_fr, height = 800 - 100, bg = 'white')
        # self.canvas_fr_hist_B.place(x = 0, y = 1500, relwidth = 1)

        self.hist_canvas_B = FigureCanvasTkAgg(self.hist_fig_B, master = self.canvas_fr_hist_B)
        self.hist_canvas_B.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_hist_B = tk.Frame(self.hist_scroll_class.window_fr, height = 35, bg = 'white')
        # self.toolbar_fr_hist_B.place(relx = 0.1, y = 2200, relwidth = 0.8)
        self.toolbar_hist_B = tkagg.NavigationToolbar2Tk(self.hist_canvas_B, self.toolbar_fr_hist_B)
        self.toolbar_hist_B.update()

        self.ax_plt_hist_B = self.plot_hist_B.plot([], [], color="blue")

    def profile_display_init(self):
        self.profile_scroll_class.frame_h = 800
        self.profile_scroll_class.window_fr['height'] = 800
        self.profile_fig_mono = Figure(figsize = (7,7))

        self.plot_profile_mono = self.profile_fig_mono.add_subplot(111)
        self.plot_profile_mono.clear()
        self.profile_fig_mono.suptitle('Monochrome', fontsize=18)
        self.plot_profile_mono.set_ylabel('Pixel Count', fontsize=16)

        self.canvas_fr_profile_mono = tk.Frame(self.profile_scroll_class.window_fr, height = 800 - 100, bg = 'white')
        # self.canvas_fr_profile_mono.place(x = 0, y = 0, relwidth = 1)

        self.profile_canvas_mono = FigureCanvasTkAgg(self.profile_fig_mono, master = self.canvas_fr_profile_mono)
        self.profile_canvas_mono.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_profile_mono = tk.Frame(self.profile_scroll_class.window_fr, height = 35, bg = 'white')
        # self.toolbar_fr_profile_mono.place(relx = 0.1, y = 700, relwidth = 0.8)
        self.toolbar_profile_mono = tkagg.NavigationToolbar2Tk(self.profile_canvas_mono, self.toolbar_fr_profile_mono)

        self.toolbar_profile_mono.update()

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
        # self.canvas_fr_profile_R.place(x = 0, y = 0, relwidth = 1)

        self.profile_canvas_R = FigureCanvasTkAgg(self.profile_fig_R, master = self.canvas_fr_profile_R)
        self.profile_canvas_R.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_profile_R = tk.Frame(self.profile_scroll_class.window_fr, height = 35, bg = 'white')
        # self.toolbar_fr_profile_R.place(relx = 0.1, y = 700, relwidth = 0.8)
        self.toolbar_profile_R = tkagg.NavigationToolbar2Tk(self.profile_canvas_R, self.toolbar_fr_profile_R)
        self.toolbar_profile_R.update()

        self.ax_plt_profile_R = self.plot_profile_R.plot([], [], color="red")
        ##########################################################################################################################

        self.profile_fig_G = Figure(figsize = (7,7))
        self.plot_profile_G = self.profile_fig_G.add_subplot(111)
        self.plot_profile_G.clear()
        self.profile_fig_G.suptitle('Green Channel', fontsize=18)
        self.plot_profile_G.set_ylabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_profile_G = tk.Frame(self.profile_scroll_class.window_fr, height = 800 - 100, bg = 'white')
        # self.canvas_fr_profile_G.place(x = 0, y = 750, relwidth = 1)

        self.profile_canvas_G = FigureCanvasTkAgg(self.profile_fig_G, master = self.canvas_fr_profile_G)
        self.profile_canvas_G.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_profile_G = tk.Frame(self.profile_scroll_class.window_fr, height = 35, bg = 'white')
        # self.toolbar_fr_profile_G.place(relx = 0.1, y = 1450, relwidth = 0.8)
        self.toolbar_profile_G = tkagg.NavigationToolbar2Tk(self.profile_canvas_G, self.toolbar_fr_profile_G)
        self.toolbar_profile_G.update()

        self.ax_plt_profile_G = self.plot_profile_G.plot([], [], color="green")
        ##########################################################################################################################

        self.profile_fig_B = Figure(figsize = (7,7))
        self.plot_profile_B = self.profile_fig_B.add_subplot(111)
        self.plot_profile_B.clear()
        self.profile_fig_B.suptitle('Blue Channel', fontsize=18)
        self.plot_profile_B.set_ylabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_profile_B = tk.Frame(self.profile_scroll_class.window_fr, height = 800 - 100, bg = 'white')
        # self.canvas_fr_profile_B.place(x = 0, y = 1500, relwidth = 1)

        self.profile_canvas_B = FigureCanvasTkAgg(self.profile_fig_B, master = self.canvas_fr_profile_B)
        self.profile_canvas_B.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_profile_B = tk.Frame(self.profile_scroll_class.window_fr, height = 35, bg = 'white')
        # self.toolbar_fr_profile_B.place(relx = 0.1, y = 2200, relwidth = 0.8)
        self.toolbar_profile_B = tkagg.NavigationToolbar2Tk(self.profile_canvas_B, self.toolbar_fr_profile_B)
        self.toolbar_profile_B.update()

        self.ax_plt_profile_B = self.plot_profile_B.plot([], [], color="blue")
        ##########################################################################################################################

        # self.canvas_fr_profile_mono.place(x = 0, y = 0, relwidth = 1)
        # self.toolbar_fr_profile_mono.place(relx = 0.1, y = 700, relwidth = 0.8)
        # self.canvas_fr_profile_R.place(x = 0, y = 0, relwidth = 1)
        # self.toolbar_fr_profile_R.place(relx = 0.1, y = 700, relwidth = 0.8)
        # self.canvas_fr_profile_G.place(x = 0, y = 750, relwidth = 1)
        # self.toolbar_fr_profile_G.place(relx = 0.1, y = 1450, relwidth = 0.8)
        # self.canvas_fr_profile_B.place(x = 0, y = 1500, relwidth = 1)
        # self.toolbar_fr_profile_B.place(relx = 0.1, y = 2200, relwidth = 0.8)


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

    def hist_display_load_v2(self):
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
                    window_state = str(self.graph_popout_toplvl.wm_state())
                    if window_state == 'normal':
                        self.graph_popout_toplvl.lift()
                        self.graph_popout_toplvl.attributes('-topmost',True)
                        self.graph_popout_toplvl.after_idle(self.graph_popout_toplvl.attributes,'-topmost',False)

                self.graph_histogram_mono(graph_data[0])

            elif len(graph_data) == 3:
                if self.auto_hist_init == False:
                    self.hist_scroll_class.frame_h = 2300
                    self.hist_scroll_class.window_fr['height'] = 2300
                    self.auto_hist_init = True
                    window_state = str(self.graph_popout_toplvl.wm_state())
                    if window_state == 'normal':
                        self.graph_popout_toplvl.lift()
                        self.graph_popout_toplvl.attributes('-topmost',True)
                        self.graph_popout_toplvl.after_idle(self.graph_popout_toplvl.attributes,'-topmost',False)

                self.graph_histogram_R(graph_data[0])
                self.graph_histogram_G(graph_data[1])
                self.graph_histogram_B(graph_data[2])
            pass
        pass

    def graph_pixel_profile(self, data_1, data_2, str_img_type):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.graph_popout_toplvl)
            if check_bool == 0:
                pass
            else:
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

        except (AttributeError, tk.TclError):
            pass

    def histogram_auto_update(self):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.graph_popout_toplvl)
            if check_bool == 0:
                pass
            else:
                _loop_interval = 300 #450

                if self.auto_graph_status.get() == 1:
                    self.auto_hist_update_handle = self.graph_popout_toplvl.after(_loop_interval, self.histogram_auto_update)
                elif self.auto_graph_status.get() == 0:
                    self.auto_hist_update_handle = None
                self.hist_display_load_v2()

        except (AttributeError, tk.TclError):
            pass

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
                    window_state = str(self.graph_popout_toplvl.wm_state())
                    if window_state == 'normal':
                        self.graph_popout_toplvl.lift()
                        self.graph_popout_toplvl.attributes('-topmost',True)
                        self.graph_popout_toplvl.after_idle(self.graph_popout_toplvl.attributes,'-topmost',False)

                self.graph_pixel_profile(profile_data_index, profile_data_mono, 'mono')

            elif len(profile_data_mono) == 0 and (len(profile_data_R) > 0 and len(profile_data_G) > 0 and len(profile_data_B) > 0):
                if self.auto_profile_init == False:
                    self.profile_scroll_class.frame_h = 2300
                    self.profile_scroll_class.window_fr['height'] = 2300
                    self.auto_profile_init = True
                    window_state = str(self.graph_popout_toplvl.wm_state())
                    if window_state == 'normal':
                        self.graph_popout_toplvl.lift()
                        self.graph_popout_toplvl.attributes('-topmost',True)
                        self.graph_popout_toplvl.after_idle(self.graph_popout_toplvl.attributes,'-topmost',False)

                self.graph_pixel_profile(profile_data_index, profile_data_R, 'red')
                self.graph_pixel_profile(profile_data_index, profile_data_G, 'green')
                self.graph_pixel_profile(profile_data_index, profile_data_B, 'blue')
            pass
        pass


    def profile_auto_update(self):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.graph_popout_toplvl)
            if check_bool == 0:
                pass
            else:
                _loop_interval = 300 #450

                if self.auto_graph_status.get() == 1:
                    self.auto_profile_update_handle = self.graph_popout_toplvl.after(_loop_interval, self.profile_auto_update)
                elif self.auto_graph_status.get() == 0:
                    self.auto_profile_update_handle = None

                self.profile_display_load()

        except (AttributeError, tk.TclError):
            pass

    def profile_stop_auto_update(self):
        if self.auto_profile_update_handle is not None:
            self.graph_popout_toplvl.after_cancel(self.auto_profile_update_handle)
            del self.auto_profile_update_handle
            self.auto_profile_update_handle = None
            self.auto_profile_init = False


    def graph_histogram_mono(self, pixel_info = None):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.graph_popout_toplvl)
            if check_bool == 0:
                pass
            else:
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

        except (AttributeError, tk.TclError):
            pass

    def graph_histogram_R(self, pixel_info = None):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.graph_popout_toplvl)
            if check_bool == 0:
                pass
            else:
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

        except (AttributeError, tk.TclError) as e:
            print(e)
            pass

    def graph_histogram_G(self, pixel_info = None):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.graph_popout_toplvl)
            if check_bool == 0:
                pass
            else:
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

        except (AttributeError, tk.TclError):
            pass

    def graph_histogram_B(self, pixel_info = None):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.graph_popout_toplvl)
            if check_bool == 0:
                pass
            else:
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

        except (AttributeError, tk.TclError):
            pass

    ###############################################################################################
    #3. CAMERA DISPLAY & CONTROL GUI
    def select_GUI_1(self):
        self.cam_display_fr_1.place(x=0, y = 30+25)
        self.cam_display_fr_2.place_forget()
        self.GUI_sel_btn_state(self.btn_normal_cam_mode, self.btn_SQ_cam_mode)

        self.btn_save_img.place(x=20, y=30)
        self.trigger_auto_save_checkbtn.place(x=20, y = 60)
        self.SQ_auto_save_checkbtn.place_forget()

        self.btn_save_sq.place_forget()

        self.check_cam_popout_disp()

    def select_GUI_2(self):
        self.cam_display_fr_2.place(x=0, y=30+25)
        self.cam_display_fr_1.place_forget()
        self.GUI_sel_btn_state(self.btn_SQ_cam_mode, self.btn_normal_cam_mode)

        self.btn_save_img.place_forget()
        self.trigger_auto_save_checkbtn.place_forget()
        self.SQ_auto_save_checkbtn.place(x=20, y = 60)

        self.btn_save_sq.place(x=20, y=30)

        self.check_cam_popout_disp()

    def clear_display_GUI_2(self):
        clear_display_func(self.cam_disp_frame_1, self.cam_disp_frame_2, self.cam_disp_frame_3, self.cam_disp_frame_4, self.cam_disp_frame_5
            ,self.cam_disp_frame_6, self.cam_disp_frame_7, self.cam_disp_frame_8, self.cam_disp_frame_9, self.cam_disp_frame_10)
        clear_display_func(self.cam_disp_frame_11, self.cam_disp_frame_12, self.cam_disp_frame_13
            , self.cam_disp_frame_14, self.cam_disp_frame_15, self.cam_disp_frame_16)


    def flip_img_display(self):
        if self.flip_img_bool == False:
            self.flip_img_bool = True
        elif  self.flip_img_bool == True:
            self.flip_img_bool = False

        #print(self.flip_img_bool)

    def flip_btn_gen(self):
        _master = self.cam_display_fr_1 #self.main_frame

        self.flip_btn_1 = tk.Button(_master, relief = tk.GROOVE, bd =0 , image = self.img_flip_icon, bg = 'white')
        #self.flip_btn_1.place(x = self.cam_display_width + self.cam_display_width - 50, y= 25)
        CreateToolTip(self.flip_btn_1, 'Flip Image by 180' + chr(176)
            , 0, -22, width = 115, height = 20)
        self.flip_btn_1['command'] = self.flip_img_display

        self.flip_btn_2 = tk.Button(self.cam_display_fr_2, relief = tk.GROOVE, bd =0 , image = self.img_flip_icon, bg = 'white')
        CreateToolTip(self.flip_btn_2, 'Flip Image by 180' + chr(176)
            , 0, -22, width = 115, height = 20)
        #self.flip_btn_2.place(x = self.cam_display_width - 20, y= 0)
        self.flip_btn_2['command'] = self.flip_img_display

        self.flip_btn_1.place(x = self.cam_display_width + self.cam_display_width - 50, y= 0+2)
        self.flip_btn_2.place(x = self.cam_display_width - 50, y= 0)

    def record_btn_gen(self):
        _master = self.cam_display_fr_1 #self.main_frame

        self.record_btn_1 = tk.Button(_master, relief = tk.GROOVE, bd =0 , bg = 'white')
        self.record_btn_1['image'] = self.record_start_icon

        CreateToolTip(self.record_btn_1, 'Record Video'
            , 0, -22, width = 80, height = 20)
        self.record_btn_1['command'] = self.record_start_func

        self.record_btn_1.place(x = self.cam_display_width + self.cam_display_width - 80, y= 0+2)

    def record_start_func(self):
        if tkinter.messagebox.askokcancel("Video Record", "Do you want to record a video?"):
            self.record_bool = True
            #print('RECORD!', self.record_bool)
            self.record_btn_1['image'] = self.record_stop_icon
            self.record_btn_1['command'] = self.record_stop_func
        else:
            self.record_bool = False
            #print('CANCELLED!', self.record_bool)

    def record_stop_func(self):
        self.record_bool = False
        self.record_btn_1['image'] = self.record_start_icon
        self.record_btn_1['command'] = self.record_start_func
        #print('STOPPED!', self.record_bool)

    def cam_display_place_GUI_1(self):
        self.cam_display_rgb.place(x = 0, y = 0+25+30)
        self.cam_display_R.place(x = self.cam_display_width + 5, y = 0+25+30)
        self.cam_display_G.place(x = 0, y = self.cam_display_height+50+30)
        self.cam_display_B.place(x = self.cam_display_width + 5, y = self.cam_display_height+50+30)

    def cam_display_forget_GUI_1(self):
        self.cam_display_rgb.place_forget()
        self.cam_display_R.place_forget()
        self.cam_display_G.place_forget()
        self.cam_display_B.place_forget()

    def camera_display_GUI_1(self):
        self.cam_display_fr_1 = tk.Frame(self.main_frame, width = self.cam_display_width + self.cam_display_width + 10
            , height = self.cam_display_height + self.cam_display_height + 50 + 30, bg= 'white')

        self.ori_disp_label = tk.Label(self.cam_display_fr_1, text = 'Original Image', font = 'Helvetica 12 bold', bg = 'snow3', fg = 'black')

        self.R_disp_label = tk.Label(self.cam_display_fr_1, text = 'Red Channel', font = 'Helvetica 12 bold', bg = 'red', fg = 'white')

        self.G_disp_label = tk.Label(self.cam_display_fr_1, text = 'Green Channel', font = 'Helvetica 12 bold', bg = 'green', fg = 'white')

        self.B_disp_label = tk.Label(self.cam_display_fr_1, text = 'Blue Channel', font = 'Helvetica 12 bold', bg = 'blue', fg = 'white')

        self.ori_disp_label.place(x = 0, y = 0+30)
        self.R_disp_label.place(x = self.cam_display_width + 5, y = 0+30)
        self.G_disp_label.place(x = 0, y = self.cam_display_height+25+30)
        self.B_disp_label.place(x = self.cam_display_width + 5, y = self.cam_display_height+25+30)


        self.dummy_canvas_rgb = tk.Canvas(self.cam_display_fr_1, width = self.cam_display_width, height = self.cam_display_height, bg = 'snow3', highlightthickness = 0)
        self.dummy_canvas_R = tk.Canvas(self.cam_display_fr_1, width = self.cam_display_width, height = self.cam_display_height, bg = 'red', highlightthickness = 0)
        self.dummy_canvas_G = tk.Canvas(self.cam_display_fr_1, width = self.cam_display_width, height = self.cam_display_height, bg = 'green', highlightthickness = 0)
        self.dummy_canvas_B = tk.Canvas(self.cam_display_fr_1, width = self.cam_display_width, height = self.cam_display_height, bg = 'blue', highlightthickness = 0)

        self.cam_display_rgb = tk.Canvas(self.cam_display_fr_1, width = self.cam_display_width, height = self.cam_display_height, bg = 'snow3', highlightthickness = 0)
        self.cam_display_R = tk.Canvas(self.cam_display_fr_1, width = self.cam_display_width, height = self.cam_display_height, bg = 'red', highlightthickness = 0)
        self.cam_display_G = tk.Canvas(self.cam_display_fr_1, width = self.cam_display_width, height = self.cam_display_height, bg = 'green', highlightthickness = 0)
        self.cam_display_B = tk.Canvas(self.cam_display_fr_1, width = self.cam_display_width, height = self.cam_display_height, bg = 'blue', highlightthickness = 0)

        self.camera_no_display_func()

        self.dummy_canvas_rgb.place(x = 0, y = 0+25+30)
        self.dummy_canvas_R.place(x = self.cam_display_width + 5, y = 0+25+30)
        self.dummy_canvas_G.place(x = 0, y = self.cam_display_height+50+30)
        self.dummy_canvas_B.place(x = self.cam_display_width + 5, y = self.cam_display_height+50+30)

    def gen_camera_disp_canvas(self, master, label_text,label_bg, label_fg,
        canvas_width, canvas_height, canvas_bg, ordinal_index):
        #First widget placement, ordinal index = 0!!
        label_x = 0
        label_y = 0 + np.multiply((canvas_height+25+5), ordinal_index)

        canvas_x = 0
        canvas_y = 0 + 25 + np.multiply((canvas_height + 25+5), ordinal_index)

        label_widget = tk.Label(master, text = label_text, font = 'Helvetica 12 bold', bg = label_bg, fg = label_fg)
        label_widget.place(x=label_x, y=label_y)

        canvas_widget = tk.Canvas(master, width = canvas_width, height = canvas_height, bg = canvas_bg, highlightthickness = 0)
        canvas_widget.place(x=canvas_x, y=canvas_y)

        return canvas_widget

    def custom_scroll_inner_bound(self, event, disp_scroll_class):
        # print(event.type)
        # print(dir(event))
        disp_scroll_class.canvas.bind_all("<MouseWheel>", lambda event: self.custom_inner_scrolly(event, disp_scroll_class))

    def custom_inner_scrolly(self, event, disp_scroll_class):
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

    def camera_display_GUI_2(self):

        self.cam_display_fr_2 = tk.Frame(self.main_frame, width = self.cam_display_width + self.cam_display_width + 10
            , height = self.cam_display_height + self.cam_display_height + 50, bg= 'white')

        self.SQ_frame_scroll_display = ScrolledCanvas(master = self.cam_display_fr_2, frame_w = self.cam_display_width, frame_h = 2800 + 1700, 
            canvas_x = self.cam_display_width + 10, canvas_y = 0 + 25, window_bg = 'white', canvas_highlightthickness = 0)

        self.SQ_frame_scroll_display.rmb_all_func() #To Place the Scroll Canvas

        #CUSTOM MOUSEWHEEL FUNCTION for self.SQ_frame_scroll_display
        self.SQ_frame_scroll_display.scrollx.place_forget()
        self.SQ_frame_scroll_display.scrolly.place_forget()

        self.SQ_frame_scroll_display.canvas.bind('<Enter>', lambda event: self.custom_scroll_inner_bound(event, self.SQ_frame_scroll_display))
        self.SQ_frame_scroll_display.canvas.bind('<Leave>', self.scroll_canvas._bound_to_mousewheel)

        self.dummy_canvas_current_frame = tk.Canvas(self.cam_display_fr_2, width = self.cam_display_width, height = self.cam_display_height, bg = 'snow3', highlightthickness = 0)
        self.dummy_canvas_current_frame.place(x = 0, y = 0+25)

        self.cam_disp_current_frame = self.gen_camera_disp_canvas(self.cam_display_fr_2, 'Live Frame', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 0) #'Current Frame'

        self.cam_disp_frame_1 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 1', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 0)
        self.tk_sq_disp_list.append(self.cam_disp_frame_1)

        self.cam_disp_frame_2 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 2', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 1)
        self.tk_sq_disp_list.append(self.cam_disp_frame_2)

        self.cam_disp_frame_3 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 3', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 2)
        self.tk_sq_disp_list.append(self.cam_disp_frame_3)

        self.cam_disp_frame_4 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 4', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 3)
        self.tk_sq_disp_list.append(self.cam_disp_frame_4)

        self.cam_disp_frame_5 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 5', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 4)
        self.tk_sq_disp_list.append(self.cam_disp_frame_5)

        self.cam_disp_frame_6 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 6', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 5)
        self.tk_sq_disp_list.append(self.cam_disp_frame_6)

        self.cam_disp_frame_7 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 7', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 6)
        self.tk_sq_disp_list.append(self.cam_disp_frame_7)

        self.cam_disp_frame_8 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 8', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 7)
        self.tk_sq_disp_list.append(self.cam_disp_frame_8)
        
        self.cam_disp_frame_9 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 9', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 8)
        self.tk_sq_disp_list.append(self.cam_disp_frame_9)

        self.cam_disp_frame_10 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 10', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 9)
        self.tk_sq_disp_list.append(self.cam_disp_frame_10)

        self.cam_disp_frame_11 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 11', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 10)
        self.tk_sq_disp_list.append(self.cam_disp_frame_11)

        self.cam_disp_frame_12 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 12', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 11)
        self.tk_sq_disp_list.append(self.cam_disp_frame_12)

        self.cam_disp_frame_13 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 13', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 12)
        self.tk_sq_disp_list.append(self.cam_disp_frame_13)

        self.cam_disp_frame_14 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 14', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 13)
        self.tk_sq_disp_list.append(self.cam_disp_frame_14)

        self.cam_disp_frame_15 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 15', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 14)
        self.tk_sq_disp_list.append(self.cam_disp_frame_15)

        self.cam_disp_frame_16 = self.gen_camera_disp_canvas(self.SQ_frame_scroll_display.window_fr, 'Frame 16', 'snow3', 'black',
            self.cam_display_width, self.cam_display_height, 'snow3', 15)
        self.tk_sq_disp_list.append(self.cam_disp_frame_16)

    def SQ_fr_popout_gen(self, toplvl_W, toplvl_H, toplvl_title):
        try:
            #raise AttributeError('AttributeError supposed to handle.')
            check_bool = tk.Toplevel.winfo_exists(self.SQ_fr_popout_toplvl)
            
            if check_bool == 0:
                self.SQ_fr_popout_toplvl = tk.Toplevel(self.main_frame, width = toplvl_W, height = toplvl_H)

                self.SQ_fr_popout_toplvl['bg'] = 'white'
                self.SQ_fr_popout_toplvl.title(toplvl_title)
                screen_width = self.SQ_fr_popout_toplvl.winfo_screenwidth()
                screen_height = self.SQ_fr_popout_toplvl.winfo_screenheight()
                x_coordinate = int((screen_width/2) - (toplvl_W/2))
                y_coordinate = int((screen_height/2) - (toplvl_H/2))
                self.SQ_fr_popout_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
                self.SQ_fr_popout_toplvl.protocol("WM_DELETE_WINDOW", self.SQ_fr_popout_close)

                try:
                    self.SQ_fr_popout_toplvl.iconphoto(False, self.window_icon)
                except Exception:
                    pass

                self.SQ_fr_popout_init()

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
                #print('exist')
                self.SQ_fr_popout_toplvl.deiconify()
                self.SQ_fr_popout_toplvl.lift()
                pass

        except (AttributeError, tk.TclError):
            #print('AttributeError caught')
            self.SQ_fr_popout_toplvl = tk.Toplevel(self.main_frame, width = toplvl_W, height = toplvl_H)

            self.SQ_fr_popout_toplvl['bg'] = 'white'
            self.SQ_fr_popout_toplvl.title(toplvl_title)
            screen_width = self.SQ_fr_popout_toplvl.winfo_screenwidth()
            screen_height = self.SQ_fr_popout_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (toplvl_W/2))
            y_coordinate = int((screen_height/2) - (toplvl_H/2))
            self.SQ_fr_popout_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
            self.SQ_fr_popout_toplvl.protocol("WM_DELETE_WINDOW", self.SQ_fr_popout_close)

            try:
                self.SQ_fr_popout_toplvl.iconphoto(False, self.window_icon)
            except Exception:
                pass

            self.SQ_fr_popout_init()

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
                    
    def SQ_fr_popout_close(self):
        try:
            self.SQ_fr_popout_toplvl.destroy()
        except (AttributeError, tk.TclError):
            pass

    def SQ_popout_fit_to_display_func(self):
        try:
            self.SQ_fr_popout_disp.fit_to_display(self.SQ_fr_popout_toplvl.winfo_width(),self.SQ_fr_popout_toplvl.winfo_height()-30)
        except (AttributeError, tk.TclError):
            pass

    def SQ_fr_popout_init(self):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.SQ_fr_popout_toplvl)
            if check_bool == 0:
                pass
            else:
                tk.Label(self.SQ_fr_popout_toplvl, text = 'Frame No. Display:', font = 'Helvetica 10', bg = 'white').place(x=5, y=0)
                self.SQ_fr_popout_toplvl.option_add('*TCombobox*Listbox.font', ('Helvetica', '10'))
                self.SQ_fr_sel = ttk.Combobox(self.SQ_fr_popout_toplvl, width=15, state='readonly', font = 'Helvetica 10')
                self.SQ_fr_sel.unbind_class("TCombobox", "<MouseWheel>")
                self.SQ_fr_sel.place(x=130, y=0)

                self.SQ_curr_disp_fr = 0

                self.SQ_fr_popout_disp = CanvasImage(self.SQ_fr_popout_toplvl)
                self.SQ_fr_popout_disp.place(x=0, y=30, relwidth = 1, relheight = 1, anchor = 'nw')
                self.SQ_fr_popout_toplvl.deiconify()
                self.SQ_fr_popout_toplvl.lift()
        except (AttributeError, tk.TclError): #as e:
            pass

    def SQ_fr_popout_load_list(self, sq_frame_img_list = None):
        try:
            #Check if popout toplvl exists
            check_bool = tk.Toplevel.winfo_exists(self.SQ_fr_popout_toplvl)
            if check_bool == 0:
                pass
            else:
                #GUI functions
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

        except (AttributeError, tk.TclError): #as e:
            #print(e)
            pass

    def SQ_fr_popout_disp_func(self, event=None, sq_frame_img_list = None):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.SQ_fr_popout_toplvl)
            if check_bool == 0:
                pass
            else:
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


        except (AttributeError, tk.TclError):
            # print(e)
            # print('Specified Error Caught')
            pass

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

    def camera_control_GUI(self):
        bg_color = 'SteelBlue1' #'DarkSlateGray2'
        cam_ctrl_fr_H = 0

        self.cam_ctrl_frame = tk.Frame(self.main_frame, bg = bg_color, highlightbackground = 'navy', highlightthickness=1)
        self.cam_ctrl_frame['width'] = 312
        self.cam_ctrl_frame.place(x = 615, y =0)

        self.cam_frame_1 = tk.Frame(self.cam_ctrl_frame, highlightthickness=0)#, bg= 'cyan')
        self.cam_frame_1['width'] = 300
        self.cam_frame_1['height'] = 150
        #self.cam_frame_1: Frame_1 is the Main Camera Controls
        self.cam_frame_1.place(x = 5, y = cam_ctrl_fr_H + 5)
        self.cam_frame_1.update_idletasks()

        cam_ctrl_fr_H = cam_ctrl_fr_H + 5 + self.cam_frame_1.winfo_height()

        self.cam_frame_2 = tk.Frame(self.cam_ctrl_frame, highlightthickness=0)#, bg= 'orange')
        self.cam_frame_2['width'] = 300
        self.cam_frame_2['height'] = 90
        #self.cam_frame_2: Frame_2 is the Save Camera Controls
        self.cam_frame_2.place(x = 5, y = cam_ctrl_fr_H + 5)
        self.cam_frame_2.update_idletasks()

        cam_ctrl_fr_H = cam_ctrl_fr_H + 5 + self.cam_frame_2.winfo_height()

        self.cam_frame_3 = tk.Frame(self.cam_ctrl_frame, highlightthickness=0)#, bg= 'green')
        self.cam_frame_3['width'] = 300
        self.cam_frame_3['height'] = 348 + 100 + 70
        #self.cam_frame_3: Frame_3 is the Exposure etc Camera Controls
        self.cam_frame_3.place(x = 5, y = cam_ctrl_fr_H + 5)
        self.cam_frame_3.update_idletasks()

        cam_ctrl_fr_H = cam_ctrl_fr_H + 5 + self.cam_frame_3.winfo_height()

        self.cam_ctrl_frame['height'] = cam_ctrl_fr_H + 10

        self.cam_mode_var = tk.StringVar(value = self.cam_mode_str)
        
        tk.Label(self.cam_frame_1, text = 'Trigger Source: ', font = 'Helvetica 10').place(x = 5 , y = 100)

        self.triggercheck_val = tk.IntVar()
        self.checkbtn_trigger_src = tk.Checkbutton(self.cam_frame_1, text='Internal Trigger', variable = self.triggercheck_val, onvalue=1, offvalue=0, highlightthickness = 0)
        self.checkbtn_trigger_src['command'] = self.trigger_src_func
        self.widget_bind_focus(self.checkbtn_trigger_src)
        self.checkbtn_trigger_src.place(x=5 ,y=90+33)
        self.checkbtn_trigger_src['state'] = 'disable'

        # self.trigger_src_list = ['LINE0', 'LINE1', 'LINE2', 'LINE3', 'COUNTER0', 'SOFTWARE']
        # self.cam_frame_1.option_add('*TCombobox*Listbox.font', ('Helvetica', '10'))
        # self.trigger_src_select = ttk.Combobox(self.cam_frame_1, values=self.trigger_src_list, width=15, state='readonly', font = 'Helvetica 10')
        # self.trigger_src_select.unbind_class("TCombobox", "<MouseWheel>")
        # self.trigger_src_select.bind('<<ComboboxSelected>>', self.trigger_src_func)
        # self.trigger_src_select.current(0)
        # self.trigger_src_select.place(x=5, y=90+33)

        tk.Label(self.cam_frame_1, text = 'Main Controls: ', font = 'Helvetica 11 bold').place(x=0, y=0)
        self.radio_continuous = tk.Radiobutton(self.cam_frame_1, text='Continuous',variable = self.cam_mode_var, value='continuous',width=15, height=1)
        self.radio_continuous['command'] = self.set_triggermode
        self.widget_bind_focus(self.radio_continuous)
        self.radio_continuous.place(x=5 + 15,y=5 + 25)

        self.radio_trigger = tk.Radiobutton(self.cam_frame_1, text='Trigger Mode',variable = self.cam_mode_var, value='triggermode',width=15, height=1)
        self.radio_trigger['command'] = self.set_triggermode
        self.widget_bind_focus(self.radio_trigger)
        self.radio_trigger.place(x=145 + 15,y=5 +25)


        self.btn_grab_frame = tk.Button(self.cam_frame_1, text='START', width=6, height=1, relief = tk.GROOVE,
            activebackground = 'forest green', bg = 'green3', activeforeground = 'white', fg = 'white', font = 'Helvetica 12 bold')
        self.grab_btn_init_state(self.btn_grab_frame, self.start_grabbing)
        self.widget_bind_focus(self.btn_grab_frame)
        self.btn_grab_frame.place(x=35 + 15, y=40+25)

        # self.capture_img_status = tk.IntVar()
        self.capture_img_checkbtn = tk.Checkbutton(self.cam_frame_1, text='Capture Image', variable = self.capture_img_status, onvalue=1, offvalue=0)
        self.capture_img_checkbtn.place(x=176,y=40+25)

        self.btn_trigger_once = tk.Button(self.cam_frame_1, text='Trigger Once', width=15, height=1, relief = tk.GROOVE)
        self.btn_trigger_once['command'] = self.trigger_once
        self.widget_bind_focus(self.btn_trigger_once)
        self.btn_trigger_once['state'] = 'disable'
        self.btn_trigger_once.place(x=150 + 15, y=90+30)
        ###############################################################################################################################
        
        tk.Label(self.cam_frame_2, text = 'Save Images: ', font = 'Helvetica 11 bold').place(x=0, y=0)

        self.btn_save_sq = tk.Button(self.cam_frame_2, text='Save SQ Frame', width=15, height=1, relief = tk.GROOVE)
        # self.btn_save_sq['command'] = self.sq_frame_save
        self.widget_bind_focus(self.btn_save_sq)

        self.btn_save_img = tk.Button(self.cam_frame_2, text='Save Image', width=15, height=1, relief = tk.GROOVE)
        self.btn_save_img['command'] = self.img_save_func
        self.widget_bind_focus(self.btn_save_img)
        self.btn_save_img.place(x=20, y=30)

        self.label_save_img_format = tk.Label(self.cam_frame_2, text = 'Image Format: ', font = 'Helvetica 10')
        self.save_img_format_list = ['.bmp', '.png', '.jpg', '.tiff', '.pdf']
        self.cam_frame_2.option_add('*TCombobox*Listbox.font', ('Helvetica', '10'))
        self.save_img_format_sel = ttk.Combobox(self.cam_frame_2, values=self.save_img_format_list, width=5, state='readonly', font = 'Helvetica 10')
        self.save_img_format_sel.unbind_class("TCombobox", "<MouseWheel>")
        self.save_img_format_sel.current(0)
        self.label_save_img_format.place(x=160,  y=5)
        self.save_img_format_sel.place(x=160, y=30)

        self.trigger_auto_save_bool = tk.IntVar(value = 0)
        self.trigger_auto_save_checkbtn = tk.Checkbutton(self.cam_frame_2, text='Trigger Mode Auto Save', variable = self.trigger_auto_save_bool, onvalue=1, offvalue=0)
        self.trigger_auto_save_checkbtn['command'] = self.set_trigger_autosave

        self.SQ_auto_save_bool = tk.IntVar(value = 0)
        self.SQ_auto_save_checkbtn = tk.Checkbutton(self.cam_frame_2, text='SQ Frame(s) Auto Save', variable = self.SQ_auto_save_bool, onvalue=1, offvalue=0)
        # self.SQ_auto_save_checkbtn['command'] = self.set_SQ_autosave

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
        self.entry_framerate['vcmd']=(self.entry_framerate.register(validate_float_entry),'%d', '%P', '%S', 6)
        self.entry_framerate.bind('<Return>', self.set_parameter_framerate)
        self.entry_framerate.bind('<Tab>', self.set_parameter_framerate)
        self.entry_framerate.bind('<FocusOut>', self.set_parameter_framerate)
        self.entry_framerate['command'] = self.set_parameter_framerate

        label_framerate_enable = tk.Label(self.cam_frame_3, text = 'Frame Rate Enable', anchor = 'e')
        self.btn_enable_framerate = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_enable_framerate['command'] = self.enable_framerate
        self.widget_bind_focus(self.btn_enable_framerate)
        
        label_framerate.place(x=35+ shift_x, y=60 + 30)
        info_framerate.place(x=0+ shift_x, y=60 + 30)
        label_framerate_enable.place(x=23+ shift_x, y= 35 + 30)
        self.entry_framerate.place(x=130+ shift_x, y=60 + 30)
        self.btn_enable_framerate.place(x=130 + shift_x, y =30 +30)

        ###############################################################################################################################
        label_exposure = tk.Label(self.cam_frame_3, text='Exposure Time', width=12, anchor = 'e')
        info_exposure = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_exposure, 'Exposure: \n' + 'Specify how long the image sensor\nis exposed to the light during image\n'+ \
            'acquisition.' +'\n\n'+ 'Min: 0\nMax: 66,821.75'
            , -220, -40, width = 220, height = 120)
        self.exposure_str = tk.StringVar()
        #self.entry_exposure = tk.Entry(self.cam_frame_3, textvariable = self.exposure_str, highlightbackground="black", highlightthickness=1, width = 9)
        self.entry_exposure = tk.Spinbox(self.cam_frame_3, textvariable = self.exposure_str, highlightbackground="black", highlightthickness=1, width = 7, from_=0, to =1000000, increment= 1000)
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

        label_exposure.place(x=35+ shift_x, y= 60 + 55 + 30)
        info_exposure.place(x=0+ shift_x, y= 60 + 55 + 30)
        label_auto_exposure.place(x=35+ shift_x, y= 35 + 55 + 30)
        self.entry_exposure.place(x=130+ shift_x, y=60 + 55 + 30)
        self.btn_auto_exposure.place(x=130+ shift_x, y=30 + 55 + 30)

        ###############################################################################################################################
        label_gain = tk.Label(self.cam_frame_3, text='Gain', width=12, anchor = 'e')
        info_gain = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_gain, 'Gain: \n' + 'Set an amplification factor applied to\nthe video signal so as to increase\n'+ \
            'the brightness of the image output\n'+ 'by the camera.' +'\n\n'+ 'Min: 14\nMax: 63'
            , -220, -40, width = 220, height = 140)

        self.gain_str = tk.StringVar()
        # self.entry_gain = tk.Entry(self.cam_frame_3, textvariable = self.gain_str, highlightbackground="black", highlightthickness=1, width = 9)
        self.entry_gain = tk.Spinbox(self.cam_frame_3, textvariable = self.gain_str, highlightbackground="black", highlightthickness=1, width = 7, from_=14, to =63)
        self.gain_str.set(self.cam_param_gain[0])
        int_validate_register(self.entry_gain, positive_bool = True)

        # self.entry_gain['validate']='key'
        # self.entry_gain['vcmd']=(self.entry_gain.register(validate_float_entry), '%d', '%P', '%S', 4)

        self.entry_gain.bind('<Return>', self.set_parameter_gain)
        self.entry_gain.bind('<Tab>', self.set_parameter_gain)
        self.entry_gain.bind('<FocusOut>', self.set_parameter_gain)
        self.entry_gain['command'] = self.set_parameter_gain

        label_auto_gain = tk.Label(self.cam_frame_3, text = 'Auto Gain', width = 12, anchor = 'e')
        self.btn_auto_gain = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_auto_gain['command'] = self.set_auto_gain
        self.widget_bind_focus(self.btn_auto_gain)

        label_gain.place(x=35+ shift_x, y=60 + 110 + 30)
        info_gain.place(x=0+ shift_x, y=60 + 110 + 30)
        label_auto_gain.place(x=35+ shift_x, y= 35 + 110 + 30)
        self.entry_gain.place(x=130+ shift_x, y=60 + 110 + 30)
        self.btn_auto_gain.place(x=130 + shift_x, y =30 + 110 + 30)

        ###############################################################################################################################
        label_auto_white = tk.Label(self.cam_frame_3, text = 'Auto White Balance', anchor = 'e')

        self.btn_auto_white = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_auto_white['command'] = self.set_auto_white
        self.widget_bind_focus(self.btn_auto_white)

        self.win_balance_ratio = tk.Frame(self.cam_frame_3, width = 165, height = 70+2)#, bg = 'grey')
        label_balance_ratio = tk.Label(self.win_balance_ratio, text = 'Balance Ratio', anchor = 'e')

        info_balance_ratio = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_balance_ratio, 'Balance Ratio: \n' + 'Gamma correction of pixel intensity,\nwhich helps optimizing the brightness\n'+ \
            'of acquired images for displaying\n'+ 'on a monitor.' +'\n\n'+ 'Min: 1\nMax: 8191'
            , -220, -40, width = 220, height = 140)

        red_tag = tk.Frame(self.win_balance_ratio, width = 20, height = 20, bg = 'red')
        green_tag = tk.Frame(self.win_balance_ratio, width = 20, height = 20, bg = 'green')
        blue_tag = tk.Frame(self.win_balance_ratio, width = 20, height = 20, bg = 'blue')

        self.red_ratio_str = tk.StringVar()
        self.green_ratio_str = tk.StringVar()
        self.blue_ratio_str = tk.StringVar()
        self.entry_red_ratio = tk.Spinbox(self.win_balance_ratio, textvariable = self.red_ratio_str, highlightbackground="black", highlightthickness=1, width = 7, from_=1, to= 4095)
        self.entry_red_ratio.bind('<Return>', self.set_parameter_red_ratio)
        self.entry_red_ratio.bind('<Tab>', self.set_parameter_red_ratio)
        self.entry_red_ratio.bind('<FocusOut>', self.set_parameter_red_ratio)
        self.entry_red_ratio['command'] = self.set_parameter_red_ratio

        self.entry_green_ratio = tk.Spinbox(self.win_balance_ratio, textvariable = self.green_ratio_str, highlightbackground="black", highlightthickness=1, width = 7, from_=1, to= 4095)
        self.entry_green_ratio.bind('<Return>', self.set_parameter_green_ratio)
        self.entry_green_ratio.bind('<Tab>', self.set_parameter_green_ratio)
        self.entry_green_ratio.bind('<FocusOut>', self.set_parameter_green_ratio)
        self.entry_green_ratio['command'] = self.set_parameter_green_ratio

        self.entry_blue_ratio = tk.Spinbox(self.win_balance_ratio, textvariable = self.blue_ratio_str, highlightbackground="black", highlightthickness=1, width = 7, from_=1, to= 4095)
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

        label_balance_ratio.place(x=0, y= 25)
        red_tag.place(x=80,y=0)
        green_tag.place(x=80,y=25)
        blue_tag.place(x=80,y=50)

        self.entry_red_ratio.place(x=105, y=0)
        self.entry_green_ratio.place(x=105, y=25)
        self.entry_blue_ratio.place(x=105, y=50)

        label_auto_white.place(x=15 +shift_x, y=35 + 193 + 30 - 25) # 165 + 55/2 = 165 + 28 = 193
        self.btn_auto_white.place(x=130 + shift_x, y =30 + 193 + 30 - 25)
        info_balance_ratio.place(x=0+ shift_x, y = 85 + 193 + 30 - 25)
        self.win_balance_ratio.place(x=25 +shift_x, y= 60 + 193 + 30 - 25) #165 + 55
        
        ###############################################################################################################################
        label_black_lvl = tk.Label(self.cam_frame_3, text='Black Level', width=12, anchor = 'e')
        info_black_lvl = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_black_lvl, 'Black Level: \n' + 'Analog black level in percent.\n\n'+ 'Min: 0\nMax: 255'
            , -180, -20, width = 180, height = 90)

        self.black_lvl_str = tk.StringVar()
        self.entry_black_lvl = tk.Spinbox(self.cam_frame_3, textvariable = self.black_lvl_str, highlightbackground="black", highlightthickness=1, width = 7, from_=0, to =255)
        self.black_lvl_str.set(self.cam_param_int[4])
        
        int_validate_register(self.entry_black_lvl, positive_bool = True)

        self.entry_black_lvl.bind('<Return>', self.set_parameter_black_lvl)
        self.entry_black_lvl.bind('<Tab>', self.set_parameter_black_lvl)
        self.entry_black_lvl.bind('<FocusOut>', self.set_parameter_black_lvl)
        self.entry_black_lvl['command'] = self.set_parameter_black_lvl

        label_black_lvl_enable = tk.Label(self.cam_frame_3, text = 'Black Level Enable', anchor = 'e')
        self.btn_enable_black_lvl = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_enable_black_lvl['command'] = self.enable_black_lvl
        self.widget_bind_focus(self.btn_enable_black_lvl)

        label_black_lvl.place(x=35+ shift_x, y=60 + 303 + 30 - 25) #193 + 55 + 55 = 303
        info_black_lvl.place(x = 0+ shift_x, y=60 + 303 + 30 - 25)
        label_black_lvl_enable.place(x=23+ shift_x, y= 35 + 303 + 30 - 25)
        self.entry_black_lvl.place(x=130+ shift_x, y=60 + 303 + 30 - 25)
        self.btn_enable_black_lvl.place(x=130 + shift_x, y =30 + 303 + 30 - 25)

        ###############################################################################################################################

        self.btn_get_parameter = tk.Button(self.cam_frame_3, text='Read Parameter', width=15, height=1, relief = tk.GROOVE)
        self.btn_get_parameter['command'] = self.get_parameter
        self.widget_bind_focus(self.btn_get_parameter)
        self.btn_get_parameter.place(x=20, y=35 + 418 + 30)

        self.btn_set_parameter = tk.Button(self.cam_frame_3, text='Set Parameter', width=15, height=1, relief = tk.GROOVE)
        self.btn_set_parameter['command'] = self.set_parameter
        self.widget_bind_focus(self.btn_set_parameter)
        self.btn_set_parameter.place(x=160, y=35 + 418 + 30)
        ###############################################################################################################################

        label_pixel_format = tk.Label(self.cam_frame_3, text = 'Pixel Format', width=12, anchor = 'e')
        info_pixel_format = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_pixel_format, 'Pixel Format: \n' + 'Format of the pixel data.'
            , -150, 0, width = 150, height = 40)

        # self.pixel_format_list = ["Mono 8", "Mono 10", "Mono 10 Packed", "Mono 12", "Mono 12 Packed", "Mono 14"
        # , "RGB 8 Packed", "YUV 422 Packed", "Bayer RG 8", "Bayer RG 10", "Bayer RG 10 Packed", "Bayer RG 12", "Bayer RG 12 Packed"]
        self.pixel_format_list = ["Mono 8", "Mono 10", "Mono 12"
        , "RGB 8 Packed"]
        self.cam_frame_3.option_add('*TCombobox*Listbox.font', ('Helvetica', '10'))
        self.pixel_format_combobox = ttk.Combobox(self.cam_frame_3, width=15, state='readonly', font = 'Helvetica 10')
        self.pixel_format_combobox['values'] = self.pixel_format_list
        self.pixel_format_combobox.unbind_class("TCombobox", "<MouseWheel>")
        self.pixel_format_combobox.bind('<<ComboboxSelected>>', self.pixel_format_sel)

        label_pixel_format.place(x=35 + shift_x, y =30)
        info_pixel_format.place(x=0+ shift_x, y = 30)
        self.pixel_format_combobox.place(x=130 + shift_x, y= 30)
    
    def grab_btn_state(self, btn, func = None):
        if btn['text'] == 'START':
            btn['text'] = 'STOP'
            btn['activebackground'] = 'red3'
            btn['bg'] = 'red'
            btn['activeforeground'] = 'white'
            btn['fg'] = 'white'
            try:
                btn['command'] = func
            except Exception: #as e:
                # print('Error for grab_btn_state: ', e)
                pass

        elif btn['text'] == 'STOP':
            btn['text'] = 'START'
            btn['activebackground'] = 'forest green'
            btn['bg'] = 'green3'
            btn['activeforeground'] = 'white'
            btn['fg'] = 'white'
            try:
                btn['command'] = func
            except Exception: #as e:
                # print('Error for grab_btn_state: ', e)
                pass

    def grab_btn_init_state(self, btn, func = None):
        btn['text'] = 'START'
        btn['activebackground'] = 'forest green'
        btn['bg'] = 'green3'
        btn['activeforeground'] = 'white'
        btn['fg'] = 'white'
        try:
            btn['command'] = func
        except Exception: #as e:
            # print('Error for grab_btn_state: ', e)
            pass

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
            widget_disable(self.btn_save_sq)

            widget_disable(self.btn_normal_cam_mode, self.btn_SQ_cam_mode)
            #self.trigger_src_select['state'] = 'disable'
            
            self.btn_trigger_once['state'] = 'disable'
            self.checkbtn_trigger_src['state'] = 'disable'
            self.pixel_format_combobox['state'] = 'disable'

            self.trigger_auto_save_checkbtn['state'] = 'disable'

            self.SQ_auto_save_checkbtn['state'] = 'disable'

            self.btn_save_img['state'] = 'disable'
            self.save_img_format_sel['state'] = 'disable'

            self.record_btn_1['state'] = 'disable'

            self.triggercheck_val.set(0)
            self.cam_mode_str = 'continuous'
            self.cam_mode_var.set(self.cam_mode_str)
            self.capture_img_status.set(0)
            self.trigger_auto_save_bool.set(0)
            self.SQ_auto_save_bool.set(0)

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

            widget_enable(self.btn_normal_cam_mode, self.btn_SQ_cam_mode)

            self.pixel_format_combobox['state'] = 'readonly'

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

    def camera_toggle_button_state(self, auto_toggle_status, auto_button, img_button_ON, img_button_OFF, 
        entry_box, toggle_type = None):
        # print(auto_toggle_status, toggle_type)
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

    def camera_no_display_func(self):
        self.dummy_canvas_rgb.create_image(self.cam_display_width/2, self.cam_display_height/2, image=self.cam_disconnect_img, anchor='center', tags='img')
        self.dummy_canvas_rgb.image = self.cam_disconnect_img

        self.dummy_canvas_R.create_image(self.cam_display_width/2, self.cam_display_height/2, image=self.cam_disconnect_img, anchor='center', tags='img')
        self.dummy_canvas_R.image = self.cam_disconnect_img

        self.dummy_canvas_G.create_image(self.cam_display_width/2, self.cam_display_height/2, image=self.cam_disconnect_img, anchor='center', tags='img')
        self.dummy_canvas_G.image = self.cam_disconnect_img

        self.dummy_canvas_B.create_image(self.cam_display_width/2, self.cam_display_height/2, image=self.cam_disconnect_img, anchor='center', tags='img')
        self.dummy_canvas_B.image = self.cam_disconnect_img

    ###############################################################################################
    #4. CREVIS FUNCTION
    def open_device(self, crevis_serial_list, nSelCamIndex):
        if len(crevis_serial_list) > 0:
            #self.CAM_stop_checkforUpdates(self.main_frame)
            init_check = c_bool()
            self.crevis_pylib.ST_IsInitSystem(init_check)
            print('init_check: ', init_check.value)
            # if init_check.value == False:
            #     #print('init_check: ', init_check.value)
            #     print('crevis_init')
            #     self.crevis_pylib.ST_InitSystem()

            # ret = self.crevis_pylib.ST_OpenDevice(int(nSelCamIndex), False)
            # print(ret)
            #self.crevis_pylib.ST_InitSystem()
            #print(nSelCamIndex)
            #self.crevis_operation.nSelCamIndex = int(nSelCamIndex)
            pSize = c_uint32(256)
            pInfo = (c_ubyte * 16)()
            self.crevis_pylib.ST_GetEnumDeviceInfo(int(nSelCamIndex), 10002, pInfo, pSize)
            serial_check = (bytes(pInfo).decode("utf-8")).strip().strip('\x00')
            # print(serial_check)
            # print(crevis_serial_list)
            if serial_check == crevis_serial_list[int(nSelCamIndex)]:
                ret = self.crevis_operation.Open_device(nSelCamIndex)
                # print('ret_crevis_open: ', ret)
                if ret != 0:
                    self.cam_conn_status = False
                    #self.CAM_device_checkForUpdates(self.main_frame)
                    tkinter.messagebox.showerror('Error','Connection Failed.\nIf device is connected and connection still failed,\n' + 
                        'please click "REFRESH" button to update device list.\n\n' + 
                        'Otherwise, report the error number: ' + str(ret))
                else:
                    self.cam_connect_class.cam_connection_toplvl.destroy()
                    self.cam_conn_status = True

                    self.cam_mode_str = 'continuous'
                    self.cam_mode_var.set(self.cam_mode_str)
                    self.trigger_src_func()
                    self.get_parameter_exposure()
                    self.get_parameter_framerate()
                    self.get_parameter_gain()
                    # self.get_parameter_white()
                    self.get_parameter_black_lvl()

                    self.crevis_operation.Normal_Mode_display_clear()
                    self.crevis_operation.SQ_Mode_display_clear()
            else:
                self.cam_conn_status = False
                tkinter.messagebox.showerror('Error','Connection Failed.\nCamera Serial Number Mismatch.\n' + 
                    'Please click "REFRESH" button to update device list.\n\n' + 
                    'Otherwise, report the error number: ' + str(ret))
        else:
            print('No camera device to connect')

    # ch:开始取流 | en:Start grab image
    def start_grabbing(self):
        ret = self.crevis_operation.Start_grab()
        #print('crevis_start_grab: ', ret)
        if ret == 0:
            self.cam_display_place_GUI_1()

            self.cam_disp_current_frame.place(x = 0, y = 0+25)
            # self.crevis_operation.Start_grab()
            self.grab_btn_state(self.btn_grab_frame, self.stop_grabbing)
            self.pixel_format_combobox['state'] = 'disable'

    # ch:停止取流 | en:Stop grab image
    def stop_grabbing(self):
        ret = self.crevis_operation.Stop_grab()
        #print('crevis_stop_grab: ', ret)
        if ret == 0:
            self.cam_display_forget_GUI_1()

            self.cam_disp_current_frame.place_forget()
            self.cam_popout_close()
            self.grab_btn_state(self.btn_grab_frame, self.start_grabbing)
            self.pixel_format_combobox['state'] = 'readonly'

    # ch:关闭设备 | Close device   
    def close_device(self):
        try:
            self.crevis_operation.Stop_grabbing()
        except AttributeError:
            pass
        
        self.btn_normal_cam_mode.invoke()

        self.cam_display_forget_GUI_1()

        self.cam_disp_current_frame.place_forget()

        self.clear_display_GUI_2()
        
        self.cam_popout_close()

        try:
            self.popout_save_btn['state'] = 'disable'
        except Exception:
            pass

        try:
            self.SQ_fr_popout_toplvl.destroy()
        except AttributeError:
            pass

        del self.cam_sq_frame_cache
        self.cam_sq_frame_cache = None
        ##############################################################################

        self.cam_conn_status = False
        self.crevis_operation.Close_device()
        
        self.grab_btn_init_state(self.btn_grab_frame, self.start_grabbing)

        self.crevis_pylib.ST_FreeSystem()

        self.stop_auto_toggle_parameter()


    def cam_quit_func(self):
        try:
            self.crevis_operation.Stop_grabbing()
        except AttributeError:
            pass

        try:
            self.crevis_operation.Close_device()
        except AttributeError:
            pass

    #ch:设置触发模式 | en:set trigger mode
    def set_triggermode(self):
        status = self.crevis_operation.Set_mode(self.cam_mode_var.get())
        if status == 0:
            if self.cam_mode_var.get() == 'continuous':
                if self.cam_mode_str != self.cam_mode_var.get():
                    self.cam_mode_str = self.cam_mode_var.get()
                    self.btn_save_img['state'] = 'normal'
                    self.capture_img_checkbtn['state'] = 'normal'
                    self.checkbtn_trigger_src['state'] = 'disable'
                    self.btn_trigger_once['state'] = 'disable'

                    self.trigger_auto_save_checkbtn['state'] = 'disable'

                    self.SQ_auto_save_checkbtn['state'] = 'disable'

                    self.trigger_auto_save_bool.set(0)
                    self.SQ_auto_save_bool.set(0)

                    self.record_btn_1['state'] = 'normal'


            elif self.cam_mode_var.get() == 'triggermode':
                #print('triggermode')
                if self.cam_mode_str != self.cam_mode_var.get():
                    try:
                        self.crevis_operation.sq_frame_save_list *= 0
                    except Exception:
                        pass

                    ### UPDATE 18-8-2021
                    try:
                        self.crevis_operation.ext_sq_fr_init = False
                    except Exception:
                        pass

                    self.cam_sq_frame_cache = None

                    self.cam_mode_str = self.cam_mode_var.get()
                    self.crevis_operation.b_save = False
                    self.btn_save_img['state'] = 'disable'

                    self.capture_img_checkbtn['state'] = 'disable'
                    self.capture_img_status.set(0)
                    
                    self.checkbtn_trigger_src['state'] = 'normal'
                    self.trigger_src_func()
                    ####################################################

                    self.trigger_auto_save_checkbtn['state'] = 'normal'

                    self.SQ_auto_save_checkbtn['state'] = 'normal'

                    self.record_btn_1['state'] = 'disable'

                    self.clear_display_GUI_2()
                    #print('Frame Display Cleared...')
                    if self.record_bool == True:
                        self.record_stop_func()


        else:
            self.cam_mode_var.set(self.cam_mode_str)


    def set_trigger_autosave(self):
        #print(self.trigger_auto_save_bool.get(), self.SQ_auto_save_bool.get())
        if self.trigger_auto_save_bool.get() == 1 and self.SQ_auto_save_bool.get() == 1:
            self.SQ_auto_save_bool.set(0)
        else:
            pass

    def set_SQ_autosave(self):
        #print(self.trigger_auto_save_bool.get(), self.SQ_auto_save_bool.get())
        if self.trigger_auto_save_bool.get() == 1 and self.SQ_auto_save_bool.get() == 1:
            self.trigger_auto_save_bool.set(0)
        else:
            pass

    def trigger_src_func(self, event = None):
        if self.triggercheck_val.get() == 0:
            strSrc = 'LINE1'
            self.btn_trigger_once['state'] = 'disable'

        elif self.triggercheck_val.get() == 1:
            strSrc = 'SOFTWARE'
            self.btn_trigger_once['state'] = 'normal'

        status = self.crevis_operation.Trigger_Source(strSrc)
        # print('crevis set trigger src: ', status)
        if status != 0:
            if self.triggercheck_val.get() == 0:
                self.triggercheck_val.set(1)
                self.btn_trigger_once['state'] = 'normal'

            elif self.triggercheck_val.get() == 1:
                self.triggercheck_val.set(0)
                self.btn_trigger_once['state'] = 'disable'
        else:
            pass

    #ch:设置触发命令 | en:set trigger software
    def trigger_once(self):
        self.crevis_operation.Trigger_once()

    def sq_camera_frame(self, sq_frame_limit = 1, sq_frame_width = 0):
        try:
            self.crevis_operation.SQ_Camera_Frame(sq_frame_limit, sq_frame_width)
        except AttributeError:
            pass

    def sq_frame_save(self):
        self.crevis_operation.Save_SQ_Frame()

    def img_save_func(self):
        self.crevis_operation.b_save = True

    def get_parameter(self,event=None):
        self.crevis_operation.Get_parameter_framerate()
        self.crevis_operation.Get_parameter_exposure()
        self.crevis_operation.Get_parameter_gain()
        # self.crevis_operation.Get_parameter_white()
        self.crevis_operation.Get_parameter_black_lvl()

        self.cam_param_float[0] = self.crevis_operation.exposure_time
        self.cam_param_gain[0] = self.crevis_operation.gain
        self.cam_param_float[2] = self.crevis_operation.frame_rate

        # self.cam_param_int[1] = self.crevis_operation.red_ratio
        # self.cam_param_int[2] = self.crevis_operation.green_ratio
        # self.cam_param_int[3] = self.crevis_operation.blue_ratio
        self.cam_param_int[4] = self.crevis_operation.black_lvl

        self.exposure_str.set(self.cam_param_float[0])
        self.gain_str.set(self.cam_param_gain[0])
        self.framerate_str.set(self.cam_param_float[2])


        # self.red_ratio_str.set(self.cam_param_int[1])
        # self.green_ratio_str.set(self.cam_param_int[2])
        # self.blue_ratio_str.set(self.cam_param_int[3])
        self.black_lvl_str.set(self.cam_param_int[4])

        int_validate_register(self.entry_gain, positive_bool = True)

        # int_validate(self.entry_red_ratio, limits=(1,4095))
        # int_validate(self.entry_green_ratio, limits=(1,4095))
        # int_validate(self.entry_blue_ratio, limits=(1,4095))
        int_validate_register(self.entry_black_lvl, positive_bool = True)

        
    def start_auto_toggle_parameter(self):
        self.get_parameter_exposure()
        self.get_parameter_gain()
        # self.get_parameter_white()

        # print('self.auto_exposure_toggle: ',self.auto_exposure_toggle)
        # print('self.auto_gain_toggle: ',self.auto_gain_toggle)
        # print('self.auto_white_toggle: ',self.auto_white_toggle)

    def stop_auto_toggle_parameter(self):
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
                self.crevis_operation.Get_parameter_exposure()
                self.cam_param_float[0] = self.crevis_operation.exposure_time
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
                self.crevis_operation.Get_parameter_gain()
                self.cam_param_gain[0] = self.crevis_operation.gain
            except AttributeError:
                pass
        else:
            pass
        self.gain_str.set(self.cam_param_gain[0])
        int_validate_register(self.entry_gain, positive_bool = True)

    def get_parameter_white(self,event=None):
        if self.cam_conn_status == True:
            if self.auto_white_toggle == True:
                self.auto_white_handle = self.cam_ctrl_frame.after(300, self.get_parameter_white)

            elif self.auto_white_toggle == False:
                self.stop_auto_white()
            try:
                self.crevis_operation.Get_parameter_white()
                self.cam_param_int[1] = self.crevis_operation.red_ratio
                self.cam_param_int[2] = self.crevis_operation.green_ratio
                self.cam_param_int[3] = self.crevis_operation.blue_ratio

            except Exception as e: #AttributeError:
                #print(e)
                pass
        else:
            pass
        #print(self.cam_param_int[1])
        self.red_ratio_str.set(self.cam_param_int[1])
        self.green_ratio_str.set(self.cam_param_int[2])
        self.blue_ratio_str.set(self.cam_param_int[3])
        int_validate(self.entry_red_ratio, limits=(1,4095))
        int_validate(self.entry_green_ratio, limits=(1,4095))
        int_validate(self.entry_blue_ratio, limits=(1,4095))

    def get_parameter_framerate(self,event=None):
        self.crevis_operation.Get_parameter_framerate()
        self.cam_param_float[2] = self.crevis_operation.frame_rate
        self.framerate_str.set(self.cam_param_float[2])

    def get_parameter_black_lvl(self, event=None):
        self.crevis_operation.Get_parameter_black_lvl()
        self.cam_param_int[4] = self.crevis_operation.black_lvl
        #print('self.cam_param_int[4]: ',self.cam_param_int[4])
        self.black_lvl_str.set(self.cam_param_int[4])
        int_validate(self.entry_black_lvl, limits=(0,255))

    def set_parameter(self,event=None):
        self.set_parameter_framerate()
        if self.auto_exposure_toggle == False:
            self.set_parameter_exposure()
        if self.auto_gain_toggle == False:
            self.set_parameter_gain()
        if self.auto_white_toggle == False:
            self.set_parameter_red_ratio()
            self.set_parameter_green_ratio()
            self.set_parameter_blue_ratio()
        self.set_parameter_black_lvl()


    def set_parameter_exposure(self,event=None):
        if self.cam_conn_status == True:
            # tk_float_verify(self.exposure_str, self.cam_param_float[0])
            tk_float_verify(self.entry_exposure, self.exposure_str, 0, 66821.75, self.cam_param_float[0], revert_bool = False)

            self.crevis_operation.exposure_time = float(self.entry_exposure.get())
            self.crevis_operation.Set_parameter_exposure(self.crevis_operation.exposure_time)

            if self.revert_val_exposure == False:
                #print('self.revert_val_exposure: False')
                self.cam_param_float[0] = self.crevis_operation.exposure_time

            elif self.revert_val_exposure == True:
                #print('self.revert_val_exposure: True')
                self.exposure_str.set(self.cam_param_float[0])
                # self.entry_exposure.xview_moveto('0')
                self.revert_val_exposure = False
        else:
            self.exposure_str.set(self.cam_param_float[0])
            self.revert_val_exposure = False

        self.entry_exposure.xview_moveto('0')

    def set_parameter_gain(self, event=None):
        if self.cam_conn_status == True:
            # print(event)
            int_validate_limit(self.entry_gain, self.gain_str, 14, 63, self.cam_param_gain[0])

            self.crevis_operation.gain = int(self.entry_gain.get())
            self.crevis_operation.Set_parameter_gain(self.crevis_operation.gain)

            if self.revert_val_gain == False:
                #print('self.revert_val_gain: False')
                self.cam_param_gain[0] = self.crevis_operation.gain

            elif self.revert_val_gain == True:
                #print('self.revert_val_gain: True')
                self.gain_str.set(int(self.cam_param_gain[0]))
                # self.entry_gain.xview_moveto('0')
                self.revert_val_gain = False
        else:
            self.gain_str.set(int(self.cam_param_gain[0]))
            self.revert_val_gain = False

        int_validate_register(self.entry_gain, positive_bool = True)

        self.entry_gain.xview_moveto('0')

    def set_parameter_framerate(self,event=None):
        if self.cam_conn_status == True:
            # tk_float_verify(self.framerate_str,self.cam_param_float[2])
            tk_float_verify(self.entry_framerate, self.framerate_str, 7.313889, 14.94985, self.cam_param_float[2], revert_bool = False)

            self.crevis_operation.frame_rate = float(self.entry_framerate.get())
            self.crevis_operation.Set_parameter_framerate(self.crevis_operation.frame_rate)

            if self.revert_val_framerate == False:
                #print('self.revert_val_framerate: False')
                self.cam_param_float[2] = self.crevis_operation.frame_rate

            elif self.revert_val_framerate == True:
                #print('self.revert_val_framerate: True')
                self.framerate_str.set(self.cam_param_float[2])
                # self.entry_framerate.xview_moveto('0')
                self.revert_val_framerate = False
        else:
            self.framerate_str.set(self.cam_param_float[2])
            self.revert_val_framerate = False

        self.entry_gain.xview_moveto('0')


    def set_parameter_red_ratio(self, event = None):
        if self.cam_conn_status == True:
            if self.red_ratio_str.get() == '':
                self.red_ratio_str.set(self.cam_param_int[1])
            int_validate(self.entry_red_ratio, limits=(1,4095))

            self.crevis_operation.red_ratio = int(self.entry_red_ratio.get())
            self.crevis_operation.Set_parameter_red_ratio(self.crevis_operation.red_ratio)

            if self.revert_val_red_ratio == False:
                self.cam_param_int[1] = self.crevis_operation.red_ratio
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

            self.crevis_operation.green_ratio = int(self.entry_green_ratio.get())
            self.crevis_operation.Set_parameter_green_ratio(self.crevis_operation.green_ratio)

            if self.revert_val_green_ratio == False:
                self.cam_param_int[2] = self.crevis_operation.green_ratio
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

            self.crevis_operation.blue_ratio = int(self.entry_blue_ratio.get())
            self.crevis_operation.Set_parameter_blue_ratio(self.crevis_operation.blue_ratio)

            if self.revert_val_blue_ratio == False:
                self.cam_param_int[3] = self.crevis_operation.blue_ratio
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
            
            int_validate_limit(self.entry_black_lvl, self.black_lvl_str, 0, 255, self.cam_param_int[4])

            self.crevis_operation.black_lvl = int(self.entry_black_lvl.get())
            self.crevis_operation.Set_parameter_black_lvl(self.crevis_operation.black_lvl)

            if self.revert_val_black_lvl == False:
                self.cam_param_int[4] = self.crevis_operation.black_lvl

            elif self.revert_val_black_lvl == True:
                self.black_lvl_str.set(self.cam_param_int[4])
                self.revert_val_black_lvl = False
        else:
            self.black_lvl_str.set(self.cam_param_int[4])
            self.revert_val_black_lvl = False

        int_validate_register(self.entry_black_lvl, positive_bool = True)

        self.entry_black_lvl.xview_moveto('0')

    def set_auto_exposure(self,event = None):
        self.crevis_operation.Auto_Exposure()
        self.get_parameter_exposure()

    def set_auto_gain(self,event = None):
        self.crevis_operation.Auto_Gain()
        self.get_parameter_gain()

    def set_auto_white(self, event = None):
        self.crevis_operation.Auto_White()
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
        self.crevis_operation.Enable_Framerate()

    def enable_black_lvl(self, event = None):
        self.crevis_operation.Enable_Blacklevel()

    def get_pixel_format(self, pixel_format_str):
        # self.pixel_format_list: ["Mono 8", "Mono 10", "Mono 10 Packed", "Mono 12", "Mono 12 Packed", "Mono 14", RGB 8 Packed", "YUV 422 Packed", "Bayer RG 8", "Bayer RG 10"
        #, "Bayer RG 10 Packed", "Bayer RG 12", "Bayer RG 12 Packed"]
        # print('get_pixel_format: ',pixel_format_str)

        if pixel_format_str == 'Mono8':
            self.pixel_format_combobox.current(0)
            pass
        elif pixel_format_str == 'Mono10':
            self.pixel_format_combobox.current(1)
            pass
        elif pixel_format_str == 'Mono12':
            self.pixel_format_combobox.current(2)
            pass
        elif pixel_format_str == 'RGB8Packed':
            self.pixel_format_combobox.current(3)
            pass

    def get_pixel_format_v0(self, pixel_format_str):
        # self.pixel_format_list: ["Mono 8", "Mono 10", "Mono 10 Packed", "Mono 12", "Mono 12 Packed", "Mono 14", RGB 8 Packed", "YUV 422 Packed", "Bayer RG 8", "Bayer RG 10"
        #, "Bayer RG 10 Packed", "Bayer RG 12", "Bayer RG 12 Packed"]
        # print('get_pixel_format: ',pixel_format_str)

        if pixel_format_str == 'Mono8':
            self.pixel_format_combobox.current(0)
            pass
        elif pixel_format_str == 'Mono10':
            self.pixel_format_combobox.current(1)
            pass
        elif pixel_format_str == 'Mono10Packed':
            self.pixel_format_combobox.current(2)
            pass
        elif pixel_format_str == 'Mono12':
            self.pixel_format_combobox.current(3)
            pass
        elif pixel_format_str == 'Mono12Packed':
            self.pixel_format_combobox.current(4)
            pass
        elif pixel_format_str == 'Mono14':
            self.pixel_format_combobox.current(5)
            pass
        elif pixel_format_str == 'RGB8Packed':
            self.pixel_format_combobox.current(6)
            pass
        elif pixel_format_str == 'YUV422Packed':
            self.pixel_format_combobox.current(7)
            pass
        elif pixel_format_str == 'BayerRG8':
            self.pixel_format_combobox.current(8)
            pass
        elif pixel_format_str == 'BayerRG10':
            self.pixel_format_combobox.current(9)
            pass
        elif pixel_format_str == 'BayerRG10Packed':
            self.pixel_format_combobox.current(10)
            pass
        elif pixel_format_str == 'BayerRG12':
            self.pixel_format_combobox.current(11)
            pass
        elif pixel_format_str == 'BayerRG12Packed':
            self.pixel_format_combobox.current(12)
            pass

    def pixel_format_sel(self, event = None):
        pixel_format_id = None
        if self.pixel_format_combobox.get() == "Mono 8":
            pixel_format_id = 'Mono8'
        elif self.pixel_format_combobox.get() == "Mono 10":
            pixel_format_id = 'Mono10'
        elif self.pixel_format_combobox.get() == "Mono 10 Packed":
            pixel_format_id = 'Mono10Packed'
        elif self.pixel_format_combobox.get() == "Mono 12":
            pixel_format_id = 'Mono12'
        elif self.pixel_format_combobox.get() == "Mono 12 Packed":
            pixel_format_id = 'Mono12Packed'
        elif self.pixel_format_combobox.get() == "Mono 14":
            pixel_format_id = 'Mono14'
        elif self.pixel_format_combobox.get() == "RGB 8 Packed":
            pixel_format_id = 'RGB8Packed'
        elif self.pixel_format_combobox.get() == "YUV 422 Packed":
            pixel_format_id = 'YUV422Packed'
        elif self.pixel_format_combobox.get() == "Bayer RG 8":
            pixel_format_id = 'BayerRG8'
        elif self.pixel_format_combobox.get() == "Bayer RG 10":
            pixel_format_id = 'BayerRG10'
        elif self.pixel_format_combobox.get() == "Bayer RG 10 Packed":
            pixel_format_id = 'BayerRG10Packed'
        elif self.pixel_format_combobox.get() == "Bayer RG 12":
            pixel_format_id = 'BayerRG12'
        elif self.pixel_format_combobox.get() == "Bayer RG 12 Packed":
            pixel_format_id = 'BayerRG12Packed'

        if pixel_format_id is not None:
            self.crevis_operation.Set_Pixel_Format(pixel_format_id)
        pass