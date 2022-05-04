"""
CODE SECTIONS:
### MAIN INTERFACE INIT
### REPEAT STROBE FEATURES
### GENERATE CONTROL PANEL
### LIGHT CONTROL FUNCTIONS
### RGBW SPECIAL FEATURES
### RESET LIGHT PARAMETERS
### LOAD LIGHT PARAMETERS
### STOP ALL THREADS
"""

import os
from os import path
import sys
import re

import tkinter as tk
from tkinter import ttk

import numpy as np
import threading
from functools import partial

import inspect
import ctypes
from ctypes import *

from LC18_pylib import LC18_Control
from Tk_Validate.tk_validate import *
from misc_module.tk_img_module import *
from Tk_Custom_Widget.tk_custom_label import *
from Tk_Custom_Widget.tk_custom_btn import *
from Tk_Custom_Widget.tk_custom_combobox import *
from Tk_Custom_Widget.tk_custom_spinbox import *
from Tk_Custom_Widget.ScrolledCanvas import ScrolledCanvas

from Tk_MsgBox.custom_msgbox import *

def widget_take_focus(*widget_args):#On Left Mouse Click the Widget is Focused
    def widget_focus(event, widget):
        if widget.focus_get() != widget:
            widget.focus_set()
            parent = widget.master
            parent.focus_set()
            # print(widget.focus_get())
    for widget in widget_args:
        widget.bind("<1>", partial(widget_focus, widget = widget), add = "+")


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

def binary_to_dec(*bins, reverse_str = False): #convert bin to unsigned number
    bin_str = None
    for bin_ in bins:
        if bin_str is None:
            bin_str = str(bin_)
        else:
            bin_str = bin_str + str(bin_)

    if reverse_str == True:
        bin_str = bin_str[::-1]
    else:
        pass
    #print(bin_str)
    dec_index = int(bin_str, 2) #binary is in base 2
    #print(dec_index)
    return dec_index #index number in decimal base

def dec_to_binary_arr(dec_num, bin_arr = None, reverse_arr = False): #convert unsigned number to bin
    #print("{:04b}".format(65535 & 0xFFFF))
    #bin_format = "{:0"+str(bin_arr.shape[0])+"b}"
    #bin_num = bin_format.format(dec_num)
    if bin_arr is not None and (isinstance(bin_arr, np.ndarray)) == True:
        bin_format = "{:0"+str(bin_arr.shape[0])+"b}"
        bin_num = bin_format.format(dec_num)
    else:
        bin_num = "{:04b}".format(dec_num & 0xF)

    bin_str = str(bin_num)
    #print(bin_str)
    #print(bin_arr.shape[0])
    bin_out = np.zeros(len(bin_str), dtype = np.uint8)
    for i, digit in enumerate (bin_str):
        bin_out[i] = digit

    if bin_arr is not None and (isinstance(bin_arr, np.ndarray)) == True:
        for i in range(bin_arr.shape[0]):
            bin_arr[i] = bin_out[i]

    if reverse_arr == True:
        if bin_arr is not None and (isinstance(bin_arr, np.ndarray)) == True:
            bin_arr = bin_arr[::-1]
            return bin_arr
        else:
            bin_out = bin_out[::-1]
            return bin_out

    elif reverse_arr == False:
        if bin_arr is not None and (isinstance(bin_arr, np.ndarray)) == True:
            return bin_arr
        else:
            return bin_out

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

