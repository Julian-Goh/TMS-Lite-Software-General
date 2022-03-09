import os
from os import path
import sys
import copy

from PIL import ImageTk, Image
import numpy as np
import imutils

from imageio import imread
import cv2

import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from tkinter import filedialog

import inspect
import ctypes
from ctypes import *

import threading
import msvcrt


def int2Hex(num):
    OFFSET = 1 << 32
    MASK = OFFSET - 1

    hex_ = '%08x' % (num + OFFSET & MASK)
    byte_ = []
    str_hex = '0x'
    for i in range(0, 4):
        byte_.append('0x' + hex_[i * 2: i * 2 + 2])

    for i in byte_:
        str_hex = str_hex + i.split('0x')[1]
        #print(i)
        #print(str_hex)
    #return byte_#byte_[::-1]  # return in little endian
    return str_hex

def create_save_folder():
    PATH = os.getcwd()
    create_folder = PATH + r'\TMS_Saved_Images'
    #print(create_folder)
    print
    if path.exists(create_folder):
        #print ('File already exists')
        pass
    else:
        os.mkdir(create_folder)
        #print ('File created')
    return create_folder

def video_file_name(folder, file_name):
    index = 0
    loop = True
    while loop == True:
        file_path = folder + '\\'+ file_name + '_' + str(index) + '.avi'
        if (path.exists(file_path)) == True:
            index = index + 1
        elif (path.exists(file_path)) == False:
            loop = False

    return file_path

def cv_img_save(folder, img_arr, img_name, img_format):
    index = 0
    loop = True
    while loop == True:
        img_path = folder + '\\'+ img_name + '_' + str(index) + img_format
        if (path.exists(img_path)) == True:
            index = index + 1
        elif (path.exists(img_path)) == False:
            loop = False
    #print(img_arr.shape)
    if len(img_arr.shape) == 3:
        img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
    cv2.imwrite(img_path, img_arr)

    return img_path

def PDF_img_save(folder, img_arr, pdf_name, ch_split_bool = True):
    index = 0
    loop = True
    while loop == True:
        pdf_path = folder + '\\'+ pdf_name + '_' + str(index) + ".PDF"
        if (path.exists(pdf_path)) == True:
            index = index + 1
        elif (path.exists(pdf_path)) == False:
            loop = False

    pdf_img = np_to_PIL(img_arr)
    if len(img_arr.shape) == 3:
        if ch_split_bool == True:
            pdf_img_R = Image.fromarray(img_arr[:,:,0])
            pdf_img_G = Image.fromarray(img_arr[:,:,1])
            pdf_img_B = Image.fromarray(img_arr[:,:,2])
            pdf_img_list = [pdf_img, pdf_img_R, pdf_img_G, pdf_img_B]

        elif ch_split_bool == False:
            pdf_img_list = [pdf_img]
    else:
        pdf_img_list = [pdf_img]

    pdf_img_list[0].save(pdf_path, save_all=True, append_images= pdf_img_list[1:])
    #pdf_img_list[-1].save(pdf_path, save_all=True, append_images= pdf_img_list[:-1])
    #pdf_img.save(pdf_path, save_all=True)

def PDF_img_list_save(folder, pdf_img_list, pdf_name):
    index = 0
    loop = True
    while loop == True:
        pdf_path = folder + '\\'+ pdf_name + '_' + str(index) + ".PDF"
        if (path.exists(pdf_path)) == True:
            index = index + 1
        elif (path.exists(pdf_path)) == False:
            loop = False

    pdf_img_list[0].save(pdf_path, save_all=True, append_images= pdf_img_list[1:])

def np_to_PIL(img_arr):
    img_PIL = Image.fromarray(img_arr)

    return img_PIL

def display_func(display, ref_img, w, h, resize_status = True):
    if resize_status == True:
        #img_resize = imutils.resize(ref_img, height = h)
        img_resize = cv2.resize(ref_img,(w,h))
        # if len(img_resize.shape) == 3:
        #     img_resize = cv2.cvtColor(img_resize, cv2.COLOR_BGR2RGB)

        img_PIL = Image.fromarray(img_resize)
    elif resize_status == False:
        img_PIL = Image.fromarray(ref_img)

    img_tk = ImageTk.PhotoImage(img_PIL)
    try:
        display.create_image(w/2, h/2, image=img_tk, anchor='center', tags='img')
        display.image = img_tk
    except Exception as e:
        print('Error display_func: ', e)
        pass

def clear_display_func(display, w, h):
    try:
        display.create_image(w/2, h/2, image='', anchor='center', tags='img')
        display.image = ''
    except Exception as e:
        print('Error clear_display_func: ', e)
        pass

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

