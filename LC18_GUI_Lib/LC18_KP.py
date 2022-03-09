#NUMBER CATEGORY OF THIS CODE:
#1. MAIN INTERFACE
#2. 
import os
from os import path
import sys

import tkinter as tk
from tkinter import ttk

import numpy as np
import threading

import inspect
import ctypes
from ctypes import *

from intvalidate import int_validate

from ctrl_LC18_lib import LC18_Control

def validate_int_entry(d, P, S, only_positive = 'False'):
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
    #print(only_positive, type(only_positive))
    if only_positive == 'False':
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

def validate_float_entry(d, P, S):
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
    if d == '1':
        try:
            float(P)
            if float(P) >= 0 and S != '-':
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

def widget_bind_focus(widget):#On Left Mouse Click the Widget is Focused
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

def binary_to_dec_v2(*bins, reverse_str = False): #convert bin to unsigned number
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

def dec_to_binary_arr_v2(dec_num, bin_arr = None, reverse_arr = False): #convert unsigned number to bin
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

class LC18_KP_GUI(tk.Frame):
    def __init__(self, master, dll_LC18, light_conn_status, firmware_model_sel, firmware_version_str, infinity_icon
        , thread_event_repeat = None, thread_event_repeat_ALL = None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        #INITIALIZE GUI INTERFACE MAIN PANEL(S) to hold the widgets
        self.master = master
        self.dll_LC18 = dll_LC18
        self.light_conn_status =  light_conn_status

        self.firmware_model_sel = firmware_model_sel
        #print('self.firmware_model_sel: ', self.firmware_model_sel)
        self.firmware_version_str = firmware_version_str
        self.infinity_icon = infinity_icon

        self.thread_event_repeat = thread_event_repeat #Thread event used in Threading
        self.thread_event_repeat_ALL = thread_event_repeat_ALL #Thread event used in Threading
        self.repeat_handle = self.repeat_ALL_handle = None

        #print('self.thread_event_repeat: ', self.thread_event_repeat)
        #print('self.thread_event_repeat_ALL: ', self.thread_event_repeat_ALL)
        #print('self.dll_LC18: ', self.dll_LC18)
        self.ctrl = LC18_Control(self.dll_LC18)

        self.sq_strobe_btn_click = False

        self.repeat_status = False
        self.repeat_ALL_status = False
        self.repeat_mode_str = 'infinity'#'infinity' or #'finite'
        self.repeat_number = 1

        self.machine_param_type = 'None'
        self.ch_sel_str = '1 - 4'

        arr_size = 8 #Array size for each Channels
        #arr_index: 0 = Current Mulitplier, 1 = Intensity(0-255), 2 = Strobe Delay(0-9999), 3 = Strobe Width(0-9999), 4 = Output Delay(0-9999), 5 = Output Width(0-9999)
        #arr_index: 6 = Channel Mode(Const, Strobe, Trigger), 7 = Channel Board Address
        self.channel_1_save = np.zeros ((arr_size),dtype=np.uint16)
        self.channel_2_save = np.zeros ((arr_size),dtype=np.uint16)
        self.channel_3_save = np.zeros ((arr_size),dtype=np.uint16)
        self.channel_4_save = np.zeros ((arr_size),dtype=np.uint16)

        self.channel_1_save[3] = self.channel_2_save[3] = self.channel_3_save[3] = self.channel_4_save[3] = 100     #Strobe Width Default
        self.channel_1_save[5] = self.channel_2_save[5] = self.channel_3_save[5] = self.channel_4_save[5] = 100     #Output Width Default
        self.channel_1_save[7] = self.channel_2_save[7] = self.channel_3_save[7] = self.channel_4_save[7] = 0       #board address index in integer

        self.strobe_ch_arr = np.zeros((16),dtype=np.uint8)

        self.addr_index_a = 0
        self.addr_a = np.array([0, 0, 0, 0]) #board address ch 1-4 #each array values represents the switches in binary, 0 or 1. #0000

        self.interval_arr = np.array([0.5])
        self.interval_parameter = self.interval_arr[0]

        self.loading_iteration = 0
        self.reset_progress_iteration = 0

        self.thread_refresh_event = threading.Event()

        self.thread_reset_event = threading.Event()

        self.GUI_refresh_handle = None
        
        self.GUI_reset_handle = None

        self.updating_bool = None

        self.load_btn_click()
    
    def load_btn_click(self):
        self.updating_bool = True

        self.loading_frame = tk.Frame(self, bg = 'white') #width = 1500 - 330, height = 900
        self.loading_frame.place(relx=0, rely =0, relheight = 1, relwidth = 1, anchor = 'nw')

        self.loading_label = tk.Label(self.loading_frame, bg = 'white', font = 'Helvetica 20 bold')
        self.loading_label['text']= 'Loading...'
        #self.loading_label.place(relx=0.45, rely=0.3, anchor = 'center')
        self.loading_label.place(relx=0.35, rely=0.25, anchor = 'center')

        self.thread_refresh_func()
        self.refresh_GUI_update()
        

    def thread_refresh_func(self):
        self.thread_refresh_handle = threading.Thread(target=self.load_parameter)
        self.thread_refresh_handle.start()

    def refresh_GUI_update(self):
        #print('Updating...')
        self.GUI_refresh_handle = self.after(150, self.refresh_GUI_update)

        self.loading_iteration = self.loading_iteration + 1

        if self.loading_iteration <= 6:
            self.loading_label['text'] = 'Loading'
        elif 6 < self.loading_iteration <= 12:
            self.loading_label['text'] = 'Loading.'
        elif 12 < self.loading_iteration <= 18:
            self.loading_label['text'] = 'Loading..'
        elif 18 < self.loading_iteration <= 24:
            self.loading_label['text'] = 'Loading...'
        elif self.loading_iteration > 24:
            self.loading_iteration = 0

        if self.thread_refresh_event.isSet():
            self.after_cancel(self.GUI_refresh_handle)
            self.loading_frame.place_forget()
            self.LC18_interface()
            self.thread_refresh_event.clear()
            print('Update Complete!')
            self.updating_bool = False
            #print(self.thread_refresh_handle)
        #print(self.GUI_refresh_handle)
    

    def reset_btn_click(self):
        self.updating_bool = True
        try:
            self.sq_frame_toplvl.destroy()
        except Exception:
            pass
        self.reset_progress_frame = tk.Frame(self, width = 1500 - 330, height = 900, bg = 'white')
        self.reset_progress_frame.place(x=0, y =0, anchor = 'nw')

        self.reset_progress_label = tk.Label(self.reset_progress_frame, bg = 'white', font = 'Helvetica 20 bold')
        self.reset_progress_label['text']= 'Resetting...'
        #self.reset_progress_label.place(relx=0.45, rely=0.3, anchor = 'center')
        self.reset_progress_label.place(relx=0.35, rely=0.25, anchor = 'center')

        self.thread_reset_func()
        self.reset_GUI_update()

    def thread_reset_func(self):
        self.thread_reset_handle = threading.Thread(target=self.reset_all)
        self.thread_reset_handle.start()

    def reset_GUI_update(self):
        #print('Resetting...')
        self.GUI_reset_handle = self.after(150, self.reset_GUI_update)

        self.reset_progress_iteration = self.reset_progress_iteration + 1

        if self.reset_progress_iteration <= 6:
            self.reset_progress_label['text'] = 'Resetting'

        elif 6 < self.reset_progress_iteration <= 12:
            self.reset_progress_label['text'] = 'Resetting.'

        elif 12 < self.reset_progress_iteration <= 18:
            self.reset_progress_label['text'] = 'Resetting..'

        elif 18 < self.reset_progress_iteration <= 24:
            self.reset_progress_label['text'] = 'Resetting...'

        elif self.reset_progress_iteration > 24:
            self.reset_progress_iteration = 0

        if self.thread_reset_event.isSet():
            self.after_cancel(self.GUI_reset_handle)
            self.reset_progress_frame.place_forget()
            #self.LC18_interface()
            self.channel_on_select()
            self.thread_reset_event.clear()
            #print('Reset Complete!')
            #print(self.thread_reset_handle)
            self.updating_bool = False

        #print(self.GUI_reset_handle)

    ###############################################################################################
    #1. MAIN INTERFACE
    def LC18_interface(self):
        #MAIN PANEL GENERATION
        #frame_panel_1 long vertical panel anchored at top-left
        #frame_panel_2 long horizontal panel anchored at top
        #frame_panel_3 and frame_panel_4 is located inside frame_panel_2

        w_fr1 = 137 #180
        h_fr1 = 800

        w_fr2 = 920
        h_fr2 = 120

        w_fr3 = 430
        h_fr3 = 120

        w_fr4 = 488
        h_fr4 = 120

        try:
            if self.frame_panel_1.winfo_exists() == 1:
                for widget in self.frame_panel_1.winfo_children():
                    widget.destroy()
                self.frame_panel_1.destroy()
        except AttributeError:
            pass
        try:
            if self.frame_panel_2.winfo_exists() == 1:
                for widget in self.frame_panel_2.winfo_children():
                    widget.destroy()
                self.frame_panel_2.destroy()
        except AttributeError:
            pass
        try:
            if self.frame_panel_3.winfo_exists() == 1:
                for widget in self.frame_panel_3.winfo_children():
                    widget.destroy()
                self.frame_panel_3.destroy()
        except AttributeError:
            pass
        try:
            if self.frame_panel_4.winfo_exists() == 1:
                for widget in self.frame_panel_4.winfo_children():
                    widget.destroy()
                self.frame_panel_4.destroy()
        except AttributeError:
            pass

        self.frame_panel_1 = tk.Frame(self, width = w_fr1, height = h_fr1, highlightcolor = 'white', highlightthickness = 1, bg='DarkSlateGray2')
        self.frame_panel_1.place(x=0,y=0, relheight = 1)

        self.frame_panel_2 = tk.Frame(self, width = w_fr2, height = h_fr2, highlightthickness = 0)#, bg='cyan')
        self.frame_panel_2['bg'] = 'white'
        #self.frame_panel_2.place(x=182,y=0)
        self.frame_panel_2.place(x=139,y=30)

        self.frame_panel_3 = tk.Frame(self.frame_panel_2, width = w_fr3, height = h_fr3, highlightthickness = 0)#, bg='yellow')
        self.frame_panel_3['bg'] = 'DarkSlateGray2'
        self.frame_panel_3.place(x=0,y=0)

        self.frame_panel_4 = tk.Frame(self.frame_panel_2, width = w_fr4, height = h_fr4, highlightthickness = 0)#, bg='orange')
        self.frame_panel_4['bg'] = 'DarkSlateGray2'
        self.frame_panel_4.place(x=460-30 + 2,y=0)

        tk.Label(self.frame_panel_3, text = 'Channel\nSettings', font='Helvetica 14 bold', bg = 'DarkSlateGray2').place(x=2,y=25)
        tk.Label(self.frame_panel_4, text = 'Auto\nStrobe\nSettings', font='Helvetica 14 bold', bg = 'DarkSlateGray2', justify = 'left').place(x=2,y=10)

        self.ch_sel_btn1 = tk.Button(self, relief = tk.GROOVE, text = 'Channel 1 - 4', width = 12, font='Helvetica 11 bold')

        self.ch_sel_btn1['command'] = self.ch_sel_1_4

        self.ch_sel_btn1.place(x=0 + 139,y=0)

        self.main_control_gen()

        self.label_interval_var = tk.StringVar()
        self.interval_var = tk.StringVar()
        self.repeat_mode_var = tk.StringVar()
        self.repeat_number_var = tk.StringVar()

        self.repeat_control_gen()
        self.repeat_ALL_control_gen()

        widget_bind_focus(self.repeat_btn)
        widget_bind_focus(self.infinity_radio_btn)
        widget_bind_focus(self.finite_radio_btn)
        widget_bind_focus(self.repeat_number_spinbox)

        widget_bind_focus(self.repeat_ALL_btn)
        widget_bind_focus(self.infinity_radio_btn_2)
        widget_bind_focus(self.finite_radio_btn_2)
        widget_bind_focus(self.repeat_number_spinbox_2)

        self.ch_sel_1_4()
           
    def main_control_gen(self):
        self.firmware_version = tk.StringVar()
        self.board_firmware = tk.Label(self.frame_panel_3, textvariable = self.firmware_version, font='Helvetica 12 bold', bg = 'DarkSlateGray2', justify= tk.LEFT)
        self.board_firmware.place(x=270, y=2)
        self.firmware_version.set('Board Firmware\n' + str(self.firmware_version_str))

        self.EEPROM_button = tk.Button(self.frame_panel_3, relief = tk.GROOVE, text='Save EEPROM', font = "Helvetica 12")
        self.EEPROM_button['command'] = self.ctrl.save_function
        self.EEPROM_button.place(x= 270, y = 60)


        self.main_control_frame = tk.Frame(self.frame_panel_1, bg = 'DarkSlateGray2', highlightbackground="white", highlightthickness=1)
        self.main_control_frame['width'] =  120 + 5 #168
        self.main_control_frame['height'] = 200
        self.main_control_frame.place(x=5, y=5)

        tk.Label(self.main_control_frame, text = 'Main', bg= 'DarkSlateGray2', justify = 'left', font = "Helvetica 14 bold").place(x=0, y=0)
        self.load_param_button = tk.Button(self.main_control_frame, width = 10, relief = tk.GROOVE, text='Refresh', font = "Helvetica 12")
        self.load_param_button['command'] = self.load_btn_click
        self.load_param_button.place(x= 5, y = 30)

        self.EEPROM_ALL_button = tk.Button(self.main_control_frame, width = 10, relief = tk.GROOVE, text='Save All\nEEPROM', font = "Helvetica 12")
        self.EEPROM_ALL_button['command'] = self.ctrl.save_function
        self.EEPROM_ALL_button.place(x= 5, y = 65)

        self.strobe_ALL_button = tk.Button(self.main_control_frame, width = 10, relief = tk.GROOVE, text='Strobe All', font = "Helvetica 12")
        self.strobe_ALL_button['command'] = self.strobe_channel_repeat_ALL
        
        self.strobe_ALL_button.place(x= 5, y = 120)

        self.RESET_ALL_button = tk.Button(self.main_control_frame, width = 10, relief = tk.GROOVE, activeforeground= 'white', fg="white", activebackground = 'navy', bg = 'royal blue'
              , text='RESET ALL', font = "Helvetica 11 bold")
        self.RESET_ALL_button['command'] = self.reset_btn_click
        self.RESET_ALL_button.place(x= 5, y = 160)

    def repeat_control_gen(self):
        #REPEAT STROBE CONTROL
        self.repeat_frame = tk.Frame(self.frame_panel_4, bg = 'DarkSlateGray2', highlightbackground="white", highlightthickness=1, highlightcolor="white")
        self.repeat_frame['width'] = 135 + 65 + 5
        self.repeat_frame['height'] = 115

        self.repeat_frame.place(x=250+ 30, y=2)

        tk.Label(self.repeat_frame, text = 'Interval: ', font = "Helvetica 11"
            , bg = 'DarkSlateGray2').place(x = 0, y = 0)

        self.interval_entry_label = tk.Label(self.repeat_frame, textvariable = self.label_interval_var, font = "Helvetica 11", bg = 'DarkSlateGray2')

        self.interval_entry = tk.Spinbox(master = self.repeat_frame, width = 7, from_=0.5, to= 9999, increment = 0.001, textvariable = self.interval_var, font = "Helvetica 11"
                                     , highlightbackground="black", highlightthickness=1)
        self.interval_entry['validate']='key'
        self.interval_entry['vcmd']=(self.interval_entry.register(validate_float_entry), '%d', '%P', '%S')
        self.interval_entry['command'] = self.interval_spinbox_function
        self.interval_entry.bind('<Return>', self.interval_spinbox_function)
        self.interval_entry.bind('<Tab>', self.interval_spinbox_function)
        self.interval_entry.bind('<FocusOut>', self.interval_spinbox_function)

        self.interval_entry_label.place(x=2, y=40)
        self.label_interval_var.set(str(self.interval_parameter) + ' seconds')
        self.interval_entry.place(x= 2, y = 20)
        self.interval_var.set(self.interval_parameter)

        self.repeat_btn = tk.Button(self.repeat_frame, relief = tk.GROOVE, width = 6, font = "Helvetica 12 bold")
        self.repeat_btn = self.repeat_btn_widget(self.repeat_status, self.repeat_btn)
        self.repeat_btn['command'] = self.repeat_btn_click
        self.repeat_btn.place(x=5, y=65)

        tk.Label(self.repeat_frame, text = 'Repeat\nMode:', font = "Helvetica 11", bg = 'DarkSlateGray2', justify = 'left').place(x=100 + 20, y =0)
        self.infinity_radio_btn = tk.Radiobutton(self.repeat_frame,variable=self.repeat_mode_var, value='infinity', bg = 'DarkSlateGray2', activebackground = 'DarkSlateGray2' , image= self.infinity_icon)
        self.infinity_radio_btn['command'] = self.repeat_mode_set
        self.finite_radio_btn = tk.Radiobutton(self.repeat_frame,variable=self.repeat_mode_var, value='finite', bg = 'DarkSlateGray2', activebackground = 'DarkSlateGray2')
        self.finite_radio_btn['command'] = self.repeat_mode_set
        
        self.repeat_number_spinbox = tk.Spinbox(master = self.repeat_frame, width = 5, from_=1, to= 9999, textvariable = self.repeat_number_var, font = "Helvetica 11"
                                     , highlightbackground="black", highlightthickness=1)
        self.repeat_number_spinbox['command'] = self.repeat_number_spinbox_func
        self.repeat_number_spinbox.bind('<Return>', self.repeat_number_spinbox_func)
        self.repeat_number_spinbox.bind('<Tab>', self.repeat_number_spinbox_func)
        self.repeat_number_spinbox.bind('<FocusOut>', self.repeat_number_spinbox_func)

        self.repeat_mode_var.set(self.repeat_mode_str)
        self.repeat_number_var.set(str(self.repeat_number))
        int_validate(self.repeat_number_spinbox, limits = (1,9999))
        self.repeat_number_spinbox_state(self.repeat_number_spinbox)
        self.infinity_radio_btn.place(x=100 +20, y=20 +20)
        self.finite_radio_btn.place(x=99 +20, y=40 +20)
        self.repeat_number_spinbox.place(x=120 +20, y=40 +20)

    def repeat_ALL_control_gen(self):
        self.repeat_ALL_frame = tk.Frame(self.frame_panel_1, bg = 'DarkSlateGray2', highlightbackground="white", highlightthickness=1, highlightcolor="white")
        self.repeat_ALL_frame['width'] = 120 + 5 #168
        self.repeat_ALL_frame['height'] = 235

        self.repeat_ALL_frame.place(x=5, y=220)

        tk.Label(self.repeat_ALL_frame, text = 'Auto Repeat\nAll Strobe', bg= 'DarkSlateGray2', justify = 'left', font = "Helvetica 12 bold").place(x=0, y=0)
        tk.Label(self.repeat_ALL_frame, text = 'Interval: ', font = "Helvetica 11", bg = 'DarkSlateGray2').place(x=5, y =40)
        tk.Label(self.repeat_ALL_frame, text = 'Repeat Mode: ', font = "Helvetica 11", bg = 'DarkSlateGray2').place(x=5, y =120)

        self.interval_entry_2_label = tk.Label(self.repeat_ALL_frame, textvariable = self.label_interval_var, font = "Helvetica 11", bg = 'DarkSlateGray2')

        self.interval_entry_2 = tk.Spinbox(master = self.repeat_ALL_frame, width = 7, from_=0.5, to= 9999, increment = 0.001, textvariable = self.interval_var, font = "Helvetica 11"
                                     , highlightbackground="black", highlightthickness=1)
        self.interval_entry_2['validate']='key'
        self.interval_entry_2['vcmd']=(self.interval_entry_2.register(validate_float_entry), '%d', '%P', '%S')
        self.interval_entry_2['command'] = self.interval_spinbox_function

        self.interval_entry_2.bind('<Return>', self.interval_spinbox_function)
        self.interval_entry_2.bind('<Tab>', self.interval_spinbox_function)
        self.interval_entry_2.bind('<FocusOut>', self.interval_spinbox_function)

        self.interval_entry_2_label.place(x=5, y=80)
        self.label_interval_var.set(str(self.interval_parameter) + ' seconds')
        self.interval_entry_2.place(x= 5, y = 60)
        self.interval_var.set(self.interval_parameter)

        self.repeat_ALL_btn = tk.Button(self.repeat_ALL_frame, relief = tk.GROOVE, width = 6, font = "Helvetica 12 bold")
        self.repeat_ALL_btn = self.repeat_btn_widget(self.repeat_ALL_status, self.repeat_ALL_btn)
        self.repeat_ALL_btn['command'] = self.repeat_ALL_btn_click
        self.repeat_ALL_btn.place(x=5, y=115 +50 +30)


        self.infinity_radio_btn_2 = tk.Radiobutton(self.repeat_ALL_frame,variable=self.repeat_mode_var, value='infinity', bg = 'DarkSlateGray2', activebackground = 'DarkSlateGray2' , image= self.infinity_icon)
        self.infinity_radio_btn_2['command'] = self.repeat_mode_set
        self.finite_radio_btn_2 = tk.Radiobutton(self.repeat_ALL_frame,variable=self.repeat_mode_var, value='finite', bg = 'DarkSlateGray2', activebackground = 'DarkSlateGray2')
        self.finite_radio_btn_2['command'] = self.repeat_mode_set

        self.repeat_number_spinbox_2 = tk.Spinbox(master = self.repeat_ALL_frame, width = 5, from_=1, to= 9999, textvariable = self.repeat_number_var, font = "Helvetica 11"
                                     , highlightbackground="black", highlightthickness=1)
        self.repeat_number_spinbox_2['command'] = self.repeat_number_spinbox_func
        self.repeat_number_spinbox_2.bind('<Return>', self.repeat_number_spinbox_func)
        self.repeat_number_spinbox_2.bind('<Tab>', self.repeat_number_spinbox_func)
        self.repeat_number_spinbox_2.bind('<FocusOut>', self.repeat_number_spinbox_func)

        self.repeat_mode_var.set(self.repeat_mode_str)
        self.repeat_number_var.set(str(self.repeat_number))
        int_validate(self.repeat_number_spinbox_2, limits = (1,9999))
        self.repeat_number_spinbox_state(self.repeat_number_spinbox_2)
        self.infinity_radio_btn_2.place(x=5, y=110 +30)
        self.finite_radio_btn_2.place(x=4, y=130 +30)
        self.repeat_number_spinbox_2.place(x=25, y=130 +30)

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

    def repeat_mode_set(self, event=None):
        self.repeat_mode_str = self.repeat_mode_var.get()
        self.repeat_number_spinbox_state(self.repeat_number_spinbox)
        self.repeat_number_spinbox_state(self.repeat_number_spinbox_2)


    def repeat_number_spinbox_state(self, spinbox_widget):
        if self.repeat_mode_str == 'infinity':
            if spinbox_widget['state'] != 'disabled':
                spinbox_widget['state'] = 'disabled'

        elif self.repeat_mode_str == 'finite':
            if spinbox_widget['state'] != 'normal':
                spinbox_widget['state'] = 'normal'

    def repeat_number_spinbox_func(self, event=None):
        if self.repeat_number_var.get() == '':
            self.repeat_number_var.set(str(1))
            pass
        else:
            self.repeat_number = int(self.repeat_number_var.get())

    def interval_spinbox_function(self, event = None):
        try:
            self.interval_parameter = float(self.interval_var.get())
            if self.interval_parameter < 0.5:
                # interval_var.set(interval_arr_v2[0])
                # self.interval_parameter = float(self.interval_entry.get())
                self.interval_var.set(0.5)
                self.interval_parameter = 0.5

            elif self.interval_parameter > 9999:
                # interval_var.set(interval_arr_v2[0])
                # self.interval_parameter = float(self.interval_entry.get())
                self.interval_var.set(9999.0)
                self.interval_parameter = 9999.0
        except:
            self.interval_var.set(self.interval_arr[0])
            pass

        self.interval_parameter = round(self.interval_parameter, 3)
        self.interval_arr[0] = self.interval_parameter
        self.label_interval_var.set(str(self.interval_parameter) + ' seconds') #displays the interval time in milliseconds
        self.interval_var.set(self.interval_parameter)
        self.interval_entry.icursor('end')
        self.interval_entry_2.icursor('end')

    ###############################################################################################
    #2. CONTROL PANEL INTERFACE 1
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

    def ch_sel_1_4(self):
        self.ch_sel_str = '1 - 4'
        self.ch_sel_btn_state(self.ch_sel_btn1)
        self.channel_on_select()

    def channel_setting_GUI(self):
        w_fr5 = 920
        h_fr5 = 650
        try:
            if self.frame_panel_5.winfo_exists() == 1:
                for widget in self.frame_panel_5.winfo_children():
                    widget.destroy()
                self.frame_panel_5.destroy()
        except AttributeError:
            pass
        self.frame_panel_5 = tk.Frame(self, width = w_fr5, height = h_fr5, highlightthickness = 0)#, bg='green')
        self.frame_panel_5['bg'] = 'white'
        #self.frame_panel_5.place(x=182,y=150)
        self.frame_panel_5.place(x=139,y=150)

    def channel_on_select(self):
        self.channel_setting_GUI()
        
        self.strobe_ch_sel()
        
        widget_enable(self.sel_1_checkbox, self.sel_2_checkbox, self.sel_3_checkbox, self.sel_4_checkbox)

        if self.ch_sel_str == '1 - 4':
            self.board_address()
            #self.channel_1_save[7] = self.channel_2_save[7] = self.channel_3_save[7] = self.channel_4_save[7] = self.addr_index_a

            self.channel_frame_1 = self.generate_ch_frame(self.frame_panel_5, 1)
            (self.ch_1_entry_c_label, self.ch_1_entry_d_label, self.ch_1_entry_e_label, self.ch_1_entry_f_label, self.ch_1_mode, 
                self.ch_1_scalevar_a, self.ch_1_scalevar_b, self.ch_1_scalevar_c, self.ch_1_scalevar_d, self.ch_1_scalevar_e, self.ch_1_scalevar_f) = self.generate_panel(self.channel_frame_1,'Channel 1', 1, self.channel_1_save)

            self.channel_frame_2 = self.generate_ch_frame(self.frame_panel_5, 2)
            (self.ch_2_entry_c_label, self.ch_2_entry_d_label, self.ch_2_entry_e_label, self.ch_2_entry_f_label, self.ch_2_mode, 
                self.ch_2_scalevar_a, self.ch_2_scalevar_b, self.ch_2_scalevar_c, self.ch_2_scalevar_d, self.ch_2_scalevar_e, self.ch_2_scalevar_f) = self.generate_panel(self.channel_frame_2,'Channel 2', 2, self.channel_2_save)

            self.channel_frame_3 = self.generate_ch_frame(self.frame_panel_5, 3)
            (self.ch_3_entry_c_label, self.ch_3_entry_d_label, self.ch_3_entry_e_label, self.ch_3_entry_f_label, self.ch_3_mode, 
                self.ch_3_scalevar_a, self.ch_3_scalevar_b, self.ch_3_scalevar_c, self.ch_3_scalevar_d, self.ch_3_scalevar_e, self.ch_3_scalevar_f) = self.generate_panel(self.channel_frame_3,'Channel 3', 3, self.channel_3_save)

            self.channel_frame_4 = self.generate_ch_frame(self.frame_panel_5, 4)
            (self.ch_4_entry_c_label, self.ch_4_entry_d_label, self.ch_4_entry_e_label, self.ch_4_entry_f_label, self.ch_4_mode, 
                self.ch_4_scalevar_a, self.ch_4_scalevar_b, self.ch_4_scalevar_c, self.ch_4_scalevar_d, self.ch_4_scalevar_e, self.ch_4_scalevar_f) = self.generate_panel(self.channel_frame_4,'Channel 4', 4, self.channel_4_save)
            
    def generate_ch_frame(self, tk_frame, ch_tag_num):
        W = 450
        H = 315
        if ch_tag_num == 1:
            channel_frame = tk.Frame(tk_frame, width = W, height = H, highlightbackground="black", highlightthickness=1)
            #channel_frame.place(x= 0, y = 210)
            channel_frame.place(x= 5, y = 5)

        elif ch_tag_num == 2:
            channel_frame = tk.Frame(tk_frame, width = W, height = H, highlightbackground="black", highlightthickness=1)
            #channel_frame.place(x= 185, y = 210)
            channel_frame.place(x= 460, y = 5)

        elif ch_tag_num == 3:
            channel_frame = tk.Frame(tk_frame, width = W, height = H, highlightbackground="black", highlightthickness=1)
            #channel_frame.place(x= 370, y = 210)
            channel_frame.place(x= 5, y = 325)

        elif ch_tag_num == 4:
            channel_frame = tk.Frame(tk_frame, width = W, height = H, highlightbackground="black", highlightthickness=1)
            #channel_frame.place(x= 555, y = 210)
            channel_frame.place(x= 460 , y = 325)
        return channel_frame
    
    def generate_panel(self, channel_frame, channel_name, ch_tag_num, channel_save):
        x_pos1 = 110+30+15
        x_pos2 = 230+30+15
        x_pos3 = 340+30+15

        channel_label = tk.Label(channel_frame, text = channel_name, font = 'Helvetica 14 bold')
        channel_label.place(x= 15, y = 0)
        
        #####################################################################################################################
        ch_label_a = tk.Label(channel_frame, text = 'Current Multiplier', font = 'Helvetica 11', width = 12)
        scalevar_a = tk.IntVar(value = channel_save[0])
        ch_entry_a = tk.Spinbox(master = channel_frame, width = 4, textvariable = scalevar_a,from_=1, to=10
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        ch_entry_a['validate']='key'
        ch_entry_a['vcmd']=(ch_entry_a.register(validate_int_entry),'%d','%P','%S', True)

        ch_scalebar_a = tk.Scale(channel_frame, from_=1, to=10, variable=scalevar_a, orient='horizontal', showvalue=0)

        self.widget_current_command(ch_tag_num, ch_entry_a)
        self.spinbox_current_bind(ch_tag_num, ch_entry_a)
        self.widget_current_command(ch_tag_num, ch_scalebar_a)

        ch_entry_a.bind('<FocusOut>', lambda event: focusout_func(widget=ch_entry_a, val=channel_save[0]))
        widget_bind_focus(ch_entry_a)
        widget_bind_focus(ch_scalebar_a)

        ch_label_a.place(x= x_pos1, y = 20)
        ch_scalebar_a.place(x= x_pos2,y=20)
        ch_entry_a.place(x= x_pos3, y = 20)

        #####################################################################################################################
        ch_label_b = tk.Label(channel_frame, text = 'Intensity', font = 'Helvetica 11', width = 12)
        scalevar_b = tk.IntVar(value = channel_save[1])
        ch_entry_b = tk.Spinbox(master = channel_frame, width = 4, textvariable = scalevar_b,from_=0, to=255
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        ch_entry_b['validate']='key'
        ch_entry_b['vcmd']=(ch_entry_b.register(validate_int_entry),'%d','%P','%S', True)
        ch_scalebar_b = tk.Scale(channel_frame, from_=0, to=255, variable=scalevar_b, orient='horizontal', showvalue=0)

        self.widget_intensity_command(ch_tag_num, ch_entry_b)
        self.spinbox_intensity_bind(ch_tag_num, ch_entry_b)
        self.widget_intensity_command(ch_tag_num, ch_scalebar_b)
        ch_entry_b.bind('<FocusOut>', lambda event: focusout_func(widget=ch_entry_b, val=channel_save[1]))
        widget_bind_focus(ch_entry_b)
        widget_bind_focus(ch_scalebar_b)

        ch_label_b.place(x= x_pos1, y = 45)
        ch_scalebar_b.place(x=x_pos2,y=45)
        ch_entry_b.place(x= x_pos3, y = 45)

        #####################################################################################################################
        ch_label_c = tk.Label(channel_frame, text = 'Strobe Delay\n(0-9999)', font = 'Helvetica 11', width = 12)
        scalevar_c = tk.IntVar(value = channel_save[2])
        ch_entry_c = tk.Spinbox(master = channel_frame, width = 4, textvariable = scalevar_c, from_=0, to= 9999, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        ch_entry_c['validate']='key'
        ch_entry_c['vcmd']=(ch_entry_c.register(validate_int_entry),'%d','%P','%S', True)
        ch_scalebar_c = tk.Scale(channel_frame, from_=0, to=9999, variable=scalevar_c, orient='horizontal', showvalue=0)

        ch_entry_c_label = tk.StringVar()
        label_c = tk.Label(channel_frame, textvariable = ch_entry_c_label,  font = 'Helvetica 11 italic')
        ch_entry_c_label.set(str(np.divide(int(channel_save[2]), 100)) + ' ms')

        self.widget_strobe_command(ch_tag_num, ch_entry_c)
        self.spinbox_strobe_bind(ch_tag_num, ch_entry_c)
        self.widget_strobe_command(ch_tag_num, ch_scalebar_c)
        ch_entry_c.bind('<FocusOut>', lambda event: focusout_func(widget=ch_entry_c, val=channel_save[2]))
        widget_bind_focus(ch_entry_c)
        widget_bind_focus(ch_scalebar_c)

        ch_label_c.place(x= x_pos1, y = 80)
        ch_scalebar_c.place(x=x_pos2,y=80)
        ch_entry_c.place(x= x_pos3, y = 80)
        label_c.place(x= x_pos3-5, y = 103)

        #####################################################################################################################
        ch_label_d = tk.Label(channel_frame, text = 'Strobe Width\n(0-9999)', font = 'Helvetica 11', width = 12)
        scalevar_d = tk.IntVar(value = channel_save[3])
        ch_entry_d = tk.Spinbox(master = channel_frame, width = 4, textvariable = scalevar_d, from_=0, to= 9999, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        ch_entry_d['validate']='key'
        ch_entry_d['vcmd']=(ch_entry_c.register(validate_int_entry),'%d','%P','%S', True)

        ch_scalebar_d = tk.Scale(channel_frame, from_=0, to=9999, variable=scalevar_d, orient='horizontal', showvalue=0)

        ch_entry_d_label = tk.StringVar()
        label_d = tk.Label(channel_frame, textvariable = ch_entry_d_label,  font = 'Helvetica 11 italic')
        ch_entry_d_label.set(str(np.divide(int(channel_save[3]), 100)) + ' ms')

        self.widget_strobe_command(ch_tag_num, ch_entry_d)
        self.spinbox_strobe_bind(ch_tag_num, ch_entry_d)
        self.widget_strobe_command(ch_tag_num, ch_scalebar_d)
        ch_entry_d.bind('<FocusOut>', lambda event: focusout_func(widget=ch_entry_d, val=channel_save[3]))
        widget_bind_focus(ch_entry_d)
        widget_bind_focus(ch_scalebar_d)

        ch_label_d.place(x= x_pos1, y = 130)
        ch_scalebar_d.place(x=x_pos2,y=130)
        ch_entry_d.place(x= x_pos3, y = 130)
        label_d.place(x= x_pos3-5, y = 153)

        #####################################################################################################################
        ch_label_e = tk.Label(channel_frame, text = 'Output Delay\n(0-9999)', font = 'Helvetica 11', width = 12)
        scalevar_e = tk.IntVar(value = channel_save[4])
        ch_entry_e = tk.Spinbox(master = channel_frame, width = 4, textvariable = scalevar_e, from_=0, to= 9999, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        ch_entry_e['validate']='key'
        ch_entry_e['vcmd']=(ch_entry_e.register(validate_int_entry),'%d','%P','%S', True)
        
        ch_scalebar_e = tk.Scale(channel_frame, from_=0, to=9999, variable=scalevar_e, orient='horizontal', showvalue=0) 

        ch_entry_e_label = tk.StringVar()
        label_e = tk.Label(channel_frame, textvariable = ch_entry_e_label,  font = 'Helvetica 11 italic')
        ch_entry_e_label.set(str(np.divide(int(channel_save[4]), 100)) + ' ms')

        self.widget_output_command(ch_tag_num, ch_entry_e)
        self.spinbox_output_bind(ch_tag_num, ch_entry_e)
        self.widget_output_command(ch_tag_num, ch_scalebar_e)
        ch_entry_e.bind('<FocusOut>', lambda event: focusout_func(widget=ch_entry_e, val=channel_save[4]))
        widget_bind_focus(ch_entry_e)
        widget_bind_focus(ch_scalebar_e)

        ch_label_e.place(x= x_pos1, y = 180)
        ch_scalebar_e.place(x=x_pos2,y=180)
        ch_entry_e.place(x= x_pos3, y = 180)
        label_e.place(x= x_pos3-5, y = 203)

        #####################################################################################################################
        ch_label_f = tk.Label(channel_frame, text = 'Output Width\n(0-9999)', font = 'Helvetica 11', width = 12)
        scalevar_f = tk.IntVar(value = channel_save[5])
        ch_entry_f = tk.Spinbox(master = channel_frame, width = 4, textvariable = scalevar_f, from_=0, to= 9999, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        ch_entry_f['validate']='key'
        ch_entry_f['vcmd']=(ch_entry_f.register(validate_int_entry),'%d','%P','%S', True)
        
        ch_scalebar_f = tk.Scale(channel_frame, from_=0, to=9999, variable=scalevar_f, orient='horizontal', showvalue=0)

        ch_entry_f_label = tk.StringVar()
        label_f = tk.Label(channel_frame, textvariable = ch_entry_f_label,  font = 'Helvetica 11 italic')
        ch_entry_f_label.set(str(np.divide(int(channel_save[5]), 100)) + ' ms')

        self.widget_output_command(ch_tag_num, ch_entry_f)
        self.spinbox_output_bind(ch_tag_num, ch_entry_f)
        self.widget_output_command(ch_tag_num, ch_scalebar_f)
        ch_entry_f.bind('<FocusOut>', lambda event: focusout_func(widget=ch_entry_f, val=channel_save[5]))
        widget_bind_focus(ch_entry_f)
        widget_bind_focus(ch_scalebar_f)

        ch_label_f.place(x= x_pos1, y = 230)
        ch_scalebar_f.place(x=x_pos2,y=230)
        ch_entry_f.place(x= x_pos3, y = 230)
        label_f.place(x= x_pos3-5, y = 253)


        tk.Label(channel_frame, text = 'Select Mode: ', font = 'Helvetica 12 italic', width = 12).place(x=10, y=45)

        mode_list = ['Constant Mode', 'Strobe Mode', 'Trigger Mode']
        channel_frame.option_add('*TCombobox*Listbox.font', ('Helvetica', '11'))
        ch_mode = ttk.Combobox(channel_frame, values=mode_list, width=13, state='readonly', font = 'Helvetica 11')
        ch_mode.place(x= 10, y = 70)
        self.combobox_widget_bind(ch_tag_num, ch_mode)
        
        if channel_save[6] == 0:
            ch_mode.current(0)
        elif channel_save[6] == 1:
            ch_mode.current(1)
        elif channel_save[6] == 2:
            ch_mode.current(2)

        ch_mode.unbind_class("TCombobox", "<MouseWheel>")

        strobe_button = tk.Button(channel_frame, relief = tk.GROOVE, width = 10, height = 1, font = 'Helvetica 12')
        strobe_button['text'] = 'Strobe CH' + str(ch_tag_num)
        self.strobe_button_command(ch_tag_num, strobe_button)

        strobe_button.place(x = 10, y = 150)

        return (ch_entry_c_label, ch_entry_d_label, ch_entry_e_label, ch_entry_f_label, ch_mode, 
            scalevar_a, scalevar_b, scalevar_c, scalevar_d, scalevar_e, scalevar_f)


    ###############################################################################################
    #3. CONTROL PANEL INTERFACE 2
    def strobe_ch_sel(self):
        #y_coordinate placement for checkboxes
        y_init_coordinate = 18 #15
        y_spacing = 23
        y_row0 = y_init_coordinate
        y_row1 = y_init_coordinate + y_spacing
        y_row2 = y_row1 + y_spacing
        y_row3 = y_row2 + y_spacing

        y_label_coordinate = y_init_coordinate + 1

        try:
            if self.ch_sel_frame.winfo_exists() == 1:
                for widget in self.ch_sel_frame.winfo_children():
                    widget.destroy()
                self.ch_sel_frame.destroy()
        except AttributeError:
            pass
            
        self.ch_sel_frame = tk.Frame(self.frame_panel_4, width = 180, height = 115, highlightbackground="white", highlightthickness=1, highlightcolor = "white")  #height = 70
        self.ch_sel_frame['bg'] = 'DarkSlateGray2'
        self.ch_sel_frame.place(x= 66 + 30, y = 2)

        self.ch_sel_frame_label = tk.Label(self.ch_sel_frame, text = 'Strobe Channel:', font='Helvetica 11')
        self.ch_sel_frame_label['bg'] = 'DarkSlateGray2'
        self.ch_sel_frame_label.place(x= 0, y = 0)

        self.ch_sel_1_status = tk.IntVar(value = self.strobe_ch_arr[0])
        self.ch_sel_2_status = tk.IntVar(value = self.strobe_ch_arr[1])
        self.ch_sel_3_status = tk.IntVar(value = self.strobe_ch_arr[2])
        self.ch_sel_4_status = tk.IntVar(value = self.strobe_ch_arr[3])

        self.ch_sel_5_status = tk.IntVar(value = self.strobe_ch_arr[4])
        self.ch_sel_6_status = tk.IntVar(value = self.strobe_ch_arr[5])
        self.ch_sel_7_status = tk.IntVar(value = self.strobe_ch_arr[6])
        self.ch_sel_8_status = tk.IntVar(value = self.strobe_ch_arr[7])

        self.ch_sel_9_status = tk.IntVar(value = self.strobe_ch_arr[8])
        self.ch_sel_10_status = tk.IntVar(value = self.strobe_ch_arr[9])
        self.ch_sel_11_status = tk.IntVar(value = self.strobe_ch_arr[10])
        self.ch_sel_12_status = tk.IntVar(value = self.strobe_ch_arr[11])

        self.ch_sel_13_status = tk.IntVar(value = self.strobe_ch_arr[12])
        self.ch_sel_14_status = tk.IntVar(value = self.strobe_ch_arr[13])
        self.ch_sel_15_status = tk.IntVar(value = self.strobe_ch_arr[14])
        self.ch_sel_16_status = tk.IntVar(value = self.strobe_ch_arr[15])
        
        self.sel_1_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_1_status, command = self.strobe_ch_sel_click)
        self.sel_2_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_2_status, command = self.strobe_ch_sel_click)
        self.sel_3_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_3_status, command = self.strobe_ch_sel_click)
        self.sel_4_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_4_status, command = self.strobe_ch_sel_click)
        self.sel_1_checkbox['bg'] = self.sel_2_checkbox['bg'] = self.sel_3_checkbox['bg'] = self.sel_4_checkbox['bg'] = 'DarkSlateGray2'
        self.sel_1_checkbox['activebackground'] = self.sel_2_checkbox['activebackground'] = self.sel_3_checkbox['activebackground'] = self.sel_4_checkbox['activebackgroun'] = 'DarkSlateGray2'
        
        self.sel_1_checkbox.place(x=5, y= y_row0) # x= 0, 40 , 85, 125
        self.sel_2_checkbox.place(x=45, y= y_row0)
        self.sel_3_checkbox.place(x=90, y= y_row0)
        self.sel_4_checkbox.place(x=130, y= y_row0)

        self.sel_5_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_5_status, command = self.strobe_ch_sel_click)
        self.sel_6_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_6_status, command = self.strobe_ch_sel_click)
        self.sel_7_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_7_status, command = self.strobe_ch_sel_click)
        self.sel_8_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_8_status, command = self.strobe_ch_sel_click)
        self.sel_5_checkbox['bg'] = self.sel_6_checkbox['bg'] = self.sel_7_checkbox['bg'] = self.sel_8_checkbox['bg'] = 'DarkSlateGray2'
        self.sel_5_checkbox['activebackground'] = self.sel_6_checkbox['activebackground'] = self.sel_7_checkbox['activebackground'] = self.sel_8_checkbox['activebackgroun'] = 'DarkSlateGray2'

        self.sel_5_checkbox.place(x=5, y= y_row1)
        self.sel_6_checkbox.place(x=45, y= y_row1)
        self.sel_7_checkbox.place(x=90, y= y_row1)
        self.sel_8_checkbox.place(x=130, y= y_row1)

        self.sel_9_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_9_status, command = self.strobe_ch_sel_click)
        self.sel_10_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_10_status, command = self.strobe_ch_sel_click)
        self.sel_11_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_11_status, command = self.strobe_ch_sel_click)
        self.sel_12_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_12_status, command = self.strobe_ch_sel_click)
        self.sel_9_checkbox['bg'] = self.sel_10_checkbox['bg'] = self.sel_11_checkbox['bg'] = self.sel_12_checkbox['bg'] = 'DarkSlateGray2'
        self.sel_9_checkbox['activebackground'] = self.sel_10_checkbox['activebackground'] = self.sel_11_checkbox['activebackground'] = self.sel_12_checkbox['activebackgroun'] = 'DarkSlateGray2'

        self.sel_9_checkbox.place(x=5, y=y_row2)
        self.sel_10_checkbox.place(x=45, y=y_row2)
        self.sel_11_checkbox.place(x=90, y=y_row2)
        self.sel_12_checkbox.place(x=130, y=y_row2)

        self.sel_13_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_13_status, command = self.strobe_ch_sel_click)
        self.sel_14_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_14_status, command = self.strobe_ch_sel_click)
        self.sel_15_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_15_status, command = self.strobe_ch_sel_click)
        self.sel_16_checkbox = tk.Checkbutton(self.ch_sel_frame, variable= self.ch_sel_16_status, command = self.strobe_ch_sel_click)
        self.sel_13_checkbox['bg'] = self.sel_14_checkbox['bg'] = self.sel_15_checkbox['bg'] = self.sel_16_checkbox['bg'] = 'DarkSlateGray2'
        self.sel_13_checkbox['activebackground'] = self.sel_14_checkbox['activebackground'] = self.sel_15_checkbox['activebackground'] = self.sel_16_checkbox['activebackgroun'] = 'DarkSlateGray2'

        self.sel_13_checkbox.place(x=5, y=y_row3)
        self.sel_14_checkbox.place(x=45, y=y_row3)
        self.sel_15_checkbox.place(x=90, y=y_row3)
        self.sel_16_checkbox.place(x=130, y=y_row3)

        widget_bind_focus(self.sel_1_checkbox)
        widget_bind_focus(self.sel_2_checkbox)
        widget_bind_focus(self.sel_3_checkbox)
        widget_bind_focus(self.sel_4_checkbox)

        widget_bind_focus(self.sel_5_checkbox)
        widget_bind_focus(self.sel_6_checkbox)
        widget_bind_focus(self.sel_7_checkbox)
        widget_bind_focus(self.sel_8_checkbox)

        widget_bind_focus(self.sel_9_checkbox)
        widget_bind_focus(self.sel_10_checkbox)
        widget_bind_focus(self.sel_11_checkbox)
        widget_bind_focus(self.sel_12_checkbox)

        widget_bind_focus(self.sel_13_checkbox)
        widget_bind_focus(self.sel_14_checkbox)
        widget_bind_focus(self.sel_15_checkbox)
        widget_bind_focus(self.sel_16_checkbox)

        ch_sel_1_label, ch_sel_2_label, ch_sel_3_label, ch_sel_4_label = self.strobe_label_sel_generate('1','2','3','4',
            x1=25,x2=65,x3=110,x4=150,    y1=y_label_coordinate,y2=y_label_coordinate,y3=y_label_coordinate,y4=y_label_coordinate)

        ch_sel_5_label, ch_sel_6_label, ch_sel_7_label, ch_sel_8_label = self.strobe_label_sel_generate('5','6','7','8',
            x1=25,x2=65,x3=110,x4=150,    y1=y_label_coordinate,y2=y_label_coordinate,y3=y_label_coordinate,y4=y_label_coordinate)

        ch_sel_9_label, ch_sel_10_label, ch_sel_11_label, ch_sel_12_label = self.strobe_label_sel_generate('9','10','11','12',
            x1=25,x2=65,x3=110,x4=150,    y1=y_label_coordinate,y2=y_label_coordinate,y3=y_label_coordinate,y4=y_label_coordinate)

        ch_sel_13_label, ch_sel_14_label, ch_sel_15_label, ch_sel_16_label = self.strobe_label_sel_generate('13','14','15','16',
            x1=25,x2=65,x3=110,x4=150,    y1=y_label_coordinate,y2=y_label_coordinate,y3=y_label_coordinate,y4=y_label_coordinate)

        widget_disable(self.sel_1_checkbox, self.sel_2_checkbox, self.sel_3_checkbox, self.sel_4_checkbox, self.sel_5_checkbox, self.sel_6_checkbox, self.sel_7_checkbox, self.sel_8_checkbox
            , self.sel_9_checkbox, self.sel_10_checkbox, self.sel_11_checkbox, self.sel_12_checkbox, self.sel_13_checkbox, self.sel_14_checkbox, self.sel_15_checkbox, self.sel_16_checkbox)


    def strobe_label_sel_generate(self, str1,str2,str3,str4,
        x1,y1,x2,y2,x3,y3,x4,y4):
        label_spacing = 23
        label_bg = 'DarkSlateGray2'

        if str1=='5' and str2=='6' and str3=='7' and str4=='8':
            y1 = y1 + label_spacing
            y2 = y2 + label_spacing
            y3 = y3 + label_spacing
            y4 = y4 + label_spacing

        elif str1=='9' and str2=='10' and str3=='11' and str4=='12':
            y1 = y1 + int(np.multiply(2,label_spacing))
            y2 = y2 + int(np.multiply(2,label_spacing))
            y3 = y3 + int(np.multiply(2,label_spacing))
            y4 = y4 + int(np.multiply(2,label_spacing))

        elif str1=='13' and str2=='14' and str3=='15' and str4=='16':
            y1 = y1 + int(np.multiply(3,label_spacing))
            y2 = y2 + int(np.multiply(3,label_spacing))
            y3 = y3 + int(np.multiply(3,label_spacing))
            y4 = y4 + int(np.multiply(3,label_spacing))

        gen_1_label = tk.Label(self.ch_sel_frame, bg=label_bg, text = str1, font='Helvetica 11 bold')
        gen_1_label.place(x= x1, y = y1)
        gen_2_label = tk.Label(self.ch_sel_frame, bg=label_bg, text = str2, font='Helvetica 11 bold')
        gen_2_label.place(x= x2, y = y2)
        gen_3_label = tk.Label(self.ch_sel_frame, bg=label_bg, text = str3, font='Helvetica 11 bold')
        gen_3_label.place(x= x3, y = y3)
        gen_4_label = tk.Label(self.ch_sel_frame, bg=label_bg, text = str4, font='Helvetica 11 bold')
        gen_4_label.place(x= x4, y = y4)

        return gen_1_label, gen_2_label, gen_3_label, gen_4_label
    

    def strobe_ch_sel_click(self, event=None):
        self.strobe_ch_arr[0] = self.ch_sel_1_status.get()
        self.strobe_ch_arr[1] = self.ch_sel_2_status.get()
        self.strobe_ch_arr[2] = self.ch_sel_3_status.get()
        self.strobe_ch_arr[3] = self.ch_sel_4_status.get()

        self.strobe_ch_arr[4] = self.ch_sel_5_status.get()
        self.strobe_ch_arr[5] = self.ch_sel_6_status.get()
        self.strobe_ch_arr[6] = self.ch_sel_7_status.get()
        self.strobe_ch_arr[7] = self.ch_sel_8_status.get()

        self.strobe_ch_arr[8] = self.ch_sel_9_status.get()
        self.strobe_ch_arr[9] = self.ch_sel_10_status.get()
        self.strobe_ch_arr[10] = self.ch_sel_11_status.get()
        self.strobe_ch_arr[11] = self.ch_sel_12_status.get()

        self.strobe_ch_arr[12] = self.ch_sel_13_status.get()
        self.strobe_ch_arr[13] = self.ch_sel_14_status.get()
        self.strobe_ch_arr[14] = self.ch_sel_15_status.get()
        self.strobe_ch_arr[15] = self.ch_sel_16_status.get()

        #print(self.strobe_ch_arr)

    def board_address(self):
        try:
            if self.board_addr_frame.winfo_exists() == 1:
                for widget in self.board_addr_frame.winfo_children():
                    widget.destroy()
                self.board_addr_frame.destroy()
        except AttributeError:
            pass

        y_addr_label = 45
        y_addr_checkbox = 25
        addr_bg_colour = "DarkSlateGray2" #"gray76"
        self.board_addr_frame = tk.Frame(self.frame_panel_3, width = 140, height = 85, bg=addr_bg_colour, highlightbackground="black", highlightthickness=1)
        self.board_addr_frame.place(x= 120, y = 10) 

        #board_addr_label = tk.Label(self.board_addr_frame, bg="gray76", text = 'Board Address', font = "Helvetica 11 bold")
        board_addr_label = tk.Label(self.board_addr_frame, bg=addr_bg_colour, text = 'Board Address', font = "Helvetica 11 bold")
        board_addr_label.place(x= 0, y = 0)

        addr_0_label = tk.Label(self.board_addr_frame, bg=addr_bg_colour, text = '0', font='Helvetica 11 bold')
        addr_0_label.place(x= 15, y = y_addr_label)

        addr_1_label = tk.Label(self.board_addr_frame, bg=addr_bg_colour, text = '1', font='Helvetica 11 bold')
        addr_1_label.place(x= 40, y = y_addr_label)

        addr_2_label = tk.Label(self.board_addr_frame, bg=addr_bg_colour, text = '2', font='Helvetica 11 bold')
        addr_2_label.place(x= 65, y = y_addr_label)

        addr_3_label = tk.Label(self.board_addr_frame, bg=addr_bg_colour, text = '3', font='Helvetica 11 bold')
        addr_3_label.place(x= 90, y = y_addr_label)
        
        self.addr_index_a = binary_to_dec_v2(self.addr_a[0], self.addr_a[1], self.addr_a[2], self.addr_a[3], reverse_str = True)

        if self.ch_sel_str == '1 - 4': #0000
            (self.addr_0_checkbox_a, self.addr_1_checkbox_a, 
                self.addr_2_checkbox_a, self.addr_3_checkbox_a) = self.board_addr_checkbox(self.addr_a[0], self.addr_a[1], self.addr_a[2], self.addr_a[3])
            self.addr_0_checkbox_a.place(x= 10, y = y_addr_checkbox)
            self.addr_1_checkbox_a.place(x= 35, y = y_addr_checkbox)
            self.addr_2_checkbox_a.place(x= 60, y = y_addr_checkbox)
            self.addr_3_checkbox_a.place(x= 85, y = y_addr_checkbox)

            widget_disable(self.addr_0_checkbox_a, self.addr_1_checkbox_a, 
                    self.addr_2_checkbox_a, self.addr_3_checkbox_a)

    def board_addr_checkbox(self,val_0, val_1, val_2, val_3):
        addr_bg_colour = "DarkSlateGray2" #"gray76"

        self.addr_0_status = tk.IntVar(value = val_0)
        self.addr_1_status = tk.IntVar(value = val_1)
        self.addr_2_status = tk.IntVar(value = val_2)
        self.addr_3_status = tk.IntVar(value = val_3)

        addr_0_checkbox = tk.Checkbutton(self.board_addr_frame, bg=addr_bg_colour, activebackground= addr_bg_colour, variable= self.addr_0_status)
        addr_1_checkbox = tk.Checkbutton(self.board_addr_frame, bg=addr_bg_colour, activebackground= addr_bg_colour, variable= self.addr_1_status)
        addr_2_checkbox = tk.Checkbutton(self.board_addr_frame, bg=addr_bg_colour, activebackground= addr_bg_colour, variable= self.addr_2_status)
        addr_3_checkbox = tk.Checkbutton(self.board_addr_frame, bg=addr_bg_colour, activebackground= addr_bg_colour, variable= self.addr_3_status)

        addr_0_checkbox['command'] = self.board_addr_click
        addr_1_checkbox['command'] = self.board_addr_click
        addr_2_checkbox['command'] = self.board_addr_click
        addr_3_checkbox['command'] = self.board_addr_click

        return addr_0_checkbox, addr_1_checkbox, addr_2_checkbox, addr_3_checkbox
    
    def board_addr_click(self,event = None):
        if self.ch_sel_str == '1 - 4':
            self.addr_a[0] = self.addr_0_status.get()
            self.addr_a[1] = self.addr_1_status.get()
            self.addr_a[2] = self.addr_2_status.get()
            self.addr_a[3] = self.addr_3_status.get()
            self.addr_index_a = binary_to_dec_v2(self.addr_a[0], self.addr_a[1], self.addr_a[2], self.addr_a[3], reverse_str = True)
            self.channel_1_save[7] = self.channel_2_save[7] = self.channel_3_save[7] = self.channel_4_save[7] = self.addr_index_a

        # print('addr_a: ', self.addr_a)

    ###############################################################################################
    #4. LIGHT CONTROL FUNCTIONS
    def widget_current_command(self, ch_tag_num, widget):
        if ch_tag_num == 1:
            widget.config(command = self.current_multi_group_A)

        elif ch_tag_num == 2:
            widget.config(command = self.current_multi_group_B)

        elif ch_tag_num == 3:
            widget.config(command = self.current_multi_group_C)

        elif ch_tag_num == 4:
            widget.config(command = self.current_multi_group_D)

    def spinbox_current_bind(self, ch_tag_num, widget):
        if ch_tag_num == 1:
            widget.bind('<Return>', self.current_multi_group_A)
            widget.bind('<Tab>', self.current_multi_group_A)
            widget.bind('<KeyRelease>', self.current_multi_group_A)

        elif ch_tag_num == 2:
            widget.bind('<Return>', self.current_multi_group_B)
            widget.bind('<Tab>', self.current_multi_group_B)
            widget.bind('<KeyRelease>', self.current_multi_group_B)

        elif ch_tag_num == 3:
            widget.bind('<Return>', self.current_multi_group_C)
            widget.bind('<Tab>', self.current_multi_group_C)
            widget.bind('<KeyRelease>', self.current_multi_group_C)

        elif ch_tag_num == 4:
            widget.bind('<Return>', self.current_multi_group_D)
            widget.bind('<Tab>', self.current_multi_group_D)
            widget.bind('<KeyRelease>', self.current_multi_group_D)


    def widget_intensity_command(self, ch_tag_num, widget):
        if ch_tag_num == 1:
            widget.config(command = self.const_intensity_group_A)

        elif ch_tag_num == 2:
            widget.config(command = self.const_intensity_group_B)

        elif ch_tag_num == 3:
            widget.config(command = self.const_intensity_group_C)

        elif ch_tag_num == 4:
            widget.config(command = self.const_intensity_group_D)

    def spinbox_intensity_bind(self, ch_tag_num, widget):
        if ch_tag_num == 1:
            widget.bind('<Return>', self.const_intensity_group_A)
            widget.bind('<Tab>', self.const_intensity_group_A)
            widget.bind('<KeyRelease>', self.const_intensity_group_A)

        elif ch_tag_num == 2:
            widget.bind('<Return>', self.const_intensity_group_B)
            widget.bind('<Tab>', self.const_intensity_group_B)
            widget.bind('<KeyRelease>', self.const_intensity_group_B)

        elif ch_tag_num == 3:
            widget.bind('<Return>', self.const_intensity_group_C)
            widget.bind('<Tab>', self.const_intensity_group_C)
            widget.bind('<KeyRelease>', self.const_intensity_group_C)

        elif ch_tag_num == 4:
            widget.bind('<Return>', self.const_intensity_group_D)
            widget.bind('<Tab>', self.const_intensity_group_D)
            widget.bind('<KeyRelease>', self.const_intensity_group_D)


    def widget_strobe_command(self, ch_tag_num, widget):
        if ch_tag_num == 1:
            widget.config(command = self.strobe_param_group_A)

        elif ch_tag_num == 2:
            widget.config(command = self.strobe_param_group_B)

        elif ch_tag_num == 3:
            widget.config(command = self.strobe_param_group_C)

        elif ch_tag_num == 4:
            widget.config(command = self.strobe_param_group_D)

    def spinbox_strobe_bind(self, ch_tag_num, widget):
        if ch_tag_num == 1:
            widget.bind('<Return>', self.strobe_param_group_A)
            widget.bind('<Tab>', self.strobe_param_group_A)
            widget.bind('<KeyRelease>', self.strobe_param_group_A)

        elif ch_tag_num == 2:
            widget.bind('<Return>', self.strobe_param_group_B)
            widget.bind('<Tab>', self.strobe_param_group_B)
            widget.bind('<KeyRelease>', self.strobe_param_group_B)

        elif ch_tag_num == 3:
            widget.bind('<Return>', self.strobe_param_group_C)
            widget.bind('<Tab>', self.strobe_param_group_C)
            widget.bind('<KeyRelease>', self.strobe_param_group_C)

        elif ch_tag_num == 4:
            widget.bind('<Return>', self.strobe_param_group_D)
            widget.bind('<Tab>', self.strobe_param_group_D)
            widget.bind('<KeyRelease>', self.strobe_param_group_D)


    def widget_output_command(self, ch_tag_num, widget):
        if ch_tag_num == 1:
            widget.config(command = self.output_param_group_A)

        elif ch_tag_num == 2:
            widget.config(command = self.output_param_group_B)

        elif ch_tag_num == 3:
            widget.config(command = self.output_param_group_C)

        elif ch_tag_num == 4:
            widget.config(command = self.output_param_group_D)

    def spinbox_output_bind(self, ch_tag_num, widget):
        if ch_tag_num == 1:
            widget.bind('<Return>', self.output_param_group_A)
            widget.bind('<Tab>', self.output_param_group_A)
            widget.bind('<KeyRelease>', self.output_param_group_A)

        elif ch_tag_num == 2:
            widget.bind('<Return>', self.output_param_group_B)
            widget.bind('<Tab>', self.output_param_group_B)
            widget.bind('<KeyRelease>', self.output_param_group_B)

        elif ch_tag_num == 3:
            widget.bind('<Return>', self.output_param_group_C)
            widget.bind('<Tab>', self.output_param_group_C)
            widget.bind('<KeyRelease>', self.output_param_group_C)

        elif ch_tag_num == 4:
            widget.bind('<Return>', self.output_param_group_D)
            widget.bind('<Tab>', self.output_param_group_D)
            widget.bind('<KeyRelease>', self.output_param_group_D)


    def combobox_widget_bind(self, ch_tag_num, widget):
        if ch_tag_num == 1:
            widget.bind('<<ComboboxSelected>>', self.mode_select_group_A)

        elif ch_tag_num == 2:
            widget.bind('<<ComboboxSelected>>', self.mode_select_group_B)

        elif ch_tag_num == 3:
            widget.bind('<<ComboboxSelected>>', self.mode_select_group_C)

        elif ch_tag_num == 4:
            widget.bind('<<ComboboxSelected>>', self.mode_select_group_D)

    def strobe_button_command(self, ch_tag_num, widget):
        if ch_tag_num == 1 or ch_tag_num == 2 or ch_tag_num == 3 or ch_tag_num == 4:
            widget['command'] = lambda: self.strobe_button_ch1_4(ch_tag_num)

    
    def param_to_machine(self, ch_index, channel_save):
        if self.machine_param_type == 'current':
            self.ctrl.set_multiplier(ch_index, channel_save[0])

        elif self.machine_param_type == 'intensity':
            self.ctrl.set_const_intensity(ch_index, int(channel_save[1]))

        elif self.machine_param_type == 'strobe':
            self.ctrl.set_strobe_delay(ch_index, channel_save[2])
            self.ctrl.set_strobe_width(ch_index, channel_save[3])

        elif self.machine_param_type == 'output':
            self.ctrl.set_output_delay(ch_index, channel_save[4])
            self.ctrl.set_output_width(ch_index, channel_save[5])

        elif self.machine_param_type == 'mode':
            self.ctrl.set_mode(ch_index, channel_save[6])

        else:
            pass

    #group A (channel 1, 5, 9, 13)
    #group B (channel 2, 6, 10, 14)
    #group C (channel 3, 7, 11, 15)
    #group D (channel 4, 8, 12, 16)
    def current_multi_func(self, channel_save, scalevar_a):
        try:
            channel_save[0] = scalevar_a.get() #Current Multiplier
        except:
            pass
        #print(channel_save[0])

    def current_multi_group_A(self, event=None):
        self.machine_param_type = 'current'
        if self.ch_sel_str == '1 - 4':
            self.current_multi_func(self.channel_1_save, self.ch_1_scalevar_a)
            self.param_to_machine(1, self.channel_1_save)

    def current_multi_group_B(self, event=None):
        self.machine_param_type = 'current'
        if self.ch_sel_str== '1 - 4':
            self.current_multi_func(self.channel_2_save, self.ch_2_scalevar_a)
            self.param_to_machine(2, self.channel_2_save)

    def current_multi_group_C(self, event=None):
        self.machine_param_type = 'current'
        if self.ch_sel_str== '1 - 4':
            self.current_multi_func(self.channel_3_save, self.ch_3_scalevar_a)
            self.param_to_machine(3, self.channel_3_save)

    def current_multi_group_D(self, event=None):
        self.machine_param_type = 'current'
        if self.ch_sel_str== '1 - 4':
            self.current_multi_func(self.channel_4_save, self.ch_4_scalevar_a)
            self.param_to_machine(4, self.channel_4_save)

    def const_intensity_func(self, channel_save, scalevar_b):
        try:
            channel_save[1] = scalevar_b.get() #Intensity (0-255)
        except:
            pass
        #print(channel_save[1])

    def const_intensity_group_A(self, event=None):
        self.machine_param_type = 'intensity'

        if self.ch_sel_str == '1 - 4':
            self.const_intensity_func(self.channel_1_save, self.ch_1_scalevar_b)
            self.param_to_machine(1, self.channel_1_save)

    def const_intensity_group_B(self, event=None):
        self.machine_param_type = 'intensity'

        if self.ch_sel_str== '1 - 4':
            self.const_intensity_func(self.channel_2_save, self.ch_2_scalevar_b)
            self.param_to_machine(2, self.channel_2_save)

    def const_intensity_group_C(self, event=None):
        self.machine_param_type = 'intensity'

        if self.ch_sel_str== '1 - 4':
            self.const_intensity_func(self.channel_3_save, self.ch_3_scalevar_b)
            self.param_to_machine(3, self.channel_3_save)

    def const_intensity_group_D(self, event=None):
        self.machine_param_type = 'intensity'

        if self.ch_sel_str== '1 - 4':
            self.const_intensity_func(self.channel_4_save, self.ch_4_scalevar_b)
            self.param_to_machine(4, self.channel_4_save)
    
    
    def strobe_param_func(self, channel_save, ch_entry_c_label, ch_entry_d_label
        , scalevar_c, scalevar_d):
        try:
            channel_save[2] = scalevar_c.get() #Strobe Delay (0-9999)
        except:
            pass
        try:
            channel_save[3] = scalevar_d.get() #Strobe width (0-9999)
        except:
            pass
        ch_entry_c_label.set(str(np.divide(int(channel_save[2]), 100)) + ' ms')
        ch_entry_d_label.set(str(np.divide(int(channel_save[3]), 100)) + ' ms')

    def strobe_param_group_A(self, event=None):
        self.machine_param_type = 'strobe'

        if self.ch_sel_str== '1 - 4':
            self.strobe_param_func(self.channel_1_save, self.ch_1_entry_c_label, self.ch_1_entry_d_label, 
                self.ch_1_scalevar_c, self.ch_1_scalevar_d)
            self.param_to_machine(1, self.channel_1_save)

        # interval_spinbox_function()

    def strobe_param_group_B(self, event=None):
        self.machine_param_type = 'strobe'

        if self.ch_sel_str== '1 - 4':
            self.strobe_param_func(self.channel_2_save, self.ch_2_entry_c_label, self.ch_2_entry_d_label, 
                self.ch_2_scalevar_c, self.ch_2_scalevar_d)
            self.param_to_machine(2, self.channel_2_save)

        # interval_spinbox_function()

    def strobe_param_group_C(self, event=None):
        self.machine_param_type = 'strobe'

        if self.ch_sel_str== '1 - 4':
            self.strobe_param_func(self.channel_3_save, self.ch_3_entry_c_label, self.ch_3_entry_d_label,
                self.ch_3_scalevar_c, self.ch_3_scalevar_d)
            self.param_to_machine(3, self.channel_3_save)

        # interval_spinbox_function()

    def strobe_param_group_D(self, event=None):
        self.machine_param_type = 'strobe'

        if self.ch_sel_str== '1 - 4':
            self.strobe_param_func(self.channel_4_save, self.ch_4_entry_c_label, self.ch_4_entry_d_label,
                self.ch_4_scalevar_c, self.ch_4_scalevar_d)
            self.param_to_machine(4, self.channel_4_save)

        # interval_spinbox_function()

    def output_param_func(self, channel_save, ch_entry_e_label, ch_entry_f_label
        , scalevar_e, scalevar_f):
        try:
            channel_save[4] = scalevar_e.get() #Output Delay (0-9999)
        except:
            pass
        try:
            channel_save[5] = scalevar_f.get() #Output width (0-9999)
        except:
            pass

        ch_entry_e_label.set(str(np.divide(int(channel_save[4]), 100)) + ' ms')
        ch_entry_f_label.set(str(np.divide(int(channel_save[5]), 100)) + ' ms')
        #print(channel_save)

    def output_param_group_A(self, event=None):
        self.machine_param_type = 'output'

        if self.ch_sel_str== '1 - 4':
            self.output_param_func(self.channel_1_save, self.ch_1_entry_e_label, self.ch_1_entry_f_label,
                self.ch_1_scalevar_e, self.ch_1_scalevar_f)

            self.param_to_machine(1, self.channel_1_save)

    def output_param_group_B(self, event=None):
        self.machine_param_type = 'output'

        if self.ch_sel_str== '1 - 4':
            self.output_param_func(self.channel_2_save, self.ch_2_entry_e_label, self.ch_2_entry_f_label,
                self.ch_2_scalevar_e, self.ch_2_scalevar_f)

            self.param_to_machine(2, self.channel_2_save)

    def output_param_group_C(self, event=None):
        self.machine_param_type = 'output'

        if self.ch_sel_str== '1 - 4':
            self.output_param_func(self.channel_3_save, self.ch_3_entry_e_label, self.ch_3_entry_f_label,
                self.ch_3_scalevar_e, self.ch_3_scalevar_f)

            self.param_to_machine(3, self.channel_3_save)

    def output_param_group_D(self, event=None):
        self.machine_param_type = 'output'

        if self.ch_sel_str== '1 - 4':
            self.output_param_func(self.channel_4_save, self.ch_4_entry_e_label, self.ch_4_entry_f_label,
                self.ch_4_scalevar_e, self.ch_4_scalevar_f)

            self.param_to_machine(4, self.channel_4_save)


    def mode_function(self, ch_mode, channel_save):
        #global self.sq_trigger_btn

        if ch_mode.get() == 'Constant Mode':
            channel_save[6] = 0 #Mode (Constant = 0, Strobe = 1, Trigger = 2)

        elif ch_mode.get() == 'Strobe Mode':
            channel_save[6] = 1 #Mode (Constant = 0, Strobe = 1, Trigger = 2)

        elif ch_mode.get() == 'Trigger Mode': 
            channel_save[6] = 2 #Mode (Constant = 0, Strobe = 1, Trigger = 2)


    def mode_select_group_A(self,event=None): #group A (channel 1, 5, 9, 13)
        self.machine_param_type = 'mode'

        if self.ch_sel_str== '1 - 4':
            self.mode_function(self.ch_1_mode, self.channel_1_save)
            self.param_to_machine(1, self.channel_1_save)

        # interval_spinbox_function()

    def mode_select_group_B(self,event=None): #group B (channel 2, 6, 10, 14)
        self.machine_param_type = 'mode'

        if self.ch_sel_str== '1 - 4':
            self.mode_function(self.ch_2_mode, self.channel_2_save)
            self.param_to_machine(2, self.channel_2_save)

        # interval_spinbox_function()

    def mode_select_group_C(self,event=None): #group C (channel 3, 7, 11, 15)
        self.machine_param_type = 'mode'

        if self.ch_sel_str== '1 - 4':
            self.mode_function(self.ch_3_mode, self.channel_3_save)
            self.param_to_machine(3, self.channel_3_save)

        # interval_spinbox_function()

    def mode_select_group_D(self,event=None): #group D (channel 4, 8, 12, 16)
        self.machine_param_type = 'mode'

        if self.ch_sel_str== '1 - 4':
            self.mode_function(self.ch_4_mode, self.channel_4_save)
            self.param_to_machine(4, self.channel_4_save)


    def strobe_button_ch1_4(self, ch_tag_num):
        ch_set = ch_tag_num
        self.ctrl.strobe(ch_set)

    def strobe_channel_repeat(self):
        if self.channel_1_save[6] == 1 and self.strobe_ch_arr[0] == 1:
            self.ctrl.strobe(1)

        if self.channel_2_save[6] == 1 and self.strobe_ch_arr[1] == 1:
            self.ctrl.strobe(2)

        if self.channel_3_save[6] == 1 and self.strobe_ch_arr[2] == 1:
            self.ctrl.strobe(3)

        if self.channel_4_save[6] == 1 and self.strobe_ch_arr[3] == 1:
            self.ctrl.strobe(4)
        else:
            pass

    def strobe_channel_repeat_ALL(self):
        if self.channel_1_save[6] == 1:
            self.ctrl.strobe(1)

        if self.channel_2_save[6] == 1:
            self.ctrl.strobe(2)

        if self.channel_3_save[6] == 1:
            self.ctrl.strobe(3)

        if self.channel_4_save[6] == 1:
            self.ctrl.strobe(4)
        else:
            pass
            
    ###############################################################################################
    #5. REPEAT STROBE PARAMETERS
    def repeat_func(self, event_thread):
        if self.repeat_mode_str == 'infinity':
            while not event_thread.isSet():
                if event_thread.isSet():
                    break #Safety measure to break if while loop didn't break
                try:
                    self.strobe_channel_repeat()
                    event_thread.wait(self.interval_parameter)

                except:
                    continue
            print('loop break(infinite): Repeat')

        elif self.repeat_mode_str == 'finite':
            for i in range(int(self.repeat_number)):
                if event_thread.isSet():
                    break
                elif not event_thread.isSet():
                    try:
                        self.strobe_channel_repeat()
                        if i == int(self.repeat_number) - 1:
                            self.repeat_btn_click()
                        event_thread.wait(self.interval_parameter)

                    except:
                        if i == int(self.repeat_number) - 1:
                            self.repeat_btn_click()
                        continue

            print('loop break(finite): Repeat')
        else:
            pass

    def repeat_ALL_func(self, event_thread):
        if self.repeat_mode_str == 'infinity':
            while not event_thread.isSet():
                if event_thread.isSet():
                    break #Safety measure to break if while loop didn't break
                try:
                    self.strobe_channel_repeat_ALL()
                    event_thread.wait(self.interval_parameter)

                except:
                    continue
            print('loop break(infite): Repeat ALL')

        elif self.repeat_mode_str == 'finite':
            for i in range(int(self.repeat_number)):
                if event_thread.isSet():
                    break
                elif not event_thread.isSet():
                    try:
                        self.strobe_channel_repeat_ALL()
                        if i == int(self.repeat_number) - 1:
                            self.repeat_ALL_btn_click()
                        event_thread.wait(self.interval_parameter)

                    except:
                        if i == int(self.repeat_number) - 1:
                            self.repeat_ALL_btn_click()
                        continue

            print('loop break(finite): Repeat ALL')
        else:
            pass

    def repeat_start_stop(self, event = None):
        if (self.repeat_status == True):
            self.interval_spinbox_function()
            self.thread_event_repeat.clear()
            self.repeat_handle = threading.Thread(target= self.repeat_func, args = (self.thread_event_repeat,))
            self.repeat_handle.start()

            widget_disable(self.infinity_radio_btn, self.finite_radio_btn, self.interval_entry,
                self.infinity_radio_btn_2, self.finite_radio_btn_2, self.interval_entry_2)

            if self.repeat_mode_str == 'finite':
                widget_disable(self.repeat_number_spinbox, self.repeat_number_spinbox_2)

            try:
                widget_disable(self.sq_strobe_btn)
            except (AttributeError, tk.TclError):
                pass
            #print(self.repeat_handle)
        else:
            self.thread_event_repeat.set()
            try:
                Stop_thread(self.repeat_handle)
                print('Thread Stopped')
            except:
                pass

            widget_enable(self.infinity_radio_btn, self.finite_radio_btn, self.interval_entry,
                self.infinity_radio_btn_2, self.finite_radio_btn_2, self.interval_entry_2)

            if self.repeat_mode_str == 'finite':
                widget_enable(self.repeat_number_spinbox, self.repeat_number_spinbox_2)

            try:
                widget_enable(self.sq_strobe_btn)
            except (AttributeError, tk.TclError):
                pass
            #print(self.repeat_handle)

    def repeat_ALL_start_stop(self, event = None):
        if (self.repeat_ALL_status == True):
            self.interval_spinbox_function()
            self.thread_event_repeat_ALL.clear()
            self.repeat_ALL_handle = threading.Thread(target=self.repeat_ALL_func, args = (self.thread_event_repeat_ALL,))
            self.repeat_ALL_handle.start()

            widget_disable(self.infinity_radio_btn, self.finite_radio_btn, self.interval_entry,
                self.infinity_radio_btn_2, self.finite_radio_btn_2, self.interval_entry_2)

            if self.repeat_mode_str == 'finite':
                widget_disable(self.repeat_number_spinbox, self.repeat_number_spinbox_2)

            #print(repeat_ALL_handle)
        else:
            self.thread_event_repeat_ALL.set()
            try:
                Stop_thread(self.repeat_ALL_handle)
                print('Thread Stopped')
            except:
                pass

            widget_enable(self.infinity_radio_btn, self.finite_radio_btn, self.interval_entry,
                self.infinity_radio_btn_2, self.finite_radio_btn_2, self.interval_entry_2)

            if self.repeat_mode_str == 'finite':
                widget_enable(self.repeat_number_spinbox, self.repeat_number_spinbox_2)
            
            #print(self.repeat_ALL_handle)

    ###############################################################################################
    #6. RESET LIGHT PARAMETERS
    def reset_function(self, ch_arr, ch_index): #Functions used in RESET ALL which switches off all the lights as well
        self.ctrl.set_multiplier(ch_index, ch_arr[0])
        self.ctrl.set_const_intensity(ch_index, int(ch_arr[1]))
        self.ctrl.set_strobe_delay(ch_index, ch_arr[2])
        self.ctrl.set_strobe_width(ch_index, ch_arr[3])
        self.ctrl.set_output_delay(ch_index, ch_arr[4])
        self.ctrl.set_output_width(ch_index, ch_arr[5])
        self.ctrl.set_mode(ch_index, ch_arr[6])

    def reset_save_arr(self, ch_arr): #reset values Version 2 of save array for a Channel to default values
        ch_arr[0]=1
        ch_arr[1]=0
        ch_arr[2]=0
        ch_arr[3]=100
        ch_arr[4]=0
        ch_arr[5]=100
        ch_arr[6]=0

    def reset_all(self): #reset everything
        self.thread_reset_event.clear()

        self.reset_save_arr(self.channel_1_save)
        self.reset_save_arr(self.channel_2_save)
        self.reset_save_arr(self.channel_3_save)
        self.reset_save_arr(self.channel_4_save)

        #self.channel_on_select()
        try:
            if self.light_conn_status == True:
                self.reset_function(self.channel_1_save, 1)
                self.reset_function(self.channel_2_save, 2)
                self.reset_function(self.channel_3_save, 3)
                self.reset_function(self.channel_4_save, 4)

        except:
            pass
        self.thread_reset_event.set()

    ###############################################################################################
    #7. LOAD LIGHT PARAMETERS
    def load_parameter(self, event=None):
        self.thread_refresh_event.clear()

        self.addr_index_a = binary_to_dec_v2(self.addr_a[0], self.addr_a[1], self.addr_a[2], self.addr_a[3], reverse_str = True)

        try:
            self.ctrl.read_function(self.channel_1_save, 1)
            self.ctrl.read_function(self.channel_2_save, 2)
            self.ctrl.read_function(self.channel_3_save, 3)
            self.ctrl.read_function(self.channel_4_save, 4)
            
        except:
            #This Exception Handling is used to Break the Thread and the GUI update loop!
            pass
        #self.LC18_interface()
        self.thread_refresh_event.set()
    ###############################################################################################
    #8. STOP ALL THREADS
    def Stop_Threads(self):
        self.thread_event_repeat.set()
        try:
            Stop_thread(self.repeat_handle)
            print('Repeat Handle Thread Stopped')
        except:
            pass
        self.thread_event_repeat_ALL.set()
        try:
            Stop_thread(self.repeat_ALL_handle)
            print('Repeat All Handle Thread Stopped')
        except:
            pass

        try:
            Stop_thread(self.thread_refresh_handle)
        except:
            pass

        try:
            Stop_thread(self.thread_reset_handle)
        except:
            pass

        try:
            Stop_thread(self.sq_strobe_frame_handle)
        except:
            pass