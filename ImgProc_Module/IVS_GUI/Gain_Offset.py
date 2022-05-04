import tkinter as tk
from tkinter.font import Font

from Tk_MsgBox.custom_msgbox import Ask_Msgbox, Info_Msgbox, Error_Msgbox, Warning_Msgbox

from Tk_Custom_Widget.tk_custom_toplvl import CustomToplvl
from Tk_Custom_Widget.tk_custom_combobox import CustomBox
from Tk_Custom_Widget.ScrolledCanvas import ScrolledCanvas
from Tk_Custom_Widget.custom_zoom_class import CanvasImage

from misc_module.tool_tip import CreateToolTip
from misc_module.TMS_file_save import cv_img_save, pil_img_save, PDF_img_save, PDF_img_list_save, np_to_PIL
from misc_module.image_resize import img_resize_dim, opencv_img_resize, pil_img_resize, open_pil_img
from misc_module.tk_canvas_display import display_func, clear_display_func

from Tk_Validate.tk_validate import Validate_Int, Validate_Float, is_number, is_int, is_float, round_float

from PIL import Image, ImageTk
import os
from os import path

import pathlib

from functools import partial

from tkinter import filedialog
import numpy as np
import re

import cv2
from imageio import imread

import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from matplotlib.figure import Figure 
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def tk_widget_forget(*widgets):
    for widget in widgets:
        widget.place_forget()

def tk_dummmy_event(event):
    return "break"

