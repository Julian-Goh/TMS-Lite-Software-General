import tkinter as tk
from tkinter import ttk

import serial.tools.list_ports    
import re

import numpy as np

import threading
from functools import partial

from Tk_MsgBox.custom_msgbox import Ask_Msgbox, Info_Msgbox, Error_Msgbox, Warning_Msgbox
from Tk_Custom_Widget.ScrolledCanvas import ScrolledCanvas
from Tk_Custom_Widget.tk_custom_toplvl import CustomToplvl
from Tk_Custom_Widget.tk_custom_combobox import CustomBox

from Tk_Validate.tk_validate import Validate_Int, is_number, is_float, is_int
from misc_module.image_resize import img_resize_dim, opencv_img_resize, pil_img_resize, open_pil_img
from misc_module.tk_img_module import to_tk_img, tk_img_insert

from LC_GUI_Lib.LC18_SQ    import LC18_SQ_GUI
from LC_GUI_Lib.LC18_16CH  import LC18_16CH_GUI
from LC_GUI_Lib.LC18_4CH   import LC18_4CH_GUI
from LC_GUI_Lib.LC18_OD    import LC18_OD_GUI
from LC_GUI_Lib.LC18_KP    import LC18_KP_GUI
from LC_GUI_Lib.LC18_RGBW  import LC18_RGBW_GUI
from LC_GUI_Lib.LC18_1CH   import LC18_1CH_GUI
from LC_GUI_Lib.LC18_2CH   import LC18_2CH_GUI

from LC_GUI_Lib.LC20_SQ    import LC20_SQ_GUI

import LC18Library
import LC20Library

def ctrl_model_type(sel_model):
    ctrl_name = "None"

    if sel_model == 'KP':
        ctrl_name = 'LC-18-4CH-KP1'

    elif sel_model == '4CH':
        ctrl_name = 'LC-18-4CH'

    elif sel_model == '16CH':
        ctrl_name = 'LC-18-16CH'

    elif sel_model == 'X10':
        ctrl_name = 'LC-18-1CH'

    elif sel_model == 'X5':
        ctrl_name = 'LC-18-2CH'

    elif sel_model == 'OD':
        ctrl_name = 'LC-18-OD'

    elif sel_model == 'SQ':
        ctrl_name = 'LC-18-SQ'

    elif sel_model == 'RGBW':
        ctrl_name = 'LC-18-4CH-A1-RGBW'

    elif sel_model == 'LC20':
        ctrl_name = 'LC-20-16CH-A1'

    return ctrl_name

def firmware_check(version_var):
    ver_check = version_var.split(".")
    if ver_check[0] == '1':
        if ver_check[1] == '0': #1.0.0.0
            model = '4CH/16CH'
        elif ver_check[1] == '1': #1.1.0.0
            model = 'X10'
        elif ver_check[1] == '2': #1.2.0.0
            model = 'X5'

    elif ver_check[0] == '2': #2.0.0.0
        model = 'OD'
    elif ver_check[0] == '3': #3.0.0.0
        model = 'SQ'
    elif ver_check[0] == '4': #4.0.0.0
        model = 'RGBW'
    elif ver_check[0] == '9': #9.0.0.0
        model = 'KP'
    else:
        model = None

    return model