class Crevis_Operation():
    def __init__(self, crevis_pylib, nSelCamIndex=0):
        self.crevis_pylib = crevis_pylib
        self.nSelCamIndex = nSelCamIndex

        self.cam_width = None
        self.cam_height = None

        self.b_open_device = False

        self.b_save = False

        self.n_payload_size = 0
        self.buf_cache = None
        self.pixel_format = None

        self.frame_rate = 7.313889 #min: 7.313889, max: 14.94985
        self.exposure_time = 0 #min: 0, max: 66821.75
        self.gain = 14 #min: 14, max: 63

        self.brightness = 255 #min: 0, max: 255
        self.red_ratio = 1 #min: 1, max: 4095
        self.green_ratio = 1 #min: 1, max: 4095
        self.blue_ratio = 1 #min: 1, max: 4095
        self.black_lvl = 0 #min: 0 , max: 4095

        self.exposure_mode = 0
        self.gain_mode = 0
        self.framerate_mode = 0
        self.white_mode = 0

        self.numArray = None
        self.freeze_numArray = None
        self.disp_clear_ALL_status = False

        self.rgb_type = False
        self.mono_type = False

        self.trigger_mode = False
        self.bool_mode_switch = False
        self.trigger_src = 'LINE1' #'LINE1', 'SOFTWARE'

        self.start_grabbing_event = threading.Event()
        self.start_grabbing_event.set()

        self.mono_format_list = ["Mono8", "Mono10", "Mono10Packed", "Mono12", "Mono12Packed", "Mono14"]
        self.color_format_list = ["BayerBG8", "BayerBG10", "BayerBG12", "BayerBG10Packed", "BayerBG12Packed", "BayerRG8",
        "BayerRG10", "BayerRG12", "BayerRG10Packed", "BayerRG12Packed", "BayerGR8", "BayerGR10", "BayerGR12" ,"BayerGR10Packed",
        "BayerGR12Packed", "BayerGB8", "BayerGB10", "BayerGB12", "BayerGB10Packed", "BayerGB12Packed", "YUV422Packed", "RGB8Packed", "BGR8Packed"]

        self.record_init = False
        self.video_file = None
        self.video_writer = None

        self.sq_frame_save_list = []
        #EXTERNAL SQ STROBE FRAME PARAMETER(S)
        self.ext_sq_fr_init = False

        self.fit_to_display_bool = False

    def Init_device(self):
        self.crevis_pylib.ST_InitSystem()

    def Free_device(self):
        self.crevis_pylib.ST_FreeSystem()

    def Check_device(self):
        open_check = c_bool()
        self.crevis_pylib.ST_IsOpenDevice(open_check)

        return open_check.value

    def Open_device(self, index):
        #print('self.nSelCamIndex: ',self.nSelCamIndex)
        self.nSelCamIndex = int(index)
        #print(self.nSelCamIndex, type(self.nSelCamIndex))
        open_ret = self.crevis_pylib.ST_OpenDevice(self.nSelCamIndex, False)

        if open_ret != 0:
            pass
        else:
            # ret = self.crevis_pylib.ST_SetEnumReg('PixelFormat'.encode('utf-8'), 'Mono12Packed'.encode('utf-8'))
            # print(ret)

            n_payload_size = c_uint32()
            ret = self.crevis_pylib.ST_GetIntReg('PayloadSize'.encode('utf-8'), n_payload_size)
            # print('n_payload_size: ', n_payload_size)
            # print('get_payload_size: ', ret)
            self.n_payload_size = n_payload_size.value
            self.buf_cache = (c_ubyte * self.n_payload_size)()

            cam_width = c_int32()
            cam_height = c_int32()
            self.crevis_pylib.ST_GetIntReg('Width'.encode('utf-8') , cam_width)
            self.crevis_pylib.ST_GetIntReg('Height'.encode('utf-8') , cam_height)

            self.cam_width = cam_width.value
            self.cam_height = cam_height.value

            # print(cam_width, self.cam_width, type(self.cam_width))
            # print(cam_height, self.cam_height, type(self.cam_height))

            # print(self.cam_width >> 1)
            self.crevis_pylib.ST_SetEnumReg('TriggerMode'.encode('utf-8'), 'Off'.encode('utf-8'))

            ##################################################################
            pixel_format_check = self.Get_Pixel_Format()
            self.Default_Pixel_Format(pixel_format_check)
            ##################################################################

            self.Init_Framerate_Mode()
            self.Init_Exposure_Mode()
            self.Init_Gain_Mode()

            # self.Init_Balance_White_Mode()

            # pSize = c_uint32(256)
            # pInfo = (c_ubyte * 16)()
            # self.crevis_pylib.ST_GetStrReg('DeviceVersion'.encode('utf-8'), pInfo, pSize)
            # crevis_device_version = (bytes(pInfo).decode("utf-8"))#.strip().strip('\x00')
            # print('crevis_device_version: ',crevis_device_version)

        return open_ret

    def Set_Pixel_Format(self, pixel_str):
        self.Normal_Mode_display_clear()
        self.SQ_Mode_display_clear()

        ret = self.crevis_pylib.ST_SetEnumReg('PixelFormat'.encode('utf-8'), pixel_str.encode('utf-8'))
        # print('Set Pixel Format: ', ret)
        if ret == 0:
            n_payload_size = c_uint32()
            ret = self.crevis_pylib.ST_GetIntReg('PayloadSize'.encode('utf-8'), n_payload_size)
            # print('n_payload_size: ', n_payload_size)
            # print('get_payload_size: ', ret)
            self.n_payload_size = n_payload_size.value
            self.buf_cache = (c_ubyte * self.n_payload_size)()
            self.pixel_format = pixel_str

            if True == self.Pixel_Format_Mono(self.pixel_format):
                # print('Mono Detected')
                _cam_class.entry_red_ratio['state'] = 'disable'
                _cam_class.entry_green_ratio['state'] = 'disable'
                _cam_class.entry_blue_ratio['state'] = 'disable'
                _cam_class.btn_auto_white['image'] = _cam_class.toggle_OFF_button_img
                _cam_class.btn_auto_white['state'] = 'disable'
                _cam_class.auto_white_toggle = False

            elif True == self.Pixel_Format_Color(self.pixel_format):
                _cam_class.btn_auto_white['state'] = 'normal'
                self.Init_Balance_White_Mode()
                _cam_class.white_balance_btn_state()
                _cam_class.get_parameter_white()

        else:
            self.Get_Pixel_Format()
            tkinter.messagebox.showerror('Error','Current Camera Does Not Support\nPixel Format: ' + pixel_str)
            pass

    def Get_Pixel_Format(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        pSize = c_uint32(256)
        # pInfo = (c_ubyte * 16)()
        pInfo = (c_ubyte * 32)()
        ret = self.crevis_pylib.ST_GetEnumReg('PixelFormat'.encode('utf-8'), pInfo, pSize)
        self.pixel_format = (bytes(pInfo).decode("utf-8")).strip().strip('\x00')
        # print(self.pixel_format, type(self.pixel_format))
        # print('get_pixel_format: ', ret)
        _cam_class.get_pixel_format(self.pixel_format)

        if True == self.Pixel_Format_Mono(self.pixel_format):
            # print('Mono Detected')
            _cam_class.entry_red_ratio['state'] = 'disable'
            _cam_class.entry_green_ratio['state'] = 'disable'
            _cam_class.entry_blue_ratio['state'] = 'disable'
            _cam_class.btn_auto_white['image'] = _cam_class.toggle_OFF_button_img
            _cam_class.btn_auto_white['state'] = 'disable'
            _cam_class.auto_white_toggle = False

        elif True == self.Pixel_Format_Color(self.pixel_format):
            _cam_class.btn_auto_white['state'] = 'normal'
            self.Init_Balance_White_Mode()
            _cam_class.white_balance_btn_state()
            _cam_class.get_parameter_white()

        return self.pixel_format

    def Default_Pixel_Format(self, pixel_str): #Temporary solution for setting Pixel Format. Some format I have trouble converting for display...
        if pixel_str == 'Mono8' or pixel_str == 'Mono10' or pixel_str == 'Mono12' or pixel_str == 'RGB8Packed':
            pass

        else:
            if True == self.Is_mono_data(pixel_str):
                self.Set_Pixel_Format('Mono8')
            elif True == self.Is_color_data(pixel_str):
                self.Set_Pixel_Format('RGB8Packed')
            else:
                self.Set_Pixel_Format('Mono8')

            self.Get_Pixel_Format()


    def Pixel_Format_Mono(self, str_id):
        if str_id in self.mono_format_list:
            return True

        else:
            return False

    def Pixel_Format_Color(self, str_id):
        if str_id in self.color_format_list:
            return True

        else:
            return False

    def Init_Framerate_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        pSize = c_uint32(256)
        pInfo = (c_ubyte * 32)()
        ret = self.crevis_pylib.ST_GetEnumReg('AcquisitionFrameRateEnable'.encode('utf-8'), pInfo, pSize)
        if ret == 0:
            self.framerate_mode = (bytes(pInfo).decode("utf-8")).strip().strip('\x00')
            if self.framerate_mode == 'On':
                _cam_class.framerate_toggle = True
            else:
                _cam_class.framerate_toggle = False

        else:
            print ("get acquisition frame rate enable fail! ret: ", ret)

    def Init_Exposure_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        pSize = c_uint32(256)
        pInfo = (c_ubyte * 32)()
        ret = self.crevis_pylib.ST_GetEnumReg('ExposureAuto'.encode('utf-8'), pInfo, pSize)

        if ret == 0:
            self.exposure_mode = (bytes(pInfo).decode("utf-8")).strip().strip('\x00')
            # print('self.exposure_mode: ', self.exposure_mode)
            if self.exposure_mode == 'Continuous':
                _cam_class.auto_exposure_toggle = True
            else:
                _cam_class.auto_exposure_toggle = False

        else:
            print ("get exposure auto fail! ret: ", ret)

    def Init_Gain_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        pSize = c_uint32(256)
        pInfo = (c_ubyte * 32)()
        ret = self.crevis_pylib.ST_GetEnumReg('GainAuto'.encode('utf-8'), pInfo, pSize)

        if ret == 0:
            self.gain_mode = (bytes(pInfo).decode("utf-8")).strip().strip('\x00')
            # print('self.gain_mode: ', self.gain_mode)
            if self.gain_mode == 'Continuous':
                _cam_class.auto_gain_toggle = True
            else:
                _cam_class.auto_gain_toggle = False

        else:
            print ("get gain auto fail! ret: ", ret)

    def Init_Balance_White_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        pSize = c_uint32(256)
        pInfo = (c_ubyte * 32)()
        ret = self.crevis_pylib.ST_GetEnumReg('BalanceWhiteAuto'.encode('utf-8'), pInfo, pSize)
        # print('BalanceWhiteAuto Init: ', ret)
        if ret == 0:
            self.white_mode = (bytes(pInfo).decode("utf-8")).strip().strip('\x00')
            # print('self.white_mode: ', self.white_mode)
            if self.white_mode == 'Continuous':
                _cam_class.auto_white_toggle = True
            else:
                _cam_class.auto_white_toggle = False

        else:
            print ("get balance white auto fail! ret: ", ret)


    def Close_device(self):
        self.start_grabbing_event.set()
        self.crevis_pylib.ST_CloseDevice()
        self.b_start_grabbing = False


    def Set_mode(self, strMode):
        _prev_state = copy.copy(self.trigger_mode) #hold the previous state of self.trigger_mode
        # print('_prev_state: ', _prev_state)
        if 'continuous' == strMode:
            ret = self.crevis_pylib.ST_SetEnumReg('TriggerMode'.encode('utf-8'), 'Off'.encode('utf-8'))
            if ret == 0:
                self.trigger_mode = False
                self.bool_mode_switch = True #UPDATE 18-8-2021, Boolean to track Camera Mode switch
                if not self.start_grabbing_event.isSet():
                    # print('Waiting: ')
                    self.start_grabbing_event.wait(0.05)

            else:
                self.trigger_mode = _prev_state
            #print('Trigger Mode: ', ret)
            # print('self.trigger_mode: ', self.trigger_mode)
            return ret

        if 'triggermode' == strMode:
            ret = self.crevis_pylib.ST_SetEnumReg('TriggerMode'.encode('utf-8'), 'On'.encode('utf-8'))
            if ret == 0:
                self.trigger_mode = True
                self.bool_mode_switch = True #UPDATE 18-8-2021, Boolean to track Camera Mode switch
                if not self.start_grabbing_event.isSet():
                    # print('Waiting: ')
                    self.start_grabbing_event.wait(0.05)
            else:
                self.trigger_mode = _prev_state
            #print('Trigger Mode: ', ret)
            return ret

        del _prev_state

    def Trigger_Source(self, strSrc):
        _prev_state = copy.copy(self.trigger_src) #hold the previous state of self.trigger_src
        if strSrc == 'LINE1':
            ret = self.crevis_pylib.ST_SetEnumReg('TriggerSource'.encode('utf-8'), 'Line1'.encode('utf-8'))
            self.trigger_src = 'LINE1'
            return ret

        elif strSrc == 'SOFTWARE':
            ret = self.crevis_pylib.ST_SetEnumReg('TriggerSource'.encode('utf-8'), 'Software'.encode('utf-8'))
            self.trigger_src = "SOFTWARE"
            return ret

        del _prev_state
    
    def Trigger_once(self):
        ret = self.crevis_pylib.ST_SetCmdReg('TriggerSoftware'.encode('utf-8'))
        #print('ret Trigger once: ',ret)

    def Start_grab(self):
        start_ret = self.crevis_pylib.ST_AcqStart()
        # print('ST_AcqStart', start_ret)
        if start_ret != 0:
            self.b_start_grabbing = False
            tkinter.messagebox.showerror('show error','start grabbing fail! ret = ' + str(ret))
        else:
            try:
                self.start_grabbing_event.clear()
                self.h_thread_handle = threading.Thread(target=self.Work_thread, daemon = True)
                self.h_thread_handle.start()
                self.b_start_grabbing = True
            except:
                self.b_start_grabbing = False
                tkinter.messagebox.showerror('show error','error: unable to start thread')

        return start_ret

    def Stop_grab(self):
        self.start_grabbing_event.set()
        stop_ret = self.crevis_pylib.ST_AcqStop()
        self.b_start_grabbing = False
        #print('ST_AcqStop', ret)
        if stop_ret != 0:
            self.b_start_grabbing = False
            tkinter.messagebox.showerror('show error','stop grabbing fail! ret = ' + str(ret))

        return stop_ret

    def Work_thread(self):
        from main_GUI import main_GUI
        _light_class = main_GUI.class_light_conn
        _cam_class = main_GUI.class_cam_conn.active_gui

        img_buff = None

        self.rgb_type = False
        self.mono_type = False

        self.display_status = False
        self.record_init = False
        self.fit_to_display_bool = False

        while not self.start_grabbing_event.isSet():
            self.b_open_device = self.Check_device()
            if False == self.b_open_device:
                break
            ret = self.crevis_pylib.ST_GrabImage(byref(self.buf_cache), self.n_payload_size)
            # print('self.buf_cache: ', cast(self.buf_cache, POINTER(c_ubyte))[1])
            # print('Grabbing Image: ', ret)
            #self.start_grabbing_event.set()
            if self.bool_mode_switch == False:
                pass

            elif self.bool_mode_switch == True:
                self.bool_mode_switch = False
                self.ext_sq_fr_init = False
                continue

            if ret != 0:
                if self.trigger_mode == True and self.ext_sq_fr_init == True: #SQ Frame Function already started but not complete.
                    if True == self.SQ_Sync_Frame_Capture_Bool_External() and False == self.SQ_Sync_Frame_Capture_Bool_Internal():
                        if len(_light_class.light_interface.sq_frame_img_list) < _light_class.light_interface.sq_fr_arr[0]:
                            self.External_SQ_Fr_Disp()
                            self.Auto_Save_SQ_Frame()
                    self.ext_sq_fr_init = False
                continue
            else:
                self.n_save_image_size = int(np.multiply(self.n_payload_size, 3)) + 2048
                if img_buff is None:
                    img_buff = (c_ubyte * self.n_save_image_size)()
                #if self.pixel_format == 'Mono8':
                if True == self.Is_mono_data(self.pixel_format):

                    self.rgb_type = False
                    self.mono_type = True
                    # print(self.pixel_format)
                    if self.pixel_format == 'Mono8':
                        self.numArray = self.Mono_numpy(self.buf_cache, self.cam_width, self.cam_height)
                    elif self.pixel_format == 'Mono10' or self.pixel_format == 'Mono12':
                        self.numArray = self.Mono_numpy_2(self.buf_cache, self.cam_width, self.cam_height)
                    # self.numArray = self.Mono_numpy_3(self.buf_cache, self.cam_width, self.cam_height)
                    else:
                        self.numArray = self.Mono_numpy_3(self.buf_cache, self.cam_width, self.cam_height)

                    if _cam_class.flip_img_bool == True:
                        self.numArray = imutils.rotate(self.numArray, 180)

                elif True == self.Is_color_data(self.pixel_format):
                    self.rgb_type = True
                    self.mono_type = False
                    self.numArray = self.Color_numpy(self.buf_cache, self.cam_width, self.cam_height)

                    if _cam_class.flip_img_bool == True:
                        self.numArray = imutils.rotate(self.numArray, 180)
                else:
                    self.rgb_type = False
                    self.mono_type = False
                    self.numArray = None

                try:
                    if self.trigger_mode == True:
                        if True == self.SQ_Sync_Frame_Capture_Bool_External() and False == self.SQ_Sync_Frame_Capture_Bool_Internal():
                            if self.ext_sq_fr_init == False:
                                _light_class.light_interface.sq_frame_img_list *= 0
                                self.ext_sq_fr_init = True

                            elif self.ext_sq_fr_init == True:
                                pass
                            
                            ## len(list) empty = 0, sq_fr_arr[0] is the frame num: 1 - 10
                            _light_class.light_interface.sq_frame_img_list.append(self.numArray)
                            # print('Sq Frames: ',len(_light_class.light_interface.sq_frame_img_list))
                            if len(_light_class.light_interface.sq_frame_img_list) ==  _light_class.light_interface.sq_fr_arr[0]:
                                #print(len(_light_class.light_interface.sq_frame_img_list), _light_class.light_interface.sq_fr_arr[0])
                                self.External_SQ_Fr_Disp()
                                self.Auto_Save_SQ_Frame()

                                self.ext_sq_fr_init = False #UPDATE 18-8-2021

                            elif len(_light_class.light_interface.sq_frame_img_list) > _light_class.light_interface.sq_fr_arr[0]:
                                #print('Reset list')
                                self.ext_sq_fr_init = False #UPDATE 18-8-2021

                        if True == self.SQ_Sync_Frame_Capture_Bool_Internal() and False == self.SQ_Sync_Frame_Capture_Bool_External():
                            self.ext_sq_fr_init = False
                            #INTERNAL TRIGGER MODE + SQ STROBE
                            if _light_class.light_interface.sq_strobe_btn_click == True:
                                if self.trigger_mode == True:
                                    if len(_light_class.light_interface.sq_frame_img_list) < _light_class.light_interface.sq_fr_arr[0]:
                                        #len(list) empty = 0, sq_fr_arr[0] is the frame num: 1 - 10
                                        _light_class.light_interface.sq_frame_img_list.append(self.numArray)
                                        #print(len(_light_class.light_interface.sq_frame_img_list))
                                elif self.trigger_mode == False:
                                    _light_class.light_interface.STOP_SQ_strobe_frame_thread()

                except Exception:
                    # print('Work Thread Cam: ', e)                
                    self.ext_sq_fr_init = False
                    pass

                if _cam_class.capture_img_status.get() == 1:
                    if self.freeze_numArray is None:
                        self.freeze_numArray = self.numArray

                elif _cam_class.capture_img_status.get() == 0:
                    self.freeze_numArray = None

                if _cam_class.trigger_auto_save_bool.get() == 1:
                    self.Normal_Mode_Save(self.numArray, self.freeze_numArray, True)
                elif _cam_class.trigger_auto_save_bool.get() == 0:
                    self.Normal_Mode_Save(self.numArray, self.freeze_numArray, False)

                self.All_Mode_Cam_Disp()

                self.OpenCV_Record_Func(_cam_class.record_bool, self.cam_width, self.cam_height)

        pass

    def SQ_Sync_Frame_Capture_Bool_External(self):
        from main_GUI import main_GUI
        _light_class = main_GUI.class_light_conn
        _light_sq_param = None

        if _light_class.light_conn_status == True:
            if (_light_class.firmware_model_sel == 'SQ' or _light_class.firmware_model_sel == 'LC20'):
                _light_sq_param = main_GUI.class_light_conn.light_interface
                if (self.trigger_src == 'LINE1' and _light_sq_param.updating_bool == False):

                    return True

            return False
        else:
            return False

    def SQ_Sync_Frame_Capture_Bool_Internal(self):
        from main_GUI import main_GUI
        _light_class = main_GUI.class_light_conn
        _light_sq_param = None

        if _light_class.light_conn_status == True:
            if _light_class.firmware_model_sel == 'SQ':
                _light_sq_param = main_GUI.class_light_conn.light_interface

                if (_light_sq_param.channel_1_save[6] == 1 and _light_sq_param.channel_2_save[6] == 1 
                    and _light_sq_param.channel_3_save[6] == 1 and _light_sq_param.channel_4_save[6] == 1):      
                    if self.trigger_src == 'SOFTWARE' and _light_sq_param.updating_bool == False:

                        return True

            elif _light_class.firmware_model_sel == 'LC20':
                _light_sq_param = main_GUI.class_light_conn.light_interface

                if (_light_sq_param.channel_SQ_save[2] == 1):
                    if self.trigger_src == 'SOFTWARE' and _light_sq_param.updating_bool == False:

                        return True

            return False

        else:
            return False

    def OpenCV_Record_Init(self, frame_w, frame_h):
        if self.record_init == False:
            save_folder = create_save_folder()
            fourcc = cv2.VideoWriter_fourcc(*'XVID') #cv2.cv.CV_FOURCC(*'XVID')  # cv2.VideoWriter_fourcc() does not exist
            self.video_file = video_file_name(save_folder, 'Output Recording')
            self.video_writer = cv2.VideoWriter(self.video_file, fourcc, 10, (frame_w, frame_h))
            self.record_init = True
        elif self.record_init == True:
            pass

    def OpenCV_Record_Func(self, _bool, frame_w, frame_h):
        if _bool == True:
            self.OpenCV_Record_Init(frame_w, frame_h)
            if self.video_writer is not None:
                if self.freeze_numArray is None:
                    if len(self.numArray.shape) == 3:
                        frame_arr = cv2.cvtColor(self.numArray, cv2.COLOR_BGR2RGB)
                    else:
                        frame_arr = cv2.cvtColor(self.numArray, cv2.COLOR_GRAY2RGB) #self.numArray
                elif self.freeze_numArray is not None:
                    if len(self.freeze_numArray.shape) == 3:
                        frame_arr = cv2.cvtColor(self.freeze_numArray, cv2.COLOR_BGR2RGB)
                    else:
                        frame_arr = cv2.cvtColor(self.freeze_numArray, cv2.COLOR_GRAY2RGB) #self.freeze_numArray
                self.video_writer.write(frame_arr)
            pass

        elif _bool == False:
            if self.video_writer is not None:
                self.video_writer.release()
                tkinter.messagebox.showinfo('show info','Video Recording Completed!' + '\n' + str(self.video_file))
            self.record_init = False
            self.video_file = None
            self.video_writer = None


    def External_SQ_Fr_Disp(self):
        from main_GUI import main_GUI
        _light_class = main_GUI.class_light_conn
        _cam_class = main_GUI.class_cam_conn.active_gui
        try:
            _cam_class.clear_display_GUI_2()
        except Exception:
            pass

        try:
            self.SQ_frame_display(_light_class.light_interface.sq_frame_img_list)
        except Exception:
            # print('Exception External_SQ_Fr_Disp: ',  e)
            pass

        _cam_class.SQ_fr_popout_load_list(sq_frame_img_list = _light_class.light_interface.sq_frame_img_list.copy())
        _cam_class.SQ_fr_popout_disp_func(sq_frame_img_list = _light_class.light_interface.sq_frame_img_list.copy())

        try:
            _cam_class.SQ_fr_sel.bind('<<ComboboxSelected>>', 
                lambda event: _cam_class.SQ_fr_popout_disp_func(sq_frame_img_list = _light_class.light_interface.sq_frame_img_list))
        except (AttributeError, tk.TclError):
            pass

    def Normal_Mode_Save(self, arr_1, arr_2 = None, auto_save = False): #Normal Camera Mode Save
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        if arr_2 is None:
            img_arr = arr_1
        elif arr_2 is not None:
            img_arr = arr_2

        if auto_save == False:
            if self.rgb_type == False and self.mono_type == True:
                if True == self.b_save:
                    img_format = _cam_class.save_img_format_sel.get()
                    #print(img_format)
                    save_folder = create_save_folder()
                    if str(img_format) == '.pdf':
                        PDF_img_save(save_folder, img_arr, 'Image_Document', ch_split_bool = False)
                        #pass
                    else:
                        cv_img_save(save_folder, img_arr, 'Original', str(img_format))

                    self.b_save = False

                    if _cam_class.popout_status == True:
                        tkinter.messagebox.showinfo('show info','Save Image success!' + '\n' + str(save_folder), parent = _cam_class.cam_popout_toplvl)
                    else:
                        tkinter.messagebox.showinfo('show info','Save Image success!' + '\n' + str(save_folder))
                    # self.b_save = False

            elif self.rgb_type == True and self.mono_type == False:
                if True == self.b_save:
                    img_format = _cam_class.save_img_format_sel.get()
                    #print(img_format)
                    save_folder = create_save_folder()
                    if str(img_format) == '.pdf':
                        PDF_img_save(save_folder, img_arr, 'Image_Document', ch_split_bool = False)
                        #pass
                    else:
                        cv_img_save(save_folder, img_arr, 'Original', str(img_format))
                        cv_img_save(save_folder, img_arr[:, :, 0], 'Red_Channel', str(img_format))
                        cv_img_save(save_folder, img_arr[:, :, 1], 'Green_Channel', str(img_format))
                        cv_img_save(save_folder, img_arr[:, :, 2], 'Blue_Channel', str(img_format))

                    self.b_save = False
                    
                    if _cam_class.popout_status == True:
                        tkinter.messagebox.showinfo('show info','Save Image success!' + '\n' + str(save_folder), parent = _cam_class.cam_popout_toplvl)
                    else:
                        tkinter.messagebox.showinfo('show info','Save Image success!' + '\n' + str(save_folder))
                    # self.b_save = False
        
        elif auto_save == True:
            if self.rgb_type == False and self.mono_type == True:
                img_format = _cam_class.save_img_format_sel.get()
                #print(img_format)
                save_folder = create_save_folder()
                if str(img_format) == '.pdf':
                    PDF_img_save(save_folder, img_arr, 'Image_Document', ch_split_bool = False)
                    #pass
                else:
                    cv_img_save(save_folder, img_arr, 'Original', str(img_format))

            elif self.rgb_type == True and self.mono_type == False:
                img_format = _cam_class.save_img_format_sel.get()
                #print(img_format)
                save_folder = create_save_folder()
                if str(img_format) == '.pdf':
                    PDF_img_save(save_folder, img_arr, 'Image_Document', ch_split_bool = False)
                    #pass
                else:
                    cv_img_save(save_folder, img_arr, 'Original', str(img_format))
                    cv_img_save(save_folder, img_arr[:, :, 0], 'Red_Channel', str(img_format))
                    cv_img_save(save_folder, img_arr[:, :, 1], 'Green_Channel', str(img_format))
                    cv_img_save(save_folder, img_arr[:, :, 2], 'Blue_Channel', str(img_format))

    def All_Mode_Cam_Disp(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        if self.rgb_type == True and self.mono_type == False:
            if _cam_class.popout_status == False:
                if self.freeze_numArray is None:
                    self.RGB_display(self.numArray)
                    self.SQ_live_display(self.numArray)

                elif self.freeze_numArray is not None:
                    self.RGB_display(self.freeze_numArray)
                    self.SQ_live_display(self.freeze_numArray)

                self.disp_clear_ALL_status = False

            elif _cam_class.popout_status == True:
                if self.disp_clear_ALL_status == False:
                    self.Normal_Mode_display_clear()
                    self.SQ_Mode_display_clear()
                    self.disp_clear_ALL_status = True
                
                if self.freeze_numArray is None:
                    self.popout_display(self.numArray)
                elif self.freeze_numArray is not None:
                    self.popout_display(self.freeze_numArray)

        elif self.rgb_type == False and self.mono_type == True:
            if _cam_class.popout_status == False:
                if self.freeze_numArray is None:
                    self.Mono_display(self.numArray)
                    self.SQ_live_display(self.numArray)

                elif self.freeze_numArray is not None:
                    self.Mono_display(self.freeze_numArray)
                    self.SQ_live_display(self.freeze_numArray)

                self.disp_clear_ALL_status = False

            elif _cam_class.popout_status == True:
                if self.disp_clear_ALL_status == False:
                    self.Normal_Mode_display_clear()
                    self.SQ_Mode_display_clear()
                    self.disp_clear_ALL_status = True
                
                if self.freeze_numArray is None:
                    self.popout_display(self.numArray)
                elif self.freeze_numArray is not None:
                    self.popout_display(self.freeze_numArray)
    
    def RGB_display(self, img_arr):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        #Display for Normal Camera Mode
        if img_arr is not None:
            display_func(_cam_class.cam_display_rgb, img_arr, _cam_class.cam_display_width, _cam_class.cam_display_height)
            display_func(_cam_class.cam_display_R, img_arr[:,:,0], _cam_class.cam_display_width, _cam_class.cam_display_height)
            display_func(_cam_class.cam_display_G, img_arr[:,:,1], _cam_class.cam_display_width, _cam_class.cam_display_height)
            display_func(_cam_class.cam_display_B, img_arr[:,:,2], _cam_class.cam_display_width, _cam_class.cam_display_height)

    def Mono_display(self, img_arr):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        #Display for Normal Camera Mode
        if img_arr is not None:
            display_func(_cam_class.cam_display_rgb, img_arr, _cam_class.cam_display_width, _cam_class.cam_display_height)

    def Normal_Mode_display_clear(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        #Clear Display for Normal Camera Model
        clear_display_func(_cam_class.cam_display_rgb, _cam_class.cam_display_width, _cam_class.cam_display_height)
        clear_display_func(_cam_class.cam_display_R, _cam_class.cam_display_width, _cam_class.cam_display_height)
        clear_display_func(_cam_class.cam_display_G, _cam_class.cam_display_width, _cam_class.cam_display_height)
        clear_display_func(_cam_class.cam_display_B, _cam_class.cam_display_width, _cam_class.cam_display_height)


    def popout_display(self, img_arr):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        
        if self.rgb_type == False and self.mono_type == True:
            _cam_class.popout_var_mode = 'original'
            _cam_class.sel_R_btn['state'] = 'disable'
            _cam_class.sel_G_btn['state'] = 'disable'
            _cam_class.sel_B_btn['state'] = 'disable'

        elif self.rgb_type == True and self.mono_type == False:
            _cam_class.sel_R_btn['state'] = 'normal'
            _cam_class.sel_G_btn['state'] = 'normal'
            _cam_class.sel_B_btn['state'] = 'normal'

        if _cam_class.popout_var_mode == 'original':
            _cam_class.popout_cam_disp_func(img_arr)
        elif _cam_class.popout_var_mode == 'red':
            _cam_class.popout_cam_disp_func(img_arr[:,:,0])
        elif _cam_class.popout_var_mode == 'green':
            _cam_class.popout_cam_disp_func(img_arr[:,:,1])
        elif _cam_class.popout_var_mode == 'blue':
            _cam_class.popout_cam_disp_func(img_arr[:,:,2])

    def SQ_live_display(self, img_arr):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        #Display for SQ Camera Mode
        if img_arr is not None:
            display_func(_cam_class.cam_disp_current_frame, img_arr, _cam_class.cam_display_width, _cam_class.cam_display_height)

    def SQ_Mode_display_clear(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        clear_display_func(_cam_class.cam_disp_current_frame, _cam_class.cam_display_width, _cam_class.cam_display_height)

    def SQ_frame_display(self, img_data, tk_disp_id = 0):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        tk_sq_disp_list = _cam_class.tk_sq_disp_list
        # print(tk_sq_disp_list)
        self.sq_frame_save_list *=0

        if type(img_data) == list:
            if len(img_data) > 0:
                for i, img_arr in enumerate(img_data):
                    try:
                        display_func(tk_sq_disp_list[i], img_arr, _cam_class.cam_display_width, _cam_class.cam_display_height)
                        self.sq_frame_save_list.append(img_arr)
                    except Exception:
                        # print('SQ_frame_display: ', e)
                        pass

                if self.rgb_type == True and self.mono_type == False:
                    self.RGB_display(img_data[-1])
                    self.SQ_live_display(img_data[-1])

                elif self.rgb_type == False and self.mono_type == True:
                    self.Mono_display(img_data[-1])
                    self.SQ_live_display(img_data[-1])

        elif (isinstance(self.loaded_img, np.ndarray)) == True:
            try:
                display_func(tk_sq_disp_list[tk_disp_id], img_data, _cam_class.cam_display_width, _cam_class.cam_display_height)
                self.sq_frame_save_list.append(img_data)
            except Exception:
                # print('SQ_frame_display: ', e)
                pass

            if self.rgb_type == True and self.mono_type == False:
                    self.RGB_display(img_data)
                    self.SQ_live_display(img_data)

            elif self.rgb_type == False and self.mono_type == True:
                self.Mono_display(img_data)
                self.SQ_live_display(img_data)

    def Save_SQ_Frame(self):
        if len(self.sq_frame_save_list) != 0:
            from main_GUI import main_GUI
            _cam_class = main_GUI.class_cam_conn.active_gui

            save_folder = create_save_folder()
            frame_index = 1
            img_format = _cam_class.save_img_format_sel.get()
            pdf_img_list = []

            for images in self.sq_frame_save_list:
                if str(img_format) == '.pdf':
                    pdf_img_list.append(np_to_PIL(images))
                    pass
                else:
                    cv_img_save(save_folder, images, 'Frame ' +  str(frame_index), str(img_format))
                # pdf_img_list.append(np_to_PIL(images))
                frame_index = frame_index + 1
            
            if str(img_format) == '.pdf':
                PDF_img_list_save(folder = save_folder, pdf_img_list = pdf_img_list, pdf_name = ('Frame 1 - ' + str(frame_index - 1) + ' Documentation'))

            tkinter.messagebox.showinfo('Info', 'All loaded SQ Frames Were Saved In' + '\n' + str(save_folder))
        else:
            tkinter.messagebox.showinfo('Alert', 'Please Ensure That All SQ Frames Were Loaded To Save')

    def Auto_Save_SQ_Frame(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        if _cam_class.SQ_auto_save_bool.get() == 1:
            save_folder = create_save_folder()
            frame_index = 1
            img_format = _cam_class.save_img_format_sel.get()
            pdf_img_list = []

            for images in self.sq_frame_save_list:
                if str(img_format) == '.pdf':
                    pdf_img_list.append(np_to_PIL(images))
                    pass
                else:
                    cv_img_save(save_folder, images, 'Frame ' +  str(frame_index), str(img_format))
                # pdf_img_list.append(np_to_PIL(images))
                frame_index = frame_index + 1

            if str(img_format) == '.pdf':
                PDF_img_list_save(folder = save_folder, pdf_img_list = pdf_img_list, pdf_name = ('Frame 1 - ' + str(frame_index - 1) + ' Documentation'))

        elif _cam_class.SQ_auto_save_bool.get() == 0:
            pass

    def Is_mono_data(self, pixel_format):
        # if "Mono8" == pixel_format or "Mono10" == pixel_format \
        #     or "Mono10Packed" == pixel_format or "Mono12" == pixel_format \
        #     or "Mono12Packed" == pixel_format or "Mono14" == pixel_format:
        #     return True
        # else:
        #     return False
        for ref in self.mono_format_list:
            if ref == pixel_format:
                return True

        return False

    def Is_color_data(self,pixel_format):
        for ref in self.color_format_list:
            if ref == pixel_format:
                return True

        return False

    def Mono_numpy(self,data,nWidth,nHeight):
        # data_ = np.frombuffer(data, count=int(nWidth * nHeight), dtype=np.uint8, offset=0)
        data_ = np.frombuffer(data, count=-1, dtype=np.uint8, offset=0)
        data_mono_arr = data_.reshape(nHeight, nWidth)
        #numArray = np.zeros([nHeight, nWidth, 1],"uint8") 
        #numArray[:, :, 0] = data_mono_arr
        numArray = np.zeros([nHeight, nWidth],"uint8") 
        numArray[:, :] = data_mono_arr
        return numArray

    def Mono_numpy_2(self,data,nWidth,nHeight):
        data_ = np.frombuffer(data, count=-1, dtype=np.uint16, offset=0)
        # print(len(data_))
        data_mono_arr = data_.reshape(nHeight, nWidth)
        # print(data_mono_arr.shape)
        numArray = np.zeros([nHeight, nWidth],"uint16") 
        numArray[:, :] = data_mono_arr
        return numArray

    def Color_numpy(self,data,nWidth,nHeight):
        data_ = np.frombuffer(data, count=int(nWidth*nHeight*3), dtype=np.uint8, offset=0)
        # print(data_)
        data_r = data_[0:nWidth*nHeight*3:3]
        data_g = data_[1:nWidth*nHeight*3:3]
        data_b = data_[2:nWidth*nHeight*3:3]

        data_r_arr = data_r.reshape(nHeight, nWidth)
        data_g_arr = data_g.reshape(nHeight, nWidth)
        data_b_arr = data_b.reshape(nHeight, nWidth)
        numArray = np.zeros([nHeight, nWidth, 3],"uint8")

        numArray[:, :, 0] = data_r_arr
        numArray[:, :, 1] = data_g_arr
        numArray[:, :, 2] = data_b_arr
        return numArray

    def Auto_Exposure(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        self.b_open_device = self.Check_device()

        if _cam_class.auto_exposure_toggle == False and self.b_open_device == True:
            # ret = self.obj_cam.MV_CC_SetEnumValue("ExposureAuto", 2) #value of 2 is to activate Exposure Auto.
            ret = self.crevis_pylib.ST_SetEnumReg('ExposureAuto'.encode('utf-8'), 'Continuous'.encode('utf-8'))
            if ret == 0:
                _cam_class.btn_auto_exposure['image'] = _cam_class.toggle_ON_button_img
                _cam_class.entry_exposure['state'] = 'disabled'
                _cam_class.auto_exposure_toggle = True

                pass
            elif ret != 0:
                _cam_class.auto_exposure_toggle = False
                pass

        elif _cam_class.auto_exposure_toggle == True and self.b_open_device == True:
            # ret = self.obj_cam.MV_CC_SetEnumValue("ExposureAuto", 0)
            ret = self.crevis_pylib.ST_SetEnumReg('ExposureAuto'.encode('utf-8'), 'Off'.encode('utf-8'))
            if ret == 0:
                #print('Auto Exposure OFF')                
                _cam_class.btn_auto_exposure['image'] = _cam_class.toggle_OFF_button_img
                _cam_class.entry_exposure['state'] = 'normal'
                _cam_class.auto_exposure_toggle = False
                pass
            elif ret != 0:
                _cam_class.auto_exposure_toggle = True
                pass
        else:
            pass

    def Auto_Gain(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        self.b_open_device = self.Check_device()

        if _cam_class.auto_gain_toggle == False and self.b_open_device == True:
            ret = self.crevis_pylib.ST_SetEnumReg('GainAuto'.encode('utf-8'), 'Continuous'.encode('utf-8'))
            if ret == 0:
                #print('Auto Gain ON')
                
                _cam_class.btn_auto_gain['image'] = _cam_class.toggle_ON_button_img
                _cam_class.entry_gain['state'] = 'disabled'
                _cam_class.auto_gain_toggle = True
                pass
            elif ret != 0:
                _cam_class.auto_gain_toggle = False
                pass

        elif _cam_class.auto_gain_toggle == True and self.b_open_device == True:
            ret = self.crevis_pylib.ST_SetEnumReg('GainAuto'.encode('utf-8'), 'Off'.encode('utf-8'))
            if ret == 0:
                #print('Auto Gain OFF')
                
                _cam_class.btn_auto_gain['image'] = _cam_class.toggle_OFF_button_img
                _cam_class.entry_gain['state'] = 'normal'
                _cam_class.auto_gain_toggle = False
                pass
            elif ret != 0:
                _cam_class.auto_gain_toggle = True
                pass
        else:
            pass

    def Auto_White(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        self.b_open_device = self.Check_device()

        if _cam_class.auto_white_toggle == False and self.b_open_device == True:
            ret = self.crevis_pylib.ST_SetEnumReg('BalanceWhiteAuto'.encode('utf-8'), 'On'.encode('utf-8'))
            print('Balance White Auto ON: ', ret)
            if ret == 0:
                #print('Auto White ON')
                _cam_class.auto_white_toggle = True
                _cam_class.white_balance_btn_state()
                pass
            elif ret != 0:
                _cam_class.auto_white_toggle = False
                pass

        elif _cam_class.auto_white_toggle == True and self.b_open_device == True:
            ret = self.crevis_pylib.ST_SetEnumReg('BalanceWhiteAuto'.encode('utf-8'), 'Off'.encode('utf-8'))
            if ret == 0:
                #print('Auto White OFF')
                _cam_class.auto_white_toggle = False
                _cam_class.white_balance_btn_state()
                pass
            elif ret != 0:
                _cam_class.auto_white_toggle = True
                pass
        else:
            pass


    def Enable_Framerate(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        self.b_open_device = self.Check_device()

        if _cam_class.framerate_toggle == False and self.b_open_device == True:
            ret = self.crevis_pylib.ST_SetEnumReg('AcquisitionFrameRateEnable'.encode('utf-8'), 'On'.encode('utf-8'))
            print('Enable Framerate', ret)
            if ret == 0:
                #print('Framerate Enabled')
                
                _cam_class.btn_enable_framerate['image'] = _cam_class.toggle_ON_button_img
                _cam_class.entry_framerate['state'] = 'normal'
                _cam_class.framerate_toggle = True

                pass
            elif ret != 0:
                _cam_class.framerate_toggle = False
                pass

        elif _cam_class.framerate_toggle == True and self.b_open_device == True:
            ret = self.crevis_pylib.ST_SetEnumReg('AcquisitionFrameRateEnable'.encode('utf-8'), 'Off'.encode('utf-8'))
            print('Disable Framerate', ret)
            if ret == 0:
                #print('Framerate Disabled')
                
                _cam_class.btn_enable_framerate['image'] = _cam_class.toggle_OFF_button_img
                _cam_class.entry_framerate['state'] = 'disabled'
                _cam_class.framerate_toggle = False
                pass
            elif ret != 0:
                _cam_class.framerate_toggle = True
                pass
        else:
            pass

    def Enable_Blacklevel(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        self.b_open_device = self.Check_device()

        if _cam_class.black_lvl_toggle == False and self.b_open_device == True:
            _cam_class.black_lvl_toggle = True
            _cam_class.black_lvl_btn_state()

        elif _cam_class.black_lvl_toggle == True and self.b_open_device == True:
            _cam_class.black_lvl_toggle = False
            _cam_class.black_lvl_btn_state()

    def Get_parameter_exposure(self):
        self.b_open_device = self.Check_device()

        if True == self.b_open_device:
            self.crevis_pylib.ST_SetCmdReg('ExposureUpdateFeature'.encode('utf-8'))
            pVal = c_double()

            ret = self.crevis_pylib.ST_GetFloatReg('ExposureTime'.encode('utf-8'), pVal)
            # print('Exposure Time: ', pVal.value)
            if ret != 0:
                self.exposure_time = 0
            elif ret == 0:
                self.exposure_time = pVal.value

            # self.crevis_pylib.ST_SetCmdReg('ExposureUpdateFeature'.encode('utf-8'))

    def Get_parameter_framerate(self):
        self.b_open_device = self.Check_device()

        if True == self.b_open_device:
            pVal = c_double()

            ret = self.crevis_pylib.ST_GetFloatReg('AcquisitionFrameRate'.encode('utf-8'), pVal)
            # print('Framerate: ', pVal.value)
            if ret != 0:
                self.frame_rate = 7.313889
            elif ret == 0:
                self.frame_rate = pVal.value
    
    def Get_parameter_gain(self):
        self.b_open_device = self.Check_device()

        if True == self.b_open_device:
            self.crevis_pylib.ST_SetCmdReg('GainUpdateFeature'.encode('utf-8'))
            pVal = c_int32()
            ret = self.crevis_pylib.ST_GetIntReg('GainRaw'.encode('utf-8'), pVal)
            # print('Gain: ', pVal.value)
            if ret != 0:
                self.gain = 14
            elif ret == 0:
                self.gain = pVal.value

    def Get_parameter_black_lvl(self):
        self.b_open_device = self.Check_device()

        if True == self.b_open_device:
            pVal = c_uint32()
            ret = self.crevis_pylib.ST_GetIntReg('BlackLevelRaw'.encode('utf-8'), pVal)

            if ret != 0:
                self.black_lvl = 0
            elif ret == 0:
                self.black_lvl = pVal.value


    def Set_parameter_exposure(self, exposureTime):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        self.b_open_device = self.Check_device()
        if True == self.b_open_device:
            pVal = c_double(float(exposureTime))
            # print('Set Exposure: ', pVal.value)
            ret = self.crevis_pylib.ST_SetFloatReg('ExposureTime'.encode('utf-8'), pVal)
            if ret != 0:
                _cam_class.revert_val_exposure = True
                pass

    def Set_parameter_framerate(self, frameRate):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui  
        self.b_open_device = self.Check_device()

        if True == self.b_open_device:
            pVal = c_double(float(frameRate))
            print('Set Framerate: ', pVal.value)
            ret = self.crevis_pylib.ST_SetFloatReg('AcquisitionFrameRate'.encode('utf-8'), pVal)
            print('Set Framerate status: ', ret)
            if ret != 0:
                _cam_class.revert_val_framerate = True
                pass

    def Set_parameter_gain(self, gain):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        self.b_open_device = self.Check_device()
        if True == self.b_open_device:
            pVal = c_int32(int(gain))
            # print('Set Gain: ', pVal.value)
            ret = self.crevis_pylib.ST_SetIntReg('GainRaw'.encode('utf-8'), pVal)
            if ret != 0:
                _cam_class.revert_val_gain = True
                pass

    def Set_parameter_black_lvl(self, val):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        self.b_open_device = self.Check_device()
        if True == self.b_open_device:
            pVal = c_int32(int(val))
            # print('Set Gain: ', pVal.value)
            ret = self.crevis_pylib.ST_SetIntReg('BlackLevelRaw'.encode('utf-8'), pVal)
            if ret != 0:
                _cam_class.revert_val_black_lvl = True