class Gain_Offset(tk.Frame):
    def __init__(self, master, scroll_class, popout_icon = None, fit_to_display_icon = None, window_icon = None
        , img_icon = None
        , **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.img_format_list = [("All Files","*.bmp *.jpg *.jpeg *.png *.tiff"),
                                ('BMP file', '*.bmp'),
                                ('JPG file', '*.jpg'),
                                ('JPEG file', '*.jpeg'),
                                ('PNG file', '*.png'),
                               ('TIFF file', '*.tiff')]

        self.hist_x_index = []
        for i in range(256):
            self.hist_x_index.append(i)

        self.hist_scroll_class = None

        self.y1_fr = 100 +20
        self.y2_fr = 240 +20
        self.y3_fr = 380 +20

        self.popout_icon = popout_icon
        self.fit_to_display_icon = fit_to_display_icon
        self.window_icon = window_icon
        self.img_icon = None
        if isinstance(img_icon, Image.Image) == True:
            img_icon      = pil_img_resize(img_icon, img_width = 28, img_height = 28)
            self.img_icon = ImageTk.PhotoImage(img_icon)

        self.scroll_class = scroll_class
        #####################################################################################
        self.__gui_size_mode = 0 ##Mode: 0: default size, 1: large size
        #####################################################################################
        self.curr_graph_view = 'histogram' #'histogram', 'profile'
        self.curr_roi_mode = None

        self.__curr_popout_disp_sel = 'original' #'original', 'red, 'green', 'blue'
        self.__curr_disp_sel = None #'Show All', 'Original', 'Red Channel', 'Green Channel', 'Blue Channel'

        self.__disp_list = ['Show All', 'Original', 'Red Channel', 'Green Channel', 'Blue Channel']
        self.__disp_mode = self.__disp_list[0] #'Show All', 'Original', 'Red Channel', 'Green Channel', 'Blue Channel'

        self.__img_file = ''
        self.__img_type = '' #mono, rgb
        self.img_imageio = None

        self.img_load_status = False

        self.img_popout_disp = None

        self.__load_curr_dir = os.path.join(os.environ['USERPROFILE'],  "TMS_Saved_Images")
        self.__save_curr_dir = os.path.join(os.environ['USERPROFILE'],  "TMS_Saved_Images")

        disp_width = 1000
        disp_height = 560

        self.mini_width = int(round (np.divide(disp_width, 2)))
        self.mini_height = int(round (np.divide(disp_height,2)))

        self.disp_scroll_master = tk.Frame(self)
        self.disp_scroll_master['width'] = 500 + 15
        self.disp_scroll_master['height'] = disp_height + 50

        self.disp_scroll_class = ScrolledCanvas(self.disp_scroll_master, frame_w = 1, frame_h = 1
            , canvas_x = 0, canvas_y = 0)
        self.disp_scroll_class.show(scroll_x = False)

        self.disp_main_frame = self.disp_scroll_class.window_fr
        
        self.__kp_time = 0 ### Keypress time/duration
        self.__kp_event_id = None

        self.gui_init()

        self.popout_img_gen()
        self.graph_popout_gen()
        self.popout_btn_gen()
        
        self.gui_resize_func()

    def del_lead_zero(self, event, tk_sbox, only_positive = True):
        if only_positive == False:
            if str(event.char).isnumeric() == True or str(event.char) == '-':
                if str(tk_sbox.get()) == '0':
                    tk_sbox.selection_clear()
                    tk_sbox.focus_set()
                    tk_sbox.selection('range', 0, tk.END)
        else:
            if str(event.char).isnumeric() == True:
                if str(tk_sbox.get()) == '0':
                    tk_sbox.selection_clear()
                    tk_sbox.focus_set()
                    tk_sbox.selection('range', 0, tk.END)
    
    def link_tk_var(self, master_var, child_var):
        child_var.set(master_var.get())

    def tk_scl_event(self, event, ch_type):
        if ch_type == 'mono':
            self.contrast_mono()

        elif ch_type == 'red':
            self.contrast_R()

        elif ch_type == 'green':
            self.contrast_G()

        elif ch_type == 'blue':
            self.contrast_B()

    def tk_scl_release(self, event, ch_type):
        # print(event.type)
        if ch_type == 'red':
            self.popout_img_disp_func(self.__curr_popout_disp_sel)
            self.tk_plot_graph_R()

        elif ch_type == 'green':
            self.popout_img_disp_func(self.__curr_popout_disp_sel)
            self.tk_plot_graph_G()

        elif ch_type == 'blue':
            self.popout_img_disp_func(self.__curr_popout_disp_sel)
            self.tk_plot_graph_B()

        elif ch_type == 'mono':
            self.popout_img_disp_func(self.__curr_popout_disp_sel)
            self.tk_plot_graph_mono()


    def sbox_focusout_callback(self, event, tk_sbox, sbox_var, scl_var, ch_type = None):
        # print(event.type, tk_sbox)
        if False == is_number(tk_sbox.get()):
            tk_sbox.delete(0, "end")
            tk_sbox.insert(0, scl_var.get())
            tk_sbox.xview_moveto('1')
            tk_sbox.icursor(tk.END)

        elif True == is_number(tk_sbox.get()):
            if float(tk_sbox.get()) != float(scl_var.get()):
                scl_var.set(tk_sbox.get())
                self.tk_scl_event(event = None, ch_type = ch_type)
                self.tk_scl_release(event = None, ch_type = ch_type)

    def tk_sbox_release(self, event, tk_sbox, ch_type):
        # print(event.type, tk_sbox)
        # print("self.__kp_time: ", self.__kp_time)
        if self.__kp_event_id is not None:
            self.after_cancel(self.__kp_event_id)
            if self.__kp_time > 1:
                self.tk_scl_event(event = None, ch_type = ch_type)
                self.tk_scl_release(event = None, ch_type = ch_type)

        self.__kp_time = 0

    def tk_sbox_press(self, event, tk_sbox, ch_type):
        # print("self.__kp_time: ", self.__kp_time)
        self.__kp_time += 1
        if self.__kp_time <= 3: #increases speed if button has been hold for 0.75 seconds
            self.__kp_event_id = self.after(250, self.tk_sbox_press, None, tk_sbox, ch_type)
            # self.tk_scl_release(event = None, ch_type = ch_type)
        else:
            tk_sbox.config(repeatdelay=1, repeatinterval=40)
        

    def tk_sbox_int_event(self, event, tk_sbox, sbox_var, scl_var, ch_type = None):
        if event is None:
            self.focus_set()

        __err = False
        if True == is_int(sbox_var.get()) and True == is_int(scl_var.get()):
            """ If sbox_var and scl_var are int-types, then both lo_limit and hi_limit must be int-types aswell"""
            # print("sbox event: Int type")
            sbox_value = int(sbox_var.get())
            scl_value  = int(scl_var.get())
            __err = False
            if sbox_value != scl_value:
                scl_var.set(sbox_value)

            """ Gain/Offset Functions"""
            if self.__kp_time <= 3:
                self.tk_scl_event(event = None, ch_type = ch_type)
                self.tk_scl_release(event = None, ch_type = ch_type)

        else:
            __err = True
            sbox_var.set(scl_var.get())
            tk_sbox.xview_moveto('1')
            tk_sbox.icursor(tk.END)
            

    def tk_sbox_float_event(self, event, tk_sbox, sbox_var, scl_var, ch_type = None):
        if event is None:
            self.focus_set()

        __err = False
        if True == is_float(sbox_var.get()) and True == is_float(scl_var.get()):
            """ If sbox_var and scl_var are float-types, then both lo_limit and hi_limit must be float-types aswell"""
            # print("sbox event: Float type")
            sbox_value = float(sbox_var.get())
            scl_value  = float(scl_var.get())
            __err = False
            if sbox_value != scl_value:
                scl_var.set(sbox_value)

            ### Checking if the value is -0, we need to convert it back to 0
            check_value = float(scl_var.get())
            if check_value == 0:
                f = float(str(check_value).strip("-")) if "-" in str(check_value) else float(check_value)
                scl_var.set(int(f))
                sbox_var.set(int(f))
                tk_sbox.xview_moveto('1')
                tk_sbox.icursor(tk.END)

            """ Gain/Offset Functions"""
            if self.__kp_time <= 3:
                self.tk_scl_event(event = None, ch_type = ch_type)
                self.tk_scl_release(event = None, ch_type = ch_type)

        else:
            __err = True
            sbox_var.set(scl_var.get())
            tk_sbox.xview_moveto('1')
            tk_sbox.icursor(tk.END)
            

    def gain_panel_init(self, master, label_name, w, h, ch_type = None
        , gain_val = 1, offset_val = 0):
        frame = tk.Frame(master, width = w, height = h, highlightthickness = 1, highlightbackground = 'black')
        #frame.place(x=0,y=300)

        main_lb = tk.Label(frame, text = label_name, font = 'Helvetica 11').place(x=0 ,y=0)

        tk_lb_a = tk.Label(frame, text = 'Gain:', font = 'Helvetica 10', width = 8)
        tk_lb_b = tk.Label(frame, text = 'Offset:', font = 'Helvetica 10', width = 8)

        tk_var_scl_a = tk.StringVar(value = gain_val)
        tk_scl_a = tk.Scale(frame, from_= 0, to= 3, resolution = 0.01, length = 150, variable= tk_var_scl_a, orient='horizontal', showvalue=1)

        tk_var_sbox_a = tk.StringVar(value = gain_val)
        tk_sbox_a = tk.Spinbox(master = frame, width = 5, textvariable = tk_var_sbox_a, from_=0, to= 3, increment = 0.01
            , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')

        Validate_Float(tk_widget = tk_sbox_a, tk_var = tk_var_sbox_a, decimal_places = 2, only_positive = True, lo_limit = 0, hi_limit = 3)

        tk_var_scl_a.trace('w', lambda var_name, var_index, operation: self.link_tk_var(master_var = tk_var_scl_a, child_var = tk_var_sbox_a))
        tk_scl_a['command'] = partial(self.tk_scl_event, ch_type = ch_type)
        tk_scl_a.bind('<ButtonRelease-1>', partial(self.tk_scl_release, ch_type = ch_type))
        

        tk_sbox_a['command'] = partial(self.tk_sbox_float_event, event = None, tk_sbox = tk_sbox_a, sbox_var = tk_var_sbox_a, scl_var = tk_var_scl_a, ch_type = ch_type)
        tk_sbox_a.bind('<ButtonPress-1>', partial(self.tk_sbox_press, tk_sbox = tk_sbox_a, ch_type = ch_type))
        tk_sbox_a.bind('<ButtonRelease-1>', partial(self.tk_sbox_release, tk_sbox = tk_sbox_a, ch_type = ch_type))
        tk_sbox_a.bind('<Return>', partial(self.tk_sbox_float_event, tk_sbox = tk_sbox_a, sbox_var = tk_var_sbox_a, scl_var = tk_var_scl_a, ch_type = ch_type))
        tk_sbox_a.bind('<KeyPress>', partial(self.del_lead_zero, tk_sbox = tk_sbox_a, only_positive = True))
        tk_sbox_a.bind('<KeyPress-Up>', tk_dummmy_event)
        tk_sbox_a.bind('<KeyPress-Down>', tk_dummmy_event)
        tk_sbox_a.bind('<FocusOut>', partial(self.sbox_focusout_callback, tk_sbox = tk_sbox_a, sbox_var = tk_var_sbox_a, scl_var = tk_var_scl_a, ch_type = ch_type))

        
        tk_var_scl_b = tk.StringVar(value = offset_val)
        tk_scl_b = tk.Scale(frame, from_= -255, to= 255, resolution = 1, length = 150, variable= tk_var_scl_b, orient='horizontal', showvalue=1)

        tk_var_sbox_b = tk.StringVar(value = offset_val)
        tk_sbox_b = tk.Spinbox(master = frame, width = 5, textvariable = tk_var_sbox_b, from_=-255, to= 255, increment = 1
            , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')

        Validate_Int(tk_widget = tk_sbox_b, tk_var = tk_var_sbox_b, only_positive = False, lo_limit = -255, hi_limit = 255)

        tk_var_scl_b.trace('w', lambda var_name, var_index, operation: self.link_tk_var(master_var = tk_var_scl_b, child_var = tk_var_sbox_b))
        tk_scl_b['command'] = partial(self.tk_scl_event, ch_type = ch_type)
        tk_scl_b.bind('<ButtonRelease-1>', partial(self.tk_scl_release, ch_type = ch_type))


        tk_sbox_b['command'] = partial(self.tk_sbox_int_event, event = None, tk_sbox = tk_sbox_b, sbox_var = tk_var_sbox_b, scl_var = tk_var_scl_b, ch_type = ch_type)
        tk_sbox_b.bind('<ButtonPress-1>', partial(self.tk_sbox_press, tk_sbox = tk_sbox_b, ch_type = ch_type))
        tk_sbox_b.bind('<ButtonRelease-1>', partial(self.tk_sbox_release, tk_sbox = tk_sbox_b, ch_type = ch_type))
        tk_sbox_b.bind('<Return>', partial(self.tk_sbox_int_event, tk_sbox = tk_sbox_b, sbox_var = tk_var_sbox_b, scl_var = tk_var_scl_b, ch_type = ch_type))
        tk_sbox_b.bind('<KeyPress>', partial(self.del_lead_zero, tk_sbox = tk_sbox_b, only_positive = False))
        tk_sbox_b.bind('<KeyPress-Up>', tk_dummmy_event)
        tk_sbox_b.bind('<KeyPress-Down>', tk_dummmy_event)
        tk_sbox_b.bind('<FocusOut>', partial(self.sbox_focusout_callback, tk_sbox = tk_sbox_b, sbox_var = tk_var_sbox_b, scl_var = tk_var_scl_b, ch_type = ch_type))

        
        tk_lb_a.place(x=0 ,y= 49)
        tk_lb_b.place(x=0 ,y=94)

        tk_scl_a.place(x=75, y = 30, relwidth = 1, width = -75 - 80, anchor = 'nw')
        tk_sbox_a.place(x=-15, y = 47, relx = 1, anchor = 'ne')

        tk_scl_b.place(x=75, y = 75, relwidth = 1, width = -75 - 80, anchor = 'nw')
        tk_sbox_b.place(x=-15, y = 92, relx = 1, anchor = 'ne')

        return [frame
                , tk_var_scl_a, tk_var_scl_b
                , tk_scl_a, tk_scl_b
                , tk_var_sbox_a, tk_var_sbox_b
                , tk_sbox_a, tk_sbox_b]

    def gui_init(self):
        self.ori_display = tk.Canvas(self.disp_main_frame, width = self.mini_width, height = self.mini_height, bg = 'snow3', highlightthickness = 0)

        self.R_display = tk.Canvas(self.disp_main_frame, width = self.mini_width, height = self.mini_height, bg = 'red', highlightthickness = 0)

        self.G_display = tk.Canvas(self.disp_main_frame, width = self.mini_width, height = self.mini_height, bg = 'green', highlightthickness = 0)

        self.B_display = tk.Canvas(self.disp_main_frame, width = self.mini_width, height = self.mini_height, bg = 'blue', highlightthickness = 0)

        self.ori_display.bind('<Configure>', partial(self.disp_canvas_config, disp_type = 'original'))
        self.R_display.bind('<Configure>'  , partial(self.disp_canvas_config, disp_type = 'red'))
        self.G_display.bind('<Configure>'  , partial(self.disp_canvas_config, disp_type = 'green'))
        self.B_display.bind('<Configure>'  , partial(self.disp_canvas_config, disp_type = 'blue'))

        self.ori_disp_label = tk.Label(self.disp_main_frame, text = 'Original Image', font = 'Helvetica 12 bold', bg = 'snow3', fg = 'black')

        self.R_disp_label = tk.Label(self.disp_main_frame, text = 'Red Channel', font = 'Helvetica 12 bold', bg = 'red', fg = 'white')

        self.G_disp_label = tk.Label(self.disp_main_frame, text = 'Green Channel', font = 'Helvetica 12 bold', bg = 'green', fg = 'white')

        self.B_disp_label = tk.Label(self.disp_main_frame, text = 'Blue Channel', font = 'Helvetica 12 bold', bg = 'blue', fg = 'white')

        self.main_ctrl_fr = tk.LabelFrame(self, bg = 'SystemButtonFace'
            , text = 'Control Panel', font = 'Helvetica 12 bold', bd = 4)

        self.resolution = tk.StringVar()
        tk.Label(self.main_ctrl_fr, textvariable = self.resolution, font = 'Helvetica 10').place(x=0 ,y=40)

        self.load_img_button = tk.Button(self.main_ctrl_fr, relief = tk.GROOVE, text = 'Load Image', font= 'Helvetica 11')

        self.load_img_button['command'] = self.load_img
        self.load_img_button.place(x = 0, y = 5)

        self.save_button_1= tk.Button(self.main_ctrl_fr, relief = tk.GROOVE, text = 'Save Original Image', font= 'Helvetica 11')
        self.save_button_1['command'] = self.save_ori_img

        self.save_button_2= tk.Button(self.main_ctrl_fr, relief = tk.GROOVE, text = 'Save Red Channel Image', font= 'Helvetica 11')
        self.save_button_2['command'] = self.save_R_img

        self.save_button_3= tk.Button(self.main_ctrl_fr, relief = tk.GROOVE, text = 'Save Green Channel Image', font= 'Helvetica 11')
        self.save_button_3['command'] = self.save_G_img

        self.save_button_4= tk.Button(self.main_ctrl_fr, relief = tk.GROOVE, text = 'Save Blue Channel Image', font= 'Helvetica 11')
        self.save_button_4['command'] = self.save_B_img

        self.display_sel = CustomBox(self.main_ctrl_fr, width=13, state='readonly', font = 'Helvetica 12')
        self.display_sel.unbind_class("TCombobox", "<MouseWheel>")
        self.display_sel.place(x= 0, y = 70)

        widget_list = self.gain_panel_init(self.main_ctrl_fr, 'Monochrome', 270, 120, ch_type = 'mono')
        self.mono_gain_frame = widget_list[0]
        self.mono_var_alpha  = widget_list[1]
        self.mono_var_beta   = widget_list[2]

        widget_list = self.gain_panel_init(self.main_ctrl_fr, 'Red Channel', 270, 120, ch_type = 'red')
        self.R_gain_frame = widget_list[0]
        self.R_var_alpha  = widget_list[1]
        self.R_var_beta   = widget_list[2]
        self.R_sbox = widget_list[7]

        widget_list = self.gain_panel_init(self.main_ctrl_fr, 'Green Channel', 270, 120, ch_type = 'green')
        self.G_gain_frame = widget_list[0]
        self.G_var_alpha  = widget_list[1]
        self.G_var_beta   = widget_list[2]

        widget_list = self.gain_panel_init(self.main_ctrl_fr, 'Blue Channel', 270, 120, ch_type = 'blue')
        self.B_gain_frame = widget_list[0]
        self.B_var_alpha  = widget_list[1]
        self.B_var_beta   = widget_list[2]
        
        self.graph_btn = tk.Button(self.main_ctrl_fr, relief = tk.GROOVE, text = 'Pixel Count', font = 'Helvetica 11')
        self.graph_btn['command'] = self.graph_popout_open
        self.graph_btn['state'] = 'disabled'
        self.graph_btn.place(x=120, y = 5)

    def disp_canvas_config(self, event, disp_type):
        if disp_type == 'original':
            self.gui_disp_func(self.ori_display, self.img_imageio)
        elif disp_type == 'red':
            if (isinstance(self.img_imageio, np.ndarray)) == True and len(self.img_imageio.shape) == 3:
                self.gui_disp_func(self.R_display, self.img_imageio[:, :, 0])
        elif disp_type == 'green':
            if (isinstance(self.img_imageio, np.ndarray)) == True and len(self.img_imageio.shape) == 3:
                self.gui_disp_func(self.G_display, self.img_imageio[:, :, 1])
        elif disp_type == 'blue':
            if (isinstance(self.img_imageio, np.ndarray)) == True and len(self.img_imageio.shape) == 3:
                self.gui_disp_func(self.B_display, self.img_imageio[:, :, 2])

    def custom_scroll_inner_bound(self, event):
        self.disp_scroll_class.canvas.bind_all("<MouseWheel>", self.custom_inner_scrolly)

    # def custom_scroll_outer_bound(self, event):
    #     self.scroll_class.canvas.bind_all("<MouseWheel>", self.custom_outer_scrolly)

    def custom_inner_scrolly(self, event):
        if self.disp_scroll_class.scrolly_lock == False:
            y0_inner = float(self.disp_scroll_class.canvas.yview()[0])
            y1_inner = float(self.disp_scroll_class.canvas.yview()[1])
            self.disp_scroll_class.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            # print('custom_inner_scrolly: ',event.delta)
            # print(y0_inner, y1_inner)
            if 0 <= y1_inner < 1:
                if y0_inner == 0: #inner scroll: Start point
                    if event.delta > 0: #scroll up
                        self.scroll_class.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            elif y1_inner == 1:
                if 0<= y0_inner < 1: #inner scroll: End point
                    if event.delta < 0: #scroll down
                        self.scroll_class.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # def custom_outer_scrolly(self, event):
    #     if self.scroll_class.scrolly_lock == False:
    #         y0_outer = float(self.scroll_class.canvas.yview()[0])
    #         y1_outer = float(self.scroll_class.canvas.yview()[1])
    #         self.scroll_class.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    #         # print('custom_outer_scrolly: ',event.delta)
    #         # print(y0_outer, y1_outer)
    #         if 0 <= y1_outer < 1:
    #             if y0_outer == 0: #outer scroll: Start point
    #                 if event.delta > 0: #scroll up
    #                     self.disp_scroll_class.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    #         elif y1_outer == 1:
    #             if 0<= y0_outer < 1: #outer scroll: End point
    #                 if event.delta < 0: #scroll down
    #                     self.disp_scroll_class.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def gui_switch_protocol(self):
        ### Protocol for Gain/Offset Tool if user wants to switch from this tool to another.
        ret_err = 0 ### ret_err is the return value of this protocol. 0 means OK. Otherwise, prevent gui switch from happening in the ImgProc_GUI.
        self.gui_popout_close()

        return ret_err ### By default gui switching is allowed.

    def gui_popout_close(self):
        if isinstance(self.img_popout_toplvl, CustomToplvl) == True and isinstance(self.graph_popout_toplvl, CustomToplvl) == True:
            self.popout_img_close(reset = False) ##Close protocol for self.img_popout_toplvl; This will execute all condition(s) in this close protocol
            # self.img_popout_toplvl.close() ##Hide the window

            self.graph_popout_close() ##Close protocol for self.graph_popout_toplvl; This will execute all condition(s) in this close protocol
            # self.graph_popout_toplvl.close() ##Hide the window


    def gui_bbox_event(self, event):
        ## widget.place_info()## Retrieve all the place information of a widget (e.g. x, y, relx, rely, relwidth, relheight, etc.)
        if event.width < 1000:
            mode = 0
            if mode != self.__gui_size_mode:
                self.__gui_size_mode = 0
                self.gui_resize_func()

        elif 1000 <= event.width:
            mode = 1
            if mode != self.__gui_size_mode:
                self.__gui_size_mode = 1
                self.gui_resize_func()

    def gui_check_resize(self, tk_bbox):
        if tk_bbox.winfo_ismapped() == False:
            tk_bbox.update() ## Force update if widget.place() has already been applied but winfo_ismapped() never update its value even after .place() has been applied.
        
        # print(tk_bbox, tk_bbox.winfo_ismapped(), tk_bbox.winfo_width())
        if tk_bbox.winfo_ismapped() == True:
            if tk_bbox.winfo_width() < 1000:
                self.__gui_size_mode = 0
                self.gui_resize_func()
            elif 1000 <= tk_bbox.winfo_width():
                self.__gui_size_mode = 1
                self.gui_resize_func()


    def gui_resize_func(self):
        # print("Gain_Offset resize func")
        if self.__gui_size_mode == 0:
            self.scroll_class.resize_frame(width = 915, height = 800)
            self.disp_scroll_master['width'] = 518

            self.main_ctrl_fr['width'] = 350
            self.main_ctrl_fr.place_forget()
            self.main_ctrl_fr.place(relx = 0, x = 550, y = 0, relheight = 1, height = -10, anchor = 'nw')

            tk_widget_forget(self.ori_display, self.R_display, self.G_display, self.B_display)
            tk_widget_forget(self.ori_disp_label, self.R_disp_label, self.G_disp_label, self.B_disp_label)

            if self.__disp_mode == self.__disp_list[0]:
                self.disp_scroll_master.place_forget()
                self.disp_scroll_master.place(relx=0, x= 5, y=0, relheight = 1, height = -20, anchor = 'nw')

                self.disp_scroll_class.resize_frame(width = self.disp_scroll_master['width'], height = 1120 + 75 + 25)
                self.disp_scroll_class.show(scroll_x = False)
                self.img_popout_btn.place(relx = 1, x = -20, y= 0, anchor = 'ne')

                self.scroll_class.canvas.bind('<Enter>', self.scroll_class._bound_to_mousewheel)

                self.disp_scroll_class.canvas.bind('<Enter>', self.custom_scroll_inner_bound)
                self.disp_scroll_class.canvas.bind('<Leave>', self.scroll_class._bound_to_mousewheel)

                # print('self.__gui_size_mode, self.__disp_mode: ', self.__gui_size_mode, self.__disp_mode)

                self.ori_display['width'] = self.mini_width
                self.ori_display['height'] = self.mini_height

                self.R_display['width'] = self.mini_width
                self.R_display['height'] = self.mini_height

                self.G_display['width'] = self.mini_width
                self.G_display['height'] = self.mini_height

                self.B_display['width'] = self.mini_width
                self.B_display['height'] = self.mini_height
                

                self.ori_display.place(relx=0, y = 25)
                self.R_display.place(relx= 0, y = 25 + self.mini_height + 25)
                self.G_display.place(relx=0, y = 25 + self.mini_height + 25 + self.mini_height + 25)
                self.B_display.place(relx= 0 , y = 25 + self.mini_height + 25 + self.mini_height + 25 + self.mini_height + 25)

                self.ori_disp_label.place(relx=0, y = 0)
                self.R_disp_label.place(relx= 0, y = self.mini_height + 25)
                self.G_disp_label.place(relx=0, y = self.mini_height+25 + self.mini_height + 25)
                self.B_disp_label.place(relx=0, y = self.mini_height+25 + self.mini_height + 25 + self.mini_height + 25)

                self.gui_disp_func(self.ori_display, self.img_imageio, force_update = True)
                if (isinstance(self.img_imageio, np.ndarray)) == True and len(self.img_imageio.shape) == 3:
                    self.gui_disp_func(self.R_display, self.img_imageio[:, :, 0], force_update = True)
                    self.gui_disp_func(self.G_display, self.img_imageio[:, :, 1], force_update = True)
                    self.gui_disp_func(self.B_display, self.img_imageio[:, :, 2], force_update = True)

            elif self.__disp_mode == self.__disp_list[1]:
                self.disp_scroll_master.place_forget()
                self.disp_scroll_master.place(relx=0, x= 5, y=0, relheight = 0.5, height = -20, anchor = 'nw')

                self.disp_scroll_class.resize_frame(width = 500, height = 280+25)
                self.disp_scroll_class.scroll_reset()
                self.disp_scroll_class.show(scroll_x = False, scroll_y = False)
                self.img_popout_btn.place(relx = 1, x = -10, y= 0, anchor = 'ne')

                self.scroll_class.canvas.bind('<Enter>', self.scroll_class._bound_to_mousewheel)
                self.disp_scroll_class.canvas.bind('<Enter>', self.scroll_class._bound_to_mousewheel)
                self.disp_scroll_class.canvas.bind('<Leave>', self.scroll_class._bound_to_mousewheel)

                self.ori_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
                self.ori_display.place(x = 0, y = 25, relx = 0, rely = 0
                    , relwidth = 1, width = 0
                    , relheight = 1, height = -25
                    , anchor = 'nw')

                self.gui_disp_func(self.ori_display, self.img_imageio, force_update = True)
                clear_display_func(self.R_display,self.G_display, self.B_display)

            elif self.__disp_mode == self.__disp_list[2]:
                self.disp_scroll_master.place_forget()
                self.disp_scroll_master.place(relx=0, x= 5, y=0, relheight = 0.5, height = -20, anchor = 'nw')

                self.disp_scroll_class.resize_frame(width = 500, height = 280+25)
                self.disp_scroll_class.scroll_reset()
                self.disp_scroll_class.show(scroll_x = False, scroll_y = False)
                self.img_popout_btn.place(relx = 1, x = -10, y= 0, anchor = 'ne')

                self.scroll_class.canvas.bind('<Enter>', self.scroll_class._bound_to_mousewheel)
                self.disp_scroll_class.canvas.bind('<Enter>', self.scroll_class._bound_to_mousewheel)
                self.disp_scroll_class.canvas.bind('<Leave>', self.scroll_class._bound_to_mousewheel)

                self.R_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
                self.R_display.place(x = 0, y = 25, relx = 0, rely = 0
                    , relwidth = 1, width = 0
                    , relheight = 1, height = -25
                    , anchor = 'nw')

                if (isinstance(self.img_imageio, np.ndarray)) == True and len(self.img_imageio.shape) == 3:
                    self.gui_disp_func(self.R_display, self.img_imageio[:, :, 0], force_update = True)
                    clear_display_func(self.ori_display, self.G_display, self.B_display)

            elif self.__disp_mode == self.__disp_list[3]:
                self.disp_scroll_master.place_forget()
                self.disp_scroll_master.place(relx=0, x= 5, y=0, relheight = 0.5, height = -20, anchor = 'nw')

                self.disp_scroll_class.resize_frame(width = 500, height = 280+25)
                self.disp_scroll_class.scroll_reset()
                self.disp_scroll_class.show(scroll_x = False, scroll_y = False)
                self.img_popout_btn.place(relx = 1, x = -10, y= 0, anchor = 'ne')

                self.scroll_class.canvas.bind('<Enter>', self.scroll_class._bound_to_mousewheel)
                self.disp_scroll_class.canvas.bind('<Enter>', self.scroll_class._bound_to_mousewheel)
                self.disp_scroll_class.canvas.bind('<Leave>', self.scroll_class._bound_to_mousewheel)

                self.G_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
                self.G_display.place(x = 0, y = 25, relx = 0, rely = 0
                    , relwidth = 1, width = 0
                    , relheight = 1, height = -25
                    , anchor = 'nw')

                if (isinstance(self.img_imageio, np.ndarray)) == True and len(self.img_imageio.shape) == 3:
                    self.gui_disp_func(self.G_display, self.img_imageio[:, :, 1], force_update = True)
                    clear_display_func(self.ori_display, self.R_display, self.B_display)

            elif self.__disp_mode == self.__disp_list[4]:
                self.disp_scroll_master.place_forget()
                self.disp_scroll_master.place(relx=0, x= 5, y=0, relheight = 0.5, height = -20, anchor = 'nw')

                self.disp_scroll_class.resize_frame(width = 500, height = 280+25)
                self.disp_scroll_class.scroll_reset()
                self.disp_scroll_class.show(scroll_x = False, scroll_y = False)
                self.img_popout_btn.place(relx = 1, x = -10, y= 0, anchor = 'ne')

                self.scroll_class.canvas.bind('<Enter>', self.scroll_class._bound_to_mousewheel)
                self.disp_scroll_class.canvas.bind('<Enter>', self.scroll_class._bound_to_mousewheel)
                self.disp_scroll_class.canvas.bind('<Leave>', self.scroll_class._bound_to_mousewheel)

                self.B_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
                self.B_display.place(x = 0, y = 25, relx = 0, rely = 0
                    , relwidth = 1, width = 0
                    , relheight = 1, height = -25
                    , anchor = 'nw')

                if (isinstance(self.img_imageio, np.ndarray)) == True and len(self.img_imageio.shape) == 3:
                    self.gui_disp_func(self.B_display, self.img_imageio[:, :, 2], force_update = True)
                    clear_display_func(self.ori_display, self.R_display, self.G_display)

        elif self.__gui_size_mode == 1:
            self.scroll_class.resize_frame(width = 1340, height = 850)
            self.disp_scroll_master['width'] = 1340 - (350+15) - (5+32) ### 1st bracket: region allocated to self.main_ctrl_fr, 2nd bracket: region allocated between self.disp_scroll_master & self.main_ctrl_fr
            self.disp_scroll_master['height'] = 560 + 25 + 25
            self.disp_scroll_class.resize_frame(width = self.disp_scroll_master['width'], height = self.disp_scroll_master['height'])
            self.disp_scroll_class.scroll_reset()
            self.disp_scroll_class.show(scroll_x = False, scroll_y = False)
            self.scroll_class.canvas.bind('<Enter>', self.scroll_class._bound_to_mousewheel)

            self.disp_scroll_class.canvas.bind('<Enter>', self.scroll_class._bound_to_mousewheel)
            self.disp_scroll_class.canvas.bind('<Leave>', self.scroll_class._bound_to_mousewheel)

            self.main_ctrl_fr['width'] = 350
            self.main_ctrl_fr.place_forget()
            self.main_ctrl_fr.place(relx=1, x = -15, y = 0, relheight = 1, height = -10, anchor = 'ne')

            self.disp_scroll_master.place_forget()
            self.disp_scroll_master.place(relx=0, x= 5, y=0, relheight = 1, height = -20, width = - (5+32) - (self.main_ctrl_fr['width']+15), relwidth = 1, anchor = 'nw')

            self.img_popout_btn.place(relx = 1, x = -5, y= 0, anchor = 'ne')

            tk_widget_forget(self.ori_display, self.R_display, self.G_display, self.B_display)
            tk_widget_forget(self.ori_disp_label, self.R_disp_label, self.G_disp_label, self.B_disp_label)

            if self.__disp_mode == self.__disp_list[0]:
                self.ori_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
                self.R_disp_label.place(x = 2, y = 0, relx = 0.5, rely = 0, anchor = 'nw')
                self.G_disp_label.place(x = 0, y = 0, relx = 0, rely = 0.5, anchor = 'nw')
                self.B_disp_label.place(x = 2, y = 0, relx = 0.5, rely = 0.5, anchor = 'nw')

                self.ori_display.place(x = 0, y = 25, relx = 0, rely = 0
                    , relwidth = 0.5, width = -2
                    , relheight = 0.5, height = -25
                    , anchor = 'nw')
                self.R_display.place(x = 2, y = 25, relx = 0.5, rely = 0
                    , relwidth = 0.5, width = -2
                    , relheight = 0.5, height = -25
                    , anchor = 'nw')
                self.G_display.place(x = 0, y = 25, relx = 0, rely = 0.5
                    , relwidth = 0.5, width = -2
                    , relheight = 0.5, height = -25
                    , anchor = 'nw')
                self.B_display.place(x = 2, y = 25, relx = 0.5, rely = 0.5
                    , relwidth = 0.5, width = -2
                    , relheight = 0.5, height = -25
                    , anchor = 'nw')

                self.gui_disp_func(self.ori_display, self.img_imageio, force_update = True)
                if (isinstance(self.img_imageio, np.ndarray)) == True and len(self.img_imageio.shape) == 3:
                    self.gui_disp_func(self.R_display, self.img_imageio[:, :, 0], force_update = True)
                    self.gui_disp_func(self.G_display, self.img_imageio[:, :, 1], force_update = True)
                    self.gui_disp_func(self.B_display, self.img_imageio[:, :, 2], force_update = True)

            elif self.__disp_mode == self.__disp_list[1]:
                self.ori_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
                self.ori_display.place(x = 0, y = 25, relx = 0, rely = 0
                    , relwidth = 1, width = 0
                    , relheight = 1, height = -25
                    , anchor = 'nw')

                self.gui_disp_func(self.ori_display, self.img_imageio, force_update = True)
                clear_display_func(self.R_display, self.G_display, self.B_display)

            elif self.__disp_mode == self.__disp_list[2]:
                self.R_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
                self.R_display.place(x = 0, y = 25, relx = 0, rely = 0
                    , relwidth = 1, width = 0
                    , relheight = 1, height = -25
                    , anchor = 'nw')

                if (isinstance(self.img_imageio, np.ndarray)) == True and len(self.img_imageio.shape) == 3:
                    self.gui_disp_func(self.R_display, self.img_imageio[:, :, 0], force_update = True)
                    clear_display_func(self.ori_display, self.G_display, self.B_display)

            elif self.__disp_mode == self.__disp_list[3]:
                self.G_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
                self.G_display.place(x = 0, y = 25, relx = 0, rely = 0
                    , relwidth = 1, width = 0
                    , relheight = 1, height = -25
                    , anchor = 'nw')

                if (isinstance(self.img_imageio, np.ndarray)) == True and len(self.img_imageio.shape) == 3:
                    self.gui_disp_func(self.G_display, self.img_imageio[:, :, 1], force_update = True)
                    clear_display_func(self.ori_display, self.R_display, self.B_display)

            elif self.__disp_mode == self.__disp_list[4]:
                self.B_disp_label.place(x = 0, y = 0, relx = 0, rely = 0, anchor = 'nw')
                self.B_display.place(x = 0, y = 25, relx = 0, rely = 0
                    , relwidth = 1, width = 0
                    , relheight = 1, height = -25
                    , anchor = 'nw')

                if (isinstance(self.img_imageio, np.ndarray)) == True and len(self.img_imageio.shape) == 3:
                    self.gui_disp_func(self.B_display, self.img_imageio[:, :, 2], force_update = True)
                    clear_display_func(self.ori_display, self.R_display, self.G_display)

    def gui_disp_func(self, display, img, *disp_args, **disp_kwargs):
        if (isinstance(img, np.ndarray)) == True:
            display_func(display, img, tag = 'img', *disp_args, **disp_kwargs)


    def popout_btn_gen(self):
        self.img_popout_btn = tk.Button(self.disp_main_frame, relief = tk.GROOVE, bd =0 , image = self.popout_icon)
        CreateToolTip(self.img_popout_btn, 'Gain/Offset Popout Display'
            , 5, -25, font = 'Tahoma 11')
        self.img_popout_btn['command'] = self.popout_img_open

        self.img_popout_btn['state'] = 'disabled'

    def popout_img_gen(self):
        self.img_popout_toplvl = CustomToplvl(self, toplvl_title = 'Gain/Offset Tool', min_w = 750, min_h = 600
            , icon_img = self.window_icon
            , bg = 'white'
            , topmost_bool = True
            , width = 750, height = 600)

        self.img_popout_toplvl.protocol("WM_DELETE_WINDOW", partial(self.popout_img_close, reset = False))
        self.popout_img_init()

    def popout_img_open(self):
        if False == self.img_popout_toplvl.check_open():
            _toplvl = self.img_popout_toplvl
            _toplvl_W = 750
            _toplvl_H = 600
            _toplvl.minsize(width = _toplvl_W, height = _toplvl_H)
            screen_width = _toplvl.winfo_screenwidth()
            screen_height = _toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (_toplvl_W/2))
            y_coordinate = int((screen_height/2) - (_toplvl_H/2))
            _toplvl.geometry("{}x{}+{}+{}".format(_toplvl_W, _toplvl_H, x_coordinate, y_coordinate))

            _toplvl.open()
            self.img_popout_disp.canvas_default_load(img = self.img_imageio)
                # , fit_to_display_bool = True
                # , display_width = self.img_popout_disp.imframe.winfo_width()
                # , display_height = self.img_popout_disp.imframe.winfo_height())
            
            self.sel_ori_btn.invoke()
            
            self.img_popout_disp.fit_to_display(disp_W = _toplvl_W, disp_H = _toplvl_H - 60)

            if True == self.graph_popout_toplvl.check_open():
                if self.__img_type == 'mono':
                    self.tk_plot_graph_mono()
                else:
                    self.tk_plot_graph_R()
                    self.tk_plot_graph_G()
                    self.tk_plot_graph_B()

                if self.roi_status_var.get() ==1 and self.roi_type_combobox.get() == self.roi_type_list[1]:
                    self.profile_view_btn['state'] = 'normal'
                else:
                    self.profile_view_btn['state'] = 'disable'

            if self.__img_type == 'mono':
                self.sel_R_btn['state'] = 'disable'
                self.sel_G_btn['state'] = 'disable'
                self.sel_B_btn['state'] = 'disable'
            else:
                self.sel_R_btn['state'] = 'normal'
                self.sel_G_btn['state'] = 'normal'
                self.sel_B_btn['state'] = 'normal'

        else:
            self.img_popout_toplvl.show()

    def popout_img_close(self, reset = False):
        if reset == True:
            ### Reset ROI status & widget(s)
            self.curr_roi_mode = None
            self.roi_status_var.set(0)
            self.roi_type_combobox.current(0)
            self.roi_type_combobox['state'] = 'disable'

            ### Reset Custom Zoom Img Display & ROI status
            self.img_popout_disp.ROI_disable()
            self.img_popout_disp.canvas_clear(init = True)

            self.img_popout_toplvl.close()

        else:
            self.img_popout_toplvl.close()

            if True == self.graph_popout_toplvl.check_open():
                self.tk_plot_graph_default()
                self.hist_view_btn.invoke()
                self.profile_view_btn['state'] = 'disable'
        
    def popout_img_init(self):
        # self.img_popout_disp = CanvasImage(self.img_popout_toplvl, loaded_img = self.img_imageio)
        # self.img_popout_disp.fit_to_display(self.img_popout_toplvl.winfo_width(),self.img_popout_toplvl.winfo_height()-60) #Fit to Screen Display

        self.img_popout_disp = CanvasImage(self.img_popout_toplvl)
        self.img_popout_disp.place(x=0, y = 60, relwidth = 1, relheight = 1, height = -60, anchor = 'nw')

        self.roi_status_var = tk.IntVar()
        self.roi_checkbtn = tk.Checkbutton(self.img_popout_toplvl, text='ROI Enable', variable = self.roi_status_var, onvalue=1, offvalue=0, highlightthickness = 0, bg = 'white')
        self.roi_checkbtn['command'] = self.roi_checkbtn_click
        self.roi_checkbtn.place(x=10,y=30)

        self.roi_type_list = ['BOX', 'LINE']
        self.roi_type_combobox = CustomBox(self.img_popout_toplvl, values=self.roi_type_list, width=10, state='readonly', font = 'Helvetica 10')
        self.roi_type_combobox.unbind_class("TCombobox", "<MouseWheel>")
        self.roi_type_combobox.bind('<<ComboboxSelected>>', self.roi_type_sel)
        self.roi_type_combobox.current(0)
        self.roi_type_combobox['state'] = 'disable'
        self.roi_type_combobox.place(x=100, y=32)

        self.pixel_count_ori_btn = tk.Button(self.img_popout_toplvl, text = 'Pixel Count', relief = tk.GROOVE, font = 'Helvetica 10')
        self.pixel_count_ori_btn['command'] = self.graph_popout_open
        self.pixel_count_ori_btn.place(x=200, y=0+30)

        self.fit_to_display_btn = tk.Button(self.img_popout_toplvl, relief = tk.GROOVE, image = self.fit_to_display_icon, bd = 0)
        self.fit_to_display_btn['command'] = lambda: self.img_popout_disp.fit_to_display(disp_W = self.img_popout_disp.imframe.winfo_width(), disp_H = self.img_popout_disp.imframe.winfo_height())
        CreateToolTip(self.fit_to_display_btn, 'Fit-to-Screen'
            , 30, 0, font = 'Tahoma 11')
        self.fit_to_display_btn.place(x=300, y=0+32)

        self.sel_ori_btn = tk.Button(self.img_popout_toplvl, relief = tk.GROOVE, text = 'Original', font = 'Helvetica 10')
        self.sel_R_btn = tk.Button(self.img_popout_toplvl, relief = tk.GROOVE, text = 'Red Channel', font = 'Helvetica 10')
        self.sel_G_btn = tk.Button(self.img_popout_toplvl, relief = tk.GROOVE, text = 'Green Channel', font = 'Helvetica 10')
        self.sel_B_btn = tk.Button(self.img_popout_toplvl, relief = tk.GROOVE, text = 'Blue Channel', font = 'Helvetica 10')

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

    def roi_checkbtn_click(self):
        if self.roi_status_var.get() == 0:
            self.roi_type_combobox['state'] = 'disable'
            self.img_popout_disp.ROI_disable()
            self.prof_clear_all()
            self.tk_plot_graph_default()
            self.curr_roi_mode = None

            self.graph_view_sel('histogram', self.hist_view_btn, self.profile_view_btn)
            self.profile_view_btn['state'] = 'disable'

        elif self.roi_status_var.get() == 1:
            self.roi_type_combobox['state'] = 'readonly'
            self.roi_type_sel()

            self.graph_view_sel('histogram', self.hist_view_btn, self.profile_view_btn)

    def roi_type_sel(self,event = None):
        if self.roi_type_combobox.get() == 'BOX':
            if self.roi_type_combobox.get() != self.curr_roi_mode:
                self.curr_roi_mode = self.roi_type_combobox.get()

                func_list = []
                if self.__img_type == 'mono':
                    func_list = [self.tk_plot_graph_mono]
                else:
                    func_list = [self.tk_plot_graph_R, self.tk_plot_graph_G, self.tk_plot_graph_B]

                _enable_status = self.img_popout_disp.ROI_box_enable('Gain', func_list = func_list)
                # print('_enable_status: ', _enable_status)
                if _enable_status == True:
                    self.hist_clear_all()
                    self.prof_clear_all()

                    self.graph_view_sel('histogram', self.hist_view_btn, self.profile_view_btn)
                    self.profile_view_btn['state'] = 'disable'

                elif _enable_status == False:
                    self.curr_roi_mode = None
                    self.roi_status_var.set(0)
                    self.roi_type_combobox['state'] = 'disable'

        elif self.roi_type_combobox.get() == 'LINE':
            if self.roi_type_combobox.get() != self.curr_roi_mode:
                self.curr_roi_mode = self.roi_type_combobox.get()

                func_list = []
                if self.__img_type == 'mono':
                    func_list = [self.tk_plot_graph_mono]
                else:
                    func_list = [self.tk_plot_graph_R, self.tk_plot_graph_G, self.tk_plot_graph_B]

                _enable_status = self.img_popout_disp.ROI_line_enable('Gain', func_list = func_list)
                # print('_enable_status: ', _enable_status)
                if _enable_status == True:
                    self.hist_clear_all()
                    self.prof_clear_all()

                    self.profile_view_btn['state'] = 'normal'

                elif _enable_status == False:
                    self.curr_roi_mode = None
                    self.roi_status_var.set(0)
                    self.roi_type_combobox['state'] = 'disable'
                    
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

        self.__curr_popout_disp_sel = str_mode
        if self.img_load_status == True:
            self.popout_img_disp_func(self.__curr_popout_disp_sel)

    def popout_img_disp_func(self, str_mode):
        if True == self.img_popout_toplvl.check_open():
            if str_mode == 'original':
                self.img_popout_disp.canvas_reload(img = self.img_imageio)

            elif str_mode == 'red':
                self.img_popout_disp.canvas_reload(img = self.img_imageio, local_img_split = True, ch_index = 0)

            elif str_mode == 'green':
                self.img_popout_disp.canvas_reload(img = self.img_imageio, local_img_split = True, ch_index = 1)

            elif str_mode == 'blue':
                self.img_popout_disp.canvas_reload(img = self.img_imageio, local_img_split = True, ch_index = 2)

    def reset_gain_param(self):
        self.mono_var_alpha.set(float(1))
        self.R_var_alpha.set(float(1))
        self.G_var_alpha.set(float(1))
        self.B_var_alpha.set(float(1))

        self.mono_var_beta.set(int(0))
        self.R_var_beta.set(int(0))
        self.G_var_beta.set(int(0))
        self.B_var_beta.set(int(0))

    def graph_popout_gen(self):
        self.graph_popout_toplvl = CustomToplvl(self, toplvl_title = 'Pixel Count: Gain/Offset Tool', min_w = 700, min_h = 600
            , icon_img = self.window_icon
            , bg = 'white'
            , topmost_bool = True
            , width = 700, height = 600)

        self.graph_display_init()

        self.graph_popout_toplvl.protocol("WM_DELETE_WINDOW", self.graph_popout_close)
        
    def graph_popout_open(self):
        if False == self.graph_popout_toplvl.check_open():
            _toplvl = self.graph_popout_toplvl
            screen_width = _toplvl.winfo_screenwidth()
            screen_height = _toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (_toplvl.winfo_width()/2))
            y_coordinate = int((screen_height/2) - (_toplvl.winfo_height()/2))
            _toplvl.geometry("{}x{}+{}+{}".format(_toplvl.winfo_width(), _toplvl.winfo_height(), x_coordinate, y_coordinate))

            _toplvl.open()

            if self.__img_type == 'mono':
                self.hist_scroll_class.resize_frame(height = 800)
                self.hist_cvs_place(self.canvas_fr_hist_mono)
                self.hist_tbar_place(self.toolbar_fr_hist_mono)

                self.profile_scroll_class.resize_frame(height = 800)
                self.prof_cvs_place(self.canvas_fr_profile_mono)
                self.prof_tbar_place(self.toolbar_fr_profile_mono)

                self.tk_plot_graph_mono()

            else:
                self.hist_scroll_class.resize_frame(height = 2300)
                self.hist_cvs_place(self.canvas_fr_hist_R, self.canvas_fr_hist_G, self.canvas_fr_hist_B)
                self.hist_tbar_place(self.toolbar_fr_hist_R, self.toolbar_fr_hist_G, self.toolbar_fr_hist_B)
                
                self.profile_scroll_class.resize_frame(height = 2300)
                self.prof_cvs_place(self.canvas_fr_profile_R, self.canvas_fr_profile_G, self.canvas_fr_profile_B)
                self.prof_tbar_place(self.toolbar_fr_profile_R, self.toolbar_fr_profile_G, self.toolbar_fr_profile_B)

                self.tk_plot_graph_R()
                self.tk_plot_graph_G()
                self.tk_plot_graph_B()
            
            self.hist_view_btn.invoke()

            #CHECKING THE PROFILE VIEW BUTTON STATUS     
            if self.roi_status_var.get() ==1 and self.roi_type_combobox.get() == self.roi_type_list[1]:
                self.profile_view_btn['state'] = 'normal'
            else:
                self.profile_view_btn['state'] = 'disable'
        else:
            self.graph_popout_toplvl.show()

    def graph_popout_close(self):
        self.graph_popout_toplvl.close()
        self.hist_clear_all()
        self.prof_clear_all()

    def graph_display_init(self):
        self.hist_scroll_class = ScrolledCanvas(master = self.graph_popout_toplvl, frame_w = 700, frame_h = 2300, 
            canvas_x = 0, canvas_y = 0 + 30, bg = 'white')

        self.profile_scroll_class = ScrolledCanvas(master = self.graph_popout_toplvl, frame_w = 700, frame_h = 2300, 
            canvas_x = 0, canvas_y = 0 + 30, bg = 'white')

        self.hist_view_btn = tk.Button(self.graph_popout_toplvl, relief = tk.GROOVE, text = 'Histogram', font = 'Helvetica 10', width = 12)
        self.hist_view_btn['command'] = lambda: self.graph_view_sel('histogram', self.hist_view_btn, self.profile_view_btn)
        self.hist_view_btn.place(x = 0, y = 4)

        self.profile_view_btn = tk.Button(self.graph_popout_toplvl, relief = tk.GROOVE, text = 'Profile', font = 'Helvetica 10', width = 12)
        self.profile_view_btn['command'] = lambda: self.graph_view_sel('profile', self.profile_view_btn, self.hist_view_btn)
        self.profile_view_btn.place(x = 115, y = 4)

        img_disp_btn = tk.Button(self.graph_popout_toplvl, relief = tk.GROOVE, image = self.img_icon)
        img_disp_btn['bg'] = 'snow4'
        img_disp_btn['activebackground'] = 'black'
        img_disp_btn['command'] = self.popout_img_open
        CreateToolTip(img_disp_btn, 'Gain/Offset Popout Display'
            , 40, 0, font = 'Tahoma 11')
        img_disp_btn.place(x = 230, y = 0)

        self.hist_display_init()

        self.profile_display_init()


    def graph_view_sel(self, str_mode, master_btn, *arg_btn):
        if str_mode == 'histogram':
            self.profile_scroll_class.hide()
            self.hist_scroll_class.show()

        elif str_mode == 'profile':
            self.profile_scroll_class.show()
            self.hist_scroll_class.hide()

        self.curr_graph_view = str_mode

        master_btn['bg'] = 'snow4'
        master_btn['fg'] = 'white'
        master_btn['font'] = 'Helvetica 10 bold'
        for btn in arg_btn:
            btn['bg'] = 'SystemButtonFace'
            btn['fg'] = 'black'
            btn['font'] = 'Helvetica 10'

    def hist_display_init(self):
        self.hist_fig_mono = Figure(figsize = (7,7))

        self.plot_hist_mono = self.hist_fig_mono.add_subplot(111)
        # self.plot_hist_mono.clear()
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
        """<------------------------------------------------------------------------------------------------------------------------->"""
        self.hist_fig_R = Figure(figsize = (7,7))
        self.plot_hist_R = self.hist_fig_R.add_subplot(111)
        # self.plot_hist_R.clear()
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

        """<------------------------------------------------------------------------------------------------------------------------->"""
        self.hist_fig_G = Figure(figsize = (7,7))
        self.plot_hist_G = self.hist_fig_G.add_subplot(111)
        # self.plot_hist_G.clear()
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

        """<------------------------------------------------------------------------------------------------------------------------->"""
        self.hist_fig_B = Figure(figsize = (7,7))
        self.plot_hist_B = self.hist_fig_B.add_subplot(111)
        # self.plot_hist_B.clear()
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

        """<------------------------------------------------------------------------------------------------------------------------->"""
        ### Created a custom place_info dictionary with custom place & place_forget functions. Because winfo_mapped() is so unreliable.
        ### So we place all the widgets to save the place_info data.
        self.canvas_fr_hist_mono.place(x = 0, y = 0, relwidth = 1)
        self.canvas_fr_hist_R.place(x = 0, y = 0, relwidth = 1)
        self.canvas_fr_hist_G.place(x = 0, y = 750, relwidth = 1)
        self.canvas_fr_hist_B.place(x = 0, y = 1500, relwidth = 1)

        self.toolbar_fr_hist_mono.place(relx = 0.1, y = 700, relwidth = 0.8)
        self.toolbar_fr_hist_R.place(relx = 0.1, y = 700, relwidth = 0.8)
        self.toolbar_fr_hist_G.place(relx = 0.1, y = 1450, relwidth = 0.8)
        self.toolbar_fr_hist_B.place(relx = 0.1, y = 2200, relwidth = 0.8)

        self.__hist_cvs_fr_info = {}
        self.__hist_cvs_fr_info[self.canvas_fr_hist_R]    = [self.canvas_fr_hist_R.place_info(), True]
        self.__hist_cvs_fr_info[self.canvas_fr_hist_G]    = [self.canvas_fr_hist_G.place_info(), True]
        self.__hist_cvs_fr_info[self.canvas_fr_hist_B]    = [self.canvas_fr_hist_B.place_info(), True]
        self.__hist_cvs_fr_info[self.canvas_fr_hist_mono] = [self.canvas_fr_hist_mono.place_info(), True]

        self.__hist_tbar_fr_info = {}
        self.__hist_tbar_fr_info[self.toolbar_fr_hist_R]    = [self.toolbar_fr_hist_R.place_info(), True]
        self.__hist_tbar_fr_info[self.toolbar_fr_hist_G]    = [self.toolbar_fr_hist_G.place_info(), True]
        self.__hist_tbar_fr_info[self.toolbar_fr_hist_B]    = [self.toolbar_fr_hist_B.place_info(), True]
        self.__hist_tbar_fr_info[self.toolbar_fr_hist_mono] = [self.toolbar_fr_hist_mono.place_info(), True]

        self.hist_clear_all() ### we hide all the widgets

    def hist_cvs_place(self, *cvs_args):
        for wid in cvs_args:
            if wid in self.__hist_cvs_fr_info:
                wid.place(self.__hist_cvs_fr_info[wid][0])
                self.__hist_cvs_fr_info[wid][1] = True

            else:
                raise Exception('Tkinter widget: {} '.format(wid) + 'does not exists, cannot place()!' 
                    + 'Please make sure the tk widget has been placed with its place_info updated in ( hist_cvs_fr_info ).')

    def hist_tbar_place(self, *tbar_args):
        for wid in tbar_args:
            if wid in self.__hist_tbar_fr_info:
                wid.place(self.__hist_tbar_fr_info[wid][0])
                self.__hist_tbar_fr_info[wid][1] = True

            else:
                raise Exception('Tkinter widget: {} '.format(wid) + 'does not exists, cannot place()!' 
                    + 'Please make sure the tk widget has been placed with its place_info updated in ( hist_tbar_fr_info ).')


    def hist_cvs_forget(self, *cvs_args):
        for wid in cvs_args:
            if wid in self.__hist_cvs_fr_info:
                wid.place_forget()
                self.__hist_cvs_fr_info[wid][1] = False

            else:
                raise Exception('Tkinter widget: {} '.format(wid) + 'does not exists, cannot place_forget()!' 
                    + 'Please make sure the tk widget has been placed with its place_info updated in ( hist_cvs_fr_info ).')

    def hist_tbar_forget(self, *tbar_args):
        for wid in tbar_args:
            if wid in self.__hist_tbar_fr_info:
                wid.place_forget()
                self.__hist_tbar_fr_info[wid][1] = True

            else:
                raise Exception('Tkinter widget: {} '.format(wid) + 'does not exists, cannot place_forget()!' 
                    + 'Please make sure the tk widget has been placed with its place_info updated in ( hist_tbar_fr_info ).')

    def hist_clear_all(self):
        for tk_obj, plc_info in self.__hist_cvs_fr_info.items():
            tk_obj.place_forget()
            self.__hist_cvs_fr_info[tk_obj][1] = False

        for tk_obj, plc_info in self.__hist_tbar_fr_info.items():
            tk_obj.place_forget()
            self.__hist_tbar_fr_info[tk_obj][1] = False
    

    def profile_display_init(self):
        self.profile_fig_mono = Figure(figsize = (7,7))
        self.plot_profile_mono = self.profile_fig_mono.add_subplot(111)
        self.profile_fig_mono.suptitle('Monochrome', fontsize=18)
        self.plot_profile_mono.set_ylabel('Pixel Count', fontsize=16)

        self.canvas_fr_profile_mono = tk.Frame(self.profile_scroll_class.window_fr, height = 800 - 100, bg = 'white')

        self.profile_canvas_mono = FigureCanvasTkAgg(self.profile_fig_mono, master = self.canvas_fr_profile_mono)
        self.profile_canvas_mono.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_profile_mono = tk.Frame(self.profile_scroll_class.window_fr, height = 35, bg = 'white')
        self.toolbar_profile_mono = tkagg.NavigationToolbar2Tk(self.profile_canvas_mono, self.toolbar_fr_profile_mono)
        self.toolbar_profile_mono.update_idletasks()

        self.ax_plt_profile_mono = self.plot_profile_mono.plot([], [], color="grey")

        """<------------------------------------------------------------------------------------------------------------------------->"""
        self.profile_fig_R = Figure(figsize = (7,7))
        self.plot_profile_R = self.profile_fig_R.add_subplot(111)
        self.profile_fig_R.suptitle('Red Channel', fontsize=18)
        self.plot_profile_R.set_ylabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_profile_R = tk.Frame(self.profile_scroll_class.window_fr, height = 800 - 100, bg = 'white')

        self.profile_canvas_R = FigureCanvasTkAgg(self.profile_fig_R, master = self.canvas_fr_profile_R)
        self.profile_canvas_R.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_profile_R = tk.Frame(self.profile_scroll_class.window_fr, height = 35, bg = 'white')
        self.toolbar_profile_R = tkagg.NavigationToolbar2Tk(self.profile_canvas_R, self.toolbar_fr_profile_R)
        self.toolbar_profile_R.update_idletasks()

        self.ax_plt_profile_R = self.plot_profile_R.plot([], [], color="red")

        """<------------------------------------------------------------------------------------------------------------------------->"""
        self.profile_fig_G = Figure(figsize = (7,7))
        self.plot_profile_G = self.profile_fig_G.add_subplot(111)
        self.profile_fig_G.suptitle('Green Channel', fontsize=18)
        self.plot_profile_G.set_ylabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_profile_G = tk.Frame(self.profile_scroll_class.window_fr, height = 800 - 100, bg = 'white')

        self.profile_canvas_G = FigureCanvasTkAgg(self.profile_fig_G, master = self.canvas_fr_profile_G)
        self.profile_canvas_G.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_profile_G = tk.Frame(self.profile_scroll_class.window_fr, height = 35, bg = 'white')
        self.toolbar_profile_G = tkagg.NavigationToolbar2Tk(self.profile_canvas_G, self.toolbar_fr_profile_G)
        self.toolbar_profile_G.update_idletasks()

        self.ax_plt_profile_G = self.plot_profile_G.plot([], [], color="green")

        """<------------------------------------------------------------------------------------------------------------------------->"""
        self.profile_fig_B = Figure(figsize = (7,7))
        self.plot_profile_B = self.profile_fig_B.add_subplot(111)
        self.profile_fig_B.suptitle('Blue Channel', fontsize=18)
        self.plot_profile_B.set_ylabel('Pixel Intensity (0 - 255)', fontsize=16)

        self.canvas_fr_profile_B = tk.Frame(self.profile_scroll_class.window_fr, height = 800 - 100, bg = 'white')

        self.profile_canvas_B = FigureCanvasTkAgg(self.profile_fig_B, master = self.canvas_fr_profile_B)
        self.profile_canvas_B.get_tk_widget().place(x=0, y=0, relwidth = 1, anchor = 'nw')

        self.toolbar_fr_profile_B = tk.Frame(self.profile_scroll_class.window_fr, height = 35, bg = 'white')
        self.toolbar_profile_B = tkagg.NavigationToolbar2Tk(self.profile_canvas_B, self.toolbar_fr_profile_B)
        self.toolbar_profile_B.update_idletasks()

        self.ax_plt_profile_B = self.plot_profile_B.plot([], [], color="blue")

        """<------------------------------------------------------------------------------------------------------------------------->"""
        ### Created a custom place_info dictionary with custom place & place_forget functions. Because winfo_mapped() is so unreliable.
        ### So we place all the widgets to save the place_info data.
        self.canvas_fr_profile_mono.place(x = 0, y = 0, relwidth = 1)
        self.canvas_fr_profile_R.place(x = 0, y = 0, relwidth = 1)
        self.canvas_fr_profile_G.place(x = 0, y = 750, relwidth = 1)
        self.canvas_fr_profile_B.place(x = 0, y = 1500, relwidth = 1)

        self.toolbar_fr_profile_mono.place(relx = 0.1, y = 700, relwidth = 0.8)
        self.toolbar_fr_profile_R.place(relx = 0.1, y = 700, relwidth = 0.8)
        self.toolbar_fr_profile_G.place(relx = 0.1, y = 1450, relwidth = 0.8)
        self.toolbar_fr_profile_B.place(relx = 0.1, y = 2200, relwidth = 0.8)

        self.__prof_cvs_fr_info = {}
        self.__prof_cvs_fr_info[self.canvas_fr_profile_R]    = [self.canvas_fr_profile_R.place_info(), True]
        self.__prof_cvs_fr_info[self.canvas_fr_profile_G]    = [self.canvas_fr_profile_G.place_info(), True]
        self.__prof_cvs_fr_info[self.canvas_fr_profile_B]    = [self.canvas_fr_profile_B.place_info(), True]
        self.__prof_cvs_fr_info[self.canvas_fr_profile_mono] = [self.canvas_fr_profile_mono.place_info(), True]

        self.__prof_tbar_fr_info = {}
        self.__prof_tbar_fr_info[self.toolbar_fr_profile_R]    = [self.toolbar_fr_profile_R.place_info(), True]
        self.__prof_tbar_fr_info[self.toolbar_fr_profile_G]    = [self.toolbar_fr_profile_G.place_info(), True]
        self.__prof_tbar_fr_info[self.toolbar_fr_profile_B]    = [self.toolbar_fr_profile_B.place_info(), True]
        self.__prof_tbar_fr_info[self.toolbar_fr_profile_mono] = [self.toolbar_fr_profile_mono.place_info(), True]

        self.prof_clear_all() ### we hide all the widgets

    def prof_cvs_place(self, *cvs_args):
        for wid in cvs_args:
            if wid in self.__prof_cvs_fr_info:
                wid.place(self.__prof_cvs_fr_info[wid][0])
                self.__prof_cvs_fr_info[wid][1] = True

            else:
                raise Exception('Tkinter widget: {} '.format(wid) + 'does not exists, cannot place()!' 
                    + 'Please make sure the tk widget has been placed with its place_info updated in ( prof_cvs_fr_info ).')

    def prof_tbar_place(self, *tbar_args):
        for wid in tbar_args:
            if wid in self.__prof_tbar_fr_info:
                wid.place(self.__prof_tbar_fr_info[wid][0])
                self.__prof_tbar_fr_info[wid][1] = True

            else:
                raise Exception('Tkinter widget: {} '.format(wid) + 'does not exists, cannot place()!' 
                    + 'Please make sure the tk widget has been placed with its place_info updated in ( prof_tbar_fr_info ).')


    def prof_cvs_forget(self, *cvs_args):
        for wid in cvs_args:
            if wid in self.__prof_cvs_fr_info:
                wid.place_forget()
                self.__prof_cvs_fr_info[wid][1] = False

            else:
                raise Exception('Tkinter widget: {} '.format(wid) + 'does not exists, cannot place_forget()!' 
                    + 'Please make sure the tk widget has been placed with its place_info updated in ( prof_cvs_fr_info ).')

    def prof_tbar_forget(self, *tbar_args):
        for wid in tbar_args:
            if wid in self.__prof_tbar_fr_info:
                wid.place_forget()
                self.__prof_tbar_fr_info[wid][1] = True

            else:
                raise Exception('Tkinter widget: {} '.format(wid) + 'does not exists, cannot place_forget()!' 
                    + 'Please make sure the tk widget has been placed with its place_info updated in ( prof_tbar_fr_info ).')

    def prof_clear_all(self):
        for tk_obj, plc_info in self.__prof_cvs_fr_info.items():
            tk_obj.place_forget()
            self.__prof_cvs_fr_info[tk_obj][1] = False

        for tk_obj, plc_info in self.__prof_tbar_fr_info.items():
            tk_obj.place_forget()
            self.__prof_tbar_fr_info[tk_obj][1] = False

    def tk_plot_graph_default(self):
        if self.__img_type == 'mono':
            self.graph_histogram_mono()
        else:
            self.graph_histogram_R()
            self.graph_histogram_G()
            self.graph_histogram_B()

    def tk_plot_graph_mono(self):
        if self.roi_type_combobox.get() == 'LINE' and self.img_popout_disp.roi_line_exist == True and True == self.img_popout_toplvl.check_open():
            (profile_data_index, profile_data_mono, _
                , _, _, hist_data_list) = self.img_popout_disp.ROI_line_pixel_update()

            self.graph_pixel_profile(profile_data_index, profile_data_mono, 'mono')
            self.graph_histogram_mono(pixel_info = hist_data_list[0])

        elif self.roi_type_combobox.get() == 'BOX' and self.img_popout_disp.roi_bbox_exist == True and True == self.img_popout_toplvl.check_open():
            hist_data_list = self.img_popout_disp.ROI_box_pixel_update()
            self.graph_histogram_mono(pixel_info = hist_data_list[0])
        else:
            self.graph_histogram_mono()

    def tk_plot_graph_R(self):
        if self.roi_type_combobox.get() == 'LINE' and self.img_popout_disp.roi_line_exist == True and True == self.img_popout_toplvl.check_open():
            (profile_data_index, _, profile_data_R
                , _, _, hist_data_list) = self.img_popout_disp.ROI_line_pixel_update()

            self.graph_pixel_profile(profile_data_index, profile_data_R, 'red')
            self.graph_histogram_R(pixel_info = hist_data_list[0])

        elif self.roi_type_combobox.get() == 'BOX' and self.img_popout_disp.roi_bbox_exist == True and True == self.img_popout_toplvl.check_open():
            hist_data_list = self.img_popout_disp.ROI_box_pixel_update()
            self.graph_histogram_R(pixel_info = hist_data_list[0])
        else:
            self.graph_histogram_R()

    def tk_plot_graph_G(self):
        if self.roi_type_combobox.get() == 'LINE' and self.img_popout_disp.roi_line_exist == True and True == self.img_popout_toplvl.check_open():
            (profile_data_index, _, _
                , profile_data_G, _, hist_data_list) = self.img_popout_disp.ROI_line_pixel_update()

            self.graph_pixel_profile(profile_data_index, profile_data_G, 'green')
            self.graph_histogram_G(pixel_info = hist_data_list[1])

        elif self.roi_type_combobox.get() == 'BOX' and self.img_popout_disp.roi_bbox_exist == True and True == self.img_popout_toplvl.check_open():
            hist_data_list = self.img_popout_disp.ROI_box_pixel_update()
            self.graph_histogram_G(pixel_info = hist_data_list[1])
        else:
            self.graph_histogram_G()

    def tk_plot_graph_B(self):
        if self.roi_type_combobox.get() == 'LINE' and self.img_popout_disp.roi_line_exist == True and True == self.img_popout_toplvl.check_open():
            (profile_data_index, _, _
                , _, profile_data_B, hist_data_list) = self.img_popout_disp.ROI_line_pixel_update()

            self.graph_pixel_profile(profile_data_index, profile_data_B, 'blue')
            self.graph_histogram_B(pixel_info = hist_data_list[2])

        elif self.roi_type_combobox.get() == 'BOX' and self.img_popout_disp.roi_bbox_exist == True and True == self.img_popout_toplvl.check_open():
            hist_data_list = self.img_popout_disp.ROI_box_pixel_update()
            self.graph_histogram_B(pixel_info = hist_data_list[2])
        else:
            self.graph_histogram_B()

    def graph_pixel_profile(self, data_1, data_2, str_img_type):
        if True == self.graph_popout_toplvl.check_open():
            _graph_spacing_x = int(round( np.multiply(np.max(data_1), 0.025) )) + 1
            _graph_spacing_y = int(round( np.multiply(np.max(data_2), 0.025) )) + 1

            if str_img_type == 'mono':
                if self.__prof_cvs_fr_info[self.canvas_fr_profile_mono][1] == False:
                    self.prof_cvs_place(self.canvas_fr_profile_mono)

                if self.__prof_tbar_fr_info[self.toolbar_fr_profile_mono][1] == False:
                    self.prof_tbar_place(self.toolbar_fr_profile_mono)

                self.ax_plt_profile_mono[0].set_data(data_1, data_2)

                self.plot_profile_mono.set_xlim(xmin=0-_graph_spacing_x, xmax=np.max(data_1)+_graph_spacing_x)
                self.plot_profile_mono.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(data_2)+_graph_spacing_y)
                self.profile_canvas_mono.draw()

            elif str_img_type == 'red':
                if self.__prof_cvs_fr_info[self.canvas_fr_profile_R][1] == False:
                    self.prof_cvs_place(self.canvas_fr_profile_R)

                if self.__prof_tbar_fr_info[self.toolbar_fr_profile_R][1] == False:
                    self.prof_tbar_place(self.toolbar_fr_profile_R)

                self.ax_plt_profile_R[0].set_data(data_1, data_2)

                self.plot_profile_R.set_xlim(xmin=0-_graph_spacing_x, xmax=np.max(data_1)+_graph_spacing_x)
                self.plot_profile_R.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(data_2)+_graph_spacing_y)
                self.profile_canvas_R.draw()

            elif str_img_type == 'green':
                if self.__prof_cvs_fr_info[self.canvas_fr_profile_G][1] == False:
                    self.prof_cvs_place(self.canvas_fr_profile_G)

                if self.__prof_tbar_fr_info[self.toolbar_fr_profile_G][1] == False:
                    self.prof_tbar_place(self.toolbar_fr_profile_G)

                self.ax_plt_profile_G[0].set_data(data_1, data_2)

                self.plot_profile_G.set_xlim(xmin=0-_graph_spacing_x, xmax=np.max(data_1)+_graph_spacing_x)
                self.plot_profile_G.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(data_2)+_graph_spacing_y)
                self.profile_canvas_G.draw()

            elif str_img_type == 'blue':
                if self.__prof_cvs_fr_info[self.canvas_fr_profile_B][1] == False:
                    self.prof_cvs_place(self.canvas_fr_profile_B)

                if self.__prof_tbar_fr_info[self.toolbar_fr_profile_B][1] == False:
                    self.prof_tbar_place(self.toolbar_fr_profile_B)

                self.ax_plt_profile_B[0].set_data(data_1, data_2)

                self.plot_profile_B.set_xlim(xmin=0-_graph_spacing_x, xmax=np.max(data_1)+_graph_spacing_x)
                self.plot_profile_B.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(data_2)+_graph_spacing_y)
                self.profile_canvas_B.draw()

    
    def graph_histogram_mono(self, pixel_info = None):
        if True == self.graph_popout_toplvl.check_open():
            # print("graph_histogram_mono: ", self.__hist_cvs_fr_info[self.canvas_fr_hist_mono][1], self.__hist_cvs_fr_info[self.canvas_fr_hist_mono][1])
            if self.__hist_cvs_fr_info[self.canvas_fr_hist_mono][1] == False:
                self.hist_cvs_place(self.canvas_fr_hist_mono)

            if self.__hist_tbar_fr_info[self.toolbar_fr_hist_mono][1] == False:
                self.hist_tbar_place(self.toolbar_fr_hist_mono)

            if pixel_info is not None and (isinstance(pixel_info, np.ndarray)) == True and pixel_info.shape[0] == 256 and pixel_info.shape[1] == 1:
                self.ax_plt_hist_mono[0].set_data(self.hist_x_index, pixel_info)
            else:
                pixel_info = cv2.calcHist([self.img_imageio],[0],None,[256],[0,256])
                self.ax_plt_hist_mono[0].set_data(self.hist_x_index, pixel_info)

            _graph_spacing_x = int(round( np.multiply(np.max(self.hist_x_index), 0.025) )) + 1
            _graph_spacing_y = int(round( np.multiply(np.max(pixel_info), 0.025) )) + 1

            self.plot_hist_mono.set_xlim(xmin=0-_graph_spacing_x, xmax=255+_graph_spacing_x)
            self.plot_hist_mono.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(pixel_info)+_graph_spacing_y)
            self.hist_canvas_mono.draw()


    def graph_histogram_R(self, pixel_info = None):
        if True == self.graph_popout_toplvl.check_open():
            # print("graph_histogram_R: ", self.__hist_cvs_fr_info[self.canvas_fr_hist_R][1], self.__hist_cvs_fr_info[self.canvas_fr_hist_R][1])
            if self.__hist_cvs_fr_info[self.canvas_fr_hist_R][1] == False:
                self.hist_cvs_place(self.canvas_fr_hist_R)

            if self.__hist_tbar_fr_info[self.toolbar_fr_hist_R][1] == False:
                self.hist_tbar_place(self.toolbar_fr_hist_R)

            if pixel_info is not None and (isinstance(pixel_info, np.ndarray)) == True and pixel_info.shape[0] == 256 and pixel_info.shape[1] == 1:
                self.ax_plt_hist_R[0].set_data(self.hist_x_index, pixel_info)
            else:
                pixel_info = cv2.calcHist([self.img_imageio[:,:,0]],[0],None,[256],[0,256])
                self.ax_plt_hist_R[0].set_data(self.hist_x_index, pixel_info)

            _graph_spacing_x = int(round( np.multiply(np.max(self.hist_x_index), 0.025) )) + 1
            _graph_spacing_y = int(round( np.multiply(np.max(pixel_info), 0.025) )) + 1

            self.plot_hist_R.set_xlim(xmin=0-_graph_spacing_x, xmax=255+_graph_spacing_x)
            self.plot_hist_R.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(pixel_info)+_graph_spacing_y)
            self.hist_canvas_R.draw()


    def graph_histogram_G(self, pixel_info = None):
        if True == self.graph_popout_toplvl.check_open():
            # print("graph_histogram_G: ", self.__hist_cvs_fr_info[self.canvas_fr_hist_G][1], self.__hist_cvs_fr_info[self.canvas_fr_hist_G][1])
            if self.__hist_cvs_fr_info[self.canvas_fr_hist_G][1] == False:
                self.hist_cvs_place(self.canvas_fr_hist_G)

            if self.__hist_tbar_fr_info[self.toolbar_fr_hist_G][1] == False:
                self.hist_tbar_place(self.toolbar_fr_hist_G)

            if pixel_info is not None and (isinstance(pixel_info, np.ndarray)) == True and pixel_info.shape[0] == 256 and pixel_info.shape[1] == 1:
                self.ax_plt_hist_G[0].set_data(self.hist_x_index, pixel_info)
            else:
                pixel_info = cv2.calcHist([self.img_imageio[:,:,1]],[0],None,[256],[0,256])
                self.ax_plt_hist_G[0].set_data(self.hist_x_index, pixel_info)

            _graph_spacing_x = int(round( np.multiply(np.max(self.hist_x_index), 0.025) )) + 1
            _graph_spacing_y = int(round( np.multiply(np.max(pixel_info), 0.025) )) + 1

            self.plot_hist_G.set_xlim(xmin=0-_graph_spacing_x, xmax=255+_graph_spacing_x)
            self.plot_hist_G.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(pixel_info)+_graph_spacing_y)
            self.hist_canvas_G.draw()

    def graph_histogram_B(self, pixel_info = None):
        if True == self.graph_popout_toplvl.check_open():
            # print("graph_histogram_B: ", self.__hist_cvs_fr_info[self.canvas_fr_hist_B][1], self.__hist_cvs_fr_info[self.canvas_fr_hist_B][1])
            if self.__hist_cvs_fr_info[self.canvas_fr_hist_B][1] == False:
                self.hist_cvs_place(self.canvas_fr_hist_B)

            if self.__hist_tbar_fr_info[self.toolbar_fr_hist_B][1] == False:
                self.hist_tbar_place(self.toolbar_fr_hist_B)

            if pixel_info is not None and (isinstance(pixel_info, np.ndarray)) == True and pixel_info.shape[0] == 256 and pixel_info.shape[1] == 1:
                self.ax_plt_hist_B[0].set_data(self.hist_x_index, pixel_info)
            else:
                pixel_info = cv2.calcHist([self.img_imageio[:,:,2]],[0],None,[256],[0,256])
                self.ax_plt_hist_B[0].set_data(self.hist_x_index, pixel_info)

            _graph_spacing_x = int(round( np.multiply(np.max(self.hist_x_index), 0.025) )) + 1
            _graph_spacing_y = int(round( np.multiply(np.max(pixel_info), 0.025) )) + 1

            self.plot_hist_B.set_xlim(xmin=0-_graph_spacing_x, xmax=255+_graph_spacing_x)
            self.plot_hist_B.set_ylim(ymin=0-_graph_spacing_y, ymax=np.max(pixel_info)+_graph_spacing_y)
            self.hist_canvas_B.draw()


    def contrast_mono(self, event = None):
        alpha_val = float(self.mono_var_alpha.get())
        beta_val = int(self.mono_var_beta.get())
        
        self.img_imageio = cv2.addWeighted(self.src_img_imageio, alpha_val, 
            np.zeros(self.src_img_imageio.shape, self.src_img_imageio.dtype), 0, beta_val)

        self.gui_disp_func(self.ori_display, self.img_imageio)

    def contrast_R(self, event = None):
        alpha_val = float(self.R_var_alpha.get())
        beta_val = int(self.R_var_beta.get())

        self.img_imageio[:,:,0] = cv2.addWeighted(self.src_img_imageio[:,:,0], alpha_val, 
            np.zeros(self.src_img_imageio[:,:,0].shape, self.src_img_imageio[:,:,0].dtype), 0, beta_val)

        self.gui_disp_func(self.ori_display, self.img_imageio)
        self.gui_disp_func(self.R_display, self.img_imageio[:, :, 0])

    def contrast_G(self, event = None):
        alpha_val = float(self.G_var_alpha.get())
        beta_val = int(self.G_var_beta.get())
        
        self.img_imageio[:,:,1] = cv2.addWeighted(self.src_img_imageio[:,:,1], alpha_val, 
            np.zeros(self.src_img_imageio[:,:,1].shape, self.src_img_imageio[:,:,1].dtype), 0, beta_val)

        self.gui_disp_func(self.ori_display, self.img_imageio)
        self.gui_disp_func(self.G_display, self.img_imageio[:, :, 1])

    def contrast_B(self, event = None):
        alpha_val = float(self.B_var_alpha.get())
        beta_val = int(self.B_var_beta.get())
        
        self.img_imageio[:,:,2] = cv2.addWeighted(self.src_img_imageio[:,:,2], alpha_val, 
            np.zeros(self.src_img_imageio[:,:,2].shape, self.src_img_imageio[:,:,2].dtype), 0, beta_val)

        self.gui_disp_func(self.ori_display, self.img_imageio)
        self.gui_disp_func(self.B_display, self.img_imageio[:, :, 2])

    def display_sel_func(self, event):
        if self.display_sel.get() == self.__disp_list[0]:
            if self.__curr_disp_sel != self.display_sel.get():
                self.__curr_disp_sel = self.display_sel.get()
                self.__disp_mode = self.display_sel.get()
                tk_widget_forget(self.R_gain_frame, self.G_gain_frame, self.B_gain_frame, self.mono_gain_frame
                    , self.save_button_1, self.save_button_2, self.save_button_3, self.save_button_4)

                self.R_gain_frame.place(x = 0, y = self.y1_fr, relwidth = 1, anchor = 'nw', width = -2)
                self.G_gain_frame.place(x = 0, y = self.y2_fr, relwidth = 1, anchor = 'nw', width = -2)
                self.B_gain_frame.place(x = 0, y = self.y3_fr, relwidth = 1, anchor = 'nw', width = -2)

                self.save_button_1.place(x = 0, y = self.y3_fr + 150)
                self.save_button_2.place(x = 0, y = self.y3_fr + 150 + 40)
                self.save_button_3.place(x = 0, y = self.y3_fr + 150 + 80)
                self.save_button_4.place(x = 0, y = self.y3_fr + 150 + 120)

                self.gui_resize_func()

        elif self.display_sel.get() == self.__disp_list[1]:
            if self.__curr_disp_sel != self.display_sel.get():
                self.__curr_disp_sel = self.display_sel.get()
                self.__disp_mode = self.display_sel.get()

                if self.__img_type == 'mono':
                    tk_widget_forget(self.R_gain_frame, self.G_gain_frame, self.B_gain_frame, self.mono_gain_frame
                        , self.save_button_1, self.save_button_2, self.save_button_3, self.save_button_4)

                    self.mono_gain_frame.place(x = 0, y = self.y1_fr, relwidth = 1, anchor = 'nw', width = -2)
                    self.save_button_1.place(x = 0, y = self.y1_fr + 150)

                elif self.__img_type == 'rgb':
                    tk_widget_forget(self.R_gain_frame, self.G_gain_frame, self.B_gain_frame, self.mono_gain_frame
                        , self.save_button_1, self.save_button_2, self.save_button_3, self.save_button_4)

                    self.R_gain_frame.place(x = 0, y = self.y1_fr, relwidth = 1, anchor = 'nw', width = -2)
                    self.G_gain_frame.place(x = 0, y = self.y2_fr, relwidth = 1, anchor = 'nw', width = -2)
                    self.B_gain_frame.place(x = 0, y = self.y3_fr, relwidth = 1, anchor = 'nw', width = -2)

                    self.save_button_1.place(x = 0, y = self.y3_fr + 150)
                    self.save_button_2.place(x = 0, y = self.y3_fr + 150 + 40)
                    self.save_button_3.place(x = 0, y = self.y3_fr + 150 + 80)
                    self.save_button_4.place(x = 0, y = self.y3_fr + 150 + 120)

                self.gui_resize_func()

        elif self.display_sel.get() == self.__disp_list[2]:
            if self.__curr_disp_sel != self.display_sel.get():
                self.__curr_disp_sel = self.display_sel.get()
                self.__disp_mode = self.display_sel.get()
                tk_widget_forget(self.R_gain_frame, self.G_gain_frame, self.B_gain_frame, self.mono_gain_frame
                    , self.save_button_1, self.save_button_2, self.save_button_3, self.save_button_4)

                self.R_gain_frame.place(x = 0, y = self.y1_fr, relwidth = 1, anchor = 'nw', width = -2)
                self.save_button_2.place(x = 0, y = self.y1_fr + 150)
                self.gui_resize_func()


        elif self.display_sel.get() == self.__disp_list[3]:
            if self.__curr_disp_sel != self.display_sel.get():
                self.__curr_disp_sel = self.display_sel.get()
                self.__disp_mode = self.display_sel.get()
                tk_widget_forget(self.R_gain_frame, self.G_gain_frame, self.B_gain_frame, self.mono_gain_frame
                    , self.save_button_1, self.save_button_2, self.save_button_3, self.save_button_4)

                self.G_gain_frame.place(x = 0, y = self.y1_fr, relwidth = 1, anchor = 'nw', width = -2)
                self.save_button_3.place(x = 0, y = self.y1_fr + 150)
                self.gui_resize_func()

        elif self.display_sel.get() == self.__disp_list[4]:
            if self.__curr_disp_sel != self.display_sel.get():
                self.__curr_disp_sel = self.display_sel.get()
                self.__disp_mode = self.display_sel.get()
                tk_widget_forget(self.R_gain_frame, self.G_gain_frame, self.B_gain_frame, self.mono_gain_frame
                    , self.save_button_1, self.save_button_2, self.save_button_3, self.save_button_4)

                self.B_gain_frame.place(x = 0, y = self.y1_fr, relwidth = 1, anchor = 'nw', width = -2)
                self.save_button_4.place(x = 0, y = self.y1_fr + 150)
                self.gui_resize_func()

    def load_img(self):
        self.__img_file = filedialog.askopenfilename(initialdir = self.__load_curr_dir, title="Select file", defaultextension = self.img_format_list, filetypes=self.img_format_list)
        #print(self.__img_file)
        if self.__img_file == '':
            #print('empty directory')
            pass
        else: 
            self.__load_curr_dir = str((pathlib.Path(self.__img_file)).parent)

            self.img_imageio = imread(self.__img_file)
            self.__curr_disp_sel = None

            self.src_img_imageio = self.img_imageio.copy()
            self.img_load_status = True

            img_megapixel = int (round (np.divide(np.multiply(self.img_imageio.shape[1], self.img_imageio.shape[0]), 1000000)) )
            if img_megapixel == 0:
                img_megapixel = round (np.divide(np.multiply(self.img_imageio.shape[1], self.img_imageio.shape[0]), 1000000), 1)

            img_resolution ='Resolution: ' + str(self.img_imageio.shape[1]) + ' x ' + str(self.img_imageio.shape[0]) + ' (' + str(img_megapixel) + ' MP)'

            self.resolution.set(img_resolution)

            self.reset_gain_param()
            self.popout_img_close(reset = True)
            self.graph_popout_close()

            if len(self.img_imageio.shape) == 2:
                self.img_popout_btn['state'] = 'normal'
                self.graph_btn['state'] = 'normal'
                self.__img_type = 'mono'
                self.display_sel['values'] = [self.__disp_list[1]]
                self.display_sel.current(0)
                self.display_sel.bind('<<ComboboxSelected>>', self.display_sel_func)

                self.display_sel_func(event=None)

            elif len(self.img_imageio.shape) == 3:
                self.img_popout_btn['state'] = 'normal'
                self.graph_btn['state'] = 'normal'
                self.__img_type = 'rgb'
                self.display_sel['values'] = self.__disp_list
                self.display_sel.current(0)
                self.display_sel.bind('<<ComboboxSelected>>', self.display_sel_func)

                self.display_sel_func(event=None)


    def save_ori_img(self):
        if self.img_load_status == True:
            f = filedialog.asksaveasfilename(initialdir = self.__save_curr_dir, defaultextension = self.img_format_list
                , filetypes = self.img_format_list, confirmoverwrite=False)
            if f is '': # asksaveasfile return `None` if dialog closed with "cancel".
                return

            file_name = (re.findall(r'[^\\/]+|[\\/]', f))[-1]
            folder_name = str((pathlib.Path(f)).parent)
            self.__save_curr_dir = folder_name
            file_extension = os.path.splitext(f)[-1]

            base_name = re.sub("("+ file_extension +")$", "", file_name)

            cv_img_save(folder_name, self.img_imageio
                    , base_name, str(file_extension)
                    , kw_str = '(Colour)')

            Info_Msgbox(message = 'The Original Image is Saved', message_anchor = 'w', title = 'Save')

        else:
            Error_Msgbox(message = 'Load an Image before Saving', message_anchor = 'w', title = 'Error')

    def save_R_img(self):
        if self.img_load_status == True:
            f = filedialog.asksaveasfilename(initialdir = self.__save_curr_dir, defaultextension = self.img_format_list
                , filetypes = self.img_format_list, confirmoverwrite=False)
            if f is '':
                return

            file_name = (re.findall(r'[^\\/]+|[\\/]', f))[-1]
            folder_name = str((pathlib.Path(f)).parent)
            self.__save_curr_dir = folder_name
            file_extension = os.path.splitext(f)[-1]

            base_name = re.sub("("+ file_extension +")$", "", file_name)

            cv_img_save(folder_name, self.img_imageio[:,:,0]
                    , base_name, str(file_extension)
                    , kw_str = '(Red-Ch)')

            Info_Msgbox(message = 'The Red Channel Image is Saved', message_anchor = 'w', title = 'Save')

        else:
            Error_Msgbox(message = 'Load an Image before Saving', message_anchor = 'w', title = 'Error')

    def save_G_img(self):
        if self.img_load_status == True:
            f = filedialog.asksaveasfilename(initialdir = self.__save_curr_dir, defaultextension = self.img_format_list
                , filetypes = self.img_format_list, confirmoverwrite=False)
            if f is '':
                return

            file_name = (re.findall(r'[^\\/]+|[\\/]', f))[-1]
            folder_name = str((pathlib.Path(f)).parent)
            self.__save_curr_dir = folder_name
            file_extension = os.path.splitext(f)[-1]

            base_name = re.sub("("+ file_extension +")$", "", file_name)

            cv_img_save(folder_name, self.img_imageio[:,:,1]
                    , base_name, str(file_extension)
                    , kw_str = '(Green-Ch)')

            Info_Msgbox(message = 'The Green Channel Image is Saved', message_anchor = 'w', title = 'Save')

        else:
            Error_Msgbox(message = 'Load an Image before Saving', message_anchor = 'w', title = 'Error')

    def save_B_img(self):
        if self.img_load_status == True:
            f = filedialog.asksaveasfilename(initialdir = self.__save_curr_dir, defaultextension = self.img_format_list
                , filetypes = self.img_format_list, confirmoverwrite=False)
            if f is '':
                return

            file_name = (re.findall(r'[^\\/]+|[\\/]', f))[-1]
            folder_name = str((pathlib.Path(f)).parent)
            self.__save_curr_dir = folder_name
            file_extension = os.path.splitext(f)[-1]

            base_name = re.sub("("+ file_extension +")$", "", file_name)

            cv_img_save(folder_name, self.img_imageio[:,:,2]
                    , base_name, str(file_extension)
                    , kw_str = '(Blue-Ch)')

            Info_Msgbox(message = 'The Blue Channel Image is Saved', message_anchor = 'w', title = 'Save')

        else:
            Error_Msgbox(message = 'Load an Image before Saving', message_anchor = 'w', title = 'Error')