class Light_Connect():
    def __init__(self, master, top_frame, scrolled_canvas
        , gui_graphic = {}, model_img = {}):

        self.model_img = dict(img_KP = None, img_4CH = None
            , img_16CH = None, img_RGBW = None
            , img_X10 = None, img_X5 = None
            , img_OD = None, img_SQ = None
            , img_LC20 = None)

        for key, item in model_img.items():
            if key in self.model_img:
                self.model_img[key] = item

        self.gui_graphic = dict(tms_logo = None, infinity_icon = None, window_icon = None)

        for key, item in gui_graphic.items():
            if key in self.gui_graphic:
                self.gui_graphic[key] = item

        # print(self.model_img)

        # print(self.gui_graphic)

        self.master = master
        self.top_frame = top_frame
        if isinstance(scrolled_canvas, ScrolledCanvas) != True:
            raise AttributeError("'scrolled_canvas' argument must be a ScrolledCanvas class object")
        self.scrolled_canvas = scrolled_canvas

        self.LC18_lib   = LC18Library.LC18()
        self.LC18KP_lib = LC18Library.LC18KP()
        self.LC18SQ_lib = LC18Library.LC18SQ()
        self.LC20_lib   = LC20Library.LC20SQ()

        print(self.LC18_lib )
        print(self.LC18KP_lib)
        print(self.LC18SQ_lib)
        print(self.LC20_lib)

        self.main_lib = None

        self.thread_event_repeat = threading.Event()
        self.thread_event_repeat_ALL = threading.Event()

        self.m_fw_version_str = None
        self.fw_version_str = None #fw_version_str is in strings type. We initialize them to string None
        self.fw_model = None
        self.fw_model_sel = None
        self.light_info_tk_var = None

        self.COM = self.TCPIP = self.USB = False

        self.TCPIP_str_arr = np.array(['192', '168', '0', '100'])

        self.light_conn_status = False

        self.com_str_search = re.compile("^(COM\\d+)")

        self.comport_info_list = []
        self.comport_tracer = self.comport_info_list.copy()

        self.light_sel_popout_mode = 'LC18' #'LC18' & 'LC20'
        self.light_info_widget()
        self.light_info_show()
        self.light_menu_btn_gen()
        self.LC18_menu_popout_gen()
        self.LC20_menu_popout_gen()
        self.conn_sett_popout_gen()

        self.light_interface_gui()


    def light_info_widget(self):
        self.light_info_tk_var = tk.StringVar()
        self.light_info_tk_lb = tk.Label(self.top_frame, font='Helvetica 12 bold', fg = 'white', bg = 'midnight blue', justify= tk.LEFT, anchor = 'w'
            , textvariable = self.light_info_tk_var)

        self.light_info_tk_var.set('')
        self.light_info_tk_lb.grid(row = 0, column = 1, rowspan = 1, ipady = 1, ipadx = 1, sticky = 'nwse')
        
        self.m_fw_version = tk.StringVar()
        self.fimware_tk_lb = tk.Label(self.top_frame, font='Helvetica 12 bold', fg = 'white', bg = 'midnight blue', justify= tk.LEFT, anchor = 'w'
            , textvariable = self.m_fw_version)

        self.m_fw_version.set('')
        self.fimware_tk_lb.grid(row = 1, column = 1, rowspan = 1, ipady = 1, ipadx = 1, sticky = 'nwse')

    def light_info_show(self):
        if self.fw_model_sel is not None and self.light_conn_status == True:
            # print(self.fw_model_sel)
            if self.fw_model_sel == 'LC20':
                model_info = 'Controller Type: ' + str(ctrl_model_type(self.fw_model_sel))
                self.light_info_tk_var.set(model_info)
                self.m_fw_version.set('')

            elif self.fw_model_sel != 'LC20':
                model_info = 'Controller Type: ' + str(ctrl_model_type(self.fw_model_sel))
                self.light_info_tk_var.set(model_info)
                firmware_info = 'Master FW Version: ' + str(self.m_fw_version_str)
                self.m_fw_version.set(firmware_info)

            self.light_info_tk_lb.lift()
            self.fimware_tk_lb.lift()
        else:
            self.light_info_hide()

    def light_info_hide(self):
        self.light_info_tk_var.set('')
        self.m_fw_version.set('')
        self.light_info_tk_lb.lower()
        self.fimware_tk_lb.lower()

    def light_menu_btn_gen(self):
        self.light_menu_btn = tk.Button(self.top_frame, relief = tk.GROOVE, font='Helvetica 16 bold', width = 10)
        self.light_menu_btn.grid(row = 0, column = 3, rowspan = 2,pady = 20, padx = 50, sticky = 'nse')
        self.light_menu_btn_state()

    def light_menu_btn_state(self):
        if self.light_conn_status == False:
            self.light_menu_btn['text'] = 'CONNECT'
            self.light_menu_btn['bg'] = 'green3'
            self.light_menu_btn['fg'] = 'white'
            self.light_menu_btn['activebackground'] = 'forest green'
            self.light_menu_btn['activeforeground'] = 'white'

            if self.light_sel_popout_mode == 'LC20':
                self.light_menu_btn['command'] = self.LC20_menu_popout_open

            else:
                self.light_menu_btn['command'] = self.LC18_menu_popout_open

        elif self.light_conn_status == True:
            self.light_menu_btn['text'] = 'DISCONNECT'
            self.light_menu_btn['bg'] = 'red'
            self.light_menu_btn['fg'] = 'white'
            self.light_menu_btn['activebackground'] = 'red3'
            self.light_menu_btn['activeforeground'] = 'white'
            self.light_menu_btn['command'] = self.light_disconnect


    def light_menu_btn_show(self):
        self.light_menu_btn.grid(row = 0, column = 3, rowspan = 2,pady = 20, padx = 50, sticky = 'nse')

    def light_menu_btn_hide(self):
        self.light_menu_btn.grid_forget()

    def LC20_menu_popout_gen(self):
        self.LC20_menu_toplvl = CustomToplvl(self.master, toplvl_title = 'LC20 Model(s)', icon_img = self.gui_graphic['window_icon'], topmost_bool = True)
        self.LC20_menu_toplvl['width']  = 500
        self.LC20_menu_toplvl['height'] = 360
        self.LC20_menu_toplvl['bg']     = 'white'
        self.LC20_menu_toplvl.resizable(False, False)
        self.LC20_menu_popout_gui()

    def LC20_menu_popout_open(self):
        if False == self.LC20_menu_toplvl.check_open():
            toplvl_W = self.LC20_menu_toplvl['width']
            toplvl_H = self.LC20_menu_toplvl['height']
            screen_width = self.LC20_menu_toplvl.winfo_screenwidth()
            screen_height = self.LC20_menu_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (toplvl_W/2))
            y_coordinate = int((screen_height/2) - (toplvl_H/2))
            self.LC20_menu_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
            self.LC20_menu_toplvl.open()
            self.light_sel_popout_mode = 'LC20'
            self.LC20_menu_toplvl.grab_set()

        else:
            self.LC20_menu_toplvl.show()

    def LC20_menu_popout_gui(self):
        menu_toplvl = self.LC20_menu_toplvl
        menu_toplvl.grid_columnconfigure(index = 0, weight = 1)
        logo_tk_lb = tk.Label(menu_toplvl, bg ='white')
        tk_img_insert(logo_tk_lb, self.gui_graphic['tms_logo'], img_height = 110)
        logo_tk_lb.grid(column = 0, row = 0, columnspan = 1, ipadx = 1, ipady = 1, sticky = 'nwse')


        menu_toplvl.grid_rowconfigure(index = 1, weight = 1)
        self.LC20_menu_fr = tk.Frame(menu_toplvl, bg = 'midnight blue', highlightbackground="midnight blue", highlightthickness=1)
        self.LC20_menu_fr.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, ipadx = 1, ipady = 1, sticky = 'nwse')

        self.LC20_menu_fr.grid_columnconfigure(index = 0, weight = 1)
        model_tk_lb = tk.Label(self.LC20_menu_fr, bg = 'midnight blue', fg = 'white', width = 12, justify = 'center'
            , text='LC-20-16CH-A1', font='Helvetica 13 bold')
        model_tk_lb.grid(column = 0, row = 0, columnspan = 1, ipadx = 1, ipady = 1, sticky = 'nwse')


        self.LC20_menu_fr.grid_rowconfigure(index = 1, weight = 1)
        tk_btn = tk.Button(self.LC20_menu_fr
            , bg = 'white', fg = 'white', activebackground ='white', activeforeground = 'white'
            , relief = tk.GROOVE)
        tk_img_insert(tk_btn, self.model_img['img_LC20'], img_width = 125, img_height = 125)
        tk_btn.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = 1, pady = 5, sticky = 'n')
        tk_btn['command'] = partial(self.select_light_model, model_str = 'LC20', lc_lib = self.LC20_lib)

        self.LC20_menu_fr.grid_rowconfigure(index = 2, weight = 1)
        other_model_btn = tk.Button(self.LC20_menu_fr, text = 'Other Models', bg = 'white', 
            fg = 'black', activeforeground = 'black', relief = tk.GROOVE, font = 'Helvetica 12')#, bd = 0)
        other_model_btn.grid(column = 0, row = 2, columnspan = 1, rowspan = 1, padx = 1, pady = 20, sticky = 's')
        other_model_btn['command'] = partial(self.popout_switch_menu, self.LC18_menu_popout_open, self.LC20_menu_toplvl.close)


    def LC18_menu_popout_gen(self):
        self.LC18_menu_toplvl = CustomToplvl(self.master, toplvl_title = 'LC18 Model(s)', icon_img = self.gui_graphic['window_icon'], topmost_bool = True)
        self.LC18_menu_toplvl['width']  = 700
        self.LC18_menu_toplvl['height'] = 550
        self.LC18_menu_toplvl['bg']     = 'white'
        self.LC18_menu_toplvl.resizable(False, False)
        self.LC18_menu_popout_gui()

    def LC18_menu_popout_open(self):
        if False == self.LC18_menu_toplvl.check_open():
            toplvl_W = self.LC18_menu_toplvl['width']
            toplvl_H = self.LC18_menu_toplvl['height']
            screen_width = self.LC18_menu_toplvl.winfo_screenwidth()
            screen_height = self.LC18_menu_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (toplvl_W/2))
            y_coordinate = int((screen_height/2) - (toplvl_H/2))
            self.LC18_menu_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
            self.LC18_menu_toplvl.open()
            self.light_sel_popout_mode = 'LC18'
            self.LC18_menu_toplvl.grab_set()
        else:
            self.LC18_menu_toplvl.show()

    def LC18_menu_popout_gui(self):
        menu_toplvl = self.LC18_menu_toplvl
        self.LC18_menu_toplvl.grid_columnconfigure(index = 0, weight = 1)
        logo_tk_lb = tk.Label(menu_toplvl, bg ='white')
        tk_img_insert(logo_tk_lb, self.gui_graphic['tms_logo'], img_height = 110)
        logo_tk_lb.grid(column = 0, row = 0, columnspan = 1, ipadx = 1, ipady = 1, sticky = 'nwse')


        menu_toplvl.grid_rowconfigure(index = 1, weight = 1)
        self.LC18_menu_fr = tk.Frame(menu_toplvl, bg = 'midnight blue', highlightbackground="midnight blue", highlightthickness=1)
        self.LC18_menu_fr.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, ipadx = 1, ipady = 1, sticky = 'nwse')


        model_data_dict = { 'LC-18-4CH-KP1': ['img_KP', 'KP', self.LC18KP_lib]
                        , 'LC-18-16CH': ['img_16CH', '16CH', self.LC18_lib] #### We will use re.compile with match to check
                        , 'LC-18-4CH-A1': ['img_4CH', '4CH', self.LC18_lib]
                        , 'LC-18-1CH' : ['img_X10', 'X10', self.LC18_lib]
                         }
        i = 0
        for model_name, model_info in model_data_dict.items():
            model_img = model_info[0]
            model_str = model_info[1]
            lc_lib = model_info[2]

            self.LC18_menu_fr.grid_columnconfigure(index = i, weight = 1)
            model_tk_lb = tk.Label(self.LC18_menu_fr, bg = 'midnight blue', fg = 'white', width = 12, justify = 'center' #'midnight blue'
            , text = model_name, font='Helvetica 13 bold')
            model_tk_lb.grid(column = i, row = 0, columnspan = 1, ipadx = 1, pady = (15,10), sticky = 'nwe')

            tk_btn = tk.Button(self.LC18_menu_fr
                , bg = 'white', fg = 'white', activebackground ='white', activeforeground = 'white'
                , relief = tk.GROOVE)
            tk_img_insert(tk_btn, self.model_img[str(model_img)], img_width = 125, img_height = 125)
            tk_btn.grid(column = i, row = 1, columnspan = 1, rowspan = 1, padx = 1, pady = 1, sticky = 'n')

            tk_btn['command'] = partial(self.select_light_model, model_str = model_str, lc_lib = lc_lib)


            i += 1
        del model_data_dict, i

        model_data_dict = { 'LC-18-2CH': ['img_X5', 'X5', self.LC18_lib]
                        , 'LC-18-OD': ['img_OD', 'OD', self.LC18_lib]
                        , 'LC-18-SQ': ['img_SQ', 'SQ', self.LC18SQ_lib]
                        , 'LC-18-4CH-A1-RGBW' : ['img_RGBW', 'RGBW', self.LC18_lib]
                         }
        i = 0
        for model_name, model_info in model_data_dict.items():
            model_img = model_info[0]
            model_str = model_info[1]
            lc_lib = model_info[2]

            self.LC18_menu_fr.grid_columnconfigure(index = i, weight = 1)
            model_tk_lb = tk.Label(self.LC18_menu_fr, bg = 'midnight blue', fg = 'white', width = 12, justify = 'center' #'midnight blue'
            , text = model_name, font='Helvetica 13 bold')
            model_tk_lb.grid(column = i, row = 2, columnspan = 1, ipadx = 1, pady = (25,10), sticky = 'nwe')

            tk_btn = tk.Button(self.LC18_menu_fr
                , bg = 'white', fg = 'white', activebackground ='white', activeforeground = 'white'
                , relief = tk.GROOVE)
            tk_img_insert(tk_btn, self.model_img[str(model_img)], img_width = 125, img_height = 125)
            tk_btn.grid(column = i, row = 3, columnspan = 1, rowspan = 1, padx = 1, pady = 1, sticky = 'n')
            
            tk_btn['command'] = partial(self.select_light_model, model_str = model_str, lc_lib = lc_lib)

            i += 1
        del model_data_dict, i

        self.LC18_menu_fr.grid_rowconfigure(index = 4, weight = 1)
        other_model_btn = tk.Button(self.LC18_menu_fr, text = 'Other Models', bg = 'white', 
            fg = 'black', activeforeground = 'black', relief = tk.GROOVE, font = 'Helvetica 12')
        other_model_btn.grid(column = 0, row = 4, columnspan = 4, rowspan = 1, padx = 1, pady = (15,10), sticky = 'n')
        other_model_btn['command'] = partial(self.popout_switch_menu, self.LC20_menu_popout_open, self.LC18_menu_toplvl.close)

    def popout_switch_menu(self, show, *hide_args, **hide_kwargs):
        if callable(show) == True:
            show()

        for hide in hide_args:
            if callable(hide) == True:
                hide()

        for hide in hide_kwargs.values():
            if callable(hide) == True:
                hide()

    def check_model_sel(self, fw_model, fw_model_sel):
        # print("fw_model, fw_model_sel: ", fw_model, fw_model_sel)
        s_find = "({})".format(fw_model_sel)
        # print("s_find: ", s_find)
        re_compile = re.compile(s_find)
        # print("Matching result: ", re_compile.search(fw_model))
        if re_compile.search(fw_model):
            return True

        else:
            return False

    def select_light_model(self, model_str, lc_lib):
        self.fw_model_sel = model_str
        self.main_lib = lc_lib
        self.conn_sett_popout_open()
        self.LC18_menu_toplvl.close()
        self.LC20_menu_toplvl.close()

    def conn_sett_popout_gen(self):
        self.conn_sett_toplvl = CustomToplvl(self.master, toplvl_title = 'Connect Settings', icon_img = self.gui_graphic['window_icon'], topmost_bool = True)
        self.conn_sett_toplvl['width']  = 700
        self.conn_sett_toplvl['height'] = 500
        self.conn_sett_toplvl['bg']     = 'white'
        self.conn_sett_toplvl.resizable(False, False)
        self.conn_sett_toplvl.protocol("WM_DELETE_WINDOW", self.conn_sett_popout_close)
        self.conn_sett_popout_gui()

    def conn_sett_popout_open(self):
        if False == self.conn_sett_toplvl.check_open():
            toplvl_W = self.conn_sett_toplvl['width']
            toplvl_H = self.conn_sett_toplvl['height']
            screen_width = self.conn_sett_toplvl.winfo_screenwidth()
            screen_height = self.conn_sett_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (toplvl_W/2))
            y_coordinate = int((screen_height/2) - (toplvl_H/2))
            self.conn_sett_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
            self.conn_sett_toplvl.open()
            self.conn_sett_toplvl.grab_set()
            self.comport_tk_radio.invoke()

            if self.fw_model_sel == 'KP':
                self.USB_tk_radio.place(x = -80, y = 50, relx = 0.5, anchor = 'se')
                self.comport_tk_radio.place(x = -80, y = 100, relx = 0.5, anchor = 'se')
                self.TCPIP_tk_radio.place(x = -80, y = 150, relx = 0.5, anchor = 'se')

            elif self.fw_model_sel == 'LC20':
                self.USB_tk_radio.place_forget()
                self.comport_tk_radio.place(x = -80, y = 100, relx = 0.5, anchor = 'se')
                self.TCPIP_tk_radio.place_forget()

            else:
                self.USB_tk_radio.place_forget()
                self.comport_tk_radio.place(x = -80, y = 100, relx = 0.5, anchor = 'se')
                self.TCPIP_tk_radio.place(x = -80, y = 150, relx = 0.5, anchor = 'se')

            self.comport_check_update()
            
        else:
            self.conn_sett_toplvl.show()

    def conn_sett_popout_close(self):
        if self.light_sel_popout_mode == 'LC18':
            self.LC18_menu_popout_open()
        elif self.light_sel_popout_mode == 'LC20':
            self.LC20_menu_popout_open()

        self.conn_sett_toplvl.close()
    
    def comport_enum(self):
        self.comport_info_list *= 0
        for comport_index, p in enumerate (serial.tools.list_ports.comports()):
            if 'USB' and 'Serial' in p.description:
                self.comport_info_list.append(p)

    def comport_check_update(self):
        self.comport_enum()
        if self.comport_tracer == self.comport_info_list:
            pass
        else:
            self.comport_tk_cbox["value"] = self.comport_info_list
            self.comport_tk_cbox.set('')
            self.comport_tk_cbox.event_generate('<Escape>')
            if len(self.comport_info_list) > 0:
                self.comport_tk_cbox.current(0)
            self.comport_tracer = self.comport_info_list.copy()

        self.conn_sett_toplvl.custom_after(200, self.comport_check_update)

    def conn_sett_popout_gui(self):
        tk_toplvl = self.conn_sett_toplvl
        
        tk_toplvl.grid_columnconfigure(index = 0, weight = 1)

        logo_tk_lb = tk.Label(tk_toplvl, bg = 'white')
        tk_img_insert(logo_tk_lb, self.gui_graphic['tms_logo'], img_height = 110)
        logo_tk_lb.grid(column = 0, row = 0, rowspan = 1, columnspan = 1, padx = 1, pady = (1,1), sticky = 'n')

        conn_tk_lb = tk.Label(tk_toplvl, text= 'Connect Settings', font= 'Helvetica 14 bold', bg = 'white')
        conn_tk_lb.grid(column = 0, row = 1, rowspan = 1, columnspan = 1, padx = 1, pady = (5,1), sticky = 'nswe')

        self.connect_type = tk.StringVar(value = 'comport')
        tk_toplvl.grid_rowconfigure(index = 2, weight = 1)
        self.conn_sett_menu = tk.Frame(tk_toplvl)
        self.conn_sett_menu['bg'] = 'white'
        self.conn_sett_menu.grid(column = 0, row = 2, rowspan = 1, columnspan = 1, padx = 1, pady = (5,5), sticky = 'nswe')

        """----------------------------------------------------------------------------------------------------------------"""
        ### USB Init
        self.USB_tk_radio = tk.Radiobutton(self.conn_sett_menu, text = 'USB', variable = self.connect_type, value = 'USB', font='Helvetica 13')
        self.USB_tk_radio['bg'] = 'white'
        self.USB_tk_radio['command'] = self.light_conn_type
        self.USB_tk_radio.place(x = -80, y = 50, relx = 0.5, anchor = 'se')

        """----------------------------------------------------------------------------------------------------------------"""
        ### Comport Init
        self.comport_tk_radio = tk.Radiobutton(self.conn_sett_menu, text = 'Comport', variable = self.connect_type, value = 'comport', font='Helvetica 13'
            , anchor = 'se')
        self.comport_tk_radio['bg'] = 'white'
        self.comport_tk_radio['command'] = self.light_conn_type

        self.comport_sett_prnt = tk.Frame(self.conn_sett_menu)
        self.comport_sett_prnt['bg'] = 'white'

        self.comport_tk_lb = tk.Label(self.comport_sett_prnt, text = 'Choose & Select COM Ports:' , font = 'Helvetica 11'
            , anchor = 'sw')
        self.comport_tk_lb['bg'] = 'white'
        self.comport_tk_lb.grid(column = 0, row = 0, rowspan = 1, columnspan = 1, padx = (1, 1), pady = (1,1), sticky = 'nw')

        self.comport_tk_cbox = CustomBox(self.comport_sett_prnt, width = 38, state='readonly', font = 'Helvetica 11')
        # self.comport_tk_cbox['values'] = self.comport_info_list
        # self.comport_tk_cbox['values'] = ['Hello World']
        self.comport_tk_cbox.grid(column = 0, row = 1, rowspan = 1, columnspan = 1, padx = (1, 1), pady = (1,1), sticky = 'nw')

        self.comport_tk_radio.place(x = -80, y = 100, relx = 0.5, anchor = 'se')
        self.comport_sett_prnt.place(x = -50, y = 100, relx = 0.5, anchor = 'sw')

        """----------------------------------------------------------------------------------------------------------------"""
        ### TCPIP Init
        self.TCPIP_tk_radio = tk.Radiobutton(self.conn_sett_menu, text = 'TCPIP', variable = self.connect_type, value = 'TCPIP', font='Helvetica 13'
            , anchor = 'se')
        self.TCPIP_tk_radio['bg'] = 'white'
        self.TCPIP_tk_radio['command'] = self.light_conn_type

        self.TCPIP_sett_prnt = tk.Frame(self.conn_sett_menu)
        self.TCPIP_sett_prnt['bg'] = 'white'

        tk_dot = tk.Label(self.TCPIP_sett_prnt, text= '.', font = 'Helvetica 12 bold', justify = 'center', anchor = 's')
        tk_dot['bg'] = 'white'
        tk_dot.grid(column = 1, row = 0, rowspan = 1, columnspan = 1, padx = (5, 5), pady = (1,1), sticky = 'ns')
        
        tk_dot = tk.Label(self.TCPIP_sett_prnt, text= '.', font = 'Helvetica 12 bold', justify = 'center', anchor = 's')
        tk_dot['bg'] = 'white'
        tk_dot.grid(column = 3, row = 0, rowspan = 1, columnspan = 1, padx = (5, 5), pady = (1,1), sticky = 'ns')

        tk_dot = tk.Label(self.TCPIP_sett_prnt, text= '.', font = 'Helvetica 12 bold', justify = 'center', anchor = 's')
        tk_dot['bg'] = 'white'
        tk_dot.grid(column = 5, row = 0, rowspan = 1, columnspan = 1, padx = (5, 5), pady = (1,1), sticky = 'ns')

        self.TCPIP_var_1 = tk.StringVar()
        self.TCPIP_var_2 = tk.StringVar()
        self.TCPIP_var_3 = tk.StringVar()
        self.TCPIP_var_4 = tk.StringVar()

        TCPIP_entry_1 = tk.Entry(self.TCPIP_sett_prnt, textvariable = self.TCPIP_var_1, highlightbackground="black", highlightthickness=1, width = 3, font = 'Helvetica 11', justify = 'center')
        TCPIP_entry_1.bind('<FocusIn>', lambda event: self.entry_highlight_focus(widget=TCPIP_entry_1))
        TCPIP_entry_1.bind('<FocusOut>', partial(self.tcpip_entry_focus_out, tk_var = self.TCPIP_var_1, str_arr_i = 0))
        Validate_Int(TCPIP_entry_1, self.TCPIP_var_1, only_positive = True, lo_limit = 0, hi_limit = 999)
        self.TCPIP_var_1.trace('w', lambda var_name, var_index, operation: self.tcpip_entry_trace(tk_var = self.TCPIP_var_1, tk_entry = TCPIP_entry_1))
        self.TCPIP_var_1.set(self.TCPIP_str_arr[0])
        TCPIP_entry_1.grid(column = 0, row = 0, rowspan = 1, columnspan = 1, padx = (1, 1), pady = (1,1), sticky = 'ns')

        TCPIP_entry_2 = tk.Entry(self.TCPIP_sett_prnt, textvariable = self.TCPIP_var_2, highlightbackground="black", highlightthickness=1, width = 3, font = 'Helvetica 11', justify = 'center')
        TCPIP_entry_2.bind('<FocusIn>', lambda event: self.entry_highlight_focus(widget=TCPIP_entry_2))
        TCPIP_entry_2.bind('<FocusOut>', partial(self.tcpip_entry_focus_out, tk_var = self.TCPIP_var_2, str_arr_i = 1))
        Validate_Int(TCPIP_entry_2, self.TCPIP_var_2, only_positive = True, lo_limit = 0, hi_limit = 999)
        self.TCPIP_var_2.trace('w', lambda var_name, var_index, operation: self.tcpip_entry_trace(tk_var = self.TCPIP_var_2, tk_entry = TCPIP_entry_2))
        self.TCPIP_var_2.set(self.TCPIP_str_arr[1])
        TCPIP_entry_2.grid(column = 2, row = 0, rowspan = 1, columnspan = 1, padx = (1, 1), pady = (1,1), sticky = 'ns')


        TCPIP_entry_3 = tk.Entry(self.TCPIP_sett_prnt, textvariable = self.TCPIP_var_3, highlightbackground="black", highlightthickness=1, width = 3, font = 'Helvetica 11', justify = 'center')
        TCPIP_entry_3.bind('<FocusIn>', lambda event: self.entry_highlight_focus(widget=TCPIP_entry_3))
        TCPIP_entry_3.bind('<FocusOut>', partial(self.tcpip_entry_focus_out, tk_var = self.TCPIP_var_3, str_arr_i = 2))
        Validate_Int(TCPIP_entry_3, self.TCPIP_var_3, only_positive = True, lo_limit = 0, hi_limit = 999)
        self.TCPIP_var_3.trace('w', lambda var_name, var_index, operation: self.tcpip_entry_trace(tk_var = self.TCPIP_var_3, tk_entry = TCPIP_entry_3))
        self.TCPIP_var_3.set(self.TCPIP_str_arr[2])
        TCPIP_entry_3.grid(column = 4, row = 0, rowspan = 1, columnspan = 1, padx = (1, 1), pady = (1,1), sticky = 'ns')

        TCPIP_entry_4 = tk.Entry(self.TCPIP_sett_prnt, textvariable = self.TCPIP_var_4, highlightbackground="black", highlightthickness=1, width = 3, font = 'Helvetica 11', justify = 'center')
        TCPIP_entry_4.bind('<FocusIn>', lambda event: self.entry_highlight_focus(widget=TCPIP_entry_4))
        TCPIP_entry_4.bind('<FocusOut>', partial(self.tcpip_entry_focus_out, tk_var = self.TCPIP_var_4, str_arr_i = 3))
        Validate_Int(TCPIP_entry_4, self.TCPIP_var_4, only_positive = True, lo_limit = 0, hi_limit = 999)
        self.TCPIP_var_4.trace('w', lambda var_name, var_index, operation: self.tcpip_entry_trace(tk_var = self.TCPIP_var_4, tk_entry = TCPIP_entry_4))
        self.TCPIP_var_4.set(self.TCPIP_str_arr[3])
        TCPIP_entry_4.grid(column = 6, row = 0, rowspan = 1, columnspan = 1, padx = (1, 1), pady = (1,1), sticky = 'ns')

        TCPIP_entry_1.focus_set()

        self.TCPIP_reset_button = tk.Button(self.TCPIP_sett_prnt, relief = tk.GROOVE, text = 'TCPIP Reset', font = 'Helvetica 11')
        self.TCPIP_reset_button['command'] = self.TCPIP_reset
        self.TCPIP_reset_button.grid(column = 7, row = 0, rowspan = 1, columnspan = 1, padx = (40, 1), pady = (1,1), sticky = 'ns')


        self.TCPIP_tk_radio.place(x = -80, y = 150, relx = 0.5, anchor = 'se')
        self.TCPIP_sett_prnt.place(x = -50, y = 150, relx = 0.5, anchor = 'sw')
        """----------------------------------------------------------------------------------------------------------------"""

        self.light_conn_btn = tk.Button(tk_toplvl, relief = tk.GROOVE, activebackground = 'forest green', bg = 'green3', activeforeground = 'white', fg = 'white'
        , text='CONNECT', width = 10, height = 1, font='Helvetica 14 bold')
        self.light_conn_btn.grid(column = 0, row = 3, rowspan = 1, columnspan = 1, padx = 1, pady = (1,5), sticky = 'n')

        back_btn = tk.Button(tk_toplvl, relief = tk.GROOVE, text='Back to Model', height = 1, font='Helvetica 12')
        back_btn['command'] = self.conn_sett_popout_close

        back_btn.grid(column = 0, row = 4, rowspan = 1, columnspan = 1, padx = 1, pady = (1,10), sticky = 'n')

        copyright_symbol = chr(169)
        copyright_text = ('Copyright ' + copyright_symbol + ' 2004 - 2020 TMS Lite Sdn Bhd.') + '\n All Right Reserved.'
        copyright_tk_lb = tk.Label(tk_toplvl, text= copyright_text, font= 'Helvetica 12')
        copyright_tk_lb['bg'] = 'white'
        copyright_tk_lb.grid(column = 0, row = 5, rowspan = 1, columnspan = 1, padx = 1, pady = (1,15), sticky = 'nswe')

    def entry_highlight_focus(self, widget):
        if isinstance(widget, tk.Entry):
            widget.selection_range(0, tk.END)

    def tcpip_entry_trace(self, tk_var, tk_entry):
        if len(tk_var.get()) == 3:
            tk_entry.tk_focusNext().focus()

    def tcpip_entry_focus_out(self, event, tk_var, str_arr_i):
        if is_int(tk_var.get()) == False:
            tk_var.set(self.TCPIP_str_arr[str_arr_i])

        elif is_int(tk_var.get()) == True:
            self.TCPIP_str_arr[str_arr_i] = tk_var.get()

    def TCPIP_reset(self, event = None):
        ask_msgbox = Ask_Msgbox('Do you want to RESET TCPIP?', title = 'RESET TCPIP', parent = self.conn_sett_toplvl, message_anchor = 'w'
            , parent_grab_set = True, ask_OK = False)
        if ask_msgbox.ask_result() == True:
            self.TCPIP_str_arr[0] = '192'
            self.TCPIP_str_arr[1] = '168'
            self.TCPIP_str_arr[2] = '0'
            self.TCPIP_str_arr[3] = '100'

            self.TCPIP_var_1.set(self.TCPIP_str_arr[0])
            self.TCPIP_var_2.set(self.TCPIP_str_arr[1])
            self.TCPIP_var_3.set(self.TCPIP_str_arr[2])
            self.TCPIP_var_4.set(self.TCPIP_str_arr[3])

    def light_conn_type(self):
        if self.connect_type.get() == 'comport':
            self.comport_sett_prnt.place(x = -50, y = 100, relx = 0.5, anchor = 'sw')
            self.TCPIP_sett_prnt.place_forget()
            if self.fw_model_sel == 'LC20':
                self.light_conn_btn['command'] = partial(self.LC20_comport_connect)
            else:
                self.light_conn_btn['command'] = partial(self.comport_connect)

        elif self.connect_type.get() == 'TCPIP':
            self.comport_sett_prnt.place_forget()
            self.TCPIP_sett_prnt.place(x = -50, y = 150, relx = 0.5, anchor = 'sw')
            self.light_conn_btn['command'] = partial(self.TCPIP_connect)

        elif self.connect_type.get() == 'USB':
            self.comport_sett_prnt.place_forget()
            self.TCPIP_sett_prnt.place_forget()
            self.light_conn_btn['command'] = partial(self.USB_connect)


    def comport_connect(self):
        if len(self.comport_info_list) > 0:
            comport_info = self.comport_tk_cbox.get()
            com_name = self.com_str_search.search(comport_info)
            if com_name is not None:
                com_port_num = re.sub('\\D', "", com_name.groups()[0])
                status = self.main_lib.ComportConnect(int(com_port_num))
                print('ComportConnect Status: ', status, com_port_num)

                if status == 0:
                    self.fw_version_str = self.main_lib.ReadFWVersion()
                    try:
                        self.m_fw_version_str = self.main_lib.ReadMasterFWVersion()
                        if self.m_fw_version_str == 'ERR':
                            self.m_fw_version_str = self.main_lib.ReadFWVersion()
                    except:
                        self.m_fw_version_str = self.main_lib.ReadFWVersion()

                    # print(self.fw_version_str)
                    fw_model = firmware_check(self.fw_version_str)
                    # print('fw_model: ', fw_model)

                    m_fw_model = firmware_check(self.m_fw_version_str)
                    # print(self.m_fw_version_str)
                    # print('m_fw_model: ', m_fw_model)

                    if fw_model is None and m_fw_model is None:
                        self.fw_model = None

                    elif fw_model is None and type(m_fw_model) == str:
                        self.fw_model = m_fw_model

                    elif type(fw_model) == str and m_fw_model is None:
                        self.fw_model = fw_model

                    elif type(fw_model) == str and type(m_fw_model) == str:
                        self.fw_model = fw_model

                    # self.fw_model = "X5"
                    if self.check_model_sel(self.fw_model, self.fw_model_sel) == True:
                        print('Connection Success')

                        self.COM = True
                        self.light_conn_status = True
                        self.light_menu_btn_state()
                        self.conn_sett_toplvl.close()
                        self.scrolled_canvas.show()
                        self.light_info_show()
                        self.light_interface_show(self.fw_model_sel)

                    else:
                        self.COM = False
                        self.light_conn_status = False
                        print('ERROR! FIRMWARE ERROR')

                        Warning_Msgbox(message = 'DETECTED FIRMWARE VERSION: '+ str(self.fw_version_str) + '\n\n' + 'EXPECTED LC18 MODEL: LC18-' + str(self.fw_model) + 
                            '\n\nFIRMWARE IS NOT COMPATIBLE.\nPLEASE SELECT THE CORRECT MODEL.', title = 'FIRMWARE ERROR', font = 'Helvetica 10', height = 225
                            , parent = self.conn_sett_toplvl, parent_grab_set = True)
                        self.main_lib.ComportDisconnect()

                else: #if status == 1 (ERROR CONNECTION)
                    self.COM = False
                    self.light_conn_status = False
                    print('ERROR! COMPORT CONNECTION FAILED')

                    Warning_Msgbox(message = 'POSSIBLE PROBLEMS:\n\n1. LOOSE CONNECTION\n2. INCORRECT COMPORT\n3. CONTROLLER IS SWITCHED OFF'
                        , title = 'CONNECTION ERROR', font = 'Helvetica 10', height = 160
                        , parent = self.conn_sett_toplvl, parent_grab_set = True)


    def LC20_comport_connect(self):
        if len(self.comport_info_list) > 0:
            comport_info = self.comport_tk_cbox.get()
            com_name = self.com_str_search.search(comport_info)
            if com_name is not None:
                com_port_num = re.sub('\\D', "", com_name.groups()[0])

                status = self.main_lib.ComportConnect(int(com_port_num))
                print('LC20 Comport Connect Status: ', status)
                if status == 0:
                    self.fw_model = 'LC20'
                    
                    if self.check_model_sel(self.fw_model, self.fw_model_sel) == True:
                        print('Connection Success')

                        self.COM = True
                        self.light_conn_status = True
                        self.light_menu_btn_state()
                        self.conn_sett_toplvl.close()
                        self.scrolled_canvas.show()
                        self.light_info_show()
                        self.light_interface_show(self.fw_model_sel)

                else: #if status == 1 (ERROR CONNECTION)
                    self.COM = False
                    self.light_conn_status = False
                    print('ERROR! COMPORT CONNECTION FAILED')

                    Warning_Msgbox(message = 'POSSIBLE PROBLEMS:\n\n1. LOOSE CONNECTION\n2. INCORRECT COMPORT\n3. CONTROLLER IS SWITCHED OFF'
                        , title = 'LC20 CONNECTION ERROR', font = 'Helvetica 10', height = 160
                        , parent = self.conn_sett_toplvl, parent_grab_set = True)
                    #self.main_lib.ComportDisconnect()

    def TCPIP_connect(self):
        TCPIP_id_number = self.TCPIP_str_arr[0] + '.' + self.TCPIP_str_arr[1] + '.' + self.TCPIP_str_arr[2] + '.' + self.TCPIP_str_arr[3]
        #print(TCPIP_id_number)
        status = self.main_lib.TCPIPConnect(TCPIP_id_number)

        if status == 0:
            self.fw_version_str = self.main_lib.ReadFWVersion()
            try:
                self.m_fw_version_str = self.main_lib.ReadMasterFWVersion()
                if self.m_fw_version_str == 'ERR':
                    self.m_fw_version_str = self.main_lib.ReadFWVersion()
            except:
                self.m_fw_version_str = self.main_lib.ReadFWVersion()

            fw_model = firmware_check(self.fw_version_str)
            m_fw_model = firmware_check(self.m_fw_version_str)

            if fw_model is None and m_fw_model is None:
                self.fw_model = None

            elif fw_model is None and type(m_fw_model) == str:
                self.fw_model = m_fw_model

            elif type(fw_model) == str and m_fw_model is None:
                self.fw_model = fw_model

            elif type(fw_model) == str and type(m_fw_model) == str:
                self.fw_model = fw_model

            if self.check_model_sel(self.fw_model, self.fw_model_sel) == True:
                print('Connection Success')
                self.TCPIP = True
                self.light_conn_status = True
                self.light_menu_btn_state()
                self.conn_sett_toplvl.close()
                self.scrolled_canvas.show()
                self.light_info_show()
                self.light_interface_show(self.fw_model_sel)

            else:
                self.TCPIP = False
                self.light_conn_status = False
                print('ERROR! FIRMWARE ERROR')

                Warning_Msgbox(message = 'DETECTED FIRMWARE VERSION: '+ str(self.fw_version_str) + '\n\n' + 'EXPECTED LC18 MODEL: LC18-' + str(self.fw_model) + 
                        '\n\nFIRMWARE IS NOT COMPATIBLE.\nPLEASE SELECT THE CORRECT MODEL.', title = 'FIRMWARE ERROR', font = 'Helvetica 10', height = 225
                        , parent = self.conn_sett_toplvl, parent_grab_set = True)
                self.main_lib.TCPIPDisconnect()#Since status is return as 0 in this 'If' statement when we are technically 'connected', We have to disconnect to clear the TCPIP bus.

        else: #if status == 1 (ERROR CONNECTION)
            self.TCPIP = False
            self.light_conn_status = False
            print('ERROR! TCPIP CONNECTION FAILED')

            Warning_Msgbox(message = 'POSSIBLE PROBLEMS:\n\n1. LOOSE CONNECTION\n2. INCORRECT COMPORT\n3. CONTROLLER IS SWITCHED OFF'
                    , title = 'CONNECTION ERROR', font = 'Helvetica 10', height = 160
                    , parent = self.conn_sett_toplvl, parent_grab_set = True)
            #self.main_lib.TCPIPDisconnect()


    def USB_connect(self):
        status = self.main_lib.USBConnect()
        #print(status)
        #print(ctrl)
        if status == 0:
            self.fw_version_str = self.main_lib.ReadFWVersion()
            try:
                self.m_fw_version_str = self.main_lib.ReadMasterFWVersion()
                if self.m_fw_version_str == 'ERR':
                    self.m_fw_version_str = self.main_lib.ReadFWVersion()
            except:
                self.m_fw_version_str = self.main_lib.ReadFWVersion()

            fw_model = firmware_check(self.fw_version_str)
            m_fw_model = firmware_check(self.m_fw_version_str)

            if fw_model is None and m_fw_model is None:
                self.fw_model = None

            elif fw_model is None and type(m_fw_model) == str:
                self.fw_model = m_fw_model

            elif type(fw_model) == str and m_fw_model is None:
                self.fw_model = fw_model

            elif type(fw_model) == str and type(m_fw_model) == str:
                self.fw_model = fw_model
                
            if self.check_model_sel(self.fw_model, self.fw_model_sel) == True:
                print('Connection Success')
                self.USB = True
                self.light_conn_status = True
                self.light_menu_btn_state()
                self.conn_sett_toplvl.close()
                self.scrolled_canvas.show()
                self.light_info_show()
                self.light_interface_show(self.fw_model_sel)

            else:
                self.USB = False
                self.light_conn_status = False
                print('ERROR! FIRMWARE ERROR')

                Warning_Msgbox(message = 'DETECTED FIRMWARE VERSION: '+ str(self.fw_version_str) + '\n\n' + 'EXPECTED LC18 MODEL: LC18-' + str(self.fw_model) + 
                        '\n\nFIRMWARE IS NOT COMPATIBLE.\nPLEASE SELECT THE CORRECT MODEL.', title = 'FIRMWARE ERROR', font = 'Helvetica 10', height = 225
                        , parent = self.conn_sett_toplvl, parent_grab_set = True)
                self.main_lib.USBDisconnect()#Since status is return as 0 in this 'If' statement when we are technically 'connected', We have to disconnect to clear the USB bus.

        else: #if status == 1 (ERROR CONNECTION)
            self.USB = False
            self.light_conn_status = False
            print('ERROR! USB CONNECTION FAILED')

            Warning_Msgbox(message = 'POSSIBLE PROBLEMS:\n\n1. LOOSE CONNECTION\n2. INCORRECT COMPORT\n3. CONTROLLER IS SWITCHED OFF'
                    , title = 'CONNECTION ERROR', font = 'Helvetica 10', height = 160
                    , parent = self.conn_sett_toplvl, parent_grab_set = True)
            #self.main_lib.USBDisconnect()


    def light_disconnect(self):
        self.scrolled_canvas.hide() #ScrolledCanvas Library
        self.scrolled_canvas.resize_frame(width = 1150, height = 980)
        self.light_disconnect_dll()
        self.light_conn_status = False
        self.light_menu_btn_state()
        self.light_info_hide()
        self.light_interface_hide(self.fw_model_sel)

        self.fw_version_str = None
        self.fw_model = None
        self.fw_model_sel = None
        self.m_fw_version_str = None

        print("Light GUI Disconnected...")

    def light_disconnect_dll(self):
        # print('Light Disconnect (LC Library): ', self.main_lib)

        if isinstance(self.main_lib, LC18Library.LC18SQ) == True:
            self.main_lib.Trigger(0)

        if self.COM == True:
            print('Disconnect Comport')
            self.main_lib.ComportDisconnect()
            self.COM = False

        if self.TCPIP == True:
            print('Disconnect TCPIP')
            self.main_lib.TCPIPDisconnect()
            self.TCPIP = False

        if self.USB == True:
            print('Disconnect USB')
            #print(self.main_lib)
            self.main_lib.USBDisconnect()
            self.USB = False

    def light_interface_gui(self):
        self.hmap_light_gui = {}
        self.hmap_light_gui['16CH'] = LC18_16CH_GUI(self.scrolled_canvas.window_fr, self.scrolled_canvas
            , self.LC18_lib, self.thread_event_repeat, self.thread_event_repeat_ALL
            , self.gui_graphic)
        self.hmap_light_gui['16CH']['bg'] = 'white'

        self.hmap_light_gui['4CH'] = LC18_4CH_GUI(self.scrolled_canvas.window_fr, self.scrolled_canvas
            , self.LC18_lib, self.thread_event_repeat, self.thread_event_repeat_ALL
            , self.gui_graphic)
        self.hmap_light_gui['4CH']['bg'] = 'white'

        self.hmap_light_gui['RGBW'] = LC18_RGBW_GUI(self.scrolled_canvas.window_fr, self.scrolled_canvas
            , self.LC18_lib, self.thread_event_repeat, self.thread_event_repeat_ALL
            , self.gui_graphic)
        self.hmap_light_gui['RGBW']['bg'] = 'white'

        self.hmap_light_gui['OD'] = LC18_OD_GUI(self.scrolled_canvas.window_fr, self.scrolled_canvas
            , self.LC18_lib, self.thread_event_repeat, self.thread_event_repeat_ALL
            , self.gui_graphic)
        self.hmap_light_gui['OD']['bg'] = 'white'

        self.hmap_light_gui['KP'] = LC18_KP_GUI(self.scrolled_canvas.window_fr, self.scrolled_canvas
            , self.LC18KP_lib, self.thread_event_repeat, self.thread_event_repeat_ALL
            , self.gui_graphic)
        self.hmap_light_gui['KP']['bg'] = 'white'

        self.hmap_light_gui['X10'] = LC18_1CH_GUI(self.scrolled_canvas.window_fr, self.scrolled_canvas
            , self.LC18_lib, self.thread_event_repeat, self.thread_event_repeat_ALL
            , self.gui_graphic)
        self.hmap_light_gui['X10']['bg'] = 'white'

        self.hmap_light_gui['X5'] = LC18_2CH_GUI(self.scrolled_canvas.window_fr, self.scrolled_canvas
            , self.LC18_lib, self.thread_event_repeat, self.thread_event_repeat_ALL
            , self.gui_graphic)
        self.hmap_light_gui['X5']['bg'] = 'white'

        self.hmap_light_gui['SQ'] = LC18_SQ_GUI(self.scrolled_canvas.window_fr, self.scrolled_canvas
            , self.LC18SQ_lib, self.thread_event_repeat_ALL
            , self.gui_graphic)
        self.hmap_light_gui['SQ']['bg'] = 'white'

        self.hmap_light_gui['LC20'] = LC20_SQ_GUI(self.scrolled_canvas.window_fr, self.scrolled_canvas
            , self.LC20_lib, self.thread_event_repeat_ALL
            , self.gui_graphic)
        self.hmap_light_gui['LC20']['bg'] = 'white'


    def light_interface_show(self, model_sel):
        # print(model_sel)
        if model_sel in self.hmap_light_gui:
            if model_sel == "X5" or model_sel == "X10":
                self.scrolled_canvas.resize_frame(width = 1150, height = 580)
                
            else:
                self.scrolled_canvas.resize_frame(width = 1150, height = 980)

            if model_sel == 'LC20':
                self.hmap_light_gui[model_sel].place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 1, relheight = 1, anchor = 'nw')
                self.hmap_light_gui[model_sel].show()
            else:
                self.hmap_light_gui[model_sel].place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 1, relheight = 1, anchor = 'nw')
                self.hmap_light_gui[model_sel].show(self.fw_version_str)

    def light_interface_hide(self, model_sel):
        # print(model_sel)
        if model_sel in self.hmap_light_gui:
            self.hmap_light_gui[model_sel].place_forget()
            self.hmap_light_gui[model_sel].hide()
                