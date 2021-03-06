import os
from os import path
import sys

import tkinter as tk
import inspect
import ctypes
from ctypes import *

import threading
import msvcrt

from Hikvision_GUI import Hikvision_GUI
from hikvision_operation import Hikvision_Operation

from misc_module.image_resize import img_resize_dim, opencv_img_resize, pil_img_resize
from misc_module.tk_img_module import to_tk_img
from misc_module.tool_tip import CreateToolTip

from Tk_Custom_Widget.tk_custom_combobox import CustomBox
from Tk_Custom_Widget.tk_custom_toplvl import CustomToplvl

# code_PATH = os.getcwd()
# sys.path.append(code_PATH + '\\MVS-Python\\MvImport')

from MvCameraControl_class import *

class Camera_Connect():
    def __init__(self, master, top_frame, scroll_canvas, tk_gui_bbox
        , light_class = None
        , gui_graphic = {}):

        self.master = master
        self.top_frame = top_frame
        self.scroll_canvas = scroll_canvas
        self.light_class = light_class ### Class for Light Control Tool. This is specifically for LC18 SQ and LC20 SQ
        # print("self.light_class: ", light_class)

        self.gui_graphic = dict(tms_logo = None, cam_disconnect_img = None
            , toggle_ON_button_img = None, toggle_OFF_button_img = None, img_flip_icon = None, record_start_icon = None, record_stop_icon = None
            , save_icon = None, popout_icon = None, info_icon = None, fit_to_display_icon = None, setting_icon = None, window_icon = None
            , inspect_icon= None, help_icon = None, add_icon = None, minus_icon = None
            , close_icon = None, video_cam_icon = None, refresh_icon = None, folder_impil = None)

        for key, item in gui_graphic.items():
            if key in self.gui_graphic:
                self.gui_graphic[key] = item

        self.window_icon            = self.gui_graphic['window_icon']

        self.tms_logo               = to_tk_img(pil_img_resize(self.gui_graphic['tms_logo'], img_height = 110))
        
        self.cam_disconnect_img     = to_tk_img(pil_img_resize(self.gui_graphic['cam_disconnect_img'], img_width = 150, img_height = 150))
        self.toggle_ON_button_img   = to_tk_img(pil_img_resize(self.gui_graphic['toggle_ON_button_img'], img_scale = 0.06))
        self.toggle_OFF_button_img  = to_tk_img(pil_img_resize(self.gui_graphic['toggle_OFF_button_img'], img_scale = 0.06))
        
        self.img_flip_icon          = to_tk_img(pil_img_resize(self.gui_graphic['img_flip_icon'], img_scale = 0.033))
        self.record_start_icon      = to_tk_img(pil_img_resize(self.gui_graphic['record_start_icon'], img_scale = 0.035))
        self.record_stop_icon       = to_tk_img(pil_img_resize(self.gui_graphic['record_stop_icon'], img_scale = 0.035))
        self.popout_icon            = to_tk_img(pil_img_resize(self.gui_graphic['popout_icon'], img_scale = 0.1))
        self.save_icon              = to_tk_img(pil_img_resize(self.gui_graphic['save_icon'], img_scale = 0.035))
        self.info_icon              = to_tk_img(pil_img_resize(self.gui_graphic['info_icon'], img_scale = 0.13))
        self.fit_to_display_icon    = to_tk_img(pil_img_resize(self.gui_graphic['fit_to_display_icon'], img_width = 22, img_height =22))
        self.setting_icon           = to_tk_img(pil_img_resize(self.gui_graphic['setting_icon'], img_width = 18, img_height =18))

        self.inspect_icon           = to_tk_img(pil_img_resize(self.gui_graphic['inspect_icon'], img_scale = 0.025))
        self.help_icon              = to_tk_img(pil_img_resize(self.gui_graphic['help_icon'], img_width = 20, img_height =20))
        self.add_icon               = to_tk_img(pil_img_resize(self.gui_graphic['add_icon'], img_width = 18, img_height =18))
        self.minus_icon             = to_tk_img(pil_img_resize(self.gui_graphic['minus_icon'], img_width = 18, img_height =18))
        self.close_icon             = to_tk_img(pil_img_resize(self.gui_graphic['close_icon'], img_width = 20, img_height =20))

        self.video_cam_icon         = to_tk_img(pil_img_resize(self.gui_graphic['video_cam_icon'], img_width = 18, img_height =18))
        self.refresh_icon           = to_tk_img(pil_img_resize(self.gui_graphic['refresh_icon'], img_width = 18, img_height =18))

        self.folder_impil           = self.gui_graphic['folder_impil']

        del self.gui_graphic

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

        ### INIT HIKVISION GUI classes.
        self.mv_camera = MvCamera()
        self.obj_cam_operation = Hikvision_Operation(self.mv_camera)
        # print(dir(self.obj_cam_operation))

        self.hikvision_gui = Hikvision_GUI(self.scroll_canvas.window_fr, self.scroll_canvas, self.obj_cam_operation
            , self.cam_conn_status, self
            , self.light_class
            , self.cam_disconnect_img
            , self.toggle_ON_button_img, self.toggle_OFF_button_img, self.img_flip_icon, self.record_start_icon, self.record_stop_icon, self.save_icon
            , self.popout_icon, self.info_icon, self.fit_to_display_icon, self.setting_icon, self.window_icon
            , inspect_icon= self.inspect_icon, help_icon = self.help_icon, add_icon = self.add_icon, minus_icon = self.minus_icon
            , close_icon = self.close_icon, video_cam_icon = self.video_cam_icon, refresh_icon = self.refresh_icon, folder_impil = self.folder_impil
            , bg = 'white')

        self.obj_cam_operation.load_gui_class(self.light_class, self.hikvision_gui)

        self.cam_gui_sel()
        
        self.proxy_fr = tk.Frame(self.scroll_canvas.window_fr, width = 1, height = 1) #use for auto-check camera devices only. lower() is invoked to place it behind the main GUI.
        self.proxy_fr.place(x = 0, y = 0, anchor = 'nw')
        self.proxy_fr.lower()

        self.cam_connect_btn_init()
        self.conn_popout_gen()

    def cam_gui_sel(self):
        if self.cam_device_type_var.get() == 'Hikvision':
            self.active_gui = self.hikvision_gui
            self.hikvision_gui.place(relx = 0, rely = 0, x=0, y=0, relwidth = 1, relheight = 1, anchor = 'nw')

    def cam_gui_update(self):
        ### function to update any existing display if required when user show the corresponding camera gui.
        if self.cam_device_type_var.get() == 'Hikvision':
            self.hikvision_gui.update_gui()

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
                , text='CONNECT', width = 10, height = 1, font='Helvetica 16 bold')
        self.cam_conn_btn_1['command'] = self.conn_popout_open

        self.cam_disconn_btn = tk.Button(self.top_frame, relief = tk.GROOVE, activebackground = 'red3', bg = 'red', activeforeground = 'white', fg = 'white'
                , text='DISCONNECT', width = 10, height = 1, font='Helvetica 16 bold')
        self.cam_disconn_btn['command'] = self.cam_disconnect_func

    def cam_connect_btn_state(self):
        # print('self.cam_conn_status: ', self.cam_conn_status)
        if self.cam_conn_status == False:
            self.cam_disconn_btn.grid_forget()
            self.cam_conn_btn_1.grid(row = 0, column = 3, rowspan = 2,pady = 20, padx = 50, sticky = 'nse')

        elif self.cam_conn_status == True:
            self.cam_conn_btn_1.grid_forget()
            self.cam_disconn_btn.grid(row = 0, column = 3, rowspan = 2,pady = 20, padx = 50, sticky = 'nse')

    def cam_connect_btn_hide(self):
        self.cam_conn_btn_1.grid_forget()
        self.cam_disconn_btn.grid_forget()

    def CAM_stop_checkforUpdates(self):
        #print('before', self.cam_update_handle)
        if self.cam_update_handle != None:
            self.proxy_fr.after_cancel(self.cam_update_handle)
        else:
            self.cam_update_handle = None
            pass

        #print('after', self.cam_update_handle)

    def CAM_device_checkForUpdates(self):
        # print(self.cam_device_type_var.get())
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

        self.cam_update_handle = self.proxy_fr.after(update_interval, self.CAM_device_checkForUpdates) #check every 150
        #print(self.cam_update_handle)

    def conn_popout_gen(self):
        self.cam_connection_toplvl = CustomToplvl(self.master, toplvl_title = 'Connect Settings', icon_img = self.window_icon, topmost_bool = True)
        self.cam_connection_toplvl['width']  = 700
        self.cam_connection_toplvl['height'] = 500
        self.cam_connection_toplvl['bg']     = 'white'
        self.cam_connection_toplvl.resizable(False, False)
        self.cam_connection_toplvl.protocol("WM_DELETE_WINDOW", self.conn_popout_close)
        self.conn_popout_gui()

    def conn_popout_gui(self):
        tk.Label(self.cam_connection_toplvl, text= ('Camera Connect Settings'), font= 'Helvetica 14 bold', bg = 'white').place(x= 230, y = 120)
        tk.Label(self.cam_connection_toplvl, image = self.tms_logo, bg = 'white').place(x= 270, y = 0)
        copyright_symbol = chr(169)
        copyright_text = ('Copyright ' + copyright_symbol + ' 2004 - 2020 TMS Lite Sdn Bhd.') + '\n All Right Reserved.'
        tk.Label(self.cam_connection_toplvl, text= copyright_text, font= 'Helvetica 12', bg = 'white').place(x= 200, y = 450)


        self.cam_conn_btn_2 = tk.Button(self.cam_connection_toplvl, relief = tk.GROOVE, activebackground = 'forest green', bg = 'green3', activeforeground = 'white', fg = 'white'
        , text='CONNECT', width = 10, height = 1, font='Helvetica 14 bold')
        self.cam_conn_btn_2.place(x=280, y = 330)

        self.cam_device_list = CustomBox(self.cam_connection_toplvl, width=35, state='readonly',font = 'Helvetica 11')

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

    def conn_popout_open(self):
        if False == self.cam_connection_toplvl.check_open():
            toplvl_W = self.cam_connection_toplvl['width']
            toplvl_H = self.cam_connection_toplvl['height']
            screen_width = self.cam_connection_toplvl.winfo_screenwidth()
            screen_height = self.cam_connection_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (toplvl_W/2))
            y_coordinate = int((screen_height/2) - (toplvl_H/2))
            self.cam_connection_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
            self.cam_connection_toplvl.open()
            self.cam_connection_toplvl.grab_set()
            self.cam_type_sel()
        
        else:
            self.cam_connection_toplvl.show()

    def conn_popout_close(self):
        self.cam_connection_toplvl.close()
        self.cam_device_type_str = 'Hikvision'
        self.cam_device_type_var.set(self.cam_device_type_str)
        self.CAM_stop_checkforUpdates()
        self.cam_gui_sel()

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
    #ch:???????????? | en:enum devices
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
                #if str_manufacturer ==  "Crevis Co., LTD":
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

        self.label_no_of_cam['text'] = ' '
        self.label_no_of_cam['text'] = 'No. of Camera(s): ' + str(hikvision_cam_index)

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
