import os
from os import path

import tkinter as tk

from PIL import ImageTk, Image
import numpy as np
import subprocess
from functools import partial

from Tk_MsgBox.custom_msgbox import Ask_Msgbox, Info_Msgbox, Error_Msgbox, Warning_Msgbox
from Tk_Custom_Widget.ScrolledCanvas import ScrolledCanvas

from misc_module.image_resize import img_resize_dim, opencv_img_resize, pil_img_resize, open_pil_img
from misc_module.tk_img_module import *
from misc_module.tool_tip import CreateToolTip

from Light_Module.Light_Connect import Light_Connect
from Cam_Module.Camera_Connect import Camera_Connect

from Report_Module.Report_GUI import Report_GUI
from WebSrc_Module.WebResource_GUI import WebResource_GUI

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
    def __init__(self, master, window_icon = None):
        self.window_icon = window_icon

        self.master = master
        self.img_PATH = os.getcwd()
        self.load_TMS_logo()
        self.load_icon_src()
        self.load_light_src()

        self.top_frame = tk.Frame(master = self.master, bg = 'midnight blue'
            , highlightbackground = 'midnight blue')
        self.top_frame['height'] = 85
        self.top_frame.place(x = 0, y = 0
            , relwidth = 1, width = self.top_frame['width']
            , height = self.top_frame['height'], anchor = 'nw')
        self.top_frame.grid_rowconfigure(index = 0, weight = 1)
        self.top_frame.grid_rowconfigure(index = 1, weight = 1)
        self.top_frame.grid_columnconfigure(index = 3, weight = 1)

        tk_lb = tk.Label(self.top_frame, bg = 'white')
        tk_img_insert(tk_lb, self.tms_logo, img_width = 130
                            , img_height = 79
                            , pil_filter = Image.ANTIALIAS)

        tk_lb.grid(row = 0, column = 0, rowspan = 2, ipady = 1, ipadx = 1, sticky = 'nwse')

        self.menu_frame = tk.Frame(master = self.master, bg = 'blue'
            , highlightbackground = 'blue') #width = 44, height = 555
        self.menu_frame_w = 33 #44
        self.menu_frame['width'] = self.menu_frame_w
        self.menu_frame.place(x = 0, y = 85, relheight = 1, height = -85, anchor = 'nw')


        self.light_main_gui = ScrolledCanvas(master = self.master, frame_w = 1150, frame_h = 980
            , canvas_x = self.menu_frame_w, canvas_y = 85, bg = 'white'
            , hbar_x = self.menu_frame_w)

        self.cam_main_fr = ScrolledCanvas(master = self.master, frame_w = 1000, frame_h = 820
            , canvas_x = self.menu_frame_w, canvas_y = 85, bg='white'
            , hbar_x = self.menu_frame_w)

        self.report_main_fr = ScrolledCanvas(master = self.master, frame_w = 970, frame_h = master.winfo_height() - 85
            , canvas_x = self.menu_frame_w, canvas_y = 85, bg = 'white'
            , hbar_x = self.menu_frame_w)
        self.report_main_fr.scrolly.place_forget()

        self.resource_main_fr = ScrolledCanvas(master = self.master, frame_w = self.master.winfo_width()-self.menu_frame_w, frame_h = self.master.winfo_height()-85, 
            canvas_x = self.menu_frame_w, canvas_y = 85, bg = 'white'
            , hbar_x = self.menu_frame_w)

        self.__subframe_list = [  self.light_main_gui
                                , self.cam_main_fr
                                , self.report_main_fr
                                , self.resource_main_fr]

        self.cam_gui_bbox = tk.Frame(self.master, bg = 'white') ## GUI Bounding box to track the size of the window for layout change(s)
        self.cam_gui_bbox.place(x = self.menu_frame_w, y = 85, relwidth = 1, relheight = 1
            , width = -self.menu_frame_w-18, height = -85-18, anchor = 'nw') ## -18 is the space occupied by the scrollbars(horizontal & vertical)

        self.__gui_bbox_dict = {}
        d = self.__gui_bbox_dict
        d[self.cam_gui_bbox] = self.cam_gui_bbox.place_info()## Retrieve all the place information of a widget (e.g. x, y, relx, rely, relwidth, relheight, etc.)

        self.place_gui_bbox()

        main_GUI.class_report_gui = Report_GUI(self.report_main_fr.window_fr, scroll_canvas_class = self.report_main_fr
            , gui_graphic = dict( toggle_ON_btn_img = self.toggle_on_icon, toggle_OFF_btn_img = self.toggle_off_icon
                                , save_icon = self.save_icon, close_icon = self.close_icon
                                , up_arrow_icon = self.up_arrow_icon, down_arrow_icon = self.down_arrow_icon
                                , refresh_icon = self.refresh_icon
                                , text_icon = self.text_icon
                                , window_icon = self.window_icon
                                , folder_icon = self.folder_icon
                                )
            )
        main_GUI.class_report_gui.place(relwidth = 1, relheight =1, x=0,y=0)


        main_GUI.class_light_conn = Light_Connect(self.master, self.top_frame, self.light_main_gui
            , gui_graphic = dict(
                tms_logo = self.tms_logo, infinity_icon = self.infinity_icon, window_icon = self.window_icon
                )
            , model_img = dict(
                img_KP = self.img_KP, img_4CH = self.img_4CH
                , img_16CH = self.img_16CH, img_RGBW = self.img_RGBW
                , img_X10 = self.img_X10, img_X5 = self.img_X5
                , img_OD = self.img_OD, img_SQ = self.img_SQ
                , img_LC20 = self.img_LC20
                ))

        main_GUI.class_cam_conn = Camera_Connect(self.master, self.top_frame, self.cam_main_fr, self.cam_gui_bbox
            , light_class = main_GUI.class_light_conn
            , gui_graphic = dict(
                              tms_logo = self.tms_logo, cam_disconnect_img = self.disconn_icon
                            , toggle_ON_button_img = self.toggle_on_icon, toggle_OFF_button_img = self.toggle_off_icon
                            , img_flip_icon = self.flip_icon, record_start_icon = self.rec_start_icon, record_stop_icon = self.rec_stop_icon
                            , save_icon = self.save_icon, popout_icon = self.popout_icon, info_icon = self.info_icon, fit_to_display_icon = self.fit_screen_icon
                            , setting_icon = self.setting_icon, window_icon = self.window_icon
                            , inspect_icon = self.inspect_icon, help_icon = self.help_icon, add_icon = self.add_icon, minus_icon = self.minus_icon
                            , close_icon = self.close_icon, video_cam_icon = self.video_icon, refresh_icon = self.refresh_icon, folder_impil = self.folder_icon
                            )
            )

        self.class_resource_gui = WebResource_GUI(self.resource_main_fr.window_fr, scroll_canvas_class = self.resource_main_fr)
        self.class_resource_gui.place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 1, relheight = 1)

        self.light_ctrl_btn     = tk.Button(self.menu_frame, relief = tk.GROOVE, activebackground = 'navy', bg = 'royal blue')
        self.camera_ctrl_btn    = tk.Button(self.menu_frame, relief = tk.GROOVE, activebackground = 'navy', bg = 'royal blue')
        self.report_ctrl_btn    = tk.Button(self.menu_frame, relief = tk.GROOVE, activebackground = 'navy', bg = 'royal blue')
        self.web_resource_btn   = tk.Button(self.menu_frame, relief = tk.GROOVE, activebackground = 'navy', bg = 'royal blue')
        
        tk_img_insert(self.light_ctrl_btn    , self.light_icon    , img_width = 26, img_height = 26)
        tk_img_insert(self.camera_ctrl_btn   , self.cam_icon      , img_width = 26, img_height = 26)
        tk_img_insert(self.report_ctrl_btn   , self.report_icon   , img_width = 26, img_height = 26)
        tk_img_insert(self.web_resource_btn  , self.web_icon      , img_width = 26, img_height = 26)


        self.__ctrl_btn_dict = {}
        hmap = self.__ctrl_btn_dict
        hmap[self.light_ctrl_btn]       = self.light_ctrl_btn_state
        hmap[self.camera_ctrl_btn]      = self.cam_ctrl_btn_state
        hmap[self.report_ctrl_btn]      = self.report_ctrl_btn_state
        hmap[self.web_resource_btn]     = self.resource_btn_state


        CreateToolTip(self.light_ctrl_btn, 'Light Control'
            , 32, -5, font = 'Tahoma 11')
        CreateToolTip(self.camera_ctrl_btn, 'Camera Control'
            , 32, -5, font = 'Tahoma 11')
        CreateToolTip(self.report_ctrl_btn, 'Report Generation'
            , 32, -5, font = 'Tahoma 11')
        CreateToolTip(self.web_resource_btn, 'Additional Resources'
            , 32, -5, font = 'Tahoma 11')

        self.light_ctrl_btn.grid(row = 0, column = 0, columnspan = 1, ipadx = 1, ipady = 1, sticky = 'nwse')
        self.camera_ctrl_btn.grid(row = 1, column = 0, columnspan = 1, ipadx = 1, ipady = 1, sticky = 'nwse')
        self.report_ctrl_btn.grid(row = 2, column = 0, columnspan = 1, ipadx = 1, ipady = 1, sticky = 'nwse')
        self.web_resource_btn.grid(row = 3, column = 0, columnspan = 1, ipadx = 1, ipady = 1, sticky = 'nwse')

        self.light_ctrl_btn_state()

    def load_TMS_logo(self):
        self.tms_logo = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "Logo.png")

    def load_icon_src(self):
        self.light_icon      = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "led (1).png")
        self.cam_icon        = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "Camera.png")
        self.multi_cam_icon  = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "multi_cam_icon_4.png")
        self.img_icon        = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "image1.png")
        self.report_icon     = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "clipboard (1).png")
        self.web_icon        = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "web_resource.png")
        self.infinity_icon   = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "infinity_2.png")
        self.info_icon       = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "info.png")
        self.flip_icon       = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "flip-arrow-icon.jpg")
        self.video_icon      = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "video_cam_icon.png")
        self.rec_start_icon  = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "recording11.png")
        self.rec_stop_icon   = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "stop11.png")
        self.fit_screen_icon = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "fit_to_screen.png")
        self.save_icon       = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "diskette.png")
        self.popout_icon     = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "popout.png")
        self.refresh_icon    = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "right.png")
        self.disconn_icon    = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "transDC_2.png")
        self.conn_icon       = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "connect_icon.png", RGBA_format = True)
        self.setting_icon    = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "settings.png")
        self.inspect_icon    = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "inspect_icon.png")
        self.add_icon        = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "plus-flat.png")
        self.minus_icon      = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "minus-flat.png")
        self.help_icon       = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "Help.png")
        self.close_icon      = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "close.png")
        self.up_arrow_icon   = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "up_arrow.png")
        self.down_arrow_icon = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "down_arrow.png")
        self.text_icon       = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "text_icon.png")
        self.folder_icon     = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "folder.png")
        self.toggle_on_icon  = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "on icon.png")
        self.toggle_off_icon = open_pil_img(img_PATH = self.img_PATH, img_folder = "TMS Icon", img_file = "off icon.png")

    def load_light_src(self):
        self.img_KP   = open_pil_img(img_PATH = self.img_PATH + "\\LC-18 Picture GUI", img_folder = "LC-18-4CH-KP1"         , img_file = "Whole View.jpg")
        self.img_4CH  = open_pil_img(img_PATH = self.img_PATH + "\\LC-18 Picture GUI", img_folder = "LC-18-4CH-A1"          , img_file = "Whole View.jpg")
        self.img_16CH = open_pil_img(img_PATH = self.img_PATH + "\\LC-18 Picture GUI", img_folder = "LC-18-16CH-A1"         , img_file = "Whole View.jpg")
        self.img_RGBW = open_pil_img(img_PATH = self.img_PATH + "\\LC-18 Picture GUI", img_folder = "LC-18-4CH-RGBW"        , img_file = "Full View.jpg")
        self.img_X10  = open_pil_img(img_PATH = self.img_PATH + "\\LC-18 Picture GUI", img_folder = "LC-18-1CH-X10"         , img_file = "Whole View.png")
        self.img_X5   = open_pil_img(img_PATH = self.img_PATH + "\\LC-18 Picture GUI", img_folder = "LC-18-2CH-X5"          , img_file = "Whole View.jpg")
        self.img_OD   = open_pil_img(img_PATH = self.img_PATH + "\\LC-18 Picture GUI", img_folder = "LC-18-OD-4CH-X2-48V"   , img_file = "full view.jpg")
        self.img_SQ   = open_pil_img(img_PATH = self.img_PATH + "\\LC-18 Picture GUI", img_folder = "LC-18-SQ-4CH-A1"       , img_file = "Whole View.jpg")
        self.img_LC20 = open_pil_img(img_PATH = self.img_PATH + "\\LC-18 Picture GUI", img_folder = "LC-20-16CH-A1"         , img_file = "LC-20-16CH-A1.png")

    def __dummy_event(self, event):
        return "break"

    def ctrl_btn_state_func(self, target_btn):
        for ctrl_btn, btn_command in self.__ctrl_btn_dict.items():
            if ctrl_btn == target_btn:
                ctrl_btn['command'] = partial(self.__dummy_event, event = None)
                ctrl_btn['bg'] = 'navy'
            else:
                ctrl_btn['command'] = btn_command
                ctrl_btn['bg'] = 'royal blue'

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
                        tk_frame.show(*args, **kwargs)
                    elif target_place == False:
                        tk_frame.hide()

                else:
                    tk_frame.hide()

            elif (isinstance(tk_frame, tk.Frame)) == True:
                if tk_frame == target_frame:
                    if target_place == True:
                        tk_frame.place(*args, **kwargs)
                    elif target_place == False:
                        tk_frame.place_forget()

                else:
                    tk_frame.place_forget()

    def top_frame_btn_hide(self):
        main_GUI.class_light_conn.light_menu_btn_hide()
        main_GUI.class_light_conn.light_info_hide()

        main_GUI.class_cam_conn.cam_connect_btn_hide()

    def light_ctrl_btn_state(self):
        self.ctrl_btn_state_func(self.light_ctrl_btn)
        self.place_gui_bbox()

        if main_GUI.class_light_conn.light_conn_status == False:
            self.show_subframe_func(target_frame = self.light_main_gui, target_place = False)

        elif main_GUI.class_light_conn.light_conn_status == True:
            self.show_subframe_func(target_frame = self.light_main_gui)

        self.top_frame_btn_hide()
        main_GUI.class_light_conn.light_menu_btn_show()
        main_GUI.class_light_conn.light_info_show()

        main_GUI.class_cam_conn.stop_auto_toggle_parameter()
        main_GUI.class_cam_conn.record_setting_close()

        main_GUI.class_report_gui.btn_blink_stop()

    def cam_ctrl_btn_state(self):
        self.ctrl_btn_state_func(self.camera_ctrl_btn)
        self.place_gui_bbox(self.cam_gui_bbox)

        self.show_subframe_func(target_frame = self.cam_main_fr)
        
        self.top_frame_btn_hide()
        main_GUI.class_cam_conn.cam_connect_btn_state()
        main_GUI.class_cam_conn.cam_gui_update()

        main_GUI.class_cam_conn.start_auto_toggle_parameter()

        main_GUI.class_report_gui.btn_blink_stop()

    def report_ctrl_btn_state(self):
        self.ctrl_btn_state_func(self.report_ctrl_btn)
        self.place_gui_bbox()

        self.show_subframe_func(target_frame = self.report_main_fr, scroll_y = False)
        
        self.top_frame_btn_hide()

        main_GUI.class_cam_conn.stop_auto_toggle_parameter()
        main_GUI.class_cam_conn.record_setting_close()

        main_GUI.class_report_gui.btn_blink_start()

    def resource_btn_state(self):
        self.ctrl_btn_state_func(self.web_resource_btn)
        self.place_gui_bbox()

        self.show_subframe_func(target_frame = self.resource_main_fr, scroll_x = False)

        self.top_frame_btn_hide()

        main_GUI.class_cam_conn.stop_auto_toggle_parameter()
        main_GUI.class_cam_conn.record_setting_close()

        main_GUI.class_report_gui.btn_blink_stop()

    def close_all(self):
        ask_msgbox = Ask_Msgbox('Do you want to quit?', title = 'Quit', parent = self.master, message_anchor = 'w')
        if ask_msgbox.ask_result() == True:
            main_GUI.class_light_conn.light_disconnect()
            main_GUI.class_cam_conn.cam_quit_func()
            self.master.destroy()
