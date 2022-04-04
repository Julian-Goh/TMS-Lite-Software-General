import os
from os import path
import sys

import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
import inspect
import ctypes
from ctypes import *

import threading
import msvcrt

from tool_tip import CreateToolTip

from Hikvision_GUI import Hikvision_GUI
from hikvision_operation import Hikvision_Operation

code_PATH = os.getcwd()
sys.path.append(code_PATH + '\\MVS-Python\\MvImport')
from MvCameraControl_class import *

class Camera_Connect():
    def __init__(self, master, top_frame, scroll_canvas, tk_gui_bbox
        , tms_logo_2 = None, cam_disconnect_img = None
        , toggle_ON_button_img = None, toggle_OFF_button_img = None, img_flip_icon = None, record_start_icon = None, record_stop_icon = None
        , save_icon = None, popout_icon = None, info_icon = None, fit_to_display_icon = None, setting_icon = None, window_icon = None
        , inspect_icon= None, help_icon = None, add_icon = None, minus_icon = None
        , close_icon = None, video_cam_icon = None, refresh_icon = None, folder_impil = None):

        self.master = master
        self.top_frame = top_frame
        self.scroll_canvas = scroll_canvas

        self.tms_logo_2 = tms_logo_2
        
        self.cam_disconnect_img = cam_disconnect_img
        self.toggle_ON_button_img = toggle_ON_button_img
        self.toggle_OFF_button_img = toggle_OFF_button_img
        
        self.img_flip_icon = img_flip_icon
        self.record_start_icon = record_start_icon
        self.record_stop_icon = record_stop_icon
        self.popout_icon = popout_icon
        self.save_icon = save_icon
        self.info_icon = info_icon
        self.fit_to_display_icon = fit_to_display_icon
        self.setting_icon = setting_icon
        self.window_icon = window_icon

        self.window_icon = window_icon
        self.inspect_icon = inspect_icon
        self.help_icon = help_icon
        self.add_icon = add_icon
        self.minus_icon = minus_icon
        self.close_icon = close_icon

        self.video_cam_icon = video_cam_icon
        self.refresh_icon = refresh_icon
        self.folder_impil = folder_impil

        self.cam_conn_status = False
        self.active_gui = None
        self.active_gui_str = None

        self.nSelCamIndex = 0
        self.cam_device_type_str = 'Hikvision'
        self.cam_device_type_var = tk.StringVar(value = self.cam_device_type_str)
        
        self.cam_update_handle = None

        self.devList = [] #init the list again since it is running in a loop #We use this list for display purposes on the GUI

        self.hikvision_devList = [] #We pass this list to the Open Device Function in Hikvision Library
        self.hikvision_list_tracer = int(0) #trace the length of devList

        self.tk_gui_bbox = tk_gui_bbox
        ### INIT HIKVISION classes.
        self.mv_camera = MvCamera()
        self.obj_cam_operation = Hikvision_Operation(self.mv_camera)

        self.hikvision_gui = Hikvision_GUI(self.scroll_canvas.window_fr, self.scroll_canvas, self.obj_cam_operation
            , self.cam_conn_status, self
            , self.tms_logo_2, self.cam_disconnect_img
            , self.toggle_ON_button_img, self.toggle_OFF_button_img, self.img_flip_icon, self.record_start_icon, self.record_stop_icon, self.save_icon
            , self.popout_icon, self.info_icon, self.fit_to_display_icon, self.setting_icon, self.window_icon
            , inspect_icon= self.inspect_icon, help_icon = self.help_icon, add_icon = self.add_icon, minus_icon = self.minus_icon
            , close_icon = self.close_icon, video_cam_icon = self.video_cam_icon, refresh_icon = self.refresh_icon, folder_impil = self.folder_impil
            , bg = 'white')

        self.cam_gui_sel()

        self.main_frame = tk.Frame(self.scroll_canvas.window_fr, bg = 'orange') #use for auto-check camera devices only. lower() is invoked to place it behind the main GUI.
        self.main_frame.place(relx = 0, rely = 0, x=0, y=0, relwidth = 1, relheight = 1, anchor = 'nw')
        self.main_frame.lower()

        self.cam_connect_btn_init()


    def cam_gui_sel(self):
        if self.cam_device_type_var.get() == 'Hikvision':
            self.active_gui = self.hikvision_gui
            self.hikvision_gui.place(relx = 0, rely = 0, x=0, y=0, relwidth = 1, relheight = 1, anchor = 'nw')
            self.tk_gui_bbox.bind('<Configure>', lambda e: self.hikvision_gui.gui_bbox_event(e))

    def cam_connect_func(self):
        if self.cam_device_type_var.get() == 'Hikvision':
            self.cam_gui_sel()
            self.hikvision_gui.open_device(self.hikvision_devList, self.nSelCamIndex)
            self.cam_conn_status = self.hikvision_gui.cam_conn_status
            self.hikvision_gui.camera_control_state()
            self.cam_connect_btn_state()
            if self.cam_conn_status == True:
                self.active_gui_str = self.cam_device_type_var.get()
            elif self.cam_conn_status == False:
                self.active_gui_str = None

    def cam_disconnect_func(self):
        if self.cam_device_type_var.get() == 'Hikvision':
            self.hikvision_gui.cam_disconnect()
            self.cam_conn_status = self.hikvision_gui.cam_conn_status
            # self.hikvision_gui.btn_normal_cam_mode.invoke()
            self.hikvision_gui.camera_control_state()
            self.cam_connect_btn_state()

    def stop_auto_toggle_parameter(self):
        if self.cam_device_type_var.get() == 'Hikvision':
            self.hikvision_gui.stop_auto_toggle_parameter()

    def start_auto_toggle_parameter(self):
        if self.cam_device_type_var.get() == 'Hikvision':
            self.hikvision_gui.start_auto_toggle_parameter()

    def record_setting_close(self):
         if self.cam_device_type_var.get() == 'Hikvision':
            self.hikvision_gui.record_setting_close()


    def cam_quit_func(self):
        if self.cam_device_type_var.get() == 'Hikvision':
            self.hikvision_gui.cam_quit_func()

    #1. CAM CONNECT GUI
    def cam_connect_btn_init(self):
        self.cam_conn_btn_1 = tk.Button(self.top_frame, relief = tk.GROOVE, activebackground = 'forest green', bg = 'green3', activeforeground = 'white', fg = 'white'
                , text='CONNECT', width = 10, height = 1, font='Helvetica 14 bold')

        self.cam_disconn_btn = tk.Button(self.top_frame, relief = tk.GROOVE, activebackground = 'red3', bg = 'red', activeforeground = 'white', fg = 'white'
                , text='DISCONNECT', width = 10, height = 1, font='Helvetica 14 bold')

    def cam_connect_btn_state(self):
        # print('self.cam_conn_status: ', self.cam_conn_status)
        if self.cam_conn_status == False:
            self.cam_disconn_btn.place_forget()
            self.cam_conn_btn_1['command'] = self.cam_connection_popout
            self.cam_conn_btn_1.place(relx = 0.75 , y = 20)

        elif self.cam_conn_status == True:
            self.cam_conn_btn_1.place_forget()
            self.cam_disconn_btn['command'] = self.cam_disconnect_func
            self.cam_disconn_btn.place(relx = 0.75 , y = 20)

    def forget_cam_connect_btn(self):
        try:
            if self.cam_conn_btn_1.winfo_exists() == 1:
                self.cam_conn_btn_1.place_forget()
        except AttributeError:
            pass

        try:
            if self.cam_disconn_btn.winfo_exists() == 1:
                self.cam_disconn_btn.place_forget()
        except AttributeError:
            pass

    def CAM_stop_checkforUpdates(self):
        #print('before', self.cam_update_handle)
        if self.cam_update_handle != None:
            self.main_frame.after_cancel(self.cam_update_handle)
        else:
            self.cam_update_handle = None
            pass

        #print('after', self.cam_update_handle)

    def CAM_device_checkForUpdates(self):
        #print(self.cam_device_type_var.get())
        if self.cam_device_type_var.get() == 'Hikvision':
            self.enum_devices()
            update_interval = 200 #150

        try:
            if self.cam_device_list.winfo_exists() == 1:
                self.cam_device_list["value"] = self.devList
                
                if self.update_cam_list == True:
                    self.cam_device_list.set('')
                    self.cam_device_list.event_generate('<Escape>')
                    #self.cam_conn_btn_2['state'] = 'normal'
                    self.update_cam_list = False
                
                if self.cam_device_list.get() == '':
                    self.cam_device_list.current(0)

                self.xFunc()
            else:
                pass
        except (AttributeError, tk.TclError):
            pass

        self.cam_update_handle = self.main_frame.after(update_interval, self.CAM_device_checkForUpdates) #check every 150
        #print(self.cam_update_handle)

    def cam_connection_popout(self):
        try:
            #print('try')
            check_bool = tk.Toplevel.winfo_exists(self.cam_connection_toplvl)
            if check_bool == 0:
                #print('not exist')
                self.cam_connection_toplvl = tk.Toplevel(master = self.master, width = 700, height = 500)

                self.cam_connection_toplvl.resizable(False, False)
                self.cam_connection_toplvl['bg'] = 'white'
                self.cam_connection_toplvl.title('Camera Connect Settings')
                screen_width = self.cam_connection_toplvl.winfo_screenwidth()
                screen_height = self.cam_connection_toplvl.winfo_screenheight()
                x_coordinate = int((screen_width/2) - (700/2))
                y_coordinate = int((screen_height/2) - (500/2))
                self.cam_connection_toplvl.geometry("{}x{}+{}+{}".format(700, 500, x_coordinate, y_coordinate))

                try:
                    self.cam_connection_toplvl.iconphoto(False, self.window_icon)
                except Exception:
                    pass
            else:
                #print('exist')
                self.cam_connection_toplvl.lift()
                pass
        except:
            #print('except')
            self.cam_connection_toplvl = tk.Toplevel(master = self.master, width = 700, height = 500) #TKINTER GENERATION CANNOT WORK WITH THREAD

            self.cam_connection_toplvl.resizable(False, False)
            self.cam_connection_toplvl['bg'] = 'white'
            self.cam_connection_toplvl.title('Camera Connect Settings')
            screen_width = self.cam_connection_toplvl.winfo_screenwidth()
            screen_height = self.cam_connection_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (700/2))
            y_coordinate = int((screen_height/2) - (500/2))
            self.cam_connection_toplvl.geometry("{}x{}+{}+{}".format(700, 500, x_coordinate, y_coordinate))

            try:
                self.cam_connection_toplvl.iconphoto(False, self.window_icon)
            except Exception:
                pass

        self.cam_connection_toplvl.grab_set()
        self.cam_connection_toplvl.protocol("WM_DELETE_WINDOW", self.cam_connection_popout_exit)

        tk.Label(self.cam_connection_toplvl, text= ('Camera Connect Settings'), font= 'Helvetica 14 bold', bg = 'white').place(x= 230, y = 120)
        tk.Label(self.cam_connection_toplvl, image = self.tms_logo_2, bg = 'white').place(x= 270, y = 0)
        copyright_symbol = chr(169)
        copyright_text = ('Copyright ' + copyright_symbol + ' 2004 - 2020 TMS Lite Sdn Bhd.') + '\n All Right Reserved.'
        tk.Label(self.cam_connection_toplvl, text= copyright_text, font= 'Helvetica 12', bg = 'white').place(x= 200, y = 450)


        self.cam_conn_btn_2 = tk.Button(self.cam_connection_toplvl, relief = tk.GROOVE, activebackground = 'forest green', bg = 'green3', activeforeground = 'white', fg = 'white'
        , text='CONNECT', width = 10, height = 1, font='Helvetica 14 bold')
        self.cam_conn_btn_2.place(x=280, y = 330)

        self.cam_connection_toplvl.option_add('*TCombobox*Listbox.font', ('Helvetica', '11'))

        self.cam_device_list = ttk.Combobox(self.cam_connection_toplvl, width=35, state='readonly',font = 'Helvetica 11')

        self.cam_device_list.bind("<<ComboboxSelected>>", self.xFunc)
        self.cam_device_list.place(x= 120, y = 250)

        self.label_no_of_cam = tk.Label(self.cam_connection_toplvl, text = 'No. of Camera(s): 0', font = 'Helvetica 11')
        self.label_no_of_cam['bg'] = 'white'
        self.label_no_of_cam.place(x=450, y=250)
        

        tk.Label(self.cam_connection_toplvl, text = 'Select the Type of Device: ', font = 'Helvetica 10', bg = 'white').place(x = 120, y = 190)
        self.radio_hikvision = tk.Radiobutton(self.cam_connection_toplvl, text='Hikvision',variable = self.cam_device_type_var, value='Hikvision',width=15, height=1
            , font = 'Helvetica 10', bg = 'white', anchor = 'w', activebackground = 'white')
        self.radio_hikvision['command'] = self.cam_type_sel
        self.radio_hikvision.place(x=120,y= 210)

        self.cam_type_sel()

    def cam_connection_popout_exit(self):
        self.cam_device_type_str = 'Hikvision'
        self.cam_device_type_var.set(self.cam_device_type_str)
        self.CAM_stop_checkforUpdates()
        self.cam_gui_sel()

        try:
            self.cam_connection_toplvl.destroy()
        except (AttributeError, tk.TclError):
            pass

    def cam_type_sel(self):
        if self.cam_device_type_var.get() == 'Hikvision':
            self.CAM_stop_checkforUpdates()

            self.cam_device_type_str = 'Hikvision'
            self.cam_device_list.set('')

            self.cam_conn_btn_2['command'] = self.cam_connect_func
            self.label_no_of_cam['text'] = 'No. of Camera(s): 0'
            self.devList *= 0

            self.CAM_device_checkForUpdates()

    #2. HIKVISION ENUM
    def TxtWrapBy(self, start_str, end, all):
        start = all.find(start_str)
        if start >= 0:
            start += len(start_str)
            end = all.find(end, start)
            if end >= 0:
                return all[start:end].strip()

    def xFunc(self, event = None):
        #print(self.cam_device_list.get())
        self.nSelCamIndex = self.TxtWrapBy("[","]",self.cam_device_list.get())
        #print(self.nSelCamIndex)
        #self.nSelCamIndex is needed to execute open device

        #print(nSelCamIndex)
    #ch:枚举相机 | en:enum devices
    def enum_devices(self):
        self.devList *= 0 #init the list again since it is running in a loop #We use this list for display purposes on the GUI
        self.hikvision_devList *= 0 #We pass this list to the Open Device Function in Hikvision Library

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
                
                # print(str_manufacturer, len(str_manufacturer))
                if str_manufacturer == "Hikvision" or str_manufacturer == "Hikrobot": #"Hikvision" "Hikrobot"
                    strModeName = ""
                    for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                        strModeName = strModeName + chr(per)
                    # print ("device model name: %s" % strModeName)

                    nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                    nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                    nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                    nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                    #print ("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
                    #self.devList.append("Gige["+str(i)+"]:"+str(nip1)+"."+str(nip2)+"."+str(nip3)+"."+str(nip4))
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

                    #print ("user serial number: %s" % strSerialNumber)
                    #self.devList.append("USB["+str(i)+"] "+str(strSerialNumber))
                    self.devList.append("USB["+str(hikvision_cam_index)+"] " + strModeName + ' (' + str(strSerialNumber) +')')
                    self.hikvision_devList.append(mvcc_dev_info)
                    hikvision_cam_index += 1

        try:
            check_bool = tk.Toplevel.winfo_exists(self.cam_connection_toplvl)
            if check_bool == 0:
                pass
            elif check_bool != 0:
                self.label_no_of_cam['text'] = ' '
                self.label_no_of_cam['text'] = 'No. of Camera(s): ' + str(hikvision_cam_index)
        except AttributeError:
            pass

        if hikvision_cam_index == 0:
            try:
                self.cam_device_list.set('')
            except (AttributeError, tk.TclError):
                pass

        if len(self.devList) != self.hikvision_list_tracer:
            self.update_cam_list = True
            # self.cam_conn_btn_2['state'] = 'disable'
            # from main_GUI import main_GUI
            # try:
            #     main_GUI.class_multi_cam_conn.refresh_devices()
            # except Exception:
            #     pass

        elif len(self.devList) == self.hikvision_list_tracer:
            self.update_cam_list = False

        self.hikvision_list_tracer = len(self.devList)

        hikvision_cam_index = int(0)
