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

from ctrl_LC18_lib import LC18_Control

code_PATH = os.getcwd()
sys.path.append(code_PATH + '\\MVS-Python\\MvImport')
from MvCameraControl_class import *

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

class LC18_SQ_GUI(tk.Frame):
    def __init__(self, master, dll_LC18, light_conn_status, firmware_model_sel, firmware_version_str, infinity_icon
        , thread_event_repeat = None, thread_event_repeat_ALL = None, window_icon = None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        #INITIALIZE GUI INTERFACE MAIN PANEL(S) to hold the widgets
        self.master = master
        self.dll_LC18 = dll_LC18
        self.light_conn_status =  light_conn_status

        self.firmware_model_sel = firmware_model_sel
        #print('self.firmware_model_sel: ', self.firmware_model_sel)
        self.firmware_version_str = firmware_version_str
        self.infinity_icon = infinity_icon
        self.window_icon = window_icon

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
        #arr_index: 6 = Channel Mode(Const, Strobe, Trigger), 7 = Channel Board Address, 8 = Channel ID number(0 - 16)
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

        self.sq_fr_arr = np.array([1,0]) #Frame Number #Frame Width
        self.sq_fr_int_arr = np.zeros((10),dtype=np.uint8) #Frame Int Value (base 10 from binary)
        self.sq_f0_arr = np.zeros((4), dtype=np.uint8) #Array for storing binary values on Frame Values
        self.sq_f1_arr = np.zeros((4), dtype=np.uint8)
        self.sq_f2_arr = np.zeros((4), dtype=np.uint8)
        self.sq_f3_arr = np.zeros((4), dtype=np.uint8)
        self.sq_f4_arr = np.zeros((4), dtype=np.uint8)
        self.sq_f5_arr = np.zeros((4), dtype=np.uint8)
        self.sq_f6_arr = np.zeros((4), dtype=np.uint8)
        self.sq_f7_arr = np.zeros((4), dtype=np.uint8)
        self.sq_f8_arr = np.zeros((4), dtype=np.uint8)
        self.sq_f9_arr = np.zeros((4), dtype=np.uint8)

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

        self.load_btn_click()

    
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

            self.LC18_interface()

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
    
    def SQ_Frame_Popout_Update(self):
        self.SQ_checkbox_update_widget()
        self.sq_fr_num_combobox.current(self.sq_fr_arr[0] - 1)
        self.sq_fr_width_var.set(self.sq_fr_arr[1])
        self.sq_fr_width_label_var.set(str(np.divide(self.sq_fr_arr[1], 100)) + ' ms')
        self.SQ_checkbox_state()


    def reset_btn_click(self):
        self.updating_bool = True
        # try:
        #     self.sq_frame_toplvl.destroy()
        # except Exception:
        #     pass
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

        if self.repeat_btn['text'] == 'STOP':
            self.repeat_status = False
            self.repeat_btn = self.repeat_btn_widget(self.repeat_status, self.repeat_btn)
            self.repeat_start_stop()

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
            #self.LC18_interface()
            self.channel_on_select()
            try:
                #self.SQ_checkbox_update_widget()
                self.SQ_Frame_Popout_Update()
            except: #(AttributeError, tk.TclError):
                pass
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

        self.ch_sel_btn1.place(x=139,y=0)

        self.main_control_gen()

        self.label_interval_var = tk.StringVar()
        self.interval_var = tk.StringVar()
        self.repeat_mode_var = tk.StringVar()
        self.repeat_number_var = tk.StringVar()

        self.repeat_control_gen()

        widget_bind_focus(self.repeat_btn)
        widget_bind_focus(self.infinity_radio_btn)
        widget_bind_focus(self.finite_radio_btn)
        widget_bind_focus(self.repeat_number_spinbox)

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

        self.RESET_ALL_button = tk.Button(self.main_control_frame, width = 10, relief = tk.GROOVE, activeforeground= 'white', fg="white", activebackground = 'navy', bg = 'royal blue'
              , text='RESET ALL', font = "Helvetica 11 bold")
        self.RESET_ALL_button['command'] = self.reset_btn_click
        self.RESET_ALL_button.place(x= 5, y = 160)

    def repeat_control_gen(self):
        #REPEAT STROBE CONTROL
        self.repeat_frame = tk.Frame(self.frame_panel_4, bg = 'DarkSlateGray2', highlightbackground="white", highlightthickness=1, highlightcolor="white")
        self.repeat_frame['width'] = 135 + 65 + 5
        self.repeat_frame['height'] = 115

        self.repeat_frame.place(x= 66 + 30, y = 2)

        tk.Label(self.repeat_frame, text = 'Interval: ', font = "Helvetica 11"
            , bg = 'DarkSlateGray2').place(x = 0, y = 0)
        tk.Label(self.repeat_frame, text = 'Repeat\nMode:', font = "Helvetica 11", bg = 'DarkSlateGray2', justify = 'left').place(x=100 + 20, y =0)

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

        elif self.repeat_btn['text'] == 'STOP':
            self.repeat_status = False

        self.repeat_btn = self.repeat_btn_widget(self.repeat_status, self.repeat_btn)
        self.repeat_start_stop()

    def repeat_mode_set(self, event=None):
        self.repeat_mode_str = self.repeat_mode_var.get()
        self.repeat_number_spinbox_state(self.repeat_number_spinbox)


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
        self.interval_entry.icursor('end')

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

        self.board_address()
        self.channel_1_save[7] = self.channel_2_save[7] = self.channel_3_save[7] = self.channel_4_save[7] = self.addr_index_a

        self.channel_frame_1 = self.generate_ch_frame(self.frame_panel_5, 1)
        (self.ch_1_entry_d_label, self.ch_1_entry_e_label, self.ch_1_entry_f_label, self.ch_1_mode, 
            self.ch_1_scalevar_a, self.ch_1_scalevar_b, self.ch_1_scalevar_d, self.ch_1_scalevar_e, self.ch_1_scalevar_f) = self.generate_panel(self.channel_frame_1,'Channel 1', 1, self.channel_1_save)

        self.channel_frame_2 = self.generate_ch_frame(self.frame_panel_5, 2)
        (self.ch_2_entry_d_label, self.ch_2_entry_e_label, self.ch_2_entry_f_label, self.ch_2_mode, 
            self.ch_2_scalevar_a, self.ch_2_scalevar_b, self.ch_2_scalevar_d, self.ch_2_scalevar_e, self.ch_2_scalevar_f) = self.generate_panel(self.channel_frame_2,'Channel 2', 2, self.channel_2_save)

        self.channel_frame_3 = self.generate_ch_frame(self.frame_panel_5, 3)
        (self.ch_3_entry_d_label, self.ch_3_entry_e_label, self.ch_3_entry_f_label, self.ch_3_mode, 
            self.ch_3_scalevar_a, self.ch_3_scalevar_b, self.ch_3_scalevar_d, self.ch_3_scalevar_e, self.ch_3_scalevar_f) = self.generate_panel(self.channel_frame_3,'Channel 3', 3, self.channel_3_save)

        self.channel_frame_4 = self.generate_ch_frame(self.frame_panel_5, 4)
        (self.ch_4_entry_d_label, self.ch_4_entry_e_label, self.ch_4_entry_f_label, self.ch_4_mode, 
            self.ch_4_scalevar_a, self.ch_4_scalevar_b, self.ch_4_scalevar_d, self.ch_4_scalevar_e, self.ch_4_scalevar_f) = self.generate_panel(self.channel_frame_4,'Channel 4', 4, self.channel_4_save)

        self.sq_fr_ctrl_frame = tk.Frame(self.frame_panel_1, width = 168, height = 115, bg = 'DarkSlateGray2', highlightbackground="white", highlightthickness=1, highlightcolor="white")
        self.sq_fr_ctrl_frame['width'] = 120 + 5#168
        self.sq_fr_ctrl_frame['height'] = 115
        self.sq_fr_ctrl_frame.place(x=5, y=220)
        tk.Label(self.sq_fr_ctrl_frame, text = 'Frame Settings', font = 'Helvetica 12 bold', bg = 'DarkSlateGray2').place(x=0, y=0)

        self.sq_fr_ctrl_btn = tk.Button(self.sq_fr_ctrl_frame, relief = tk.GROOVE, text = 'SQ Frame\nControl Panel', font = 'Helvetica 11', justify = 'center')
        #self.sq_fr_ctrl_btn.place(x=10, y=230)
        self.sq_fr_ctrl_btn.place(x=5, y=35)
        self.sq_fr_ctrl_btn['command'] = self.SQ_frame_popout

    def generate_ch_frame(self, tk_frame, ch_tag_num):
        W = 450
        H = 315
        if ch_tag_num == 1:
            channel_frame = tk.Frame(tk_frame, width = W, height = H, highlightbackground="black", highlightthickness=1)
            #channel_frame.place(x= 0, y = 210)
            channel_frame.place(x= 5, y = 5)
            return channel_frame

        elif ch_tag_num == 2:
            channel_frame = tk.Frame(tk_frame, width = W, height = H, highlightbackground="black", highlightthickness=1)
            #channel_frame.place(x= 185, y = 210)
            channel_frame.place(x= 460, y = 5)
            return channel_frame

        elif ch_tag_num == 3:
            channel_frame = tk.Frame(tk_frame, width = W, height = H, highlightbackground="black", highlightthickness=1)
            #channel_frame.place(x= 370, y = 210)
            channel_frame.place(x= 5, y = 325)
            return channel_frame

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
        #SQ HAS NO STROBE DELAY
        #####################################################################################################################
        ch_label_d = tk.Label(channel_frame, text = 'Strobe Width\n(0-9999)', font = 'Helvetica 11', width = 12)
        scalevar_d = tk.IntVar(value = channel_save[3])
        ch_entry_d = tk.Spinbox(master = channel_frame, width = 4, textvariable = scalevar_d, from_=0, to= 9999, increment = 1
                             , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        ch_entry_d['validate']='key'
        ch_entry_d['vcmd']=(ch_entry_d.register(validate_int_entry),'%d','%P','%S', True)

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

        ch_label_d.place(x= x_pos1, y = 130-50)
        ch_scalebar_d.place(x=x_pos2,y=130-50)
        ch_entry_d.place(x= x_pos3, y = 130-50)
        label_d.place(x= x_pos3-5, y = 153-50)

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

        ch_label_e.place(x= x_pos1, y = 180-50)
        ch_scalebar_e.place(x=x_pos2,y=180-50)
        ch_entry_e.place(x= x_pos3, y = 180-50)
        label_e.place(x= x_pos3-5, y = 203-50)

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

        ch_label_f.place(x= x_pos1, y = 230-50)
        ch_scalebar_f.place(x=x_pos2,y=230-50)
        ch_entry_f.place(x= x_pos3, y = 230-50)
        label_f.place(x= x_pos3-5, y = 253-50)

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


        return (ch_entry_d_label, ch_entry_e_label, ch_entry_f_label, ch_mode, 
            scalevar_a, scalevar_b, scalevar_d, scalevar_e, scalevar_f)

    ###############################################################################################
    #3. CONTROL PANEL INTERFACE 2
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
    #4. CONTROL PANEL INTERFACE 3 (SQ)
    def SQ_frame_popout(self):
        try:
            #print('try')
            check_bool = tk.Toplevel.winfo_exists(self.sq_frame_toplvl)
            if check_bool == 0:
                #print('not exist')
                self.sq_frame_toplvl = tk.Toplevel(master= self, width = 730, height = 250)
                self.sq_frame_toplvl.resizable(False, False)
                self.sq_frame_toplvl['bg'] = 'white'
                self.sq_frame_toplvl.title('LC18-SQ Frame')
                screen_width = self.sq_frame_toplvl.winfo_screenwidth()
                screen_height = self.sq_frame_toplvl.winfo_screenheight()
                x_coordinate = int((screen_width/2) - (730/2))
                y_coordinate = int((screen_height/2) - (250/2))
                self.sq_frame_toplvl.geometry("{}x{}+{}+{}".format(730, 250, x_coordinate, y_coordinate))

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
            self.sq_frame_toplvl = tk.Toplevel(master= self, width = 730, height = 250) #TKINTER GENERATION CANNOT WORK WITH THREAD
            self.sq_frame_toplvl.resizable(False, False)
            self.sq_frame_toplvl['bg'] = 'white'
            self.sq_frame_toplvl.title('LC18-SQ Frame')
            screen_width = self.sq_frame_toplvl.winfo_screenwidth()
            screen_height = self.sq_frame_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (730/2))
            y_coordinate = int((screen_height/2) - (250/2))
            self.sq_frame_toplvl.geometry("{}x{}+{}+{}".format(730, 250, x_coordinate, y_coordinate))

            try:
                self.sq_frame_toplvl.iconphoto(False, self.window_icon)
            except Exception:
                pass
                    
            self.SQ_frame_popout_init()

        

    def SQ_frame_popout_init(self):
        (self.sq_fr_main_frame, self.sq_fr_btn_group_frame, self.sq_checkbox_group_frame, 
            self.sq_fr_num_combobox, self.sq_fr_width_spinbox, self.sq_set_fr_btn, self.sq_trigger_btn, self.sq_strobe_btn) = self.SQ_panel_gen(self.sq_frame_toplvl, self.sq_fr_arr)

        #self.sq_fr_main_frame.place(x = 270, y = 805)
        self.sq_fr_main_frame.place(x=0,y=0)

        self.sq_fr_width_spinbox['command'] = self.SQ_frame_width_get
        self.sq_set_fr_btn['command'] = self.SQ_set_frame
        widget_bind_focus(self.sq_set_fr_btn)
        self.sq_trigger_btn['command'] = lambda: self.SQ_trigger(self.sq_trigger_btn)
        widget_bind_focus(self.sq_trigger_btn)
        self.sq_trigger_btn = self.SQ_trigger_condition(self.sq_trigger_btn, self.channel_1_save)
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

    def SQ_panel_gen(self, window_frame, arr):
        tk_frame_1 = tk.Frame(window_frame, width = 730, height = 250, highlightbackground="black", highlightthickness=1) # Main SQ tk_frame for FRAME functions
        #tk_frame_1.place(x = 270, y = 805)
        #tk_frame_1.place(x=0,y=0)
        tk.Label(tk_frame_1, text = 'Frame', font='Helvetica 14 bold').place(x = 0, y =0)

        #tk.Button(tk_frame_1, relief = tk.GROOVE, text = 'Popout', font='Helvetica 11', command = self.SQ_frame_popout).place(x= 80, y=0)


        tk_frame_2 = tk.Frame(tk_frame_1, width = 725, height = 55)#, bg = 'green') # tk_frame to hold the SQ FRAME Parameters Widgets and Buttons.
        tk_frame_2.place(x = 0, y = 35)


        tk_frame_3 = tk.Frame(tk_frame_1, width = 600, height = 155)#, bg = 'purple') # tk_frame to hold the SQ FRAME checkboxes and CH1, CH2, CH3, and CH4 labels
        tk_frame_3.place(x = 0, y = 90)#y = 80)
        ######################################################################################
        #tk_frame_2
        tk.Label(tk_frame_2, text = 'No. of Frame:', font='Helvetica 11').place(x = 0, y = 5)

        number_list = ['1','2','3','4','5','6','7','8','9','10']
        tk_frame_1.option_add('*TCombobox*Listbox.font', ('Helvetica', '11'))
        combobox_1 = ttk.Combobox(tk_frame_2, values=number_list, width = 3, state='readonly', font = 'Helvetica 11')
        combobox_1.place(x = 100, y = 5)
        combobox_1.current(self.sq_fr_arr[0] - 1)

        tk.Label(tk_frame_2, text = 'Frame Width:\n(0-9999)', font = 'Helvetica 11').place(x = 180, y = 5)

        self.sq_fr_width_var = tk.StringVar()

        spinbox_1 = tk.Spinbox(master = tk_frame_2, width = 4, from_=0, to= 9999, textvariable = self.sq_fr_width_var
                                     , highlightbackground="black", highlightthickness=1, font = 'Helvetica 11')
        spinbox_1.place(x = 280, y = 3)

        self.sq_fr_width_var.set(self.sq_fr_arr[1])

        self.sq_fr_width_label_var = tk.StringVar()

        label_1 = tk.Label(tk_frame_2, textvariable = self.sq_fr_width_label_var, font = 'Helvetica 11 italic') #Label frame width

        self.sq_fr_width_label_var.set(str(np.divide(arr[1], 100)) + ' ms')
        label_1.place(x = 280, y = 27)

        button_1 = tk.Button(tk_frame_2,relief = tk.GROOVE, width = 8,text = 'Set Frame', font = 'Helvetica 11') #self.sq_set_fr_btn
        button_1.place(x = 390, y =10)

        button_2 = tk.Button(tk_frame_2,relief = tk.GROOVE, width = 14, font='Helvetica 11 bold') #self.sq_trigger_btn
        button_2 = self.SQ_trigger_btn_init(button_2)
        button_2.place(x = 590, y =10)

        button_3 = tk.Button(tk_frame_2,relief = tk.GROOVE, width = 10, text = 'Strobe Frame', font='Helvetica 11') #self.sq_strobe_btn
        button_3.place(x = 482, y =10)

        ######################################################################################
        #tk_frame_3
        tk.Label(tk_frame_3, text = 'CH1', font='Helvetica 11').place(x = 10, y = 25 + 3) 
        tk.Label(tk_frame_3, text = 'CH2', font='Helvetica 11').place(x = 10, y = 55 + 3) 
        tk.Label(tk_frame_3, text = 'CH3', font='Helvetica 11').place(x = 10, y = 85 + 3) 
        tk.Label(tk_frame_3, text = 'CH4', font='Helvetica 11').place(x = 10, y = 115 + 3) 

        return tk_frame_1, tk_frame_2, tk_frame_3, combobox_1, spinbox_1, button_1, button_2, button_3

    def SQ_checkbox_frame_gen(self, tk_frame, frame_index):
        place_x = 0
        x_spacing = int(np.multiply(frame_index, 52))
        place_y = 5
        checkbox_frame = tk.Frame(tk_frame, width = 50, height = 140, bg="gray76", highlightbackground="black", highlightthickness=1)
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
        self.ctrl.SQ_SetNoOfFrame(self.sq_fr_arr[0])

    def SQ_frame_width_get(self, event=None):
        try:
            curr_val = int(self.sq_fr_width_spinbox.get())
            if curr_val > 9999:
                self.sq_fr_width_var.set(9999)
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
        self.ctrl.SQ_SetFrameWidth(self.sq_fr_arr[1])

    def SQ_frame_width_keypress(self, event = None):
        try:
            curr_val = int(self.sq_fr_width_spinbox.get())
            if curr_val > 9999:
                self.sq_fr_width_var.set(9999)
            elif curr_val < 0:
                self.sq_fr_width_var.set(0)
        except ValueError:
            pass

    def SQ_set_frame(self, event=None):
        for i in range (0, self.sq_fr_arr[0]):
            #print(int(i), self.sq_fr_int_arr[i])
            self.ctrl.SQ_SetFrame(int(i), self.sq_fr_int_arr[i])

    def SQ_trigger_condition(self, button, channel_save):
        if channel_save[6] == 2:
            button['state'] = 'normal'
            button = self.SQ_trigger_btn_init(button)
            # self.ctrl.SQ_Trigger(0)
        else:
            button['state'] = 'disabled'
            button = self.SQ_trigger_btn_init(button)
            # self.ctrl.SQ_Trigger(0)

        return button

    def SQ_trigger(self, btn):
        if btn['text'] == 'START TRIGGER':
            btn['text'] = 'STOP TRIGGER'
            btn['activebackground'] = 'red3'
            btn['bg'] = 'red'
            btn['activeforeground'] = 'white'
            btn['fg'] = 'white'
            self.ctrl.SQ_Trigger(1)

        elif btn['text'] == 'STOP TRIGGER':
            btn['text'] = 'START TRIGGER'
            btn['activebackground'] = 'forest green'
            btn['bg'] = 'green3'
            btn['activeforeground'] = 'white'
            btn['fg'] = 'white'
            # self.ctrl.SQ_Trigger(0)# This is not working for SQ System Setup with External Motor, so...
            self.ctrl.set_mode(None, 1)
            self.ctrl.set_mode(None, 2)
            #print('Trigger stop')

    def SQ_trigger_btn_init(self, btn):
        btn['text'] = 'START TRIGGER'
        btn['activebackground'] = 'forest green'
        btn['bg'] = 'green3'
        btn['activeforeground'] = 'white'
        btn['fg'] = 'white'
        return btn

    def SQ_checkbox_click_v2(self, f_n_arr, fr_int_arr, fr_index, *tk_intvar_args):
        #where n is the the frame number (e.g. f0, f1, etc.)
        for i, intvar in enumerate(tk_intvar_args):
            f_n_arr[i] = intvar.get()
            #print(f_n_arr)
        #print(f_n_arr)
        fr_int_arr[fr_index] = binary_to_dec_v2(f_n_arr[0],f_n_arr[1],f_n_arr[2],f_n_arr[3], reverse_str = True)

        #print('int fr:', fr_index)
        #print ('int val:',fr_int_arr)
        self.ctrl.SQ_SetFrame(int(fr_index), fr_int_arr[fr_index])

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
        #print(sq_arr.shape)
        #print(sq_arr)
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
            self.ch1_status_f0,self.ch2_status_f0, self.ch3_status_f0, self.ch4_status_f0)

        self.SQ_checkbox_update_func(self.sq_f1_arr, self.sq_fr_int_arr[1],
            self.ch1_status_f1,self.ch2_status_f1, self.ch3_status_f1, self.ch4_status_f1)

        self.SQ_checkbox_update_func(self.sq_f2_arr, self.sq_fr_int_arr[2],
            self.ch1_status_f2,self.ch2_status_f2, self.ch3_status_f2, self.ch4_status_f2)

        self.SQ_checkbox_update_func(self.sq_f3_arr, self.sq_fr_int_arr[3],
            self.ch1_status_f3,self.ch2_status_f3, self.ch3_status_f3, self.ch4_status_f3)

        self.SQ_checkbox_update_func(self.sq_f4_arr, self.sq_fr_int_arr[4],
            self.ch1_status_f4,self.ch2_status_f4, self.ch3_status_f4, self.ch4_status_f4)

        self.SQ_checkbox_update_func(self.sq_f5_arr, self.sq_fr_int_arr[5],
            self.ch1_status_f5,self.ch2_status_f5, self.ch3_status_f5, self.ch4_status_f5)

        self.SQ_checkbox_update_func(self.sq_f6_arr, self.sq_fr_int_arr[6],
            self.ch1_status_f6,self.ch2_status_f6, self.ch3_status_f6, self.ch4_status_f6)

        self.SQ_checkbox_update_func(self.sq_f7_arr, self.sq_fr_int_arr[7],
            self.ch1_status_f7,self.ch2_status_f7, self.ch3_status_f7, self.ch4_status_f7)

        self.SQ_checkbox_update_func(self.sq_f8_arr, self.sq_fr_int_arr[8],
            self.ch1_status_f8,self.ch2_status_f8, self.ch3_status_f8, self.ch4_status_f8)

        self.SQ_checkbox_update_func(self.sq_f9_arr, self.sq_fr_int_arr[9],
            self.ch1_status_f9,self.ch2_status_f9, self.ch3_status_f9, self.ch4_status_f9)

    def SQ_Frame_Popout_Update(self):
        self.SQ_checkbox_update_widget()
        self.sq_fr_num_combobox.current(self.sq_fr_arr[0] - 1)
        self.sq_fr_width_var.set(self.sq_fr_arr[1])
        self.sq_fr_width_label_var.set(str(np.divide(self.sq_fr_arr[1], 100)) + ' ms')
        self.SQ_checkbox_state()

    def SQ_checkbox(self):
        #print(self.sq_fr_int_arr)
        arr_size = 4
        (self.sq_f0_arr, self.ch1_status_f0,self.ch2_status_f0, self.ch3_status_f0, self.ch4_status_f0) = self.SQ_checkbox_param(self.sq_f0_arr, self.sq_fr_int_arr[0], arr_size)

        #print(self.SQ_checkbox_param(self.sq_f0_arr, self.sq_fr_int_arr[0], 16))
        #self.sq_fr_int_arr[1] = 100
        (self.sq_f1_arr, self.ch1_status_f1,self.ch2_status_f1, self.ch3_status_f1, self.ch4_status_f1) = self.SQ_checkbox_param(self.sq_f1_arr, self.sq_fr_int_arr[1], arr_size)

        (self.sq_f2_arr, self.ch1_status_f2,self.ch2_status_f2, self.ch3_status_f2, self.ch4_status_f2) = self.SQ_checkbox_param(self.sq_f2_arr, self.sq_fr_int_arr[2], arr_size)

        (self.sq_f3_arr, self.ch1_status_f3,self.ch2_status_f3, self.ch3_status_f3, self.ch4_status_f3) = self.SQ_checkbox_param(self.sq_f3_arr, self.sq_fr_int_arr[3], arr_size)

        (self.sq_f4_arr, self.ch1_status_f4,self.ch2_status_f4, self.ch3_status_f4, self.ch4_status_f4) = self.SQ_checkbox_param(self.sq_f4_arr, self.sq_fr_int_arr[4], arr_size)

        (self.sq_f5_arr, self.ch1_status_f5,self.ch2_status_f5, self.ch3_status_f5, self.ch4_status_f5) = self.SQ_checkbox_param(self.sq_f5_arr, self.sq_fr_int_arr[5], arr_size)

        (self.sq_f6_arr, self.ch1_status_f6,self.ch2_status_f6, self.ch3_status_f6, self.ch4_status_f6) = self.SQ_checkbox_param(self.sq_f6_arr, self.sq_fr_int_arr[6], arr_size)

        (self.sq_f7_arr, self.ch1_status_f7,self.ch2_status_f7, self.ch3_status_f7, self.ch4_status_f7) = self.SQ_checkbox_param(self.sq_f7_arr, self.sq_fr_int_arr[7], arr_size)

        (self.sq_f8_arr, self.ch1_status_f8,self.ch2_status_f8, self.ch3_status_f8, self.ch4_status_f8) = self.SQ_checkbox_param(self.sq_f8_arr, self.sq_fr_int_arr[8], arr_size)

        (self.sq_f9_arr, self.ch1_status_f9,self.ch2_status_f9, self.ch3_status_f9, self.ch4_status_f9) = self.SQ_checkbox_param(self.sq_f9_arr, self.sq_fr_int_arr[9], arr_size)

        ################################################################################################################################################
        #F0
        (self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_0,
            self.ch1_status_f0,self.ch2_status_f0, self.ch3_status_f0, self.ch4_status_f0)

        self.ch1_box_f0['command'] = self.ch2_box_f0['command'] = self.ch3_box_f0['command'] = self.ch4_box_f0['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f0_arr, self.sq_fr_int_arr, 0, 
            self.ch1_status_f0,self.ch2_status_f0, self.ch3_status_f0, self.ch4_status_f0)

        self.SQ_checkbox_bind_focus(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0)

        ################################################################################################################################################
        #F1
        (self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_1,
            self.ch1_status_f1,self.ch2_status_f1, self.ch3_status_f1, self.ch4_status_f1)

        self.ch1_box_f1['command'] = self.ch2_box_f1['command'] = self.ch3_box_f1['command'] = self.ch4_box_f1['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f1_arr, self.sq_fr_int_arr, 1, 
            self.ch1_status_f1,self.ch2_status_f1, self.ch3_status_f1, self.ch4_status_f1)

        self.SQ_checkbox_bind_focus(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1)

        ################################################################################################################################################
        #F2
        (self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_2,
            self.ch1_status_f2,self.ch2_status_f2, self.ch3_status_f2, self.ch4_status_f2)

        self.ch1_box_f2['command'] = self.ch2_box_f2['command'] = self.ch3_box_f2['command'] = self.ch4_box_f2['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f2_arr, self.sq_fr_int_arr, 2, 
            self.ch1_status_f2,self.ch2_status_f2, self.ch3_status_f2, self.ch4_status_f2)

        self.SQ_checkbox_bind_focus(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2)
        
        ################################################################################################################################################
        #F3
        (self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_3,
            self.ch1_status_f3,self.ch2_status_f3, self.ch3_status_f3, self.ch4_status_f3)

        self.ch1_box_f3['command'] = self.ch2_box_f3['command'] = self.ch3_box_f3['command'] = self.ch4_box_f3['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f3_arr, self.sq_fr_int_arr, 3, 
            self.ch1_status_f3,self.ch2_status_f3, self.ch3_status_f3, self.ch4_status_f3)

        self.SQ_checkbox_bind_focus(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3)

        ################################################################################################################################################
        #F4
        (self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_4,
            self.ch1_status_f4,self.ch2_status_f4, self.ch3_status_f4, self.ch4_status_f4)

        self.ch1_box_f4['command'] = self.ch2_box_f4['command'] = self.ch3_box_f4['command'] = self.ch4_box_f4['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f4_arr, self.sq_fr_int_arr, 4, 
            self.ch1_status_f4,self.ch2_status_f4, self.ch3_status_f4, self.ch4_status_f4)

        self.SQ_checkbox_bind_focus(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4)

        ################################################################################################################################################
        #F5
        (self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_5,
            self.ch1_status_f5,self.ch2_status_f5, self.ch3_status_f5, self.ch4_status_f5)

        self.ch1_box_f5['command'] = self.ch2_box_f5['command'] = self.ch3_box_f5['command'] = self.ch4_box_f5['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f5_arr, self.sq_fr_int_arr, 5, 
            self.ch1_status_f5,self.ch2_status_f5, self.ch3_status_f5, self.ch4_status_f5)

        self.SQ_checkbox_bind_focus(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5)

        ################################################################################################################################################
        #F6
        (self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_6,
            self.ch1_status_f6,self.ch2_status_f6, self.ch3_status_f6, self.ch4_status_f6)

        self.ch1_box_f6['command'] = self.ch2_box_f6['command'] = self.ch3_box_f6['command'] = self.ch4_box_f6['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f6_arr, self.sq_fr_int_arr, 6, 
            self.ch1_status_f6,self.ch2_status_f6, self.ch3_status_f6, self.ch4_status_f6)

        self.SQ_checkbox_bind_focus(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6)

        ################################################################################################################################################
        #F7
        (self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_7,
            self.ch1_status_f7,self.ch2_status_f7, self.ch3_status_f7, self.ch4_status_f7)

        self.ch1_box_f7['command'] = self.ch2_box_f7['command'] = self.ch3_box_f7['command'] = self.ch4_box_f7['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f7_arr, self.sq_fr_int_arr, 7, 
            self.ch1_status_f7,self.ch2_status_f7, self.ch3_status_f7, self.ch4_status_f7)

        self.SQ_checkbox_bind_focus(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7)

        ################################################################################################################################################
        #F8
        (self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_8,
            self.ch1_status_f8,self.ch2_status_f8, self.ch3_status_f8, self.ch4_status_f8)

        self.ch1_box_f8['command'] = self.ch2_box_f8['command'] = self.ch3_box_f8['command'] = self.ch4_box_f8['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f8_arr, self.sq_fr_int_arr, 8, 
            self.ch1_status_f8,self.ch2_status_f8, self.ch3_status_f8, self.ch4_status_f8)

        self.SQ_checkbox_bind_focus(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8)

        ################################################################################################################################################
        #F9
        (self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9) = \
        self.SQ_checkbox_gen_v2(self.sq_checkbox_frame_9,
            self.ch1_status_f9,self.ch2_status_f9, self.ch3_status_f9, self.ch4_status_f9)

        self.ch1_box_f9['command'] = self.ch2_box_f9['command'] = self.ch3_box_f9['command'] = self.ch4_box_f9['command'] =\
        lambda: self.SQ_checkbox_click_v2(self.sq_f9_arr, self.sq_fr_int_arr, 9, 
            self.ch1_status_f9,self.ch2_status_f9, self.ch3_status_f9, self.ch4_status_f9)

        self.SQ_checkbox_bind_focus(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9)

    def SQ_checkbox_state(self, event=None):
        if self.sq_fr_arr[0] == 1:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0)

            widget_disable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1)
            widget_disable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2)
            widget_disable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3)
            widget_disable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4)
            widget_disable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5)
            widget_disable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6)
            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9)

        elif self.sq_fr_arr[0] == 2:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1)

            widget_disable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2)
            widget_disable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3)
            widget_disable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4)
            widget_disable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5)
            widget_disable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6)
            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9)

        elif self.sq_fr_arr[0] == 3:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2)

            widget_disable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3)
            widget_disable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4)
            widget_disable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5)
            widget_disable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6)
            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9)

        elif self.sq_fr_arr[0] == 4:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3)

            widget_disable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4)
            widget_disable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5)
            widget_disable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6)
            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9)

        elif self.sq_fr_arr[0] == 5:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4)

            widget_disable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5)
            widget_disable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6)
            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9)

        elif self.sq_fr_arr[0] == 6:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5)

            widget_disable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6)
            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9)

        elif self.sq_fr_arr[0] == 7:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6)

            widget_disable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7)
            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9)

        elif self.sq_fr_arr[0] == 8:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6)
            widget_enable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7)

            widget_disable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8)
            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9)

        elif self.sq_fr_arr[0] == 9:
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6)
            widget_enable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7)
            widget_enable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8)

            widget_disable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9)

        elif self.sq_fr_arr[0] == 10:         
            widget_enable(self.ch1_box_f0, self.ch2_box_f0, self.ch3_box_f0, self.ch4_box_f0)
            widget_enable(self.ch1_box_f1, self.ch2_box_f1, self.ch3_box_f1, self.ch4_box_f1)
            widget_enable(self.ch1_box_f2, self.ch2_box_f2, self.ch3_box_f2, self.ch4_box_f2)
            widget_enable(self.ch1_box_f3, self.ch2_box_f3, self.ch3_box_f3, self.ch4_box_f3)
            widget_enable(self.ch1_box_f4, self.ch2_box_f4, self.ch3_box_f4, self.ch4_box_f4)
            widget_enable(self.ch1_box_f5, self.ch2_box_f5, self.ch3_box_f5, self.ch4_box_f5)
            widget_enable(self.ch1_box_f6, self.ch2_box_f6, self.ch3_box_f6, self.ch4_box_f6)
            widget_enable(self.ch1_box_f7, self.ch2_box_f7, self.ch3_box_f7, self.ch4_box_f7)
            widget_enable(self.ch1_box_f8, self.ch2_box_f8, self.ch3_box_f8, self.ch4_box_f8)
            widget_enable(self.ch1_box_f9, self.ch2_box_f9, self.ch3_box_f9, self.ch4_box_f9)

    ###############################################################################################
    #5. LIGHT CONTROL FUNCTIONS
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


    def param_to_machine(self, ch_index, channel_save):
        self.ctrl.select_address(channel_save[7])

        if self.machine_param_type == 'current':
            self.ctrl.set_multiplier(ch_index, channel_save[0])

        elif self.machine_param_type == 'intensity':
            self.ctrl.set_const_intensity(ch_index, int(channel_save[1]))

        elif self.machine_param_type == 'strobe':
            self.ctrl.set_strobe_width(ch_index, channel_save[3])

        elif self.machine_param_type == 'output':
            #self.ctrl.set_output(ch_index, channel_save[4], channel_save[5])
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
    
    
    def strobe_param_func(self, channel_save, ch_entry_d_label, scalevar_d):
        try:
            channel_save[3] = scalevar_d.get() #Strobe width (0-9999)
        except:
            pass
        ch_entry_d_label.set(str(np.divide(int(channel_save[3]), 100)) + ' ms')

    def strobe_param_group_A(self, event=None):
        self.machine_param_type = 'strobe'

        if self.ch_sel_str== '1 - 4':
            self.strobe_param_func(self.channel_1_save, self.ch_1_entry_d_label, self.ch_1_scalevar_d)

            self.param_to_machine(1, self.channel_1_save)
        # interval_spinbox_function()

    def strobe_param_group_B(self, event=None):
        self.machine_param_type = 'strobe'

        if self.ch_sel_str== '1 - 4':
            self.strobe_param_func(self.channel_2_save, self.ch_2_entry_d_label, self.ch_2_scalevar_d)

            self.param_to_machine(2, self.channel_2_save)
        # interval_spinbox_function()

    def strobe_param_group_C(self, event=None):
        self.machine_param_type = 'strobe'

        if self.ch_sel_str== '1 - 4':
            self.strobe_param_func(self.channel_3_save, self.ch_3_entry_d_label, self.ch_3_scalevar_d)

            self.param_to_machine(3, self.channel_3_save)
        # interval_spinbox_function()

    def strobe_param_group_D(self, event=None):
        self.machine_param_type = 'strobe'

        if self.ch_sel_str== '1 - 4':
            self.strobe_param_func(self.channel_4_save, self.ch_4_entry_d_label, self.ch_4_scalevar_d)

            self.param_to_machine(4, self.channel_4_save)
        # interval_spinbox_function()

    
    def SQ_output_param_sync(self, ref_save_arr, target_save_arr, target_scalevar_e, target_scalevar_f, target_label_e, target_label_f):
        target_save_arr[4] = ref_save_arr[4]
        target_save_arr[5] = ref_save_arr[5]

        target_scalevar_e.set(target_save_arr[4])
        target_scalevar_f.set(target_save_arr[5])

        target_label_e.set(str(np.divide(int(target_save_arr[4]), 100)) + ' ms')
        target_label_f.set(str(np.divide(int(target_save_arr[5]), 100)) + ' ms')

    def output_param_func(self, channel_save, ch_entry_e_label, ch_entry_f_label
        , scalevar_e, scalevar_f):
        try:
            channel_save[4] = scalevar_e.get() #Strobe Delay (0-9999)
        except:
            pass
        try:
            channel_save[5] = scalevar_f.get() #Strobe width (0-9999)
        except:
            pass

        ch_entry_e_label.set(str(np.divide(int(channel_save[4]), 100)) + ' ms')
        ch_entry_f_label.set(str(np.divide(int(channel_save[5]), 100)) + ' ms')

        #print(channel_save)

    def output_param_group_A(self, event=None):
        self.machine_param_type = 'output'

        if self.ch_sel_str== '1 - 4':
            self.output_param_func(self.channel_1_save, self.ch_1_entry_e_label, self.ch_1_entry_f_label, self.ch_1_scalevar_e, self.ch_1_scalevar_f)

            self.param_to_machine(None, self.channel_1_save)
            
            self.SQ_output_param_sync(self.channel_1_save, self.channel_2_save, self.ch_2_scalevar_e, self.ch_2_scalevar_f, self.ch_2_entry_e_label, self.ch_2_entry_f_label)
            self.SQ_output_param_sync(self.channel_1_save, self.channel_3_save, self.ch_3_scalevar_e, self.ch_3_scalevar_f, self.ch_3_entry_e_label, self.ch_3_entry_f_label)
            self.SQ_output_param_sync(self.channel_1_save, self.channel_4_save, self.ch_4_scalevar_e, self.ch_4_scalevar_f, self.ch_4_entry_e_label, self.ch_4_entry_f_label)

    def output_param_group_B(self, event=None):
        self.machine_param_type = 'output'

        if self.ch_sel_str== '1 - 4':
            self.output_param_func(self.channel_2_save, self.ch_2_entry_e_label, self.ch_2_entry_f_label,self.ch_2_scalevar_e, self.ch_2_scalevar_f)

            self.param_to_machine(None, self.channel_2_save)

            self.SQ_output_param_sync(self.channel_2_save, self.channel_1_save, self.ch_1_scalevar_e, self.ch_1_scalevar_f, self.ch_1_entry_e_label, self.ch_1_entry_f_label)
            self.SQ_output_param_sync(self.channel_2_save, self.channel_3_save, self.ch_3_scalevar_e, self.ch_3_scalevar_f, self.ch_3_entry_e_label, self.ch_3_entry_f_label)
            self.SQ_output_param_sync(self.channel_2_save, self.channel_4_save, self.ch_4_scalevar_e, self.ch_4_scalevar_f, self.ch_4_entry_e_label, self.ch_4_entry_f_label)

    def output_param_group_C(self, event=None):
        self.machine_param_type = 'output'

        if self.ch_sel_str== '1 - 4':
            self.output_param_func(self.channel_3_save, self.ch_3_entry_e_label, self.ch_3_entry_f_label,self.ch_3_scalevar_e, self.ch_3_scalevar_f)

            self.param_to_machine(None, self.channel_3_save)
            
            self.SQ_output_param_sync(self.channel_3_save, self.channel_1_save, self.ch_1_scalevar_e, self.ch_1_scalevar_f, self.ch_1_entry_e_label, self.ch_1_entry_f_label)
            self.SQ_output_param_sync(self.channel_3_save, self.channel_2_save, self.ch_2_scalevar_e, self.ch_2_scalevar_f, self.ch_2_entry_e_label, self.ch_2_entry_f_label)
            self.SQ_output_param_sync(self.channel_3_save, self.channel_4_save, self.ch_4_scalevar_e, self.ch_4_scalevar_f, self.ch_4_entry_e_label, self.ch_4_entry_f_label)

    def output_param_group_D(self, event=None):
        self.machine_param_type = 'output'

        if self.ch_sel_str== '1 - 4':
            self.output_param_func(self.channel_4_save, self.ch_4_entry_e_label, self.ch_4_entry_f_label,self.ch_4_scalevar_e, self.ch_4_scalevar_f)

            self.param_to_machine(None, self.channel_4_save)

            self.SQ_output_param_sync(self.channel_4_save, self.channel_1_save, self.ch_1_scalevar_e, self.ch_1_scalevar_f, self.ch_1_entry_e_label, self.ch_1_entry_f_label)
            self.SQ_output_param_sync(self.channel_4_save, self.channel_2_save, self.ch_2_scalevar_e, self.ch_2_scalevar_f, self.ch_2_entry_e_label, self.ch_2_entry_f_label)
            self.SQ_output_param_sync(self.channel_4_save, self.channel_3_save, self.ch_3_scalevar_e, self.ch_3_scalevar_f, self.ch_3_entry_e_label, self.ch_3_entry_f_label)

    def SQ_mode_select_sync(self, ref_save_arr, target_save_arr, target_ch_mode):
        target_save_arr[6] = ref_save_arr[6]

        if target_save_arr[6] == 0:
            target_ch_mode.current(0)
        elif target_save_arr[6] == 1:
            target_ch_mode.current(1)
        elif target_save_arr[6] == 2:
            target_ch_mode.current(2)

    def mode_function(self, ch_mode, channel_save):
        #global self.sq_trigger_btn

        if ch_mode.get() == 'Constant Mode':
            if channel_save[6] != 0:
                channel_save[6] = 0 #Mode (Constant = 0, Strobe = 1, Trigger = 2)
                self.STOP_SQ_strobe_frame_thread()

        elif ch_mode.get() == 'Strobe Mode':
            if channel_save[6] != 1:
                channel_save[6] = 1 #Mode (Constant = 0, Strobe = 1, Trigger = 2)
                self.STOP_SQ_strobe_frame_thread()

        elif ch_mode.get() == 'Trigger Mode': 
            if channel_save[6] != 2:
                channel_save[6] = 2 #Mode (Constant = 0, Strobe = 1, Trigger = 2)
                self.STOP_SQ_strobe_frame_thread()
        try:
            self.sq_trigger_btn = self.SQ_trigger_condition(self.sq_trigger_btn, channel_save)
        except (AttributeError, tk.TclError):
            pass


    def mode_select_group_A(self,event=None): #group A (channel 1, 5, 9, 13)
        self.machine_param_type = 'mode'

        if self.ch_sel_str== '1 - 4':
            self.mode_function(self.ch_1_mode, self.channel_1_save)

            self.SQ_mode_select_sync(self.channel_1_save, self.channel_2_save, self.ch_2_mode)
            self.SQ_mode_select_sync(self.channel_1_save, self.channel_3_save, self.ch_3_mode)
            self.SQ_mode_select_sync(self.channel_1_save, self.channel_4_save, self.ch_4_mode)

            self.param_to_machine(None, self.channel_1_save)

            # self.param_to_machine(1, self.channel_1_save)
            # self.param_to_machine(2, self.channel_2_save)
            # self.param_to_machine(3, self.channel_3_save)
            # self.param_to_machine(4, self.channel_4_save)

        # interval_spinbox_function()

    def mode_select_group_B(self,event=None): #group B (channel 2, 6, 10, 14)
        self.machine_param_type = 'mode'

        if self.ch_sel_str== '1 - 4':
            self.mode_function(self.ch_2_mode, self.channel_2_save)

            self.SQ_mode_select_sync(self.channel_2_save, self.channel_1_save, self.ch_1_mode)
            self.SQ_mode_select_sync(self.channel_2_save, self.channel_3_save, self.ch_3_mode)
            self.SQ_mode_select_sync(self.channel_2_save, self.channel_4_save, self.ch_4_mode)

            self.param_to_machine(None, self.channel_2_save)

            # self.param_to_machine(1, self.channel_1_save)
            # self.param_to_machine(2, self.channel_2_save)
            # self.param_to_machine(3, self.channel_3_save)
            # self.param_to_machine(4, self.channel_4_save)

        # interval_spinbox_function()

    def mode_select_group_C(self,event=None): #group C (channel 3, 7, 11, 15)
        self.machine_param_type = 'mode'

        if self.ch_sel_str== '1 - 4':
            self.mode_function(self.ch_3_mode, self.channel_3_save)

            self.SQ_mode_select_sync(self.channel_3_save, self.channel_2_save, self.ch_2_mode)
            self.SQ_mode_select_sync(self.channel_3_save, self.channel_1_save, self.ch_1_mode)
            self.SQ_mode_select_sync(self.channel_3_save, self.channel_4_save, self.ch_4_mode)

            self.param_to_machine(None, self.channel_3_save)

            # self.param_to_machine(1, self.channel_1_save)
            # self.param_to_machine(2, self.channel_2_save)
            # self.param_to_machine(3, self.channel_3_save)
            # self.param_to_machine(4, self.channel_4_save)

        # interval_spinbox_function()

    def mode_select_group_D(self,event=None): #group D (channel 4, 8, 12, 16)
        self.machine_param_type = 'mode'

        if self.ch_sel_str== '1 - 4':
            self.mode_function(self.ch_4_mode, self.channel_4_save)

            self.SQ_mode_select_sync(self.channel_4_save, self.channel_1_save, self.ch_1_mode)
            self.SQ_mode_select_sync(self.channel_4_save, self.channel_2_save, self.ch_2_mode)
            self.SQ_mode_select_sync(self.channel_4_save, self.channel_3_save, self.ch_3_mode)

            self.param_to_machine(None, self.channel_4_save)

            # self.param_to_machine(1, self.channel_1_save)
            # self.param_to_machine(2, self.channel_2_save)
            # self.param_to_machine(3, self.channel_3_save)
            # self.param_to_machine(4, self.channel_4_save)

    def SQ_strobe_frame(self):
        if self.sq_strobe_btn_click == False:
            self.sq_strobe_btn_click = True

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
        
        self.ctrl.select_address(self.addr_index_a)

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
            self.dll_LC18.Strobe()
            #print(self.sq_frame_delay_event)
            while not self.sq_frame_delay_event.isSet():
                # print('Strobe Internal Trigger', len(self.sq_frame_img_list))
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

                    if 3 < len(self.sq_frame_img_list) < 10:
                        self.sq_frame_delay_event.wait(self.sq_trigger_delay - (t2-t1) - self.delay_step)#0.05)
                    else:
                        self.sq_frame_delay_event.wait(self.sq_trigger_delay - (t2-t1))

            if len(self.sq_frame_img_list) == self.sq_fr_arr[0]:
                self.Internal_SQ_Fr_Disp()

            try:
                _cam_class.btn_save_sq['state'] = 'normal'
            except AttributeError:
                pass
            try:
                _cam_class.checkbtn_trigger_src['state'] = 'normal'
            except AttributeError:
                pass

        else:
            self.dll_LC18.Strobe()

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

    def strobe_channel_repeat(self):
        self.ctrl.select_address(self.addr_index_a)
        self.dll_LC18.Strobe()

    def SQ_internal_strobe_bool(self):
        from main_GUI import main_GUI
        cam_active_str = main_GUI.class_cam_conn.active_gui_str
        _cam_class = main_GUI.class_cam_conn.active_gui

        strobe_mode_bool = False
        if (self.channel_1_save[6] == 1 and self.channel_2_save[6] == 1 
            and self.channel_3_save[6] == 1 and self.channel_4_save[6] == 1):
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

    def repeat_start_stop(self, event = None):
        if (self.repeat_status == True):
            self.interval_spinbox_function()
            self.thread_event_repeat.clear()
            self.repeat_handle = threading.Thread(target= self.repeat_func, args = (self.thread_event_repeat,))
            self.repeat_handle.start()

            widget_disable(self.infinity_radio_btn, self.finite_radio_btn, self.interval_entry)

            if self.repeat_mode_str == 'finite':
                widget_disable(self.repeat_number_spinbox)

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

            widget_enable(self.infinity_radio_btn, self.finite_radio_btn, self.interval_entry)

            if self.repeat_mode_str == 'finite':
                widget_enable(self.repeat_number_spinbox)

            try:
                widget_enable(self.sq_strobe_btn)
            except (AttributeError, tk.TclError):
                pass
            #print(self.repeat_handle)

    ###############################################################################################
    #7. RESET LIGHT PARAMETERS
    def SQ_reset_function(self, ch_arr, ch_index, fr_arr, fr_int_arr):
        for i in range(0, 4): #This resets up to board address no.3 and all channels (with various configurations)
            self.ctrl.select_address(i)
            self.ctrl.set_multiplier(ch_index, ch_arr[0])
            self.ctrl.set_const_intensity(ch_index, int(ch_arr[1]))
            self.ctrl.set_strobe_width(ch_index, ch_arr[3])
            self.ctrl.set_output_delay(ch_index, ch_arr[4])
            self.ctrl.set_output_width(ch_index, ch_arr[5])
            self.ctrl.set_mode(ch_index, ch_arr[6])

            self.ctrl.SQ_SetNoOfFrame(fr_arr[0])
            self.ctrl.SQ_SetFrameWidth(fr_arr[1])

            self.ctrl.SQ_SetFrame(0, fr_int_arr[0])
            self.ctrl.SQ_SetFrame(1, fr_int_arr[1])
            self.ctrl.SQ_SetFrame(2, fr_int_arr[2])
            self.ctrl.SQ_SetFrame(3, fr_int_arr[3])
            self.ctrl.SQ_SetFrame(4, fr_int_arr[4])

            self.ctrl.SQ_SetFrame(5, fr_int_arr[5])
            self.ctrl.SQ_SetFrame(6, fr_int_arr[6])
            self.ctrl.SQ_SetFrame(7, fr_int_arr[7])
            self.ctrl.SQ_SetFrame(8, fr_int_arr[8])
            self.ctrl.SQ_SetFrame(9, fr_int_arr[9])

    def reset_save_arr(self, ch_arr): #reset values Version 2 of save array for a Channel to default values
        ch_arr[0]=1
        ch_arr[1]=0
        ch_arr[2]=0
        ch_arr[3]=100
        ch_arr[4]=0
        ch_arr[5]=100
        ch_arr[6]=0

    def SQ_reset_frame_arr(self, fr_arr, fr_int_arr):
        fr_arr[0] = 1
        fr_arr[1] = 0
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
    

    def reset_all(self): #reset everything
        self.thread_reset_event.clear()

        self.reset_save_arr(self.channel_1_save)
        self.reset_save_arr(self.channel_2_save)
        self.reset_save_arr(self.channel_3_save)
        self.reset_save_arr(self.channel_4_save)

        self.SQ_reset_frame_arr(self.sq_fr_arr, self.sq_fr_int_arr)

        #self.channel_on_select()
        try:
            if self.light_conn_status == True:
                self.SQ_reset_function(self.channel_1_save, 1, self.sq_fr_arr, self.sq_fr_int_arr)
                self.SQ_reset_function(self.channel_2_save, 2, self.sq_fr_arr, self.sq_fr_int_arr)
                self.SQ_reset_function(self.channel_3_save, 3, self.sq_fr_arr, self.sq_fr_int_arr)
                self.SQ_reset_function(self.channel_4_save, 4, self.sq_fr_arr, self.sq_fr_int_arr)
                self.sq_trigger_btn = self.SQ_trigger_condition(self.sq_trigger_btn, self.channel_1_save)
        except:
            pass
        self.thread_reset_event.set()

    ###############################################################################################
    #8. LOAD LIGHT PARAMETERS
    def load_parameter(self, event=None):
        self.thread_refresh_event.clear()

        self.addr_index_a = binary_to_dec_v2(self.addr_a[0], self.addr_a[1], self.addr_a[2], self.addr_a[3], reverse_str = True)

        try:
            #board_address()
            self.ctrl.select_address(self.addr_index_a)

            self.ctrl.SQ_read_function(self.channel_1_save, 1)
            self.ctrl.SQ_read_function(self.channel_2_save, 2)
            self.ctrl.SQ_read_function(self.channel_3_save, 3)
            self.ctrl.SQ_read_function(self.channel_4_save, 4)

            self.ctrl.SQ_read_frame_function(self.sq_fr_arr, self.sq_fr_int_arr)
            self.sq_trigger_btn = self.SQ_trigger_condition(self.sq_trigger_btn, self.channel_1_save)
        except:
            #This Exception Handling is used to Break the Thread and the GUI update loop!
            pass
        #self.LC18_interface()
        self.thread_refresh_event.set()
    ###############################################################################################
    #9. STOP ALL THREADS
    def Stop_Threads(self):
        self.thread_event_repeat.set()
        try:
            Stop_thread(self.repeat_handle)
            print('Repeat Handle Thread Stopped')
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