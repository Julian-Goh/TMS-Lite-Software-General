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
### SQ SPECIAL FEATURES
"""

import os
from os import path
import sys
import re

import tkinter as tk
from tkinter import ttk

import numpy as np
import threading
import functools
from functools import partial

import inspect
import ctypes
from ctypes import *

from LC18SQ_pylib import LC18SQ_Control

from Tk_Validate.tk_validate import *
from misc_module.tk_img_module import *
from Tk_Custom_Widget.tk_custom_label import *
from Tk_Custom_Widget.tk_custom_btn import *
from Tk_Custom_Widget.tk_custom_combobox import *
from Tk_Custom_Widget.tk_custom_spinbox import *
from Tk_Custom_Widget.ScrolledCanvas import ScrolledCanvas
from Tk_Custom_Widget.tk_custom_toplvl import CustomToplvl

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

class LC18_SQ_GUI(tk.Frame):
    def __init__(self, master, scroll_class, dll_LC18
        , thread_event_repeat_ALL = None
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

        self.gui_graphic = {"infinity_icon" : None
                          , "window_icon" : None}
        for key, item in gui_graphic.items():
            if key in self.gui_graphic:
                self.gui_graphic[key] = item

        self.thread_event_repeat_ALL = thread_event_repeat_ALL #Thread event used in Threading
        self.repeat_ALL_handle = None
        # print('self.thread_event_repeat_ALL: ', self.thread_event_repeat_ALL)
        # print('self.dll_LC18: ', self.dll_LC18)
        self.ctrl = LC18SQ_Control(self.dll_LC18)
        # print(self.ctrl)

        self.__read_mode = False ### When Software is reading from device, we need to stop writing to device process.

        self.repeat_ALL_status = False
        self.repeat_mode_str = 'infinity'#'infinity' or #'finite'
        self.repeat_num = 1

        self.ch_sel_str = '1 - 4'

        self.addr_a = np.array([0, 0, 0, 0]) #board address ch 1-4 #each array values represents the switches in binary, 0 or 1. #0000

        self.hmap_addr = {}
        self.hmap_addr['a'] = binary_to_dec(self.addr_a[0], self.addr_a[1], self.addr_a[2], self.addr_a[3], reverse_str = True)

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

        self.updating_bool = None

        self.interval_lb_var    = tk.StringVar()
        self.interval_var       = tk.StringVar()
        self.repeat_mode_var    = tk.StringVar()
        self.repeat_num_var     = tk.StringVar()

        self.sq_frame_delay_event = threading.Event()
        self.sq_frame_img_list = []

        self.hmap_param = self.hmap_param_init()
        self.hmap_sq_param = self.hmap_sq_param_init()

        self.refresh_gui_init()
        self.reset_gui_init()
        self.save_gui_init()
        self.LC18_interface()
        self.SQ_panel_popout()

    def show(self, firmware_version = None):
        self.refresh_btn_click(override = True)
        self.firmware_version.set('Board Firmware:\n' + "{}".format(firmware_version))

    def hide(self):
        self.stop_threads()
        self.firmware_version.set('Board Firmware:\n' + "None")
        self.sq_panel_toplvl.close()

    def hmap_param_init(self):
        def hashmap_init(ch_index):
            hashmap = {}
            hashmap['multiplier']   = {'widget' : None, 'value' : None} ### we will insert tk.StringVar()
            hashmap['intensity']    = {'widget' : None, 'value' : None} ### we will insert tk.StringVar()
            hashmap['strobe_width'] = {'widget' : None, 'value' : None} ### we will insert tk.StringVar()
            hashmap['ch_index']     = ch_index

            return hashmap

        hmap = {}
        for i in range(1, 5):
            ch_index = i%4
            if ch_index == 0:
                ch_index = 4

            hmap['{}'.format(i)] = hashmap_init(ch_index)

        return hmap

    def hmap_sq_param_init(self):
        hmap = {}
        hmap['mode']          = {'widget' : None, 'value' : None}
        hmap['output_delay']  = {'widget' : None, 'value' : None}
        hmap['output_width']  = {'widget' : None, 'value' : None}
        hmap['frame_num']     = {'widget' : None, 'value' : None}
        hmap['frame_width']   = {'widget' : None, 'value' : None}
        
        fr_val = {}
        for i in range(0, 10):
            ### We Generate tk.IntVar() to be used with checkbutton widgets when user set the SQ frame values
            ### This will be used in:  SQ SPECIAL FEATURES      section of the code.
            tk_list = []
            for j in range(0, 4): 
                tk_list.append(tk.IntVar(value = 0))

            fr_val[str(i)] = {'widget' : tk_list, 'value': None}
        
        hmap['frame_val']     = fr_val
        
        # print(hmap)
        return hmap

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
            self.updating_bool = True
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
            self.updating_bool = False
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
                self.updating_bool = True
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
            self.updating_bool = False
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
        self.grid_rowconfigure(index = 1, weight = 0)
        self.grid_rowconfigure(index = 2, weight = 1)

        self.left_anchor_fr = tk.Frame(self, width = 137, height = 800, highlightcolor = 'white', highlightthickness = 1)
        self.left_anchor_fr['bg'] = 'DarkSlateGray2'
        self.left_anchor_fr.grid(column = 0, row = 0, columnspan = 1, rowspan = 4, padx = (1,1), pady = (1,1), sticky = 'nwse')
        
        self.left_anchor_fr.grid_columnconfigure(index = 0, weight = 1)

        self.ch_sel_btn_gen()

        self.main_control_gen()

        self.sq_setting_gen()

        self.ch_setting_gen()


        self.repeat_ALL_ctrl_gen()

        prnt_gui = self.sq_ch_setting_gui()
        prnt_gui.grid(column = 1, row = 1, columnspan = 1, rowspan = 1, padx = (150, 150), pady = (3,1), sticky = 'nwse')
        self.ch_ctrl_gui_dict = {   '1 - 4'  : self.ch_setting_gui('1 - 4')
                                    }

        self.ch_sel_btn1.invoke()

    def main_control_gen(self):
        self.main_ctrl_prnt = tk.Frame(self.left_anchor_fr, bg = 'DarkSlateGray2', highlightbackground="white", highlightthickness=1)
        self.main_ctrl_prnt['width'] =  120 + 5
        self.main_ctrl_prnt['height'] = 200
        self.main_ctrl_prnt.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,1), sticky = 'we')

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


        self.RESET_btn = WrappingButton(self.main_ctrl_prnt, width = 10, relief = tk.GROOVE, activeforeground= 'white', fg="white", activebackground = 'navy', bg = 'royal blue'
              , text='RESET', font = "Helvetica 11 bold", justify = tk.CENTER, anchor = 'c')
        self.RESET_btn['command'] = partial(self.reset_btn_click, reset_all = False)
        self.RESET_btn.grid(column = 0, row = 4, columnspan = 1, rowspan = 1, padx = (20,20), pady = (5,1), sticky = 'nwse')

        self.RESET_ALL_btn = WrappingButton(self.main_ctrl_prnt, width = 10, relief = tk.GROOVE, activeforeground= 'white', fg="white", activebackground = 'navy', bg = 'royal blue'
              , text='RESET ALL', font = "Helvetica 11 bold", justify = tk.CENTER, anchor = 'c')
        self.RESET_ALL_btn['command'] = partial(self.reset_btn_click, reset_all = True)
        self.RESET_ALL_btn.grid(column = 0, row = 5, columnspan = 1, rowspan = 1, padx = (20,20), pady = (5,10), sticky = 'nwse')

    def ch_sel_btn_gen(self):
        self.ch_sel_btn_subprnt = tk.Frame(self, highlightthickness = 0, bd = 0)
        self.ch_sel_btn_subprnt['bg'] = 'white'
        prnt = self.ch_sel_btn_subprnt
        self.ch_sel_btn1 = tk.Button(prnt, relief = tk.GROOVE, text = 'Channel 1 - 4', width = 12, font='Helvetica 11 bold')

        self.ch_sel_btn1['command'] = partial(self.ch_sel_func, '1 - 4'  , self.ch_sel_btn1)

        self.hmap_ch_btn = {}
        self.hmap_ch_btn[str(self.ch_sel_btn1)] = partial(self.ch_sel_func, '1 - 4'  , self.ch_sel_btn1)

        self.ch_sel_btn1.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,5), pady = (1,1), sticky = 'nwse')

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

    def sq_setting_gen(self):
        self.sq_sett_prnt = tk.Frame(self.left_anchor_fr, highlightbackground="white", highlightthickness = 1)
        self.sq_sett_prnt['width'] = 137
        self.sq_sett_prnt['bg'] = 'DarkSlateGray2'
        self.sq_sett_prnt.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,1), sticky = 'nwse')

        self.sq_sett_prnt.grid_columnconfigure(index = 0, weight = 1, min = 140)

        tk_lb = WrappingLabel(self.sq_sett_prnt, font='Helvetica 14 bold', bg = 'DarkSlateGray2', justify= tk.LEFT, anchor = 'nw')
        tk_lb['text'] = 'SQ Frame Settings  '
        tk_lb['width'] = len('SQ Frame ')
        tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')

        tk_btn = WrappingButton(self.sq_sett_prnt, relief = tk.GROOVE
            , font = "Helvetica 12", justify = tk.CENTER, anchor = 'c')
        tk_btn['text'] = "SQ Frame\nControl Panel"
        tk_btn['width'] = 10
        tk_btn.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (20, 20), pady = (5,10), sticky = 'we')
        tk_btn['command'] = self.SQ_panel_open


    def ch_setting_gen(self):
        self.ch_sett_prnt = tk.Frame(self.left_anchor_fr, highlightbackground="white", highlightthickness = 1)
        self.ch_sett_prnt['width'] = 137
        self.ch_sett_prnt['bg'] = 'DarkSlateGray2'
        self.ch_sett_prnt.grid(column = 0, row = 2, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,1), sticky = 'nwse')

        self.ch_sett_prnt.grid_columnconfigure(index = 0, weight = 1, min = 140)
        self.ch_sett_prnt.grid_rowconfigure(index = 1, weight = 0, min = 140)

        ch_sett_tk_lb = WrappingLabel(self.ch_sett_prnt, font='Helvetica 14 bold', bg = 'DarkSlateGray2', justify= tk.LEFT, anchor = 'nw')
        ch_sett_tk_lb['text'] = 'Channel Settings  '
        ch_sett_tk_lb['width'] = len('Channel')
        ch_sett_tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')

        self.board_addr_fr = tk.Frame(self.ch_sett_prnt, width = 140, height = 140, bg = 'DarkSlateGray2', highlightbackground="white", highlightcolor = 'white', highlightthickness=1)
        self.board_addr_fr.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,1), sticky = 'nwse')
        self.board_addr_gui()

        self.firmware_version = tk.StringVar()
        self.board_firmware = WrappingLabel(self.ch_sett_prnt, textvariable = self.firmware_version, font='Helvetica 12 bold', bg = 'DarkSlateGray2', justify= tk.LEFT, anchor = 'nw')
        self.board_firmware['width'] = len('Board Firmware')
        self.firmware_version.set('Board Firmware:\n' + "None")
        self.board_firmware.grid(column = 0, row = 2, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,5), sticky = 'we')

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


    def board_addr_click(self, event = None):
        if self.ch_sel_str == '1 - 4':
            self.addr_a[0] = self.addr_0_var.get()
            self.addr_a[1] = self.addr_1_var.get()
            self.addr_a[2] = self.addr_2_var.get()
            self.addr_a[3] = self.addr_3_var.get()
            self.hmap_addr['a'] = binary_to_dec(self.addr_a[0], self.addr_a[1], self.addr_a[2], self.addr_a[3], reverse_str = True)

    def repeat_ALL_ctrl_gen(self):
        self.repeat_ALL_prnt = tk.Frame(self.left_anchor_fr, bg = 'DarkSlateGray2', highlightbackground="white", highlightthickness=1, highlightcolor="white")
        self.repeat_ALL_prnt['width'] = 120 + 5
        self.repeat_ALL_prnt['height'] = 235

        self.repeat_ALL_prnt.grid(column = 0, row = 3, columnspan = 1, rowspan = 1, padx = (5,5), pady = (5,5), sticky = 'nwse')
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

    def repeat_ALL_btn_click(self, event = None):
        if self.repeat_ALL_btn['text'] == 'START':
            self.repeat_ALL_status = True

        elif self.repeat_ALL_btn['text'] == 'STOP':
            self.repeat_ALL_status = False

        self.repeat_ALL_btn = self.repeat_btn_widget(self.repeat_ALL_status, self.repeat_ALL_btn)
        self.repeat_ALL_start_stop()

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

    def repeat_ALL_start_stop(self, event = None):
        if (self.repeat_ALL_status == True):
            self.interval_sbox_func()
            self.thread_event_repeat_ALL.clear()
            self.repeat_ALL_handle = threading.Thread(target=self.repeat_ALL_func, args = (self.thread_event_repeat_ALL,))
            self.repeat_ALL_handle.start()

            widget_disable(self.infinity_radio_btn_2, self.finite_radio_btn_2, self.interval_entry_2)

            if self.repeat_mode_str == 'finite':
                widget_disable(self.repeat_num_sbox_2)

            # print(repeat_ALL_handle)
        else:
            self.thread_event_repeat_ALL.set()

            widget_enable(self.infinity_radio_btn_2, self.finite_radio_btn_2, self.interval_entry_2)

            if self.repeat_mode_str == 'finite':
                widget_enable(self.repeat_num_sbox_2)
            
            try:
                Stop_thread(self.repeat_ALL_handle)
                # print('Thread Stopped')
            except (Exception):
                pass

    def repeat_mode_set(self, event=None):
        self.repeat_mode_str = self.repeat_mode_var.get()
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

    def sq_ch_setting_gui(self):
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
                if float(tk_sbox.get()) != float(scl_var.get()):
                    scl_var.set(tk_sbox.get())
                    self.sbox_param_event(id_num = id_num, param = param)

        prnt_gui = tk.Frame(self, highlightthickness = 1, highlightbackground = 'black')
        prnt_gui.grid_columnconfigure(index = 0, weight = 1) ## This column will contain strobe mode widgets [setting gui]
        prnt_gui.grid_columnconfigure(index = 1, weight = 10)
        name_tk_lb = tk.Label(prnt_gui, text = "SQ Channel Settings", font = 'Helvetica 14 bold'
            , justify = tk.LEFT, anchor = 'nw')
        name_tk_lb.grid(column = 0, row = 0, columnspan = 2, rowspan = 1, padx = (5,1), pady = (5,5), sticky = 'nwse')

        strobe_sett_gui = tk.Frame(prnt_gui)
        strobe_sett_gui.grid_columnconfigure(index = 0, weight = 1)
        strobe_sett_gui.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (20,1), pady = (1,1), sticky = 'nwse')

        strobe_mode_lb = tk.Label(strobe_sett_gui, text = 'Select Mode: ', font = 'Helvetica 12 italic', width = 12
            , justify = 'left', anchor = 'w')
        strobe_mode_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,5), pady = (1,1), sticky = 'nwse')

        
        ch_mode = CustomBox(strobe_sett_gui, values = self.mode_list, width=13, state='readonly', font = 'Helvetica 11')
        ch_mode.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (1,5), pady = (5,1), sticky = 'nwse')
        ch_mode.current(0)

        ch_mode.unbind_class("TCombobox", "<MouseWheel>")

        #####################################################################################################################
        ch_sett_gui = tk.Frame(prnt_gui)
        ch_sett_gui.grid_columnconfigure(index = 0, weight = 3)
        ch_sett_gui.grid_columnconfigure(index = 1, weight = 15)
        ch_sett_gui.grid_columnconfigure(index = 2, weight = 1)

        ch_sett_gui.grid(column = 1, row = 1, columnspan = 1, rowspan = 1, padx = (10,20), pady = (1,1), sticky = 'nwse')

        for i in range(0, 2):
            ch_sett_gui.grid_rowconfigure(index = i, weight = 1, min = 90)

        #####################################################################################################################
        ch_label_e = WrappingLabel(ch_sett_gui, text = 'Output Delay (0-9999)', font = 'Helvetica 12', justify = 'right', anchor = 'ne')
        ch_label_e['width'] = len('Output Delay')
        
        scl_var_e   = tk.StringVar()
        sbox_var_e  = tk.StringVar()
        tk_info_e   = tk.StringVar()
        scl_var_e.trace('wa', lambda *args: link_tk_var(prnt_var = scl_var_e, child_var = sbox_var_e))
        scl_var_e.trace('wr', lambda *args: ch_output_info(prnt_var = scl_var_e, child_var = tk_info_e))

        ch_scl_e = tk.Scale(ch_sett_gui, from_=0, to=9999, variable = scl_var_e, orient='horizontal', showvalue=0) 

        entry_e_gui = tk.Frame(ch_sett_gui)
        entry_e_gui.grid_columnconfigure(index = 0, weight = 1, min = 70)

        ch_sbox_e = CustomSpinbox(master = entry_e_gui, width = 4, textvariable = sbox_var_e, from_=0, to= 9999, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 12', input_rate = 10)
        
        Validate_Int(ch_sbox_e, sbox_var_e, only_positive = True, lo_limit = 0, hi_limit = 9999)

        tk_lb = tk.Label(entry_e_gui, textvariable = tk_info_e,  font = 'Helvetica 11 italic', justify = 'left', anchor = 'nw')

        ch_sbox_e.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')
        tk_lb.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')

        ch_sbox_e.bind('<Return>'  , partial(sbox_cmd, scl_var = scl_var_e, sbox_var = sbox_var_e, id_num = None, param = 'output_delay'))
        ch_sbox_e.bind('<FocusOut>', partial(sbox_focusout, tk_sbox = ch_sbox_e, scl_var = scl_var_e, id_num = None, param = 'output_delay'))
        ch_sbox_e.bind_class(ch_sbox_e.get_tag(), '<ButtonRelease-1>', partial(sbox_cmd, scl_var = scl_var_e, sbox_var = sbox_var_e
            , id_num = None, param = 'output_delay')
            , add = "+")

        widget_take_focus(ch_sbox_e)
        widget_take_focus(ch_scl_e)

        scl_var_e.set(0)
        ch_label_e.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwes')
        ch_scl_e.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (3,1), pady = (4,1), sticky = 'nwe')
        entry_e_gui.grid(column = 2, row = 0, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwe')
        
        #####################################################################################################################
        ch_label_f = WrappingLabel(ch_sett_gui, text = 'Output Width (0-9999)', font = 'Helvetica 12', justify = 'right', anchor = 'ne')
        ch_label_f['width'] = len('Output Delay')
        
        scl_var_f   = tk.StringVar()
        sbox_var_f  = tk.StringVar()
        tk_info_f   = tk.StringVar()
        scl_var_f.trace('wa', lambda *args: link_tk_var(prnt_var = scl_var_f, child_var = sbox_var_f))
        scl_var_f.trace('wr', lambda *args: ch_output_info(prnt_var = scl_var_f, child_var = tk_info_f))

        ch_scl_f = tk.Scale(ch_sett_gui, from_=0, to=9999, variable=scl_var_f, orient='horizontal', showvalue=0)

        entry_f_gui = tk.Frame(ch_sett_gui)
        entry_f_gui.grid_columnconfigure(index = 0, weight = 1, min = 70)

        ch_sbox_f = CustomSpinbox(master = entry_f_gui, width = 4, textvariable = sbox_var_f, from_=0, to= 9999, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 12', input_rate = 10)
        
        Validate_Int(ch_sbox_f, sbox_var_f, only_positive = True, lo_limit = 0, hi_limit = 9999)

        tk_lb = tk.Label(entry_f_gui, textvariable = tk_info_f,  font = 'Helvetica 11 italic', justify = 'left', anchor = 'nw')

        ch_sbox_f.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')
        tk_lb.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')

        ch_sbox_f.bind('<Return>'  , partial(sbox_cmd, scl_var = scl_var_f, sbox_var = sbox_var_f, id_num = None, param = 'output_width'))
        ch_sbox_f.bind('<FocusOut>', partial(sbox_focusout, tk_sbox = ch_sbox_f, scl_var = scl_var_f, id_num = None, param = 'output_width'))
        ch_sbox_f.bind_class(ch_sbox_f.get_tag(), '<ButtonRelease-1>', partial(sbox_cmd, scl_var = scl_var_f, sbox_var = sbox_var_f
            , id_num = None, param = 'output_width')
            , add = "+")

        widget_take_focus(ch_sbox_f)
        widget_take_focus(ch_scl_f)

        scl_var_f.set(100)
        ch_label_f.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,10), sticky = 'nwes')
        ch_scl_f.grid(column = 1, row = 1, columnspan = 1, rowspan = 1, padx = (3,1), pady = (4,10), sticky = 'nwe')
        entry_f_gui.grid(column = 2, row = 1, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,10), sticky = 'nwe')

        hmap = self.hmap_sq_param
        hmap['mode']['widget']           = ch_mode
        hmap['output_delay']['widget']   = scl_var_e
        hmap['output_width']['widget']   = scl_var_f

        hmap['mode']['value']            = self.get_mode_value(ch_mode)
        hmap['output_delay']['value']    = int(scl_var_e.get())
        hmap['output_width']['value']    = int(scl_var_f.get())

        ch_scl_e['command'] = partial(self.out_output_delay)
        ch_scl_f['command'] = partial(self.out_output_width)
        ch_mode.bind('<<ComboboxSelected>>', partial(self.out_set_mode) )

        return prnt_gui

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
                + " The name must be 'Channel {number}' where 'number' is a numerical value from 1 to 4" 
                + "to access the hashmap containing Tkinter Var objects.")

        subprnt_gui = tk.Frame(prnt, highlightthickness = 1, highlightbackground = 'black')

        subprnt_gui.grid_columnconfigure(index = 0, weight = 1) ## This column will contain strobe mode widgets [setting gui]

        subprnt_gui.grid_rowconfigure(index = 0, weight = 0) ## This row will contain the panel name
        subprnt_gui.grid_rowconfigure(index = 1, weight = 1) ## This row will contain the rest of the [settings gui]

        name_tk_lb = tk.Label(subprnt_gui, text = panel_name, font = 'Helvetica 14 bold'
            , justify = tk.LEFT, anchor = 'nw')
        name_tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (5,1), pady = (5,5), sticky = 'nwse')

        #####################################################################################################################
        ch_sett_gui = tk.Frame(subprnt_gui)
        ch_sett_gui.grid_columnconfigure(index = 0, weight = 1)
        ch_sett_gui.grid_columnconfigure(index = 1, weight = 10)
        ch_sett_gui.grid_columnconfigure(index = 2, weight = 1)

        ch_sett_gui.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (10,20), pady = (1,1), sticky = 'nwse')

        for i in range(0, 3):
            ch_sett_gui.grid_rowconfigure(index = i, weight = 1, min = 50)
        #####################################################################################################################
        ch_label_a  = WrappingLabel(ch_sett_gui, text = 'Current Multiplier', font = 'Helvetica 12', justify = 'right', anchor = 'ne')
        ch_label_a['width'] = len('Current ')

        scl_var_a   = tk.StringVar()
        sbox_var_a  = tk.StringVar()
        scl_var_a.trace('wa', lambda *args: link_tk_var(prnt_var = scl_var_a, child_var = sbox_var_a))

        ch_scl_a = tk.Scale(ch_sett_gui, from_=1, to=10, variable=scl_var_a, orient='horizontal', showvalue=0)

        ch_sbox_a  = CustomSpinbox(ch_sett_gui, width = 4, textvariable = sbox_var_a, from_=1, to=10
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 12', input_rate = 20)

        Validate_Int(ch_sbox_a, sbox_var_a, only_positive = True, lo_limit = 1, hi_limit = 10)

        ch_sbox_a.bind('<Return>'  , partial(sbox_cmd, scl_var = scl_var_a, sbox_var = sbox_var_a, id_num = str(panel_num), param = 'multiplier'))
        ch_sbox_a.bind('<FocusOut>', partial(sbox_focusout, tk_sbox = ch_sbox_a, scl_var = scl_var_a, id_num = str(panel_num), param = 'multiplier'))
        ch_sbox_a.bind_class(ch_sbox_a.get_tag(), '<ButtonRelease-1>', partial(sbox_cmd, scl_var = scl_var_a, sbox_var = sbox_var_a
            , id_num = str(panel_num), param = 'multiplier')
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
        ch_sbox_b.bind_class(ch_sbox_b.get_tag(), '<ButtonRelease-1>', partial(sbox_cmd, scl_var = scl_var_b, sbox_var = sbox_var_b
            , id_num = str(panel_num), param = 'intensity')
            , add = "+")

        widget_take_focus(ch_sbox_b)
        widget_take_focus(ch_scl_b)
        
        scl_var_b.set(0)
        ch_label_b.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwes')
        ch_scl_b.grid(column = 1, row = 1, columnspan = 1, rowspan = 1, padx = (3,1), pady = (4,1), sticky = 'nwe')
        ch_sbox_b.grid(column = 2, row = 1, columnspan = 1, rowspan = 1, padx = (3,3), pady = (3,1), sticky = 'nwe')

        #####################################################################################################################
        ch_label_d = WrappingLabel(ch_sett_gui, text = 'Strobe Width (0-9999)', font = 'Helvetica 12', justify = 'right', anchor = 'ne')
        ch_label_d['width'] = len('Strobe Width ')
        
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
        ch_sbox_d.bind_class(ch_sbox_d.get_tag(), '<ButtonRelease-1>', partial(sbox_cmd, scl_var = scl_var_d, sbox_var = sbox_var_d
            , id_num = str(panel_num), param = 'strobe_width')
            , add = "+")

        widget_take_focus(ch_sbox_d)
        widget_take_focus(ch_scl_d)

        scl_var_d.set(100)
        ch_label_d.grid(column = 0, row = 2, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwes')
        ch_scl_d.grid(column = 1, row = 2, columnspan = 1, rowspan = 1, padx = (3,1), pady = (4,1), sticky = 'nwe')
        entry_d_gui.grid(column = 2, row = 2, columnspan = 1, rowspan = 1, padx = (3,1), pady = (3,1), sticky = 'nwe')

        if str(panel_num) in self.hmap_param:
            self.hmap_param[str(panel_num)]['multiplier']['widget']        = scl_var_a
            self.hmap_param[str(panel_num)]['intensity']['widget']      = scl_var_b
            self.hmap_param[str(panel_num)]['strobe_width']['widget']   = scl_var_d

            self.hmap_param[str(panel_num)]['multiplier']['value']         = int(scl_var_a.get())
            self.hmap_param[str(panel_num)]['intensity']['value']       = int(scl_var_b.get())
            self.hmap_param[str(panel_num)]['strobe_width']['value']    = int(scl_var_d.get())
        else:
            raise KeyError("Hashmap parameters needs to reinitialized, current hashmap does not support Channel {}".format(panel_num))
        
        ch_scl_a['command'] = partial(self.out_multiplier, id_num = str(panel_num))
        ch_scl_b['command'] = partial(self.out_intensity, id_num = str(panel_num))

        ch_scl_d['command'] = partial(self.out_strobe_width, id_num = str(panel_num))
        
        return subprnt_gui

    ###############################################################################################
    ### LIGHT CONTROL FUNCTIONS
    def set_mode_combobox(self):
        hmap = self.hmap_sq_param
        mode_value = hmap['mode']['value']
        if is_int(mode_value) == True:
            if int(mode_value) == 0:
                hmap['mode']['widget'].current(0)
                return

            elif int(mode_value) == 1:
                hmap['mode']['widget'].current(1)
                return

            elif int(mode_value) == 2:
                hmap['mode']['widget'].current(2)
                return

        hmap['mode']['widget'].set('')

    def get_mode_value(self, combobox):
        if combobox.get() == self.mode_list[0]:
            return 0
        elif combobox.get() == self.mode_list[1]:
            return 1
        elif combobox.get() == self.mode_list[2]:
            return 2

        return 0

    def sbox_param_event(self, id_num = None, param = None):
        if param == 'multiplier':
            self.out_multiplier(None, id_num)

        elif param == 'intensity':
            self.out_intensity(None, id_num)

        elif param == 'strobe_width':
            self.out_strobe_width(None, id_num)

        elif param == 'output_delay':
            self.out_output_delay(None)

        elif param == 'output_width':
            self.out_output_width(None)


    def out_multiplier(self, event, id_num, save = False):
        if self.__read_mode == False:
            hmap = self.hmap_param
            scl_var   = hmap[id_num]['multiplier']['widget']

            addr_id = 'a'
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

            addr_id = 'a'
            ch_index = hmap[id_num]['ch_index']

            value = int(float(scl_var.get()))

            if type(save) == bool:
                if value == hmap[id_num]['intensity']['value'] and save == False:
                    return

                hmap[id_num]['intensity']['value'] = value
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.ctrl.set_intensity(ch_index, value)

    def out_strobe_width(self, event, id_num, save = False):
        if self.__read_mode == False:
            hmap = self.hmap_param
            scl_var   = hmap[id_num]['strobe_width']['widget']

            addr_id = 'a'
            ch_index = hmap[id_num]['ch_index']

            value = int(float(scl_var.get()))

            if type(save) == bool:
                if value == hmap[id_num]['strobe_width']['value'] and save == False:
                    return

                hmap[id_num]['strobe_width']['value'] = value
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.ctrl.set_strobe_width(ch_index, value)

    def out_output_delay(self, event, save = False):
        if self.__read_mode == False:
            hmap = self.hmap_sq_param
            scl_var   = hmap['output_delay']['widget']

            addr_id = 'a'

            value = int(float(scl_var.get()))

            if type(save) == bool:
                if value == hmap['output_delay']['value'] and save == False:
                    return

                hmap['output_delay']['value'] = value
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.ctrl.set_output_delay(value)

    def out_output_width(self, event, save = False):
        if self.__read_mode == False:
            hmap = self.hmap_sq_param
            scl_var   = hmap['output_width']['widget']

            addr_id = 'a'

            value = int(float(scl_var.get()))

            if type(save) == bool:
                if value == hmap['output_width']['value'] and save == False:
                    return

                hmap['output_width']['value'] = value
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.ctrl.set_output_width(value)


    def out_set_mode(self, event, save = False):
        hmap = self.hmap_sq_param

        combobox = hmap['mode']['widget']

        addr_id = 'a'
        
        value = self.get_mode_value(combobox)

        if type(save) == bool:
            if value == hmap['mode']['value'] and save == False:
                return

            hmap['mode']['value'] = value
            self.ctrl.select_address(self.hmap_addr[addr_id])
            self.ctrl.set_mode(value)
            self.SQ_trigger_state()

    def save_out_param(self):
        self.thread_save_event.clear()
        start = 1
        end = 4
        self.out_set_mode(None, save = True)
        self.out_output_delay(None, save = True)
        self.out_output_width(None, save = True)

        for i in range(start, end + 1):
            self.out_multiplier(None, str(i), save = True)
            self.out_intensity(None, str(i), save = True)
            self.out_strobe_width(None, str(i), save = True)

        self.SQ_set_frnum(event = None)
        self.SQ_set_width(event = None)
        self.SQ_set_frame()

        self.ctrl.save_function()
        self.thread_save_event.set()

    ###############################################################################################
    def strobe_channel_repeat_ALL(self):
        hmap = self.hmap_sq_param
        mode_val = hmap['mode']['value']
        if mode_val == 1:
            addr_id = 'a'
            self.ctrl.select_address(self.hmap_addr[addr_id])
            self.ctrl.strobe()

    ###############################################################################################
    ### RESET LIGHT PARAMETERS
    def reset_func(self, id_num):
        ### self.hmap_param reset
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

        tk_var   = hmap[id_num]['strobe_width']['widget']
        value = int(float(tk_var.get()))
        hmap[id_num]['strobe_width']['value'] = value
        self.ctrl.set_strobe_width(ch_index, value)

        ############################################################
        ### self.hmap_sq_param reset
        hmap = self.hmap_sq_param
        tk_var   = hmap['output_delay']['widget']
        value = int(float(tk_var.get()))
        hmap['output_delay']['value'] = value
        self.ctrl.set_output_delay(value)

        tk_var   = hmap['output_width']['widget']
        value = int(float(tk_var.get()))
        hmap['output_width']['value'] = value
        self.ctrl.set_output_width(value)

        combobox = hmap['mode']['widget']
        value = self.get_mode_value(combobox)
        hmap['mode']['value'] = value
        self.ctrl.set_mode(value)

    def reset_event(self): #Functions used in RESET ALL which switches off all the lights as well
        self.thread_reset_event.clear()

        self.hmap_sq_param['mode']['widget'].current(0)
        self.hmap_sq_param['output_delay']['widget'].set(0)
        self.hmap_sq_param['output_width']['widget'].set(100)

        for hmap_id, hmap_data in self.hmap_param.items():
            hmap_data['multiplier']['widget'].set(1)
            hmap_data['intensity']['widget'].set(0)
            hmap_data['strobe_width']['widget'].set(100)
            
            if self.__reset_all == True:
                for i in range(0, 16):
                    self.ctrl.select_address(int(i))
                    self.reset_func(hmap_id)

            elif self.__reset_all == False:
                addr_id = 'a'
                self.ctrl.select_address(self.hmap_addr[addr_id])
                self.reset_func(hmap_id)
        
        self.hmap_sq_param['frame_num']['widget'].current(0)
        self.SQ_set_frnum(event = None)

        self.hmap_sq_param['frame_width']['widget'].set(1000)
        self.SQ_set_width(event = None)

        for id_num, fr_val_hmap in self.hmap_sq_param['frame_val'].items():
            for intvar in fr_val_hmap['widget']:
                intvar.set(0)
            self.SQ_checkbox_click(id_num)

        self.SQ_checkbox_hide()
        self.SQ_trigger_state()

        self.thread_reset_event.set()

    ###############################################################################################
    ### LOAD LIGHT PARAMETERS
    def refresh_event(self, event=None):
        self.thread_refresh_event.clear()

        addr_id = 'a'
        self.ctrl.select_address(self.hmap_addr[addr_id])
        self.hmap_sq_param['mode']['value'] = self.ctrl.read_mode()
        self.hmap_sq_param['output_delay']['value'] = self.ctrl.read_output_delay()
        self.hmap_sq_param['output_width']['value'] = self.ctrl.read_output_width()

        self.set_mode_combobox()
        self.hmap_sq_param['output_delay']['widget'].set(self.hmap_sq_param['output_delay']['value'])
        self.hmap_sq_param['output_width']['widget'].set(self.hmap_sq_param['output_width']['value'])

        for hmap_id, hmap_data in self.hmap_param.items():
            ch_index = hmap_data['ch_index']
            hmap_data['multiplier']['value']   = self.ctrl.read_multiplier(ch_index)
            hmap_data['intensity']['value']    = self.ctrl.read_intensity(ch_index)
            hmap_data['strobe_width']['value'] = self.ctrl.read_strobe_width(ch_index)

            hmap_data['multiplier']['widget'].set(hmap_data['multiplier']['value'])
            hmap_data['intensity']['widget'].set(hmap_data['intensity']['value'])
            hmap_data['strobe_width']['widget'].set(hmap_data['strobe_width']['value'])
        
        self.hmap_sq_param['frame_num']['value'] = self.ctrl.read_frame_num()
        self.hmap_sq_param['frame_width']['value'] = self.ctrl.read_frame_width()

        self.SQ_frnum_refresh()
        self.SQ_width_refresh()

        fr_val = self.ctrl.SQ_read_frame()
        # print(fr_val)
        if type(fr_val) == dict:
            for id_num, val in fr_val.items():
                self.SQ_checkbox_refresh(id_num, val)

        self.SQ_checkbox_hide()
        self.SQ_trigger_state()

        self.thread_refresh_event.set()

    ###############################################################################################
    ### STOP ALL THREADS
    def stop_threads(self):
        if self.repeat_ALL_status == True:
            self.repeat_ALL_btn_click()

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

    ###############################################################################################
    ### SQ SPECIAL FEATURES
    def SQ_panel_popout(self):
        self.sq_panel_toplvl = CustomToplvl(self.master, toplvl_title = 'SQ Frame Settings', icon_img = self.gui_graphic['window_icon'], topmost_bool = True)
        self.sq_panel_toplvl['width'] = 750
        self.sq_panel_toplvl.resizable(False, False)
        self.SQ_panel_gen(self.sq_panel_toplvl)

    def SQ_panel_open(self):
        if False == self.sq_panel_toplvl.check_open():
            toplvl_W = self.sq_panel_toplvl['width']
            toplvl_H = self.sq_panel_toplvl['height']
            screen_width = self.sq_panel_toplvl.winfo_screenwidth()
            screen_height = self.sq_panel_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (toplvl_W/2))
            y_coordinate = int((screen_height/2) - (toplvl_H/2))
            self.sq_panel_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
            self.sq_panel_toplvl.open()

        else:
            self.sq_panel_toplvl.show()

    def SQ_panel_gen(self, prnt):
        ### top_anchor to hold the SQ FRAME Parameters Widgets and Buttons.
        prnt.grid_columnconfigure(index = 0, weight = 1)

        main_lb = tk.Label(prnt, text = 'Frame', font='Helvetica 12 bold', justify = tk.RIGHT, anchor = 'nw')
        main_lb.grid(column = 0, row = 0, columnspan = 2, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'we')

        top_anchor = tk.Frame(prnt, width = 725, height = 55)#, bg = 'green')
        top_anchor.grid(column = 0, row = 1, columnspan = 2, rowspan = 1, padx = (1,1), pady = (10,1), sticky = 'we')

        ##################################################################################################################
        ### top_anchor widgets creation
        tk_lb = tk.Label(top_anchor, text = 'No. of Frame:', font='Helvetica 11', justify = tk.RIGHT, anchor = 'nw')
        tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (2,1), pady = (1,1), sticky = 'nwe')

        self.sq_fr_num_list = ['1','2','3','4','5','6','7','8','9','10']
        self.sq_fr_cbox = CustomBox(top_anchor, values = self.sq_fr_num_list, width = 3
            , state = 'readonly', font = 'Helvetica 11')
        self.sq_fr_cbox.current(0)
        self.sq_fr_cbox.bind('<<ComboboxSelected>>', partial(self.SQ_set_frnum) )

        self.sq_fr_cbox.grid(column = 1, row = 0, columnspan = 1, rowspan = 1, padx = (5,1), pady = (1,1), sticky = 'nwe')

        tk_lb = tk.Label(top_anchor, text = 'Frame Width:\n(0-9999)', font = 'Helvetica 11'
            , justify = tk.RIGHT, anchor = 'nw')
        tk_lb.grid(column = 2, row = 0, columnspan = 1, rowspan = 1, padx = (15,1), pady = (1,1), sticky = 'nwe')

        self.sq_fr_width_var = tk.StringVar()
        self.sq_fr_width_lb_var = tk.StringVar()

        lb_sbox_gui = tk.Frame(top_anchor)
        lb_sbox_gui.grid(column = 3, row = 0, columnspan = 1, rowspan = 1, padx = (5,1), pady = (1,1), sticky = 'nwe')

        lb_sbox_gui.grid_columnconfigure(index = 0, weight = 0, min = 70)
        fr_width_sbox = CustomSpinbox(master = lb_sbox_gui, width = 4, from_=0, to= 9999, textvariable = self.sq_fr_width_var
                                     , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11', input_rate = 10)

        Validate_Int(fr_width_sbox, self.sq_fr_width_var, only_positive = True, lo_limit = 0, hi_limit = 9999)

        fr_width_sbox.bind("<Return>", self.SQ_set_width)
        fr_width_sbox.bind("<FocusOut>", self.SQ_set_width)
        fr_width_sbox.bind_class(fr_width_sbox.get_tag(), '<ButtonRelease-1>', self.SQ_set_width)

        fr_width_sbox.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')

        tk_lb = tk.Label(lb_sbox_gui, textvariable = self.sq_fr_width_lb_var, font = 'Helvetica 11 italic'
            , justify = tk.LEFT, anchor = 'nw')
        tk_lb.grid(column = 0, row = 1, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwse')

        self.sq_fr_width_var.set(1000)
        val = float(self.sq_fr_width_var.get()) / 100
        self.sq_fr_width_lb_var.set("{} ms".format(str_float(val, 2))  )

        setfr_btn = tk.Button(top_anchor,relief = tk.GROOVE, width = 8,text = 'Set Frame', font = 'Helvetica 11')
        widget_take_focus(setfr_btn)
        setfr_btn['command'] = self.SQ_set_frame
        setfr_btn.grid(column = 4, row = 0, columnspan = 1, rowspan = 1, padx = (15,1), pady = (1,1), sticky = 'nwe')

        strobe_btn = tk.Button(top_anchor,relief = tk.GROOVE, width = 10, text = 'Strobe Frame', font='Helvetica 11')
        widget_take_focus(strobe_btn)
        strobe_btn['command'] = self.SQ_strobe
        strobe_btn.grid(column = 5, row = 0, columnspan = 1, rowspan = 1, padx = (10,1), pady = (1,1), sticky = 'nwe')

        self.sq_trigg_btn = tk.Button(top_anchor,relief = tk.GROOVE, font='Helvetica 11 bold')
        widget_take_focus(self.sq_trigg_btn)
        self.SQ_trigger_state()
        self.sq_trigg_btn.grid(column = 6, row = 0, columnspan = 1, rowspan = 1, padx = (10,2), pady = (1,1), sticky = 'nwe')

        #############################################################################################################################
        ### chbox_prnt to hold the SQ FRAME checkboxes and CH1, CH2, CH3, and CH4 labels
        chbox_prnt = tk.Frame(prnt)
        prnt.grid_columnconfigure(index = 2, weight = 1)
        chbox_prnt.grid(column = 0, row = 2, columnspan = 1, rowspan = 1, padx = (1,1), pady = (10,10), sticky = 'we')

        ### Generate the CH1, CH2, CH3, & CH4 labels.
        for i in range(0, 5):
            chbox_prnt.grid_rowconfigure(index = i, weight = 1, uniform = 'sq_chbox')
            if i == 0:
                tk_lb = tk.Label(chbox_prnt) ### Dummy Label to fill the 1st row
                tk_lb.grid(column = 0, row = i, columnspan = 1, rowspan = 1, padx = (5,1), pady = (1,9), sticky = 'nwes')
            else:
                tk_lb = tk.Label(chbox_prnt, text = 'CH{}'.format(i), font='Helvetica 11', justify = tk.RIGHT, anchor = 'c')
                tk_lb.grid(column = 0, row = i, columnspan = 1, rowspan = 1, padx = (5,1), pady = (1,10), sticky = 'nwes')
            del i

        ### Generate the Checkboxes Sub-parent and Widgets.
        hmap = self.hmap_sq_param
        self.chbox_gui_list = []
        j = 1
        for id_num in hmap['frame_val'].keys():
            chbox_prnt.grid_columnconfigure(index = j, weight = 1, uniform = 'sq_chbox')
            subprnt = self.SQ_checkbox_gen(chbox_prnt, id_num = id_num)
            subprnt.grid(column = j, row = 0, columnspan = 1, rowspan = 5, padx = (1,1), pady = (1,1), sticky = 'nwes')
            self.chbox_gui_list.append(subprnt)
            j += 1
        
        ### Create a Frame widget to hide the subprnt from self.SQ_checkbox_gen when user select the corresponding frame number
        hide_gui_fr = tk.Frame(chbox_prnt)
        hide_gui_fr.grid(column = 1, row = 0, columnspan = j, rowspan = 5, padx = (1,1), pady = (1,1), sticky = 'nwes')
        hide_gui_fr.lower()
        del j


        ### Insert Widgets into the respective keys in self.hmap_sq_param.
        hmap = self.hmap_sq_param
        hmap['frame_num']['widget']   = self.sq_fr_cbox
        hmap['frame_width']['widget'] = self.sq_fr_width_var

        hmap['frame_num']['value']    = int(self.sq_fr_cbox.get())
        hmap['frame_width']['value']  = int(self.sq_fr_width_var.get())

        self.sq_panel_toplvl.update_idletasks()
        self.sq_panel_toplvl['height'] = self.sq_panel_toplvl.winfo_reqheight()

    def SQ_checkbox_gen(self, prnt, id_num):
        subprnt = tk.Frame(prnt, bg = "gray76", highlightbackground="black", highlightthickness=1)
        subprnt.grid_columnconfigure(index = 0, weight = 1, uniform = 'sq_chbox')
        ### Generate the Label for each checkboxes sub-parent: eg. F0, F1, F2, etc.
        subprnt.grid_rowconfigure(index = 0, weight = 1, uniform = 'sq_chbox')
        tk_lb = tk.Label(subprnt, font = 'Helvetica 11', justify = tk.CENTER, anchor = 'c', bg = "gray76")
        tk_lb['text'] = "F{}".format(id_num)
        tk_lb.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, padx = (1,1), pady = (1,1), sticky = 'nwes')

        ### Generate the checkboxes widget based on self.hmap_sq_param
        hmap = self.hmap_sq_param
        tk_list = hmap['frame_val'][id_num]['widget']
        i = 1
        max_i = len(tk_list)
        for intvar in tk_list:
            subprnt.grid_rowconfigure(index = i, weight = 1, uniform = 'sq_chbox')
            chbox = tk.Checkbutton(subprnt, bg = "gray76", activebackground = "gray76", variable= intvar)
            widget_take_focus(chbox)
            chbox['command'] = partial(self.SQ_checkbox_click, id_num  = id_num)

            chbox.grid(column = 0, row = i, columnspan = 1, rowspan = 1, padx = (7,1), pady = (1,10), sticky = 'nwes')

            i += 1

        del i
        
        return subprnt

    def SQ_checkbox_click(self, id_num):
        addr_id = 'a'
        self.ctrl.select_address(self.hmap_addr[addr_id])

        hmap = self.hmap_sq_param
        bin_list = []
        for intvar in hmap['frame_val'][id_num]['widget']:
            bin_list.append(intvar.get())

        bin_tuple = tuple(bin_list)

        del bin_list

        hmap['frame_val'][id_num]['value'] = binary_to_dec(*bin_tuple, reverse_str = True)
        # print(int(id_num), hmap['frame_val'][id_num]['value'])

        self.ctrl.SQ_SetFrame(int(id_num), hmap['frame_val'][id_num]['value'])

    def SQ_checkbox_refresh(self, id_num, fr_val):
        hmap  = self.hmap_sq_param
        hmap['frame_val'][id_num]['value'] = fr_val
        ### We set the length of the arr_size to match the list length from hmap['frame_val'][id_num]['widget']
        arr_size = len(hmap['frame_val'][id_num]['widget'])
        bin_arr = np.zeros((arr_size, ),  dtype=np.uint8)
        bin_arr = dec_to_binary_arr(fr_val, bin_arr, reverse_arr = True)
        for i in range(0, arr_size):
            hmap['frame_val'][id_num]['widget'][i].set(bin_arr[i])

        del bin_arr
        # print(hmap['frame_val'][id_num])
    
    def SQ_checkbox_hide(self):
        hmap = self.hmap_sq_param
        val  = hmap['frame_num']['value']
        if is_int(val) == True:
            for i, chbox_gui in enumerate(self.chbox_gui_list):
                if i <= val - 1:
                    chbox_gui.lift()
                else:
                    chbox_gui.lower()

    def SQ_set_frnum(self, event):
        hmap = self.hmap_sq_param
        wid  = hmap['frame_num']['widget']
        val  = int(wid.get())

        addr_id = 'a'
        self.ctrl.select_address(self.hmap_addr[addr_id])
        self.ctrl.SQ_SetNoOfFrame(val)
        hmap['frame_num']['value'] = val
        self.SQ_checkbox_hide()

    def SQ_frnum_refresh(self):
        hmap = self.hmap_sq_param
        wid = hmap['frame_num']['widget']
        val = hmap['frame_num']['value']
        index = self.sq_fr_num_list.index(str(val))
        wid.current(index)

    def SQ_set_width(self, event):
        hmap = self.hmap_sq_param
        tk_var   = hmap['frame_width']['widget']
        curr_val = int(hmap['frame_width']['value'])

        if False == is_number(tk_var.get()):
            tk_var.set(curr_val)
        elif True == is_number(tk_var.get()):
            addr_id = 'a'
            self.ctrl.select_address(self.hmap_addr[addr_id])

            hmap['frame_width']['value'] = int(tk_var.get())
            self.ctrl.SQ_SetFrameWidth(hmap['frame_width']['value'])

        val_ms = float(hmap['frame_width']['value']) / 100
        self.sq_fr_width_lb_var.set("{} ms".format(str_float(val_ms, 2)))

    def SQ_width_refresh(self):
        hmap = self.hmap_sq_param
        hmap['frame_width']['widget'].set(hmap['frame_width']['value'])
        val_ms = float(hmap['frame_width']['value']) / 100
        self.sq_fr_width_lb_var.set("{} ms".format(str_float(val_ms, 2)))


    def SQ_set_frame(self): ### Set Frame Button Event
        addr_id = 'a'
        self.ctrl.select_address(self.hmap_addr[addr_id])

        hmap = self.hmap_sq_param
        for id_num, fr_data in hmap['frame_val'].items():
            # print(id_num, fr_data['value'])
            self.ctrl.SQ_SetFrame(int(id_num), fr_data['value'])

    def SQ_trigger_init(self, btn):
        btn['text'] = 'START TRIGGER'
        btn['activebackground'] = 'forest green'
        btn['bg'] = 'green3'
        btn['activeforeground'] = 'white'
        btn['fg'] = 'white'
        btn['command'] = partial(self.SQ_trigger_click, btn = btn)
        return btn

    def SQ_trigger_disable(self, btn):
        btn['text'] = 'TRIGGER DISABLED'
        btn['activebackground'] = 'gold2'
        btn['bg'] = 'gold'
        btn['activeforeground'] = 'black'
        btn['fg'] = 'black'
        btn['command'] = lambda : None
        return btn

    def SQ_trigger_click(self, btn):
        if btn['text'] == 'START TRIGGER':
            btn['text'] = 'STOP TRIGGER'
            btn['activebackground'] = 'red3'
            btn['bg'] = 'red'
            btn['activeforeground'] = 'white'
            btn['fg'] = 'white'
            self.SQ_trigger_start()
            
        elif btn['text'] == 'STOP TRIGGER':
            btn['text'] = 'START TRIGGER'
            btn['activebackground'] = 'forest green'
            btn['bg'] = 'green3'
            btn['activeforeground'] = 'white'
            btn['fg'] = 'white'
            self.SQ_trigger_stop()

    def SQ_trigger_state(self):
        hmap = self.hmap_sq_param
        val = hmap['mode']['value']

        if is_int(val) == True:
            if val == 2:
                self.SQ_trigger_init(btn = self.sq_trigg_btn)
                return

        self.SQ_trigger_disable(btn = self.sq_trigg_btn)

    def SQ_trigger_start(self):
        self.ctrl.SQ_Trigger(1)

    def SQ_trigger_stop(self):
        ### self.ctrl.SQ_Trigger(0)# This is not working for SQ System Setup with External Motor, so...
        self.ctrl.set_mode(1)
        self.ctrl.set_mode(2)

    def SQ_strobe(self): ### SQ Strobe button Event
        addr_id = 'a'
        self.ctrl.select_address(self.hmap_addr[addr_id])
        self.ctrl.strobe()
