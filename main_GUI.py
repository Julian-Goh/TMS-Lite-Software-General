import os
from os import path

import tkinter as tk
from tkinter import ttk

from Tk_MsgBox.custom_msgbox import Ask_Msgbox, Info_Msgbox, Error_Msgbox, Warning_Msgbox

from PIL import ImageTk, Image
import numpy as np
import subprocess
from functools import partial

from image_resize import img_resize_dim, opencv_img_resize, pil_img_resize, pil_icon_resize

from ScrolledCanvas import ScrolledCanvas

from Light_Connect import Light_Connect
from Camera_Connect import Camera_Connect

from Report_GUI import Report_GUI
from WebResource_GUI import WebResource_GUI

from tool_tip import CreateToolTip

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

class main_GUI():
    def __init__(self, master, LC18_lib, LC18KP_lib, LC18SQ_lib, LC20_lib = None, window_icon = None):
        self.LC18_lib = LC18_lib
        self.LC18KP_lib = LC18KP_lib
        self.LC18SQ_lib = LC18SQ_lib

        self.LC20_lib = LC20_lib
        self.window_icon = window_icon

        self.master = master
        self.img_PATH = os.getcwd()
        self.load_TMS_logo()
        self.load_icon_img()
        self.load_light_img()
        self.load_camera_img()

        self.top_frame = tk.Frame(master = self.master, bg = 'midnight blue'
            , highlightbackground = 'midnight blue', highlightthickness = 1) # width = 1080, height = 85
        self.top_frame['height'] = 85
        self.top_frame.place(relwidth = 1, relx = 0, rely =0)

        tk.Label(self.top_frame, image = self.tms_logo).place(x=0, y=0)

        self.icon_frame = tk.Frame(master = self.master, bg = 'blue'
            , highlightbackground = 'blue', highlightthickness = 1) #width = 44, height = 555
        self.icon_frame_W = 33 #44
        self.icon_frame['width'] = self.icon_frame_W
        self.icon_frame.place(relheight = 1, x = 0, y = 85, height = -85)

        self.light_main_fr = ScrolledCanvas(master = self.master, frame_w = 1127, frame_h = 900, 
            canvas_x = self.icon_frame_W, canvas_y = 85, window_bg = 'white', canvas_bg='white'
            , hbar_x = self.icon_frame_W)

        self.cam_main_fr = ScrolledCanvas(master = self.master, frame_w = 950, frame_h = 820,
            canvas_x = self.icon_frame_W, canvas_y = 85, window_bg = 'white', canvas_bg='white', canvas_highlightthickness = 0
            , hbar_x = self.icon_frame_W)

        self.report_main_fr = ScrolledCanvas(master = self.master, frame_w = 970, frame_h = master.winfo_height() - 85, 
            canvas_x = self.icon_frame_W, canvas_y = 85, window_bg = 'white', canvas_highlightthickness = 0
            , hbar_x = self.icon_frame_W)
        self.report_main_fr.scrolly.place_forget()

        self.resource_main_fr = ScrolledCanvas(master = self.master, frame_w = self.master.winfo_width()-self.icon_frame_W, frame_h = self.master.winfo_height()-85, 
            canvas_x = self.icon_frame_W, canvas_y = 85, window_bg = 'white', canvas_highlightthickness = 0
            , hbar_x = self.icon_frame_W)

        self.__subframe_list = [self.light_main_fr
                                , self.cam_main_fr
                                , self.report_main_fr
                                , self.resource_main_fr]

        self.cam_gui_bbox = tk.Frame(self.master, bg = 'white') ## GUI Bounding box to track the size of the window for layout change(s)
        self.cam_gui_bbox.place(x = self.icon_frame_W, y = 85, relwidth = 1, relheight = 1
            , width = -self.icon_frame_W-18, height = -85-18, anchor = 'nw') ## -18 is the space occupied by the scrollbars(horizontal & vertical)

        self.__gui_bbox_dict = {}
        self.__gui_bbox_dict[self.cam_gui_bbox] = self.cam_gui_bbox.place_info()## Retrieve all the place information of a widget (e.g. x, y, relx, rely, relwidth, relheight, etc.)

        self.place_gui_bbox()

        main_GUI.class_report_gui = Report_GUI(self.report_main_fr.window_fr, scroll_canvas_class = self.report_main_fr
            , toggle_ON_btn_img = self.toggle_ON_button_img
            , toggle_OFF_btn_img = self.toggle_OFF_button_img
            , save_impil = self.save_impil
            , close_impil = self.close_impil
            , up_arrow_icon = self.up_arrow_icon
            , down_arrow_icon = self.down_arrow_icon
            , refresh_impil = self.refresh_impil
            , text_icon = self.text_icon
            , folder_impil = self.folder_impil
            , window_icon = self.window_icon)
        main_GUI.class_report_gui.place(relwidth = 1, relheight =1, x=0,y=0)

        main_GUI.class_light_conn = Light_Connect(self.master, self.top_frame, self.light_main_fr, 1127, 900
            , self.LC18_lib, self.LC18KP_lib, self.LC18SQ_lib, self.tms_logo_2, self.infinity_icon
            , self.img_KP, self.img_4CH, self.img_16CH, self.img_RGBW, self.img_X10, self.img_X5, self.img_OD, self.img_SQ, self.img_LC20_16CH, self.LC20_lib
            , self.window_icon)

        main_GUI.class_cam_conn = Camera_Connect(self.master, self.top_frame, self.cam_main_fr, self.cam_gui_bbox
            , self.tms_logo_2, self.cam_disconnect_img
            , self.toggle_ON_button_img, self.toggle_OFF_button_img, self.img_flip_icon, self.record_start_icon, self.record_stop_icon, self.save_icon
            , self.popout_icon, self.info_icon, self.fit_to_display_icon, self.setting_icon, self.window_icon
            , inspect_icon= self.inspect_icon, help_icon = self.help_icon, add_icon = self.add_icon, minus_icon = self.minus_icon
            , close_icon = self.close_icon, video_cam_icon = self.video_cam_icon, refresh_icon = self.refresh_icon, folder_impil = self.folder_impil)

        self.class_resource_gui = WebResource_GUI(self.resource_main_fr.window_fr, scroll_canvas_class = self.resource_main_fr)
        self.class_resource_gui.place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 1, relheight = 1)

        self.light_ctrl_btn = tk.Button(self.icon_frame, relief = tk.GROOVE, activebackground = 'navy', bg = 'royal blue', image=self.light_icon)
        self.camera_ctrl_btn = tk.Button(self.icon_frame, relief = tk.GROOVE, activebackground = 'navy', bg = 'royal blue', image=self.camera_icon)
        self.report_ctrl_btn = tk.Button(self.icon_frame, relief = tk.GROOVE, activebackground = 'navy', bg = 'royal blue', image=self.report_icon)

        self.web_resource_btn = tk.Button(self.icon_frame, relief = tk.GROOVE, activebackground = 'navy', bg = 'royal blue', image=self.web_resource_icon)
        
        self.__ctrl_btn_list = [self.light_ctrl_btn
                                , self.camera_ctrl_btn
                                , self.report_ctrl_btn
                                , self.web_resource_btn]

        self.light_ctrl_btn['command'] = self.light_ctrl_btn_state
        self.camera_ctrl_btn['command'] = self.cam_ctrl_btn_state
        self.report_ctrl_btn['command'] = self.report_ctrl_btn_state
        self.web_resource_btn['command'] = self.resource_btn_state

        self.light_ctrl_btn['state'] = 'disabled'
        self.camera_ctrl_btn['state'] = 'normal'
        self.report_ctrl_btn['state'] = 'normal'
        self.web_resource_btn['state'] = 'normal'

        CreateToolTip(self.light_ctrl_btn, 'Light Control'
            , 32, -5, font = 'Tahoma 11')
        CreateToolTip(self.camera_ctrl_btn, 'Camera Control'
            , 32, -5, font = 'Tahoma 11')
        CreateToolTip(self.report_ctrl_btn, 'Report Generation'
            , 32, -5, font = 'Tahoma 11')
        CreateToolTip(self.web_resource_btn, 'Additional Resources'
            , 32, -5, font = 'Tahoma 11')

        self.light_ctrl_btn.place(x=0, y=0)
        self.camera_ctrl_btn.place(x= 0, y = 31)
        self.report_ctrl_btn.place(x= 0, y = 62)
        self.web_resource_btn.place(x= 0, y = 93)

        # self.web_resource_btn.place(relx=0, rely=1, y = -20, anchor = 'sw')

        self.light_ctrl_btn_state()


    def load_TMS_logo(self):
        ### pil_filter, Image.: NEAREST, BILINEAR, BICUBIC and ANTIALIAS

        # self.tms_logo, tms_logo_src = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "TMS logo PNG(2).png", img_height = 79)
        self.tms_logo, tms_logo_src = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "Logo.png"
            , img_width = 130
            , img_height = 79
            , pil_filter = Image.ANTIALIAS)
        tms_logo_resize = pil_img_resize(tms_logo_src, img_height = 110)
        self.tms_logo_2 = ImageTk.PhotoImage(tms_logo_resize)

        del tms_logo_src, tms_logo_resize

    def load_icon_img(self):
        self.light_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "led (1).png", img_width = 26, img_height =26)
        self.camera_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "Camera.png", img_width = 26, img_height =26)
        self.multi_camera_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "multi_cam_icon_4.png", img_width = 26, img_height =26)
        self.imgproc_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "image1.png", img_width = 26, img_height =26)
        self.report_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "clipboard (1).png", img_width = 26, img_height =26)
        self.web_resource_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "web_resource.png", img_width = 26, img_height =26)

        self.infinity_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "infinity_2.png", img_scale = 0.04)
        self.info_icon, _ = pil_icon_resize(img_PATH = os.getcwd(), img_folder = "TMS Icon", img_file = "info.png", img_scale = 0.13)

        self.img_flip_icon, _ = pil_icon_resize(img_PATH = os.getcwd(), img_folder = "TMS Icon", img_file = "flip-arrow-icon.jpg", img_scale = 0.033)

        self.video_cam_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "video_cam_icon.png", img_width = 18, img_height =18)

        self.record_start_icon, _ = pil_icon_resize(img_PATH = os.getcwd(), img_folder = "TMS Icon", img_file = "recording11.png", img_scale = 0.035)

        self.record_stop_icon, _ = pil_icon_resize(img_PATH = os.getcwd(), img_folder = "TMS Icon", img_file = "stop11.png", img_scale = 0.035)
        
        self.fit_to_display_icon, _ = pil_icon_resize(img_PATH = os.getcwd(), img_folder = "TMS Icon", img_file = "fit_to_screen.png", img_width = 22, img_height =22) #img_scale = 0.04)

        self.save_icon, self.save_impil = pil_icon_resize(img_PATH = os.getcwd(), img_folder = "TMS Icon", img_file = "diskette.png", img_scale = 0.035)

        self.popout_icon, _ = pil_icon_resize(img_PATH = os.getcwd(), img_folder = "TMS Icon", img_file = "popout.png", img_scale = 0.1)

        self.refresh_icon, self.refresh_impil = pil_icon_resize(img_PATH = os.getcwd(), img_folder = "TMS Icon", img_file = "right.png", img_width = 18, img_height =18)

        self.cam_disconnect_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "transDC_2.png", img_width = 18, img_height =18)
        self.cam_connect_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "connect_icon.png", img_width = 18, img_height = 18, RGBA_format = True)

        self.setting_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "settings.png", img_width = 18, img_height =18)

        self.inspect_icon, _ = pil_icon_resize(img_PATH = os.getcwd(), img_folder = "TMS Icon", img_file = "inspect_icon.png", img_scale = 0.025)

        self.add_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "plus-flat.png", img_width = 18, img_height =18)

        self.minus_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "minus-flat.png", img_width = 18, img_height =18)

        self.help_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "Help.png", img_width = 20, img_height =20)

        self.close_icon, self.close_impil = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "close.png", img_width = 20, img_height =20)

        self.up_arrow_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "up_arrow.png", img_width = 20, img_height =20)
        self.down_arrow_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "down_arrow.png", img_width = 20, img_height =20)

        self.text_icon, _ = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "text_icon.png", img_width = 20, img_height =20)
        
        _, self.folder_impil = pil_icon_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "folder.png", img_width = 20, img_height =20)

    def load_light_img(self):
        standard_width = 0#120
        standard_height = 0#120
        standard_scale = 0.03
        self.img_KP, _ = _icon_load_resize(img_PATH = self.img_PATH, img_folder = "LC-18 Picture GUI\\LC-18-4CH-KP1", img_file = "Whole View.jpg", img_scale=standard_scale ,
            img_height = standard_height, img_width = standard_width)
        self.img_4CH, _ = _icon_load_resize(img_PATH = self.img_PATH, img_folder = "LC-18 Picture GUI\\LC-18-4CH-A1", img_file = "Whole View.jpg", img_scale=standard_scale ,
            img_height = standard_height, img_width = standard_width)
        self.img_16CH, _ = _icon_load_resize(img_PATH = self.img_PATH, img_folder = "LC-18 Picture GUI\\LC-18-16CH-A1", img_file = "Whole View.jpg", img_scale=standard_scale ,
            img_height = standard_height, img_width = standard_width)
        self.img_RGBW, _ = _icon_load_resize(img_PATH = self.img_PATH, img_folder = "LC-18 Picture GUI\\LC-18-4CH-RGBW", img_file = "Full View.jpg", img_scale=standard_scale ,
            img_height = standard_height, img_width = standard_width)

        self.img_X10, _ = _icon_load_resize(img_PATH = self.img_PATH, img_folder = "LC-18 Picture GUI\\LC-18-1CH-X10", img_file = "Whole View.png", img_scale=standard_scale ,
            img_height = standard_height, img_width = standard_width)
        self.img_X5, _ = _icon_load_resize(img_PATH = self.img_PATH, img_folder = "LC-18 Picture GUI\\LC-18-2CH-X5", img_file = "Whole View.jpg", img_scale=standard_scale ,
            img_height = standard_height, img_width = standard_width)
        self.img_OD, _ = _icon_load_resize(img_PATH = self.img_PATH, img_folder = "LC-18 Picture GUI\\LC-18-OD-4CH-X2-48V", img_file = "full view.jpg", img_scale=standard_scale ,
            img_height = standard_height, img_width = standard_width)
        self.img_SQ, _ = _icon_load_resize(img_PATH = self.img_PATH, img_folder = "LC-18 Picture GUI\\LC-18-SQ-4CH-A1", img_file = "Whole View.jpg", img_scale=standard_scale ,
            img_height = standard_height, img_width = standard_width)

        self.img_LC20_16CH, _ = _icon_load_resize(img_PATH = self.img_PATH, img_folder = "LC-18 Picture GUI\\LC-20-16CH-A1", img_file = "LC-20-16CH-A1.png", img_scale=standard_scale ,
            img_height = standard_height, img_width = standard_width)

    def load_camera_img(self):
        self.cam_disconnect_img, _ = _icon_load_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "transDC.png", img_width = 250, img_height =250)
        self.toggle_ON_button_img, _ = _icon_load_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "on icon.png", img_scale = 0.06)
        self.toggle_OFF_button_img, _ = _icon_load_resize(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "off icon.png", img_scale = 0.06)

    def ctrl_btn_state_func(self, target_btn):
        for ctrl_btn in self.__ctrl_btn_list:
            if ctrl_btn == target_btn:
                widget_disable(ctrl_btn)
            else:
                widget_enable(ctrl_btn)

    def place_gui_bbox(self, target_bbox = None):
        for gui_bbox, place_info in self.__gui_bbox_dict.items():
            if gui_bbox == target_bbox:
                gui_bbox.place(**place_info)
                gui_bbox.lower()
            else:
                gui_bbox.place_forget()

    def show_subframe_func(self, target_frame, target_place = True, *args, **kwargs):
        for tk_frame in self.__subframe_list:
            if (isinstance(tk_frame, ScrolledCanvas)) == True:
                if tk_frame == target_frame:
                    if target_place == True:
                        tk_frame.rmb_all_func(*args, **kwargs)
                    elif target_place == False:
                        tk_frame.forget_all_func()

                else:
                    tk_frame.forget_all_func()

            elif (isinstance(tk_frame, tk.Frame)) == True:
                if tk_frame == target_frame:
                    if target_place == True:
                        tk_frame.place(*args, **kwargs)
                    elif target_place == False:
                        tk_frame.place_forget()

                else:
                    tk_frame.place_forget()

    def light_ctrl_btn_state(self):
        self.ctrl_btn_state_func(self.light_ctrl_btn)
        self.place_gui_bbox()

        if main_GUI.class_light_conn.light_conn_status == False:
            self.show_subframe_func(target_frame = self.light_main_fr, target_place = False)

        elif main_GUI.class_light_conn.light_conn_status == True:
            self.show_subframe_func(target_frame = self.light_main_fr)

        main_GUI.class_report_gui.btn_blink_stop()

        self.top_frame_btn_manage()

        main_GUI.class_light_conn.top_frame_light_info()

        main_GUI.class_light_conn.light_connect_btn_state()

        main_GUI.class_cam_conn.stop_auto_toggle_parameter()

        main_GUI.class_cam_conn.record_setting_close()


    def cam_ctrl_btn_state(self):
        self.ctrl_btn_state_func(self.camera_ctrl_btn)
        self.place_gui_bbox(self.cam_gui_bbox)

        self.show_subframe_func(target_frame = self.cam_main_fr)

        main_GUI.class_report_gui.btn_blink_stop()

        self.top_frame_btn_manage()
        main_GUI.class_light_conn.forget_light_info()

        main_GUI.class_cam_conn.cam_connect_btn_state()

        main_GUI.class_cam_conn.start_auto_toggle_parameter()


    def report_ctrl_btn_state(self):
        self.ctrl_btn_state_func(self.report_ctrl_btn)
        self.place_gui_bbox()

        self.show_subframe_func(target_frame = self.report_main_fr, scroll_y = False)

        main_GUI.class_report_gui.btn_blink_start()
        
        self.top_frame_btn_manage()

        main_GUI.class_light_conn.forget_light_info()

        main_GUI.class_cam_conn.stop_auto_toggle_parameter()

        main_GUI.class_cam_conn.record_setting_close()


    def resource_btn_state(self):
        self.ctrl_btn_state_func(self.web_resource_btn)
        self.place_gui_bbox()

        self.show_subframe_func(target_frame = self.resource_main_fr, scroll_x = False)

        main_GUI.class_report_gui.btn_blink_stop()

        self.top_frame_btn_manage()
        main_GUI.class_light_conn.forget_light_info()

        main_GUI.class_cam_conn.stop_auto_toggle_parameter()

        main_GUI.class_cam_conn.record_setting_close()

    def top_frame_btn_manage(self):
        main_GUI.class_light_conn.forget_light_connect_btn()
        main_GUI.class_cam_conn.forget_cam_connect_btn()

    def close_all(self):
        ask_msgbox = Ask_Msgbox('Do you want to quit?', title = 'Quit', parent = self.master, message_anchor = 'w')
        if ask_msgbox.ask_result() == True:
            main_GUI.class_light_conn.light_quit_func()
            main_GUI.class_cam_conn.cam_quit_func()

            for widget in self.master.winfo_children(): # Loop through each widget in main window
                if isinstance(widget, tk.Toplevel): # If widget is an instance of toplevel
                    try:
                        widget.destroy()
                    except (tk.TclError):
                        pass
            self.master.destroy()
