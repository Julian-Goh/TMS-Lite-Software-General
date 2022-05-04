import os
from os import path
import sys

import tkinter as tk
import tkinter.messagebox
from tkinter import ttk

from PIL import ImageTk, Image
import numpy as np
import imutils

import inspect
import ctypes
from ctypes import *

import threading
import msvcrt

from Tk_MsgBox.custom_msgbox import Ask_Msgbox, Info_Msgbox, Error_Msgbox, Warning_Msgbox

from Tk_Custom_Widget.ScrolledCanvas import ScrolledCanvas
from Tk_Custom_Widget.custom_zoom_class import CanvasImage

from misc_module.tool_tip import CreateToolTip
from misc_module.tk_canvas_display import display_func, clear_display_func

from Tk_Validate.tk_validate import *

from multi_camera_operation import MultiCameraOp

# code_PATH = os.getcwd()
# sys.path.append(code_PATH + '\\MVS-Python\\MvImport')

from MvCameraControl_class import *

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

class Multi_Camera_GUI():
    #cam_conn_status = False
    def __init__(self, cam_conn_status = False, main_frame = None, scroll_class = None, cam_disconnect_img = None
        , toggle_ON_button_img = None, toggle_OFF_button_img = None, img_flip_icon = None
        , save_icon = None, popout_icon = None, info_icon = None, fit_to_display_icon = None, window_icon = None):

        self.cam_conn_status = cam_conn_status
        self.main_frame = main_frame
        self.scroll_class = scroll_class
        self.info_icon = info_icon
        self.cam_disconnect_img = cam_disconnect_img
        self.toggle_ON_button_img = toggle_ON_button_img
        self.toggle_OFF_button_img = toggle_OFF_button_img 

        self.img_flip_icon = img_flip_icon

        self.save_icon = save_icon
        self.popout_icon = popout_icon

        self.fit_to_display_icon = fit_to_display_icon

        self.window_icon = window_icon

        self.popout_status = False
        self.popout_var_mode = 'original'

        #print(self.popout_icon)

        #self.mv_camera = MvCamera()
        self.obj_cam_operation = None

        self.hikvision_device_ID = None
        self.cam_display_width = 400
        self.cam_display_height = 300

        self.cam_mode_str = 'continuous'
        self.cam_param_float = np.zeros((3), dtype=np.float32)
        #param_float index--> 0:exposure, 1:gain, 2:frame rate
        self.cam_param_int = np.zeros((6), dtype=np.uint16)
        self.cam_param_int[1] = self.cam_param_int[2] = self.cam_param_int[3] = 1
        #param_int index--> 0: brightness, 1: R-ch, 2: G-ch, 3: B-ch, 4: black level, 5: sharpness

        self.revert_val_gain = self.revert_val_exposure = self.revert_val_framerate = False
        self.revert_val_brightness = False
        self.revert_val_red_ratio = self.revert_val_green_ratio = self.revert_val_blue_ratio = False
        self.revert_val_black_lvl = False
        self.revert_val_sharpness = False

        self.cam_update_ID = None
        self.auto_exposure_handle = None
        self.auto_gain_handle = None
        self.auto_white_handle = None

        self.auto_gain_toggle = self.auto_exposure_toggle = self.framerate_toggle = False
        self.auto_white_toggle = False
        self.black_lvl_toggle = False
        self.sharpness_toggle = False

        self.flip_img_bool = False

        self.GUI_mode_sel = 'normal'

        self.btn_normal_cam_mode = tk.Button(self.main_frame, relief = tk.GROOVE, text = 'Normal Camera Mode')
        self.btn_normal_cam_mode['width'] = 17
        self.btn_normal_cam_mode['command'] = self.select_GUI_1

        self.GUI_sel_btn_state(self.btn_normal_cam_mode)

        self.popout_disp_tk_status = tk.StringVar() # 'Popout Live Display: Inactive' or 'Popout Live Display: Active'
        self.popout_disp_tk_label = tk.Label(self.main_frame, textvariable = self.popout_disp_tk_status, font = 'Helvetica 10 bold italic', fg = 'white')
        self.popout_disp_tk_label['bg'] = 'red'
        self.popout_disp_tk_status.set('Popout Live Display: Inactive')

        self.master_width = self.scroll_class.get_frame_size()[0]

        self.camera_display_GUI_1()
        self.camera_control_GUI()
        self.flip_btn_gen()
        self.popout_button_generate()

        self.camera_control_state()

    def show_camera_control(self):
        #print(self.nSelCamIndex, self.GUI_mode_sel)
        self.scroll_class.resize_frame(width = self.cam_display_width + self.cam_display_width + 15 + self.cam_ctrl_frame['width'] + 5)
        self.btn_normal_cam_mode.place(x=0,y=0+35)
        self.popout_disp_tk_label.place(x=0, y = 30+35)

        self.select_GUI_1()

        if self.cam_conn_status == True:
            self.start_auto_toggle_parameter()

    def hide_camera_control(self):
        self.scroll_class.resize_frame(width = self.master_width)
        self.btn_normal_cam_mode.place_forget()
        self.cam_display_fr_1.place_forget()
        self.cam_ctrl_frame.place_forget()

        self.stop_auto_toggle_parameter()

    def select_GUI_1(self):
        self.GUI_mode_sel = 'normal'
        #print(self.nSelCamIndex, self.GUI_mode_sel)
        self.GUI_sel_btn_state(self.btn_normal_cam_mode)
        self.cam_display_fr_1.place(x=0, y=30+35+25)
        self.cam_ctrl_frame.place(x = self.cam_display_width + self.cam_display_width + 15, y =0)

        self.btn_save_img.place(x=20, y=30)
        self.trigger_auto_save_checkbtn.place(x=20, y = 60)

        self.check_cam_popout_disp()

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

    def widget_bind_focus(self, widget):
        widget.bind("<1>", lambda event: self.focus_set_func(widget))

    def focus_set_func(self, widget):
        widget.focus_set()
        self.main_frame.focus_set()

    def flip_img_display(self):
        if self.flip_img_bool == False:
            self.flip_img_bool = True
        elif self.flip_img_bool == True:
            self.flip_img_bool = False

        #print(self.flip_img_bool)

    def flip_btn_gen(self):
        self.flip_btn_1 = tk.Button(self.cam_display_fr_1, relief = tk.GROOVE, bd =0 , image = self.img_flip_icon, bg = 'white')

        CreateToolTip(self.flip_btn_1, 'Flip Image by 180' + chr(176)
            , 0, -22, width = 115, height = 20)
        self.flip_btn_1['command'] = self.flip_img_display

        self.flip_btn_1.place(x = self.cam_display_width + self.cam_display_width - 50, y= 0+2)

    def popout_button_generate(self):
        self.Normal_cam_popout_btn = tk.Button(self.cam_display_fr_1, relief = tk.GROOVE, bd =0 , image = self.popout_icon, bg = 'white')
        CreateToolTip(self.Normal_cam_popout_btn, 'Camera Pop-out Display'
            , 0, -22, width = 145, height = 20)

        self.Normal_cam_popout_btn['command'] = lambda: self.cam_popout_gen(toplvl_W = 700, toplvl_H = 500, toplvl_title = 'Camera Display')

        self.Normal_cam_popout_btn.place(x = self.cam_display_width + self.cam_display_width - 20, y= 0)

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

                try:
                    self.cam_popout_toplvl.iconphoto(False, self.window_icon)
                except Exception:
                    pass

                self.cam_popout_init()
                if self.obj_cam_operation is not None:
                    if self.obj_cam_operation.numArray is not None:
                        self.popout_cam_disp_func(self.obj_cam_operation.numArray)
                        self.cam_popout_disp.fit_to_display(self.cam_popout_toplvl.winfo_width(),self.cam_popout_toplvl.winfo_height()-30)
            else:
                #print('exist')
                self.cam_popout_toplvl.deiconify()
                self.cam_popout_toplvl.lift()
                pass

        except AttributeError:
            #print('AttributeError caught')
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

            try:
                self.cam_popout_toplvl.iconphoto(False, self.window_icon)
            except Exception:
                pass

            self.cam_popout_init()

            if self.obj_cam_operation is not None:
                if self.obj_cam_operation.numArray is not None:
                    self.popout_cam_disp_func(self.obj_cam_operation.numArray)
                    self.cam_popout_disp.fit_to_display(self.cam_popout_toplvl.winfo_width(),self.cam_popout_toplvl.winfo_height()-30)

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

        try:
            self.cam_popout_toplvl.destroy()
        except (AttributeError, tk.TclError) as e:
            pass

        if self.obj_cam_operation is not None:
            if self.obj_cam_operation.numArray is not None:
                self.obj_cam_operation.All_Mode_Cam_Disp()

        self.check_cam_popout_disp()


    def cam_popout_init(self):
        self.check_cam_popout_disp()
        try:
            check_bool = tk.Toplevel.winfo_exists(self.cam_popout_toplvl)
            if check_bool == 0:
                pass
            else:
                clear_display_func(self.cam_display_rgb, self.cam_display_R, self.cam_display_G, self.cam_display_B)
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
                self.cam_popout_disp.place(x=0, y=30, relwidth = 1, relheight = 1, anchor = 'nw')

                self.fit_to_display_btn = tk.Button(self.cam_popout_toplvl, relief = tk.GROOVE, image = self.fit_to_display_icon, borderwidth=0)
                self.fit_to_display_btn['command'] = lambda: self.cam_popout_disp.fit_to_display(self.cam_popout_toplvl.winfo_width(),self.cam_popout_toplvl.winfo_height()-30)
                CreateToolTip(self.fit_to_display_btn, 'Fit-to-Screen'
                    , 30, 0, width = 80, height = 20)
                self.fit_to_display_btn.place(x=480, y=3)

                self.cam_popout_toplvl.deiconify()
                self.cam_popout_toplvl.lift()
        except AttributeError:
            pass

    def popout_cam_disp_func(self, numArray):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.cam_popout_toplvl)
            if check_bool == 0:
                pass
            else:
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

                if self.cam_popout_toplvl.wm_state() == 'normal':
                    #self.cam_popout_toplvl.attributes('-topmost', 'true')
                    self.cam_popout_toplvl.lift()

        except (AttributeError, tk.TclError) as e:
            #print(e)
            #print('Specified Error Caught')
            pass

    ###############################################################################################
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

    #1. CAMERA DEFAULT DISPLAY
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
            
    def camera_control_GUI(self):
        bg_color = 'SteelBlue1' #'DarkSlateGray2'
        cam_ctrl_fr_H = 0

        self.cam_ctrl_frame = tk.Frame(self.main_frame, bg = bg_color, highlightbackground = 'navy', highlightthickness=1)
        self.cam_ctrl_frame['width'] = 312
        self.cam_ctrl_frame.place(x = self.cam_display_width + self.cam_display_width + 15, y =0)

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
        self.btn_grab_frame['command'] = self.start_grabbing
        self.widget_bind_focus(self.btn_grab_frame)
        self.btn_grab_frame.place(x=35 + 15, y=40+25)

        self.capture_img_status = tk.IntVar()
        self.capture_img_checkbtn = tk.Checkbutton(self.cam_frame_1, text='Capture Image', variable = self.capture_img_status, onvalue=1, offvalue=0)
        self.capture_img_checkbtn.place(x=176,y=40+25)

        self.btn_trigger_once = tk.Button(self.cam_frame_1, text='Trigger Once', width=15, height=1, relief = tk.GROOVE)
        self.btn_trigger_once['command'] = self.trigger_once
        self.widget_bind_focus(self.btn_trigger_once)
        self.btn_trigger_once['state'] = 'disable'
        self.btn_trigger_once.place(x=150 + 15, y=90+30)
        ###############################################################################################################################
        
        tk.Label(self.cam_frame_2, text = 'Save Images: ', font = 'Helvetica 11 bold').place(x=0, y=0)

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
        self.trigger_auto_save_checkbtn.place(x=20,y=60)

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

        Validate_Float(self.entry_framerate, self.framerate_str, decimal_places = 2, only_positive = True, lo_limit = 1, hi_limit = 1000)

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
            'acquisition.' +'\n\n'+ 'Min: 28\nMax: 1,000,000'
            , -220, -40, width = 220, height = 120)
        self.exposure_str = tk.StringVar()
        #self.entry_exposure = tk.Entry(self.cam_frame_3, textvariable = self.exposure_str, highlightbackground="black", highlightthickness=1, width = 9)
        self.entry_exposure = tk.Spinbox(self.cam_frame_3, textvariable = self.exposure_str, highlightbackground="black", highlightthickness=1, width = 7, from_=28, to =1000000, increment= 1000)
        self.exposure_str.set(self.cam_param_float[0])

        Validate_Float(self.entry_exposure, self.exposure_str, decimal_places = 2, only_positive = True, lo_limit = 28, hi_limit = 1000000)

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
            'the brightness of the image output\n'+ 'by the camera.' +'\n\n'+ 'Min: 0\nMax: 15.0062'
            , -220, -40, width = 220, height = 140)

        self.gain_str = tk.StringVar()
        # self.entry_gain = tk.Entry(self.cam_frame_3, textvariable = self.gain_str, highlightbackground="black", highlightthickness=1, width = 9)
        self.entry_gain = tk.Spinbox(self.cam_frame_3, textvariable = self.gain_str, highlightbackground="black", highlightthickness=1, width = 7, from_=0, to =15.0062)
        self.gain_str.set(self.cam_param_float[1])

        Validate_Float(self.entry_gain, self.gain_str, decimal_places = 4, only_positive = True, lo_limit = 0, hi_limit = 15.0062)

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
        label_brightness = tk.Label(self.cam_frame_3, text='Brightness', width=12, anchor = 'e')
        info_brightness = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_brightness, 'Brightness: \n' + 'Sets the selected Brightness control.' + \
            '\n\n' + 'Min: 0\nMax: 255'
            , -220, -30, width = 220, height = 90)

        self.brightness_str = tk.StringVar()
        #self.entry_brightness = tk.Entry(self.cam_frame_3, textvariable = self.brightness_str, highlightbackground="black", highlightthickness=1, width = 9)
        self.entry_brightness = tk.Spinbox(self.cam_frame_3, textvariable = self.brightness_str, highlightbackground="black", highlightthickness=1, width = 7, from_=0, to= 255)
        Validate_Int(self.entry_brightness, self.brightness_str, only_positive = True, lo_limit = 0, hi_limit = 255)
        self.brightness_str.set(self.cam_param_int[0])

        self.entry_brightness.bind('<Return>', self.set_parameter_brightness)
        self.entry_brightness.bind('<Tab>', self.set_parameter_brightness)
        self.entry_brightness.bind('<FocusOut>', self.set_parameter_brightness)
        self.entry_brightness['command'] = self.set_parameter_brightness

        self.entry_brightness['state'] = 'disable'
        label_brightness.place(x=35+ shift_x, y=35 + 165 + 30)
        info_brightness.place(x=0+ shift_x, y=35 + 165 + 30)
        self.entry_brightness.place(x=130+ shift_x, y=35 + 165 + 30)

        ###############################################################################################################################
        label_auto_white = tk.Label(self.cam_frame_3, text = 'Auto White Balance', anchor = 'e')

        self.btn_auto_white = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_auto_white['command'] = self.set_auto_white
        self.widget_bind_focus(self.btn_auto_white)

        self.win_balance_ratio = tk.Frame(self.cam_frame_3, width = 165, height = 70+2)#, bg = 'grey')
        label_balance_ratio = tk.Label(self.win_balance_ratio, text = 'Balance Ratio', anchor = 'e')

        info_balance_ratio = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_balance_ratio, 'Balance Ratio: \n' + 'Gamma correction of pixel intensity,\nwhich helps optimizing the brightness\n'+ \
            'of acquired images for displaying\n'+ 'on a monitor.' +'\n\n'+ 'Min: 1\nMax: 4095'
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
        Validate_Int(self.entry_red_ratio, self.red_ratio_str, only_positive = True, lo_limit = 1, hi_limit = 4095)
        Validate_Int(self.entry_green_ratio, self.green_ratio_str, only_positive = True, lo_limit = 1, hi_limit = 4095)
        Validate_Int(self.entry_blue_ratio, self.blue_ratio_str, only_positive = True, lo_limit = 1, hi_limit = 4095)

        label_balance_ratio.place(x=0, y= 25)
        red_tag.place(x=80,y=0)
        green_tag.place(x=80,y=25)
        blue_tag.place(x=80,y=50)

        self.entry_red_ratio.place(x=105, y=0)
        self.entry_green_ratio.place(x=105, y=25)
        self.entry_blue_ratio.place(x=105, y=50)

        label_auto_white.place(x=15 +shift_x, y=35 + 193 + 30) # 165 + 55/2 = 165 + 28 = 193
        self.btn_auto_white.place(x=130 + shift_x, y =30 + 193 + 30)
        info_balance_ratio.place(x=0+ shift_x, y = 85 + 193 + 30)
        self.win_balance_ratio.place(x=25 +shift_x, y= 60 + 193 + 30) #165 + 55
        
        ###############################################################################################################################
        label_black_lvl = tk.Label(self.cam_frame_3, text='Black Level', width=12, anchor = 'e')
        info_black_lvl = tk.Label(self.cam_frame_3, image = self.info_icon)
        CreateToolTip(info_black_lvl, 'Black Level: \n' + 'Analog black level in percent.\n\n'+ 'Min: 0\nMax: 4095'
            , -180, -20, width = 180, height = 90)

        self.black_lvl_str = tk.StringVar()
        self.entry_black_lvl = tk.Spinbox(self.cam_frame_3, textvariable = self.black_lvl_str, highlightbackground="black", highlightthickness=1, width = 7, from_=0, to =4095)
        self.black_lvl_str.set(self.cam_param_int[4])
        Validate_Int(self.entry_black_lvl, self.black_lvl_str, only_positive = True, lo_limit = 0, hi_limit = 4095)

        self.entry_black_lvl.bind('<Return>', self.set_parameter_black_lvl)
        self.entry_black_lvl.bind('<Tab>', self.set_parameter_black_lvl)
        self.entry_black_lvl.bind('<FocusOut>', self.set_parameter_black_lvl)
        self.entry_black_lvl['command'] = self.set_parameter_black_lvl

        label_black_lvl_enable = tk.Label(self.cam_frame_3, text = 'Black Level Enable', anchor = 'e')
        self.btn_enable_black_lvl = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_enable_black_lvl['command'] = self.enable_black_lvl
        self.widget_bind_focus(self.btn_enable_black_lvl)

        label_black_lvl.place(x=35+ shift_x, y=60 + 303 + 30) #193 + 55 + 55 = 303
        info_black_lvl.place(x = 0+ shift_x, y=60 + 303 + 30)
        label_black_lvl_enable.place(x=23+ shift_x, y= 35 + 303 + 30)
        self.entry_black_lvl.place(x=130+ shift_x, y=60 + 303 + 30)
        self.btn_enable_black_lvl.place(x=130 + shift_x, y =30 + 303 + 30)

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
        Validate_Int(self.entry_sharpness, self.sharpness_str, only_positive = True, lo_limit = 0, hi_limit = 100)

        self.entry_sharpness.bind('<Return>', self.set_parameter_sharpness)
        self.entry_sharpness.bind('<Tab>', self.set_parameter_sharpness)
        self.entry_sharpness.bind('<FocusOut>', self.set_parameter_sharpness)
        self.entry_sharpness['command'] = self.set_parameter_sharpness

        label_sharpness_enable = tk.Label(self.cam_frame_3, text = 'Sharpness Enable', anchor = 'e')
        self.btn_enable_sharpness = tk.Button(self.cam_frame_3, image = self.toggle_OFF_button_img, borderwidth=0)
        self.btn_enable_sharpness['command'] = self.enable_sharpness
        self.widget_bind_focus(self.btn_enable_sharpness)
        
        label_sharpness.place(x=35+ shift_x, y=60 + 358 + 30)
        info_sharpness.place(x = 0+ shift_x, y=60 + 358 + 30)
        label_sharpness_enable.place(x=23+ shift_x, y= 35 + 358 + 30)
        self.entry_sharpness.place(x=130+ shift_x, y=60 + 358 + 30)
        self.btn_enable_sharpness.place(x=130 + shift_x, y =30 + 358 + 30)

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

        self.pixel_format_list = ["Mono 8", "Mono 10", "Mono 10 Packed", "Mono 12", "Mono 12 Packed", "RGB 8", "BGR 8", "YUV 422 (YUYV) Packed", "YUV 422 Packed", "Bayer RG 8", "Bayer RG 10", "Bayer RG 10 Packed", "Bayer RG 12", "Bayer RG 12 Packed"]
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

            if isinstance(func, list) == True:
                try:
                    btn['command'] = func[0]
                except Exception as e:
                    print('Error for grab_btn_state: ', e)
                    pass

            elif isinstance(func, list) == False:
                try:
                    btn['command'] = func
                except Exception as e:
                    print('Error for grab_btn_state: ', e)
                    pass

        elif btn['text'] == 'STOP':
            btn['text'] = 'START'
            btn['activebackground'] = 'forest green'
            btn['bg'] = 'green3'
            btn['activeforeground'] = 'white'
            btn['fg'] = 'white'

            if isinstance(func, list) == True:
                try:
                    btn['command'] = func[1]
                except Exception as e:
                    print('Error for grab_btn_state: ', e)
                    pass

            elif isinstance(func, list) == False:
                try:
                    btn['command'] = func
                except Exception as e:
                    print('Error for grab_btn_state: ', e)
                    pass

    def grab_btn_init_state(self, btn, func = None):
        btn['text'] = 'START'
        btn['activebackground'] = 'forest green'
        btn['bg'] = 'green3'
        btn['activeforeground'] = 'white'
        btn['fg'] = 'white'
        try:
            btn['command'] = func
        except Exception as e:
            print('Error for grab_btn_state: ', e)
            pass

    def camera_control_state(self):
        if self.cam_conn_status == False:
            widget_disable(self.radio_continuous, self.radio_trigger, self.btn_grab_frame
                , self.btn_get_parameter, self.btn_set_parameter
                , self.btn_auto_gain, self.btn_auto_exposure, self.btn_enable_framerate
                , self.entry_gain, self.entry_exposure, self.entry_framerate
                , self.capture_img_checkbtn)

            widget_disable(self.btn_auto_white, self.entry_red_ratio, self.entry_green_ratio, self.entry_blue_ratio)
            widget_disable(self.btn_enable_black_lvl, self.entry_black_lvl)
            widget_disable(self.btn_enable_sharpness, self.entry_sharpness)

            widget_disable(self.btn_normal_cam_mode)

            #self.trigger_src_select['state'] = 'disable'
            
            self.btn_trigger_once['state'] = 'disable'
            self.checkbtn_trigger_src['state'] = 'disable'
            self.entry_brightness['state'] = 'disable'
            self.pixel_format_combobox['state'] = 'disable'

            self.trigger_auto_save_checkbtn['state'] = 'disable'

            self.btn_save_img['state'] = 'disable'
            self.save_img_format_sel['state'] = 'disable'

            self.triggercheck_val.set(0)
            self.cam_mode_str = 'continuous'
            self.cam_mode_var.set(self.cam_mode_str)
            self.capture_img_status.set(0)
            self.trigger_auto_save_bool.set(0)

        elif self.cam_conn_status == True:
            widget_enable(self.radio_continuous, self.radio_trigger, self.btn_grab_frame
                , self.btn_get_parameter, self.btn_set_parameter
                , self.btn_auto_gain, self.btn_auto_exposure, self.btn_enable_framerate
                , self.entry_gain, self.entry_exposure, self.entry_framerate
                , self.capture_img_checkbtn)

            widget_enable(self.btn_auto_white)
            widget_enable(self.btn_enable_black_lvl)
            widget_enable(self.btn_enable_sharpness)

            widget_enable(self.btn_normal_cam_mode)

            self.pixel_format_combobox['state'] = 'readonly'

            self.btn_save_img['state'] = 'normal'
            self.save_img_format_sel['state'] = 'readonly'

            self.btn_auto_exposure, self.entry_exposure = self.camera_toggle_button_state(self.auto_exposure_toggle, self.btn_auto_exposure, 
                self.toggle_ON_button_img, self.toggle_OFF_button_img, self.entry_exposure)

            self.btn_auto_gain, self.entry_gain = self.camera_toggle_button_state(self.auto_gain_toggle, self.btn_auto_gain, 
                self.toggle_ON_button_img, self.toggle_OFF_button_img, self.entry_gain)

            self.btn_enable_framerate, self.entry_framerate = self.camera_toggle_button_state(self.framerate_toggle, self.btn_enable_framerate, 
                self.toggle_ON_button_img, self.toggle_OFF_button_img, self.entry_framerate, 'framerate')

            self.white_balance_btn_state()
            self.black_lvl_btn_state()
            self.sharpness_btn_state()
            self.camera_brightness_entry_state()

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

    def camera_no_display_func(self):
        self.dummy_canvas_rgb.create_image(self.cam_display_width/2, self.cam_display_height/2, image=self.cam_disconnect_img, anchor='center', tags='img')
        self.dummy_canvas_rgb.image = self.cam_disconnect_img

        self.dummy_canvas_R.create_image(self.cam_display_width/2, self.cam_display_height/2, image=self.cam_disconnect_img, anchor='center', tags='img')
        self.dummy_canvas_R.image = self.cam_disconnect_img

        self.dummy_canvas_G.create_image(self.cam_display_width/2, self.cam_display_height/2, image=self.cam_disconnect_img, anchor='center', tags='img')
        self.dummy_canvas_G.image = self.cam_disconnect_img

        self.dummy_canvas_B.create_image(self.cam_display_width/2, self.cam_display_height/2, image=self.cam_disconnect_img, anchor='center', tags='img')
        self.dummy_canvas_B.image = self.cam_disconnect_img

    def open_device(self, hikvision_device_ID, nSelCamIndex, mv_camera):
        self.hikvision_device_ID = hikvision_device_ID
        self.nSelCamIndex = nSelCamIndex
        self.mv_camera = mv_camera
        # print(self.mv_camera)
        # print('self.hikvision_device_ID: ',self.hikvision_device_ID)
        # print('self.nSelCamIndex: ', self.nSelCamIndex)
        #print(self.cam_conn_status)

        # if int(self.nSelCamIndex) == 0:
        #     self.cam_conn_status = True
        # else:
        #     self.cam_conn_status = False
        # print(self.cam_conn_status)
        if True == self.cam_conn_status:
            tkinter.messagebox.showinfo('show info','Camera is Running!')
            return

        self.obj_cam_operation = MultiCameraOp(self.mv_camera, self.hikvision_device_ID, self.nSelCamIndex)
        #print('self.obj_cam_operation: ', self.obj_cam_operation)
        #print(dir(self.mv_camera))
        try:
            ret = self.obj_cam_operation.Open_device()
            if  0!= ret:
                self.cam_conn_status = False
            else:
                self.cam_conn_status = True
                self.cam_mode_str = 'continuous'
                self.cam_mode_var.set(self.cam_mode_str)
                self.camera_control_state()
                self.trigger_src_func()

                try:
                    self.popout_save_btn['state'] = 'normal'
                except Exception:
                    pass

                self.get_parameter_exposure()
                self.get_parameter_gain()
                self.get_parameter_framerate()
                self.get_parameter_brightness()
                self.get_parameter_white()
                self.get_parameter_black_lvl()
                self.get_parameter_sharpness()

                self.stop_auto_toggle_parameter() #because control panel is not active during Home in Multi Camera Operation

        except Exception as e:
            print(e)
            self.cam_conn_status = False

        #print('self.cam_conn_status: ',self.cam_conn_status)

        return ret

    def start_grabbing(self):
        self.cam_display_place_GUI_1()

        self.obj_cam_operation.Start_grabbing()
        self.grab_btn_state(self.btn_grab_frame, [self.stop_grabbing, self.start_grabbing])
        self.pixel_format_combobox['state'] = 'disable'

    def stop_grabbing(self):
        #print('stop grab')
        try:
            self.obj_cam_operation.Stop_grabbing()
        except AttributeError:
            #tkinter.messagebox.showinfo('show info','Device not Opened to Stop Grab!')
            pass
        #self.start_grab_status = False

        try:
            from main_GUI import main_GUI
            _main_class = main_GUI.class_multi_cam_conn
            _main_class.display_gui_list[self.nSelCamIndex].create_image(self.cam_display_width/2, self.cam_display_height/2, image='', anchor='center', tags='img')
            _main_class.display_gui_list[self.nSelCamIndex].image = ''
        except Exception:
            pass

        self.cam_display_forget_GUI_1()

        self.cam_popout_close()
        self.grab_btn_state(self.btn_grab_frame, [self.stop_grabbing, self.start_grabbing])
        self.pixel_format_combobox['state'] = 'readonly'

    def close_device(self):
        try:
            self.obj_cam_operation.Stop_grabbing()
        except AttributeError:
            pass

        self.btn_normal_cam_mode.invoke()

        self.cam_display_forget_GUI_1()

        self.cam_popout_close()

        self.grab_btn_init_state(self.btn_grab_frame, self.start_grabbing)
        self.cam_conn_status = False
        self.camera_control_state() #state disabled or normal

        self.stop_auto_toggle_parameter()
        # self.stop_auto_exposure()
        # self.stop_auto_gain()
        try:
            self.obj_cam_operation.Close_device()
        except Exception as e:#AttributeError:
            #print(e)
            pass

    def cam_quit_func(self):
        print('Quitting...')
        try:
            self.obj_cam_operation.Stop_grabbing()
        except AttributeError:
            pass

        try:
            self.obj_cam_operation.Close_device()
        except AttributeError:
            pass

    def set_triggermode(self):
        # strMode = self.cam_mode_var.get()
        # print(strMode)
        
        #print(self.cam_mode_str)
        if self.cam_mode_var.get() == 'continuous':
            if self.cam_mode_str != self.cam_mode_var.get():
                self.cam_mode_str = self.cam_mode_var.get()
                self.btn_save_img['state'] = 'normal'
                self.capture_img_checkbtn['state'] = 'normal'
                self.checkbtn_trigger_src['state'] = 'disable'
                self.btn_trigger_once['state'] = 'disable'
                self.trigger_auto_save_checkbtn['state'] = 'disable'
                self.trigger_auto_save_bool.set(0)

                try:
                    #self.obj_cam_operation.Set_trigger_mode(strMode)
                    self.obj_cam_operation.Set_trigger_mode(self.cam_mode_str)
                except AttributeError:
                    pass

        elif self.cam_mode_var.get() == 'triggermode':
            #print('triggermode')
            if self.cam_mode_str != self.cam_mode_var.get():

                self.cam_mode_str = self.cam_mode_var.get()
                self.obj_cam_operation.b_save = False
                self.btn_save_img['state'] = 'normal'

                self.capture_img_checkbtn['state'] = 'disable'
                self.capture_img_status.set(0)
                
                self.checkbtn_trigger_src['state'] = 'normal'
                self.trigger_src_func()

                self.trigger_auto_save_checkbtn['state'] = 'normal'

                #print('Frame Display Cleared...')
                try:
                    #self.obj_cam_operation.Set_trigger_mode(strMode)
                    self.obj_cam_operation.Set_trigger_mode(self.cam_mode_str)
                except AttributeError:
                    pass

    def trigger_src_func(self, event = None):
        if self.triggercheck_val.get() == 0:
            strSrc = 'LINE0'
            self.btn_trigger_once['state'] = 'disable'

        elif self.triggercheck_val.get() == 1:
            strSrc = 'SOFTWARE'
            self.btn_trigger_once['state'] = 'normal'

        try:
            #self.obj_cam_operation.Trigger_Source(self.trigger_src_select.get())
            self.obj_cam_operation.Trigger_Source(strSrc)
        except AttributeError:
            pass

    #ch:设置触发命令 | en:set trigger software
    def trigger_once(self):
        #nCommand = self.triggercheck_val.get()
        #self.obj_cam_operation.Trigger_once(nCommand)
        self.obj_cam_operation.Trigger_once()

    def img_save_func(self):
        if True == self.obj_cam_operation.check_cam_frame():
            self.obj_cam_operation.b_save = True
            self.obj_cam_operation.img_save_flag = False
            self.obj_cam_operation.img_save_folder = None
            self.img_save_msg_box()
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

    def get_parameter_exposure(self,event=None):
        if self.cam_conn_status == True:
            if self.auto_exposure_toggle == True:
                self.auto_exposure_handle = self.cam_ctrl_frame.after(300, self.get_parameter_exposure)

            elif self.auto_exposure_toggle == False:
                self.stop_auto_exposure()

            #print('self.auto_exposure_handle: ', self.auto_exposure_handle)
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

            except Exception as e: #AttributeError:
                #print(e)
                pass
        else:
            pass
        #print(self.cam_param_int[1])
        self.red_ratio_str.set(self.cam_param_int[1])
        self.green_ratio_str.set(self.cam_param_int[2])
        self.blue_ratio_str.set(self.cam_param_int[3])

    def get_parameter_framerate(self,event=None):
        self.obj_cam_operation.Get_parameter_framerate()
        self.cam_param_float[2] = self.obj_cam_operation.frame_rate
        self.framerate_str.set(self.cam_param_float[2])

    def get_parameter_brightness(self, event=None):
        self.obj_cam_operation.Get_parameter_brightness()
        self.cam_param_int[0] = self.obj_cam_operation.brightness
        #print('self.cam_param_int[0]: ',self.cam_param_int[0])
        self.brightness_str.set(self.cam_param_int[0])

    def get_parameter_black_lvl(self, event=None):
        self.obj_cam_operation.Get_parameter_black_lvl()
        self.cam_param_int[4] = self.obj_cam_operation.black_lvl
        #print('self.cam_param_int[4]: ',self.cam_param_int[4])
        self.black_lvl_str.set(self.cam_param_int[4])

    def get_parameter_sharpness(self, event=None):
        self.obj_cam_operation.Get_parameter_sharpness()
        self.cam_param_int[5] = self.obj_cam_operation.sharpness
        #print('self.cam_param_int[5]: ',self.cam_param_int[5])
        self.sharpness_str.set(self.cam_param_int[5])

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
            self.obj_cam_operation.exposure_time = self.entry_exposure.get()
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
            self.obj_cam_operation.gain = self.entry_gain.get()
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
            self.obj_cam_operation.frame_rate = self.entry_framerate.get()
            self.obj_cam_operation.Set_parameter_framerate(self.obj_cam_operation.frame_rate)

            if self.revert_val_framerate == False:
                #print('self.revert_val_framerate: False')
                self.cam_param_float[2] = self.obj_cam_operation.frame_rate

            elif self.revert_val_framerate == True:
                #print('self.revert_val_framerate: True')
                self.framerate_str.set(self.cam_param_float[2])
                self.revert_val_framerate = False
        else:
            self.framerate_str.set(self.cam_param_float[2])
            self.revert_val_framerate = False

    def set_parameter_brightness(self, event = None):
        if self.cam_conn_status == True:
            if self.brightness_str.get() == '':
                self.brightness_str.set(self.cam_param_int[0])

            self.obj_cam_operation.brightness = self.entry_brightness.get()
            self.obj_cam_operation.Set_parameter_brightness(self.obj_cam_operation.brightness)

            if self.revert_val_brightness == False:
                self.cam_param_int[0] = self.obj_cam_operation.brightness
            elif self.revert_val_brightness == True:
                self.brightness_str.set(self.cam_param_int[0])
                self.revert_val_brightness = False

        else:
            self.brightness_str.set(self.cam_param_int[0])
            self.revert_val_brightness = False

    def set_parameter_red_ratio(self, event = None):
        if self.cam_conn_status == True:
            if self.red_ratio_str.get() == '':
                self.red_ratio_str.set(self.cam_param_int[1])

            self.obj_cam_operation.red_ratio = self.entry_red_ratio.get()
            self.obj_cam_operation.Set_parameter_red_ratio(self.obj_cam_operation.red_ratio)

            if self.revert_val_red_ratio == False:
                self.cam_param_int[1] = self.obj_cam_operation.red_ratio
            elif self.revert_val_red_ratio == True:
                self.red_ratio_str.set(self.cam_param_int[1])
                self.revert_val_red_ratio = False

        else:
            self.red_ratio_str.set(self.cam_param_int[1])
            self.revert_val_red_ratio = False

    def set_parameter_green_ratio(self, event = None):
        if self.cam_conn_status == True:
            if self.green_ratio_str.get() == '':
                self.green_ratio_str.set(self.cam_param_int[2])

            self.obj_cam_operation.green_ratio = self.entry_green_ratio.get()
            self.obj_cam_operation.Set_parameter_green_ratio(self.obj_cam_operation.green_ratio)

            if self.revert_val_green_ratio == False:
                self.cam_param_int[2] = self.obj_cam_operation.green_ratio
            elif self.revert_val_green_ratio == True:
                self.green_ratio_str.set(self.cam_param_int[2])
                self.revert_val_green_ratio = False

        else:
            self.green_ratio_str.set(self.cam_param_int[2])
            self.revert_val_green_ratio = False

    def set_parameter_blue_ratio(self, event = None):
        if self.cam_conn_status == True:
            if self.blue_ratio_str.get() == '':
                self.blue_ratio_str.set(self.cam_param_int[3])

            self.obj_cam_operation.blue_ratio = self.entry_blue_ratio.get()
            self.obj_cam_operation.Set_parameter_blue_ratio(self.obj_cam_operation.blue_ratio)

            if self.revert_val_blue_ratio == False:
                self.cam_param_int[3] = self.obj_cam_operation.blue_ratio
            elif self.revert_val_blue_ratio == True:
                self.blue_ratio_str.set(self.cam_param_int[3])
                self.revert_val_blue_ratio = False

        else:
            self.blue_ratio_str.set(self.cam_param_int[3])
            self.revert_val_blue_ratio = False

    def set_parameter_black_lvl(self, event = None):
        if self.cam_conn_status == True:
            if self.black_lvl_str.get() == '':
                self.black_lvl_str.set(self.cam_param_int[4])
            self.obj_cam_operation.black_lvl = self.entry_black_lvl.get()
            self.obj_cam_operation.Set_parameter_black_lvl(self.obj_cam_operation.black_lvl)

            if self.revert_val_black_lvl == False:
                self.cam_param_int[4] = self.obj_cam_operation.black_lvl

            elif self.revert_val_black_lvl == True:
                self.black_lvl_str.set(self.cam_param_int[4])
                self.revert_val_black_lvl = False
        else:
            self.black_lvl_str.set(self.cam_param_int[4])
            self.revert_val_black_lvl = False

    def set_parameter_sharpness(self, event = None):
        if self.cam_conn_status == True:
            if self.sharpness_str.get() == '':
                self.sharpness_str.set(self.cam_param_int[5])
            self.obj_cam_operation.sharpness = self.entry_sharpness.get()
            self.obj_cam_operation.Set_parameter_sharpness(self.obj_cam_operation.sharpness)

            if self.revert_val_sharpness == False:
                self.cam_param_int[5] = self.obj_cam_operation.sharpness

            elif self.revert_val_sharpness == True:
                self.sharpness_str.set(self.cam_param_int[5])
                self.revert_val_sharpness = False
        else:
            self.sharpness_str.set(self.cam_param_int[5])
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
            # print('Auto White Stopped...')

    def enable_framerate(self,event = None):
        self.obj_cam_operation.Enable_Framerate()

    def enable_black_lvl(self, event = None):
        self.obj_cam_operation.Enable_Blacklevel()

    def enable_sharpness(self, event = None):
        self.obj_cam_operation.Enable_Sharpness()

    def get_pixel_format(self, hex_int):
        #print('get_pixel_format: ',hex_int)
        pixel_str_id = self.obj_cam_operation.Pixel_Format_Str_ID(hex_int)
        if isinstance(pixel_str_id, str) == True:
            self.pixel_format_combobox.current(self.pixel_format_list.index(pixel_str_id))

    def pixel_format_sel(self, event = None):
        hex_id = None
        if self.pixel_format_combobox.get() == "Mono 8":
            hex_id = 0x01080001
        elif self.pixel_format_combobox.get() == "Mono 10":
            hex_id = 0x01100003
        elif self.pixel_format_combobox.get() == "Mono 10 Packed":
            hex_id = 0x010C0004
        elif self.pixel_format_combobox.get() == "Mono 12":
            hex_id = 0x01100005
        elif self.pixel_format_combobox.get() == "Mono 12 Packed":
            hex_id = 0x010C0006
        elif self.pixel_format_combobox.get() == "RGB 8":
            hex_id = 0x02180014
        elif self.pixel_format_combobox.get() == "BGR 8":
            hex_id = 0x02180015
        elif self.pixel_format_combobox.get() == "YUV 422 (YUYV) Packed":
            hex_id = 0x02100032
        elif self.pixel_format_combobox.get() == "YUV 422 Packed":
            hex_id = 0x0210001F
        elif self.pixel_format_combobox.get() == "Bayer RG 8":
            hex_id = 0x01080009
        elif self.pixel_format_combobox.get() == "Bayer RG 10":
            hex_id = 0x0110000d
        elif self.pixel_format_combobox.get() == "Bayer RG 10 Packed":
            hex_id = 0x010C0027
        elif self.pixel_format_combobox.get() == "Bayer RG 12":
            hex_id = 0x01100011
        elif self.pixel_format_combobox.get() == "Bayer RG 12 Packed":
            hex_id = 0x010C002B

        if hex_id is not None:
            self.obj_cam_operation.Set_Pixel_Format(hex_id)
        pass