class LC18_16CH_GUI(tk.Frame):
    def __init__(self, master, scroll_class, dll_LC18
        , thread_event_repeat = None, thread_event_repeat_ALL = None
        , gui_graphic = {}
        , **kwargs):

        if isinstance(scroll_class, ScrolledCanvas) == False:
            raise AttributeError("scroll_class must be a ScrolledCanvas class-object")

        tk.Frame.__init__(self, master, **kwargs)

        #INITIALIZE GUI INTERFACE MAIN PANEL(S) to hold the widgets
        self.master = master
        self.scroll_class = scroll_class
        self.dll_LC18 = dll_LC18

        self.firmware_version_str = None

        self.gui_graphic = dict(infinity_icon = None)
        for key, item in gui_graphic.items():
            if key in self.gui_graphic:
                self.gui_graphic[key] = item

        self.thread_event_repeat = thread_event_repeat #Thread event used in Threading
        self.thread_event_repeat_ALL = thread_event_repeat_ALL #Thread event used in Threading
        self.repeat_handle = self.repeat_ALL_handle = None

        # print('self.thread_event_repeat: ', self.thread_event_repeat)
        # print('self.thread_event_repeat_ALL: ', self.thread_event_repeat_ALL)
        # print('self.dll_LC18: ', self.dll_LC18)
        self.ctrl = LC18_Control(self.dll_LC18)
        # print(self.ctrl)
        self.__read_mode = False ### When Software is reading from device, we need to stop writing to device process.

        self.repeat_status = False
        self.repeat_ALL_status = False
        self.repeat_mode_str = 'infinity'#'infinity' or #'finite'
        self.repeat_num = 1

        self.ch_sel_str = '1 - 4'

        self.addr_a = np.array([0, 0, 0, 0]) #board address ch 1-4 #each array values represents the switches in binary, 0 or 1. #0000
        self.addr_b = np.array([1, 0, 0, 0]) #board address ch 5-8 #each array values represents the switches in binary, 0 or 1. #0001
        self.addr_c = np.array([0, 1, 0, 0]) #board address ch 9-12 #each array values represents the switches in binary, 0 or 1. #0010
        self.addr_d = np.array([1, 1, 0, 0]) #board address ch 13-16 #each array values represents the switches in binary, 0 or 1. #0011

        self.hmap_addr = {}
        self.hmap_addr['a'] = binary_to_dec(self.addr_a[0], self.addr_a[1], self.addr_a[2], self.addr_a[3], reverse_str = True)
        self.hmap_addr['b'] = binary_to_dec(self.addr_b[0], self.addr_b[1], self.addr_b[2], self.addr_b[3], reverse_str = True)
        self.hmap_addr['c'] = binary_to_dec(self.addr_c[0], self.addr_c[1], self.addr_c[2], self.addr_c[3], reverse_str = True)
        self.hmap_addr['d'] = binary_to_dec(self.addr_d[0], self.addr_d[1], self.addr_d[2], self.addr_d[3], reverse_str = True)

        self.mode_list = ['Constant Mode', 'Strobe Mode', 'Trigger Mode']

        self.addr_0_var = tk.IntVar(value = 0)
        self.addr_1_var = tk.IntVar(value = 0)
        self.addr_2_var = tk.IntVar(value = 0)
        self.addr_3_var = tk.IntVar(value = 0)

        self.interval_time = 0.5

        self.__reset_all = False
        self.refresh_iter = 0
        self.reset_iter = 0
        self.save_iter = 0

        self.thread_refresh_event = threading.Event()
        self.thread_reset_event = threading.Event()
        self.thread_save_event = threading.Event()

        self.GUI_refresh_handle = None
        self.GUI_reset_handle = None
        self.GUI_save_handle = None

        self.interval_lb_var    = tk.StringVar()
        self.interval_var       = tk.StringVar()
        self.repeat_mode_var    = tk.StringVar()
        self.repeat_num_var     = tk.StringVar()

        self.hmap_param_init()
        self.refresh_gui_init()
        self.reset_gui_init()
        self.save_gui_init()
        self.LC18_interface()

    def show(self, firmware_version = None):
        self.refresh_btn_click(override = True)
        self.firmware_version.set('Board Firmware:\n' + "{}".format(firmware_version))

    def hide(self):
        self.stop_threads()
        self.firmware_version.set('Board Firmware:\n' + "None")

    def hmap_param_init(self):
        def hashmap_init(ch_index, addr_id):
            hashmap = {}
            hashmap['mode']         = {'widget' : None, 'value' : None}
            hashmap['multiplier']   = {'widget' : None, 'value' : None} ### we will insert tk.StringVar()
            hashmap['intensity']    = {'widget' : None, 'value' : None} ### we will insert tk.StringVar()
            hashmap['strobe_delay'] = {'widget' : None, 'value' : None} ### we will insert tk.StringVar()
            hashmap['strobe_width'] = {'widget' : None, 'value' : None} ### we will insert tk.StringVar()
            hashmap['output_delay'] = {'widget' : None, 'value' : None} ### we will insert tk.StringVar()
            hashmap['output_width'] = {'widget' : None, 'value' : None} ### we will insert tk.StringVar()
            hashmap['ch_index']     = ch_index
            hashmap['addr_id']      = addr_id
            return hashmap

        self.hmap_param = {}
        for i in range(1, 17):
            ch_index = i%4
            if ch_index == 0:
                ch_index = 4
            if 1 <= i <= 4:
                addr_id = 'a'

            elif 5 <= i <= 8:
                addr_id = 'b'

            elif 9 <= i <= 12:
                addr_id = 'c'

            elif 13 <= i <= 16:
                addr_id = 'd'
            self.hmap_param['{}'.format(i)] = hashmap_init(ch_index, addr_id)

            # print(self.hmap_param)

    def refresh_gui_init(self):
        self.refresh_progress_fr = tk.Frame(self.master, bg = 'white')

        self.refresh_progress_lb = tk.Label(self.refresh_progress_fr, bg = 'white', font = 'Helvetica 20 bold')
        self.refresh_progress_lb['text']= 'Loading...'
        self.refresh_progress_lb.place(relx=0.5, rely=0.5, anchor = 'center')

    def refresh_btn_click(self, override = False):
        proceed = True
        if override == False:
            ask_msgbox = Ask_Msgbox('Do you want to REFRESH values?', title = 'Refresh', parent = self, message_anchor = 'w')
            if ask_msgbox.ask_result() == True:
                proceed = True
            else:
                proceed = False

        if proceed == True:
            #### since we used .place() method on self.master to display the LC18 GUI. we use .place() method for this as well
            self.refresh_progress_fr.place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 1, relheight = 1, anchor = 'nw')
            self.refresh_progress_fr.lift()
            self.scroll_class.canvas_view(relx = 0.15, rely = 0.25)
            self.thread_refresh_func()
            self.refresh_gui_update()

    def thread_refresh_func(self):
        self.__read_mode = True
        self.thread_refresh_handle = threading.Thread(target = self.refresh_event)
        self.thread_refresh_handle.start()

    def refresh_gui_update(self):
        # print('Updating...')
        self.GUI_refresh_handle = self.after(150, self.refresh_gui_update)

        self.refresh_iter = self.refresh_iter + 1

        if self.refresh_iter <= 6:
            self.refresh_progress_lb['text'] = 'Loading'
        elif 6 < self.refresh_iter <= 12:
            self.refresh_progress_lb['text'] = 'Loading.'
        elif 12 < self.refresh_iter <= 18:
            self.refresh_progress_lb['text'] = 'Loading..'
        elif 18 < self.refresh_iter <= 24:
            self.refresh_progress_lb['text'] = 'Loading...'
        elif self.refresh_iter > 24:
            self.refresh_iter = 0

        if self.thread_refresh_event.isSet():
            self.after_cancel(self.GUI_refresh_handle)
            self.refresh_progress_fr.place_forget()
            self.thread_refresh_event.clear()
            self.scroll_class.canvas_view(relx = 0, rely = 0)
            # print('Update Complete!')
            #print(self.thread_refresh_handle)
            self.__read_mode = False

        #print(self.GUI_refresh_handle)
    
    def reset_gui_init(self):
        self.reset_progress_fr = tk.Frame(self.master, bg = 'white')

        self.reset_progress_lb = tk.Label(self.reset_progress_fr, bg = 'white', font = 'Helvetica 20 bold')
        self.reset_progress_lb['text']= 'Resetting...'
        self.reset_progress_lb.place(relx=0.5, rely=0.5, anchor = 'center')

    def reset_btn_click(self, override = False, reset_all = False):
        proceed = True
        if override == False:
            if reset_all == True:
                ask_msgbox = Ask_Msgbox('Do you want to RESET ALL values?', title = 'Reset All', parent = self, message_anchor = 'w')
                if ask_msgbox.ask_result() == True:
                    proceed = True
                else:
                    proceed = False

            elif reset_all == False:
                ask_msgbox = Ask_Msgbox('Do you want to RESET values?', title = 'Reset', parent = self, message_anchor = 'w')
                if ask_msgbox.ask_result() == True:
                    proceed = True
                else:
                    proceed = False

        if proceed == True:
            if reset_all == True or reset_all == False:
                self.__reset_all = reset_all
                #### since we used .place() method on self.master to display the LC18 GUI. we use .place() method for this as well
                self.reset_progress_fr.place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 1, relheight = 1, anchor = 'nw')
                self.reset_progress_fr.lift()
                self.scroll_class.canvas_view(relx = 0.15, rely = 0.25)
                self.thread_reset_func()
                self.reset_gui_update()

    def thread_reset_func(self):
        self.thread_reset_handle = threading.Thread(target=self.reset_event)
        self.thread_reset_handle.start()

    def reset_gui_update(self):
        #print('Resetting...')
        self.GUI_reset_handle = self.after(150, self.reset_gui_update)

        self.reset_iter = self.reset_iter + 1

        if self.reset_iter <= 6:
            self.reset_progress_lb['text'] = 'Resetting'

        elif 6 < self.reset_iter <= 12:
            self.reset_progress_lb['text'] = 'Resetting.'

        elif 12 < self.reset_iter <= 18:
            self.reset_progress_lb['text'] = 'Resetting..'

        elif 18 < self.reset_iter <= 24:
            self.reset_progress_lb['text'] = 'Resetting...'

        elif self.reset_iter > 24:
            self.reset_iter = 0

        if self.thread_reset_event.isSet():
            self.after_cancel(self.GUI_reset_handle)
            self.reset_progress_fr.place_forget()
            self.thread_reset_event.clear()
            self.scroll_class.canvas_view(relx = 0, rely = 0)
            #print('Reset Complete!')
            #print(self.thread_reset_handle)
            self.__reset_all = False

        #print(self.GUI_reset_handle)

    def save_gui_init(self):
        self.save_progress_fr = tk.Frame(self.master, bg = 'white')

        self.save_progress_lb = tk.Label(self.save_progress_fr, bg = 'white', font = 'Helvetica 20 bold')
        self.save_progress_lb['text']= 'Saving...'
        self.save_progress_lb.place(relx=0.5, rely=0.5, anchor = 'center')

    def save_btn_click(self):
        self.save_progress_fr.place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 1, relheight = 1, anchor = 'nw')
        self.save_progress_fr.lift()
        self.scroll_class.canvas_view(relx = 0.15, rely = 0.25)
        self.thread_save_func()
        self.save_gui_update()

    def thread_save_func(self):
        self.thread_save_handle = threading.Thread(target = self.save_out_param)
        self.thread_save_handle.start()

    def save_gui_update(self):
        self.GUI_save_handle = self.after(150, self.save_gui_update)

        self.save_iter = self.save_iter + 1

        if self.save_iter <= 6:
            self.save_progress_lb['text'] = 'Saving'

        elif 6 < self.save_iter <= 12:
            self.save_progress_lb['text'] = 'Saving.'

        elif 12 < self.save_iter <= 18:
            self.save_progress_lb['text'] = 'Saving..'

        elif 18 < self.save_iter <= 24:
            self.save_progress_lb['text'] = 'Saving...'

        elif self.save_iter > 24:
            self.save_iter = 0

        if self.thread_save_event.isSet():
            self.after_cancel(self.GUI_save_handle)
            self.save_progress_fr.place_forget()
            self.thread_save_event.clear()
            self.scroll_class.canvas_view(relx = 0, rely = 0)

    ###############################################################################################
    ### MAIN INTERFACE INIT
    def LC18_interface(self):
        #MAIN PANEL GENERATION
        self.grid_columnconfigure(index = 0, weight = 1, min = 137)
        self.grid_columnconfigure(index = 1, weight = 10, min = 920)
        self.grid_rowconfigure(index = 2, weight = 1)
        
        self.ch_sel_btn_gen()

        self.left_anchor_fr = tk.Frame(self, width = 137, height = 800, highlightcolor = 'white', highlightthickness = 1)
        self.left_anchor_fr['bg'] = 'DarkSlateGray2'
        self.left_anchor_fr.grid(column = 0, row = 0, columnspan = 1, rowspan = 3, padx = (1,1), pady = (1,1), sticky = 'nwse')
        
        self.left_anchor_fr.grid_columnconfigure(index = 0, weight = 1)

        self.main_control_gen()
        self.repeat_ALL_ctrl_gen()

        self.top_anchor_fr = tk.Frame(self, width = 920, height = 120, highlightthickness = 0)
        self.top_anchor_fr['bg'] = 'white'
        self.top_anchor_fr.grid(column = 1, row = 1, columnspan = 1, rowspan = 1, padx = (2,1), pady = (1,1), sticky = 'nwse')

        self.top_anchor_fr.grid_columnconfigure(index = 0, weight = 1)
        self.top_anchor_fr.grid_columnconfigure(index = 1, weight = 1)
        self.top_anchor_fr.grid_rowconfigure(index = 0, weight = 1)

        self.ch_setting_gen()
        self.strobe_setting_gen()

        self.ch_ctrl_gui_dict = {   '1 - 4'  : self.ch_setting_gui('1 - 4')
                                  , '5 - 8'  : self.ch_setting_gui('5 - 8')
                                  , '9 - 12' : self.ch_setting_gui('9 - 12')
                                  , '13 - 16': self.ch_setting_gui('13 - 16')}

        self.ch_sel_btn1.invoke()

    def main_control_gen(self):
        self.main_ctrl_prnt = tk.Frame(self.left_anchor_fr, bg = 'DarkSlateGray2', highlightbackground="white", highlightthickness=1)
        self.main_ctrl_prnt['width'] =  120 + 5
        self.main_ctrl_prnt['height'] = 200
        self.main_ctrl_prnt.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,5), sticky = 'nwse')

        tk_lb = tk.Label(self.main_ctrl_prnt, justify = 'left', font = "Helvetica 14 bold", anchor = 'nw')
        tk_lb['text'] = 'Main'
        tk_lb['bg'] = 'DarkSlateGray2'
        tk_lb['width'] = len('Main')
        tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (5,1), sticky = 'nwse')

        self.main_ctrl_prnt.grid_columnconfigure(index = 0, weight = 1)
        self.refresh_btn = WrappingButton(self.main_ctrl_prnt, width = 10, relief = tk.GROOVE
            , text='Refresh', font = "Helvetica 12", justify = tk.CENTER, anchor = 'c')
        self.refresh_btn['command'] = self.refresh_btn_click
        self.refresh_btn.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (20,20), pady = (5,1), sticky = 'nwse')


        self.EEPROM_ALL_btn = WrappingButton(self.main_ctrl_prnt, width = 10, relief = tk.GROOVE
            , text = 'Save All EEPROM', font = 'Helvetica 12', justify = tk.CENTER, anchor = 'c')
        self.EEPROM_ALL_btn['command'] = self.save_btn_click
        self.EEPROM_ALL_btn.grid(column = 0, row = 2, columnspan = 1, rowspan = 1, padx = (20,20), pady = (5,1), sticky = 'nwse')


        self.strobe_ALL_btn = WrappingButton(self.main_ctrl_prnt, width = 10, relief = tk.GROOVE
            , text='Strobe All', font = "Helvetica 12", justify = tk.CENTER, anchor = 'c')
        self.strobe_ALL_btn['command'] = self.strobe_channel_repeat_ALL
        self.strobe_ALL_btn.grid(column = 0, row = 3, columnspan = 1, rowspan = 1, padx = (20,20), pady = (5,1), sticky = 'nwse')


        self.RESET_btn = WrappingButton(self.main_ctrl_prnt, width = 10, relief = tk.GROOVE, activeforeground= 'white', fg="white", activebackground = 'navy', bg = 'royal blue'
              , text='RESET', font = "Helvetica 11 bold", justify = tk.CENTER, anchor = 'c')
        self.RESET_btn['command'] = partial(self.reset_btn_click, reset_all = False)
        self.RESET_btn.grid(column = 0, row = 4, columnspan = 1, rowspan = 1, padx = (20,20), pady = (5,1), sticky = 'nwse')

        self.RESET_ALL_btn = WrappingButton(self.main_ctrl_prnt, width = 10, relief = tk.GROOVE, activeforeground= 'white', fg="white", activebackground = 'navy', bg = 'royal blue'
              , text='RESET ALL', font = "Helvetica 11 bold", justify = tk.CENTER, anchor = 'c')
        self.RESET_ALL_btn['command'] = partial(self.reset_btn_click, reset_all = True)
        self.RESET_ALL_btn.grid(column = 0, row = 5, columnspan = 1, rowspan = 1, padx = (20,20), pady = (5,5), sticky = 'nwse')

    def ch_sel_btn_gen(self):
        self.ch_sel_btn_subprnt = tk.Frame(self, highlightthickness = 0, bd = 0)
        self.ch_sel_btn_subprnt['bg'] = 'white'
        prnt = self.ch_sel_btn_subprnt
        self.ch_sel_btn1 = tk.Button(prnt, relief = tk.GROOVE, text = 'Channel 1 - 4', width = 12, font='Helvetica 11 bold')
        self.ch_sel_btn2 = tk.Button(prnt, relief = tk.GROOVE, text = 'Channel 5 - 8', width = 12, font='Helvetica 11 bold')
        self.ch_sel_btn3 = tk.Button(prnt, relief = tk.GROOVE, text = 'Channel 9 - 12', width = 12, font='Helvetica 11 bold')
        self.ch_sel_btn4 = tk.Button(prnt, relief = tk.GROOVE, text = 'Channel 13 - 16', width = 12, font='Helvetica 11 bold')

        self.ch_sel_btn1['command'] = partial(self.ch_sel_func, '1 - 4'  , self.ch_sel_btn1, self.ch_sel_btn2, self.ch_sel_btn3, self.ch_sel_btn4)
        self.ch_sel_btn2['command'] = partial(self.ch_sel_func, '5 - 8'  , self.ch_sel_btn2, self.ch_sel_btn1, self.ch_sel_btn3, self.ch_sel_btn4)
        self.ch_sel_btn3['command'] = partial(self.ch_sel_func, '9 - 12' , self.ch_sel_btn3, self.ch_sel_btn1, self.ch_sel_btn2, self.ch_sel_btn4)
        self.ch_sel_btn4['command'] = partial(self.ch_sel_func, '13 - 16', self.ch_sel_btn4, self.ch_sel_btn1, self.ch_sel_btn2, self.ch_sel_btn3)

        self.hmap_ch_btn = {}
        self.hmap_ch_btn[str(self.ch_sel_btn1)] = partial(self.ch_sel_func, '1 - 4'  , self.ch_sel_btn1, self.ch_sel_btn2, self.ch_sel_btn3, self.ch_sel_btn4)
        self.hmap_ch_btn[str(self.ch_sel_btn2)] = partial(self.ch_sel_func, '5 - 8'  , self.ch_sel_btn2, self.ch_sel_btn1, self.ch_sel_btn3, self.ch_sel_btn4)
        self.hmap_ch_btn[str(self.ch_sel_btn3)] = partial(self.ch_sel_func, '9 - 12' , self.ch_sel_btn3, self.ch_sel_btn1, self.ch_sel_btn2, self.ch_sel_btn4)
        self.hmap_ch_btn[str(self.ch_sel_btn4)] = partial(self.ch_sel_func, '13 - 16', self.ch_sel_btn4, self.ch_sel_btn1, self.ch_sel_btn2, self.ch_sel_btn3)

        self.ch_sel_btn1.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,5), pady = (1,1), sticky = 'nwse')
        self.ch_sel_btn2.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (1,5), pady = (1,1), sticky = 'nwse')
        self.ch_sel_btn3.grid(column = 2, row = 0, columnspan = 1, rowspan = 1, padx = (1,5), pady = (1,1), sticky = 'nwse')
        self.ch_sel_btn4.grid(column = 3, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')

        self.ch_sel_btn_subprnt.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (2,1), pady = (1,1), sticky = 'nwse')

    def ch_sel_func(self, str_mode, active_widget, *inactive_args, **inactive_kwargs):
        self.ch_sel_btn_state(active_widget, *inactive_args, **inactive_kwargs)
        active_widget['command'] = lambda: None

        for tk_btn in inactive_args:
            if str(tk_btn) in self.hmap_ch_btn:
                tk_btn['command'] = self.hmap_ch_btn[str(tk_btn)]

        for tk_btn in inactive_kwargs.values():
            if str(tk_btn) in self.hmap_ch_btn:
                tk_btn['command'] = self.hmap_ch_btn[str(tk_btn)]

        self.ch_sel_str = str_mode
        self.board_addr_load()

        for kw, tk_gui in self.ch_ctrl_gui_dict.items():
            if kw == str_mode:
                tk_gui.grid(column = 1, row = 2, columnspan = 1, rowspan = 1, padx = (2,2), pady = (3,1), sticky = 'nwse')
            else:
                tk_gui.grid_forget()

            tk_gui.update_idletasks()

    def ch_setting_gen(self):
        self.ch_sett_prnt = tk.Frame(self.top_anchor_fr, width = 430, height = 120, highlightthickness = 0)
        self.ch_sett_prnt['bg'] = 'DarkSlateGray2'
        self.ch_sett_prnt.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')

        self.ch_sett_prnt.grid_columnconfigure(index = 0, weight = 1)
        self.ch_sett_prnt.grid_columnconfigure(index = 1, weight = 1, min = 140)
        self.ch_sett_prnt.grid_columnconfigure(index = 2, weight = 1)

        self.ch_sett_prnt.grid_rowconfigure(index = 0, weight = 1)
        self.ch_sett_prnt.grid_rowconfigure(index = 1, weight = 1)

        ch_sett_tk_lb = WrappingLabel(self.ch_sett_prnt, text = 'Channel Settings', font='Helvetica 14 bold', bg = 'DarkSlateGray2', justify= tk.LEFT, anchor = 'c')
        ch_sett_tk_lb['width'] = len('Settings')
        # ch_sett_tk_lb.place(x=2,y=25)
        ch_sett_tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 2, padx = (1,1), pady = (1,1), sticky = 'nwse')

        self.board_addr_fr = tk.Frame(self.ch_sett_prnt, width = 140, height = 85, bg = 'DarkSlateGray2', highlightbackground="white", highlightcolor = 'white', highlightthickness=1)
        # self.board_addr_fr.place(x= 120, y = 10) 
        self.board_addr_fr.grid(column = 1, row = 0, columnspan = 1, rowspan = 2, padx = (5,5), pady = (5,5), sticky = 'nwse')
        self.board_addr_gui()

        self.firmware_version = tk.StringVar()
        self.board_firmware = WrappingLabel(self.ch_sett_prnt, textvariable = self.firmware_version, font='Helvetica 12 bold', bg = 'DarkSlateGray2', justify= tk.LEFT, anchor = 'c')
        self.board_firmware['width'] = len('Board Firmware')
        self.firmware_version.set('Board Firmware:\n' + "None")
        # self.board_firmware.place(x=270, y=2)
        self.board_firmware.grid(column = 2, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1))

        self.EEPROM_btn = tk.Button(self.ch_sett_prnt, relief = tk.GROOVE, text='Save EEPROM', font = "Helvetica 12")
        self.EEPROM_btn['command'] = self.save_btn_click
        self.EEPROM_btn.grid(column = 2, row = 1, columnspan = 1, rowspan = 1, padx = (1,5), pady = (1,1))

    def board_addr_gui(self):
        self.board_addr_fr.grid_columnconfigure(index = 0, weight = 1)
        self.board_addr_fr.grid_rowconfigure(index = 1, weight = 1)
        addr_bg = 'DarkSlateGray2'

        tk_lb = tk.Label(self.board_addr_fr, bg = addr_bg, text = 'Board Address:', font = "Helvetica 11 bold"
            , justify = 'left', anchor = 'nw')
        tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (5,1), pady = (5,1), sticky = 'nwse')

        addr_prnt = tk.Frame(self.board_addr_fr)
        addr_prnt['bg'] = addr_bg
        addr_prnt.grid_columnconfigure(index = 0, weight = 1)
        addr_prnt.grid_columnconfigure(index = 1, weight = 1)
        addr_prnt.grid_columnconfigure(index = 2, weight = 1)
        addr_prnt.grid_columnconfigure(index = 3, weight = 1)

        addr_0_lb = tk.Label(addr_prnt, bg = addr_bg, text = '0', font='Helvetica 11 bold')
        addr_1_lb = tk.Label(addr_prnt, bg = addr_bg, text = '1', font='Helvetica 11 bold')
        addr_2_lb = tk.Label(addr_prnt, bg = addr_bg, text = '2', font='Helvetica 11 bold')
        addr_3_lb = tk.Label(addr_prnt, bg = addr_bg, text = '3', font='Helvetica 11 bold')
        
        addr_0_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')
        addr_1_lb.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')
        addr_2_lb.grid(column = 2, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')
        addr_3_lb.grid(column = 3, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')
        
        addr_0_chbox = tk.Checkbutton(addr_prnt, bg = addr_bg, activebackground = addr_bg, variable = self.addr_0_var)
        addr_1_chbox = tk.Checkbutton(addr_prnt, bg = addr_bg, activebackground = addr_bg, variable = self.addr_1_var)
        addr_2_chbox = tk.Checkbutton(addr_prnt, bg = addr_bg, activebackground = addr_bg, variable = self.addr_2_var)
        addr_3_chbox = tk.Checkbutton(addr_prnt, bg = addr_bg, activebackground = addr_bg, variable = self.addr_3_var)

        widget_take_focus(addr_0_chbox, addr_1_chbox
                        , addr_2_chbox, addr_3_chbox)

        addr_0_chbox.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')
        addr_1_chbox.grid(column = 1, row = 1, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')
        addr_2_chbox.grid(column = 2, row = 1, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')
        addr_3_chbox.grid(column = 3, row = 1, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')

        addr_0_chbox['command'] = self.board_addr_click
        addr_1_chbox['command'] = self.board_addr_click
        addr_2_chbox['command'] = self.board_addr_click
        addr_3_chbox['command'] = self.board_addr_click

        addr_prnt.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (5,1), pady = (15,1), sticky = 'nwse')

    def board_addr_load(self):
        if self.ch_sel_str == '1 - 4':
            self.addr_0_var.set(self.addr_a[0])
            self.addr_1_var.set(self.addr_a[1])
            self.addr_2_var.set(self.addr_a[2])
            self.addr_3_var.set(self.addr_a[3])

        elif self.ch_sel_str == '5 - 8':
            self.addr_0_var.set(self.addr_b[0])
            self.addr_1_var.set(self.addr_b[1])
            self.addr_2_var.set(self.addr_b[2])
            self.addr_3_var.set(self.addr_b[3])

        elif self.ch_sel_str == '9 - 12':
            self.addr_0_var.set(self.addr_c[0])
            self.addr_1_var.set(self.addr_c[1])
            self.addr_2_var.set(self.addr_c[2])
            self.addr_3_var.set(self.addr_c[3])

        elif self.ch_sel_str == '13 - 16':
            self.addr_0_var.set(self.addr_d[0])
            self.addr_1_var.set(self.addr_d[1])
            self.addr_2_var.set(self.addr_d[2])
            self.addr_3_var.set(self.addr_d[3])

    def board_addr_click(self, event = None):
        if self.ch_sel_str == '1 - 4':
            self.addr_a[0] = self.addr_0_var.get()
            self.addr_a[1] = self.addr_1_var.get()
            self.addr_a[2] = self.addr_2_var.get()
            self.addr_a[3] = self.addr_3_var.get()
            self.hmap_addr['a'] = binary_to_dec(self.addr_a[0], self.addr_a[1], self.addr_a[2], self.addr_a[3], reverse_str = True)

        elif self.ch_sel_str == '5 - 8':
            self.addr_b[0] = self.addr_0_var.get()
            self.addr_b[1] = self.addr_1_var.get()
            self.addr_b[2] = self.addr_2_var.get()
            self.addr_b[3] = self.addr_3_var.get()
            self.hmap_addr['b'] = binary_to_dec(self.addr_b[0], self.addr_b[1], self.addr_b[2], self.addr_b[3], reverse_str = True)
            
        elif self.ch_sel_str == '9 - 12':
            self.addr_c[0] = self.addr_0_var.get()
            self.addr_c[1] = self.addr_1_var.get()
            self.addr_c[2] = self.addr_2_var.get()
            self.addr_c[3] = self.addr_3_var.get()
            self.hmap_addr['c'] = binary_to_dec(self.addr_c[0], self.addr_c[1], self.addr_c[2], self.addr_c[3], reverse_str = True)

        elif self.ch_sel_str == '13 - 16':
            self.addr_d[0] = self.addr_0_var.get()
            self.addr_d[1] = self.addr_1_var.get()
            self.addr_d[2] = self.addr_2_var.get()
            self.addr_d[3] = self.addr_3_var.get()
            self.hmap_addr['d'] = binary_to_dec(self.addr_d[0], self.addr_d[1], self.addr_d[2], self.addr_d[3], reverse_str = True)

    def strobe_setting_gen(self):
        self.strobe_sett_prnt = tk.Frame(self.top_anchor_fr, width = 488, height = 120, highlightthickness = 0)
        self.strobe_sett_prnt['bg'] = 'DarkSlateGray2'
        self.strobe_sett_prnt.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (2,1), pady = (1,1), sticky = 'nwse')

        self.strobe_sett_prnt.grid_columnconfigure(index = 0, weight = 1)
        self.strobe_sett_prnt.grid_rowconfigure(index = 0, weight = 1)

        auto_strobe_tk_lb = WrappingLabel(self.strobe_sett_prnt, text = 'Auto Strobe Settings', font='Helvetica 14 bold', justify = 'left', anchor = 'c')
        auto_strobe_tk_lb['width'] = len('Settings')
        auto_strobe_tk_lb['bg'] = 'DarkSlateGray2'
        auto_strobe_tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')
        self.strobe_ch_sel()
        self.repeat_ctrl_gen()

    def strobe_ch_sel(self):
        self.strobe_sett_prnt.grid_columnconfigure(index = 1, weight = 1, min = 180)
        self.ch_sel_subprnt = tk.Frame(self.strobe_sett_prnt, width = 180, height = 115, highlightbackground="white", highlightthickness=1, highlightcolor = "white")
        self.ch_sel_subprnt['bg'] = 'DarkSlateGray2'
        self.ch_sel_subprnt.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,5), sticky = 'nwse')

        self.ch_sel_subprnt.grid_columnconfigure(index = 0, weight = 1)

        self.ch_sel_subprnt.grid_rowconfigure(index = 0, weight = 0)
        """ The Label """
        ch_sel_tk_lb = tk.Label(self.ch_sel_subprnt, text = 'Strobe Channel:', font='Helvetica 11 bold', justify = tk.LEFT, anchor = 'nw')
        ch_sel_tk_lb['bg'] = 'DarkSlateGray2'
        ch_sel_tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (5,5), pady = (1,1), sticky = 'nwse')

        self.ch_sel_subprnt.grid_rowconfigure(index = 1, weight = 1)
        """ Frame to hold all the checkbutton widgets """
        ch_sel_fr = tk.Frame(self.ch_sel_subprnt, highlightthickness = 0, bd = 0)
        ch_sel_fr['bg'] = 'DarkSlateGray2'
        ch_sel_fr.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (5,5), pady = (1,1), sticky = 'nwse')

        self.ch_sel_var_hmap = {}
        for i in range(1,17):
            self.ch_sel_var_hmap['{}'.format(i)] = tk.IntVar(value = 0)
        i = 1
        row_j = 0
        col_j = 0
        ch_sel_fr.grid_columnconfigure(index = 0, weight = 1)
        ch_sel_fr.grid_columnconfigure(index = 1, weight = 1)
        ch_sel_fr.grid_columnconfigure(index = 2, weight = 1)
        ch_sel_fr.grid_columnconfigure(index = 3, weight = 1)

        ch_sel_fr.grid_rowconfigure(index = 0, weight = 1)
        ch_sel_fr.grid_rowconfigure(index = 1, weight = 1)
        ch_sel_fr.grid_rowconfigure(index = 2, weight = 1)
        ch_sel_fr.grid_rowconfigure(index = 3, weight = 1)
        for tk_var in self.ch_sel_var_hmap.values():
            tk_fr, tk_cbtn = self.strobe_ch_sel_widget(ch_sel_fr, tk_var, '{}'.format(i))
            if (i - 1)%4 == 0 and i > 1:
                row_j = 0
                col_j += 1
            if col_j < 3:
                tk_fr.grid(column = col_j, row = row_j, columnspan = 1, rowspan = 1, padx = (2,1), pady = (1,1), sticky = 'nwse')
            elif col_j == 3:
                tk_fr.grid(column = col_j, row = row_j, columnspan = 1, rowspan = 1, padx = (2,2), pady = (1,1), sticky = 'nwse')
            i += 1
            row_j += 1

    def strobe_ch_sel_widget(self, master, tk_var, lb_text):
        tk_fr = tk.Frame(master, highlightthickness = 0, bd = 0)
        tk_fr['bg'] = 'DarkSlateGray2'

        tk_fr.grid_columnconfigure(index = 0, weight = 1)
        tk_fr.grid_columnconfigure(index = 1, weight = 1)
        tk_fr.grid_rowconfigure(index = 0, weight = 1)

        tk_lb = tk.Label(tk_fr, font = 'Helvetica 11 bold', justify = tk.RIGHT, anchor = 'e')
        tk_lb['text'] = lb_text
        tk_lb['bg'] = 'DarkSlateGray2'
        tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')

        tk_cbtn = tk.Checkbutton(tk_fr, anchor = 'w', padx = 0, pady = 0)
        if isinstance(tk_var, tk.IntVar) == True:
            tk_cbtn['variable'] = tk_var
        tk_cbtn['bg'] = 'DarkSlateGray2'
        tk_cbtn['activebackground'] = 'DarkSlateGray2'

        widget_take_focus(tk_cbtn)

        tk_cbtn.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')

        return tk_fr, tk_cbtn

    def repeat_ctrl_gen(self):
        #REPEAT STROBE CONTROL
        self.strobe_sett_prnt.grid_columnconfigure(index = 2, weight = 1, min = 205)
        self.repeat_prnt = tk.Frame(self.strobe_sett_prnt, bg = 'DarkSlateGray2', highlightbackground="white", highlightthickness=1, highlightcolor="white")
        self.repeat_prnt['width'] = 205
        self.repeat_prnt['height'] = 115

        self.repeat_prnt.grid(column = 2, row = 0, columnspan = 1, rowspan = 1, padx = (1,5), pady = (5,5), sticky = 'nwse')

        self.repeat_prnt.grid_columnconfigure(index = 0, weight = 1)
        self.repeat_prnt.grid_columnconfigure(index = 1, weight = 1)

        tk_lb = WrappingLabel(self.repeat_prnt, text = 'Interval:', font = "Helvetica 11"
            , justify = tk.LEFT, anchor = 'w')
        tk_lb['bg'] = 'DarkSlateGray2'
        tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')

        interval_tk_lb = tk.Label(self.repeat_prnt, textvariable = self.interval_lb_var, font = "Helvetica 11", justify = tk.LEFT, anchor = 'nw')
        interval_tk_lb['bg'] = 'DarkSlateGray2'

        self.interval_entry = tk.Spinbox(master = self.repeat_prnt, width = 7, from_=0.5, to= 9999, increment = 0.001, font = "Helvetica 11"
                                     , highlightbackground="black", highlightthickness=1)
        self.interval_entry['textvariable'] = self.interval_var

        Validate_Float(self.interval_entry, self.interval_var, only_positive = True, lo_limit = 0.5, hi_limit = 9999, decimal_places = 3)

        self.interval_entry['command'] = self.interval_sbox_func
        self.interval_entry.bind('<Return>', self.interval_sbox_func)
        self.interval_entry.bind('<FocusOut>', self.interval_sbox_func)

        self.interval_lb_var.set("{} seconds".format(str_float(self.interval_time, 3)))
        self.interval_var.set(self.interval_time)

        self.interval_entry.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,1), sticky = 'nwse')
        interval_tk_lb.grid(column = 0, row = 2, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,1), sticky = 'nwse')

        self.repeat_btn = tk.Button(self.repeat_prnt, relief = tk.GROOVE, width = 6, font = "Helvetica 12 bold")
        self.repeat_btn = self.repeat_btn_widget(self.repeat_status, self.repeat_btn)
        self.repeat_btn['command'] = self.repeat_btn_click
        self.repeat_btn.grid(column = 0, row = 3, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,1), sticky = 'nwse')

        tk_lb = tk.Label(self.repeat_prnt, text = 'Repeat Mode:', font = "Helvetica 11", bg = 'DarkSlateGray2', justify = 'left')
        tk_lb.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nw')

        self.infinity_radio_btn = tk.Radiobutton(self.repeat_prnt,variable=self.repeat_mode_var, value='infinity', bg = 'DarkSlateGray2', activebackground = 'DarkSlateGray2'
            , anchor = 'nw', bd = 2 + 2) ## Put extra 2 pixels to the bd for alignment
        tk_img_insert(self.infinity_radio_btn, self.gui_graphic['infinity_icon'], img_scale = 0.04)
        self.infinity_radio_btn['command'] = self.repeat_mode_set


        finite_subprnt = tk.Frame(self.repeat_prnt)
        finite_subprnt['bg'] = 'DarkSlateGray2'
        self.finite_radio_btn = tk.Radiobutton(finite_subprnt, variable=self.repeat_mode_var, value='finite', bg = 'DarkSlateGray2', activebackground = 'DarkSlateGray2'
            , anchor = 'nw', bd = 2)
        self.finite_radio_btn['command'] = self.repeat_mode_set
        
        self.repeat_num_sbox = tk.Spinbox(master = finite_subprnt, width = 5, from_=1, to= 9999, textvariable = self.repeat_num_var, font = "Helvetica 11"
                                     , highlightbackground="black", highlightthickness=1)
        self.repeat_num_sbox['command'] = self.repeat_num_sbox_func
        self.repeat_num_sbox.bind('<Return>', self.repeat_num_sbox_func)
        self.repeat_num_sbox.bind('<Tab>', self.repeat_num_sbox_func)
        self.repeat_num_sbox.bind('<FocusOut>', self.repeat_num_sbox_func)

        self.repeat_mode_var.set(self.repeat_mode_str)
        self.repeat_num_var.set(str(self.repeat_num))
        
        self.finite_radio_btn.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nw')
        finite_subprnt.grid_columnconfigure(index = 1, weight = 1)
        self.repeat_num_sbox.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (2,1), pady = (1,1), sticky = 'nwse')

        Validate_Int(self.repeat_num_sbox, self.repeat_num_var, only_positive = True, lo_limit = 1, hi_limit = 9999)

        self.repeat_num_sbox_state(self.repeat_num_sbox)
        self.infinity_radio_btn.grid(column = 1, row = 1, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,1), sticky = 'nw')
        finite_subprnt.grid(column = 1, row = 2, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,1), sticky = 'nwse')

        widget_take_focus(self.repeat_btn
                        , self.infinity_radio_btn
                        , self.finite_radio_btn
                        , self.repeat_num_sbox
                        , self.interval_entry)

    def repeat_ALL_ctrl_gen(self):
        self.repeat_ALL_prnt = tk.Frame(self.left_anchor_fr, bg = 'DarkSlateGray2', highlightbackground="white", highlightthickness=1, highlightcolor="white")
        self.repeat_ALL_prnt['width'] = 120 + 5
        self.repeat_ALL_prnt['height'] = 235

        self.repeat_ALL_prnt.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,5), sticky = 'nwse')
        self.repeat_ALL_prnt.grid_columnconfigure(index = 0, weight = 1)

        tk_lb = WrappingLabel(self.repeat_ALL_prnt, justify = 'left', font = "Helvetica 14 bold", anchor = 'nw')
        tk_lb['text'] = 'Auto Repeat All Strobe'
        tk_lb['bg'] = 'DarkSlateGray2'
        tk_lb['width'] = len('Auto Repeat ')
        tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (5,1), sticky = 'we')

        tk_lb = tk.Label(self.repeat_ALL_prnt, font = "Helvetica 11", anchor = 'nw')
        tk_lb['text'] = 'Interval:'
        tk_lb['bg'] = 'DarkSlateGray2'
        tk_lb.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (10,1), pady = (5,1), sticky = 'we')

        interval_tk_lb = tk.Label(self.repeat_ALL_prnt, textvariable = self.interval_lb_var, font = "Helvetica 11", anchor = 'nw')
        interval_tk_lb['bg'] = 'DarkSlateGray2'

        self.interval_entry_2 = tk.Spinbox(master = self.repeat_ALL_prnt, width = 7, from_=0.5, to= 9999, increment = 0.001, font = "Helvetica 11"
                                     , highlightbackground="black", highlightthickness=1)
        self.interval_entry_2['textvariable'] = self.interval_var

        Validate_Float(self.interval_entry_2, self.interval_var, only_positive = True, lo_limit = 0.5, hi_limit = 9999, decimal_places = 3)

        self.interval_entry_2['command'] = self.interval_sbox_func

        self.interval_entry_2.bind('<Return>', self.interval_sbox_func)
        self.interval_entry_2.bind('<FocusOut>', self.interval_sbox_func)

        self.interval_lb_var.set("{} seconds".format(str_float(self.interval_time, 3)))
        self.interval_var.set(self.interval_time)

        self.interval_entry_2.grid(column = 0, row = 2, columnspan = 1, rowspan = 1, padx = (10,20), pady = (2,1), sticky = 'we')
        interval_tk_lb.grid(column = 0, row = 3, columnspan = 1, rowspan = 1, padx = (10,20), pady = (1,1), sticky = 'we')


        tk_lb = tk.Label(self.repeat_ALL_prnt, font = "Helvetica 11", anchor = 'nw')
        tk_lb['text'] = 'Repeat Mode:'
        tk_lb['bg'] = 'DarkSlateGray2'
        tk_lb.grid(column = 0, row = 4, columnspan = 1, rowspan = 1, padx = (10,20), pady = (1,1), sticky = 'we')

        self.repeat_ALL_btn = tk.Button(self.repeat_ALL_prnt, relief = tk.GROOVE, width = 6, font = "Helvetica 12 bold")
        self.repeat_ALL_btn = self.repeat_btn_widget(self.repeat_ALL_status, self.repeat_ALL_btn)
        self.repeat_ALL_btn['command'] = self.repeat_ALL_btn_click

        self.infinity_radio_btn_2 = tk.Radiobutton(self.repeat_ALL_prnt,variable=self.repeat_mode_var, value='infinity', bg = 'DarkSlateGray2', activebackground = 'DarkSlateGray2'
            , anchor = 'nw', bd = 2 + 2) ## Put extra 2 pixels to the bd for alignment
        tk_img_insert(self.infinity_radio_btn_2, self.gui_graphic['infinity_icon'], img_scale = 0.04)
        self.infinity_radio_btn_2['command'] = self.repeat_mode_set


        finite_subprnt = tk.Frame(self.repeat_ALL_prnt)
        finite_subprnt['bg'] = 'DarkSlateGray2'
        self.finite_radio_btn_2 = tk.Radiobutton(finite_subprnt, variable=self.repeat_mode_var, value='finite', bg = 'DarkSlateGray2', activebackground = 'DarkSlateGray2'
            , anchor = 'nw', bd = 2)
        self.finite_radio_btn_2['command'] = self.repeat_mode_set

        self.repeat_num_sbox_2 = tk.Spinbox(master = finite_subprnt, width = 5, from_=1, to= 9999, textvariable = self.repeat_num_var, font = "Helvetica 11"
                                     , highlightbackground="black", highlightthickness=1)
        self.repeat_num_sbox_2['command'] = self.repeat_num_sbox_func
        self.repeat_num_sbox_2.bind('<Return>', self.repeat_num_sbox_func)
        self.repeat_num_sbox_2.bind('<Tab>', self.repeat_num_sbox_func)
        self.repeat_num_sbox_2.bind('<FocusOut>', self.repeat_num_sbox_func)

        self.repeat_mode_var.set(self.repeat_mode_str)
        self.repeat_num_var.set(str(self.repeat_num))

        self.finite_radio_btn_2.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')
        finite_subprnt.grid_columnconfigure(index = 1, weight = 1)
        self.repeat_num_sbox_2.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')

        Validate_Int(self.repeat_num_sbox_2, self.repeat_num_var, only_positive = True, lo_limit = 1, hi_limit = 9999)

        self.repeat_num_sbox_state(self.repeat_num_sbox_2)
        self.infinity_radio_btn_2.grid(column = 0, row = 5, columnspan = 1, rowspan = 1, padx = (10,20), pady = (1,1), sticky = 'we')
        finite_subprnt.grid(column = 0, row = 6, columnspan = 1, rowspan = 1, padx = (10,20), pady = (1,1), sticky = 'we')
        self.repeat_ALL_btn.grid(column = 0, row = 7, columnspan = 1, rowspan = 1, padx = (10,20), pady = (10,10), sticky = 'we')

        widget_take_focus(self.repeat_ALL_btn
                        , self.infinity_radio_btn_2
                        , self.finite_radio_btn_2
                        , self.repeat_num_sbox_2
                        , self.interval_entry_2)

    def repeat_btn_widget(self, status, button):
        if status == True:
            button['text'] = 'STOP'
            button['activebackground'] = 'red3'
            button['bg'] = 'red'
            button['activeforeground'] = 'white'
            button['fg'] = 'white'
            
        else:
            button['text'] = 'START'
            button['activebackground'] = 'forest green'
            button['bg'] = 'green3'
            button['activeforeground'] = 'white'
            button['fg'] = 'white'

        return button

    ###############################################################################################
    ### REPEAT STROBE FEATURES
    def repeat_btn_click(self, event = None):
        if self.repeat_btn['text'] == 'START':
            self.repeat_status = True

            if self.repeat_ALL_btn['state'] == 'normal':
                self.repeat_ALL_btn['state'] = 'disabled'
            elif self.repeat_ALL_btn['state'] == 'disabled':
                pass

        elif self.repeat_btn['text'] == 'STOP':
            self.repeat_status = False

            if self.repeat_ALL_btn['state'] == 'disabled':
                self.repeat_ALL_btn['state'] = 'normal'
            elif self.repeat_ALL_btn['state'] == 'normal':
                pass

        self.repeat_btn = self.repeat_btn_widget(self.repeat_status, self.repeat_btn)
        self.repeat_start_stop()

    def repeat_ALL_btn_click(self, event = None):
        if self.repeat_ALL_btn['text'] == 'START':
            self.repeat_ALL_status = True

            if self.repeat_btn['state'] == 'normal':
                self.repeat_btn['state'] = 'disabled'
            elif self.repeat_btn['state'] == 'disabled':
                pass

        elif self.repeat_ALL_btn['text'] == 'STOP':
            self.repeat_ALL_status = False

            if self.repeat_btn['state'] == 'disabled':
                self.repeat_btn['state'] = 'normal'
            elif self.repeat_btn['state'] == 'normal':
                pass

        self.repeat_ALL_btn = self.repeat_btn_widget(self.repeat_ALL_status, self.repeat_ALL_btn)
        self.repeat_ALL_start_stop()

    def repeat_func(self, event_thread):
        if self.repeat_mode_str == 'infinity':
            while not event_thread.isSet():
                if event_thread.isSet():
                    break #Safety measure to break if while loop didn't break
                try:
                    self.strobe_channel_repeat()
                    event_thread.wait(self.interval_time)
                except Exception:
                    continue
            # print('loop break(infinite): Repeat')

        elif self.repeat_mode_str == 'finite':
            for i in range(int(self.repeat_num)):
                if event_thread.isSet():
                    break
                elif not event_thread.isSet():
                    # print("i, repeat_num: ", i, self.repeat_num)
                    # print("interval: ", self.interval_time)
                    try:
                        self.strobe_channel_repeat()
                        if i == int(self.repeat_num) - 1:
                            self.repeat_btn_click()
                        event_thread.wait(self.interval_time)
                    except Exception:
                        if i == int(self.repeat_num) - 1:
                            self.repeat_btn_click()
                        continue

            # print('loop break(finite): Repeat')
        else:
            pass

    def repeat_ALL_func(self, event_thread):
        if self.repeat_mode_str == 'infinity':
            while not event_thread.isSet():
                if event_thread.isSet():
                    break #Safety measure to break if while loop didn't break
                try:
                    self.strobe_channel_repeat_ALL()
                    event_thread.wait(self.interval_time)
                except Exception:
                    continue
            # print('loop break(infite): Repeat ALL')

        elif self.repeat_mode_str == 'finite':
            for i in range(int(self.repeat_num)):
                if event_thread.isSet():
                    break
                elif not event_thread.isSet():
                    try:
                        self.strobe_channel_repeat_ALL()
                        if i == int(self.repeat_num) - 1:
                            self.repeat_ALL_btn_click()
                        event_thread.wait(self.interval_time)
                    except Exception:
                        if i == int(self.repeat_num) - 1:
                            self.repeat_ALL_btn_click()
                        continue

            # print('loop break(finite): Repeat ALL')
        else:
            pass

    def repeat_start_stop(self, event = None):
        if (self.repeat_status == True):
            self.interval_sbox_func()
            self.thread_event_repeat.clear()
            self.repeat_handle = threading.Thread(target= self.repeat_func, args = (self.thread_event_repeat,))
            self.repeat_handle.start()

            widget_disable(self.infinity_radio_btn, self.finite_radio_btn, self.interval_entry,
                self.infinity_radio_btn_2, self.finite_radio_btn_2, self.interval_entry_2)

            if self.repeat_mode_str == 'finite':
                widget_disable(self.repeat_num_sbox, self.repeat_num_sbox_2)

        else:
            self.thread_event_repeat.set()

            widget_enable(self.infinity_radio_btn, self.finite_radio_btn, self.interval_entry,
                self.infinity_radio_btn_2, self.finite_radio_btn_2, self.interval_entry_2)

            if self.repeat_mode_str == 'finite':
                widget_enable(self.repeat_num_sbox, self.repeat_num_sbox_2)

            try:
                Stop_thread(self.repeat_handle)
                # print('Thread Stopped')
            except (Exception):
                pass

    def repeat_ALL_start_stop(self, event = None):
        if (self.repeat_ALL_status == True):
            self.interval_sbox_func()
            self.thread_event_repeat_ALL.clear()
            self.repeat_ALL_handle = threading.Thread(target=self.repeat_ALL_func, args = (self.thread_event_repeat_ALL,))
            self.repeat_ALL_handle.start()

            widget_disable(self.infinity_radio_btn, self.finite_radio_btn, self.interval_entry,
                self.infinity_radio_btn_2, self.finite_radio_btn_2, self.interval_entry_2)

            if self.repeat_mode_str == 'finite':
                widget_disable(self.repeat_num_sbox, self.repeat_num_sbox_2)

            # print(repeat_ALL_handle)
        else:
            self.thread_event_repeat_ALL.set()

            widget_enable(self.infinity_radio_btn, self.finite_radio_btn, self.interval_entry,
                self.infinity_radio_btn_2, self.finite_radio_btn_2, self.interval_entry_2)

            if self.repeat_mode_str == 'finite':
                widget_enable(self.repeat_num_sbox, self.repeat_num_sbox_2)
            
            try:
                Stop_thread(self.repeat_ALL_handle)
                # print('Thread Stopped')
            except (Exception):
                pass

    def repeat_mode_set(self, event=None):
        self.repeat_mode_str = self.repeat_mode_var.get()
        self.repeat_num_sbox_state(self.repeat_num_sbox)
        self.repeat_num_sbox_state(self.repeat_num_sbox_2)

    def repeat_num_sbox_state(self, spinbox_widget):
        if self.repeat_mode_str == 'infinity':
            if spinbox_widget['state'] != 'disabled':
                spinbox_widget['state'] = 'disabled'

        elif self.repeat_mode_str == 'finite':
            if spinbox_widget['state'] != 'normal':
                spinbox_widget['state'] = 'normal'

    def repeat_num_sbox_func(self, event=None):
        if self.repeat_num_var.get() == '':
            self.repeat_num_var.set(str(1))
            pass
        else:
            self.repeat_num = int(self.repeat_num_var.get())

    def interval_sbox_func(self, event = None):
        if is_float(self.interval_var.get()) == True:
            self.interval_time = float(self.interval_var.get())
            self.interval_lb_var.set("{} seconds".format(str_float(self.interval_var.get(), 3)) )
        else:
            self.interval_lb_var.set("")

    ###############################################################################################
    ### GENERATE CONTROL PANEL
    def ch_sel_btn_state(self, active_button, inactive_button1 = None,inactive_button2 = None, inactive_button3 = None):
        orig_colour_bg = 'snow2'
        active_button['activeforeground'] = 'white'
        active_button['fg'] = 'white'
        active_button['activebackground'] = 'blue'
        active_button['bg'] = 'blue'

        if inactive_button1 != None:
            inactive_button1['activeforeground'] = 'black'
            inactive_button1['fg'] = 'black'
            inactive_button1['activebackground'] = orig_colour_bg
            inactive_button1['bg'] = orig_colour_bg

        if inactive_button2 != None:
            inactive_button2['activeforeground'] = 'black'
            inactive_button2['fg'] = 'black'
            inactive_button2['activebackground'] = orig_colour_bg
            inactive_button2['bg'] = orig_colour_bg

        if inactive_button3 != None:
            inactive_button3['activeforeground'] = 'black'
            inactive_button3['fg'] = 'black'
            inactive_button3['activebackground'] = orig_colour_bg
            inactive_button3['bg'] = orig_colour_bg

    def ch_setting_gui(self, kw):
        prnt_gui = tk.Frame(self)
        prnt_gui['bg'] = 'white'
        prnt_gui.grid_columnconfigure(index = 0, weight = 1)
        prnt_gui.grid_columnconfigure(index = 1, weight = 1)
        prnt_gui.grid_rowconfigure(index = 0, weight = 1)
        prnt_gui.grid_rowconfigure(index = 1, weight = 1)

        tag_num_list = re.findall("\\d+", kw)
        # print(tag_num_list)
        if len(tag_num_list) == 2:
            start_num = int(float(tag_num_list[0]))
            end_num   = int(float(tag_num_list[-1]))
            if end_num - start_num == 3:
                ctrl_gui_a = self.ch_ctrl_panel(prnt_gui, 'Channel {}'.format(start_num))
                ctrl_gui_b = self.ch_ctrl_panel(prnt_gui, 'Channel {}'.format(start_num + 1))
                ctrl_gui_c = self.ch_ctrl_panel(prnt_gui, 'Channel {}'.format(start_num + 2))
                ctrl_gui_d = self.ch_ctrl_panel(prnt_gui, 'Channel {}'.format(end_num))

                ctrl_gui_a.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')
                ctrl_gui_b.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (3,1), pady = (1,1), sticky = 'nwse')
                ctrl_gui_c.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (1,1), pady = (3,1), sticky = 'nwse')
                ctrl_gui_d.grid(column = 1, row = 1, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwse')

        return prnt_gui

    def ch_ctrl_panel(self, prnt, panel_name):
        def ch_strobe_info(prnt_var, child_var):
            str_var = prnt_var.get()
            if is_float(str_var) == True:
                value = np.divide( float(str_var), 100)
                child_var.set("{} ms".format(str_float(value, 2)))

        def ch_output_info(prnt_var, child_var):
            str_var = prnt_var.get()
            if is_float(str_var) == True:
                value = np.divide( float(str_var), 100)
                child_var.set("{} ms".format(str_float(value, 2)))

        def link_tk_var(prnt_var, child_var):
            prnt_var.get()
            child_var.set(prnt_var.get())

        def sbox_cmd(event, scl_var, sbox_var, id_num, param = None):
            scl_var.set(sbox_var.get())
            self.sbox_param_event(id_num = id_num, param = param)

        def sbox_focusout(event, tk_sbox, scl_var, id_num, param = None):
            if False == is_number(tk_sbox.get()):
                tk_sbox.delete(0, "end")
                tk_sbox.insert(0, scl_var.get())
                tk_sbox.xview_moveto('1')
                tk_sbox.icursor(tk.END)
            elif True == is_number(tk_sbox.get()):
                scl_var.set(tk_sbox.get())
                self.sbox_param_event(id_num = id_num, param = param)

        re_compiler = re.compile("^(Channel \\d+)")
        check = re_compiler.match(panel_name)
        panel_num = ''
        if check is not None:
            get_name = check.groups()[0]
            num_list = re.findall("\\d+", get_name)
            if len(num_list) > 0:
                panel_num = num_list[0]

        if not (panel_num in self.hmap_param):
            raise KeyError("Channel Panel name (a)does not have a number tag or (b)unmatching number tag." 
                + " The name must be 'Channel {number}' where 'number' is a numerical value from 1 to 16" 
                + "to access the hashmap containing Tkinter Var objects.")

        subprnt_gui = tk.Frame(prnt, highlightthickness = 1, highlightbackground = 'black')

        subprnt_gui.grid_columnconfigure(index = 0, weight = 1) ## This column will contain strobe mode widgets [setting gui]
        subprnt_gui.grid_columnconfigure(index = 1, weight = 10) ## This column will contain the main ctrl widgets (e.g. Intensity, Multiplier, etc.) [setting gui]

        subprnt_gui.grid_rowconfigure(index = 0, weight = 0) ## This row will contain the panel name
        subprnt_gui.grid_rowconfigure(index = 1, weight = 1) ## This row will contain the rest of the [settings gui]

        name_tk_lb = tk.Label(subprnt_gui, text = panel_name, font = 'Helvetica 14 bold'
            , justify = tk.LEFT, anchor = 'nw')
        name_tk_lb.grid(column = 0, row = 0, columnspan = 2, rowspan = 1, padx = (5,1), pady = (5,5), sticky = 'nwse')

        strobe_sett_gui = tk.Frame(subprnt_gui)
        strobe_sett_gui.grid_columnconfigure(index = 0, weight = 1)
        strobe_sett_gui.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (20,1), pady = (1,1), sticky = 'nwse')

        strobe_mode_lb = tk.Label(strobe_sett_gui, text = 'Select Mode: ', font = 'Helvetica 12 italic', width = 12
            , justify = 'left', anchor = 'w')
        strobe_mode_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,5), pady = (1,1), sticky = 'nwse')

        
        ch_mode = CustomBox(strobe_sett_gui, values = self.mode_list, width=13, state='readonly', font = 'Helvetica 11')
        ch_mode.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (1,5), pady = (5,1), sticky = 'nwse')
        ch_mode.current(0)

        ch_mode.unbind_class("TCombobox", "<MouseWheel>")

        strobe_btn = tk.Button(strobe_sett_gui, relief = tk.GROOVE, width = 10, height = 1, font = 'Helvetica 12')
        strobe_btn['text'] = 'Strobe CH{}'.format(panel_num)
        strobe_btn['command'] = partial(self.out_strobe_cmd, id_num = str(panel_num))

        strobe_btn.grid(column = 0, row = 2, columnspan = 1, rowspan = 1, padx = (1,5), pady = (100,1), sticky = 'nwse')

        #####################################################################################################################
        ch_sett_gui = tk.Frame(subprnt_gui)
        ch_sett_gui.grid_columnconfigure(index = 0, weight = 5)
        ch_sett_gui.grid_columnconfigure(index = 1, weight = 10)
        ch_sett_gui.grid_columnconfigure(index = 2, weight = 1)

        ch_sett_gui.grid(column = 1, row = 1, columnspan = 1, rowspan = 1, padx = (10,20), pady = (1,1), sticky = 'nwse')

        for i in range(0, 6):
            ch_sett_gui.grid_rowconfigure(index = i, weight = 1, min = 50)
        #####################################################################################################################
        ch_label_a  = WrappingLabel(ch_sett_gui, text = 'Current Multiplier', font = 'Helvetica 12', justify = 'right', anchor = 'ne')
        ch_label_a['width'] = len('Current')

        scl_var_a   = tk.StringVar()
        sbox_var_a  = tk.StringVar()
        scl_var_a.trace('wa', lambda *args: link_tk_var(prnt_var = scl_var_a, child_var = sbox_var_a))

        ch_scl_a = tk.Scale(ch_sett_gui, from_=1, to=10, variable=scl_var_a, orient='horizontal', showvalue=0)

        ch_sbox_a  = CustomSpinbox(ch_sett_gui, width = 4, textvariable = sbox_var_a, from_=1, to=10
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 12', input_rate = 20)

        Validate_Int(ch_sbox_a, sbox_var_a, only_positive = True, lo_limit = 1, hi_limit = 10)

        ch_sbox_a.bind('<Return>'  , partial(sbox_cmd, scl_var = scl_var_a, sbox_var = sbox_var_a, id_num = str(panel_num), param = 'multiplier'))
        ch_sbox_a.bind('<FocusOut>', partial(sbox_focusout, tk_sbox = ch_sbox_a, scl_var = scl_var_a, id_num = str(panel_num), param = 'multiplier'))
        ch_sbox_a.bind_class(ch_sbox_a.get_tag(), '<ButtonRelease-1>'
            , partial(sbox_cmd, scl_var = scl_var_a, sbox_var = sbox_var_a, id_num = str(panel_num), param = 'multiplier')
            , add = "+")

        widget_take_focus(ch_sbox_a)
        widget_take_focus(ch_scl_a)

        scl_var_a.set(1)
        ch_label_a.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwes')
        ch_scl_a.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (3,1), pady = (4,1), sticky = 'nwe')
        ch_sbox_a.grid(column = 2, row = 0, columnspan = 1, rowspan = 1, padx = (3,3), pady = (3,1), sticky = 'nwe')

        #####################################################################################################################
        ch_label_b = WrappingLabel(ch_sett_gui, text = 'Intensity', font = 'Helvetica 12', justify = 'right', anchor = 'ne')
        ch_label_b['width'] = len('Intensity')
        
        scl_var_b   = tk.StringVar()
        sbox_var_b  = tk.StringVar()
        scl_var_b.trace('wa', lambda *args: link_tk_var(prnt_var = scl_var_b, child_var = sbox_var_b))

        ch_scl_b = tk.Scale(ch_sett_gui, from_=0, to=255, variable=scl_var_b, orient='horizontal', showvalue=0)

        ch_sbox_b = CustomSpinbox(master = ch_sett_gui, width = 4, textvariable = sbox_var_b,from_=0, to=255
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 12', input_rate = 20)

        Validate_Int(ch_sbox_b, sbox_var_b, only_positive = True, lo_limit = 0, hi_limit = 255)

        ch_sbox_b.bind('<Return>'  , partial(sbox_cmd, scl_var = scl_var_b, sbox_var = sbox_var_b, id_num = str(panel_num), param = 'intensity'))
        ch_sbox_b.bind('<FocusOut>', partial(sbox_focusout, tk_sbox = ch_sbox_b, scl_var = scl_var_b, id_num = str(panel_num), param = 'intensity'))
        ch_sbox_b.bind_class(ch_sbox_b.get_tag(), '<ButtonRelease-1>'
            , partial(sbox_cmd, scl_var = scl_var_b, sbox_var = sbox_var_b, id_num = str(panel_num), param = 'intensity')
            , add = "+")

        widget_take_focus(ch_sbox_b)
        widget_take_focus(ch_scl_b)
        
        scl_var_b.set(0)
        ch_label_b.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwes')
        ch_scl_b.grid(column = 1, row = 1, columnspan = 1, rowspan = 1, padx = (3,1), pady = (4,1), sticky = 'nwe')
        ch_sbox_b.grid(column = 2, row = 1, columnspan = 1, rowspan = 1, padx = (3,3), pady = (3,1), sticky = 'nwe')

        #####################################################################################################################
        ch_label_c = WrappingLabel(ch_sett_gui, text = 'Strobe Delay (0-9999)', font = 'Helvetica 12', justify = 'right', anchor = 'ne')
        ch_label_c['width'] = len('Strobe Delay')
        
        scl_var_c   = tk.StringVar()
        sbox_var_c  = tk.StringVar()
        tk_info_c   = tk.StringVar()

        scl_var_c.trace('wa', lambda *args: link_tk_var(prnt_var = scl_var_c, child_var = sbox_var_c))
        scl_var_c.trace('wr', lambda *args: ch_strobe_info(prnt_var = scl_var_c, child_var = tk_info_c))

        ch_scl_c = tk.Scale(ch_sett_gui, from_=0, to=9999, variable=scl_var_c, orient='horizontal', showvalue=0)

        entry_c_gui = tk.Frame(ch_sett_gui)
        entry_c_gui.grid_columnconfigure(index = 0, weight = 1, min = 70)

        ch_sbox_c = CustomSpinbox(master = entry_c_gui, width = 4, textvariable = sbox_var_c, from_=0, to= 9999, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 12', input_rate = 10)

        Validate_Int(ch_sbox_c, sbox_var_c, only_positive = True, lo_limit = 0, hi_limit = 9999)

        tk_lb = tk.Label(entry_c_gui, textvariable = tk_info_c,  font = 'Helvetica 11 italic', justify = 'left', anchor = 'nw')

        ch_sbox_c.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')
        tk_lb.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')

        ch_sbox_c.bind('<Return>'  , partial(sbox_cmd, scl_var = scl_var_c, sbox_var = sbox_var_c, id_num = str(panel_num), param = 'strobe_delay'))
        ch_sbox_c.bind('<FocusOut>', partial(sbox_focusout, tk_sbox = ch_sbox_c, scl_var = scl_var_c, id_num = str(panel_num), param = 'strobe_delay'))
        ch_sbox_c.bind_class(ch_sbox_c.get_tag(), '<ButtonRelease-1>'
            , partial(sbox_cmd, scl_var = scl_var_c, sbox_var = sbox_var_c, id_num = str(panel_num), param = 'strobe_delay')
            , add = "+")

        widget_take_focus(ch_sbox_c)
        widget_take_focus(ch_scl_c)

        scl_var_c.set(0)
        ch_label_c.grid(column = 0, row = 2, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwes')
        ch_scl_c.grid(column = 1, row = 2, columnspan = 1, rowspan = 1, padx = (3,1), pady = (4,1), sticky = 'nwe')
        entry_c_gui.grid(column = 2, row = 2, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwe')

        #####################################################################################################################
        ch_label_d = WrappingLabel(ch_sett_gui, text = 'Strobe Width (0-9999)', font = 'Helvetica 12', justify = 'right', anchor = 'ne')
        ch_label_d['width'] = len('Strobe Width')
        
        scl_var_d   = tk.StringVar()
        sbox_var_d  = tk.StringVar()
        tk_info_d   = tk.StringVar()
        scl_var_d.trace('wa', lambda *args: link_tk_var(prnt_var = scl_var_d, child_var = sbox_var_d))
        scl_var_d.trace('wr', lambda *args: ch_strobe_info(prnt_var = scl_var_d, child_var = tk_info_d))
        
        ch_scl_d = tk.Scale(ch_sett_gui, from_=0, to=9999, variable=scl_var_d, orient='horizontal', showvalue=0)

        entry_d_gui = tk.Frame(ch_sett_gui)
        entry_d_gui.grid_columnconfigure(index = 0, weight = 1, min = 70)

        ch_sbox_d = CustomSpinbox(master = entry_d_gui, width = 4, textvariable = sbox_var_d, from_=0, to= 9999, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 12', input_rate = 10)
        
        Validate_Int(ch_sbox_d, sbox_var_d, only_positive = True, lo_limit = 0, hi_limit = 9999)
        
        tk_lb = tk.Label(entry_d_gui, textvariable = tk_info_d,  font = 'Helvetica 11 italic', justify = 'left', anchor = 'nw')

        ch_sbox_d.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')
        tk_lb.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')

        ch_sbox_d.bind('<Return>'  , partial(sbox_cmd, scl_var = scl_var_d, sbox_var = sbox_var_d, id_num = str(panel_num), param = 'strobe_width'))
        ch_sbox_d.bind('<FocusOut>', partial(sbox_focusout, tk_sbox = ch_sbox_d, scl_var = scl_var_d, id_num = str(panel_num), param = 'strobe_width'))
        ch_sbox_d.bind_class(ch_sbox_d.get_tag(), '<ButtonRelease-1>'
            , partial(sbox_cmd, scl_var = scl_var_d, sbox_var = sbox_var_d, id_num = str(panel_num), param = 'strobe_width')
            , add = "+")

        widget_take_focus(ch_sbox_d)
        widget_take_focus(ch_scl_d)

        scl_var_d.set(100)
        ch_label_d.grid(column = 0, row = 3, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwes')
        ch_scl_d.grid(column = 1, row = 3, columnspan = 1, rowspan = 1, padx = (3,1), pady = (4,1), sticky = 'nwe')
        entry_d_gui.grid(column = 2, row = 3, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwe')
        
        #####################################################################################################################
        ch_label_e = WrappingLabel(ch_sett_gui, text = 'Output Delay (0-9999)', font = 'Helvetica 12', justify = 'right', anchor = 'ne')
        ch_label_e['width'] = len('Output Delay')
        
        scl_var_e   = tk.StringVar()
        sbox_var_e  = tk.StringVar()
        tk_info_e   = tk.StringVar()
        scl_var_e.trace('wa', lambda *args: link_tk_var(prnt_var = scl_var_e, child_var = sbox_var_e))
        scl_var_e.trace('wr', lambda *args: ch_strobe_info(prnt_var = scl_var_e, child_var = tk_info_e))

        ch_scl_e = tk.Scale(ch_sett_gui, from_=0, to=9999, variable=scl_var_e, orient='horizontal', showvalue=0) 

        entry_e_gui = tk.Frame(ch_sett_gui)
        entry_e_gui.grid_columnconfigure(index = 0, weight = 1, min = 70)

        ch_sbox_e = CustomSpinbox(master = entry_e_gui, width = 4, textvariable = sbox_var_e, from_=0, to= 9999, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 12', input_rate = 10)
        
        Validate_Int(ch_sbox_e, sbox_var_e, only_positive = True, lo_limit = 0, hi_limit = 9999)

        tk_lb = tk.Label(entry_e_gui, textvariable = tk_info_e,  font = 'Helvetica 11 italic', justify = 'left', anchor = 'nw')

        ch_sbox_e.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')
        tk_lb.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')

        ch_sbox_e.bind('<Return>'  , partial(sbox_cmd, scl_var = scl_var_e, sbox_var = sbox_var_e, id_num = str(panel_num), param = 'output_delay'))
        ch_sbox_e.bind('<FocusOut>', partial(sbox_focusout, tk_sbox = ch_sbox_e, scl_var = scl_var_e, id_num = str(panel_num), param = 'output_delay'))
        ch_sbox_e.bind_class(ch_sbox_e.get_tag(), '<ButtonRelease-1>'
            , partial(sbox_cmd, scl_var = scl_var_e, sbox_var = sbox_var_e, id_num = str(panel_num), param = 'output_delay')
            , add = "+")

        widget_take_focus(ch_sbox_e)
        widget_take_focus(ch_scl_e)

        scl_var_e.set(0)
        ch_label_e.grid(column = 0, row = 4, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwes')
        ch_scl_e.grid(column = 1, row = 4, columnspan = 1, rowspan = 1, padx = (3,1), pady = (4,1), sticky = 'nwe')
        entry_e_gui.grid(column = 2, row = 4, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwe')
        
        #####################################################################################################################
        ch_label_f = WrappingLabel(ch_sett_gui, text = 'Output Width (0-9999)', font = 'Helvetica 12', justify = 'right', anchor = 'ne')
        ch_label_f['width'] = len('Output Delay')
        
        scl_var_f   = tk.StringVar()
        sbox_var_f  = tk.StringVar()
        tk_info_f   = tk.StringVar()
        scl_var_f.trace('wa', lambda *args: link_tk_var(prnt_var = scl_var_f, child_var = sbox_var_f))
        scl_var_f.trace('wr', lambda *args: ch_strobe_info(prnt_var = scl_var_f, child_var = tk_info_f))

        ch_scl_f = tk.Scale(ch_sett_gui, from_=0, to=9999, variable=scl_var_f, orient='horizontal', showvalue=0)

        entry_f_gui = tk.Frame(ch_sett_gui)
        entry_f_gui.grid_columnconfigure(index = 0, weight = 1, min = 70)

        ch_sbox_f = CustomSpinbox(master = entry_f_gui, width = 4, textvariable = sbox_var_f, from_=0, to= 9999, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 12', input_rate = 10)
        
        Validate_Int(ch_sbox_f, sbox_var_f, only_positive = True, lo_limit = 0, hi_limit = 9999)

        tk_lb = tk.Label(entry_f_gui, textvariable = tk_info_f,  font = 'Helvetica 11 italic', justify = 'left', anchor = 'nw')

        ch_sbox_f.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')
        tk_lb.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')

        ch_sbox_f.bind('<Return>'  , partial(sbox_cmd, scl_var = scl_var_f, sbox_var = sbox_var_f, id_num = str(panel_num), param = 'output_width'))
        ch_sbox_f.bind('<FocusOut>', partial(sbox_focusout, tk_sbox = ch_sbox_f, scl_var = scl_var_f, id_num = str(panel_num), param = 'output_width'))
        ch_sbox_f.bind_class(ch_sbox_f.get_tag(), '<ButtonRelease-1>'
            , partial(sbox_cmd, scl_var = scl_var_f, sbox_var = sbox_var_f, id_num = str(panel_num), param = 'output_width')
            , add = "+")

        widget_take_focus(ch_sbox_f)
        widget_take_focus(ch_scl_f)

        scl_var_f.set(100)
        ch_label_f.grid(column = 0, row = 5, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,10), sticky = 'nwes')
        ch_scl_f.grid(column = 1, row = 5, columnspan = 1, rowspan = 1, padx = (3,1), pady = (4,10), sticky = 'nwe')
        entry_f_gui.grid(column = 2, row = 5, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,10), sticky = 'nwe')
        

        if str(panel_num) in self.hmap_param:
            self.hmap_param[str(panel_num)]['mode']['widget']           = ch_mode
            self.hmap_param[str(panel_num)]['multiplier']['widget']     = scl_var_a
            self.hmap_param[str(panel_num)]['intensity']['widget']      = scl_var_b
            self.hmap_param[str(panel_num)]['strobe_delay']['widget']   = scl_var_c
            self.hmap_param[str(panel_num)]['strobe_width']['widget']   = scl_var_d
            self.hmap_param[str(panel_num)]['output_delay']['widget']   = scl_var_e
            self.hmap_param[str(panel_num)]['output_width']['widget']   = scl_var_f

            self.hmap_param[str(panel_num)]['mode']['value']            = self.get_mode_value(ch_mode)
            self.hmap_param[str(panel_num)]['multiplier']['value']      = int(scl_var_a.get())
            self.hmap_param[str(panel_num)]['intensity']['value']       = int(scl_var_b.get())
            self.hmap_param[str(panel_num)]['strobe_delay']['value']    = int(scl_var_c.get())
            self.hmap_param[str(panel_num)]['strobe_width']['value']    = int(scl_var_d.get())
            self.hmap_param[str(panel_num)]['output_delay']['value']    = int(scl_var_e.get())
            self.hmap_param[str(panel_num)]['output_width']['value']    = int(scl_var_f.get())
        else:
            raise KeyError("Hashmap parameters needs to reinitialized, current hashmap does not support Channel {}".format(panel_num))

        ch_mode.bind('<<ComboboxSelected>>', partial(self.out_set_mode, id_num = str(panel_num)) )
        
        ch_scl_a['command'] = partial(self.out_multiplier, id_num = str(panel_num))
        ch_scl_b['command'] = partial(self.out_intensity, id_num = str(panel_num))

        ch_scl_c['command'] = partial(self.out_strobe_delay, id_num = str(panel_num))
        ch_scl_d['command'] = partial(self.out_strobe_width, id_num = str(panel_num))

        ch_scl_e['command'] = partial(self.out_output_delay, id_num = str(panel_num))
        ch_scl_f['command'] = partial(self.out_output_width, id_num = str(panel_num))
        
        return subprnt_gui

    ###############################################################################################
    ### LIGHT CONTROL FUNCTIONS
    def set_mode_combobox(self, id_num):
        hmap = self.hmap_param
        mode_value = hmap[id_num]['mode']['value']
        if is_int(mode_value) == True:
            if int(mode_value) == 0:
                hmap[id_num]['mode']['widget'].current(0)
                return

            elif int(mode_value) == 1:
                hmap[id_num]['mode']['widget'].current(1)
                return

            elif int(mode_value) == 2:
                hmap[id_num]['mode']['widget'].current(2)
                return

        hmap[id_num]['mode']['widget'].set('')

    def get_mode_value(self, combobox):
        if combobox.get() == self.mode_list[0]:
            return 0
        elif combobox.get() == self.mode_list[1]:
            return 1
        elif combobox.get() == self.mode_list[2]:
            return 2

        return 0

    def sbox_param_event(self, id_num, param = None):
        if param == 'multiplier':
            self.out_multiplier(None, id_num)

        elif param == 'intensity':
            self.out_intensity(None, id_num)

        elif param == 'strobe_delay':
            self.out_strobe_delay(None, id_num)

        elif param == 'strobe_width':
            self.out_strobe_width(None, id_num)

        elif param == 'output_delay':
            self.out_output_delay(None, id_num)

        elif param == 'output_width':
            self.out_output_width(None, id_num)


    def out_multiplier(self, event, id_num, save = False):
        if self.__read_mode == False:
            hmap = self.hmap_param
            scl_var   = hmap[id_num]['multiplier']['widget']

            addr_id = hmap[id_num]['addr_id']
            ch_index = hmap[id_num]['ch_index']

            value = int(float(scl_var.get()))

            if type(save) == bool:
                if value == hmap[id_num]['multiplier']['value'] and save == False:
                    return

                hmap[id_num]['multiplier']['value'] = value
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.ctrl.set_multiplier(ch_index, value)

    def out_intensity(self, event, id_num, save = False):
        if self.__read_mode == False:
            hmap = self.hmap_param
            scl_var   = hmap[id_num]['intensity']['widget']

            addr_id = hmap[id_num]['addr_id']
            ch_index = hmap[id_num]['ch_index']

            value = int(float(scl_var.get()))

            if type(save) == bool:
                if value == hmap[id_num]['intensity']['value'] and save == False:
                    return
                    
                hmap[id_num]['intensity']['value'] = value
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.ctrl.set_intensity(ch_index, value)

    def out_strobe_delay(self, event, id_num, save = False):
        if self.__read_mode == False:
            hmap = self.hmap_param
            scl_var   = hmap[id_num]['strobe_delay']['widget']

            addr_id = hmap[id_num]['addr_id']
            ch_index = hmap[id_num]['ch_index']

            value = int(float(scl_var.get()))

            if type(save) == bool:
                if value == hmap[id_num]['strobe_delay']['value'] and save == False:
                    return

                hmap[id_num]['strobe_delay']['value'] = value
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.ctrl.set_strobe_delay(ch_index, value)

    def out_strobe_width(self, event, id_num, save = False):
        if self.__read_mode == False:
            hmap = self.hmap_param
            scl_var   = hmap[id_num]['strobe_width']['widget']

            addr_id = hmap[id_num]['addr_id']
            ch_index = hmap[id_num]['ch_index']

            value = int(float(scl_var.get()))

            if type(save) == bool:
                if value == hmap[id_num]['strobe_width']['value'] and save == False:
                    return

                hmap[id_num]['strobe_width']['value'] = value
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.ctrl.set_strobe_width(ch_index, value)

    def out_output_delay(self, event, id_num, save = False):
        if self.__read_mode == False:
            hmap = self.hmap_param
            scl_var   = hmap[id_num]['output_delay']['widget']

            addr_id = hmap[id_num]['addr_id']
            ch_index = hmap[id_num]['ch_index']

            value = int(float(scl_var.get()))

            if type(save) == bool:
                if value == hmap[id_num]['output_delay']['value'] and save == False:
                    return

                hmap[id_num]['output_delay']['value'] = value
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.ctrl.set_output_delay(ch_index, value)

    def out_output_width(self, event, id_num, save = False):
        if self.__read_mode == False:
            hmap = self.hmap_param
            scl_var   = hmap[id_num]['output_width']['widget']

            addr_id = hmap[id_num]['addr_id']
            ch_index = hmap[id_num]['ch_index']

            value = int(float(scl_var.get()))

            if type(save) == bool:
                if value == hmap[id_num]['output_width']['value'] and save == False:
                    return

                hmap[id_num]['output_width']['value'] = value
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.ctrl.set_output_width(ch_index, value)

    def out_set_mode(self, event, id_num, save = False):
        hmap = self.hmap_param
        addr_id = hmap[id_num]['addr_id']
        ch_index = hmap[id_num]['ch_index']

        combobox = hmap[id_num]['mode']['widget']
        value = self.get_mode_value(combobox)

        if type(save) == bool:
            if value == hmap[id_num]['mode']['value'] and save == False:
                return

            hmap[id_num]['mode']['value'] = value
            self.ctrl.select_address(self.hmap_addr[addr_id])
            self.ctrl.set_mode(ch_index, value)

    def out_strobe_cmd(self, id_num):
        hmap = self.hmap_param
        addr_id = hmap[id_num]['addr_id']
        ch_index = hmap[id_num]['ch_index']

        self.ctrl.select_address(self.hmap_addr[addr_id])
        self.ctrl.strobe(ch_index)

    def save_out_param(self):
        self.thread_save_event.clear()

        if self.ch_sel_str == '1 - 4':
            start = 1
            end = 4

        elif self.ch_sel_str == '5 - 8':
            start = 5
            end = 8

        elif self.ch_sel_str == '9 - 12':
            start = 9
            end = 12

        elif self.ch_sel_str == '13 - 16':
            start = 13
            end = 16
        else:
            self.thread_save_event.set()
            return

        for i in range(start, end + 1):
            self.out_set_mode(None, str(i), save = True)
            self.out_multiplier(None, str(i), save = True)
            self.out_intensity(None, str(i), save = True)
            self.out_strobe_delay(None, str(i), save = True)
            self.out_strobe_width(None, str(i), save = True)
            self.out_output_delay(None, str(i), save = True)
            self.out_output_width(None, str(i), save = True)

        self.ctrl.save_function()
        self.thread_save_event.set()

    ###############################################################################################

    def strobe_channel_repeat(self):
        for hmap_id, hmap_data in self.hmap_param.items():
            addr_id  = hmap_data['addr_id']
            ch_index = hmap_data['ch_index']
            mode_val = hmap_data['mode']['value']

            ch_sel_var = self.ch_sel_var_hmap[hmap_id]

            if mode_val == 1 and ch_sel_var.get() == 1:
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.ctrl.strobe(ch_index)

    def strobe_channel_repeat_ALL(self):
        for hmap_id, hmap_data in self.hmap_param.items():
            addr_id  = hmap_data['addr_id']
            ch_index = hmap_data['ch_index']
            mode_val = hmap_data['mode']['value']

            if mode_val == 1:
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.ctrl.strobe(ch_index)

    ###############################################################################################
    ### RESET LIGHT PARAMETERS
    def reset_func(self, id_num):
        hmap = self.hmap_param
        ch_index = hmap[id_num]['ch_index']

        tk_var   = hmap[id_num]['multiplier']['widget']
        value = int(float(tk_var.get()))
        hmap[id_num]['multiplier']['value'] = value
        self.ctrl.set_multiplier(ch_index, value)

        tk_var   = hmap[id_num]['intensity']['widget']
        value = int(float(tk_var.get()))
        hmap[id_num]['intensity']['value'] = value
        self.ctrl.set_intensity(ch_index, value)

        tk_var   = hmap[id_num]['strobe_delay']['widget']
        value = int(float(tk_var.get()))
        hmap[id_num]['strobe_delay']['value'] = value
        self.ctrl.set_strobe_delay(ch_index, value)

        tk_var   = hmap[id_num]['strobe_width']['widget']
        value = int(float(tk_var.get()))
        hmap[id_num]['strobe_width']['value'] = value
        self.ctrl.set_strobe_width(ch_index, value)

        tk_var   = hmap[id_num]['output_delay']['widget']
        value = int(float(tk_var.get()))
        hmap[id_num]['output_delay']['value'] = value
        self.ctrl.set_output_delay(ch_index, value)

        tk_var   = hmap[id_num]['output_width']['widget']
        value = int(float(tk_var.get()))
        hmap[id_num]['output_width']['value'] = value
        self.ctrl.set_output_width(ch_index, value)

        combobox = hmap[id_num]['mode']['widget']
        value = self.get_mode_value(combobox)
        hmap[id_num]['mode']['value'] = value
        self.ctrl.set_mode(ch_index, value)

    def reset_event(self): #Functions used in RESET ALL which switches off all the lights as well
        self.thread_reset_event.clear()
        for hmap_id, hmap_data in self.hmap_param.items():
            hmap_data['multiplier']['widget'].set(1)
            hmap_data['intensity']['widget'].set(0)
            hmap_data['strobe_delay']['widget'].set(0)
            hmap_data['strobe_width']['widget'].set(100)
            hmap_data['output_delay']['widget'].set(0)
            hmap_data['output_width']['widget'].set(100)
            hmap_data['mode']['widget'].current(0)
            
            if self.__reset_all == True:
                for i in range(0, 16):
                    self.ctrl.select_address(int(i))
                    self.reset_func(hmap_id)

            elif self.__reset_all == False:
                addr_id = hmap_data['addr_id']
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.reset_func(hmap_id)
        
        self.thread_reset_event.set()

    ###############################################################################################
    ### LOAD LIGHT PARAMETERS
    def refresh_event(self, event=None):
        self.thread_refresh_event.clear()

        for hmap_id, hmap_data in self.hmap_param.items():
            addr_id = hmap_data['addr_id']
            self.ctrl.select_address(self.hmap_addr[addr_id])
            ch_index = hmap_data['ch_index']

            hmap_data['multiplier']['value']    = self.ctrl.read_multiplier(ch_index)
            hmap_data['mode']['value']          = self.ctrl.read_mode(ch_index)
            hmap_data['intensity']['value']     = self.ctrl.read_intensity(ch_index)
            hmap_data['strobe_delay']['value']  = self.ctrl.read_strobe_delay(ch_index)
            hmap_data['strobe_width']['value']  = self.ctrl.read_strobe_width(ch_index)
            hmap_data['output_delay']['value']  = self.ctrl.read_output_delay(ch_index)
            hmap_data['output_width']['value']  = self.ctrl.read_output_width(ch_index)

            self.set_mode_combobox(hmap_id)
            hmap_data['multiplier']['widget'].set(hmap_data['multiplier']['value'])
            hmap_data['intensity']['widget'].set(hmap_data['intensity']['value'])
            hmap_data['strobe_delay']['widget'].set(hmap_data['strobe_delay']['value'])
            hmap_data['strobe_width']['widget'].set(hmap_data['strobe_width']['value'])
            hmap_data['output_delay']['widget'].set(hmap_data['output_delay']['value'])
            hmap_data['output_width']['widget'].set(hmap_data['output_width']['value'])

        self.thread_refresh_event.set()

    ###############################################################################################
    ### STOP ALL THREADS
    def stop_threads(self):
        if self.repeat_status == True:
            self.repeat_btn_click()
        if self.repeat_ALL_status == True:
            self.repeat_ALL_btn_click()
        self.thread_event_repeat.set()
        self.thread_event_repeat_ALL.set()

        try:
            Stop_thread(self.thread_refresh_handle)
        except (Exception):
            pass

        try:
            Stop_thread(self.thread_reset_handle)
        except (Exception):
            pass

        self.thread_refresh_event.set()
        self.thread_reset_event.set()
