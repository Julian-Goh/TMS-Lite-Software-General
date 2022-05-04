import os
from os import path
import sys

import tkinter as tk

from PIL import ImageTk, Image
import numpy as np
import imutils

import inspect
import ctypes
from ctypes import *

import threading
import msvcrt

from Tk_Custom_Widget.ScrolledCanvas import ScrolledCanvas
from Tk_Custom_Widget.custom_zoom_class import CanvasImage

from misc_module.tool_tip import CreateToolTip
from misc_module.image_resize import img_resize_dim, opencv_img_resize, pil_img_resize
from misc_module.tk_img_module import to_tk_img

from Multi_Camera_GUI import Multi_Camera_GUI

# code_PATH = os.getcwd()
# sys.path.append(code_PATH + '\\MVS-Python\\MvImport')

from MvCameraControl_class import *

def To_hex_str(num):
        chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
        hexStr = ""
        if num < 0:
            num = num + 2**32
        while num >= 16:
            digit = num % 16
            hexStr = chaDic.get(digit, str(digit)) + hexStr
            num //= 16
        hexStr = chaDic.get(num, str(num)) + hexStr   
        return hexStr

class Multi_Camera_Home(tk.Frame):
    def __init__(self, master, scrolled_canvas, gui_graphic = {}, **kwargs):

        tk.Frame.__init__(self, master, **kwargs)

        self.master_canvas = scrolled_canvas

        self.gui_graphic = dict(  cam_disconnect_icon = None, cam_connect_icon = None
                                , toggle_ON_button_img = None, toggle_OFF_button_img = None
                                , img_flip_icon = None, save_icon = None, popout_icon = None
                                , info_icon = None, refresh_icon = None, fit_to_display_icon = None, window_icon = None)

        for key, item in gui_graphic.items():
            if key in self.gui_graphic:
                self.gui_graphic[key] = item

        self.cam_disconnect_icon    = to_tk_img(pil_img_resize(self.gui_graphic['cam_disconnect_icon'], img_width = 18, img_height =18))
        self.cam_connect_icon       = to_tk_img(pil_img_resize(self.gui_graphic['cam_connect_icon'], img_width = 18, img_height =18))

        self.cam_disconnect_img     = to_tk_img(pil_img_resize(self.gui_graphic['cam_disconnect_icon'], img_width = 150, img_height = 150))
        self.toggle_ON_button_img   = to_tk_img(pil_img_resize(self.gui_graphic['toggle_ON_button_img'], img_scale = 0.06))
        self.toggle_OFF_button_img  = to_tk_img(pil_img_resize(self.gui_graphic['toggle_OFF_button_img'], img_scale = 0.06))

        self.img_flip_icon          = to_tk_img(pil_img_resize(self.gui_graphic['img_flip_icon'], img_scale = 0.033))
        self.save_icon              = to_tk_img(pil_img_resize(self.gui_graphic['save_icon'], img_scale = 0.035))
        self.popout_icon            = to_tk_img(pil_img_resize(self.gui_graphic['popout_icon'], img_scale = 0.1))
        self.info_icon              = to_tk_img(pil_img_resize(self.gui_graphic['info_icon'], img_scale = 0.13))
        self.refresh_icon           = to_tk_img(pil_img_resize(self.gui_graphic['refresh_icon'], img_width = 18, img_height =18))
        self.fit_to_display_icon    = to_tk_img(pil_img_resize(self.gui_graphic['fit_to_display_icon'], img_width = 22, img_height =22))
        self.window_icon            = self.gui_graphic['window_icon']

        self.mv_camera = MvCamera()
        
        self.thread_refresh_handle = None

        self.auto_refresh_tk_id = None

        self.devList = []
        self.hikvision_devList = []

        self._serial_list = []

        self.device_label_list = []
        self.connect_btn_list = []
        self.connected_serial_id = {}

        self.load_gui_class = []

        self.display_gui_list = []
        self.fr_display_list = []

        self.cam_serial_checker = []
        self.cam_serial_list = []

        self.init_enum_bool = False

        self.mv_camera_list = []

        self.curr_widget = None
        self.click_tracker = 0

        self.home_mode = True

        self.cam_display_width = 400
        self.cam_display_height = 300

        self.default_gui = tk.Frame(self)
        self.default_gui.place(relwidth=1, relheight=1, x=0, y=0)        

        self.tk_frame_cam_disp = tk.Frame(self.default_gui, highlightbackground="black", highlightthickness=1)
        self.tk_frame_cam_disp['bg'] = 'white'
        self.tk_frame_cam_disp['width'] = self.cam_display_width + self.cam_display_width + 50

        self.tk_frame_cam_disp.place(x = 230, y = 0, relheight = 1, height = -110, anchor = 'nw')

        master_width = int(self.tk_frame_cam_disp.place_info()['x']) + self.cam_display_width + self.cam_display_width + 50 + 10 
        self.master_canvas.resize_frame(width = master_width)

        self.scroll_cam_disp = ScrolledCanvas(master = self.tk_frame_cam_disp
            , frame_w = self.cam_display_width + self.cam_display_width + 50, frame_h = 900
            , canvas_x = 0, canvas_y = 0, bg = 'white')
        self.scroll_cam_disp.show(scroll_x = False)

        #CUSTOM SCROLLS FOR MULTI CAMERA GUI
        self.scroll_cam_disp.canvas.bind('<Enter>', lambda event: self.custom_scroll_inner_bound(event, self.scroll_cam_disp))
        self.scroll_cam_disp.canvas.bind('<Leave>', self.master_canvas._bound_to_mousewheel)


        self.ctrl_panel_gui = tk.Frame(self)
        self.ctrl_panel_gui['bg'] = 'white'
        self.home_btn = tk.Button(self.ctrl_panel_gui, relief = tk.GROOVE, text = 'HOME', font = 'Helvetica 11')
        self.home_btn['width'] = 7
        self.home_btn['command'] = self.home_func
        self.home_btn.place(x=0, y=0)

        self.connect_frame()

        #self.start_auto_refresh()

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
                        self.master_canvas.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            elif y1_inner == 1:
                if 0<= y0_inner < 1: #inner scroll: End point
                    if event.delta < 0: #scroll down
                        self.master_canvas.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def home_func(self):
        self.hide_camera_control()
        self.ctrl_panel_gui.place_forget()
        self.default_gui.place(relwidth=1, relheight=1, x=0, y=0)
        self.home_mode = True

    def hide_camera_control(self):
        try:
            self.load_gui_class[self.disp_index].hide_camera_control()
        except Exception:
            pass

    def show_camera_control(self):
        try:
            self.load_gui_class[self.disp_index].show_camera_control()
        except Exception:
            pass

    def connect_frame(self):
        self.conn_frame_w = 300
        self.conn_frame_h = 350 + 100

        detect_window_1 = tk.Frame(self.default_gui)
        detect_window_1['width'] = 200
        detect_window_1['height'] = 350 + 100
        detect_window_1.place(x=0, y= 0, anchor = 'nw')

        self.hikvision_fr = ScrolledCanvas(master = detect_window_1, frame_w = self.conn_frame_w, frame_h = self.conn_frame_h, 
            canvas_x = 0, canvas_y = 0, bg = 'white')

        self.hikvision_fr.show()
        self.hikvision_fr.canvas.bind('<Enter>', lambda event: self.custom_scroll_inner_bound(event, self.hikvision_fr))
        self.hikvision_fr.canvas.bind('<Leave>', self.master_canvas._bound_to_mousewheel)

        tk.Label(self.hikvision_fr.window_fr ,text = 'HikVision Device(s):', font = 'Helvetica 11', bg = 'white').place(x=0, y=0, anchor = 'nw')

        self.init_devices()

        refresh_btn = tk.Button(self.hikvision_fr.window_fr, relief = tk.GROOVE)
        # refresh_btn['width'] = 2
        # refresh_btn['height'] = 1
        refresh_btn['image'] = self.refresh_icon
        refresh_btn['anchor'] = 'center'
        refresh_btn['bg'] = 'snow2' 
        refresh_btn['fg'] = 'snow2'
        refresh_btn['activebackground'] = 'snow2'
        refresh_btn['activeforeground'] = 'snow2'
        refresh_btn.place(x=135, y=0, anchor = 'nw')
        refresh_btn['command'] = self.hard_refresh_devices

        CreateToolTip(refresh_btn, 'Refresh Device List'
            , 0, -22, width = 115, height = 20)

    def start_auto_refresh(self):
        self.normal_refresh_devices()
        update_interval = 250
        self.auto_refresh_tk_id = self.default_gui.after(update_interval, self.start_auto_refresh)

    def stop_auto_refresh(self):
        if self.auto_refresh_tk_id is not None:
            self.default_gui.after_cancel(self.auto_refresh_tk_id)
        else:
            self.auto_refresh_tk_id  = None
            pass

    def init_devices(self):
        self.enum_devices()

        self.load_gui_class *= 0
        if len(self.connect_btn_list) > 0:
            try:
                for btn in self.connect_btn_list:
                    btn.destroy()
            except Exception:
                pass

        self.display_GUI()
        if len(self.hikvision_devList) > 0:
            self.connect_btn_list *= 0
            for i in range(len(self.hikvision_devList)):
                _gui_class = Multi_Camera_GUI(main_frame = self.ctrl_panel_gui, scroll_class = self.master_canvas, cam_disconnect_img = self.cam_disconnect_img
                    , toggle_ON_button_img = self.toggle_ON_button_img, toggle_OFF_button_img = self.toggle_OFF_button_img
                    , img_flip_icon = self.img_flip_icon, save_icon = self.save_icon, popout_icon = self.popout_icon
                    , info_icon = self.info_icon, fit_to_display_icon = self.fit_to_display_icon
                    , window_icon = self.window_icon)

                self.load_gui_class.append(_gui_class)

                self.mv_camera_list.append(MvCamera())

                place_y = int(25 + np.multiply(25, int(i)))
                label = tk.Label(self.hikvision_fr.window_fr, text = self.devList[i], font = 'Helvetica 10', bg = 'white')
                label.place(anchor = 'nw', x=25, y = place_y)
                self.device_label_list.append(label)

                btn = tk.Button(self.hikvision_fr.window_fr, relief = tk.GROOVE)
                #btn['width'] = 2
                #btn['height'] = 1
                btn['image'] = self.cam_disconnect_icon
                btn['anchor'] = 'center'
                btn['bg'] = 'snow2' 
                btn['fg'] = 'snow2'
                btn['activebackground'] = 'snow2'
                btn['activeforeground'] = 'snow2'

                btn.place(x = 0, y = place_y - 2)
                self.connect_btn_list.append(btn)

            if (place_y + 45) > self.conn_frame_h:
                self.hikvision_fr.resize_frame(height = place_y + 45)

            # print(self.load_gui_class)
            # self.display_GUI()

            for i, btn in enumerate(self.connect_btn_list):
                # btn.configure(command = lambda gui_class = self.load_gui_class[i],\
                #     nSelCamIndex = int(i), mv_camera = self.mv_camera_list[i], tk_btn = btn, tk_display = self.display_gui_list[i]:\
                #     self.connect_func(gui_class, nSelCamIndex, mv_camera, tk_btn, tk_display))
                btn.configure(command = self.custom_lambda_connect_btn(gui_class = self.load_gui_class[i],
                    nSelCamIndex = int(i), mv_camera = self.mv_camera_list[i], tk_btn = btn, tk_display = self.display_gui_list[i]))

    def normal_refresh_devices(self):
        self.enum_devices()

        if len(self.hikvision_devList) > len(self.load_gui_class):
            self.home_func()

            invoke_dictionary = self.connected_serial_id.copy()
            if len(invoke_dictionary) != 0:
                #print('device increased: ',invoke_dictionary)
                for serial, cam_index in invoke_dictionary.items():
                    self.connect_btn_list[cam_index].invoke()

            for _ in range(len(self.hikvision_devList) - len(self.load_gui_class)):
                _gui_class = Multi_Camera_GUI(main_frame = self.ctrl_panel_gui, scroll_class = self.master_canvas, cam_disconnect_img = self.cam_disconnect_img
                    , toggle_ON_button_img = self.toggle_ON_button_img, toggle_OFF_button_img = self.toggle_OFF_button_img
                    , img_flip_icon = self.img_flip_icon, save_icon = self.save_icon, popout_icon = self.popout_icon
                    , info_icon = self.info_icon, fit_to_display_icon = self.fit_to_display_icon
                    , window_icon = self.window_icon)

                self.load_gui_class.append(_gui_class)

                self.mv_camera_list.append(MvCamera())
            

            if len(self.connect_btn_list) > 0:
                try:
                    for btn in self.connect_btn_list:
                        btn.destroy()
                except Exception:
                    pass

            if len(self.device_label_list) > 0:
                try:
                    for label in self.device_label_list:
                        label.destroy()
                except Exception:
                    pass

            self.connect_btn_list *= 0
            self.device_label_list *= 0

            self.hikvision_fr.resize_frame(height = self.conn_frame_h)

            self.display_GUI()

            if len(self.hikvision_devList) > 0:
                for i in range(len(self.hikvision_devList)):
                    place_y = int(25 + np.multiply(25, int(i)))
                    label = tk.Label(self.hikvision_fr.window_fr, text = self.devList[i], font = 'Helvetica 10', bg = 'white')
                    label.place(anchor = 'nw', x=25, y = place_y)
                    self.device_label_list.append(label)
                    #btn['width'] = 2
                    #btn['height'] = 1
                    btn = tk.Button(self.hikvision_fr.window_fr, relief = tk.GROOVE)
                    if self.load_gui_class[i].cam_conn_status == False:
                        btn['image'] = self.cam_disconnect_icon
                        btn['anchor'] = 'center'
                        btn['bg'] = 'snow2' 
                        btn['fg'] = 'snow2'
                        btn['activebackground'] = 'snow2'
                        btn['activeforeground'] = 'snow2'

                    elif self.load_gui_class[i].cam_conn_status == True:
                        btn['image'] = self.cam_connect_icon
                        btn['anchor'] = 'center'
                        btn['bg'] = 'snow2' 
                        btn['fg'] = 'snow2'
                        btn['activebackground'] = 'snow2'
                        btn['activeforeground'] = 'snow2'

                    btn.place(x = 0, y = place_y - 2)
                    self.connect_btn_list.append(btn)

                if (place_y + 45) > self.conn_frame_h:
                    self.hikvision_fr.resize_frame(height = place_y + 45)

                # self.display_GUI()

                for i, btn in enumerate(self.connect_btn_list):
                    # btn.configure(command = lambda gui_class = self.load_gui_class[i],\
                    #     nSelCamIndex = int(i), mv_camera = self.mv_camera_list[i], tk_btn = btn, tk_display = self.display_gui_list[i]:\
                    #     self.connect_func(gui_class, nSelCamIndex, mv_camera, tk_btn, tk_display))
                    btn.configure(command = self.custom_lambda_connect_btn(gui_class = self.load_gui_class[i],
                        nSelCamIndex = int(i), mv_camera = self.mv_camera_list[i], tk_btn = btn, tk_display = self.display_gui_list[i]))

                if len(invoke_dictionary) != 0:
                    #print(invoke_dictionary)
                    for i in range(len(self.hikvision_devList)):
                        _serial = self.hikvision_get_cam_serial(self.hikvision_devList[i])
                        for serial, cam_index in invoke_dictionary.items():
                            if _serial == serial:
                                self.connect_btn_list[i].invoke()


        elif len(self.hikvision_devList) < len(self.load_gui_class):
            self.home_func()

            invoke_dictionary = self.connected_serial_id.copy()
            if len(invoke_dictionary) != 0:
                #print('device decreased: ',invoke_dictionary)
                for serial, cam_index in invoke_dictionary.items():
                    self.connect_btn_list[cam_index].invoke()

            for _ in range(len(self.load_gui_class) - len(self.hikvision_devList)):
                del self.load_gui_class[-1]
                del self.mv_camera_list[-1]

            if len(self.connect_btn_list) > 0:
                try:
                    for btn in self.connect_btn_list:
                        btn.destroy()
                except Exception:
                    pass

            if len(self.device_label_list) > 0:
                try:
                    for label in self.device_label_list:
                        label.destroy()
                except Exception:
                    pass

            self.connect_btn_list *= 0
            self.device_label_list *= 0

            self.hikvision_fr.resize_frame(height = self.conn_frame_h)

            self.display_GUI()

            if len(self.hikvision_devList) == 0:
                self.connected_serial_id.clear()
                self._serial_list *= 0

            elif len(self.hikvision_devList) > 0:
                #TO UPDATE THE CONNECTION DICTIONARY WHEN USER PULL OUT THE CONNECTION
                self._serial_list *= 0
                for i in range(len(self.hikvision_devList)):
                    _serial = self.hikvision_get_cam_serial(self.hikvision_devList[i])
                    self._serial_list.append(_serial)
                _serial_checker = set(self._serial_list)
                #print(_serial_checker)
                if len(self.connected_serial_id) > 0:
                    #disconnected_serial_list = [_serial for _serial in list(self.connected_serial_id.copy()) if _serial not in _serial_checker]
                    disconnected_serial_list = [_serial for _serial in list(invoke_dictionary) if _serial not in _serial_checker]
                    #print(disconnected_serial_list)
                    if len(disconnected_serial_list) > 0:
                        for _serial in disconnected_serial_list:
                            del self.connected_serial_id[_serial] # to update the actual dictionary and clear all disconnected ID
                            del invoke_dictionary[_serial] #to update the copy which will be used to invoke the connections again after re-creating widgets

                for i in range(len(self.hikvision_devList)):
                    place_y = int(25 + np.multiply(25, int(i)))
                    label = tk.Label(self.hikvision_fr.window_fr, text = self.devList[i], font = 'Helvetica 10', bg = 'white')
                    label.place(anchor = 'nw', x=25, y = place_y)
                    self.device_label_list.append(label)
                    #btn['width'] = 2
                    #btn['height'] = 1
                    btn = tk.Button(self.hikvision_fr.window_fr, relief = tk.GROOVE)
                    if self.load_gui_class[i].cam_conn_status == False:
                        btn['image'] = self.cam_disconnect_icon
                        btn['anchor'] = 'center'
                        btn['bg'] = 'snow2' 
                        btn['fg'] = 'snow2'
                        btn['activebackground'] = 'snow2'
                        btn['activeforeground'] = 'snow2'

                    elif self.load_gui_class[i].cam_conn_status == True:
                        btn['image'] = self.cam_connect_icon
                        btn['anchor'] = 'center'
                        btn['bg'] = 'snow2' 
                        btn['fg'] = 'snow2'
                        btn['activebackground'] = 'snow2'
                        btn['activeforeground'] = 'snow2'

                    btn.place(x = 0, y = place_y - 2)
                    self.connect_btn_list.append(btn)

                if (place_y + 45) > self.conn_frame_h:
                    self.hikvision_fr.resize_frame(height = place_y + 45)

                for i, btn in enumerate(self.connect_btn_list):
                    # btn.configure(command = lambda gui_class = self.load_gui_class[i],\
                    #     nSelCamIndex = int(i), mv_camera = self.mv_camera_list[i], tk_btn = btn, tk_display = self.display_gui_list[i]:\
                    #     self.connect_func(gui_class, nSelCamIndex, mv_camera, tk_btn, tk_display))
                    btn.configure(command = self.custom_lambda_connect_btn(gui_class = self.load_gui_class[i],
                        nSelCamIndex = int(i), mv_camera = self.mv_camera_list[i], tk_btn = btn, tk_display = self.display_gui_list[i]))

                if len(invoke_dictionary) != 0:
                    for i in range(len(self.hikvision_devList)):
                        _serial = self.hikvision_get_cam_serial(self.hikvision_devList[i])
                        for serial, _ in invoke_dictionary.items():
                            if _serial == serial:
                                self.connect_btn_list[i].invoke()

        elif len(self.hikvision_devList) == len(self.load_gui_class):
            pass

    
    def hard_refresh_devices(self):
        self.enum_devices()

        if len(self.hikvision_devList) > len(self.load_gui_class):
            self.home_func()

            invoke_dictionary = self.connected_serial_id.copy()
            if len(invoke_dictionary) != 0:
                #print('device increased: ',invoke_dictionary)
                for serial, cam_index in invoke_dictionary.items():
                    self.connect_btn_list[cam_index].invoke()

            for _ in range(len(self.hikvision_devList) - len(self.load_gui_class)):
                _gui_class = Multi_Camera_GUI(main_frame = self.ctrl_panel_gui, scroll_class = self.master_canvas, cam_disconnect_img = self.cam_disconnect_img
                    , toggle_ON_button_img = self.toggle_ON_button_img, toggle_OFF_button_img = self.toggle_OFF_button_img
                    , img_flip_icon = self.img_flip_icon, save_icon = self.save_icon, popout_icon = self.popout_icon
                    , info_icon = self.info_icon, fit_to_display_icon = self.fit_to_display_icon
                    , window_icon = self.window_icon)

                self.load_gui_class.append(_gui_class)

                self.mv_camera_list.append(MvCamera())
            

            if len(self.connect_btn_list) > 0:
                try:
                    for btn in self.connect_btn_list:
                        btn.destroy()
                except Exception:
                    pass

            if len(self.device_label_list) > 0:
                try:
                    for label in self.device_label_list:
                        label.destroy()
                except Exception:
                    pass

            self.connect_btn_list *= 0
            self.device_label_list *= 0

            self.hikvision_fr.resize_frame(height = self.conn_frame_h)

            self.display_GUI()

            if len(self.hikvision_devList) > 0:
                for i in range(len(self.hikvision_devList)):
                    place_y = int(25 + np.multiply(25, int(i)))
                    label = tk.Label(self.hikvision_fr.window_fr, text = self.devList[i], font = 'Helvetica 10', bg = 'white')
                    label.place(anchor = 'nw', x=25, y = place_y)
                    self.device_label_list.append(label)
                    #btn['width'] = 2
                    #btn['height'] = 1
                    btn = tk.Button(self.hikvision_fr.window_fr, relief = tk.GROOVE)
                    if self.load_gui_class[i].cam_conn_status == False:
                        btn['image'] = self.cam_disconnect_icon
                        btn['anchor'] = 'center'
                        btn['bg'] = 'snow2' 
                        btn['fg'] = 'snow2'
                        btn['activebackground'] = 'snow2'
                        btn['activeforeground'] = 'snow2'

                    elif self.load_gui_class[i].cam_conn_status == True:
                        btn['image'] = self.cam_connect_icon
                        btn['anchor'] = 'center'
                        btn['bg'] = 'snow2' 
                        btn['fg'] = 'snow2'
                        btn['activebackground'] = 'snow2'
                        btn['activeforeground'] = 'snow2'

                    btn.place(x = 0, y = place_y - 2)
                    self.connect_btn_list.append(btn)

                if (place_y + 45) > self.conn_frame_h:
                    self.hikvision_fr.resize_frame(height = place_y + 45)

                # self.display_GUI()

                for i, btn in enumerate(self.connect_btn_list):
                    # btn.configure(command = lambda gui_class = self.load_gui_class[i],\
                    #     nSelCamIndex = int(i), mv_camera = self.mv_camera_list[i], tk_btn = btn, tk_display = self.display_gui_list[i]:\
                    #     self.connect_func(gui_class, nSelCamIndex, mv_camera, tk_btn, tk_display))
                    btn.configure(command = self.custom_lambda_connect_btn(gui_class = self.load_gui_class[i],
                        nSelCamIndex = int(i), mv_camera = self.mv_camera_list[i], tk_btn = btn, tk_display = self.display_gui_list[i]))

                if len(invoke_dictionary) != 0:
                    #print(invoke_dictionary)
                    for i in range(len(self.hikvision_devList)):
                        _serial = self.hikvision_get_cam_serial(self.hikvision_devList[i])
                        for serial, cam_index in invoke_dictionary.items():
                            if _serial == serial:
                                self.connect_btn_list[i].invoke()

        elif len(self.hikvision_devList) < len(self.load_gui_class):
            self.home_func()

            invoke_dictionary = self.connected_serial_id.copy()
            if len(invoke_dictionary) != 0:
                #print('device decreased: ',invoke_dictionary)
                for serial, cam_index in invoke_dictionary.items():
                    self.connect_btn_list[cam_index].invoke()

            for _ in range(len(self.load_gui_class) - len(self.hikvision_devList)):
                del self.load_gui_class[-1]
                del self.mv_camera_list[-1]

            if len(self.connect_btn_list) > 0:
                    try:
                        for btn in self.connect_btn_list:
                            btn.destroy()
                    except Exception:
                        pass

            if len(self.device_label_list) > 0:
                try:
                    for label in self.device_label_list:
                        label.destroy()
                except Exception:
                    pass

            self.connect_btn_list *= 0
            self.device_label_list *= 0

            self.hikvision_fr.resize_frame(height = self.conn_frame_h)

            self.display_GUI()

            if len(self.hikvision_devList) == 0:
                self.connected_serial_id.clear()
                self._serial_list *= 0

            elif len(self.hikvision_devList) > 0:
                #TO UPDATE THE CONNECTION DICTIONARY WHEN USER PULL OUT THE CONNECTION
                self._serial_list *= 0
                for i in range(len(self.hikvision_devList)):
                    _serial = self.hikvision_get_cam_serial(self.hikvision_devList[i])
                    self._serial_list.append(_serial)
                _serial_checker = set(self._serial_list)
                #print(_serial_checker)
                if len(self.connected_serial_id) > 0:
                    #disconnected_serial_list = [_serial for _serial in list(self.connected_serial_id.copy()) if _serial not in _serial_checker]
                    disconnected_serial_list = [_serial for _serial in list(invoke_dictionary) if _serial not in _serial_checker]
                    #print(disconnected_serial_list)
                    if len(disconnected_serial_list) > 0:
                        for _serial in disconnected_serial_list:
                            del self.connected_serial_id[_serial] # to update the actual dictionary and clear all disconnected ID
                            del invoke_dictionary[_serial] #to update the copy which will be used to invoke the connections again after re-creating widgets

                for i in range(len(self.hikvision_devList)):
                    place_y = int(25 + np.multiply(25, int(i)))
                    label = tk.Label(self.hikvision_fr.window_fr, text = self.devList[i], font = 'Helvetica 10', bg = 'white')
                    label.place(anchor = 'nw', x=25, y = place_y)
                    self.device_label_list.append(label)
                    #btn['width'] = 2
                    #btn['height'] = 1
                    btn = tk.Button(self.hikvision_fr.window_fr, relief = tk.GROOVE)
                    if self.load_gui_class[i].cam_conn_status == False:
                        btn['image'] = self.cam_disconnect_icon
                        btn['anchor'] = 'center'
                        btn['bg'] = 'snow2' 
                        btn['fg'] = 'snow2'
                        btn['activebackground'] = 'snow2'
                        btn['activeforeground'] = 'snow2'

                    elif self.load_gui_class[i].cam_conn_status == True:
                        btn['image'] = self.cam_connect_icon
                        btn['anchor'] = 'center'
                        btn['bg'] = 'snow2' 
                        btn['fg'] = 'snow2'
                        btn['activebackground'] = 'snow2'
                        btn['activeforeground'] = 'snow2'

                    btn.place(x = 0, y = place_y - 2)
                    self.connect_btn_list.append(btn)

                if (place_y + 45) > self.conn_frame_h:
                    self.hikvision_fr.resize_frame(height = place_y + 45)

                # self.display_GUI()

                for i, btn in enumerate(self.connect_btn_list):
                    # btn.configure(command = lambda gui_class = self.load_gui_class[i],\
                    #     nSelCamIndex = int(i), mv_camera = self.mv_camera_list[i], tk_btn = btn, tk_display = self.display_gui_list[i]:\
                    #     self.connect_func(gui_class, nSelCamIndex, mv_camera, tk_btn, tk_display))
                    btn.configure(command = self.custom_lambda_connect_btn(gui_class = self.load_gui_class[i],
                        nSelCamIndex = int(i), mv_camera = self.mv_camera_list[i], tk_btn = btn, tk_display = self.display_gui_list[i]))

                if len(invoke_dictionary) != 0:
                    for i in range(len(self.hikvision_devList)):
                        _serial = self.hikvision_get_cam_serial(self.hikvision_devList[i])
                        for serial, _ in invoke_dictionary.items():
                            if _serial == serial:
                                self.connect_btn_list[i].invoke()

        elif len(self.hikvision_devList) == len(self.load_gui_class):
            self.home_func()
            invoke_dictionary = self.connected_serial_id.copy()
            if len(invoke_dictionary) != 0:
                #print('device decreased: ',invoke_dictionary)
                for serial, cam_index in invoke_dictionary.items():
                    self.connect_btn_list[cam_index].invoke()

            if len(self.device_label_list) > 0:
                try:
                    for label in self.device_label_list:
                        label.destroy()
                except Exception:
                    pass

            self.device_label_list *= 0

            self.hikvision_fr.resize_frame(height = self.conn_frame_h)

            if len(self.hikvision_devList) > 0:
                #TO UPDATE THE CONNECTION DICTIONARY WHEN USER PULL OUT THE CONNECTION
                self._serial_list *= 0
                for i in range(len(self.hikvision_devList)):
                    _serial = self.hikvision_get_cam_serial(self.hikvision_devList[i])
                    self._serial_list.append(_serial)
                _serial_checker = set(self._serial_list)
                #print(_serial_checker)
                if len(self.connected_serial_id) > 0:
                    #disconnected_serial_list = [_serial for _serial in list(self.connected_serial_id.copy()) if _serial not in _serial_checker]
                    disconnected_serial_list = [_serial for _serial in list(invoke_dictionary) if _serial not in _serial_checker]
                    #print(disconnected_serial_list)
                    if len(disconnected_serial_list) > 0:
                        for _serial in disconnected_serial_list:
                            del self.connected_serial_id[_serial] # to update the actual dictionary and clear all disconnected ID
                            del invoke_dictionary[_serial] #to update the copy which will be used to invoke the connections again after re-creating widgets

            for i in range(len(self.hikvision_devList)):
                place_y = int(25 + np.multiply(25, int(i)))
                label = tk.Label(self.hikvision_fr.window_fr, text = self.devList[i], font = 'Helvetica 10', bg = 'white')
                label.place(anchor = 'nw', x=25, y = place_y)
                self.device_label_list.append(label)

            for i, btn in enumerate(self.connect_btn_list):
                # btn.configure(command = lambda gui_class = self.load_gui_class[i],\
                #     nSelCamIndex = int(i), mv_camera = self.mv_camera_list[i], tk_btn = btn, tk_display = self.display_gui_list[i]:\
                #     self.connect_func(gui_class, nSelCamIndex, mv_camera, tk_btn, tk_display))
                btn.configure(command = self.custom_lambda_connect_btn(gui_class = self.load_gui_class[i],
                    nSelCamIndex = int(i), mv_camera = self.mv_camera_list[i], tk_btn = btn, tk_display = self.display_gui_list[i]))

            if len(invoke_dictionary) != 0:
                for i in range(len(self.hikvision_devList)):
                    _serial = self.hikvision_get_cam_serial(self.hikvision_devList[i])
                    for serial, _ in invoke_dictionary.items():
                        if _serial == serial:
                            self.connect_btn_list[i].invoke()


    def custom_lambda_connect_btn(self, **arg_):
        return lambda: self.connect_func(**arg_) 

    def connect_func(self, gui_class = None, nSelCamIndex = int(0), mv_camera = None
        , tk_btn = None, tk_display = None):

        if gui_class is not None:
            if gui_class.cam_conn_status == False:
                try:
                    ret = gui_class.open_device(hikvision_device_ID = self.hikvision_devList[nSelCamIndex], nSelCamIndex = nSelCamIndex, mv_camera = mv_camera)
                    if ret == 0:
                        _serial = self.hikvision_get_cam_serial(self.hikvision_devList[nSelCamIndex])
                        self.connected_serial_id[_serial] = nSelCamIndex
                        gui_class.start_grabbing()

                    elif ret != 0:
                        _error_code = To_hex_str(ret)
                        print(_error_code)
                        if _error_code == '80000004':
                            self.enum_devices()
                            #self.normal_refresh_devices()
                            ret = gui_class.open_device(hikvision_device_ID = self.hikvision_devList[nSelCamIndex], nSelCamIndex = nSelCamIndex, mv_camera = mv_camera)
                            if ret == 0:
                                _serial = self.hikvision_get_cam_serial(self.hikvision_devList[nSelCamIndex])
                                self.connected_serial_id[_serial] = nSelCamIndex
                                gui_class.start_grabbing()

                except Exception as e:
                    print(e)
                    pass

                if gui_class.cam_conn_status == False:
                    pass
                elif gui_class.cam_conn_status == True:
                    if tk_btn is not None:
                        try:
                            tk_btn['image'] = self.cam_connect_icon
                            tk_btn['anchor'] = 'center'
                        except AttributeError:
                            pass

            elif gui_class.cam_conn_status == True:
                try:
                    gui_class.close_device()
                except Exception:
                    pass

                try:
                    _serial = self.hikvision_get_cam_serial(self.hikvision_devList[nSelCamIndex])
                    del self.connected_serial_id[_serial]
                except Exception:
                    pass

                if gui_class.cam_conn_status == True:
                    pass
                elif gui_class.cam_conn_status == False:
                    gui_class.cam_popout_close()
                    if tk_btn is not None:
                        try:
                            tk_btn['image'] = self.cam_disconnect_icon
                            tk_btn['anchor'] = 'center'
                        except AttributeError:
                            pass

                    if tk_display is not None:
                        try:
                            tk_display.create_image(self.cam_display_width/2, self.cam_display_height/2, image='', anchor='center', tags='img')
                            tk_display.image = ''
                        except AttributeError:
                            pass

    def hikvision_check_cam_serial(self):
        self.cam_serial_checker *=0
        self.init_enum_bool = False
        #print('self.cam_serial_list: ',self.cam_serial_list)
        if len(self.hikvision_devList) != 0:
            for i in range(len(self.hikvision_devList)):
                strSerialNumber = self.hikvision_get_cam_serial(self.hikvision_devList[i])
                print(strSerialNumber)

                self.cam_serial_checker.append(strSerialNumber)

        if len(self.cam_serial_checker) == len(self.cam_serial_list):
            for i, serial in enumerate (self.cam_serial_list):
                if serial != self.cam_serial_checker[i]: #this is assuming that HikVision Enum function is always sorted the same way
                    self.init_enum_bool = True
                    break
                else:
                    self.init_enum_bool = False

        elif len(self.cam_serial_checker) != len(self.cam_serial_list):
            self.init_enum_bool = True

        #print('self.init_enum_bool: ',self.init_enum_bool)

    def hikvision_get_cam_serial(self, arg = None):
        if arg is not None:
            try:
                if arg.nTLayerType == MV_GIGE_DEVICE:
                    strSerialNumber = ''
                    for per in arg.SpecialInfo.stGigEInfo.chSerialNumber:
                        if per == 0:
                            break
                        strSerialNumber = strSerialNumber + chr(per)

                    return strSerialNumber

                elif arg.nTLayerType == MV_USB_DEVICE:
                    strSerialNumber = ''
                    for per in arg.SpecialInfo.stUsb3VInfo.chSerialNumber:
                        if per == 0:
                            break
                        strSerialNumber = strSerialNumber + chr(per)

                    return strSerialNumber

                else:
                    return None

            except Exception:
                return None
        else:
            return None

    def gen_camera_disp_canvas(self, master, label_text,label_bg, label_fg,
        canvas_width, canvas_height, canvas_bg, ordinal_index, place_index):
        #ordinal index: used to determine the detected camera index
        #place index: used to determine how/where to place the display widget

        if (int(ordinal_index) % 2) == 0:
            frame_x = 0
            frame_y = 0 + np.multiply((canvas_height+25+2+10), place_index)

        elif (int(ordinal_index) % 2) != 0:
            frame_x = 0 + canvas_width+2+10
            frame_y = 0 + np.multiply((canvas_height+25+2+10), place_index)

        tk_frame_holder = tk.Frame(master, width = canvas_width + 10, height = canvas_height + 25 + 10, bg = 'white')
        tk_frame_holder['highlightcolor'] = 'orange'
        tk_frame_holder['highlightthickness'] = 5
        tk_frame_holder['highlightbackground'] = 'white'

        tk_frame_holder.place(x = frame_x, y = frame_y)

        label_widget = tk.Label(tk_frame_holder, text = label_text, font = 'Helvetica 12 bold', bg = label_bg, fg = label_fg)
        label_widget.place(x=0, y= 0)

        canvas_widget = tk.Canvas(tk_frame_holder, width = canvas_width, height = canvas_height, bg = canvas_bg, highlightthickness = 0)
        canvas_widget.place(x=0, y=25)

        total_frame_height = 0 + np.multiply((canvas_height+25+2+10), place_index + 1)
        return canvas_widget, tk_frame_holder, total_frame_height

    def display_GUI(self):
        self.scroll_cam_disp.resize_frame(height = 900)

        if len(self.fr_display_list) > 0:
            for frame in self.fr_display_list:
                for widget in frame.winfo_children():
                    widget.destroy()
                frame.destroy()

        self.display_gui_list *= 0
        self.fr_display_list *= 0
        # _parent = self.tk_frame_cam_disp 
        _parent = self.scroll_cam_disp.window_fr
        place_index = 0

        if len(self.hikvision_devList) > 0:
            for i in range(len(self.hikvision_devList)): #ideally we need to use a list of connected device(s) not detected device(s)
            # for i in range(20):
                if (int(i) % 2) == 0 and int(i) > 0:
                    place_index += 1
                else:
                    pass

                _disp, _parent_frame, total_frame_height = self.gen_camera_disp_canvas(_parent, 'Camera ' + str(i+1), 'snow3', 'black',
                    self.cam_display_width, self.cam_display_height, 'snow3', int(i), int(place_index))

                _parent_frame.bind("<1>", self.custom_lambda_leftclick(_parent_frame))
                _disp.bind("<1>", self.custom_lambda_leftclick(_parent_frame))

                self.display_gui_list.append(_disp)
                self.fr_display_list.append(_parent_frame)

            if total_frame_height > self.scroll_cam_disp.frame_h:
                self.scroll_cam_disp.resize_frame(height = total_frame_height)

        place_index = 0

    def custom_lambda_leftclick(self, arg_):
        return lambda event: self.double_click_event(event, arg_) 

    def double_click_event(self, event = None, widget=None):
        if self.curr_widget == widget:
            if self.click_tracker < 1:
                self.click_tracker += 1
            elif self.click_tracker >= 1:
                self.click_tracker = 0
                #print('Double Click Success...')
                self.open_disp_ctrl_panel(widget)

        elif self.curr_widget != widget:
            self.click_tracker = 0

        widget.focus_set()

        self.curr_widget = widget


    def open_disp_ctrl_panel(self, tk_disp_id):
        self.home_mode = False
        if len(self.fr_display_list) > 0:
            for i, tk_id in enumerate(self.fr_display_list):
                if tk_disp_id == tk_id:
                    self.disp_index = i
                    break

            self.ctrl_panel_gui.place(relwidth = 1, relheight =1, x=0,y=0)
            self.show_camera_control()
            #self.load_gui_class[self.disp_index].show_camera_control()
            #print('Camera ID: ', self.disp_index + 1)

    def enum_devices(self):
        self.devList *= 0 #init the list again since it is running in a loop #We use this list for display purposes on the GUI
        self.hikvision_devList *= 0 #We pass this list to the Open Device Function in Hikvision Library
        self.cam_serial_list *= 0

        self.deviceList = MV_CC_DEVICE_INFO_LIST()
        self.tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
        ret = MvCamera.MV_CC_EnumDevices(self.tlayerType, self.deviceList)
        if ret != 0:
            print('No Devices')
            pass

        hikvision_cam_index = int(0)
        for i in range(0, self.deviceList.nDeviceNum):
            mvcc_dev_info = cast(self.deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            #print(mvcc_dev_info.SpecialInfo.stGigEInfo.chDeviceVersion)
            #print(mvcc_dev_info.nTLayerType, MV_GIGE_DEVICE)
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
                #print ("\ngige device: [%d]" % i)
                str_manufacturer = ""
                # chDeviceVersion
                # chManufacturerName
                # chModelName
                # chSerialNumber
                for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chManufacturerName: 
                    if per != 0:
                        str_manufacturer = str_manufacturer + chr(per)
                
                #print(str_manufacturer, len(str_manufacturer))
                if str_manufacturer == "Hikvision" or str_manufacturer == "Hikrobot": #"Hikvision" "Hikrobot"
                #if str_manufacturer ==  "Crevis Co., LTD":
                    strModeName = ""
                    for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                        strModeName = strModeName + chr(per)
                    #print ("device model name: %s" % strModeName)

                    nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                    nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                    nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                    nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                    #print ("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
                    #self.devList.append("Gige["+str(i)+"]:"+str(nip1)+"."+str(nip2)+"."+str(nip3)+"."+str(nip4))

                    strSerialNumber = ""
                    for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chSerialNumber:
                        if per == 0:
                            break
                        strSerialNumber = strSerialNumber + chr(per)

                    self.cam_serial_list.append(strSerialNumber)

                    self.devList.append("Gige["+str(hikvision_cam_index)+"] " + str(nip1)+"."+str(nip2)+"."+str(nip3)+"."+str(nip4) )
                    self.hikvision_devList.append(mvcc_dev_info)
                    hikvision_cam_index += 1

            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                #print ("\nu3v device: [%d]" % i)
                str_manufacturer = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chManufacturerName:
                    if per != 0:
                        str_manufacturer = str_manufacturer + chr(per)
                #print(len(str_manufacturer))
                if str_manufacturer == "Hikvision" or str_manufacturer == "Hikrobot": #"Hikvision" "Hikrobot"
                    strModeName = ""
                    for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                        if per == 0:
                            break
                        strModeName = strModeName + chr(per)
                    #print ("device model name: %s" % strModeName)

                    strSerialNumber = ""
                    for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                        if per == 0:
                            break
                        strSerialNumber = strSerialNumber + chr(per)

                    self.cam_serial_list.append(strSerialNumber)
                    #print ("user serial number: %s" % strSerialNumber)
                    #self.devList.append("USB["+str(i)+"] "+str(strSerialNumber))
                    self.devList.append("USB["+str(hikvision_cam_index)+"] " + strModeName + ' (' + str(strSerialNumber) +')')
                    self.hikvision_devList.append(mvcc_dev_info)
                    hikvision_cam_index += 1