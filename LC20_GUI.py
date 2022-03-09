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

import time

from intvalidate import int_validate

from ctrl_LC20_lib import LC20_Control

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

    elif only_positive == 'True':
        if d == '1':
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

#print(binary_to_dec_v2(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))
# print(len("{:04b}".format(65535)))

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

# test = np.zeros(16, dtype = np.uint8)
# print(dec_to_binary_arr_v2(65535))

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

class LC20_GUI(tk.Frame):
    def __init__(self, master, dll_LC20, light_conn_status, firmware_model_sel, firmware_version_str, infinity_icon
        , thread_event_repeat = None, thread_event_repeat_ALL = None, window_icon = None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        #INITIALIZE GUI INTERFACE MAIN PANEL(S) to hold the widgets
        self.master = master
        self.dll_LC20 = dll_LC20
        self.light_conn_status =  light_conn_status

        self.firmware_model_sel = firmware_model_sel
        #print('self.firmware_model_sel: ', self.firmware_model_sel)
        self.firmware_version_str = firmware_version_str
        self.infinity_icon = infinity_icon
        self.window_icon = window_icon

        self.thread_event_repeat = thread_event_repeat #Thread event used in Threading
        self.thread_event_repeat_ALL = thread_event_repeat_ALL #Thread event used in Threading
        self.repeat_ALL_handle = None

        #print('self.thread_event_repeat: ', self.thread_event_repeat)
        #print('self.thread_event_repeat_ALL: ', self.thread_event_repeat_ALL)
        #print('self.dll_LC20: ', self.dll_LC20)
        self.ctrl = LC20_Control(self.dll_LC20)

        self.sq_strobe_btn_click = False

        self.repeat_status = False
        self.repeat_ALL_status = False
        self.repeat_mode_str = 'infinity'#'infinity' or #'finite'
        self.repeat_number = 1

        self.machine_param_type = 'None'
        self.ch_sel_str = '1 - 4'

        arr_size = 4 #Array size for each Channels
        #arr_index: 0 = Current Multiplier, 1 = Intensity(0-255), 2 = Strobe Intensity(0-1023), 3 = Strobe Width(0-99999), 4 = Unused, 5 = Unused
        #arr_index: 6 = Unused, 7 = Unused, 8 = Channel ID number(0 - 16)
        self.channel_SQ_save = np.zeros((3),dtype=np.uint32) #Save SQ Channel Settings for SQ Controllers
        #index: 0 = Output Delay (0-99999), 1 = Output Width (0-99999), 2 = Channel Mode (Const, Strobe)
        self.channel_SQ_save[1] = 1000

        self.channel_1_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_2_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_3_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_4_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_5_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_6_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_7_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_8_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_9_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_10_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_11_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_12_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_13_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_14_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_15_save = np.zeros ((arr_size),dtype=np.uint32)
        self.channel_16_save = np.zeros ((arr_size),dtype=np.uint32)

        self.channel_1_save[3] = self.channel_2_save[3] = self.channel_3_save[3] = self.channel_4_save[3] = 100     #Strobe Width Default

        self.channel_5_save[3] = self.channel_6_save[3] = self.channel_7_save[3] = self.channel_8_save[3] = 100 

        self.channel_9_save[3] = self.channel_10_save[3] = self.channel_11_save[3] = self.channel_12_save[3] = 100 

        self.channel_13_save[3] = self.channel_14_save[3] = self.channel_15_save[3] = self.channel_16_save[3] = 100

        self.channel_1_save[0] = self.channel_2_save[0] = self.channel_3_save[0] = self.channel_4_save[0] = 1     #Current Multiplier Default

        self.channel_5_save[0] = self.channel_6_save[0] = self.channel_7_save[0] = self.channel_8_save[0] = 1 

        self.channel_9_save[0] = self.channel_10_save[0] = self.channel_11_save[0] = self.channel_12_save[0] = 1 

        self.channel_13_save[0] = self.channel_14_save[0] = self.channel_15_save[0] = self.channel_16_save[0] = 1


        self.strobe_ch_arr = np.zeros((16),dtype=np.uint8)

        self.addr_index_a = self.addr_index_b = self.addr_index_c = self.addr_index_d = 0
        self.addr_a = np.array([0, 0, 0, 0]) #board address ch 1-4 #each array values represents the switches in binary, 0 or 1. #0000
        self.addr_b = np.array([1, 0, 0, 0]) #board address ch 5-8 #each array values represents the switches in binary, 0 or 1. #0001
        self.addr_c = np.array([0, 1, 0, 0]) #board address ch 9-12 #each array values represents the switches in binary, 0 or 1. #0010
        self.addr_d = np.array([1, 1, 0, 0]) #board address ch 13-16 #each array values represents the switches in binary, 0 or 1. #0011

        

        self.sq_fr_arr = np.array([1,50000], dtype = np.uint32) #Frame Number #Frame Width
        self.sq_fr_int_arr = np.zeros((16),dtype=np.uint16) #Frame Int Value (base 10 from binary) #Each index represents the Frame no. (0-15)
        self.sq_f0_arr = np.zeros((16), dtype=np.uint8) #Array for storing binary values on Frame Values
        self.sq_f1_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f2_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f3_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f4_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f5_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f6_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f7_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f8_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f9_arr = np.zeros((16), dtype=np.uint8)

        self.sq_f10_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f11_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f12_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f13_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f14_arr = np.zeros((16), dtype=np.uint8)
        self.sq_f15_arr = np.zeros((16), dtype=np.uint8)

        self.interval_arr = np.array([0.5])
        self.interval_parameter = self.interval_arr[0]


        self.sq_frame_delay_event = threading.Event()

        self.loading_iteration = 0
        self.reset_progress_iteration = 0

        self.thread_refresh_event = threading.Event()

        self.thread_reset_event = threading.Event()

        self.GUI_refresh_handle = None
        
        self.GUI_reset_handle = None
        
        self.sq_frame_img_list = []
        self.updating_bool = None
        #Finalized function...
        self.load_btn_click()

        #DEBUG without loading parameters...
        #self.LC20_interface()
    
    def load_btn_click(self):
        self.updating_bool = True
        self.loading_frame = tk.Frame(self, bg = 'white') #width = 1500 - 330, height = 900
        self.loading_frame.place(relx=0, rely =0, relheight = 1, relwidth = 1, anchor = 'nw')

        self.loading_label = tk.Label(self.loading_frame, bg = 'white', font = 'Helvetica 20 bold')
        self.loading_label['text']= 'Loading...'
        #self.loading_label.place(relx=0.45, rely=0.3, anchor = 'center')
        self.loading_label.place(relx=0.35, rely=0.25, anchor = 'center')

        try:
            check_bool = tk.Toplevel.winfo_exists(self.sq_frame_toplvl)
            if check_bool == 0:
                pass
            else:
                self.loading_SQ_frame = tk.Frame(self.sq_frame_toplvl, bg = 'white')
                self.loading_SQ_frame.place(relx=0, rely =0, relheight = 1, relwidth = 1, anchor = 'nw')
                self.loading_SQ_label = tk.Label(self.loading_SQ_frame, bg = 'white', font = 'Helvetica 20 bold')
                self.loading_SQ_label['text']= 'Loading...'
                self.loading_SQ_label.place(relx=0.5, rely=0.5, anchor = 'center')
        except (AttributeError, tk.TclError):
            pass

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
            try:
                self.loading_SQ_label['text']= 'Loading'
            except:
                pass
        elif 6 < self.loading_iteration <= 12:
            self.loading_label['text'] = 'Loading.'
            try:
                self.loading_SQ_label['text']= 'Loading.'
            except:
                pass
        elif 12 < self.loading_iteration <= 18:
            self.loading_label['text'] = 'Loading..'
            try:
                self.loading_SQ_label['text']= 'Loading..'
            except:
                pass
        elif 18 < self.loading_iteration <= 24:
            self.loading_label['text'] = 'Loading...'
            try:
                self.loading_SQ_label['text']= 'Loading...'
            except:
                pass
        elif self.loading_iteration > 24:
            self.loading_iteration = 0

        if self.thread_refresh_event.isSet():
            self.after_cancel(self.GUI_refresh_handle)
            self.loading_frame.place_forget()

            try:
                self.loading_SQ_frame.place_forget()
            except:
                pass

            self.LC20_interface()

            try:
                #self.SQ_checkbox_update_widget()
                self.SQ_Frame_Popout_Update()
            except: #(AttributeError, tk.TclError):
                pass

            self.thread_refresh_event.clear()
            print('Update Complete!')
            self.updating_bool = False
            #print(self.thread_refresh_handle)
        #print(self.GUI_refresh_handle)
    

    def reset_btn_click(self):
        self.updating_bool = True
        self.reset_progress_frame = tk.Frame(self, width = 1500 - 330, height = 900, bg = 'white')
        self.reset_progress_frame.place(x=0, y =0, anchor = 'nw')

        self.reset_progress_label = tk.Label(self.reset_progress_frame, bg = 'white', font = 'Helvetica 20 bold')
        self.reset_progress_label['text']= 'Resetting...'
        #self.reset_progress_label.place(relx=0.45, rely=0.3, anchor = 'center')
        self.reset_progress_label.place(relx=0.35, rely=0.25, anchor = 'center')

        try:
            check_bool = tk.Toplevel.winfo_exists(self.sq_frame_toplvl)
            if check_bool == 0:
                pass
            else:
                self.reset_progress_SQ_frame = tk.Frame(self.sq_frame_toplvl, bg = 'white')
                self.reset_progress_SQ_frame.place(relx=0, rely =0, relheight = 1, relwidth = 1, anchor = 'nw')
                self.reset_progress_SQ_label = tk.Label(self.reset_progress_SQ_frame, bg = 'white', font = 'Helvetica 20 bold')
                self.reset_progress_SQ_label['text']= 'Resetting...'
                self.reset_progress_SQ_label.place(relx=0.5, rely=0.5, anchor = 'center')
        except (AttributeError, tk.TclError):
            pass

        if self.repeat_ALL_btn['text'] == 'STOP':
            self.repeat_ALL_status = False
            self.repeat_ALL_btn = self.repeat_btn_widget(self.repeat_ALL_status, self.repeat_ALL_btn)
            self.repeat_ALL_start_stop()

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
            try:
                self.reset_progress_SQ_label['text']= 'Resetting'
            except:
                pass
        elif 6 < self.reset_progress_iteration <= 12:
            self.reset_progress_label['text'] = 'Resetting.'
            try:
                self.reset_progress_SQ_label['text']= 'Resetting.'
            except:
                pass

        elif 12 < self.reset_progress_iteration <= 18:
            self.reset_progress_label['text'] = 'Resetting..'
            try:
                self.reset_progress_SQ_label['text']= 'Resetting..'
            except:
                pass

        elif 18 < self.reset_progress_iteration <= 24:
            self.reset_progress_label['text'] = 'Resetting...'
            try:
                self.reset_progress_SQ_label['text']= 'Resetting...'
            except:
                pass

        elif self.reset_progress_iteration > 24:
            self.reset_progress_iteration = 0

        if self.thread_reset_event.isSet():
            self.after_cancel(self.GUI_reset_handle)
            self.reset_progress_frame.place_forget()
            try:
                self.reset_progress_SQ_frame.place_forget()
            except:
                pass

            self.channel_on_select()
            try:
                #self.SQ_checkbox_update_widget()
                self.SQ_Frame_Popout_Update()
            except: #(AttributeError, tk.TclError):
                pass
            self.thread_reset_event.clear()
            #print('Reset Complete!')
            self.updating_bool = False
            #print(self.thread_reset_handle)

        #print(self.GUI_reset_handle)

    ###############################################################################################
    #1. MAIN INTERFACE
    def LC20_interface(self):
        #MAIN PANEL GENERATION
        #frame_panel_1 long vertical panel anchored at top-left

        w_fr1 = 137 #180
        h_fr1 = 800

        try:
            if self.frame_panel_1.winfo_exists() == 1:
                for widget in self.frame_panel_1.winfo_children():
                    widget.destroy()
                self.frame_panel_1.destroy()
        except AttributeError:
            pass

        self.frame_panel_1 = tk.Frame(self, width = w_fr1, height = h_fr1, highlightcolor = 'white', highlightthickness = 1, bg='DarkSlateGray2')
        self.frame_panel_1.place(x=0,y=0, relheight = 1)
        

        self.ch_sel_btn1 = tk.Button(self, relief = tk.GROOVE, text = 'Channel 1 - 4', width = 12, font='Helvetica 11 bold')
        self.ch_sel_btn2 = tk.Button(self, relief = tk.GROOVE, text = 'Channel 5 - 8', width = 12, font='Helvetica 11 bold')
        self.ch_sel_btn3 = tk.Button(self, relief = tk.GROOVE, text = 'Channel 9 - 12', width = 12, font='Helvetica 11 bold')
        self.ch_sel_btn4 = tk.Button(self, relief = tk.GROOVE, text = 'Channel 13 - 16', width = 12, font='Helvetica 11 bold')

        self.ch_sel_btn1['command'] = self.ch_sel_1_4
        self.ch_sel_btn2['command'] = self.ch_sel_5_8
        self.ch_sel_btn3['command'] = self.ch_sel_9_12
        self.ch_sel_btn4['command'] = self.ch_sel_13_16

        self.ch_sel_btn1.place(x=0 + 139,y=0)
        self.ch_sel_btn2.place(x=120 + 139,y=0)
        self.ch_sel_btn3.place(x=240 + 139,y=0)
        self.ch_sel_btn4.place(x=360 + 139,y=0)

        self.main_control_gen()

        self.label_interval_var = tk.StringVar()
        self.interval_var = tk.StringVar()
        self.repeat_mode_var = tk.StringVar()
        self.repeat_number_var = tk.StringVar()

        self.repeat_ALL_control_gen()

        widget_bind_focus(self.repeat_ALL_btn)
        widget_bind_focus(self.infinity_radio_btn_2)
        widget_bind_focus(self.finite_radio_btn_2)
        widget_bind_focus(self.repeat_number_spinbox_2)

        if self.ch_sel_str == '1 - 4':
           self.ch_sel_1_4()
        elif self.ch_sel_str == '5 - 8':
            self.ch_sel_5_8()
        elif self.ch_sel_str == '9 - 12':
            self.ch_sel_9_12()
        elif self.ch_sel_str == '13 - 16':
            self.ch_sel_13_16()
           
    def main_control_gen(self):
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

        self.RESET_ALL_button = tk.Button(self.main_control_frame, width = 10, relief = tk.GROOVE, activeforeground= 'white', fg="white", activebackground = 'navy', bg = 'royal blue'
              , text='RESET ALL', font = "Helvetica 11 bold")
        self.RESET_ALL_button['command'] = self.reset_btn_click
        self.RESET_ALL_button.place(x= 5, y = 160)

    def repeat_ALL_control_gen(self):
        self.repeat_ALL_frame = tk.Frame(self.frame_panel_1, bg = 'DarkSlateGray2', highlightbackground="white", highlightthickness=1, highlightcolor="white")
        self.repeat_ALL_frame['width'] = 120 + 5 #168
        self.repeat_ALL_frame['height'] = 235

        self.repeat_ALL_frame.place(x=5, y=350)

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

    def repeat_ALL_btn_click(self, event = None):
        if self.repeat_ALL_btn['text'] == 'START':
            self.repeat_ALL_status = True

        elif self.repeat_ALL_btn['text'] == 'STOP':
            self.repeat_ALL_status = False

        self.repeat_ALL_btn = self.repeat_btn_widget(self.repeat_ALL_status, self.repeat_ALL_btn)
        self.repeat_ALL_start_stop()

    def repeat_mode_set(self, event=None):
        self.repeat_mode_str = self.repeat_mode_var.get()
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
                self.interval_var.set(0.5)
                self.interval_parameter = 0.5

            elif self.interval_parameter > 9999:
                self.interval_var.set(9999.0)
                self.interval_parameter = 9999.0
        except:
            self.interval_var.set(self.interval_arr[0])
            pass

        self.interval_parameter = round(self.interval_parameter, 3)
        self.interval_arr[0] = self.interval_parameter
        self.label_interval_var.set(str(self.interval_parameter) + ' seconds') #displays the interval time in milliseconds
        self.interval_var.set(self.interval_parameter)
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
        self.ch_sel_btn_state(self.ch_sel_btn1, self.ch_sel_btn2, self.ch_sel_btn3, self.ch_sel_btn4)
        self.channel_on_select()
    def ch_sel_5_8(self):
        self.ch_sel_str = '5 - 8'
        self.ch_sel_btn_state(self.ch_sel_btn2, self.ch_sel_btn1, self.ch_sel_btn3, self.ch_sel_btn4)
        self.channel_on_select()
    def ch_sel_9_12(self):
        self.ch_sel_str = '9 - 12'
        self.ch_sel_btn_state(self.ch_sel_btn3, self.ch_sel_btn1, self.ch_sel_btn2, self.ch_sel_btn4)
        self.channel_on_select()
    def ch_sel_13_16(self):
        self.ch_sel_str = '13 - 16'
        self.ch_sel_btn_state(self.ch_sel_btn4, self.ch_sel_btn1, self.ch_sel_btn2, self.ch_sel_btn3)
        self.channel_on_select()

    def channel_setting_GUI(self):
        w_fr5 = 920 + 60
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
        self.frame_panel_5.place(x=139,y=150 - 150 + 32)

        ##################################################################################################################################################################################
        self.sq_fr_ctrl_frame = tk.Frame(self.frame_panel_1, width = 168, height = 115, bg = 'DarkSlateGray2', highlightbackground="white", highlightthickness=1, highlightcolor="white")
        self.sq_fr_ctrl_frame['width'] = 120 + 5#168
        self.sq_fr_ctrl_frame['height'] = 115
        self.sq_fr_ctrl_frame.place(x=5, y=220)
        tk.Label(self.sq_fr_ctrl_frame, text = 'Frame Settings', font = 'Helvetica 12 bold', bg = 'DarkSlateGray2').place(x=0, y=0)

        self.sq_fr_ctrl_btn = tk.Button(self.sq_fr_ctrl_frame, relief = tk.GROOVE, text = 'SQ Frame\nControl Panel', font = 'Helvetica 11', justify = 'center')
        #self.sq_fr_ctrl_btn.place(x=10, y=230)
        self.sq_fr_ctrl_btn.place(x=5, y=35)
        self.sq_fr_ctrl_btn['command'] = self.SQ_frame_popout
        #################################################################################################################################################################################

        self.channel_setting_frame = tk.Frame(self.frame_panel_5, width = 450 + 30, height = 130, highlightbackground="black", highlightthickness=1)
        self.channel_setting_frame.place(x= 230 + 15, y = 5)
        tk_ch_setting = tk.Label(self.channel_setting_frame, text = 'Channel Settings', font = 'Helvetica 13 bold')
        tk_ch_setting.place(x= 5, y = 0)

        tk_output_delay_1 = tk.Label(self.channel_setting_frame, text = 'Output Delay\n(0-99999)', font = 'Helvetica 11', width = 12)
        self.sq_output_delay_scalevar = tk.IntVar(value = self.channel_SQ_save[0])
        self.sq_output_delay_entry = tk.Spinbox(master = self.channel_setting_frame, width = 5, textvariable = self.sq_output_delay_scalevar, from_=0, to= 99999, increment = 1
                              , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        self.sq_output_delay_entry['validate']='key'
        self.sq_output_delay_entry['vcmd']=(self.sq_output_delay_entry.register(validate_int_entry),'%d','%P','%S', True)
        
        self.sq_output_delay_scalebar= tk.Scale(self.channel_setting_frame, from_=0, to=99999, variable = self.sq_output_delay_scalevar, orient='horizontal', showvalue=0) 
        self.sq_output_delay_label = tk.StringVar()
        tk_output_delay_2 = tk.Label(self.channel_setting_frame, textvariable = self.sq_output_delay_label,  font = 'Helvetica 11 italic')
        self.sq_output_delay_label.set(str(np.divide(int(self.channel_SQ_save[0]), 100)) + ' ms')

        self.widget_output_delay_command(self.sq_output_delay_scalebar)
        self.spinbox_output_delay_bind(self.sq_output_delay_entry)
        self.widget_output_delay_command(self.sq_output_delay_entry)

        self.sq_output_delay_entry.bind('<FocusOut>', lambda event: focusout_func(widget=self.sq_output_delay_entry, val=self.channel_SQ_save[0]))
        widget_bind_focus(self.sq_output_delay_entry)
        widget_bind_focus(self.sq_output_delay_scalebar)
        
        tk_output_delay_1.place(x= 110+30+15, y = 20)
        self.sq_output_delay_scalebar.place(x= 230+30+15,y=20)
        tk_output_delay_2.place(x= 340+30+15-5, y = 20 + 23)
        self.sq_output_delay_entry.place(x= 340+30+15, y = 20)


        tk_output_width_1 = tk.Label(self.channel_setting_frame, text = 'Output Width\n(0-99999)', font = 'Helvetica 11', width = 12)
        self.sq_output_width_scalevar = tk.IntVar(value = self.channel_SQ_save[1])
        self.sq_output_width_entry = tk.Spinbox(master = self.channel_setting_frame, width = 5, textvariable = self.sq_output_width_scalevar, from_=0, to= 99999, increment = 1
                              , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        self.sq_output_width_entry['validate']='key'
        self.sq_output_width_entry['vcmd']=(self.sq_output_width_entry.register(validate_int_entry),'%d','%P','%S', True)
        
        self.sq_output_width_scalebar= tk.Scale(self.channel_setting_frame, from_=0, to=99999, variable = self.sq_output_width_scalevar, orient='horizontal', showvalue=0) 
        self.sq_output_width_label = tk.StringVar()
        tk_output_width_2 = tk.Label(self.channel_setting_frame, textvariable = self.sq_output_width_label,  font = 'Helvetica 11 italic')
        self.sq_output_width_label.set(str(np.divide(int(self.channel_SQ_save[1]), 100)) + ' ms')

        self.widget_output_width_command(self.sq_output_width_scalebar)
        self.spinbox_output_width_bind(self.sq_output_width_entry)
        self.widget_output_width_command(self.sq_output_width_entry)

        self.sq_output_width_entry.bind('<FocusOut>', lambda event: focusout_func(widget=self.sq_output_width_entry, val=self.channel_SQ_save[1]))
        widget_bind_focus(self.sq_output_width_entry)
        widget_bind_focus(self.sq_output_width_scalebar)
        
        tk_output_width_1.place(x= 110+30+15, y = 70)
        self.sq_output_width_scalebar.place(x= 230+30+15,y=70)
        tk_output_width_2.place(x= 340+30+15-5, y = 70 + 23)
        self.sq_output_width_entry.place(x= 340+30+15, y = 70)

        tk.Label(self.channel_setting_frame, text = 'Select Mode: ', font = 'Helvetica 12 italic', width = 12).place(x=10, y=30)
        mode_list = ['Constant Mode', 'Strobe Mode']
        self.channel_setting_frame.option_add('*TCombobox*Listbox.font', ('Helvetica', '11'))
        self.sq_ch_mode = ttk.Combobox(self.channel_setting_frame, values = mode_list, width=13, state='readonly', font = 'Helvetica 11')
        self.sq_ch_mode.place(x= 10, y = 55)
        self.combobox_widget_bind(self.sq_ch_mode)
        
        if self.channel_SQ_save[2] == 0:
            self.sq_ch_mode.current(0)
        elif self.channel_SQ_save[2] == 1:
            self.sq_ch_mode.current(1)

        self.sq_ch_mode.unbind_class("TCombobox", "<MouseWheel>")

    def channel_on_select(self):
        self.channel_setting_GUI()

        self.sq_output_delay_scalebar.set(int(self.channel_SQ_save[0]))
        self.sq_output_delay_label.set(str(np.divide(int(self.channel_SQ_save[0]), 100)) + ' ms')

        self.sq_output_width_scalebar.set(int(self.channel_SQ_save[1]))
        self.sq_output_width_label.set(str(np.divide(int(self.channel_SQ_save[1]), 100)) + ' ms')

        #print(self.channel_SQ_save)
        if self.channel_SQ_save[2] == 0:
            #print('channel on select MODE: Constant')
            self.sq_ch_mode.current(0)
        elif self.channel_SQ_save[2] == 1:
            #print('channel on select MODE: Strobe')
            self.sq_ch_mode.current(1)

        if self.ch_sel_str == '1 - 4':
            # self.board_address()
            # self.channel_1_save[7] = self.channel_2_save[7] = self.channel_3_save[7] = self.channel_4_save[7] = self.addr_index_a

            self.channel_frame_1 = self.generate_ch_frame(self.frame_panel_5, 1)
            (self.ch_1_entry_d_label,
                self.ch_1_scalevar_a, self.ch_1_scalevar_b, self.ch_1_scalevar_c, self.ch_1_scalevar_d) = self.generate_panel(self.channel_frame_1,'Channel 1', 1, self.channel_1_save)

            self.channel_frame_2 = self.generate_ch_frame(self.frame_panel_5, 2)
            (self.ch_2_entry_d_label,
                self.ch_2_scalevar_a, self.ch_2_scalevar_b, self.ch_2_scalevar_c, self.ch_2_scalevar_d) = self.generate_panel(self.channel_frame_2,'Channel 2', 2, self.channel_2_save)

            self.channel_frame_3 = self.generate_ch_frame(self.frame_panel_5, 3)
            (self.ch_3_entry_d_label, 
                self.ch_3_scalevar_a, self.ch_3_scalevar_b, self.ch_3_scalevar_c, self.ch_3_scalevar_d) = self.generate_panel(self.channel_frame_3,'Channel 3', 3, self.channel_3_save)

            self.channel_frame_4 = self.generate_ch_frame(self.frame_panel_5, 4)
            (self.ch_4_entry_d_label,
                self.ch_4_scalevar_a, self.ch_4_scalevar_b, self.ch_4_scalevar_c, self.ch_4_scalevar_d) = self.generate_panel(self.channel_frame_4,'Channel 4', 4, self.channel_4_save)

        elif self.ch_sel_str == '5 - 8':
            # self.board_address()
            # self.channel_5_save[7] = self.channel_6_save[7] = self.channel_7_save[7] = self.channel_8_save[7] = self.addr_index_b

            self.channel_frame_5 = self.generate_ch_frame(self.frame_panel_5, 5)
            (self.ch_5_entry_d_label,
                self.ch_5_scalevar_a, self.ch_5_scalevar_b, self.ch_5_scalevar_c, self.ch_5_scalevar_d) = self.generate_panel(self.channel_frame_5,'Channel 5', 5, self.channel_5_save)

            self.channel_frame_6 = self.generate_ch_frame(self.frame_panel_5, 6)
            (self.ch_6_entry_d_label,
                self.ch_6_scalevar_a, self.ch_6_scalevar_b, self.ch_6_scalevar_c, self.ch_6_scalevar_d) = self.generate_panel(self.channel_frame_6,'Channel 6', 6, self.channel_6_save)

            self.channel_frame_7 = self.generate_ch_frame(self.frame_panel_5, 7)
            (self.ch_7_entry_d_label,
                self.ch_7_scalevar_a, self.ch_7_scalevar_b, self.ch_7_scalevar_c, self.ch_7_scalevar_d) = self.generate_panel(self.channel_frame_7,'Channel 7', 7, self.channel_7_save)

            self.channel_frame_8 = self.generate_ch_frame(self.frame_panel_5, 8)
            (self.ch_8_entry_d_label,
                self.ch_8_scalevar_a, self.ch_8_scalevar_b, self.ch_8_scalevar_c, self.ch_8_scalevar_d) = self.generate_panel(self.channel_frame_8,'Channel 8', 8, self.channel_8_save)

            pass

        elif self.ch_sel_str == '9 - 12':
            # self.board_address()
            # self.channel_9_save[7] = self.channel_10_save[7] = self.channel_11_save[7] = self.channel_12_save[7] = self.addr_index_c

            self.channel_frame_9 = self.generate_ch_frame(self.frame_panel_5, 9)
            (self.ch_9_entry_d_label,
                self.ch_9_scalevar_a, self.ch_9_scalevar_b, self.ch_9_scalevar_c, self.ch_9_scalevar_d) = self.generate_panel(self.channel_frame_9,'Channel 9', 9, self.channel_9_save)

            self.channel_frame_10 = self.generate_ch_frame(self.frame_panel_5, 10)
            (self.ch_10_entry_d_label,
                self.ch_10_scalevar_a, self.ch_10_scalevar_b, self.ch_10_scalevar_c, self.ch_10_scalevar_d) = self.generate_panel(self.channel_frame_10,'Channel 10', 10, self.channel_10_save)

            self.channel_frame_11 = self.generate_ch_frame(self.frame_panel_5, 11)
            (self.ch_11_entry_d_label,
                self.ch_11_scalevar_a, self.ch_11_scalevar_b, self.ch_11_scalevar_c, self.ch_11_scalevar_d) = self.generate_panel(self.channel_frame_11,'Channel 11', 11, self.channel_11_save)

            self.channel_frame_12 = self.generate_ch_frame(self.frame_panel_5, 12)
            (self.ch_12_entry_d_label,
                self.ch_12_scalevar_a, self.ch_12_scalevar_b, self.ch_12_scalevar_c, self.ch_12_scalevar_d) = self.generate_panel(self.channel_frame_12,'Channel 12', 12, self.channel_12_save)

            pass
        elif self.ch_sel_str == '13 - 16':
            # self.board_address()
            # self.channel_13_save[7] = self.channel_14_save[7] = self.channel_15_save[7] = self.channel_16_save[7] = self.addr_index_d

            self.channel_frame_13 = self.generate_ch_frame(self.frame_panel_5, 13)
            (self.ch_13_entry_d_label,
                self.ch_13_scalevar_a, self.ch_13_scalevar_b, self.ch_13_scalevar_c, self.ch_13_scalevar_d) = self.generate_panel(self.channel_frame_13,'Channel 13', 13, self.channel_13_save)

            self.channel_frame_14 = self.generate_ch_frame(self.frame_panel_5, 14)
            (self.ch_14_entry_d_label,
                self.ch_14_scalevar_a, self.ch_14_scalevar_b, self.ch_14_scalevar_c, self.ch_14_scalevar_d) = self.generate_panel(self.channel_frame_14,'Channel 14', 14, self.channel_14_save)

            self.channel_frame_15 = self.generate_ch_frame(self.frame_panel_5, 15)
            (self.ch_15_entry_d_label,
                self.ch_15_scalevar_a, self.ch_15_scalevar_b, self.ch_15_scalevar_c, self.ch_15_scalevar_d) = self.generate_panel(self.channel_frame_15,'Channel 15', 15, self.channel_15_save)

            self.channel_frame_16 = self.generate_ch_frame(self.frame_panel_5, 16)
            (self.ch_16_entry_d_label,
                self.ch_16_scalevar_a, self.ch_16_scalevar_b, self.ch_16_scalevar_c, self.ch_16_scalevar_d) = self.generate_panel(self.channel_frame_16,'Channel 16', 16, self.channel_16_save)
            pass
            
    def generate_ch_frame(self, tk_frame, ch_tag_num):
        W = 450 + 30
        H = 315 - 135
        if ch_tag_num == 1 or ch_tag_num == 5 or ch_tag_num == 9 or ch_tag_num == 13:
            channel_frame = tk.Frame(tk_frame, width = W, height = H, highlightbackground="black", highlightthickness=1)
            #channel_frame.place(x= 0, y = 210)
            channel_frame.place(x= 5, y = 5 + 135)

        elif ch_tag_num == 2 or ch_tag_num == 6 or ch_tag_num == 10 or ch_tag_num == 14:
            channel_frame = tk.Frame(tk_frame, width = W, height = H, highlightbackground="black", highlightthickness=1)
            #channel_frame.place(x= 185, y = 210)
            channel_frame.place(x= 460 + 30, y = 5 + 135)

        elif ch_tag_num == 3 or ch_tag_num == 7 or ch_tag_num == 11 or ch_tag_num == 15:
            channel_frame = tk.Frame(tk_frame, width = W, height = H, highlightbackground="black", highlightthickness=1)
            #channel_frame.place(x= 370, y = 210)
            channel_frame.place(x= 5, y = 325)

        elif ch_tag_num == 4 or ch_tag_num == 8 or ch_tag_num == 12 or ch_tag_num == 16:
            channel_frame = tk.Frame(tk_frame, width = W, height = H, highlightbackground="black", highlightthickness=1)
            #channel_frame.place(x= 555, y = 210)
            channel_frame.place(x= 460 +30, y = 325)
        return channel_frame

    def generate_panel(self, channel_frame, channel_name, ch_tag_num, channel_save):
        x_pos1 = 110+30+15 - 80
        x_pos2 = 230+30+15 - 80
        x_pos3 = 340+30+15

        channel_label = tk.Label(channel_frame, text = channel_name, font = 'Helvetica 13 bold')
        channel_label.place(x= 15, y = 0)
        
        #####################################################################################################################
        ch_label_a = tk.Label(channel_frame, text = 'Current Multiplier', font = 'Helvetica 11', width = 12)
        scalevar_a = tk.IntVar(value = channel_save[0])
        ch_entry_a = tk.Spinbox(master = channel_frame, width = 5, textvariable = scalevar_a,from_=1, to=10
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        ch_entry_a['validate']='key'
        ch_entry_a['vcmd']=(ch_entry_a.register(validate_int_entry),'%d','%P','%S', True)

        ch_scalebar_a = tk.Scale(channel_frame, from_=1, to=10, variable=scalevar_a, orient='horizontal', showvalue=0, length = 170)

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
        ch_entry_b = tk.Spinbox(master = channel_frame, width = 5, textvariable = scalevar_b,from_=0, to=255
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        ch_entry_b['validate']='key'
        ch_entry_b['vcmd']=(ch_entry_b.register(validate_int_entry),'%d','%P','%S', True)
        ch_scalebar_b = tk.Scale(channel_frame, from_=0, to=255, variable=scalevar_b, orient='horizontal', showvalue=0, length = 170)

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
        ch_label_c = tk.Label(channel_frame, text = 'Strobe Intensity\n(0-1023)', font = 'Helvetica 11', width = 12)
        scalevar_c = tk.IntVar(value = channel_save[2])
        ch_entry_c = tk.Spinbox(master = channel_frame, width = 5, textvariable = scalevar_c, from_=0, to= 1023, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        ch_entry_c['validate']='key'
        ch_entry_c['vcmd']=(ch_entry_c.register(validate_int_entry),'%d','%P','%S', True)
        ch_scalebar_c = tk.Scale(channel_frame, from_=0, to=1023, variable=scalevar_c, orient='horizontal', showvalue=0, length = 170)

        self.widget_strobe_command(ch_tag_num, ch_entry_c)
        self.spinbox_strobe_bind(ch_tag_num, ch_entry_c)
        self.widget_strobe_command(ch_tag_num, ch_scalebar_c)
        ch_entry_c.bind('<FocusOut>', lambda event: focusout_func(widget=ch_entry_c, val=channel_save[2]))
        widget_bind_focus(ch_entry_c)
        widget_bind_focus(ch_scalebar_c)

        ch_label_c.place(x= x_pos1, y = 80)
        ch_scalebar_c.place(x=x_pos2,y=80)
        ch_entry_c.place(x= x_pos3, y = 80)

        #####################################################################################################################
        ch_label_d = tk.Label(channel_frame, text = 'Strobe Width\n(0-99999)', font = 'Helvetica 11', width = 12)
        scalevar_d = tk.IntVar(value = channel_save[3])
        ch_entry_d = tk.Spinbox(master = channel_frame, width = 5, textvariable = scalevar_d, from_=0, to= 99999, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        ch_entry_d['validate']='key'
        ch_entry_d['vcmd']=(ch_entry_d.register(validate_int_entry),'%d','%P','%S', True)

        ch_scalebar_d = tk.Scale(channel_frame, from_=0, to=99999, variable=scalevar_d, orient='horizontal', showvalue=0, length = 170)

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

        return (ch_entry_d_label,
            scalevar_a, scalevar_b, scalevar_c, scalevar_d)
        
    ###############################################################################################
    

    ###############################################################################################
    #4. CONTROL PANEL INTERFACE 3 (SQ)
    def SQ_frame_popout(self):
        toplvl_width = 730 +200
        toplvl_height = 250 + 360
        try:
            #print('try')
            check_bool = tk.Toplevel.winfo_exists(self.sq_frame_toplvl)
            if check_bool == 0:
                #print('not exist')
                self.sq_frame_toplvl = tk.Toplevel(master= self, width = toplvl_width, height = toplvl_height)
                self.sq_frame_toplvl.resizable(False, False)
                self.sq_frame_toplvl['bg'] = 'white'
                self.sq_frame_toplvl.title('LC20-SQ Frame')
                screen_width = self.sq_frame_toplvl.winfo_screenwidth()
                screen_height = self.sq_frame_toplvl.winfo_screenheight()
                x_coordinate = int((screen_width/2) - (toplvl_width/2))
                y_coordinate = int((screen_height/2) - (toplvl_height/2))
                self.sq_frame_toplvl.geometry("{}x{}+{}+{}".format(toplvl_width, toplvl_height, x_coordinate, y_coordinate))

                try:
                    self.sq_frame_toplvl.iconphoto(False, self.window_icon)
                except Exception:
                    pass

                self.SQ_frame_popout_init()
            else:
                #print('exist')
                self.sq_frame_toplvl.deiconify()
                self.sq_frame_toplvl.lift()
                pass
        except AttributeError:
            #print('except')
            self.sq_frame_toplvl = tk.Toplevel(master= self, width = toplvl_width, height = toplvl_height) #TKINTER GENERATION CANNOT WORK WITH THREAD
            self.sq_frame_toplvl.resizable(False, False)
            self.sq_frame_toplvl['bg'] = 'white'
            self.sq_frame_toplvl.title('LC20-SQ Frame')
            screen_width = self.sq_frame_toplvl.winfo_screenwidth()
            screen_height = self.sq_frame_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (toplvl_width/2))
            y_coordinate = int((screen_height/2) - (toplvl_height/2))
            self.sq_frame_toplvl.geometry("{}x{}+{}+{}".format(toplvl_width, toplvl_height, x_coordinate, y_coordinate))

            try:
                self.sq_frame_toplvl.iconphoto(False, self.window_icon)
            except Exception:
                pass

            self.SQ_frame_popout_init()

        

    def SQ_frame_popout_init(self):
        (self.sq_fr_main_frame, self.sq_fr_btn_group_frame, self.sq_checkbox_group_frame, 
            self.sq_fr_num_combobox, self.sq_fr_width_spinbox, self.sq_set_fr_btn, self.sq_strobe_btn) = self.SQ_panel_gen(self.sq_frame_toplvl)

        #self.sq_fr_main_frame.place(x = 270, y = 805)
        self.sq_fr_main_frame.place(x=0,y=0)

        self.sq_fr_width_spinbox['command'] = self.SQ_frame_width_get
        self.sq_set_fr_btn['command'] = self.SQ_set_frame
        widget_bind_focus(self.sq_set_fr_btn)

        self.sq_strobe_btn['command'] = self.SQ_strobe_frame #self.SQ_strobe_frame_thread #self.SQ_strobe_frame
        widget_bind_focus(self.sq_strobe_btn)


        self.sq_fr_num_combobox.bind('<<ComboboxSelected>>', self.SQ_frame_num_get)

        self.sq_fr_width_spinbox.bind('<Return>',self.SQ_frame_width_get)
        self.sq_fr_width_spinbox.bind('<Tab>',self.SQ_frame_width_get)
        self.sq_fr_width_spinbox.bind('<KeyRelease>',self.SQ_frame_width_get)
        self.sq_fr_width_spinbox.bind('<FocusOut>', lambda event: focusout_func(widget=self.sq_fr_width_spinbox, val=self.sq_fr_arr[1]))
        
        self.sq_fr_width_spinbox.bind('<KeyPress>',self.SQ_frame_width_keypress)

        self.sq_fr_width_spinbox['validate']='key'
        self.sq_fr_width_spinbox['vcmd']=(self.sq_fr_width_spinbox.register(validate_int_entry),'%d','%P','%S', True)

        self.sq_checkbox_frame_0 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 1)
        self.sq_checkbox_frame_1 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 2)
        self.sq_checkbox_frame_2 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 3)
        self.sq_checkbox_frame_3 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 4)
        self.sq_checkbox_frame_4 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 5)
        self.sq_checkbox_frame_5 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 6)
        self.sq_checkbox_frame_6 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 7)
        self.sq_checkbox_frame_7 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 8)
        self.sq_checkbox_frame_8 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 9)
        self.sq_checkbox_frame_9 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 10)

        self.sq_checkbox_frame_10 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 11)
        self.sq_checkbox_frame_11 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 12)
        self.sq_checkbox_frame_12 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 13)
        self.sq_checkbox_frame_13 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 14)
        self.sq_checkbox_frame_14 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 15)
        self.sq_checkbox_frame_15 = self.SQ_checkbox_frame_gen(self.sq_checkbox_group_frame, frame_index = 16)

        self.SQ_checkbox()
        self.SQ_checkbox_state()

        if (self.repeat_status == True):
            try:
                widget_disable(self.sq_strobe_btn)
            except (AttributeError, tk.TclError):
                pass
        elif (self.repeat_status == False):
            try:
                widget_enable(self.sq_strobe_btn)
            except (AttributeError, tk.TclError):
                pass

    def SQ_panel_gen(self, window_frame):
        tk_frame_1 = tk.Frame(window_frame, width = 730+200, height = 250 + 360, highlightbackground="black", highlightthickness=1) # Main SQ tk_frame for FRAME functions
        #tk_frame_1['bg'] = 'blue'
        #tk_frame_1.place(x = 270, y = 805)
        #tk_frame_1.place(x=0,y=0)
        tk.Label(tk_frame_1, text = 'Frame', font='Helvetica 14 bold').place(x = 0, y =0)

        #tk.Button(tk_frame_1, relief = tk.GROOVE, text = 'Popout', font='Helvetica 11', command = self.SQ_frame_popout).place(x= 80, y=0)


        tk_frame_2 = tk.Frame(tk_frame_1, width = 725 + 205, height = 55)#, bg = 'green') # tk_frame to hold the SQ FRAME Parameters Widgets and Buttons.
        tk_frame_2.place(x = 0, y = 35)


        tk_frame_3 = tk.Frame(tk_frame_1, width = 600 + 330, height = 155 + 360)#, bg = 'purple') # tk_frame to hold the SQ FRAME checkboxes and CH1, CH2, CH3, and CH4 labels
        tk_frame_3.place(x = 0, y = 90)#y = 80)
        ######################################################################################
        #tk_frame_2
        tk.Label(tk_frame_2, text = 'No. of Frame:', font='Helvetica 11').place(x = 0, y = 5)

        number_list = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16']
        tk_frame_1.option_add('*TCombobox*Listbox.font', ('Helvetica', '11'))
        combobox_1 = ttk.Combobox(tk_frame_2, values=number_list, width = 3, state='readonly', font = 'Helvetica 11')
        combobox_1.place(x = 100, y = 5)
        combobox_1.current(self.sq_fr_arr[0] - 1)

        tk.Label(tk_frame_2, text = 'Frame Width:\n(0-99999)', font = 'Helvetica 11').place(x = 180, y = 5)

        self.sq_fr_width_var = tk.StringVar()

        spinbox_1 = tk.Spinbox(master = tk_frame_2, width = 5, from_=0, to= 99999, textvariable = self.sq_fr_width_var
                                     , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        spinbox_1.place(x = 280, y = 3)

        self.sq_fr_width_var.set(self.sq_fr_arr[1])

        self.sq_fr_width_label_var = tk.StringVar()

        label_1 = tk.Label(tk_frame_2, textvariable = self.sq_fr_width_label_var, font = 'Helvetica 11 italic') #Label frame width

        self.sq_fr_width_label_var.set(str(np.divide(self.sq_fr_arr[1], 100)) + ' ms')
        label_1.place(x = 280, y = 27)

        button_1 = tk.Button(tk_frame_2,relief = tk.GROOVE, width = 8,text = 'Set Frame', font = 'Helvetica 11') #self.sq_set_fr_btn
        button_1.place(x = 390, y =10)

        button_3 = tk.Button(tk_frame_2,relief = tk.GROOVE, width = 10, text = 'Strobe Frame', font='Helvetica 11') #self.sq_strobe_btn
        button_3.place(x = 482, y =10)

        ######################################################################################
        #tk_frame_3
        tk.Label(tk_frame_3, text = 'CH1', font='Helvetica 11').place(x = 10-5, y = 25 + 3) 
        tk.Label(tk_frame_3, text = 'CH2', font='Helvetica 11').place(x = 10-5, y = 55 + 3) 
        tk.Label(tk_frame_3, text = 'CH3', font='Helvetica 11').place(x = 10-5, y = 85 + 3) 
        tk.Label(tk_frame_3, text = 'CH4', font='Helvetica 11').place(x = 10-5, y = 115 + 3)

        tk.Label(tk_frame_3, text = 'CH5', font='Helvetica 11').place(x = 10-5, y = 145 + 3) 
        tk.Label(tk_frame_3, text = 'CH6', font='Helvetica 11').place(x = 10-5, y = 175 + 3) 
        tk.Label(tk_frame_3, text = 'CH7', font='Helvetica 11').place(x = 10-5, y = 205 + 3) 
        tk.Label(tk_frame_3, text = 'CH8', font='Helvetica 11').place(x = 10-5, y = 235 + 3) 

        tk.Label(tk_frame_3, text = 'CH9', font='Helvetica 11').place(x = 10-5, y = 265 + 3) 
        tk.Label(tk_frame_3, text = 'CH10', font='Helvetica 11').place(x = 10-5, y = 295 + 3) 
        tk.Label(tk_frame_3, text = 'CH11', font='Helvetica 11').place(x = 10-5, y = 325 + 3) 
        tk.Label(tk_frame_3, text = 'CH12', font='Helvetica 11').place(x = 10-5, y = 355 + 3)

        tk.Label(tk_frame_3, text = 'CH13', font='Helvetica 11').place(x = 10-5, y = 385 + 3) 
        tk.Label(tk_frame_3, text = 'CH14', font='Helvetica 11').place(x = 10-5, y = 415 + 3) 
        tk.Label(tk_frame_3, text = 'CH15', font='Helvetica 11').place(x = 10-5, y = 445 + 3) 
        tk.Label(tk_frame_3, text = 'CH16', font='Helvetica 11').place(x = 10-5, y = 475 + 3)

        return tk_frame_1, tk_frame_2, tk_frame_3, combobox_1, spinbox_1, button_1, button_3

    def SQ_checkbox_frame_gen(self, tk_frame, frame_index):
        place_x = 0
        x_spacing = int(np.multiply(frame_index, 52))
        place_y = 5
        checkbox_frame = tk.Frame(tk_frame, width = 50, height = 140 + 360, bg="gray76", highlightbackground="black", highlightthickness=1)
        checkbox_frame.place(x = place_x + x_spacing, y = place_y)

        label_index = frame_index - 1
        tk.Label(checkbox_frame, text = 'F%d'%label_index, font='Helvetica 11', bg="gray76").place(x=12, y=0)

        return checkbox_frame

    def SQ_checkbox_gen_v2(self, frame, *tk_intvar_args):
        x_checkbox = 12
        y_checkbox = 20 #+ int(np.multiply(30, ))

        x_label = 31
        y_label = 22 #+ int(np.multiply(30, ))

        checkbox_list = []
        for i, intvar in enumerate(tk_intvar_args):
            checkbox = tk.Checkbutton(frame, bg="gray76", activebackground= "gray76", variable= intvar)
            checkbox.place(x= x_checkbox, y = y_checkbox + int(np.multiply(30, i)))
            tk.Label(frame, bg="gray76").place(x= x_label, y = y_label + int(np.multiply(30, i)))
            checkbox_list.append(checkbox)

        return tuple(checkbox_list)

    def SQ_frame_num_get(self, event=None):

        self.sq_fr_arr[0] = int(self.sq_fr_num_combobox.get())
        self.SQ_checkbox_state()
        #ctrl.SetNoOfFrame(self.sq_fr_arr[0])
        self.ctrl.SetNoOfFrame(self.sq_fr_arr[0])

    def SQ_frame_width_get(self, event=None):
        try:
            curr_val = int(self.sq_fr_width_spinbox.get())
            if curr_val > 99999:
                self.sq_fr_width_var.set(99999)
            elif curr_val < 0:
                self.sq_fr_width_var.set(0)
            self.sq_fr_arr[1] = int(self.sq_fr_width_spinbox.get())
            #rint(self.sq_fr_width_var.get())
            self.sq_fr_width_spinbox['validate']='key'
            self.sq_fr_width_spinbox['vcmd']=(self.sq_fr_width_spinbox.register(validate_int_entry),'%d','%P','%S', True)
        except ValueError:
            #self.sq_fr_width_var.set(self.sq_fr_arr[1])
            pass

        #print(self.sq_fr_arr[1])
        self.sq_fr_width_label_var.set(str(np.divide(self.sq_fr_arr[1], 100)) + ' ms')
        #ctrl.SetFrameWidth(self.sq_fr_arr[1])
        self.ctrl.SetFrameWidth(self.sq_fr_arr[1])

    def SQ_frame_width_keypress(self, event = None):
        try:
            curr_val = int(self.sq_fr_width_spinbox.get())
            if curr_val > 99999:
                self.sq_fr_width_var.set(99999)
            elif curr_val < 0:
                self.sq_fr_width_var.set(0)
        except ValueError:
            pass

    def SQ_set_frame(self, event=None):
        for i in range (0, self.sq_fr_arr[0]):
            #print(int(i), self.sq_fr_int_arr[i])
            #ctrl.SetFrame(int(i), self.sq_fr_int_arr[i])
            self.ctrl.SetFrame(int(i), self.sq_fr_int_arr[i])
        

    def SQ_checkbox_click_v2(self, f_n_arr, fr_int_arr, fr_index, *tk_intvar_args):
        #where n is the the frame number (e.g. f0, f1, etc.)
        for i, intvar in enumerate(tk_intvar_args):
            f_n_arr[i] = intvar.get()
            #print(f_n_arr)
        #print(f_n_arr)
        fr_int_arr[fr_index] = binary_to_dec_v2(f_n_arr[0],f_n_arr[1],f_n_arr[2],f_n_arr[3],
            f_n_arr[4],f_n_arr[5],f_n_arr[6],f_n_arr[7],
            f_n_arr[8],f_n_arr[9],f_n_arr[10],f_n_arr[11],
            f_n_arr[12],f_n_arr[13],f_n_arr[14],f_n_arr[15], reverse_str = True)

        #ctrl.SetFrame(int(fr_index), fr_int_arr[fr_index])
        #print('int fr:', fr_index)
        print ('int val:',fr_int_arr)
        self.ctrl.SetFrame(int(fr_index), fr_int_arr[fr_index])

    def SQ_checkbox_bind_focus(self, checkbox_1 = None, checkbox_2 = None, checkbox_3 = None, checkbox_4 = None):
        if checkbox_1 is not None:
            checkbox_1.bind("<1>", lambda event: checkbox_1.focus_set())
        if checkbox_2 is not None:
            checkbox_2.bind("<1>", lambda event: checkbox_2.focus_set())
        if checkbox_3 is not None:
            checkbox_3.bind("<1>", lambda event: checkbox_3.focus_set())
        if checkbox_4 is not None:
            checkbox_4.bind("<1>", lambda event: checkbox_4.focus_set())

    def SQ_checkbox_param(self, sq_arr, sq_fr_int, arr_size):
        return_list = []
        sq_arr = dec_to_binary_arr_v2(sq_fr_int, sq_arr, reverse_arr = True)
        
        return_list.append(sq_arr)
        for i in range(arr_size):
            tk_intvar = tk.IntVar(value = sq_arr[i])
            return_list.append(tk_intvar)

        #print(return_list)
        return tuple(return_list)

    def SQ_checkbox_update_func(self, sq_arr, sq_fr_int, *tk_intvar):
        sq_arr = dec_to_binary_arr_v2(sq_fr_int, sq_arr, reverse_arr = True)
        for i,intvar in enumerate(tk_intvar):
            intvar.set(sq_arr[i])


    def SQ_checkbox_update_widget(self):
        self.SQ_checkbox_update_func(self.sq_f0_arr, self.sq_fr_int_arr[0],
            self.ch1_status_f0,self.ch2_status_f0, self.ch3_status_f0, self.ch4_status_f0,
            self.ch5_status_f0,self.ch6_status_f0, self.ch7_status_f0, self.ch8_status_f0,
            self.ch9_status_f0,self.ch10_status_f0, self.ch11_status_f0, self.ch12_status_f0,
            self.ch13_status_f0,self.ch14_status_f0, self.ch15_status_f0, self.ch16_status_f0)

        self.SQ_checkbox_update_func(self.sq_f1_arr, self.sq_fr_int_arr[1],
            self.ch1_status_f1,self.ch2_status_f1, self.ch3_status_f1, self.ch4_status_f1,
            self.ch5_status_f1,self.ch6_status_f1, self.ch7_status_f1, self.ch8_status_f1,
            self.ch9_status_f1,self.ch10_status_f1, self.ch11_status_f1, self.ch12_status_f1,
            self.ch13_status_f1,self.ch14_status_f1, self.ch15_status_f1, self.ch16_status_f1)

        self.SQ_checkbox_update_func(self.sq_f2_arr, self.sq_fr_int_arr[2],
            self.ch1_status_f2,self.ch2_status_f2, self.ch3_status_f2, self.ch4_status_f2,
            self.ch5_status_f2,self.ch6_status_f2, self.ch7_status_f2, self.ch8_status_f2,
            self.ch9_status_f2,self.ch10_status_f2, self.ch11_status_f2, self.ch12_status_f2,
            self.ch13_status_f2,self.ch14_status_f2, self.ch15_status_f2, self.ch16_status_f2)

        self.SQ_checkbox_update_func(self.sq_f3_arr, self.sq_fr_int_arr[3],
            self.ch1_status_f3,self.ch2_status_f3, self.ch3_status_f3, self.ch4_status_f3,
            self.ch5_status_f3,self.ch6_status_f3, self.ch7_status_f3, self.ch8_status_f3,
            self.ch9_status_f3,self.ch10_status_f3, self.ch11_status_f3, self.ch12_status_f3,
            self.ch13_status_f3,self.ch14_status_f3, self.ch15_status_f3, self.ch16_status_f3)

        self.SQ_checkbox_update_func(self.sq_f4_arr, self.sq_fr_int_arr[4],
            self.ch1_status_f4,self.ch2_status_f4, self.ch3_status_f4, self.ch4_status_f4,
            self.ch5_status_f4,self.ch6_status_f4, self.ch7_status_f4, self.ch8_status_f4,
            self.ch9_status_f4,self.ch10_status_f4, self.ch11_status_f4, self.ch12_status_f4,
            self.ch13_status_f4,self.ch14_status_f4, self.ch15_status_f4, self.ch16_status_f4)

        self.SQ_checkbox_update_func(self.sq_f5_arr, self.sq_fr_int_arr[5],
            self.ch1_status_f5,self.ch2_status_f5, self.ch3_status_f5, self.ch4_status_f5,
            self.ch5_status_f5,self.ch6_status_f5, self.ch7_status_f5, self.ch8_status_f5,
            self.ch9_status_f5,self.ch10_status_f5, self.ch11_status_f5, self.ch12_status_f5,
            self.ch13_status_f5,self.ch14_status_f5, self.ch15_status_f5, self.ch16_status_f5)

        self.SQ_checkbox_update_func(self.sq_f6_arr, self.sq_fr_int_arr[6],
            self.ch1_status_f6,self.ch2_status_f6, self.ch3_status_f6, self.ch4_status_f6,
            self.ch5_status_f6,self.ch6_status_f6, self.ch7_status_f6, self.ch8_status_f6,
            self.ch9_status_f6,self.ch10_status_f6, self.ch11_status_f6, self.ch12_status_f6,
            self.ch13_status_f6,self.ch14_status_f6, self.ch15_status_f6, self.ch16_status_f6)

        self.SQ_checkbox_update_func(self.sq_f7_arr, self.sq_fr_int_arr[7],
            self.ch1_status_f7,self.ch2_status_f7, self.ch3_status_f7, self.ch4_status_f7,
            self.ch5_status_f7,self.ch6_status_f7, self.ch7_status_f7, self.ch8_status_f7,
            self.ch9_status_f7,self.ch10_status_f7, self.ch11_status_f7, self.ch12_status_f7,
            self.ch13_status_f7,self.ch14_status_f7, self.ch15_status_f7, self.ch16_status_f7)

        self.SQ_checkbox_update_func(self.sq_f8_arr, self.sq_fr_int_arr[8],
            self.ch1_status_f8,self.ch2_status_f8, self.ch3_status_f8, self.ch4_status_f8,
            self.ch5_status_f8,self.ch6_status_f8, self.ch7_status_f8, self.ch8_status_f8,
            self.ch9_status_f8,self.ch10_status_f8, self.ch11_status_f8, self.ch12_status_f8,
            self.ch13_status_f8,self.ch14_status_f8, self.ch15_status_f8, self.ch16_status_f8)

        self.SQ_checkbox_update_func(self.sq_f9_arr, self.sq_fr_int_arr[9],
            self.ch1_status_f9,self.ch2_status_f9, self.ch3_status_f9, self.ch4_status_f9,
            self.ch5_status_f9,self.ch6_status_f9, self.ch7_status_f9, self.ch8_status_f9,
            self.ch9_status_f9,self.ch10_status_f9, self.ch11_status_f9, self.ch12_status_f9,
            self.ch13_status_f9,self.ch14_status_f9, self.ch15_status_f9, self.ch16_status_f9)

        self.SQ_checkbox_update_func(self.sq_f10_arr, self.sq_fr_int_arr[10],
            self.ch1_status_f10,self.ch2_status_f10, self.ch3_status_f10, self.ch4_status_f10,
            self.ch5_status_f10,self.ch6_status_f10, self.ch7_status_f10, self.ch8_status_f10,
            self.ch9_status_f10,self.ch10_status_f10, self.ch11_status_f10, self.ch12_status_f10,
            self.ch13_status_f10,self.ch14_status_f10, self.ch15_status_f10, self.ch16_status_f10)

        self.SQ_checkbox_update_func(self.sq_f11_arr, self.sq_fr_int_arr[11],
            self.ch1_status_f11,self.ch2_status_f11, self.ch3_status_f11, self.ch4_status_f11,
            self.ch5_status_f11,self.ch6_status_f11, self.ch7_status_f11, self.ch8_status_f11,
            self.ch9_status_f11,self.ch10_status_f11, self.ch11_status_f11, self.ch12_status_f11,
            self.ch13_status_f11,self.ch14_status_f11, self.ch15_status_f11, self.ch16_status_f11)

        self.SQ_checkbox_update_func(self.sq_f12_arr, self.sq_fr_int_arr[12],
            self.ch1_status_f12,self.ch2_status_f12, self.ch3_status_f12, self.ch4_status_f12,
            self.ch5_status_f12,self.ch6_status_f12, self.ch7_status_f12, self.ch8_status_f12,
            self.ch9_status_f12,self.ch10_status_f12, self.ch11_status_f12, self.ch12_status_f12,
            self.ch13_status_f12,self.ch14_status_f12, self.ch15_status_f12, self.ch16_status_f12)

        self.SQ_checkbox_update_func(self.sq_f13_arr, self.sq_fr_int_arr[13],
            self.ch1_status_f13,self.ch2_status_f13, self.ch3_status_f13, self.ch4_status_f13,
            self.ch5_status_f13,self.ch6_status_f13, self.ch7_status_f13, self.ch8_status_f13,
            self.ch9_status_f13,self.ch10_status_f13, self.ch11_status_f13, self.ch12_status_f13,
            self.ch13_status_f13,self.ch14_status_f13, self.ch15_status_f13, self.ch16_status_f13)

        self.SQ_checkbox_update_func(self.sq_f14_arr, self.sq_fr_int_arr[14],
            self.ch1_status_f14,self.ch2_status_f14, self.ch3_status_f14, self.ch4_status_f14,
            self.ch5_status_f14,self.ch6_status_f14, self.ch7_status_f14, self.ch8_status_f14,
            self.ch9_status_f14,self.ch10_status_f14, self.ch11_status_f14, self.ch12_status_f14,
            self.ch13_status_f14,self.ch14_status_f14, self.ch15_status_f14, self.ch16_status_f14)

        self.SQ_checkbox_update_func(self.sq_f15_arr, self.sq_fr_int_arr[15],
            self.ch1_status_f15,self.ch2_status_f15, self.ch3_status_f15, self.ch4_status_f15,
            self.ch5_status_f15,self.ch6_status_f15, self.ch7_status_f15, self.ch8_status_f15,
            self.ch9_status_f15,self.ch10_status_f15, self.ch11_status_f15, self.ch12_status_f15,
            self.ch13_status_f15,self.ch14_status_f15, self.ch15_status_f15, self.ch16_status_f15)
    
    def SQ_Frame_Popout_Update(self):
        self.SQ_checkbox_update_widget()
        self.sq_fr_num_combobox.current(self.sq_fr_arr[0] - 1)
        self.sq_fr_width_var.set(self.sq_fr_arr[1])
        self.sq_fr_width_label_var.set(str(np.divide(self.sq_fr_arr[1], 100)) + ' ms')
        self.SQ_checkbox_state()

    def SQ_checkbox(self):
        #print(self.sq_fr_int_arr)
        arr_size = 16
        (self.sq_f0_arr, self.ch1_status_f0,self.ch2_status_f0, self.ch3_status_f0, self.ch4_status_f0,
            self.ch5_status_f0,self.ch6_status_f0, self.ch7_status_f0, self.ch8_status_f0,
            self.ch9_status_f0,self.ch10_status_f0, self.ch11_status_f0, self.ch12_status_f0,
            self.ch13_status_f0,self.ch14_status_f0, self.ch15_status_f0, self.ch16_status_f0) = self.SQ_checkbox_param(self.sq_f0_arr, self.sq_fr_int_arr[0], arr_size)

        #print(self.SQ_checkbox_param(self.sq_f0_arr, self.sq_fr_int_arr[0], 16))
        #self.sq_fr_int_arr[1] = 100
        (self.sq_f1_arr, self.ch1_status_f1,self.ch2_status_f1, self.ch3_status_f1, self.ch4_status_f1,
            self.ch5_status_f1,self.ch6_status_f1, self.ch7_status_f1, self.ch8_status_f1,
            self.ch9_status_f1,self.ch10_status_f1, self.ch11_status_f1, self.ch12_status_f1,
            self.ch13_status_f1,self.ch14_status_f1, self.ch15_status_f1, self.ch16_status_f1) = self.SQ_checkbox_param(self.sq_f1_arr, self.sq_fr_int_arr[1], arr_size)

        (self.sq_f2_arr, self.ch1_status_f2,self.ch2_status_f2, self.ch3_status_f2, self.ch4_status_f2,
            self.ch5_status_f2,self.ch6_status_f2, self.ch7_status_f2, self.ch8_status_f2,
            self.ch9_status_f2,self.ch10_status_f2, self.ch11_status_f2, self.ch12_status_f2,
            self.ch13_status_f2,self.ch14_status_f2, self.ch15_status_f2, self.ch16_status_f2) = self.SQ_checkbox_param(self.sq_f2_arr, self.sq_fr_int_arr[2], arr_size)

        (self.sq_f3_arr, self.ch1_status_f3,self.ch2_status_f3, self.ch3_status_f3, self.ch4_status_f3,
            self.ch5_status_f3,self.ch6_status_f3, self.ch7_status_f3, self.ch8_status_f3,
            self.ch9_status_f3,self.ch10_status_f3, self.ch11_status_f3, self.ch12_status_f3,
            self.ch13_status_f3,self.ch14_status_f3, self.ch15_status_f3, self.ch16_status_f3) = self.SQ_checkbox_param(self.sq_f3_arr, self.sq_fr_int_arr[3], arr_size)

        (self.sq_f4_arr, self.ch1_status_f4,self.ch2_status_f4, self.ch3_status_f4, self.ch4_status_f4,
            self.ch5_status_f4,self.ch6_status_f4, self.ch7_status_f4, self.ch8_status_f4,
            self.ch9_status_f4,self.ch10_status_f4, self.ch11_status_f4, self.ch12_status_f4,
            self.ch13_status_f4,self.ch14_status_f4, self.ch15_status_f4, self.ch16_status_f4) = self.SQ_checkbox_param(self.sq_f4_arr, self.sq_fr_int_arr[4], arr_size)

        (self.sq_f5_arr, self.ch1_status_f5,self.ch2_status_f5, self.ch3_status_f5, self.ch4_status_f5,
            self.ch5_status_f5,self.ch6_status_f5, self.ch7_status_f5, self.ch8_status_f5,
            self.ch9_status_f5,self.ch10_status_f5, self.ch11_status_f5, self.ch12_status_f5,
            self.ch13_status_f5,self.ch14_status_f5, self.ch15_status_f5, self.ch16_status_f5) = self.SQ_checkbox_param(self.sq_f5_arr, self.sq_fr_int_arr[5], arr_size)

        (self.sq_f6_arr, self.ch1_status_f6,self.ch2_status_f6, self.ch3_status_f6, self.ch4_status_f6,
            self.ch5_status_f6,self.ch6_status_f6, self.ch7_status_f6, self.ch8_status_f6,
            self.ch9_status_f6,self.ch10_status_f6, self.ch11_status_f6, self.ch12_status_f6,
            self.ch13_status_f6,self.ch14_status_f6, self.ch15_status_f6, self.ch16_status_f6) = self.SQ_checkbox_param(self.sq_f6_arr, self.sq_fr_int_arr[6], arr_size)

        (self.sq_f7_arr, self.ch1_status_f7,self.ch2_status_f7, self.ch3_status_f7, self.ch4_status_f7,
            self.ch5_status_f7,self.ch6_status_f7, self.ch7_status_f7, self.ch8_status_f7,
            self.ch9_status_f7,self.ch10_status_f7, self.ch11_status_f7, self.ch12_status_f7,
            self.ch13_status_f7,self.ch14_status_f7, self.ch15_status_f7, self.ch16_status_f7) = self.SQ_checkbox_param(self.sq_f7_arr, self.sq_fr_int_arr[7], arr_size)

        (self.sq_f8_arr, self.ch1_status_f8,self.ch2_status_f8, self.ch3_status_f8, self.ch4_status_f8,
            self.ch5_status_f8,self.ch6_status_f8, self.ch7_status_f8, self.ch8_status_f8,
            self.ch9_status_f8,self.ch10_status_f8, self.ch11_status_f8, self.ch12_status_f8,
            self.ch13_status_f8,self.ch14_status_f8, self.ch15_status_f8, self.ch16_status_f8) = self.SQ_checkbox_param(self.sq_f8_arr, self.sq_fr_int_arr[8], arr_size)

        (self.sq_f9_arr, self.ch1_status_f9,self.ch2_status_f9, self.ch3_status_f9, self.ch4_status_f9,
            self.ch5_status_f9,self.ch6_status_f9, self.ch7_status_f9, self.ch8_status_f9,
            self.ch9_status_f9,self.ch10_status_f9, self.ch11_status_f9, self.ch12_status_f9,
            self.ch13_status_f9,self.ch14_status_f9, self.ch15_status_f9, self.ch16_status_f9) = self.SQ_checkbox_param(self.sq_f9_arr, self.sq_fr_int_arr[9], arr_size)

        (self.sq_f10_arr, self.ch1_status_f10,self.ch2_status_f10, self.ch3_status_f10, self.ch4_status_f10,
            self.ch5_status_f10,self.ch6_status_f10, self.ch7_status_f10, self.ch8_status_f10,
            self.ch9_status_f10,self.ch10_status_f10, self.ch11_status_f10, self.ch12_status_f10,
            self.ch13_status_f10,self.ch14_status_f10, self.ch15_status_f10, self.ch16_status_f10) = self.SQ_checkbox_param(self.sq_f10_arr, self.sq_fr_int_arr[10], arr_size)

        (self.sq_f11_arr, self.ch1_status_f11,self.ch2_status_f11, self.ch3_status_f11, self.ch4_status_f11,
            self.ch5_status_f11,self.ch6_status_f11, self.ch7_status_f11, self.ch8_status_f11,
            self.ch9_status_f11,self.ch10_status_f11, self.ch11_status_f11, self.ch12_status_f11,
            self.ch13_status_f11,self.ch14_status_f11, self.ch15_status_f11, self.ch16_status_f11) = self.SQ_checkbox_param(self.sq_f11_arr, self.sq_fr_int_arr[11], arr_size)

        (self.sq_f12_arr, self.ch1_status_f12,self.ch2_status_f12, self.ch3_status_f12, self.ch4_status_f12,
            self.ch5_status_f12,self.ch6_status_f12, self.ch7_status_f12, self.ch8_status_f12,
            self.ch9_status_f12,self.ch10_status_f12, self.ch11_status_f12, self.ch12_status_f12,
            self.ch13_status_f12,self.ch14_status_f12, self.ch15_status_f12, self.ch16_status_f12) = self.SQ_checkbox_param(self.sq_f12_arr, self.sq_fr_int_arr[12], arr_size)

        (self.sq_f13_arr, self.ch1_status_f13,self.ch2_status_f13, self.ch3_status_f13, self.ch4_status_f13,
            self.ch5_status_f13,self.ch6_status_f13, self.ch7_status_f13, self.ch8_status_f13,
            self.ch9_status_f13,self.ch10_status_f13, self.ch11_status_f13, self.ch12_status_f13,
            self.ch13_status_f13,self.ch14_status_f13, self.ch15_status_f13, self.ch16_status_f13) = self.SQ_checkbox_param(self.sq_f13_arr, self.sq_fr_int_arr[13], arr_size)

        (self.sq_f14_arr, self.ch1_status_f14,self.ch2_status_f14, self.ch3_status_f14, self.ch4_status_f14,
            self.ch5_status_f14,self.ch6_status_f14, self.ch7_status_f14, self.ch8_status_f14,
            self.ch9_status_f14,self.ch10_status_f14, self.ch11_status_f14, self.ch12_status_f14,
            self.ch13_status_f14,self.ch14_status_f14, self.ch15_status_f14, self.ch16_status_f14) = self.SQ_checkbox_param(self.sq_f14_arr, self.sq_fr_int_arr[14], arr_size)

        (self.sq_f15_arr, self.ch1_status_f15,self.ch2_status_f15, self.ch3_status_f15, self.ch4_status_f15,
            self.ch5_status_f15,self.ch6_status_f15, self.ch7_status_f15, self.ch8_status_f15,
            self.ch9_status_f15,self.ch10_status_f15, self.ch11_status_f15, self.ch12_status_f15,
            self.ch13_status_f15,self.ch14_status_f15, self.ch15_status_f15, self.ch16_status_f15) = self.SQ_checkbox_param(self.sq_f15_arr, self.sq_fr_int_arr[15], arr_size)
        ################################################################################################################################################
        #F0
        (self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
            self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
            self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
            self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_0,
            self.ch1_status_f0,self.ch2_status_f0, self.ch3_status_f0, self.ch4_status_f0,
            self.ch5_status_f0,self.ch6_status_f0, self.ch7_status_f0, self.ch8_status_f0,
            self.ch9_status_f0,self.ch10_status_f0, self.ch11_status_f0, self.ch12_status_f0,
            self.ch13_status_f0,self.ch14_status_f0, self.ch15_status_f0, self.ch16_status_f0)

        self.ch1_box_f0['command'] = self.ch2_box_f0['command'] = self.ch3_box_f0['command'] = self.ch4_box_f0['command'] =\
        self.ch5_box_f0['command'] = self.ch6_box_f0['command'] = self.ch7_box_f0['command'] = self.ch8_box_f0['command'] =\
        self.ch9_box_f0['command'] = self.ch10_box_f0['command'] = self.ch11_box_f0['command'] = self.ch12_box_f0['command'] =\
        self.ch13_box_f0['command'] = self.ch14_box_f0['command'] = self.ch15_box_f0['command'] = self.ch16_box_f0['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f0_arr, self.sq_fr_int_arr, 0, 
            self.ch1_status_f0,self.ch2_status_f0, self.ch3_status_f0, self.ch4_status_f0,
            self.ch5_status_f0,self.ch6_status_f0, self.ch7_status_f0, self.ch8_status_f0,
            self.ch9_status_f0,self.ch10_status_f0, self.ch11_status_f0, self.ch12_status_f0,
            self.ch13_status_f0,self.ch14_status_f0, self.ch15_status_f0, self.ch16_status_f0)

        self.SQ_checkbox_bind_focus(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0)
        self.SQ_checkbox_bind_focus(self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0)
        self.SQ_checkbox_bind_focus(self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0)
        self.SQ_checkbox_bind_focus(self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
        ################################################################################################################################################
        #F1
        (self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
            self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
            self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
            self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_1,
            self.ch1_status_f1,self.ch2_status_f1, self.ch3_status_f1, self.ch4_status_f1,
            self.ch5_status_f1,self.ch6_status_f1, self.ch7_status_f1, self.ch8_status_f1,
            self.ch9_status_f1,self.ch10_status_f1, self.ch11_status_f1, self.ch12_status_f1,
            self.ch13_status_f1,self.ch14_status_f1, self.ch15_status_f1, self.ch16_status_f1)

        self.ch1_box_f1['command'] = self.ch2_box_f1['command'] = self.ch3_box_f1['command'] = self.ch4_box_f1['command'] =\
        self.ch5_box_f1['command'] = self.ch6_box_f1['command'] = self.ch7_box_f1['command'] = self.ch8_box_f1['command'] =\
        self.ch9_box_f1['command'] = self.ch10_box_f1['command'] = self.ch11_box_f1['command'] = self.ch12_box_f1['command'] =\
        self.ch13_box_f1['command'] = self.ch14_box_f1['command'] = self.ch15_box_f1['command'] = self.ch16_box_f1['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f1_arr, self.sq_fr_int_arr, 1, 
            self.ch1_status_f1,self.ch2_status_f1, self.ch3_status_f1, self.ch4_status_f1,
            self.ch5_status_f1,self.ch6_status_f1, self.ch7_status_f1, self.ch8_status_f1,
            self.ch9_status_f1,self.ch10_status_f1, self.ch11_status_f1, self.ch12_status_f1,
            self.ch13_status_f1,self.ch14_status_f1, self.ch15_status_f1, self.ch16_status_f1)

        self.SQ_checkbox_bind_focus(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1)
        self.SQ_checkbox_bind_focus(self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1)
        self.SQ_checkbox_bind_focus(self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1)
        self.SQ_checkbox_bind_focus(self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)

        ################################################################################################################################################
        #F2
        (self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
            self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
            self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
            self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_2,
            self.ch1_status_f2,self.ch2_status_f2, self.ch3_status_f2, self.ch4_status_f2,
            self.ch5_status_f2,self.ch6_status_f2, self.ch7_status_f2, self.ch8_status_f2,
            self.ch9_status_f2,self.ch10_status_f2, self.ch11_status_f2, self.ch12_status_f2,
            self.ch13_status_f2,self.ch14_status_f2, self.ch15_status_f2, self.ch16_status_f2)

        self.ch1_box_f2['command'] = self.ch2_box_f2['command'] = self.ch3_box_f2['command'] = self.ch4_box_f2['command'] =\
        self.ch5_box_f2['command'] = self.ch6_box_f2['command'] = self.ch7_box_f2['command'] = self.ch8_box_f2['command'] =\
        self.ch9_box_f2['command'] = self.ch10_box_f2['command'] = self.ch11_box_f2['command'] = self.ch12_box_f2['command'] =\
        self.ch13_box_f2['command'] = self.ch14_box_f2['command'] = self.ch15_box_f2['command'] = self.ch16_box_f2['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f2_arr, self.sq_fr_int_arr, 2, 
            self.ch1_status_f2,self.ch2_status_f2, self.ch3_status_f2, self.ch4_status_f2,
            self.ch5_status_f2,self.ch6_status_f2, self.ch7_status_f2, self.ch8_status_f2,
            self.ch9_status_f2,self.ch10_status_f2, self.ch11_status_f2, self.ch12_status_f2,
            self.ch13_status_f2,self.ch14_status_f2, self.ch15_status_f2, self.ch16_status_f2)

        self.SQ_checkbox_bind_focus(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2)
        self.SQ_checkbox_bind_focus(self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2)
        self.SQ_checkbox_bind_focus(self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2)
        self.SQ_checkbox_bind_focus(self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
        
        ################################################################################################################################################
        #F3
        (self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
            self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
            self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
            self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_3,
            self.ch1_status_f3,self.ch2_status_f3, self.ch3_status_f3, self.ch4_status_f3,
            self.ch5_status_f3,self.ch6_status_f3, self.ch7_status_f3, self.ch8_status_f3,
            self.ch9_status_f3,self.ch10_status_f3, self.ch11_status_f3, self.ch12_status_f3,
            self.ch13_status_f3,self.ch14_status_f3, self.ch15_status_f3, self.ch16_status_f3)

        self.ch1_box_f3['command'] = self.ch2_box_f3['command'] = self.ch3_box_f3['command'] = self.ch4_box_f3['command'] =\
        self.ch5_box_f3['command'] = self.ch6_box_f3['command'] = self.ch7_box_f3['command'] = self.ch8_box_f3['command'] =\
        self.ch9_box_f3['command'] = self.ch10_box_f3['command'] = self.ch11_box_f3['command'] = self.ch12_box_f3['command'] =\
        self.ch13_box_f3['command'] = self.ch14_box_f3['command'] = self.ch15_box_f3['command'] = self.ch16_box_f3['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f3_arr, self.sq_fr_int_arr, 3, 
            self.ch1_status_f3,self.ch2_status_f3, self.ch3_status_f3, self.ch4_status_f3,
            self.ch5_status_f3,self.ch6_status_f3, self.ch7_status_f3, self.ch8_status_f3,
            self.ch9_status_f3,self.ch10_status_f3, self.ch11_status_f3, self.ch12_status_f3,
            self.ch13_status_f3,self.ch14_status_f3, self.ch15_status_f3, self.ch16_status_f3)

        self.SQ_checkbox_bind_focus(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3)
        self.SQ_checkbox_bind_focus(self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3)
        self.SQ_checkbox_bind_focus(self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3)
        self.SQ_checkbox_bind_focus(self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)

        ################################################################################################################################################
        #F4
        (self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
            self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
            self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
            self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_4,
            self.ch1_status_f4,self.ch2_status_f4, self.ch3_status_f4, self.ch4_status_f4,
            self.ch5_status_f4,self.ch6_status_f4, self.ch7_status_f4, self.ch8_status_f4,
            self.ch9_status_f4,self.ch10_status_f4, self.ch11_status_f4, self.ch12_status_f4,
            self.ch13_status_f4,self.ch14_status_f4, self.ch15_status_f4, self.ch16_status_f4)

        self.ch1_box_f4['command'] = self.ch2_box_f4['command'] = self.ch3_box_f4['command'] = self.ch4_box_f4['command'] =\
        self.ch5_box_f4['command'] = self.ch6_box_f4['command'] = self.ch7_box_f4['command'] = self.ch8_box_f4['command'] =\
        self.ch9_box_f4['command'] = self.ch10_box_f4['command'] = self.ch11_box_f4['command'] = self.ch12_box_f4['command'] =\
        self.ch13_box_f4['command'] = self.ch14_box_f4['command'] = self.ch15_box_f4['command'] = self.ch16_box_f4['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f4_arr, self.sq_fr_int_arr, 4, 
            self.ch1_status_f4,self.ch2_status_f4, self.ch3_status_f4, self.ch4_status_f4,
            self.ch5_status_f4,self.ch6_status_f4, self.ch7_status_f4, self.ch8_status_f4,
            self.ch9_status_f4,self.ch10_status_f4, self.ch11_status_f4, self.ch12_status_f4,
            self.ch13_status_f4,self.ch14_status_f4, self.ch15_status_f4, self.ch16_status_f4)

        self.SQ_checkbox_bind_focus(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4)
        self.SQ_checkbox_bind_focus(self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4)
        self.SQ_checkbox_bind_focus(self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4)
        self.SQ_checkbox_bind_focus(self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)

        ################################################################################################################################################
        #F5
        (self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
            self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
            self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
            self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_5,
            self.ch1_status_f5,self.ch2_status_f5, self.ch3_status_f5, self.ch4_status_f5,
            self.ch5_status_f5,self.ch6_status_f5, self.ch7_status_f5, self.ch8_status_f5,
            self.ch9_status_f5,self.ch10_status_f5, self.ch11_status_f5, self.ch12_status_f5,
            self.ch13_status_f5,self.ch14_status_f5, self.ch15_status_f5, self.ch16_status_f5)

        self.ch1_box_f5['command'] = self.ch2_box_f5['command'] = self.ch3_box_f5['command'] = self.ch4_box_f5['command'] =\
        self.ch5_box_f5['command'] = self.ch6_box_f5['command'] = self.ch7_box_f5['command'] = self.ch8_box_f5['command'] =\
        self.ch9_box_f5['command'] = self.ch10_box_f5['command'] = self.ch11_box_f5['command'] = self.ch12_box_f5['command'] =\
        self.ch13_box_f5['command'] = self.ch14_box_f5['command'] = self.ch15_box_f5['command'] = self.ch16_box_f5['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f5_arr, self.sq_fr_int_arr, 5, 
            self.ch1_status_f5,self.ch2_status_f5, self.ch3_status_f5, self.ch4_status_f5,
            self.ch5_status_f5,self.ch6_status_f5, self.ch7_status_f5, self.ch8_status_f5,
            self.ch9_status_f5,self.ch10_status_f5, self.ch11_status_f5, self.ch12_status_f5,
            self.ch13_status_f5,self.ch14_status_f5, self.ch15_status_f5, self.ch16_status_f5)

        self.SQ_checkbox_bind_focus(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5)
        self.SQ_checkbox_bind_focus(self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5)
        self.SQ_checkbox_bind_focus(self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5)
        self.SQ_checkbox_bind_focus(self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)

        ################################################################################################################################################
        #F6
        (self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
            self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
            self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
            self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_6,
            self.ch1_status_f6,self.ch2_status_f6, self.ch3_status_f6, self.ch4_status_f6,
            self.ch5_status_f6,self.ch6_status_f6, self.ch7_status_f6, self.ch8_status_f6,
            self.ch9_status_f6,self.ch10_status_f6, self.ch11_status_f6, self.ch12_status_f6,
            self.ch13_status_f6,self.ch14_status_f6, self.ch15_status_f6, self.ch16_status_f6)

        self.ch1_box_f6['command'] = self.ch2_box_f6['command'] = self.ch3_box_f6['command'] = self.ch4_box_f6['command'] =\
        self.ch5_box_f6['command'] = self.ch6_box_f6['command'] = self.ch7_box_f6['command'] = self.ch8_box_f6['command'] =\
        self.ch9_box_f6['command'] = self.ch10_box_f6['command'] = self.ch11_box_f6['command'] = self.ch12_box_f6['command'] =\
        self.ch13_box_f6['command'] = self.ch14_box_f6['command'] = self.ch15_box_f6['command'] = self.ch16_box_f6['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f6_arr, self.sq_fr_int_arr, 6, 
            self.ch1_status_f6,self.ch2_status_f6, self.ch3_status_f6, self.ch4_status_f6,
            self.ch5_status_f6,self.ch6_status_f6, self.ch7_status_f6, self.ch8_status_f6,
            self.ch9_status_f6,self.ch10_status_f6, self.ch11_status_f6, self.ch12_status_f6,
            self.ch13_status_f6,self.ch14_status_f6, self.ch15_status_f6, self.ch16_status_f6)

        self.SQ_checkbox_bind_focus(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6)
        self.SQ_checkbox_bind_focus(self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6)
        self.SQ_checkbox_bind_focus(self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6)
        self.SQ_checkbox_bind_focus(self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)

        ################################################################################################################################################
        #F7
        (self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
            self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
            self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
            self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_7,
            self.ch1_status_f7,self.ch2_status_f7, self.ch3_status_f7, self.ch4_status_f7,
            self.ch5_status_f7,self.ch6_status_f7, self.ch7_status_f7, self.ch8_status_f7,
            self.ch9_status_f7,self.ch10_status_f7, self.ch11_status_f7, self.ch12_status_f7,
            self.ch13_status_f7,self.ch14_status_f7, self.ch15_status_f7, self.ch16_status_f7)

        self.ch1_box_f7['command'] = self.ch2_box_f7['command'] = self.ch3_box_f7['command'] = self.ch4_box_f7['command'] =\
        self.ch5_box_f7['command'] = self.ch6_box_f7['command'] = self.ch7_box_f7['command'] = self.ch8_box_f7['command'] =\
        self.ch9_box_f7['command'] = self.ch10_box_f7['command'] = self.ch11_box_f7['command'] = self.ch12_box_f7['command'] =\
        self.ch13_box_f7['command'] = self.ch14_box_f7['command'] = self.ch15_box_f7['command'] = self.ch16_box_f7['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f7_arr, self.sq_fr_int_arr, 7, 
            self.ch1_status_f7,self.ch2_status_f7, self.ch3_status_f7, self.ch4_status_f7,
            self.ch5_status_f7,self.ch6_status_f7, self.ch7_status_f7, self.ch8_status_f7,
            self.ch9_status_f7,self.ch10_status_f7, self.ch11_status_f7, self.ch12_status_f7,
            self.ch13_status_f7,self.ch14_status_f7, self.ch15_status_f7, self.ch16_status_f7)

        self.SQ_checkbox_bind_focus(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7)
        self.SQ_checkbox_bind_focus(self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7)
        self.SQ_checkbox_bind_focus(self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7)
        self.SQ_checkbox_bind_focus(self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)

        ################################################################################################################################################
        #F8
        (self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
            self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
            self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
            self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_8,
            self.ch1_status_f8,self.ch2_status_f8, self.ch3_status_f8, self.ch4_status_f8,
            self.ch5_status_f8,self.ch6_status_f8, self.ch7_status_f8, self.ch8_status_f8,
            self.ch9_status_f8,self.ch10_status_f8, self.ch11_status_f8, self.ch12_status_f8,
            self.ch13_status_f8,self.ch14_status_f8, self.ch15_status_f8, self.ch16_status_f8)

        self.ch1_box_f8['command'] = self.ch2_box_f8['command'] = self.ch3_box_f8['command'] = self.ch4_box_f8['command'] =\
        self.ch5_box_f8['command'] = self.ch6_box_f8['command'] = self.ch7_box_f8['command'] = self.ch8_box_f8['command'] =\
        self.ch9_box_f8['command'] = self.ch10_box_f8['command'] = self.ch11_box_f8['command'] = self.ch12_box_f8['command'] =\
        self.ch13_box_f8['command'] = self.ch14_box_f8['command'] = self.ch15_box_f8['command'] = self.ch16_box_f8['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f8_arr, self.sq_fr_int_arr, 8, 
            self.ch1_status_f8,self.ch2_status_f8, self.ch3_status_f8, self.ch4_status_f8,
            self.ch5_status_f8,self.ch6_status_f8, self.ch7_status_f8, self.ch8_status_f8,
            self.ch9_status_f8,self.ch10_status_f8, self.ch11_status_f8, self.ch12_status_f8,
            self.ch13_status_f8,self.ch14_status_f8, self.ch15_status_f8, self.ch16_status_f8)

        self.SQ_checkbox_bind_focus(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8)
        self.SQ_checkbox_bind_focus(self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8)
        self.SQ_checkbox_bind_focus(self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8)
        self.SQ_checkbox_bind_focus(self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)

        ################################################################################################################################################
        #F9
        (self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
            self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
            self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
            self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_9,
            self.ch1_status_f9,self.ch2_status_f9, self.ch3_status_f9, self.ch4_status_f9,
            self.ch5_status_f9,self.ch6_status_f9, self.ch7_status_f9, self.ch8_status_f9,
            self.ch9_status_f9,self.ch10_status_f9, self.ch11_status_f9, self.ch12_status_f9,
            self.ch13_status_f9,self.ch14_status_f9, self.ch15_status_f9, self.ch16_status_f9)

        self.ch1_box_f9['command'] = self.ch2_box_f9['command'] = self.ch3_box_f9['command'] = self.ch4_box_f9['command'] =\
        self.ch5_box_f9['command'] = self.ch6_box_f9['command'] = self.ch7_box_f9['command'] = self.ch8_box_f9['command'] =\
        self.ch9_box_f9['command'] = self.ch10_box_f9['command'] = self.ch11_box_f9['command'] = self.ch12_box_f9['command'] =\
        self.ch13_box_f9['command'] = self.ch14_box_f9['command'] = self.ch15_box_f9['command'] = self.ch16_box_f9['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f9_arr, self.sq_fr_int_arr, 9, 
            self.ch1_status_f9,self.ch2_status_f9, self.ch3_status_f9, self.ch4_status_f9,
            self.ch5_status_f9,self.ch6_status_f9, self.ch7_status_f9, self.ch8_status_f9,
            self.ch9_status_f9,self.ch10_status_f9, self.ch11_status_f9, self.ch12_status_f9,
            self.ch13_status_f9,self.ch14_status_f9, self.ch15_status_f9, self.ch16_status_f9)

        self.SQ_checkbox_bind_focus(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9)
        self.SQ_checkbox_bind_focus(self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9)
        self.SQ_checkbox_bind_focus(self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9)
        self.SQ_checkbox_bind_focus(self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)

        ################################################################################################################################################
        #F10
        (self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
            self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
            self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
            self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_10,
            self.ch1_status_f10,self.ch2_status_f10, self.ch3_status_f10, self.ch4_status_f10,
            self.ch5_status_f10,self.ch6_status_f10, self.ch7_status_f10, self.ch8_status_f10,
            self.ch9_status_f10,self.ch10_status_f10, self.ch11_status_f10, self.ch12_status_f10,
            self.ch13_status_f10,self.ch14_status_f10, self.ch15_status_f10, self.ch16_status_f10)

        self.ch1_box_f10['command'] = self.ch2_box_f10['command'] = self.ch3_box_f10['command'] = self.ch4_box_f10['command'] =\
        self.ch5_box_f10['command'] = self.ch6_box_f10['command'] = self.ch7_box_f10['command'] = self.ch8_box_f10['command'] =\
        self.ch9_box_f10['command'] = self.ch10_box_f10['command'] = self.ch11_box_f10['command'] = self.ch12_box_f10['command'] =\
        self.ch13_box_f10['command'] = self.ch14_box_f10['command'] = self.ch15_box_f10['command'] = self.ch16_box_f10['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f10_arr, self.sq_fr_int_arr, 10, 
            self.ch1_status_f10,self.ch2_status_f10, self.ch3_status_f10, self.ch4_status_f10,
            self.ch5_status_f10,self.ch6_status_f10, self.ch7_status_f10, self.ch8_status_f10,
            self.ch9_status_f10,self.ch10_status_f10, self.ch11_status_f10, self.ch12_status_f10,
            self.ch13_status_f10,self.ch14_status_f10, self.ch15_status_f10, self.ch16_status_f10)

        self.SQ_checkbox_bind_focus(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10)
        self.SQ_checkbox_bind_focus(self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10)
        self.SQ_checkbox_bind_focus(self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10)
        self.SQ_checkbox_bind_focus(self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)

        ################################################################################################################################################
        #F11
        (self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
            self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
            self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
            self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_11,
            self.ch1_status_f11,self.ch2_status_f11, self.ch3_status_f11, self.ch4_status_f11,
            self.ch5_status_f11,self.ch6_status_f11, self.ch7_status_f11, self.ch8_status_f11,
            self.ch9_status_f11,self.ch10_status_f11, self.ch11_status_f11, self.ch12_status_f11,
            self.ch13_status_f11,self.ch14_status_f11, self.ch15_status_f11, self.ch16_status_f11)

        self.ch1_box_f11['command'] = self.ch2_box_f11['command'] = self.ch3_box_f11['command'] = self.ch4_box_f11['command'] =\
        self.ch5_box_f11['command'] = self.ch6_box_f11['command'] = self.ch7_box_f11['command'] = self.ch8_box_f11['command'] =\
        self.ch9_box_f11['command'] = self.ch10_box_f11['command'] = self.ch11_box_f11['command'] = self.ch12_box_f11['command'] =\
        self.ch13_box_f11['command'] = self.ch14_box_f11['command'] = self.ch15_box_f11['command'] = self.ch16_box_f11['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f11_arr, self.sq_fr_int_arr, 11, 
            self.ch1_status_f11,self.ch2_status_f11, self.ch3_status_f11, self.ch4_status_f11,
            self.ch5_status_f11,self.ch6_status_f11, self.ch7_status_f11, self.ch8_status_f11,
            self.ch9_status_f11,self.ch10_status_f11, self.ch11_status_f11, self.ch12_status_f11,
            self.ch13_status_f11,self.ch14_status_f11, self.ch15_status_f11, self.ch16_status_f11)

        self.SQ_checkbox_bind_focus(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11)
        self.SQ_checkbox_bind_focus(self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11)
        self.SQ_checkbox_bind_focus(self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11)
        self.SQ_checkbox_bind_focus(self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)

        ################################################################################################################################################
        #F12
        (self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
            self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
            self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
            self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_12,
            self.ch1_status_f12,self.ch2_status_f12, self.ch3_status_f12, self.ch4_status_f12,
            self.ch5_status_f12,self.ch6_status_f12, self.ch7_status_f12, self.ch8_status_f12,
            self.ch9_status_f12,self.ch10_status_f12, self.ch11_status_f12, self.ch12_status_f12,
            self.ch13_status_f12,self.ch14_status_f12, self.ch15_status_f12, self.ch16_status_f12)

        self.ch1_box_f12['command'] = self.ch2_box_f12['command'] = self.ch3_box_f12['command'] = self.ch4_box_f12['command'] =\
        self.ch5_box_f12['command'] = self.ch6_box_f12['command'] = self.ch7_box_f12['command'] = self.ch8_box_f12['command'] =\
        self.ch9_box_f12['command'] = self.ch10_box_f12['command'] = self.ch11_box_f12['command'] = self.ch12_box_f12['command'] =\
        self.ch13_box_f12['command'] = self.ch14_box_f12['command'] = self.ch15_box_f12['command'] = self.ch16_box_f12['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f12_arr, self.sq_fr_int_arr, 12, 
            self.ch1_status_f12,self.ch2_status_f12, self.ch3_status_f12, self.ch4_status_f12,
            self.ch5_status_f12,self.ch6_status_f12, self.ch7_status_f12, self.ch8_status_f12,
            self.ch9_status_f12,self.ch10_status_f12, self.ch11_status_f12, self.ch12_status_f12,
            self.ch13_status_f12,self.ch14_status_f12, self.ch15_status_f12, self.ch16_status_f12)

        self.SQ_checkbox_bind_focus(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12)
        self.SQ_checkbox_bind_focus(self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12)
        self.SQ_checkbox_bind_focus(self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12)
        self.SQ_checkbox_bind_focus(self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)

        ################################################################################################################################################
        #F13
        (self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
            self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
            self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
            self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_13,
            self.ch1_status_f13,self.ch2_status_f13, self.ch3_status_f13, self.ch4_status_f13,
            self.ch5_status_f13,self.ch6_status_f13, self.ch7_status_f13, self.ch8_status_f13,
            self.ch9_status_f13,self.ch10_status_f13, self.ch11_status_f13, self.ch12_status_f13,
            self.ch13_status_f13,self.ch14_status_f13, self.ch15_status_f13, self.ch16_status_f13)

        self.ch1_box_f13['command'] = self.ch2_box_f13['command'] = self.ch3_box_f13['command'] = self.ch4_box_f13['command'] =\
        self.ch5_box_f13['command'] = self.ch6_box_f13['command'] = self.ch7_box_f13['command'] = self.ch8_box_f13['command'] =\
        self.ch9_box_f13['command'] = self.ch10_box_f13['command'] = self.ch11_box_f13['command'] = self.ch12_box_f13['command'] =\
        self.ch13_box_f13['command'] = self.ch14_box_f13['command'] = self.ch15_box_f13['command'] = self.ch16_box_f13['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f13_arr, self.sq_fr_int_arr, 13, 
            self.ch1_status_f13,self.ch2_status_f13, self.ch3_status_f13, self.ch4_status_f13,
            self.ch5_status_f13,self.ch6_status_f13, self.ch7_status_f13, self.ch8_status_f13,
            self.ch9_status_f13,self.ch10_status_f13, self.ch11_status_f13, self.ch12_status_f13,
            self.ch13_status_f13,self.ch14_status_f13, self.ch15_status_f13, self.ch16_status_f13)

        self.SQ_checkbox_bind_focus(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13)
        self.SQ_checkbox_bind_focus(self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13)
        self.SQ_checkbox_bind_focus(self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13)
        self.SQ_checkbox_bind_focus(self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)

        ################################################################################################################################################
        #F14
        (self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
            self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
            self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
            self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_14,
            self.ch1_status_f14,self.ch2_status_f14, self.ch3_status_f14, self.ch4_status_f14,
            self.ch5_status_f14,self.ch6_status_f14, self.ch7_status_f14, self.ch8_status_f14,
            self.ch9_status_f14,self.ch10_status_f14, self.ch11_status_f14, self.ch12_status_f14,
            self.ch13_status_f14,self.ch14_status_f14, self.ch15_status_f14, self.ch16_status_f14)

        self.ch1_box_f14['command'] = self.ch2_box_f14['command'] = self.ch3_box_f14['command'] = self.ch4_box_f14['command'] =\
        self.ch5_box_f14['command'] = self.ch6_box_f14['command'] = self.ch7_box_f14['command'] = self.ch8_box_f14['command'] =\
        self.ch9_box_f14['command'] = self.ch10_box_f14['command'] = self.ch11_box_f14['command'] = self.ch12_box_f14['command'] =\
        self.ch13_box_f14['command'] = self.ch14_box_f14['command'] = self.ch15_box_f14['command'] = self.ch16_box_f14['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f14_arr, self.sq_fr_int_arr, 14,
            self.ch1_status_f14,self.ch2_status_f14, self.ch3_status_f14, self.ch4_status_f14,
            self.ch5_status_f14,self.ch6_status_f14, self.ch7_status_f14, self.ch8_status_f14,
            self.ch9_status_f14,self.ch10_status_f14, self.ch11_status_f14, self.ch12_status_f14,
            self.ch13_status_f14,self.ch14_status_f14, self.ch15_status_f14, self.ch16_status_f14)

        self.SQ_checkbox_bind_focus(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14)
        self.SQ_checkbox_bind_focus(self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14)
        self.SQ_checkbox_bind_focus(self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14)
        self.SQ_checkbox_bind_focus(self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)

        ################################################################################################################################################
        #F15
        (self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
            self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
            self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
            self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_15,
            self.ch1_status_f15,self.ch2_status_f15, self.ch3_status_f15, self.ch4_status_f15,
            self.ch5_status_f15,self.ch6_status_f15, self.ch7_status_f15, self.ch8_status_f15,
            self.ch9_status_f15,self.ch10_status_f15, self.ch11_status_f15, self.ch12_status_f15,
            self.ch13_status_f15,self.ch14_status_f15, self.ch15_status_f15, self.ch16_status_f15)

        self.ch1_box_f15['command'] = self.ch2_box_f15['command'] = self.ch3_box_f15['command'] = self.ch4_box_f15['command'] =\
        self.ch5_box_f15['command'] = self.ch6_box_f15['command'] = self.ch7_box_f15['command'] = self.ch8_box_f15['command'] =\
        self.ch9_box_f15['command'] = self.ch10_box_f15['command'] = self.ch11_box_f15['command'] = self.ch12_box_f15['command'] =\
        self.ch13_box_f15['command'] = self.ch14_box_f15['command'] = self.ch15_box_f15['command'] = self.ch16_box_f15['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f15_arr, self.sq_fr_int_arr, 15, 
            self.ch1_status_f15,self.ch2_status_f15, self.ch3_status_f15, self.ch4_status_f15,
            self.ch5_status_f15,self.ch6_status_f15, self.ch7_status_f15, self.ch8_status_f15,
            self.ch9_status_f15,self.ch10_status_f15, self.ch11_status_f15, self.ch12_status_f15,
            self.ch13_status_f15,self.ch14_status_f15, self.ch15_status_f15, self.ch16_status_f15)

        self.SQ_checkbox_bind_focus(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15)
        self.SQ_checkbox_bind_focus(self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15)
        self.SQ_checkbox_bind_focus(self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15)
        self.SQ_checkbox_bind_focus(self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)

    def SQ_checkbox_state(self, event=None):
        if self.sq_fr_arr[0] == 1:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)

            widget_disable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_disable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_disable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_disable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_disable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_disable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_disable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_disable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_disable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)

        elif self.sq_fr_arr[0] == 2:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)

            widget_disable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_disable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_disable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_disable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_disable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_disable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_disable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_disable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)

        elif self.sq_fr_arr[0] == 3:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)

            widget_disable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_disable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_disable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_disable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_disable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_disable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_disable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)

        elif self.sq_fr_arr[0] == 4:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)

            widget_disable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_disable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_disable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_disable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_disable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_disable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)
                
        elif self.sq_fr_arr[0] == 5:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)

            widget_disable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_disable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_disable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_disable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_disable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)

        elif self.sq_fr_arr[0] == 6:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)

            widget_disable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_disable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_disable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_disable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)

        elif self.sq_fr_arr[0] == 7:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)

            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_disable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_disable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_disable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)

        elif self.sq_fr_arr[0] == 8:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_enable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)

            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_disable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_disable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_disable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)

        elif self.sq_fr_arr[0] == 9:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_enable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_enable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)

            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_disable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_disable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_disable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)

        elif self.sq_fr_arr[0] == 10:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_enable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_enable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_enable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)

            widget_disable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_disable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_disable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)

        elif self.sq_fr_arr[0] == 11:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_enable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_enable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_enable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_enable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)

            widget_disable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_disable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)
    
        elif self.sq_fr_arr[0] == 12:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_enable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_enable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_enable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_enable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_enable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)

            widget_disable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)
        
        elif self.sq_fr_arr[0] == 13:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_enable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_enable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_enable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_enable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_enable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_enable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)

            widget_disable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)

        elif self.sq_fr_arr[0] == 14:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_enable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_enable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_enable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_enable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_enable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_enable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_enable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)

            widget_disable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)
    
        elif self.sq_fr_arr[0] == 15:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_enable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_enable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_enable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_enable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_enable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_enable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_enable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_enable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)

            widget_disable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)

        elif self.sq_fr_arr[0] == 16:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0,
                self.ch5_box_f0, self.ch6_box_f0, self.ch7_box_f0, self.ch8_box_f0,
                self.ch9_box_f0, self.ch10_box_f0, self.ch11_box_f0, self.ch12_box_f0,
                self.ch13_box_f0, self.ch14_box_f0, self.ch15_box_f0, self.ch16_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1,
                self.ch5_box_f1, self.ch6_box_f1, self.ch7_box_f1, self.ch8_box_f1,
                self.ch9_box_f1, self.ch10_box_f1, self.ch11_box_f1, self.ch12_box_f1,
                self.ch13_box_f1, self.ch14_box_f1, self.ch15_box_f1, self.ch16_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2,
                self.ch5_box_f2, self.ch6_box_f2, self.ch7_box_f2, self.ch8_box_f2,
                self.ch9_box_f2, self.ch10_box_f2, self.ch11_box_f2, self.ch12_box_f2,
                self.ch13_box_f2, self.ch14_box_f2, self.ch15_box_f2, self.ch16_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3,
                self.ch5_box_f3, self.ch6_box_f3, self.ch7_box_f3, self.ch8_box_f3,
                self.ch9_box_f3, self.ch10_box_f3, self.ch11_box_f3, self.ch12_box_f3,
                self.ch13_box_f3, self.ch14_box_f3, self.ch15_box_f3, self.ch16_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4,
                self.ch5_box_f4, self.ch6_box_f4, self.ch7_box_f4, self.ch8_box_f4,
                self.ch9_box_f4, self.ch10_box_f4, self.ch11_box_f4, self.ch12_box_f4,
                self.ch13_box_f4, self.ch14_box_f4, self.ch15_box_f4, self.ch16_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5,
                self.ch5_box_f5, self.ch6_box_f5, self.ch7_box_f5, self.ch8_box_f5,
                self.ch9_box_f5, self.ch10_box_f5, self.ch11_box_f5, self.ch12_box_f5,
                self.ch13_box_f5, self.ch14_box_f5, self.ch15_box_f5, self.ch16_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6,
                self.ch5_box_f6, self.ch6_box_f6, self.ch7_box_f6, self.ch8_box_f6,
                self.ch9_box_f6, self.ch10_box_f6, self.ch11_box_f6, self.ch12_box_f6,
                self.ch13_box_f6, self.ch14_box_f6, self.ch15_box_f6, self.ch16_box_f6)
            widget_enable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7,
                self.ch5_box_f7, self.ch6_box_f7, self.ch7_box_f7, self.ch8_box_f7,
                self.ch9_box_f7, self.ch10_box_f7, self.ch11_box_f7, self.ch12_box_f7,
                self.ch13_box_f7, self.ch14_box_f7, self.ch15_box_f7, self.ch16_box_f7)
            widget_enable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8,
                self.ch5_box_f8, self.ch6_box_f8, self.ch7_box_f8, self.ch8_box_f8,
                self.ch9_box_f8, self.ch10_box_f8, self.ch11_box_f8, self.ch12_box_f8,
                self.ch13_box_f8, self.ch14_box_f8, self.ch15_box_f8, self.ch16_box_f8)
            widget_enable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9,
                self.ch5_box_f9, self.ch6_box_f9, self.ch7_box_f9, self.ch8_box_f9,
                self.ch9_box_f9, self.ch10_box_f9, self.ch11_box_f9, self.ch12_box_f9,
                self.ch13_box_f9, self.ch14_box_f9, self.ch15_box_f9, self.ch16_box_f9)
            widget_enable(self.ch1_box_f10, self.ch2_box_f10, self.ch3_box_f10, self.ch4_box_f10,
                self.ch5_box_f10, self.ch6_box_f10, self.ch7_box_f10, self.ch8_box_f10,
                self.ch9_box_f10, self.ch10_box_f10, self.ch11_box_f10, self.ch12_box_f10,
                self.ch13_box_f10, self.ch14_box_f10, self.ch15_box_f10, self.ch16_box_f10)
            widget_enable(self.ch1_box_f11, self.ch2_box_f11, self.ch3_box_f11, self.ch4_box_f11,
                self.ch5_box_f11, self.ch6_box_f11, self.ch7_box_f11, self.ch8_box_f11,
                self.ch9_box_f11, self.ch10_box_f11, self.ch11_box_f11, self.ch12_box_f11,
                self.ch13_box_f11, self.ch14_box_f11, self.ch15_box_f11, self.ch16_box_f11)
            widget_enable(self.ch1_box_f12, self.ch2_box_f12, self.ch3_box_f12, self.ch4_box_f12,
                self.ch5_box_f12, self.ch6_box_f12, self.ch7_box_f12, self.ch8_box_f12,
                self.ch9_box_f12, self.ch10_box_f12, self.ch11_box_f12, self.ch12_box_f12,
                self.ch13_box_f12, self.ch14_box_f12, self.ch15_box_f12, self.ch16_box_f12)
            widget_enable(self.ch1_box_f13, self.ch2_box_f13, self.ch3_box_f13, self.ch4_box_f13,
                self.ch5_box_f13, self.ch6_box_f13, self.ch7_box_f13, self.ch8_box_f13,
                self.ch9_box_f13, self.ch10_box_f13, self.ch11_box_f13, self.ch12_box_f13,
                self.ch13_box_f13, self.ch14_box_f13, self.ch15_box_f13, self.ch16_box_f13)
            widget_enable(self.ch1_box_f14, self.ch2_box_f14, self.ch3_box_f14, self.ch4_box_f14,
                self.ch5_box_f14, self.ch6_box_f14, self.ch7_box_f14, self.ch8_box_f14,
                self.ch9_box_f14, self.ch10_box_f14, self.ch11_box_f14, self.ch12_box_f14,
                self.ch13_box_f14, self.ch14_box_f14, self.ch15_box_f14, self.ch16_box_f14)
            widget_enable(self.ch1_box_f15, self.ch2_box_f15, self.ch3_box_f15, self.ch4_box_f15,
                self.ch5_box_f15, self.ch6_box_f15, self.ch7_box_f15, self.ch8_box_f15,
                self.ch9_box_f15, self.ch10_box_f15, self.ch11_box_f15, self.ch12_box_f15,
                self.ch13_box_f15, self.ch14_box_f15, self.ch15_box_f15, self.ch16_box_f15)
    ###############################################################################################
    #5. LIGHT CONTROL FUNCTIONS
    def widget_current_command(self, ch_tag_num, widget):
        if ch_tag_num == 1 or ch_tag_num == 5 or ch_tag_num == 9 or ch_tag_num == 13:
            widget.config(command = self.current_multi_group_A)

        elif ch_tag_num == 2 or ch_tag_num == 6 or ch_tag_num == 10 or ch_tag_num == 14:
            widget.config(command = self.current_multi_group_B)

        elif ch_tag_num == 3 or ch_tag_num == 7 or ch_tag_num == 11 or ch_tag_num == 15:
            widget.config(command = self.current_multi_group_C)

        elif ch_tag_num == 4 or ch_tag_num == 8 or ch_tag_num == 12 or ch_tag_num == 16:
            widget.config(command = self.current_multi_group_D)

    def spinbox_current_bind(self, ch_tag_num, widget):
        if ch_tag_num == 1 or ch_tag_num == 5 or ch_tag_num == 9 or ch_tag_num == 13:
            widget.bind('<Return>', self.current_multi_group_A)
            widget.bind('<Tab>', self.current_multi_group_A)
            widget.bind('<KeyRelease>', self.current_multi_group_A)

        elif ch_tag_num == 2 or ch_tag_num == 6 or ch_tag_num == 10 or ch_tag_num == 14:
            widget.bind('<Return>', self.current_multi_group_B)
            widget.bind('<Tab>', self.current_multi_group_B)
            widget.bind('<KeyRelease>', self.current_multi_group_B)

        elif ch_tag_num == 3 or ch_tag_num == 7 or ch_tag_num == 11 or ch_tag_num == 15:
            widget.bind('<Return>', self.current_multi_group_C)
            widget.bind('<Tab>', self.current_multi_group_C)
            widget.bind('<KeyRelease>', self.current_multi_group_C)

        elif ch_tag_num == 4 or ch_tag_num == 8 or ch_tag_num == 12 or ch_tag_num == 16:
            widget.bind('<Return>', self.current_multi_group_D)
            widget.bind('<Tab>', self.current_multi_group_D)
            widget.bind('<KeyRelease>', self.current_multi_group_D)


    def widget_intensity_command(self, ch_tag_num, widget):
        if ch_tag_num == 1 or ch_tag_num == 5 or ch_tag_num == 9 or ch_tag_num == 13:
            widget.config(command = self.const_intensity_group_A)

        elif ch_tag_num == 2 or ch_tag_num == 6 or ch_tag_num == 10 or ch_tag_num == 14:
            widget.config(command = self.const_intensity_group_B)

        elif ch_tag_num == 3 or ch_tag_num == 7 or ch_tag_num == 11 or ch_tag_num == 15:
            widget.config(command = self.const_intensity_group_C)

        elif ch_tag_num == 4 or ch_tag_num == 8 or ch_tag_num == 12 or ch_tag_num == 16:
            widget.config(command = self.const_intensity_group_D)

    def spinbox_intensity_bind(self, ch_tag_num, widget):
        if ch_tag_num == 1 or ch_tag_num == 5 or ch_tag_num == 9 or ch_tag_num == 13:
            widget.bind('<Return>', self.const_intensity_group_A)
            widget.bind('<Tab>', self.const_intensity_group_A)
            widget.bind('<KeyRelease>', self.const_intensity_group_A)

        elif ch_tag_num == 2 or ch_tag_num == 6 or ch_tag_num == 10 or ch_tag_num == 14:
            widget.bind('<Return>', self.const_intensity_group_B)
            widget.bind('<Tab>', self.const_intensity_group_B)
            widget.bind('<KeyRelease>', self.const_intensity_group_B)

        elif ch_tag_num == 3 or ch_tag_num == 7 or ch_tag_num == 11 or ch_tag_num == 15:
            widget.bind('<Return>', self.const_intensity_group_C)
            widget.bind('<Tab>', self.const_intensity_group_C)
            widget.bind('<KeyRelease>', self.const_intensity_group_C)

        elif ch_tag_num == 4 or ch_tag_num == 8 or ch_tag_num == 12 or ch_tag_num == 16:
            widget.bind('<Return>', self.const_intensity_group_D)
            widget.bind('<Tab>', self.const_intensity_group_D)
            widget.bind('<KeyRelease>', self.const_intensity_group_D)


    def widget_strobe_command(self, ch_tag_num, widget):
        if ch_tag_num == 1 or ch_tag_num == 5 or ch_tag_num == 9 or ch_tag_num == 13:
            widget.config(command = self.strobe_param_group_A)

        elif ch_tag_num == 2 or ch_tag_num == 6 or ch_tag_num == 10 or ch_tag_num == 14:
            widget.config(command = self.strobe_param_group_B)

        elif ch_tag_num == 3 or ch_tag_num == 7 or ch_tag_num == 11 or ch_tag_num == 15:
            widget.config(command = self.strobe_param_group_C)

        elif ch_tag_num == 4 or ch_tag_num == 8 or ch_tag_num == 12 or ch_tag_num == 16:
            widget.config(command = self.strobe_param_group_D)

    def spinbox_strobe_bind(self, ch_tag_num, widget):
        if ch_tag_num == 1 or ch_tag_num == 5 or ch_tag_num == 9 or ch_tag_num == 13:
            widget.bind('<Return>', self.strobe_param_group_A)
            widget.bind('<Tab>', self.strobe_param_group_A)
            widget.bind('<KeyRelease>', self.strobe_param_group_A)

        elif ch_tag_num == 2 or ch_tag_num == 6 or ch_tag_num == 10 or ch_tag_num == 14:
            widget.bind('<Return>', self.strobe_param_group_B)
            widget.bind('<Tab>', self.strobe_param_group_B)
            widget.bind('<KeyRelease>', self.strobe_param_group_B)

        elif ch_tag_num == 3 or ch_tag_num == 7 or ch_tag_num == 11 or ch_tag_num == 15:
            widget.bind('<Return>', self.strobe_param_group_C)
            widget.bind('<Tab>', self.strobe_param_group_C)
            widget.bind('<KeyRelease>', self.strobe_param_group_C)

        elif ch_tag_num == 4 or ch_tag_num == 8 or ch_tag_num == 12 or ch_tag_num == 16:
            widget.bind('<Return>', self.strobe_param_group_D)
            widget.bind('<Tab>', self.strobe_param_group_D)
            widget.bind('<KeyRelease>', self.strobe_param_group_D)


    def widget_output_delay_command(self, widget):
        widget.config(command = self.output_delay_param)

    def spinbox_output_delay_bind(self, widget):
        widget.bind('<Return>', self.output_delay_param)
        widget.bind('<Tab>', self.output_delay_param)
        widget.bind('<KeyRelease>', self.output_delay_param)

    def widget_output_width_command(self, widget):
        widget.config(command = self.output_width_param)

    def spinbox_output_width_bind(self, widget):
        widget.bind('<Return>', self.output_width_param)
        widget.bind('<Tab>', self.output_width_param)
        widget.bind('<KeyRelease>', self.output_width_param)

    def combobox_widget_bind(self, widget):
        widget.bind('<<ComboboxSelected>>', self.mode_select_param)

    
    def param_to_machine(self, ch_index, channel_save):
        if self.machine_param_type == 'current':
            self.ctrl.set_multiplier(ch_index, channel_save[0])

        elif self.machine_param_type == 'intensity':
            self.ctrl.set_const_intensity(ch_index, int(channel_save[1]))

        elif self.machine_param_type == 'strobe':
            self.ctrl.set_strobe_intensity(ch_index,channel_save[2])
            self.ctrl.set_strobe_width(ch_index, channel_save[3])

        elif self.machine_param_type == 'output delay':
            self.ctrl.set_output_delay(channel_save[0])

        elif self.machine_param_type == 'output width':
            self.ctrl.set_output_width(channel_save[1])

        elif self.machine_param_type == 'mode':
            self.ctrl.set_mode(channel_save[2])

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

        elif self.ch_sel_str== '5 - 8':
            self.current_multi_func(self.channel_5_save, self.ch_5_scalevar_a)
            self.param_to_machine(5, self.channel_5_save)

        elif self.ch_sel_str== '9 - 12':
            self.current_multi_func(self.channel_9_save, self.ch_9_scalevar_a)
            self.param_to_machine(9, self.channel_9_save)

        elif self.ch_sel_str== '13 - 16':
            self.current_multi_func(self.channel_13_save, self.ch_13_scalevar_a)
            self.param_to_machine(13, self.channel_13_save)

    def current_multi_group_B(self, event=None):
        self.machine_param_type = 'current'
        if self.ch_sel_str== '1 - 4':
            self.current_multi_func(self.channel_2_save, self.ch_2_scalevar_a)
            self.param_to_machine(2, self.channel_2_save)

        elif self.ch_sel_str== '5 - 8':
            self.current_multi_func(self.channel_6_save, self.ch_6_scalevar_a)
            self.param_to_machine(6, self.channel_6_save)

        elif self.ch_sel_str== '9 - 12':
            self.current_multi_func(self.channel_10_save, self.ch_10_scalevar_a)
            self.param_to_machine(10, self.channel_10_save)

        elif self.ch_sel_str== '13 - 16':
            self.current_multi_func(self.channel_14_save, self.ch_14_scalevar_a)
            self.param_to_machine(14, self.channel_14_save)

    def current_multi_group_C(self, event=None):
        self.machine_param_type = 'current'
        if self.ch_sel_str== '1 - 4':
            self.current_multi_func(self.channel_3_save, self.ch_3_scalevar_a)
            self.param_to_machine(3, self.channel_3_save)

        elif self.ch_sel_str== '5 - 8':
            self.current_multi_func(self.channel_7_save, self.ch_7_scalevar_a)
            self.param_to_machine(7, self.channel_7_save)

        elif self.ch_sel_str== '9 - 12':
            self.current_multi_func(self.channel_11_save, self.ch_11_scalevar_a)
            self.param_to_machine(11, self.channel_11_save)

        elif self.ch_sel_str== '13 - 16':
            self.current_multi_func(self.channel_15_save, self.ch_15_scalevar_a)
            self.param_to_machine(15, self.channel_15_save)

    def current_multi_group_D(self, event=None):
        self.machine_param_type = 'current'
        if self.ch_sel_str== '1 - 4':
            self.current_multi_func(self.channel_4_save, self.ch_4_scalevar_a)
            self.param_to_machine(4, self.channel_4_save)

        elif self.ch_sel_str== '5 - 8':
            self.current_multi_func(self.channel_8_save, self.ch_8_scalevar_a)
            self.param_to_machine(8, self.channel_8_save)

        elif self.ch_sel_str== '9 - 12':
            self.current_multi_func(self.channel_12_save, self.ch_12_scalevar_a)
            self.param_to_machine(12, self.channel_12_save)

        elif self.ch_sel_str== '13 - 16':
            self.current_multi_func(self.channel_16_save, self.ch_16_scalevar_a)
            self.param_to_machine(16, self.channel_16_save)

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

        elif self.ch_sel_str == '5 - 8':
            self.const_intensity_func(self.channel_5_save, self.ch_5_scalevar_b)
            self.param_to_machine(5, self.channel_5_save)

        elif self.ch_sel_str == '9 - 12':
            self.const_intensity_func(self.channel_9_save, self.ch_9_scalevar_b)
            self.param_to_machine(9, self.channel_9_save)

        elif self.ch_sel_str == '13 - 16':
            self.const_intensity_func(self.channel_13_save, self.ch_13_scalevar_b)
            self.param_to_machine(13, self.channel_13_save)

    def const_intensity_group_B(self, event=None):
        self.machine_param_type = 'intensity'

        if self.ch_sel_str== '1 - 4':
            self.const_intensity_func(self.channel_2_save, self.ch_2_scalevar_b)
            self.param_to_machine(2, self.channel_2_save)

        elif self.ch_sel_str== '5 - 8':
            self.const_intensity_func(self.channel_6_save, self.ch_6_scalevar_b)
            self.param_to_machine(6, self.channel_6_save)

        elif self.ch_sel_str== '9 - 12':
            self.const_intensity_func(self.channel_10_save, self.ch_10_scalevar_b)
            self.param_to_machine(10, self.channel_10_save)

        elif self.ch_sel_str== '13 - 16':
            self.const_intensity_func(self.channel_14_save, self.ch_14_scalevar_b)
            self.param_to_machine(14, self.channel_14_save)

    def const_intensity_group_C(self, event=None):
        self.machine_param_type = 'intensity'

        if self.ch_sel_str== '1 - 4':
            self.const_intensity_func(self.channel_3_save, self.ch_3_scalevar_b)
            self.param_to_machine(3, self.channel_3_save)

        elif self.ch_sel_str== '5 - 8':
            self.const_intensity_func(self.channel_7_save, self.ch_7_scalevar_b)
            self.param_to_machine(7, self.channel_7_save)

        elif self.ch_sel_str== '9 - 12':
            self.const_intensity_func(self.channel_11_save, self.ch_11_scalevar_b)
            self.param_to_machine(11, self.channel_11_save)

        elif self.ch_sel_str== '13 - 16':
            self.const_intensity_func(self.channel_15_save, self.ch_15_scalevar_b)
            self.param_to_machine(15, self.channel_15_save)

    def const_intensity_group_D(self, event=None):
        self.machine_param_type = 'intensity'

        if self.ch_sel_str== '1 - 4':
            self.const_intensity_func(self.channel_4_save, self.ch_4_scalevar_b)
            self.param_to_machine(4, self.channel_4_save)

        elif self.ch_sel_str== '5 - 8':
            self.const_intensity_func(self.channel_8_save, self.ch_8_scalevar_b)
            self.param_to_machine(8, self.channel_8_save)

        elif self.ch_sel_str== '9 - 12':
            self.const_intensity_func(self.channel_12_save, self.ch_12_scalevar_b)
            self.param_to_machine(12, self.channel_12_save)

        elif self.ch_sel_str== '13 - 16':
            self.const_intensity_func(self.channel_16_save, self.ch_16_scalevar_b)
            self.param_to_machine(16, self.channel_16_save)
    
    
    def strobe_param_func(self, channel_save, ch_entry_d_label
        , scalevar_c, scalevar_d):
        try:
            channel_save[2] = scalevar_c.get() #Strobe Intensity (0-1023)
        except:
            pass
        try:
            channel_save[3] = scalevar_d.get() #Strobe width (0-99999)
        except:
            pass
        ch_entry_d_label.set(str(np.divide(int(channel_save[3]), 100)) + ' ms')


    def strobe_param_group_A(self, event=None):
        self.machine_param_type = 'strobe'

        if self.ch_sel_str== '1 - 4':
            self.strobe_param_func(self.channel_1_save, self.ch_1_entry_d_label, 
                self.ch_1_scalevar_c, self.ch_1_scalevar_d)

            self.param_to_machine(1, self.channel_1_save)

        elif self.ch_sel_str== '5 - 8':
            self.strobe_param_func(self.channel_5_save, self.ch_5_entry_d_label, 
                self.ch_5_scalevar_c, self.ch_5_scalevar_d)

            self.param_to_machine(5, self.channel_5_save)

        elif self.ch_sel_str== '9 - 12':
            self.strobe_param_func(self.channel_9_save, self.ch_9_entry_d_label, 
                self.ch_9_scalevar_c, self.ch_9_scalevar_d)

            self.param_to_machine(9, self.channel_9_save)

        elif self.ch_sel_str== '13 - 16':
            self.strobe_param_func(self.channel_13_save, self.ch_13_entry_d_label, 
                self.ch_13_scalevar_c, self.ch_13_scalevar_d)

            self.param_to_machine(13, self.channel_13_save)

        # interval_spinbox_function()

    def strobe_param_group_B(self, event=None):
        self.machine_param_type = 'strobe'

        if self.ch_sel_str== '1 - 4':
            self.strobe_param_func(self.channel_2_save, self.ch_2_entry_d_label, 
                self.ch_2_scalevar_c, self.ch_2_scalevar_d)

            self.param_to_machine(2, self.channel_2_save)

        elif self.ch_sel_str== '5 - 8':
            self.strobe_param_func(self.channel_6_save, self.ch_6_entry_d_label, 
                self.ch_6_scalevar_c, self.ch_6_scalevar_d)

            self.param_to_machine(6, self.channel_6_save)

        elif self.ch_sel_str== '9 - 12':
            self.strobe_param_func(self.channel_10_save, self.ch_10_entry_d_label, 
                self.ch_10_scalevar_c, self.ch_10_scalevar_d)

            self.param_to_machine(10, self.channel_10_save)

        elif self.ch_sel_str== '13 - 16':
            self.strobe_param_func(self.channel_14_save, self.ch_14_entry_d_label, 
                self.ch_14_scalevar_c, self.ch_14_scalevar_d)

            self.param_to_machine(14, self.channel_14_save)

        # interval_spinbox_function()

    def strobe_param_group_C(self, event=None):
        self.machine_param_type = 'strobe'

        if self.ch_sel_str== '1 - 4':
            self.strobe_param_func(self.channel_3_save, self.ch_3_entry_d_label,
                self.ch_3_scalevar_c, self.ch_3_scalevar_d)

            self.param_to_machine(3, self.channel_3_save)

        elif self.ch_sel_str== '5 - 8':
            self.strobe_param_func(self.channel_7_save, self.ch_7_entry_d_label,
                self.ch_7_scalevar_c, self.ch_7_scalevar_d)

            self.param_to_machine(7, self.channel_7_save)

        elif self.ch_sel_str== '9 - 12':
            self.strobe_param_func(self.channel_11_save, self.ch_11_entry_d_label,
                self.ch_11_scalevar_c, self.ch_11_scalevar_d)

            self.param_to_machine(11, self.channel_11_save)

        elif self.ch_sel_str== '13 - 16':
            self.strobe_param_func(self.channel_15_save, self.ch_15_entry_d_label,
                self.ch_15_scalevar_c, self.ch_15_scalevar_d)

            self.param_to_machine(15, self.channel_15_save)

        # interval_spinbox_function()

    def strobe_param_group_D(self, event=None):
        self.machine_param_type = 'strobe'

        if self.ch_sel_str== '1 - 4':
            self.strobe_param_func(self.channel_4_save, self.ch_4_entry_d_label,
                self.ch_4_scalevar_c, self.ch_4_scalevar_d)

            self.param_to_machine(4, self.channel_4_save)

        elif self.ch_sel_str== '5 - 8':
            self.strobe_param_func(self.channel_8_save, self.ch_8_entry_d_label,
                self.ch_8_scalevar_c, self.ch_8_scalevar_d)

            self.param_to_machine(8, self.channel_8_save)

        elif self.ch_sel_str== '9 - 12':
            self.strobe_param_func(self.channel_12_save, self.ch_12_entry_d_label,
                self.ch_12_scalevar_c, self.ch_12_scalevar_d)

            self.param_to_machine(12, self.channel_12_save)

        elif self.ch_sel_str== '13 - 16':
            self.strobe_param_func(self.channel_16_save, self.ch_16_entry_d_label,
                self.ch_16_scalevar_c, self.ch_16_scalevar_d)

            self.param_to_machine(16, self.channel_16_save)


    def SQ_output_delay_func(self, channel_save, scalevar, ch_entry_label):
        try:
            channel_save[0] = scalevar.get() #Output Delay (0-99999)
        except:
            pass
        ch_entry_label.set(str(np.divide(int(channel_save[0]), 100)) + ' ms')

    def SQ_output_width_func(self, channel_save, scalevar, ch_entry_label):
        try:
            channel_save[1] = scalevar.get() #Output Width (0-99999)
        except:
            pass
        ch_entry_label.set(str(np.divide(int(channel_save[1]), 100)) + ' ms')

    def output_delay_param(self, event = None):
        self.machine_param_type = 'output delay'
        self.SQ_output_delay_func(self.channel_SQ_save, self.sq_output_delay_scalevar, self.sq_output_delay_label)
        self.param_to_machine(None, self.channel_SQ_save)
        #print(self.channel_SQ_save)

    def output_width_param(self, event = None):
        self.machine_param_type = 'output width'
        self.SQ_output_width_func(self.channel_SQ_save, self.sq_output_width_scalevar, self.sq_output_width_label)
        self.param_to_machine(None, self.channel_SQ_save)
        #print(self.channel_SQ_save)

    def mode_function(self, ch_mode, channel_save):
        if ch_mode.get() == 'Constant Mode':
            if channel_save[2] != 0:
                channel_save[2] = 0 #Mode (Constant = 0, Strobe = 1)
                self.STOP_SQ_strobe_frame_thread()

        elif ch_mode.get() == 'Strobe Mode':
            if channel_save[2] != 1:
                channel_save[2] = 1 #Mode (Constant = 0, Strobe = 1)
                self.STOP_SQ_strobe_frame_thread()


    def mode_select_param(self, event = None):
        self.machine_param_type = 'mode'
        self.mode_function(self.sq_ch_mode,self.channel_SQ_save)
        self.param_to_machine(None, self.channel_SQ_save)
        # print(self.channel_SQ_save)

    def SQ_strobe_frame(self):
        if self.sq_strobe_btn_click == False:
            self.sq_strobe_btn_click = True

            if self.sq_fr_arr[1] <100:
                self.sq_trigger_delay = np.divide(self.sq_fr_arr[1],100000)
            else:
                self.sq_trigger_delay = np.divide(self.sq_fr_arr[1],100000)

            self.delay_step = np.multiply(np.divide(self.sq_fr_arr[1],100000), 0.12)
            self.sq_strobe_frame_handle = threading.Thread(target=self.SQ_strobe_frame_thread, daemon = True)
            self.sq_strobe_frame_handle.start()
            
        else:
            pass

    def SQ_strobe_frame_thread(self):
        from main_GUI import main_GUI
        cam_active_str = main_GUI.class_cam_conn.active_gui_str
        _cam_class = main_GUI.class_cam_conn.active_gui
        self.sq_frame_delay_event.clear()

        if True == self.SQ_internal_strobe_bool():
            try:
                _cam_class.btn_save_sq['state'] = 'disable'
            except AttributeError:
                pass
            try:
                _cam_class.checkbtn_trigger_src['state'] = 'disable'
            except AttributeError:
                pass
                
            self.sq_frame_img_list *= 0
            _cam_class.clear_display_GUI_2()
            self.sq_frame_delay_event.wait(0.025)
            self.dll_LC20.Strobe()
            while not self.sq_frame_delay_event.isSet():
                if len(self.sq_frame_img_list) >= self.sq_fr_arr[0]:
                    self.sq_frame_delay_event.set()
                    break

                elif len(self.sq_frame_img_list) < self.sq_fr_arr[0]:
                    t1 = time.perf_counter()
                    if cam_active_str == 'Hikvision':
                        _cam_class.obj_cam_operation.Trigger_once()
                    elif cam_active_str == 'Crevis':
                        _cam_class.crevis_operation.Trigger_once()

                    t2 = time.perf_counter()

                    if 8 < len(self.sq_frame_img_list) < 10:
                        self.sq_frame_delay_event.wait(self.sq_trigger_delay - (t2-t1) - self.delay_step)#0.05)
                    else:
                        self.sq_frame_delay_event.wait(self.sq_trigger_delay - (t2-t1))

                    pass

            if len(self.sq_frame_img_list) == self.sq_fr_arr[0]:
                self.Internal_SQ_Fr_Disp()

            try:
                _cam_class.btn_save_sq['state'] = 'disable'
            except AttributeError:
                pass
            try:
                _cam_class.checkbtn_trigger_src['state'] = 'disable'
            except AttributeError:
                pass

        else:
            self.dll_LC20.Strobe()
            
        self.sq_strobe_btn_click = False

    def Internal_SQ_Fr_Disp(self):
        from main_GUI import main_GUI
        cam_active_str = main_GUI.class_cam_conn.active_gui_str
        _cam_class = main_GUI.class_cam_conn.active_gui
        if cam_active_str == 'Hikvision':
            _cam_class.obj_cam_operation.SQ_frame_display(self.sq_frame_img_list)
            _cam_class.obj_cam_operation.Auto_Save_SQ_Frame()
        elif cam_active_str == 'Crevis':
            _cam_class.crevis_operation.SQ_frame_display(self.sq_frame_img_list)
            _cam_class.crevis_operation.Auto_Save_SQ_Frame()
        
        _cam_class.SQ_fr_popout_load_list(sq_frame_img_list = self.sq_frame_img_list.copy())
        _cam_class.SQ_fr_popout_disp_func(sq_frame_img_list = self.sq_frame_img_list.copy())

        try:
            _cam_class.SQ_fr_sel.bind('<<ComboboxSelected>>', 
                lambda event: _cam_class.SQ_fr_popout_disp_func(sq_frame_img_list = self.sq_frame_img_list))
        except (AttributeError, tk.TclError):# as e:
            # print('Exception SQ Frame Popout, Internal Trigger: ', e)
            pass

    def STOP_SQ_strobe_frame_thread(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        self.sq_frame_delay_event.set()
        self.sq_frame_img_list *= 0
        self.sq_strobe_btn_click = False
        try:
            Stop_thread(self.sq_strobe_frame_handle)
        except Exception:
            pass

        try:
            _cam_class.btn_save_sq['state'] = 'normal'
        except AttributeError:
            pass
        try:
            _cam_class.checkbtn_trigger_src['state'] = 'normal'
        except AttributeError:
            pass

    def strobe_channel_repeat_ALL(self):
        self.dll_LC20.Strobe()

    def SQ_internal_strobe_bool(self):
        from main_GUI import main_GUI
        cam_active_str = main_GUI.class_cam_conn.active_gui_str
        _cam_class = main_GUI.class_cam_conn.active_gui

        strobe_mode_bool = False
        if self.channel_SQ_save[2] == 1:
            strobe_mode_bool = True


        if strobe_mode_bool == True:
            if cam_active_str is None:
                return False
            elif cam_active_str is not None and type(cam_active_str) == str:
                if cam_active_str == 'Hikvision':
                    if _cam_class.obj_cam_operation is not None and _cam_class.obj_cam_operation.trigger_mode == True and _cam_class.obj_cam_operation.b_start_grabbing == True and _cam_class.obj_cam_operation.trigger_src == 7:
                        return True
                    else:
                        return False
                elif cam_active_str == 'Crevis':
                    if _cam_class.crevis_operation is not None and _cam_class.crevis_operation.trigger_mode == True and _cam_class.crevis_operation.b_start_grabbing == True and _cam_class.crevis_operation.trigger_src == 'SOFTWARE':
                        return True
                    else:
                        return False
                else:
                    return False
        else:
            return False
    ###############################################################################################
    #6. REPEAT STROBE PARAMETERS
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

    def repeat_ALL_start_stop(self, event = None):
        if (self.repeat_ALL_status == True):
            self.interval_spinbox_function()
            self.thread_event_repeat_ALL.clear()
            self.repeat_ALL_handle = threading.Thread(target=self.repeat_ALL_func, args = (self.thread_event_repeat_ALL,))
            self.repeat_ALL_handle.start()

            widget_disable(self.infinity_radio_btn_2, self.finite_radio_btn_2, self.interval_entry_2)

            if self.repeat_mode_str == 'finite':
                widget_disable(self.repeat_number_spinbox_2)

            #print(repeat_ALL_handle)
        else:
            self.thread_event_repeat_ALL.set()
            try:
                Stop_thread(self.repeat_ALL_handle)
                print('Thread Stopped')
            except:
                pass

            widget_enable(self.infinity_radio_btn_2, self.finite_radio_btn_2, self.interval_entry_2)

            if self.repeat_mode_str == 'finite':
                widget_enable(self.repeat_number_spinbox_2)
            
            try:
                widget_enable(self.sq_strobe_btn)
            except (AttributeError, tk.TclError):
                pass

            #print(self.repeat_ALL_handle)

    ###############################################################################################
    #7. RESET LIGHT PARAMETERS
    def SQ_reset_ch(self, ch_arr, ch_index):
        self.ctrl.set_multiplier(ch_index, ch_arr[0])
        self.ctrl.set_const_intensity(ch_index, int(ch_arr[1]))
        self.ctrl.set_strobe_intensity(ch_index, ch_arr[2])
        self.ctrl.set_strobe_width(ch_index, ch_arr[3])

    def SQ_reset_output_mode(self, arr):
        self.ctrl.set_mode(arr[2])
        self.ctrl.set_output_delay(arr[0])
        self.ctrl.set_output_width(arr[1])

    def SQ_reset_frame(self, fr_arr, fr_int_arr):
        self.ctrl.SetNoOfFrame(fr_arr[0])
        self.ctrl.SetFrameWidth(fr_arr[1])

        self.ctrl.SetFrame(0, fr_int_arr[0])
        self.ctrl.SetFrame(1, fr_int_arr[1])
        self.ctrl.SetFrame(2, fr_int_arr[2])
        self.ctrl.SetFrame(3, fr_int_arr[3])
        self.ctrl.SetFrame(4, fr_int_arr[4])

        self.ctrl.SetFrame(5, fr_int_arr[5])
        self.ctrl.SetFrame(6, fr_int_arr[6])
        self.ctrl.SetFrame(7, fr_int_arr[7])
        self.ctrl.SetFrame(8, fr_int_arr[8])
        self.ctrl.SetFrame(9, fr_int_arr[9])

    def SQ_reset_arr_1(self, ch_arr): #reset values for each Channel
        ch_arr[0]=1
        ch_arr[1]=0
        ch_arr[2]=0
        ch_arr[3]=100
    
    def SQ_reset_arr_2(self, arr): #reset values for Output and Mode
        arr[0]=0 #Output Delay
        arr[1]=1000 #Output Width
        arr[2]=0 #Mode

    def SQ_reset_frame_arr(self, fr_arr, fr_int_arr):
        fr_arr[0] = 1
        fr_arr[1] = 50000
        fr_int_arr[0] = 0
        fr_int_arr[1] = 0
        fr_int_arr[2] = 0
        fr_int_arr[3] = 0

        fr_int_arr[4] = 0
        fr_int_arr[5] = 0
        fr_int_arr[6] = 0
        fr_int_arr[7] = 0

        fr_int_arr[8] = 0
        fr_int_arr[9] = 0
        fr_int_arr[10] = 0
        fr_int_arr[11] = 0

        fr_int_arr[12] = 0
        fr_int_arr[13] = 0
        fr_int_arr[14] = 0
        fr_int_arr[15] = 0

    def reset_all(self): #reset everything
        self.thread_reset_event.clear()

        self.SQ_reset_arr_1(self.channel_1_save)
        self.SQ_reset_arr_1(self.channel_2_save)
        self.SQ_reset_arr_1(self.channel_3_save)
        self.SQ_reset_arr_1(self.channel_4_save)
        self.SQ_reset_arr_1(self.channel_5_save)
        self.SQ_reset_arr_1(self.channel_6_save)
        self.SQ_reset_arr_1(self.channel_7_save)
        self.SQ_reset_arr_1(self.channel_8_save)
        self.SQ_reset_arr_1(self.channel_9_save)
        self.SQ_reset_arr_1(self.channel_10_save)
        self.SQ_reset_arr_1(self.channel_11_save)
        self.SQ_reset_arr_1(self.channel_12_save)
        self.SQ_reset_arr_1(self.channel_13_save)
        self.SQ_reset_arr_1(self.channel_14_save)
        self.SQ_reset_arr_1(self.channel_15_save)
        self.SQ_reset_arr_1(self.channel_16_save)

        self.SQ_reset_arr_2(self.channel_SQ_save)

        self.SQ_reset_frame_arr(self.sq_fr_arr, self.sq_fr_int_arr)

        #self.channel_on_select()
        try:
            if self.light_conn_status == True:
                self.SQ_reset_ch(self.channel_1_save, 1)
                self.SQ_reset_ch(self.channel_2_save, 2)
                self.SQ_reset_ch(self.channel_3_save, 3)
                self.SQ_reset_ch(self.channel_4_save, 4)
                self.SQ_reset_ch(self.channel_5_save, 5)
                self.SQ_reset_ch(self.channel_6_save, 6)
                self.SQ_reset_ch(self.channel_7_save, 7)
                self.SQ_reset_ch(self.channel_8_save, 8)
                self.SQ_reset_ch(self.channel_9_save, 9)
                self.SQ_reset_ch(self.channel_10_save, 10)
                self.SQ_reset_ch(self.channel_11_save, 11)
                self.SQ_reset_ch(self.channel_12_save, 12)
                self.SQ_reset_ch(self.channel_13_save, 13)
                self.SQ_reset_ch(self.channel_14_save, 14)
                self.SQ_reset_ch(self.channel_15_save, 15)
                self.SQ_reset_ch(self.channel_16_save, 16)

                self.SQ_reset_output_mode(self.channel_SQ_save)

                self.SQ_reset_frame(self.sq_fr_arr, self.sq_fr_int_arr)

        except Exception as e:
            print(e)
            pass
        self.thread_reset_event.set()

    ###############################################################################################
    #8. LOAD LIGHT PARAMETERS
    def load_parameter(self, event=None):
        self.thread_refresh_event.clear()
        try:
            self.ctrl.SQ_read_ch(self.channel_1_save, 1)
            self.ctrl.SQ_read_ch(self.channel_2_save, 2)
            self.ctrl.SQ_read_ch(self.channel_3_save, 3)
            self.ctrl.SQ_read_ch(self.channel_4_save, 4)

            self.ctrl.SQ_read_ch(self.channel_5_save, 5)
            self.ctrl.SQ_read_ch(self.channel_6_save, 6)
            self.ctrl.SQ_read_ch(self.channel_7_save, 7)
            self.ctrl.SQ_read_ch(self.channel_8_save, 8)

            self.ctrl.SQ_read_ch(self.channel_9_save, 9)
            self.ctrl.SQ_read_ch(self.channel_10_save, 10)
            self.ctrl.SQ_read_ch(self.channel_11_save, 11)
            self.ctrl.SQ_read_ch(self.channel_12_save, 12)

            self.ctrl.SQ_read_ch(self.channel_13_save, 13)
            self.ctrl.SQ_read_ch(self.channel_14_save, 14)
            self.ctrl.SQ_read_ch(self.channel_15_save, 15)
            self.ctrl.SQ_read_ch(self.channel_16_save, 16)
            
            self.ctrl.SQ_read_output_mode(self.channel_SQ_save)

            self.ctrl.SQ_read_frame(self.sq_fr_arr, self.sq_fr_int_arr)
        except:
            #This Exception Handling is used to Break the Thread and the GUI update loop!
            pass
        self.thread_refresh_event.set()
    ###############################################################################################
    #9. STOP ALL THREADS
    def Stop_Threads(self):
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



if __name__ == '__main__':
    from ScrolledCanvas import ScrolledCanvas
    import clr
    from PIL import ImageTk, Image
    code_PATH = os.getcwd()
    sys.path.append(code_PATH)

    clr.AddReference("LC20Library")
    from LC20Library import *

    def _icon_load_resize(img_PATH, img_folder, img_file, img_scale = 0, img_width = 0, img_height = 0):
        img = Image.open(img_PATH + "\\" + img_folder + "\\" + img_file)

        if img_scale !=0 and (img_width == 0 and img_height == 0):
            img = img.resize((round(img.size[0]*img_scale), round(img.size[1]*img_scale)))
            img = ImageTk.PhotoImage(img)
            return img

        if img_scale ==0 and (img_width != 0 and img_height != 0):
            img = img.resize((img_width, img_height))
            img = ImageTk.PhotoImage(img)
            return img

        else:
            pass

    main_window = tk.Tk()
    main_window.title('TMS Lite Software.exe')
    main_window.resizable(True, True)
    main_window_width = 890 #1080 #1280 #1080 #760       #890
    main_window_height = 600 #640 #720 #640 #720 #600    #600
    main_window.minsize(width=890, height=600)

    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()

    x_coordinate = int((screen_width/2) - (main_window_width/2))
    y_coordinate = int((screen_height/2) - (main_window_height/2))

    main_window.geometry("{}x{}+{}+{}".format(main_window_width, main_window_height, x_coordinate, y_coordinate))

    #main_panel = main_GUI(master = main_window, LC18_lib = LC18(), LC18KP_lib = LC18KP(), LC18SQ_lib =LC18SQ())
    main_lib = LC20SQ()
    print('main_lib: ', main_lib)
    ret = main_lib.ComportConnect(int(3))
    print('connect_status: ',ret)
    img_PATH = os.getcwd()

    infinity_icon = _icon_load_resize(img_PATH = img_PATH, img_folder = "TMS Icon", img_file = "infinity_2.png", img_scale = 0.04)
    
    scrolled_canvas = ScrolledCanvas(master = main_window, frame_w = 1500 -330 - 43, frame_h = 900, 
            canvas_x = 0, canvas_y = 0, window_bg = 'white', canvas_bg='white')

    scrolled_canvas.rmb_all_func()

    light_interface = LC20_GUI(scrolled_canvas.window_fr, main_lib, True, 'LC20', 'LC20', infinity_icon
            , None, None, width = 1500 - 330, height = 900, bg = 'white')
    light_interface.place(x=0, y=0, anchor = 'nw')

    main_window.mainloop()