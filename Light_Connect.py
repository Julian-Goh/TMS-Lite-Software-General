import tkinter as tk
from tkinter import ttk

import serial.tools.list_ports    

import numpy as np

import threading

# from LC18_GUI import LC18_GUI
from Tk_MsgBox.custom_warning_msgbox import Warning_Msgbox

from LC18_GUI_Lib.LC18_SQ import LC18_SQ_GUI
from LC18_GUI_Lib.LC18_16CH import LC18_16CH_GUI
from LC18_GUI_Lib.LC18_OD import LC18_OD_GUI
from LC18_GUI_Lib.LC18_KP import LC18_KP_GUI
from LC18_GUI_Lib.LC18_RGBW import LC18_RGBW_GUI
from LC18_GUI_Lib.LC18_1CH import LC18_1CH_GUI
from LC18_GUI_Lib.LC18_2CH import LC18_2CH_GUI

from LC20_GUI import LC20_GUI

def ctrl_model_type(sel_model, _type):
    # 'LC-18-4CH-KP1'
    # 'LC-18-16CH'
    # 'LC-18-4CH-A1'
    # 'LC-18-1CH'
    # 'LC-18-2CH'
    # 'LC-18-OD'
    # 'LC-18-SQ'
    # 'LC-18-4CH-A1-RGBW'
    if sel_model == 'KP':
        _type = 'LC-18-4CH-KP1'

    elif sel_model == '4CH/16CH':
        _type = 'LC-18-4CH / LC-18-16CH'

    elif sel_model == 'X10':
        _type = 'LC-18-1CH'

    elif sel_model == 'X5':
        _type = 'LC-18-2CH'

    elif sel_model == 'OD':
        _type = 'LC-18-OD'

    elif sel_model == 'SQ':
        _type = 'LC-18-SQ'

    elif sel_model == 'RGBW':
        #print('here')
        _type = 'LC-18-4CH-A1-RGBW'

    elif sel_model == 'LC20':
        _type = 'LC-20-16CH-A1'

    return _type

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
    def __init__(self, master, top_frame, scrolled_canvas, scrolled_canvas_W, scrolled_canvas_H, LC18_lib, LC18KP_lib, LC18SQ_lib, tms_logo_2, infinity_icon,
        img_KP, img_4CH, img_16CH, img_RGBW, img_X10, img_X5, img_OD, img_SQ, img_LC20_16CH = None, LC20_lib = None, window_icon = None):

        self.master = master
        self.top_frame = top_frame
        self.scrolled_canvas = scrolled_canvas
        self.scrolled_canvas_W = scrolled_canvas_W #Width of window_fr in scrolled_canvas class
        self.scrolled_canvas_H = scrolled_canvas_H #Height of window_fr in scrolled_canvas class

        self.LC18_lib = LC18_lib
        self.LC18KP_lib = LC18KP_lib
        self.LC18SQ_lib = LC18SQ_lib
        self.LC20_lib = LC20_lib
        #print(self.LC20_lib)

        self.main_lib = None

        self.thread_event_repeat = threading.Event()
        self.thread_event_repeat_ALL = threading.Event()

        self.master_firmware_version_str = None
        self.firmware_version_str = None #firmware_version_str is in strings type. We initialize them to string None
        self.firmware_model = None
        self.firmware_model_sel = None
        self.light_ctrl_type = None

        self.COM = self.TCPIP = self.USB = False

        self.TCPIP_str_arr = np.array(['192', '168', '0', '100'])

        self.light_conn_status = False

        self.tms_logo_2 = tms_logo_2
        self.infinity_icon = infinity_icon
        self.window_icon = window_icon

        self.img_KP = img_KP
        self.img_4CH = img_4CH
        self.img_16CH = img_16CH
        self.img_RGBW = img_RGBW
        self.img_X10 = img_X10
        self.img_X5 = img_X5
        self.img_OD = img_OD
        self.img_SQ = img_SQ

        self.img_LC20_16CH = img_LC20_16CH
        self.light_select_popout_MODE = 'LC18' #'LC18' & 'LC20'

    def top_frame_light_info(self):
        if self.light_conn_status == True:
            self.forget_light_info()
            if self.firmware_model_sel == 'LC20':
                self.light_ctrl_type_label = tk.Label(self.top_frame, font='Helvetica 12 bold', fg = 'white', bg = 'midnight blue', justify= tk.LEFT)
                self.light_ctrl_type = ctrl_model_type(self.firmware_model_sel, self.light_ctrl_type)
                self.light_ctrl_type_label['text'] = 'Controller Type: ' + self.light_ctrl_type
                self.light_ctrl_type_label.place(x=150, y=10)

            elif self.firmware_model_sel != 'LC20' and self.firmware_model_sel != None:

                self.master_firmware_version = tk.StringVar()
                self.board_master_firmware = tk.Label(self.top_frame, textvariable = self.master_firmware_version, font='Helvetica 12 bold', fg = 'white', bg = 'midnight blue', justify= tk.LEFT)
                self.master_firmware_version.set('Master FW Version: ' + str(self.master_firmware_version_str))
                self.board_master_firmware.place(x=150, y=40)

                self.light_ctrl_type_label = tk.Label(self.top_frame, font='Helvetica 12 bold', fg = 'white', bg = 'midnight blue', justify= tk.LEFT)
                self.light_ctrl_type = ctrl_model_type(self.firmware_model_sel, self.light_ctrl_type)
                self.light_ctrl_type_label['text'] = 'Controller Type: ' + self.light_ctrl_type
                self.light_ctrl_type_label.place(x=150, y=10)

        elif self.light_conn_status == False:
            self.forget_light_info()
            pass

    def forget_light_info(self):
        try:
            if self.board_master_firmware.winfo_exists() == 1:
                self.board_master_firmware.place_forget()
        except AttributeError:
            pass

        try:
            if self.light_ctrl_type_label.winfo_exists() == 1:
                self.light_ctrl_type_label.place_forget()
        except AttributeError:
            pass

    def light_connect_btn_state(self):
        self.forget_light_connect_btn()
        
        if self.light_conn_status == False:
            self.light_conn_btn_1 = tk.Button(self.top_frame, relief = tk.GROOVE, activebackground = 'forest green', bg = 'green3', activeforeground = 'white', fg = 'white'
                , text='CONNECT', width = 10, height = 1, font='Helvetica 14 bold')
            if self.light_select_popout_MODE == 'LC18':
                self.light_conn_btn_1['command'] = self.light_select_popout #self.LC20_select_popout #self.light_select_popout
            elif self.light_select_popout_MODE == 'LC20':
                self.light_conn_btn_1['command'] = self.LC20_select_popout #self.light_select_popout
            #self.light_conn_btn_1.place(x=550 + 200, y = 20)
            self.light_conn_btn_1.place(relx = 0.75 , y = 20)


        elif self.light_conn_status == True:
            self.light_disconn_btn = tk.Button(self.top_frame, relief = tk.GROOVE, activebackground = 'red3', bg = 'red', activeforeground = 'white', fg = 'white'
                , text='DISCONNECT', width = 10, height = 1, font='Helvetica 14 bold')
            self.light_disconn_btn['command'] = self.light_disconnect
            #self.light_disconn_btn.place(x=550 + 200, y = 20)
            self.light_disconn_btn.place(relx = 0.75 , y = 20)

    def forget_light_connect_btn(self):
        try:
            if self.light_conn_btn_1.winfo_exists() == 1:
                self.light_conn_btn_1.place_forget()
        except AttributeError:
            pass

        try:
            if self.light_disconn_btn.winfo_exists() == 1:
                self.light_disconn_btn.place_forget()
        except AttributeError:
            pass

    def LC20_select_popout(self):
        toplvl_W = 500
        toplvl_H = 360
        self.light_select_popout_MODE = 'LC20'
        self.light_conn_btn_1['command'] = self.LC20_select_popout
        try:
            self.light_connection_toplvl.destroy()
        except AttributeError:
            pass
        try:
            self.light_sel_toplvl.destroy()
        except AttributeError:
            pass

        try:
            #print('try')
            check_bool = tk.Toplevel.winfo_exists(self.LC20_sel_toplvl)
            if check_bool == 0:
                #print('not exist')
                self.LC20_sel_toplvl = tk.Toplevel(master= self.master, width = toplvl_W, height = toplvl_H)
                self.LC20_sel_toplvl.resizable(False, False)
                self.LC20_sel_toplvl['bg'] = 'white'
                self.LC20_sel_toplvl.title('LC20 Models')
                screen_width = self.LC20_sel_toplvl.winfo_screenwidth()
                screen_height = self.LC20_sel_toplvl.winfo_screenheight()
                x_coordinate = int((screen_width/2) - (toplvl_W/2))
                y_coordinate = int((screen_height/2) - (toplvl_H/2))
                self.LC20_sel_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))

                try:
                    self.LC20_sel_toplvl.iconphoto(False, self.window_icon)
                except Exception:
                    pass

            else:
                #print('exist')
                self.LC20_sel_toplvl.lift()
                pass
        except AttributeError:
            #print('except')
            self.LC20_sel_toplvl = tk.Toplevel(master= self.master, width = toplvl_W, height = toplvl_H) #TKINTER GENERATION CANNOT WORK WITH THREAD
            self.LC20_sel_toplvl.resizable(False, False)
            self.LC20_sel_toplvl['bg'] = 'white'
            self.LC20_sel_toplvl.title('LC20 Models')
            screen_width = self.LC20_sel_toplvl.winfo_screenwidth()
            screen_height = self.LC20_sel_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (toplvl_W/2))
            y_coordinate = int((screen_height/2) - (toplvl_H/2))
            self.LC20_sel_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))

            try:
                self.LC20_sel_toplvl.iconphoto(False, self.window_icon)
            except Exception:
                pass
        
        tk.Label(self.LC20_sel_toplvl, image = self.tms_logo_2, bg ='white').place(relx= 0.5, y = 0 + 50, anchor = tk.CENTER)


        self.LC20_sel_frame = tk.Frame(self.LC20_sel_toplvl, width = toplvl_W, height = toplvl_H -120, bg = 'midnight blue', highlightbackground="midnight blue", highlightthickness=1)
        self.LC20_sel_frame.place(x = 0 , y =120)

        button_place_y = 50

        tk.Label(self.LC20_sel_frame, bg = 'midnight blue', fg = 'white', width = 12, justify = 'center',
            text='LC-20-16CH-A1', font='Helvetica 13 bold').place(relx = 0.5, y = button_place_y-30, anchor = tk.CENTER)

        other_model_btn = tk.Button(self.LC20_sel_frame, text = 'Other Models', bg = 'white', 
            fg = 'black', activeforeground = 'black', relief = tk.GROOVE, font = 'Helvetica 12', bd = 0)
        other_model_btn.place(relx = 0.5, y = 205, anchor = tk.CENTER)
        other_model_btn['command'] = self.light_select_popout

        button_1 = tk.Button(self.LC20_sel_frame, width = 120, height = 120, bg = 'white', 
            fg = 'white', activebackground ='white', activeforeground = 'white', relief = tk.GROOVE, image = self.img_LC20_16CH)
            
        button_1.place(relx = 0.5, y = button_place_y + 60, anchor = tk.CENTER)
        button_1['command']=self.select_LC20_16CH


    def light_select_popout(self):
        toplvl_W = 700
        toplvl_H = 550
        self.light_select_popout_MODE = 'LC18'
        self.light_conn_btn_1['command'] = self.light_select_popout
        try:
            self.light_connection_toplvl.destroy()
        except AttributeError:
            pass

        try:
            self.LC20_sel_toplvl.destroy()
        except AttributeError:
            pass

        try:
            #print('try')
            check_bool = tk.Toplevel.winfo_exists(self.light_sel_toplvl)
            if check_bool == 0:
                #print('not exist')
                self.light_sel_toplvl = tk.Toplevel(master= self.master, width = toplvl_W, height = toplvl_H)
                self.light_sel_toplvl.resizable(False, False)
                self.light_sel_toplvl['bg'] = 'white'
                self.light_sel_toplvl.title('LC18 Models')
                screen_width = self.light_sel_toplvl.winfo_screenwidth()
                screen_height = self.light_sel_toplvl.winfo_screenheight()
                x_coordinate = int((screen_width/2) - (toplvl_W/2))
                y_coordinate = int((screen_height/2) - (toplvl_H/2))
                self.light_sel_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))

                try:
                    self.light_sel_toplvl.iconphoto(False, self.window_icon)
                except Exception:
                    pass

            else:
                #print('exist')
                self.light_sel_toplvl.lift()
                pass
        except AttributeError:
            #print('except')
            self.light_sel_toplvl = tk.Toplevel(master= self.master, width = toplvl_W, height = toplvl_H) #TKINTER GENERATION CANNOT WORK WITH THREAD
            self.light_sel_toplvl.resizable(False, False)
            self.light_sel_toplvl['bg'] = 'white'
            self.light_sel_toplvl.title('LC18 Models')
            screen_width = self.light_sel_toplvl.winfo_screenwidth()
            screen_height = self.light_sel_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (toplvl_W/2))
            y_coordinate = int((screen_height/2) - (toplvl_H/2))
            self.light_sel_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))

            try:
                self.light_sel_toplvl.iconphoto(False, self.window_icon)
            except Exception:
                pass
        
        tk.Label(self.light_sel_toplvl, image = self.tms_logo_2, bg ='white').place(x= 270, y = 0)


        self.light_sel_frame = tk.Frame(self.light_sel_toplvl, width = 700, height = 380 + 50, bg = 'midnight blue', highlightbackground="midnight blue", highlightthickness=1)
        self.light_sel_frame.place(x = 0 , y =120)

        other_model_btn = tk.Button(self.light_sel_frame, text = 'Other Models', bg = 'white', 
            fg = 'black', activeforeground = 'black', relief = tk.GROOVE, font = 'Helvetica 12', bd = 0)
        other_model_btn.place(relx = 0.5, y = 395, anchor = tk.CENTER)
        other_model_btn['command'] = self.LC20_select_popout

        button_place_x = 58
        button_place_y = 50
        x_spacing = 150
        y_spacing = 185

        tk.Label(self.light_sel_frame, bg = 'midnight blue', fg = 'white', width = 12, justify = 'center',
            text='LC-18-4CH-KP1', font='Helvetica 13 bold').place(x= button_place_x, y = button_place_y-30)
        tk.Label(self.light_sel_frame, bg = 'midnight blue', fg = 'white', width =12, justify = 'center',
            text='LC-18-16CH', font='Helvetica 13 bold').place(x= button_place_x + x_spacing, y = button_place_y-30)
        tk.Label(self.light_sel_frame, bg = 'midnight blue', fg = 'white', width =12, justify = 'center',
            text='LC-18-4CH-A1', font='Helvetica 13 bold').place(x= button_place_x + x_spacing*2, y = button_place_y-30)
        tk.Label(self.light_sel_frame, bg = 'midnight blue', fg = 'white', width =12, justify = 'center',
            text='LC-18-1CH', font='Helvetica 13 bold').place(x= button_place_x + x_spacing*3, y = button_place_y-30)
        tk.Label(self.light_sel_frame, bg = 'midnight blue', fg = 'white', width =12, justify = 'center',
            text='LC-18-2CH', font='Helvetica 13 bold').place(x= button_place_x, y = button_place_y + y_spacing-30)
        tk.Label(self.light_sel_frame, bg = 'midnight blue', fg = 'white', width =12, justify = 'center',
            text='LC-18-OD', font='Helvetica 13 bold').place(x= button_place_x + x_spacing, y = button_place_y + y_spacing-30)
        tk.Label(self.light_sel_frame, bg = 'midnight blue', fg = 'white', width =12, justify = 'center',
            text='LC-18-SQ', font='Helvetica 13 bold').place(x= button_place_x + x_spacing*2, y = button_place_y + y_spacing-30)
        tk.Label(self.light_sel_frame, bg = 'midnight blue', fg = 'white', width =17, justify = 'center',
            text='LC-18-4CH-A1-RGBW', font='Helvetica 13 bold').place(x= button_place_x + x_spacing*3, y = button_place_y + y_spacing-30)


        button_1 = tk.Button(self.light_sel_frame, width = 120, height = 120, bg = 'white', 
            fg = 'white', activebackground ='white', activeforeground = 'white', relief = tk.GROOVE, image = self.img_KP)
        button_2 = tk.Button(self.light_sel_frame, width = 120, height = 120, bg = 'white', 
            fg = 'white', activebackground ='white', activeforeground = 'white', relief = tk.GROOVE, image = self.img_16CH)
        button_3 = tk.Button(self.light_sel_frame, width = 120, height = 120, bg = 'white', 
            fg = 'white', activebackground ='white', activeforeground = 'white', relief = tk.GROOVE, image = self.img_4CH)
        button_4 = tk.Button(self.light_sel_frame, width = 120, height = 120, bg = 'white', 
            fg = 'white', activebackground ='white', activeforeground = 'white', relief = tk.GROOVE, image = self.img_X10)
        button_5 = tk.Button(self.light_sel_frame, width = 120, height = 120, bg = 'white', 
            fg = 'white', activebackground ='white', activeforeground = 'white', relief = tk.GROOVE, image = self.img_X5)
        button_6 = tk.Button(self.light_sel_frame, width = 120, height = 120, bg = 'white', 
            fg = 'white', activebackground ='white', activeforeground = 'white', relief = tk.GROOVE, image = self.img_OD)
        button_7 = tk.Button(self.light_sel_frame, width = 120, height = 120, bg = 'white', 
            fg = 'white', activebackground ='white', activeforeground = 'white', relief = tk.GROOVE, image = self.img_SQ)
        button_8 = tk.Button(self.light_sel_frame, width = 120, height = 120, bg = 'white', 
            fg = 'white', activebackground ='white', activeforeground = 'white', relief = tk.GROOVE, image = self.img_RGBW)
               
        
        button_1.place(x= button_place_x, y = button_place_y)
        button_2.place(x= button_place_x + x_spacing, y = button_place_y)
        button_3.place(x= button_place_x + x_spacing*2, y = button_place_y)
        button_4.place(x= button_place_x + x_spacing*3, y = button_place_y)
        button_5.place(x= button_place_x , y = button_place_y + y_spacing)
        button_6.place(x= button_place_x + x_spacing, y = button_place_y + y_spacing)
        button_7.place(x= button_place_x + x_spacing*2, y = button_place_y + y_spacing)
        button_8.place(x= button_place_x + x_spacing*3, y = button_place_y + y_spacing)

        button_1['command']=self.select_LC18_KP
        button_2['command']=self.select_LC18
        button_3['command']=self.select_LC18
        button_4['command']=self.select_LC18_X10
        button_5['command']=self.select_LC18_X5
        button_6['command']=self.select_LC18_OD
        button_7['command']=self.select_LC18_SQ
        button_8['command']=self.select_LC18_RGBW

    def select_LC18(self):
        self.firmware_model_sel='4CH/16CH'
        self.main_lib = self.LC18_lib
        self.light_connection_popout()
        #print(firmware_model_sel)

    def select_LC18_RGBW(self):
        self.firmware_model_sel='RGBW'
        self.main_lib = self.LC18_lib
        self.light_connection_popout()
        #print(firmware_model_sel)

    def select_LC18_OD(self):
        self.firmware_model_sel='OD'
        self.main_lib = self.LC18_lib
        self.light_connection_popout()
        #print(firmware_model_sel)

    def select_LC18_X5(self):
        self.firmware_model_sel='X5'
        self.main_lib = self.LC18_lib
        self.light_connection_popout()
        #print(firmware_model_sel)

    def select_LC18_X10(self):
        self.firmware_model_sel='X10'
        self.main_lib = self.LC18_lib
        self.light_connection_popout()
        #print(firmware_model_sel)

    def select_LC18_KP(self):
        self.firmware_model_sel='KP'
        self.main_lib = self.LC18KP_lib
        self.light_connection_popout()
        #print(firmware_model_sel)

    def select_LC18_SQ(self):
        self.firmware_model_sel='SQ'
        self.main_lib = self.LC18SQ_lib
        self.light_connection_popout()
        #print(firmware_model_sel)

    def select_LC20_16CH(self):
        self.firmware_model_sel='LC20'
        self.main_lib = self.LC20_lib
        self.light_connection_popout()

    def comport_combobox_on_select(self,event=None):
        self.comport_text = str(self.comport_list.get())

    def widget_highlight_focus(self,widget):
        widget.selection_range(0, tk.END)

    def validate_TCPIP_entry_1(self,d, P, S):# i = index, S = insert character, d = action, P = entry value
        if d == '1':
            try:
                int(P)
                if int(P) >= 0 and S != '-':
                    if len(P) == 3 and d != 0:
                        self.TCPIP_entry_1.tk_focusNext().focus()
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

    def validate_TCPIP_entry_2(self,d, P, S):# i = index, S = insert character, d = action, P = entry value
        if d == '1':
            try:
                int(P)
                if int(P) >= 0 and S != '-':
                    if len(P) == 3 and d != 0:
                        self.TCPIP_entry_2.tk_focusNext().focus()
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

    def validate_TCPIP_entry_3(self, d, P, S):# i = index, S = insert character, d = action, P = entry value
        if d == '1':
            try:
                int(P)
                if int(P) >= 0 and S != '-':
                    if len(P) == 3 and d != 0:
                        self.TCPIP_entry_3.tk_focusNext().focus()
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

    def validate_TCPIP_entry_4(self,d, P, S):# i = index, S = insert character, d = action, P = entry value
        if d == '1':
            try:
                int(P)
                if int(P) >= 0 and S != '-':
                    if len(P) == 3 and d != 0:
                        #TCPIP_entry_4.tk_focusNext().focus()
                        self.TCPIP_reset_button.tk_focusNext().focus()
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

    def TCPIP_entry_func(self, event=None):
        if self.TCPIP_var_1.get() == '':
            self.TCPIP_var_1.set(self.TCPIP_str_arr[0])

        if self.TCPIP_var_2.get() == '':
            self.TCPIP_var_2.set(self.TCPIP_str_arr[1])

        if self.TCPIP_var_3.get() == '':
            self.TCPIP_var_3.set(self.TCPIP_str_arr[2])

        if self.TCPIP_var_4.get() == '':
            self.TCPIP_var_4.set(self.TCPIP_str_arr[3])

        else:
            self.TCPIP_str_arr[0] = self.TCPIP_var_1.get()
            self.TCPIP_str_arr[1] = self.TCPIP_var_2.get()
            self.TCPIP_str_arr[2] = self.TCPIP_var_3.get()
            self.TCPIP_str_arr[3] = self.TCPIP_var_4.get()

    def TCPIP_reset(self,event=None):
        self.TCPIP_str_arr[0] = '192'
        self.TCPIP_str_arr[1] = '168'
        self.TCPIP_str_arr[2] = '0'
        self.TCPIP_str_arr[3] = '100'

        self.TCPIP_var_1.set(self.TCPIP_str_arr[0])
        self.TCPIP_var_2.set(self.TCPIP_str_arr[1])
        self.TCPIP_var_3.set(self.TCPIP_str_arr[2])
        self.TCPIP_var_4.set(self.TCPIP_str_arr[3])

    def light_connection_type(self):
        if self.connect_type.get() == 'comport':
            try:
                if self.TCPIP_entry_frame.winfo_exists() == 1:
                    self.TCPIP_entry_frame.place_forget()
            except AttributeError:
                pass
            try:
                if self.comport_list_frame.winfo_exists() == 1:
                    self.comport_list_frame.place_forget()
            except AttributeError:
                pass
            self.comport_list_frame = tk.Frame(self.light_connection_frame, width = 330, height = 45)
            self.comport_list_frame['bg'] = 'white'
            self.comport_list_frame.place(x = 150, y = 55)
            #print(self.comport_list_frame)

            self.comport_list_label = tk.Label(self.comport_list_frame, text = 'Choose & Select COM Ports:' , font = 'Helvetica 10')
            self.comport_list_label['bg'] = 'white'
            self.comport_list_label.place(x= 0, y = 0)
            self.comport_list_frame.option_add('*TCombobox*Listbox.font', ('Helvetica', '10'))

            self.comport_list = ttk.Combobox(self.comport_list_frame, values=serial.tools.list_ports.comports() ,width=42, state='readonly', font = 'Helvetica 10')
            self.comport_list.place(x=0, y= 20)
            self.comport_list.bind('<<ComboboxSelected>>', self.comport_combobox_on_select)

            self.comport_index_list = []

            for comport_index, p in enumerate (serial.tools.list_ports.comports()):
                if 'USB' and 'Serial' in p.description:
                    self.comport_index_list.append((comport_index, p))

            if len(self.comport_index_list) != 0:
                self.comport_list.current(self.comport_index_list[0][0])
                self.comport_text = str(self.comport_index_list[0][1])
            elif len(self.comport_index_list) == 0:
                self.comport_text = "Default COMPort not found"

            print('comport')
            if self.firmware_model_sel == 'LC20':
                self.light_conn_btn_2['command'] = self.LC20_comport_connect
            else:           
                self.light_conn_btn_2['command'] = self.comport_connect

        elif self.connect_type.get() == 'TCPIP':      
            try:
                if self.TCPIP_entry_frame.winfo_exists() == 1:
                    self.TCPIP_entry_frame.place_forget()
            except AttributeError:
                pass
            try:
                if self.comport_list_frame.winfo_exists() == 1:
                    self.comport_list_frame.place_forget()
            except AttributeError:
                pass
            self.TCPIP_entry_frame = tk.Frame(self.light_connection_frame, width = 330, height = 45)
            self.TCPIP_entry_frame['bg'] = 'white'
            self.TCPIP_entry_frame.place(x = 150, y = 110)

            self.TCPIP_var_1 = tk.StringVar()
            self.TCPIP_var_2 = tk.StringVar()
            self.TCPIP_var_3 = tk.StringVar()
            self.TCPIP_var_4 = tk.StringVar()

            dot_1 = tk.Label(self.TCPIP_entry_frame, text= '.', font = 'Helvetica 12 bold', justify = 'center')
            dot_1['bg'] = 'white'
            dot_1.place(x=40, y =10)
            
            dot_2 = tk.Label(self.TCPIP_entry_frame, text= '.', font = 'Helvetica 12 bold', justify = 'center')
            dot_2['bg'] = 'white'
            dot_2.place(x=95, y =10)

            dot_3 = tk.Label(self.TCPIP_entry_frame, text= '.', font = 'Helvetica 12 bold', justify = 'center')
            dot_3['bg'] = 'white'
            dot_3.place(x=150, y =10)

            self.TCPIP_entry_1 = tk.Entry(self.TCPIP_entry_frame, textvariable = self.TCPIP_var_1, highlightbackground="black", highlightthickness=1, width = 3, font = 'Helvetica 11', justify = 'center')
            self.TCPIP_entry_1.bind('<FocusIn>', lambda event: self.widget_highlight_focus(widget=self.TCPIP_entry_1))
            self.TCPIP_entry_1['validate']='key'
            self.TCPIP_entry_1['vcmd']=(self.TCPIP_entry_1.register(self.validate_TCPIP_entry_1), '%d', '%P', '%S')
            self.TCPIP_entry_1.bind('<FocusOut>', self.TCPIP_entry_func)
            self.TCPIP_var_1.set(self.TCPIP_str_arr[0])
            self.TCPIP_entry_1.place(x = 5, y = 10)

            self.TCPIP_entry_2 = tk.Entry(self.TCPIP_entry_frame, textvariable = self.TCPIP_var_2, highlightbackground="black", highlightthickness=1, width = 3, font = 'Helvetica 11', justify = 'center')
            self.TCPIP_entry_2.bind('<FocusIn>', lambda event: self.widget_highlight_focus(widget=self.TCPIP_entry_2))
            self.TCPIP_entry_2['validate']='key'
            self.TCPIP_entry_2['vcmd']=(self.TCPIP_entry_2.register(self.validate_TCPIP_entry_2), '%d', '%P', '%S')
            self.TCPIP_entry_2.bind('<FocusOut>', self.TCPIP_entry_func)
            self.TCPIP_var_2.set(self.TCPIP_str_arr[1])
            self.TCPIP_entry_2.place(x = 60, y = 10)


            self.TCPIP_entry_3 = tk.Entry(self.TCPIP_entry_frame, textvariable = self.TCPIP_var_3, highlightbackground="black", highlightthickness=1, width = 3, font = 'Helvetica 11', justify = 'center')
            self.TCPIP_entry_3.bind('<FocusIn>', lambda event: self.widget_highlight_focus(widget=self.TCPIP_entry_3))
            self.TCPIP_entry_3['validate']='key'
            self.TCPIP_entry_3['vcmd']=(self.TCPIP_entry_3.register(self.validate_TCPIP_entry_3), '%d', '%P', '%S')
            self.TCPIP_entry_3.bind('<FocusOut>', self.TCPIP_entry_func)
            self.TCPIP_var_3.set(self.TCPIP_str_arr[2])
            self.TCPIP_entry_3.place(x = 115, y = 10)

            self.TCPIP_entry_4 = tk.Entry(self.TCPIP_entry_frame, textvariable = self.TCPIP_var_4, highlightbackground="black", highlightthickness=1, width = 3, font = 'Helvetica 11', justify = 'center')
            self.TCPIP_entry_4.bind('<FocusIn>', lambda event: self.widget_highlight_focus(widget=self.TCPIP_entry_4))
            self.TCPIP_entry_4['validate']='key'
            self.TCPIP_entry_4['vcmd']=(self.TCPIP_entry_4.register(self.validate_TCPIP_entry_4), '%d', '%P', '%S')
            self.TCPIP_entry_4.bind('<FocusOut>', self.TCPIP_entry_func)
            self.TCPIP_var_4.set(self.TCPIP_str_arr[3])
            self.TCPIP_entry_4.place(x = 170, y = 10)

            self.TCPIP_entry_1.focus_set()
            self.TCPIP_entry_1.icursor('end')
            self.TCPIP_entry_2.icursor('end')
            self.TCPIP_entry_3.icursor('end')
            self.TCPIP_entry_4.icursor('end')

            self.TCPIP_reset_button = tk.Button(self.TCPIP_entry_frame, relief = tk.GROOVE, text = 'TCPIP Reset', font = 'Helvetica 11')
            self.TCPIP_reset_button['command'] = self.TCPIP_reset
            self.TCPIP_reset_button.place(x = 230, y = 7)
            print('TCPIP')
            self.light_conn_btn_2['command'] = self.TCPIP_connect

        elif self.connect_type.get() == 'USB':
            try:
                if self.TCPIP_entry_frame.winfo_exists() == 1:
                    self.TCPIP_entry_frame.place_forget()
            except AttributeError:
                pass
            try:
                if self.comport_list_frame.winfo_exists() == 1:
                    self.comport_list_frame.place_forget()
            except AttributeError:
                pass
            self.light_conn_btn_2['command'] = self.USB_connect

            print('USB')
        pass

    def close_light_connection_popout(self):
        if self.light_select_popout_MODE == 'LC18':
            self.light_select_popout()
        elif self.light_select_popout_MODE == 'LC20':
            self.LC20_select_popout()

    def light_connection_popout(self):
        try:
            self.light_sel_toplvl.destroy()
        except:
            pass
        try:
            self.LC20_sel_toplvl.destroy()
        except:
            pass

        #Normally it is better to handle destroy() event. But, since this window will always appear after _ctrl_select_window, I choose to ignore error handling.
        try:
            #print('try')
            # check_bool = tk.Toplevel.winfo_exists(self.light_sel_toplvl)
            check_bool = tk.Toplevel.winfo_exists(self.light_connection_toplvl)
            
            if check_bool == 0:
                #print('not exist')
                self.light_connection_toplvl = tk.Toplevel(master = self.master, width = 700, height = 500)
                self.light_connection_toplvl.resizable(False, False)
                self.light_connection_toplvl['bg'] = 'white'
                self.light_connection_toplvl.title('Connect Settings')
                screen_width = self.light_connection_toplvl.winfo_screenwidth()
                screen_height = self.light_connection_toplvl.winfo_screenheight()
                x_coordinate = int((screen_width/2) - (700/2))
                y_coordinate = int((screen_height/2) - (500/2))
                self.light_connection_toplvl.geometry("{}x{}+{}+{}".format(700, 500, x_coordinate, y_coordinate))
                
                try:
                    self.light_connection_toplvl.iconphoto(False, self.window_icon)
                except Exception:
                    pass

            else:
                #print('exist')
                self.light_connection_toplvl.lift()
                pass
        except AttributeError:
            #print('except')
            self.light_connection_toplvl = tk.Toplevel(master = self.master, width = 700, height = 500) #TKINTER GENERATION CANNOT WORK WITH THREAD
            self.light_connection_toplvl.resizable(False, False)
            self.light_connection_toplvl['bg'] = 'white'
            self.light_connection_toplvl.title('Connect Settings')
            screen_width = self.light_connection_toplvl.winfo_screenwidth()
            screen_height = self.light_connection_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (700/2))
            y_coordinate = int((screen_height/2) - (500/2))
            self.light_connection_toplvl.geometry("{}x{}+{}+{}".format(700, 500, x_coordinate, y_coordinate))
            
            try:
                self.light_connection_toplvl.iconphoto(False, self.window_icon)
            except Exception:
                pass
                
        self.light_connection_toplvl.grab_set()
        tk.Label(self.light_connection_toplvl, text= ('Connect Settings'), font= 'Helvetica 14 bold', bg = 'white').place(x= 270, y = 120)
        tk.Label(self.light_connection_toplvl, image = self.tms_logo_2, bg = 'white').place(x= 270, y = 0)
        copyright_symbol = chr(169)
        copyright_text = ('Copyright ' + copyright_symbol + ' 2004 - 2020 TMS Lite Sdn Bhd.') + '\n All Right Reserved.'
        tk.Label(self.light_connection_toplvl, text= copyright_text, font= 'Helvetica 12', bg = 'white').place(x= 200, y = 450)


        self.connect_type = tk.StringVar(value = 'comport')

        self.light_connection_frame = tk.Frame(self.light_connection_toplvl, width = 500, height = 300 - 30)
        self.light_connection_frame['bg'] = 'white'
        self.light_connection_frame.place(x = 100, y = 110 + 40)

        self.light_conn_btn_2 = tk.Button(self.light_connection_frame, relief = tk.GROOVE, activebackground = 'forest green', bg = 'green3', activeforeground = 'white', fg = 'white'
        , text='CONNECT', width = 10, height = 1, font='Helvetica 14 bold')
        self.light_conn_btn_2.place(x=180, y = 200-20)

        self.light_back_btn = tk.Button(self.light_connection_frame, relief = tk.GROOVE, text='Back to Model', height = 1, font='Helvetica 12')
        # self.light_back_btn['command'] = self.light_select_popout
        self.light_back_btn['command'] = self.close_light_connection_popout

        self.light_back_btn.place(x=188, y = 250-20)

        #print(self.main_lib)

        if str(self.main_lib) == 'LC18Library.LC18':
            comport_radio = tk.Radiobutton(self.light_connection_frame, text = 'Comport', variable = self.connect_type, value = 'comport', font='Helvetica 13')
            comport_radio['bg'] = 'white'
            comport_radio['command'] = self.light_connection_type
            comport_radio.invoke()
            comport_radio.place(x= 50, y=100 - 30)

            TCPIP_radio = tk.Radiobutton(self.light_connection_frame, text = 'TCPIP', variable = self.connect_type, value = 'TCPIP', font='Helvetica 13')
            TCPIP_radio['bg'] = 'white'
            TCPIP_radio['command'] = self.light_connection_type
            TCPIP_radio.place(x= 50, y=150 - 30)

        elif str(self.main_lib) == 'LC18Library.LC18KP':
            comport_radio = tk.Radiobutton(self.light_connection_frame, text = 'Comport', variable = self.connect_type, value = 'comport', font='Helvetica 13')
            comport_radio['bg'] = 'white'
            comport_radio['command'] = self.light_connection_type
            comport_radio.invoke()
            comport_radio.place(x= 50, y=100 - 30)

            TCPIP_radio = tk.Radiobutton(self.light_connection_frame, text = 'TCPIP', variable = self.connect_type, value = 'TCPIP', font='Helvetica 13')
            TCPIP_radio['bg'] = 'white'
            TCPIP_radio['command'] = self.light_connection_type
            TCPIP_radio.place(x= 50, y=150 - 30)

            USB_radio = tk.Radiobutton(self.light_connection_frame, text = 'USB', variable = self.connect_type, value = 'USB', font='Helvetica 13')
            USB_radio['bg'] = 'white'
            USB_radio['command'] = self.light_connection_type
            USB_radio.place(x= 50, y=50 - 30)

        elif str(self.main_lib) == 'LC18Library.LC18SQ':
            comport_radio = tk.Radiobutton(self.light_connection_frame, text = 'Comport', variable = self.connect_type, value = 'comport', font='Helvetica 13')
            comport_radio['bg'] = 'white'
            comport_radio['command'] = self.light_connection_type
            comport_radio.invoke()
            comport_radio.place(x= 50, y=100 - 30)

            TCPIP_radio = tk.Radiobutton(self.light_connection_frame, text = 'TCPIP', variable = self.connect_type, value = 'TCPIP', font='Helvetica 13')
            TCPIP_radio['bg'] = 'white'
            TCPIP_radio['command'] = self.light_connection_type
            TCPIP_radio.place(x= 50, y=150 - 30)

        elif str(self.main_lib) == 'LC20Library.LC20SQ':
            comport_radio = tk.Radiobutton(self.light_connection_frame, text = 'Comport', variable = self.connect_type, value = 'comport', font='Helvetica 13')
            comport_radio['bg'] = 'white'
            comport_radio['command'] = self.light_connection_type
            comport_radio.invoke()
            comport_radio.place(x= 50, y=100 - 30)

        #self.light_connection_toplvl.protocol("WM_DELETE_WINDOW", self.light_select_popout)
        self.light_connection_toplvl.protocol("WM_DELETE_WINDOW", self.close_light_connection_popout)

    def comport_connect(self):
        #self.main_lib = self.LC18SQ_lib
        if self.comport_text == "Default COMPort not found":
            pass
        else:
            com_name = self.comport_text.split(' ')[0]
            com_port_num = com_name.strip('COM')

            status = self.main_lib.ComportConnect(int(com_port_num))
            # print('ComportConnect Status: ', status)
            #status = 0
            if status == 0:
                self.firmware_version_str = self.main_lib.ReadFWVersion()
                try:
                    self.master_firmware_version_str = self.main_lib.ReadMasterFWVersion()
                    if self.master_firmware_version_str == 'ERR':
                        self.master_firmware_version_str = self.main_lib.ReadFWVersion()
                except:
                    self.master_firmware_version_str = self.main_lib.ReadFWVersion() #None

                # print(self.firmware_version_str)
                #self.firmware_version_str = '1.1.0.0'
                firmware_model = firmware_check(self.firmware_version_str)
                # print('firmware_model: ', firmware_model)

                master_firmware_model = firmware_check(self.master_firmware_version_str)
                # print(self.master_firmware_version_str)
                # print('master_firmware_model: ', master_firmware_model)

                if firmware_model is None and master_firmware_model is None:
                    self.firmware_model = None

                elif firmware_model is None and type(master_firmware_model) == str:
                    self.firmware_model = master_firmware_model

                elif type(firmware_model) == str and master_firmware_model is None:
                    self.firmware_model = firmware_model

                elif type(firmware_model) == str and type(master_firmware_model) == str:
                    self.firmware_model = firmware_model
                
                if self.firmware_model == self.firmware_model_sel:
                    print('Connection Success')

                    self.COM = True
                    self.light_conn_status = True
                    self.light_connection_toplvl.destroy()
                    self.scrolled_canvas.rmb_all_func()
                    self.light_connect_btn_state()
                    self.top_frame_light_info()
                    self.light_interface_disp()

                elif self.firmware_model != self.firmware_model_sel:
                    self.COM = False
                    self.light_conn_status = False
                    print('ERROR! FIRMWARE ERROR')

                    Warning_Msgbox(message = 'DETECTED FIRMWARE VERSION: '+ str(self.firmware_version_str) + '\n\n' + 'EXPECTED LC18 MODEL: LC18-' + str(self.firmware_model) + 
                        '\n\nFIRMWARE IS NOT COMPATIBLE.\nPLEASE SELECT THE CORRECT MODEL.', title = 'FIRMWARE ERROR', font = 'Helvetica 10', height = 225
                        , parent = self.light_connection_toplvl, parent_grab_set = True)
                    self.main_lib.ComportDisconnect()

            else: #if status == 1 (ERROR CONNECTION)
                self.COM = False
                self.light_conn_status = False
                print('ERROR! COMPORT CONNECTION FAILED')

                Warning_Msgbox(message = 'POSSIBLE PROBLEMS:\n\n1. LOOSE CONNECTION\n2. INCORRECT COMPORT\n3. CONTROLLER IS SWITCHED OFF'
                    , title = 'CONNECTION ERROR', font = 'Helvetica 10', height = 160
                    , parent = self.light_connection_toplvl, parent_grab_set = True)

                #self.main_lib.ComportDisconnect()


    def LC20_comport_connect(self):
        #self.main_lib = self.LC18SQ_lib
        if self.comport_text == "Default COMPort not found":
            pass
        else:
            com_name = self.comport_text.split(' ')[0]
            com_port_num = com_name.strip('COM')

            status = self.main_lib.ComportConnect(int(com_port_num))
            print('LC20 Comport Connect Status: ', status)
            if status == 0:
                self.firmware_model = 'LC20'
                
                if self.firmware_model == self.firmware_model_sel:
                    print('Connection Success')

                    self.COM = True
                    self.light_conn_status = True
                    self.light_connection_toplvl.destroy()
                    self.scrolled_canvas.rmb_all_func()
                    self.light_connect_btn_state()
                    self.top_frame_light_info()
                    self.light_interface_disp()

            else: #if status == 1 (ERROR CONNECTION)
                self.COM = False
                self.light_conn_status = False
                print('ERROR! COMPORT CONNECTION FAILED')

                Warning_Msgbox(message = 'POSSIBLE PROBLEMS:\n\n1. LOOSE CONNECTION\n2. INCORRECT COMPORT\n3. CONTROLLER IS SWITCHED OFF'
                    , title = 'LC20 CONNECTION ERROR', font = 'Helvetica 10', height = 160
                    , parent = self.light_connection_toplvl, parent_grab_set = True)
                #self.main_lib.ComportDisconnect()

    def TCPIP_connect(self):
        TCPIP_id_number = self.TCPIP_str_arr[0] + '.' + self.TCPIP_str_arr[1] + '.' + self.TCPIP_str_arr[2] + '.' + self.TCPIP_str_arr[3]
        #print(TCPIP_id_number)
        status = self.main_lib.TCPIPConnect(TCPIP_id_number)

        if status == 0:
            self.firmware_version_str = self.main_lib.ReadFWVersion()
            try:
                self.master_firmware_version_str = self.main_lib.ReadMasterFWVersion()
                if self.master_firmware_version_str == 'ERR':
                    self.master_firmware_version_str = self.main_lib.ReadFWVersion()
            except:
                self.master_firmware_version_str = self.main_lib.ReadFWVersion()

            firmware_model = firmware_check(self.firmware_version_str)
            master_firmware_model = firmware_check(self.master_firmware_version_str)

            if firmware_model is None and master_firmware_model is None:
                self.firmware_model = None

            elif firmware_model is None and type(master_firmware_model) == str:
                self.firmware_model = master_firmware_model

            elif type(firmware_model) == str and master_firmware_model is None:
                self.firmware_model = firmware_model

            elif type(firmware_model) == str and type(master_firmware_model) == str:
                self.firmware_model = firmware_model

            #print(firmware_model)
            if self.firmware_model == self.firmware_model_sel:
                print('Connection Success')
                self.TCPIP = True
                self.light_conn_status = True
                self.light_connection_toplvl.destroy()
                
                self.scrolled_canvas.rmb_all_func()

                self.light_connect_btn_state()
                self.top_frame_light_info()
                self.light_interface_disp()
                #lighting_interface_v2()
                #load_button_click()

            elif self.firmware_model != self.firmware_model_sel:
                self.TCPIP = False
                self.light_conn_status = False
                print('ERROR! FIRMWARE ERROR')

                Warning_Msgbox(message = 'DETECTED FIRMWARE VERSION: '+ str(self.firmware_version_str) + '\n\n' + 'EXPECTED LC18 MODEL: LC18-' + str(self.firmware_model) + 
                        '\n\nFIRMWARE IS NOT COMPATIBLE.\nPLEASE SELECT THE CORRECT MODEL.', title = 'FIRMWARE ERROR', font = 'Helvetica 10', height = 225
                        , parent = self.light_connection_toplvl, parent_grab_set = True)
                self.main_lib.TCPIPDisconnect()#Since status is return as 0 in this 'If' statement when we are technically 'connected', We have to disconnect to clear the TCPIP bus.

        else: #if status == 1 (ERROR CONNECTION)
            self.TCPIP = False
            self.light_conn_status = False
            print('ERROR! TCPIP CONNECTION FAILED')

            Warning_Msgbox(message = 'POSSIBLE PROBLEMS:\n\n1. LOOSE CONNECTION\n2. INCORRECT COMPORT\n3. CONTROLLER IS SWITCHED OFF'
                    , title = 'CONNECTION ERROR', font = 'Helvetica 10', height = 160
                    , parent = self.light_connection_toplvl, parent_grab_set = True)
            #self.main_lib.TCPIPDisconnect()


    def USB_connect(self):
        status = self.main_lib.USBConnect()
        #print(status)
        #print(ctrl)
        if status == 0:
            self.firmware_version_str = self.main_lib.ReadFWVersion()
            try:
                self.master_firmware_version_str = self.main_lib.ReadMasterFWVersion()
                if self.master_firmware_version_str == 'ERR':
                    self.master_firmware_version_str = self.main_lib.ReadFWVersion()
            except:
                self.master_firmware_version_str = self.main_lib.ReadFWVersion()

            firmware_model = firmware_check(self.firmware_version_str)
            master_firmware_model = firmware_check(self.master_firmware_version_str)
            
            if firmware_model is None and master_firmware_model is None:
                self.firmware_model = None

            elif firmware_model is None and type(master_firmware_model) == str:
                self.firmware_model = master_firmware_model

            elif type(firmware_model) == str and master_firmware_model is None:
                self.firmware_model = firmware_model

            elif type(firmware_model) == str and type(master_firmware_model) == str:
                self.firmware_model = firmware_model

            if self.firmware_model == self.firmware_model_sel:
                print('Connection Success')
                self.USB = True
                self.light_conn_status = True
                self.light_connection_toplvl.destroy()
                
                self.scrolled_canvas.rmb_all_func()

                self.light_connect_btn_state()
                self.top_frame_light_info()

                self.light_interface_disp()
                #lighting_interface_v2()
                #load_button_click()

            elif firmware_model != firmware_model_sel:
                self.USB = False
                self.light_conn_status = False
                print('ERROR! FIRMWARE ERROR')

                Warning_Msgbox(message = 'DETECTED FIRMWARE VERSION: '+ str(self.firmware_version_str) + '\n\n' + 'EXPECTED LC18 MODEL: LC18-' + str(self.firmware_model) + 
                        '\n\nFIRMWARE IS NOT COMPATIBLE.\nPLEASE SELECT THE CORRECT MODEL.', title = 'FIRMWARE ERROR', font = 'Helvetica 10', height = 225
                        , parent = self.light_connection_toplvl, parent_grab_set = True)
                self.main_lib.USBDisconnect()#Since status is return as 0 in this 'If' statement when we are technically 'connected', We have to disconnect to clear the USB bus.

        else: #if status == 1 (ERROR CONNECTION)
            self.USB = False
            self.light_conn_status = False
            print('ERROR! USB CONNECTION FAILED')

            Warning_Msgbox(message = 'POSSIBLE PROBLEMS:\n\n1. LOOSE CONNECTION\n2. INCORRECT COMPORT\n3. CONTROLLER IS SWITCHED OFF'
                    , title = 'CONNECTION ERROR', font = 'Helvetica 10', height = 160
                    , parent = self.light_connection_toplvl, parent_grab_set = True)
            #self.main_lib.USBDisconnect()


    def light_disconnect(self):
        self.scrolled_canvas.window_fr['width'] = self.scrolled_canvas_W
        self.scrolled_canvas.window_fr['height'] = self.scrolled_canvas_H

        self.scrolled_canvas.forget_all_func() #ScrolledCanvas Library
        self.light_disconnect_dll()
        self.light_conn_status = False
        self.light_connect_btn_state()
        self.forget_light_info()

        # self.thread_event_repeat.set()
        # self.thread_event_repeat_ALL.set()

        self.firmware_version_str = None
        self.firmware_model = None
        self.firmware_model_sel = None

        self.master_firmware_version_str = None

        try:
            self.light_interface.sq_frame_toplvl.destroy()
        except AttributeError:
            pass
        try:
            self.light_interface.Stop_Threads()
        except AttributeError:
            pass

        del self.light_interface
        self.light_interface = None

    def light_quit_func(self):
        self.light_disconnect_dll()
        try:
            self.light_interface.Stop_Threads()
        except AttributeError:
            pass

    def light_disconnect_dll(self):
        print('Light Disconnect (LC Library): ', self.main_lib)

        if str(self.main_lib) == 'LC18Library.LC18SQ':
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
        pass

    def light_interface_disp(self):
        if self.firmware_model_sel == 'LC20':
            self.light_interface = LC20_GUI(self.scrolled_canvas.window_fr, self.main_lib, self.light_conn_status, self.firmware_model_sel, self.firmware_version_str, self.infinity_icon
                , None, self.thread_event_repeat_ALL, width = 1500 - 330, height = 900, bg = 'white')
            self.light_interface.place(x=0, y=0, anchor = 'nw')

        elif self.firmware_model_sel != 'LC20' and self.firmware_model_sel != None:
            if self.firmware_model_sel == 'SQ':
                self.light_interface = LC18_SQ_GUI(self.scrolled_canvas.window_fr, self.main_lib, self.light_conn_status, self.firmware_model_sel, self.firmware_version_str, self.infinity_icon
                    , self.thread_event_repeat, None, width = 1500 - 330, height = 900, bg = 'white')
                self.light_interface.place(x=0, y=0, anchor = 'nw')

            elif self.firmware_model_sel == '4CH/16CH':
                self.light_interface = LC18_16CH_GUI(self.scrolled_canvas.window_fr, self.main_lib, self.light_conn_status, self.firmware_model_sel, self.firmware_version_str, self.infinity_icon
                    , self.thread_event_repeat, self.thread_event_repeat_ALL, width = 1500 - 330, height = 900, bg = 'white')
                self.light_interface.place(x=0, y=0, anchor = 'nw')

            elif self.firmware_model_sel == 'OD':
                self.light_interface = LC18_OD_GUI(self.scrolled_canvas.window_fr, self.main_lib, self.light_conn_status, self.firmware_model_sel, self.firmware_version_str, self.infinity_icon
                    , self.thread_event_repeat, self.thread_event_repeat_ALL, width = 1500 - 330, height = 900, bg = 'white')
                self.light_interface.place(x=0, y=0, anchor = 'nw')

            elif self.firmware_model_sel == 'KP':
                self.light_interface = LC18_KP_GUI(self.scrolled_canvas.window_fr, self.main_lib, self.light_conn_status, self.firmware_model_sel, self.firmware_version_str, self.infinity_icon
                    , self.thread_event_repeat, self.thread_event_repeat_ALL, width = 1500 - 330, height = 900, bg = 'white')
                self.light_interface.place(x=0, y=0, anchor = 'nw')

            elif self.firmware_model_sel == 'RGBW':
                self.light_interface = LC18_RGBW_GUI(self.scrolled_canvas.window_fr, self.main_lib, self.light_conn_status, self.firmware_model_sel, self.firmware_version_str, self.infinity_icon
                    , self.thread_event_repeat, self.thread_event_repeat_ALL, width = 1500 - 330, height = 900, bg = 'white')
                self.light_interface.place(x=0, y=0, anchor = 'nw')

            elif self.firmware_model_sel == 'X10': #LC18-1CH
                self.light_interface = LC18_1CH_GUI(self.scrolled_canvas.window_fr, self.main_lib, self.light_conn_status, self.firmware_model_sel, self.firmware_version_str, self.infinity_icon
                    , self.thread_event_repeat, self.thread_event_repeat_ALL, width = 1500 - 330, height = 900, bg = 'white')
                self.light_interface.place(x=0, y=0, anchor = 'nw')

            elif self.firmware_model_sel == 'X5': #LC18-2CH
                self.light_interface = LC18_2CH_GUI(self.scrolled_canvas.window_fr, self.main_lib, self.light_conn_status, self.firmware_model_sel, self.firmware_version_str, self.infinity_icon
                    , self.thread_event_repeat, self.thread_event_repeat_ALL, width = 1500 - 330, height = 900, bg = 'white')
                self.light_interface.place(x=0, y=0, anchor = 'nw')