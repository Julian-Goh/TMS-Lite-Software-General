import os
from os import path
import shutil
import sys
import copy
# import io

import queue
from queue import Queue
import time
import psutil

import re

from PIL import ImageTk, Image
import numpy as np
import imutils

from datetime import datetime

from imageio import imread
import cv2

import tkinter as tk

from Tk_MsgBox.custom_msgbox import Ask_Msgbox, Info_Msgbox, Error_Msgbox, Warning_Msgbox

from tkinter import ttk

import inspect
import ctypes
from ctypes import *

import threading
import msvcrt

code_PATH = os.getcwd()

sys.path.append(code_PATH + '\\MVS-Python\\MvImport')
from MvCameraControl_class import *

def time_convert(sec):
    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60
    return "{:02d}:{:02d}:{:02d}".format(int(hours),int(mins), int(round(sec)) )

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

def create_save_folder(folder_dir = os.getcwd() + r'\TMS_Saved_Images', duplicate = False):
    if duplicate == True:
        if path.exists(folder_dir):
            index = 0
            loop = True
            while loop == True:
                new_dir = folder_dir + '({})'.format(index)
                if path.exists(new_dir):
                    index = index + 1
                else:
                    os.mkdir(new_dir)
                    loop = False

            return new_dir

        else:
            os.mkdir(folder_dir)
            return folder_dir
    else:
        if path.exists(folder_dir):
            #print ('File already exists')
            pass
        else:
            os.mkdir(folder_dir)
            #print ('File created')
        return folder_dir

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

def text_file_name(folder, file_name):
    index = 0
    loop = True
    while loop == True:
        file_path = folder + '\\'+ file_name + '_' + str(index) + '.txt'
        if (path.exists(file_path)) == True:
            index = index + 1
        elif (path.exists(file_path)) == False:
            loop = False

    return file_path

def cv_img_save(folder, img_arr, img_name, img_format, kw_str = '', overwrite = False):
    index = 0

    if overwrite == False:
        if (isinstance(kw_str, str) == True) and len(kw_str) > 0:
            new_img_name = re.sub('(\\'+ kw_str + '\\)' + '(--id)(\\d)' + '$', '', img_name)
            # new_img_name = re.sub('\\s{2,}', ' ', new_img_name) # Replace all double spaces with single spaces
            new_img_name = re.sub('\\s$', '', new_img_name) #Remove 1 space from the image name if any, because we will add 1 space in the following loop
            loop = True
            while loop == True:
                img_path = folder + '\\'+ new_img_name + '-' + kw_str + '--id{}'.format(index) + img_format
                if (path.exists(img_path)) == True:
                    index = index + 1
                elif (path.exists(img_path)) == False:
                    loop = False

        else:
            loop = True
            while loop == True:
                img_path = folder + '\\'+ img_name + '--id{}'.format(index) + img_format
                if (path.exists(img_path)) == True:
                    index = index + 1
                elif (path.exists(img_path)) == False:
                    loop = False

    else:
        img_path = folder + '\\'+ img_name + img_format

    # print(img_path)
    if len(img_arr.shape) == 3:
        img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
    cv2.imwrite(img_path, img_arr)

    return img_path, index

def PDF_img_save(folder, img_arr, pdf_name, ch_split_bool = True, kw_str = '', overwrite = False):
    index = 0
    if overwrite == False:
        if (isinstance(kw_str, str) == True) and len(kw_str) > 0:
            new_pdf_name = re.sub('(\\'+ kw_str + '\\)' + '--(id)(\\d)' + '$', '', pdf_name)
            new_pdf_name = re.sub('\\s$', '', new_pdf_name) #Remove 1 space from the image name if any, because we will add 1 space in the following loop
            loop = True
            while loop == True:
                pdf_path = folder + '\\'+ new_pdf_name + '-' + kw_str + '--id{}'.format(index) + ".PDF"
                if (path.exists(pdf_path)) == True:
                    index = index + 1
                elif (path.exists(pdf_path)) == False:
                    loop = False

        else:
            loop = True
            while loop == True:
                pdf_path = folder + '\\'+ pdf_name + '--id{}'.format(index) + ".PDF"
                if (path.exists(pdf_path)) == True:
                    index = index + 1
                elif (path.exists(pdf_path)) == False:
                    loop = False
    
    else:
        pdf_path = folder + '\\'+ pdf_name + ".PDF"

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

    return pdf_path, index

def PDF_img_list_save(folder, pdf_img_list, pdf_name):
    index = 0
    loop = True
    while loop == True:
        pdf_path = folder + '\\'+ pdf_name + '--id{}'.format(index) + ".PDF"
        if (path.exists(pdf_path)) == True:
            index = index + 1
        elif (path.exists(pdf_path)) == False:
            loop = False

    pdf_img_list[0].save(pdf_path, save_all=True, append_images= pdf_img_list[1:])

def np_to_PIL(img_arr):
    img_PIL = Image.fromarray(img_arr)

    return img_PIL

def display_func(display, ref_img, w, h, resize_status = True, interpolation = cv2.INTER_LINEAR):
    if resize_status == True:
        #cv2.INTER_NEAREST, #cv2.INTER_LINEAR
        #img_resize = imutils.resize(ref_img, height = h)
        img_resize = cv2.resize(ref_img,(w,h), interpolation = interpolation)
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

def clear_display_func(*canvas_widgets):
    for widget in canvas_widgets:
        widget.delete('all')

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

#MV_CC_SetEnumValue("BalanceWhiteAuto", 1) or MV_CC_GetEnumValue("BalanceWhiteAuto", ref enumParam)
#MV_CC_SetBalanceRatioRed((uint)brRed.Value) #MV_CC_SetBalanceRatioGreen((uint)brGreen.Value) or MV_CC_SetBalanceRatioBlue((uint)brBlue.Value)

#MV_CC_SetIntValueEx("Brightness", (int)brightness.Value) or MV_CC_GetIntValueEx("Brightness", ref intParam)  #Brightness is enabled when either Exposure or Gain in Auto Mode (0-255)

#MV_CC_SetBoolValue("BlackLevelEnable", c_bool(True)) or MV_CC_GetBoolValue
#MV_CC_SetIntValueEx("BlackLevel", (int)blackLevel.Value) or MV_CC_GetIntValueEx (0 - 4095)

#MV_CC_SetBoolValue("SharpnessEnable", c_bool(True)) or MV_CC_GetBoolValue
#MV_CC_GetIntValueEx("Sharpness", ref intParam) or MV_CC_SetIntValueEx

class Hikvision_Operation():
    def __init__(self,obj_cam, st_device_ID = None,b_open_device=False,b_start_grabbing = False,h_thread_handle=None,\
                b_thread_closed=False,st_frame_info=None,buf_cache=None,b_exit=False,buf_save_image=None,\
                n_save_image_size=0,n_payload_size=0,frame_rate=1,exposure_time=28,gain=0, gain_mode = 0, exposure_mode = 0, framerate_mode = 0):

        self.obj_cam = obj_cam
        self.st_device_ID = st_device_ID

        self.b_open_device = b_open_device
        self.b_start_grabbing = b_start_grabbing 
        self.b_thread_closed = b_thread_closed
        self.st_frame_info = st_frame_info
        self.buf_cache = buf_cache
        self.b_exit = b_exit
        
        self.n_payload_size = n_payload_size
        self.buf_save_image = buf_save_image
        self.h_thread_handle = h_thread_handle
        self.n_save_image_size = n_save_image_size

        self.b_save = False
        self.custom_b_save = False
        self.__custom_save_folder = None
        self.__custom_save_name = None
        self.__custom_save_overwrite = False

        self.img_save_flag = False ## Used to trigger tkinter msgbox in Camera GUI
        self.img_save_folder = None ## Used for display in tkinter msgbox in Camera GUI
        
        self.frame_rate = frame_rate #min: 1, max: 1000
        self.exposure_time = exposure_time #min: 28, max: 1 000 000
        self.gain = gain #min: 0, max: 15.0026

        self.brightness = 255 #min: 0, max: 255
        self.red_ratio = 1 #min: 1, max: 4095
        self.green_ratio = 1 #min: 1, max: 4095
        self.blue_ratio = 1 #min: 1, max: 4095
        self.black_lvl = 0 #min: 0 , max: 4095
        self.sharpness = 0 #min: 0 , max: 100

        self.exposure_mode = exposure_mode
        self.gain_mode = gain_mode
        self.framerate_mode = framerate_mode
        self.white_mode = 0

        self.numArray = None
        self.freeze_numArray = None

        self.disp_clear_ALL_status = False

        self.rgb_type = False
        self.mono_type = False

        self.trigger_mode = False
        
        self.bool_mode_switch = False #UPDATED 18-8-2021

        self.trigger_src = 0 #values: 0, 1, 2, 3, 4, 7

        self.start_grabbing_event = threading.Event()
        self.start_grabbing_event.set()
        
        self.record_init = False
        self.video_file = None
        self.video_writer = None

        self.sq_frame_save_list = []
        self.__sq_save_next_id_index = None
        #EXTERNAL SQ STROBE FRAME PARAMETER(S)
        self.ext_sq_fr_init = False

        self.cam_display_thread = None
        self.cam_display_event = threading.Event()
        self.cam_display_event.set()
        self.cam_display_bool = False

        self.video_write_thread = None
        self.video_record_thread = None
        self.video_record_event = threading.Event()
        self.video_record_event.set()
        self.frame_queue = None
        self.__record_force_stop = False
        self.__video_empty_bool = True
        
        self.record_complete_flag = False #used to flag for Msgbox if video completed successfully.
        self.record_warning_flag = False #used to flag for Msgbox if warning occur in video recording.

        self.elapse_time = 0
        self.start_record_time = None
        self.pause_record_duration = 0


    def To_hex_str(self,num):
        chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
        hexStr = ""
        if num < 0:
            num = num + 2**32
        while num >= 16:
            digit = num % 16
            hexStr = chaDic.get(digit, str(digit)) + hexStr
            num //= 16
        hexStr = chaDic.get(num, str(num)) + hexStr   
        return hexStr

    def Open_device(self, st_device_ID = None):
        self.st_device_ID = st_device_ID
        
        if False == self.b_open_device:
            # ch:选择设备并创建句柄 | en:Select device and create handle
            ret = self.obj_cam.MV_CC_CreateHandle(self.st_device_ID)
            if ret != 0:
                return ret

            ret = self.obj_cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
            if ret != 0:
                Error_Msgbox(message = 'Open device fail!\nError('+ self.To_hex_str(ret)+')', title = 'Open Device Error', message_anchor = 'w')
                return ret
            print ("open device successfully!")
            self.b_open_device = True
            self.b_thread_closed = False

            # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
            if self.st_device_ID.nTLayerType == MV_GIGE_DEVICE:
                nPacketSize = self.obj_cam.MV_CC_GetOptimalPacketSize()
                if int(nPacketSize) > 0:
                    ret = self.obj_cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
                    if ret != 0:
                        print ("warning: set packet size fail! ret[0x%x]" % ret)
                else:
                    print ("warning: set packet size fail! ret[0x%x]" % nPacketSize)

            stParam =  MVCC_INTVALUE()

            memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))
            
            ret = self.obj_cam.MV_CC_GetIntValue("PayloadSize", stParam)
            if ret != 0:
                print ("get payload size fail! ret[0x%x]" % ret)
            self.n_payload_size = stParam.nCurValue
            #print(self.n_payload_size)
            self.n_payload_size_SQ = self.n_payload_size

            if None == self.buf_cache:
                self.buf_cache = (c_ubyte * self.n_payload_size)()
                #print(self.buf_cache)
                self.buf_cache_SQ = self.buf_cache
            # ch:设置触发模式为off | en:Set trigger mode as off
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
            #print(MV_TRIGGER_MODE_OFF)
            if ret != 0:
                print ("set trigger mode fail! ret[0x%x]" % ret)

            self.Get_Pixel_Format()

            self.Init_Framerate_Mode()
            self.Get_parameter_framerate()

            self.Init_Exposure_Mode()

            self.Init_Gain_Mode()

            self.Init_Black_Level_Mode()

            self.Init_Sharpness_Mode()

            stFloatParam_FrameRate =  MVCC_FLOATVALUE()
            memset(byref(stFloatParam_FrameRate), 0, sizeof(MVCC_FLOATVALUE))
            ret = self.obj_cam.MV_CC_GetFloatValue("AcquisitionFrameRate", stFloatParam_FrameRate)
            if ret != 0:
                self.frame_rate = 1
            elif ret == 0:
                self.frame_rate = stFloatParam_FrameRate.fCurValue

            return 0

    def Set_Pixel_Format(self, hex_val):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        self.Normal_Mode_display_clear()
        self.SQ_Mode_display_clear()
        setpixel_ret = self.obj_cam.MV_CC_SetEnumValue("PixelFormat", hex_val)
        #print(setpixel_ret)
        if setpixel_ret == 0:
            if self.st_device_ID.nTLayerType == MV_GIGE_DEVICE:
                nPacketSize = self.obj_cam.MV_CC_GetOptimalPacketSize()
                if int(nPacketSize) > 0:
                    ret = self.obj_cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
                    if ret != 0:
                        print ("warning: set packet size fail! ret[0x%x]" % ret)
                else:
                    print ("warning: set packet size fail! ret[0x%x]" % nPacketSize)

            stParam =  MVCC_INTVALUE()

            memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))
            
            ret = self.obj_cam.MV_CC_GetIntValue("PayloadSize", stParam)
            if ret != 0:
                print ("get payload size fail! ret[0x%x]" % ret)
            self.n_payload_size = stParam.nCurValue

            self.n_payload_size_SQ = self.n_payload_size

            self.buf_cache = (c_ubyte * self.n_payload_size)()
            self.buf_cache_SQ = self.buf_cache

            pixel_str_id = self.Pixel_Format_Str_ID(hex_val)
            # print('Set Pixel; pixel_str_id: ', pixel_str_id)
            if True == self.Pixel_Format_Mono(pixel_str_id):
                _cam_class.entry_red_ratio['state'] = 'disable'
                _cam_class.entry_green_ratio['state'] = 'disable'
                _cam_class.entry_blue_ratio['state'] = 'disable'
                _cam_class.btn_auto_white['image'] = _cam_class.toggle_OFF_button_img
                _cam_class.btn_auto_white['state'] = 'disable'
                _cam_class.auto_white_toggle = False

            elif True == self.Pixel_Format_Color(pixel_str_id):
                _cam_class.btn_auto_white['state'] = 'normal'
                self.Init_Balance_White_Mode()
                _cam_class.white_balance_btn_state()
                if _cam_class.auto_white_handle is not None:
                    _cam_class.stop_auto_white()
                    _cam_class.get_parameter_white()
                elif _cam_class.auto_white_handle is None:
                    _cam_class.get_parameter_white()
                pass
        else:
            self.Get_Pixel_Format()
            pixel_str_id = self.Pixel_Format_Str_ID(hex_val)
            Error_Msgbox(message = 'Current Camera Does Not Support Pixel Format: ' + pixel_str_id, title = 'Pixel Format Error', message_anchor = 'w')
            pass

        return setpixel_ret


    def Get_Pixel_Format(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        st_pixel_format = MVCC_ENUMVALUE()
        memset(byref(st_pixel_format), 0, sizeof(MVCC_ENUMVALUE))
        ret = self.obj_cam.MV_CC_GetEnumValue("PixelFormat", st_pixel_format)

        pixel_format_int = st_pixel_format.nCurValue
        _cam_class.get_pixel_format(pixel_format_int) #Update the HikVision Camera GUI
        # print(int2Hex(pixel_format_int))

        pixel_str_id = self.Pixel_Format_Str_ID(pixel_format_int)
        # print(pixel_str_id)

        if True == self.Pixel_Format_Mono(pixel_str_id):
            # print('Mono Detected')
            _cam_class.entry_red_ratio['state'] = 'disable'
            _cam_class.entry_green_ratio['state'] = 'disable'
            _cam_class.entry_blue_ratio['state'] = 'disable'
            _cam_class.btn_auto_white['image'] = _cam_class.toggle_OFF_button_img
            _cam_class.btn_auto_white['state'] = 'disable'
            # print('Mono Detected')
            _cam_class.auto_white_toggle = False

        elif True == self.Pixel_Format_Color(pixel_str_id):
            _cam_class.btn_auto_white['state'] = 'normal'
            # print('Color Detected')
            self.Init_Balance_White_Mode()
            _cam_class.white_balance_btn_state()
            if _cam_class.auto_white_handle is not None:
                _cam_class.stop_auto_white()
                _cam_class.get_parameter_white()
            elif _cam_class.auto_white_handle is None:
                _cam_class.get_parameter_white()
            pass

    def Pixel_Format_Str_ID(self, hex_int):
        if hex_int == 0x01080001:
            return 'Mono 8'
        elif hex_int == 0x01100003:
            return 'Mono 10'
        elif hex_int == 0x010C0004:
            return 'Mono 10 Packed'
        elif hex_int == 0x01100005:
            return 'Mono 12'
        elif hex_int == 0x010C0006:
            return 'Mono 12 Packed'
        elif hex_int == 0x02180014:
            return 'RGB 8'
        elif hex_int == 0x02180015:
            return 'BGR 8'
        elif hex_int == 0x02100032:
            return 'YUV 422 (YUYV) Packed'
        elif hex_int == 0x0210001F:
            return 'YUV 422 Packed'
        elif hex_int == 0x01080009:
            return 'Bayer RG 8'
        elif hex_int == 0x0110000d:
            return 'Bayer RG 10'
        elif hex_int == 0x010C0027:
            return 'Bayer RG 10 Packed'
        elif hex_int == 0x01100011:
            return 'Bayer RG 12'
        elif hex_int == 0x010C002B:
            return 'Bayer RG 12 Packed'

        else:
            return None

    def Pixel_Format_Mono(self, str_id):
        if str_id == 'Mono 8' or str_id == 'Mono 10' or str_id == 'Mono 10 Packed' or str_id == 'Mono 12' or str_id == 'Mono 12 Packed':
            return True

        else:
            return False

    def Pixel_Format_Color(self, str_id):
        if str_id == 'RGB 8' or str_id == 'BGR 10' or str_id == 'YUV 422 (YUYV) Packed' or str_id == 'YUV 422 Packed' or str_id == 'Bayer RG 8'\
        or str_id == 'Bayer RG 10' or str_id == 'Bayer RG 10 Packed' or str_id == 'Bayer RG 12' or str_id == 'Bayer RG 12 Packed':
            return True

        else:
            return False

    def Init_Framerate_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        stBool = c_bool(False)
        ret =self.obj_cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", byref(stBool))
        if ret != 0:
            print ("get acquisition frame rate enable fail! ret[0x%x]" % ret)

        if str(stBool) == 'c_bool(True)':
            _cam_class.framerate_toggle = True
        elif str(stBool) == 'c_bool(False)':
            _cam_class.framerate_toggle = False

    def Init_Exposure_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        st_exposure_mode = MVCC_ENUMVALUE()
        memset(byref(st_exposure_mode), 0, sizeof(MVCC_ENUMVALUE))
        ret = self.obj_cam.MV_CC_GetEnumValue("ExposureAuto", st_exposure_mode)

        self.exposure_mode = st_exposure_mode.nCurValue
        if self.exposure_mode == 2: #2 is continuous mode
            _cam_class.auto_exposure_toggle = True
        #elif self.exposure_mode == 1: #1 is once mode, #0 is off mode
        else:
            _cam_class.auto_exposure_toggle = False

    def Init_Gain_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        st_gain_mode = MVCC_ENUMVALUE()
        memset(byref(st_gain_mode), 0, sizeof(MVCC_ENUMVALUE))
        ret = self.obj_cam.MV_CC_GetEnumValue("GainAuto", st_gain_mode)
        self.gain_mode = st_gain_mode.nCurValue
        if self.gain_mode == 2: #2 is continuous mode
            _cam_class.auto_gain_toggle = True
        #elif self.gain_mode == 1: #1 is once mode, #0 is off mode
        else:
            _cam_class.auto_gain_toggle = False

    def Init_Balance_White_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        st_white_mode = MVCC_ENUMVALUE()
        memset(byref(st_white_mode), 0, sizeof(MVCC_ENUMVALUE))
        ret = self.obj_cam.MV_CC_GetEnumValue("BalanceWhiteAuto", st_white_mode)
        self.white_mode = st_white_mode.nCurValue
        if self.white_mode == 1: #1 is continuous mode
            #print(True)
            _cam_class.auto_white_toggle = True
        #elif self.white_mode == 2: #2 is once mode, #0 is off mode
        else:
            #print(False)
            _cam_class.auto_white_toggle = False

        # print(_cam_class.auto_white_toggle)

    def Init_Black_Level_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        stBool = c_bool(False)
        ret =self.obj_cam.MV_CC_GetBoolValue("BlackLevelEnable", byref(stBool))
        if ret != 0:
            print ("get acquisition black level enable fail! ret[0x%x]" % ret)

        if str(stBool) == 'c_bool(True)':
            _cam_class.black_lvl_toggle = True
        elif str(stBool) == 'c_bool(False)':
            _cam_class.black_lvl_toggle = False

    def Init_Sharpness_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        stBool = c_bool(False)
        ret =self.obj_cam.MV_CC_GetBoolValue("SharpnessEnable", byref(stBool))
        #print(ret)
        if ret != 0:
            print ("get acquisition sharpness enable fail! ret[0x%x]" % ret)

        if str(stBool) == 'c_bool(True)':
            _cam_class.sharpness_toggle = True
        elif str(stBool) == 'c_bool(False)':
            _cam_class.sharpness_toggle = False

    def Start_grabbing(self):
        ret = None
        if False == self.b_start_grabbing and True == self.b_open_device:
            self.b_exit = False

            ret = self.obj_cam.MV_CC_StartGrabbing()
            if ret != 0:
                # ret = 2147483648
                Error_Msgbox(message = 'Start grabbing fail!\nError('+ self.To_hex_str(ret)+')', title = 'Start Grab Error', message_anchor = 'w')
                self.b_start_grabbing = False
                self.start_grabbing_event.set()
                return ret

            self.b_start_grabbing = True

            if self.cam_display_thread is None:
                self.cam_display_event.clear()
                self.cam_display_thread = threading.Thread(target=self.Cam_Disp_Thread, daemon = True)
                self.cam_display_thread.start()

            try:
                self.start_grabbing_event.clear()
                self.h_thread_handle = threading.Thread(target=self.Work_thread, daemon = True)
                self.h_thread_handle.start()
                #print(self.h_thread_handle)
                self.b_thread_closed = True
            except Exception:
                Error_Msgbox(message = 'Start grabbing fail!\nUnable to start thread', title = 'Start Grab Error', message_anchor = 'w')
                self.b_start_grabbing = False
                self.start_grabbing_event.set()
                ret = None

        return ret

    def Stop_grabbing(self):
        if True == self.b_start_grabbing and self.b_open_device == True:
            #退出线程
            self.start_grabbing_event.set()
            
            ####################################
            self.cam_display_event.set()

            if self.cam_display_thread is not None:
                # try:
                #     Stop_thread(self.cam_display_thread)
                # except Exception:# as e:
                #     # print("Force Stop Error: ", e)
                #     pass
                del self.cam_display_thread
                self.cam_display_thread = None
                self.Normal_Mode_display_clear()
                self.SQ_Mode_display_clear()

            self.cam_display_bool = False

            if True == self.b_thread_closed:
                try:
                    Stop_thread(self.h_thread_handle)
                except Exception:# as e:
                    # print("Force Stop Error: ", e)
                    pass
                del self.h_thread_handle
                self.h_thread_handle = None
                #print(self.h_thread_handle)
                self.b_thread_closed = False
                
            ret = self.obj_cam.MV_CC_StopGrabbing()
            if ret != 0:
                Error_Msgbox(message = 'Stop grabbing fail!\nError('+ self.To_hex_str(ret)+')', title = 'Stop Grab Error', message_anchor = 'w')

            #print ("stop grabbing successfully!")
            self.b_start_grabbing = False
            self.b_exit  = True

        self.freeze_numArray = None
        self.numArray = None
        #print(self.freeze_numArray, self.numArray)


    def Close_device(self):
        from main_GUI import main_GUI
        _light_class = main_GUI.class_light_conn
        
        self.__record_force_stop = True
        # self.video_record_event.set()
        
        if True == self.b_open_device:
            #退出线程
            self.start_grabbing_event.set()

            if True == self.b_thread_closed:
                try:
                    Stop_thread(self.h_thread_handle)
                except Exception:
                    pass
                del self.h_thread_handle
                self.h_thread_handle = None
                #print(self.h_thread_handle)
                self.b_thread_closed = False

            ret = self.obj_cam.MV_CC_CloseDevice()
                
        # ch:销毁句柄 | Destroy handle
        self.b_open_device = False
        self.b_start_grabbing = False
        self.b_exit  = True
        
        self.freeze_numArray = None
        self.numArray = None
        try:
            _light_class.light_interface.sq_frame_img_list *= 0
        except AttributeError:
            pass

        self.obj_cam.MV_CC_DestroyHandle()
        #print(self.obj_cam)
        print ("close device successfully!")

    def Set_trigger_mode(self,strMode):
        if True == self.b_open_device:
            if "continuous" == strMode: 
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode",0)
                self.trigger_mode = False

                self.bool_mode_switch = True #UPDATE 18-8-2021, Boolean to track Camera Mode switch
                if not self.start_grabbing_event.isSet():
                    # print('Waiting: ')
                    self.start_grabbing_event.wait(0.05)

                if ret != 0:
                    Error_Msgbox(message = 'Set Continuous Mode fail!\nError('+ self.To_hex_str(ret)+')', title = 'Camera Mode Error', message_anchor = 'w')

            if "triggermode" == strMode:
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode",1)
                if ret != 0:
                    Error_Msgbox(message = 'Set Trigger Mode fail!\nError('+ self.To_hex_str(ret)+')', title = 'Camera Mode Error', message_anchor = 'w')
                    self.trigger_mode = False

                elif ret == 0:
                    self.trigger_mode = True
                    self.bool_mode_switch = True #UPDATE 18-8-2021, Boolean to track Camera Mode switch
                    if not self.start_grabbing_event.isSet():
                        # print('Waiting: ')
                        self.start_grabbing_event.wait(0.05)

    def Trigger_Source(self, strSrc):
        if True == self.b_open_device:
            if strSrc == 'LINE0':
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerSource",0)
                self.trigger_src = 0
                # print(ret)
            elif strSrc == 'LINE1':
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerSource",1)
                self.trigger_src = 1
                # print(ret)
            elif strSrc == 'LINE2':
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerSource",2)
                self.trigger_src = 2
                # print(ret)
            elif strSrc == 'LINE3':
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerSource",3)
                self.trigger_src = 3
                # print(ret)
            elif strSrc == 'COUNTER0':
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerSource",4)
                self.trigger_src = 4
                # print(ret)
            elif strSrc == 'SOFTWARE':
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerSource",7)
                self.trigger_src = 7
                # print(ret)

    def Trigger_once(self):
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetCommandValue("TriggerSoftware")
            #print('ret Trigger once: ',ret)

    def Work_thread(self):
        from main_GUI import main_GUI
        _light_class = main_GUI.class_light_conn
        _cam_class = main_GUI.class_cam_conn.active_gui

        # ch:创建显示的窗口 | en:Create the window for display
        stFrameInfo = MV_FRAME_OUT_INFO_EX()  
        img_buff = None
        self.rgb_type = False
        self.mono_type = False

        while not self.start_grabbing_event.isSet():
            # start_time = time.time()
            ret = self.obj_cam.MV_CC_GetOneFrameTimeout(byref(self.buf_cache), self.n_payload_size, stFrameInfo, 1000) #If Set to Trigger mode ret != 0 until trigger once is pressed.
            # print('Get Frame Error: ', self.To_hex_str(ret))
            #### UPDATE 18-8-2021 To introduce a delay in the loop during Camera Mode Switching
            if self.bool_mode_switch == False:
                pass

            elif self.bool_mode_switch == True:
                self.bool_mode_switch = False
                self.ext_sq_fr_init = False
                continue
            #### *
            # print('grab_ret_val: ',ret, self.trigger_mode)

            if ret == 0:
                #获取到图像的时间开始节点获取到图像的时间开始节点
                self.st_frame_info = stFrameInfo
                # print(stFrameInfo.nFrameCounter)
                size = np.multiply(self.st_frame_info.nWidth, self.st_frame_info.nHeight)

                self.n_save_image_size = int(np.multiply(size, 3)) + 2048

                if img_buff is None:
                    img_buff = (c_ubyte * self.n_save_image_size)()


            else:
                if self.trigger_mode == True and self.ext_sq_fr_init == True: #SQ Frame Function already started but not complete.
                    if True == self.SQ_Sync_Frame_Capture_Bool_External() and False == self.SQ_Sync_Frame_Capture_Bool_Internal():
                        if len(_light_class.light_interface.sq_frame_img_list) < _light_class.light_interface.sq_fr_arr[0]:
                            self.External_SQ_Fr_Disp()
                            self.Auto_Save_SQ_Frame()
                    self.ext_sq_fr_init = False

                continue

            #转换像素结构体赋值
            stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
            memset(byref(stConvertParam), 0, sizeof(stConvertParam))
            stConvertParam.nWidth = self.st_frame_info.nWidth
            stConvertParam.nHeight = self.st_frame_info.nHeight
            stConvertParam.pSrcData = self.buf_cache
            stConvertParam.nSrcDataLen = self.st_frame_info.nFrameLen
            stConvertParam.enSrcPixelType = self.st_frame_info.enPixelType 

            # print(self.buf_cache)
            #print(stConvertParam.enSrcPixelType)
            # Mono8直接显示
            #print('self.st_frame_info.enPixelType: ',self.st_frame_info.enPixelType)
            #print(int2Hex(self.st_frame_info.enPixelType))
            if PixelType_Gvsp_Mono8 == self.st_frame_info.enPixelType:
                numArray = self.Mono_numpy(self.buf_cache,self.st_frame_info.nWidth,self.st_frame_info.nHeight)
                if _cam_class.flip_img_bool == True:
                    self.numArray = imutils.rotate(numArray, 180)
                else:
                    self.numArray = numArray

                # print(self.numArray)
                self.mono_type = True
                self.rgb_type = False


            # RGB直接显示
            elif PixelType_Gvsp_RGB8_Packed == self.st_frame_info.enPixelType:
                numArray = self.Color_numpy(self.buf_cache,self.st_frame_info.nWidth,self.st_frame_info.nHeight)
                if _cam_class.flip_img_bool == True:
                    self.numArray = imutils.rotate(numArray, 180)
                else:
                    self.numArray = numArray
                #print(self.st_frame_info.nWidth, self.st_frame_info.nHeight)
                #print(type(self.st_frame_info.nWidth), type(self.st_frame_info.nHeight))
                self.mono_type = False
                self.rgb_type = True


            #如果是黑白且非Mono8则转为Mono8
            elif True == self.Is_mono_data(self.st_frame_info.enPixelType):
                #nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight
                nConvertSize = int(np.multiply(self.st_frame_info.nWidth, self.st_frame_info.nHeight))
                stConvertParam.enDstPixelType = PixelType_Gvsp_Mono8
                stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
                stConvertParam.nDstBufferSize = nConvertSize
                ret = self.obj_cam.MV_CC_ConvertPixelType(stConvertParam)
                if ret != 0:
                    print('Mono MV_CC_ConvertPixelType Error, ret: ' + self.To_hex_str(ret))
                    continue

                cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
                numArray = self.Mono_numpy(img_buff,self.st_frame_info.nWidth,self.st_frame_info.nHeight)
                if _cam_class.flip_img_bool == True:
                    self.numArray = imutils.rotate(numArray, 180)
                else:
                    self.numArray = numArray

                self.mono_type = True
                self.rgb_type = False


            #如果是彩色且非RGB则转为RGB后显示
            elif  True == self.Is_color_data(self.st_frame_info.enPixelType):
                #print('Is_color_data')
                #nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3
                
                nConvertSize = int( np.multiply (np.multiply(self.st_frame_info.nWidth, self.st_frame_info.nHeight), 3) )
                stConvertParam.enDstPixelType = PixelType_Gvsp_RGB8_Packed
                stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
                stConvertParam.nDstBufferSize = nConvertSize
                ret = self.obj_cam.MV_CC_ConvertPixelType(stConvertParam)
                if ret != 0:
                    print('Color MV_CC_ConvertPixelType Error, ret: ' + self.To_hex_str(ret))
                    continue
                    
                cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
                #self.numArray = CameraOperation.Color_numpy(self,img_buff,self.st_frame_info.nWidth,self.st_frame_info.nHeight)
                numArray = self.Color_numpy(img_buff,self.st_frame_info.nWidth,self.st_frame_info.nHeight)
                if _cam_class.flip_img_bool == True:
                    self.numArray = imutils.rotate(numArray, 180)
                else:
                    self.numArray = numArray

                self.mono_type = False
                self.rgb_type = True

                #print('color')
                ################################################################

            if _cam_class.capture_img_status.get() == 1:
                if self.freeze_numArray is None:
                    self.freeze_numArray = self.numArray

            elif _cam_class.capture_img_status.get() == 0:
                self.freeze_numArray = None

            self.cam_display_bool = True
            # stop_time = time.time()
            # elapsed_time = stop_time - start_time
            # print('FPS: ', 1/elapsed_time)

            try:
                if self.trigger_mode == True:
                    if True == self.SQ_Sync_Frame_Capture_Bool_External() and False == self.SQ_Sync_Frame_Capture_Bool_Internal():
                        # print('SQ Sync Frame External Mode')
                        if self.ext_sq_fr_init == False:
                            _light_class.light_interface.sq_frame_img_list *= 0
                            # print('SQ Frame Clear: ', len(_light_class.light_interface.sq_frame_img_list))
                            self.ext_sq_fr_init = True

                        elif self.ext_sq_fr_init == True:
                            pass
                        
                        ## len(list) empty = 0, sq_fr_arr[0] is the frame num: 1 - 10
                        _light_class.light_interface.sq_frame_img_list.append(self.numArray)
                        # print('Sq Frame: ',len(_light_class.light_interface.sq_frame_img_list))
                        if len(_light_class.light_interface.sq_frame_img_list) ==  _light_class.light_interface.sq_fr_arr[0]:
                            #print(len(_light_class.light_interface.sq_frame_img_list), _light_class.light_interface.sq_fr_arr[0])
                            # print('SQ Display')
                            self.External_SQ_Fr_Disp()
                            self.Auto_Save_SQ_Frame()

                            self.ext_sq_fr_init = False #UPDATE 18-8-2021

                        elif len(_light_class.light_interface.sq_frame_img_list) > _light_class.light_interface.sq_fr_arr[0]:
                            # print('SQ Frame Overflow')
                            #print('Reset list')
                            self.ext_sq_fr_init = False #UPDATE 18-8-2021


                    if True == self.SQ_Sync_Frame_Capture_Bool_Internal() and False == self.SQ_Sync_Frame_Capture_Bool_External():
                        # print('SQ Sync Frame Internal Mode')
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

            if _cam_class.trigger_auto_save_bool.get() == 1 and self.trigger_mode == True:
                self.Normal_Mode_Save(self.numArray, self.freeze_numArray, auto_save = True)
            elif _cam_class.trigger_auto_save_bool.get() == 0 and self.trigger_mode == False:
                self.Normal_Mode_Save(self.numArray, self.freeze_numArray, auto_save = False)


            # stop_time = time.time()
            # elapsed_time = stop_time - start_time
            # print('FPS: ', 1/elapsed_time)

            if _cam_class.record_bool == False:
                self.record_init = False

            elif _cam_class.record_bool == True:
                if self.video_record_thread is None:
                    self.video_record_event.clear()
                    isColor = False
                    if len(self.numArray.shape) == 3:
                        isColor = True 

                    self.video_record_thread = threading.Thread(target=self.OpenCV_Record_Func_v2, args=(self.st_frame_info.nWidth,self.st_frame_info.nHeight, isColor), daemon = True)
                    print('Record Started')
                    self.video_record_thread.start()

            # self.All_Mode_Cam_Disp()

            # stop_time = time.time()
            # elapsed_time = stop_time - start_time
            # print('FPS: ', 1/elapsed_time)

            if self.b_exit == True:
                #print('breaking')
                break

    def SQ_Sync_Frame_Capture_Bool_External(self):
        from main_GUI import main_GUI
        _light_class = main_GUI.class_light_conn
        _light_sq_param = None

        if _light_class.light_conn_status == True:
            if (_light_class.firmware_model_sel == 'SQ' or _light_class.firmware_model_sel == 'LC20'):
                _light_sq_param = main_GUI.class_light_conn.light_interface
                if (self.trigger_src == 0 and _light_sq_param.updating_bool == False):

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
                    if self.trigger_src == 7 and _light_sq_param.updating_bool == False:

                        return True

            elif _light_class.firmware_model_sel == 'LC20':
                _light_sq_param = main_GUI.class_light_conn.light_interface

                if (_light_sq_param.channel_SQ_save[2] == 1):
                    if self.trigger_src == 7 and _light_sq_param.updating_bool == False:

                        return True

            return False

        else:
            return False

    def OpenCV_Record_Init_v2(self, frame_w, frame_h, isColor):
        if self.record_init == False:
            if self.frame_queue is not None:
                del self.frame_queue
                self.frame_queue = None

            save_folder = create_save_folder()
            fourcc = cv2.VideoWriter_fourcc(*'XVID') #cv2.VideoWriter_fourcc(*'MP42') #cv2.VideoWriter_fourcc(*'XVID')
            self.video_file = video_file_name(save_folder, 'Output Recording')

            # print(self.video_writer.getBackendName())
            
            actual_FrameRate =  MVCC_FLOATVALUE()
            memset(byref(actual_FrameRate), 0, sizeof(MVCC_FLOATVALUE))
            ret = self.obj_cam.MV_CC_GetFloatValue("ResultingFrameRate", actual_FrameRate)
            if ret != 0:
                actual_FrameRate.fCurValue = 1
            # print('Resulting FPS: ', actual_FrameRate.fCurValue)
            
            expected_FrameRate =  MVCC_FLOATVALUE()
            memset(byref(expected_FrameRate), 0, sizeof(MVCC_FLOATVALUE))
            self.obj_cam.MV_CC_GetFloatValue("AcquisitionFrameRate", expected_FrameRate)
            if ret != 0:
                expected_FrameRate.fCurValue = 1
            print('Expected FPS: ', expected_FrameRate.fCurValue)

            resultant_fps = int( min(actual_FrameRate.fCurValue, expected_FrameRate.fCurValue))
            # resultant_fps = int(min(actual_FrameRate.fCurValue, 12))

            self.record_init = True
            self.__video_empty_bool = True #Checker to check whether video file is empty or not
            self.__record_force_stop = False
            self.__queue_start = False

            self.queue_size = int( np.multiply(np.multiply(resultant_fps, 60), 20) ) #lets record for maximum of 10 mins(outdated) #New implementation with batch, we set it to queue size to hold double of batch threshold
            print('Allocated frame queue size: ', self.queue_size)
            self.frame_queue = Queue(maxsize = self.queue_size) # We will also control this by setting a video timer, to minimize the occurence of memory overload.
            
            # self.frame_queue = Queue(maxsize = 0) #infinite queue size. But we will control this by setting a video timer, to minimize the occurence of memory overload.
            print('Write FPS: ', resultant_fps)
            self.video_writer = cv2.VideoWriter(self.video_file, fourcc, resultant_fps
                , (frame_w, frame_h), isColor = isColor)

            self.dequeue_num = 0
            self.video_write_thread = None
            self.start_record_time = time.time() #Init record time.
            self.pause_record_duration = 0
            self.elapse_time = 0

            return resultant_fps

        else:
            return None

    def OpenCV_Record_Func_v2(self, frame_w, frame_h, isColor): #(self, resultant_fps):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        video_size = _cam_class.rec_setting_param[1]
        resize_w = int(np.multiply(frame_w, video_size))
        resize_h = int(np.multiply(frame_h, video_size))

        resultant_fps = self.OpenCV_Record_Init_v2(resize_w, resize_h, isColor)

        delay = np.divide(1, resultant_fps*1.5) #Nyquist Rule (but not exactly Nyquist Rule)
        # delay = np.divide(1, resultant_fps)
        # print(resultant_fps, delay)
        # batch_size = int( max(np.multiply(resultant_fps, 5), 30) )
        self.elapse_time = 0
        while not self.video_record_event.isSet():
            if self.record_init == True:
                if psutil.virtual_memory().percent <= 80:
                    if self.freeze_numArray is None:
                        if self.numArray is not None and (isinstance(self.numArray, np.ndarray)) == True:
                            if len(self.numArray.shape) == 3:
                                frame_arr = cv2.cvtColor(self.numArray, cv2.COLOR_BGR2RGB)
                            else:
                                frame_arr = self.numArray

                            if video_size < float(1):
                                frame_arr = cv2.resize(frame_arr, (resize_w, resize_h), interpolation = cv2.INTER_LINEAR)
                                # print(frame_arr.shape)

                            if not self.frame_queue.full() and self.b_start_grabbing == True:
                                time_update = time.time()
                                self.elapse_time = int( time_update - self.start_record_time) - self.pause_record_duration

                                # print('Recording Time: ', self.elapse_time, self.pause_record_duration)

                                queue_check = int(np.multiply(resultant_fps, self.elapse_time + 1) ) - self.dequeue_num
                                if self.frame_queue.qsize() < queue_check:
                                    self.frame_queue.put(frame_arr)
                                    self.__queue_start = True
                                    _cam_class.time_lapse_var.set(time_convert(self.elapse_time))

                                if self.frame_queue.qsize() > 0:
                                    # print('Memory Tracker: ', self.frame_queue.qsize(), psutil.virtual_memory().percent)
                                    if self.video_write_thread is None:
                                        self.video_write_thread = threading.Thread(target=self.OpenCV_video_write_batch_v2, args=(None,), daemon = True)
                                        self.video_write_thread.start()

                    elif self.freeze_numArray is not None and (isinstance(self.freeze_numArray, np.ndarray)) == True:
                        if len(self.freeze_numArray.shape) == 3:
                            frame_arr = cv2.cvtColor(self.freeze_numArray, cv2.COLOR_BGR2RGB)
                        else:
                            frame_arr = self.freeze_numArray

                        if not self.frame_queue.full() and self.b_start_grabbing == True:
                            self.elapse_time = int( time.time() - self.start_record_time) 
                            queue_check = int(np.multiply(resultant_fps, self.elapse_time + 1) ) - self.dequeue_num
                            if self.frame_queue.qsize() < queue_check:
                                self.frame_queue.put(frame_arr)
                                self.__queue_start = True
                                _cam_class.time_lapse_var.set(time_convert(self.elapse_time))


                            if self.frame_queue.qsize() > 0:
                                # print('Memory Tracker: ', self.frame_queue.qsize(), psutil.virtual_memory().percent)
                                if self.video_write_thread is None:
                                    self.video_write_thread = threading.Thread(target=self.OpenCV_video_write_batch_v2, args=(None,), daemon = True)
                                    self.video_write_thread.start()

                    if self.b_start_grabbing == False:
                        time_update = time.time()
                        self.pause_record_duration = int(time_update - self.start_record_time) - self.elapse_time
                        # print('Pause: ', self.pause_record_duration)

                else:
                    _cam_class.record_stop_func()
                    self.record_warning_flag = True
                    

            elif self.record_init == False:
                _cam_class.record_btn_1['state'] = 'disable'

                if self.__queue_start == True:
                    #To Flush All the contents in frame Queue
                    if self.video_write_thread is None:
                        self.video_write_thread = threading.Thread(target=self.OpenCV_video_write_full_v2, daemon = True)
                        self.video_write_thread.start()

                elif self.__queue_start == False:
                    self.video_record_event.set()

            self.video_record_event.wait(delay)

            # print(self.frame_queue.qsize())
        del self.video_record_thread
        self.video_record_thread = None

        if _cam_class.cam_conn_status == True:
            _cam_class.record_setting_btn['state'] = 'normal'
            if _cam_class.cam_mode_var.get() == 'continuous':
                _cam_class.record_btn_1['state'] = 'normal'
            _cam_class.time_lapse_var.set('')

        elif _cam_class.cam_conn_status == False:
            _cam_class.record_btn_1['state'] = 'disable'
            _cam_class.record_setting_btn['state'] = 'disable'
            _cam_class.time_lapse_var.set('')

        # print('Exitted Queue Load')
        if self.__record_force_stop == True:
            # print('Queue Load Force Stop...')
            if self.frame_queue is not None:
                del self.frame_queue
                self.frame_queue = None

            if self.video_writer is not None:
                self.video_writer.release()
                del self.video_writer
                self.video_writer = None

            # if self.__video_empty_bool == True:
            #     os.remove(self.video_file)
            os.remove(self.video_file)

        elif self.__record_force_stop == False:
            if self.frame_queue is not None:
                del self.frame_queue
                self.frame_queue = None

            if self.video_writer is not None:
                self.video_writer.release()
                del self.video_writer
                self.video_writer = None

            if self.__video_empty_bool == True:
                os.remove(self.video_file)

            elif self.__video_empty_bool == False:
                self.record_complete_flag = True


    def OpenCV_video_write_full_v2(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        # _cam_class.record_btn_1['state'] = 'disable'

        print('Full Writing...')
        while not self.frame_queue.empty():
            if self.__record_force_stop == True:
                break
            frame_item = self.frame_queue.get()
            if frame_item is not None and (isinstance(frame_item, np.ndarray)) == True:
                self.video_writer.write(frame_item)
                if self.__video_empty_bool == True:
                    self.__video_empty_bool = False
            self.frame_queue.task_done()

        print('Full Write Done...')
        if self.video_write_thread is not None:
            del self.video_write_thread
            self.video_write_thread = None

        if self.video_writer is not None:
            self.video_writer.release()
            del self.video_writer
            self.video_writer = None

        self.__queue_start = False


    def OpenCV_video_write_batch_v2(self, batch_num = None):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        # print('Batch Writing...')
        if batch_num is not None:
            frame_counter = 0
            while not self.frame_queue.empty():
                if self.__record_force_stop == True:
                    break
                if frame_counter == batch_num:
                    break
                frame_item = self.frame_queue.get()
                self.dequeue_num += 1
                if frame_item is not None and (isinstance(frame_item, np.ndarray)) == True:
                    self.video_writer.write(frame_item)
                    if self.__video_empty_bool == True:
                        self.__video_empty_bool = False

                self.frame_queue.task_done()
                frame_counter += 1

        elif batch_num is None:
            while not self.frame_queue.empty():
                if self.__record_force_stop == True:
                    break
                frame_item = self.frame_queue.get()
                self.dequeue_num += 1
                if frame_item is not None and (isinstance(frame_item, np.ndarray)) == True:
                    self.video_writer.write(frame_item)
                    if self.__video_empty_bool == True:
                        self.__video_empty_bool = False

                self.frame_queue.task_done()

        # print('Batch Write Done...')

        if self.__record_force_stop == True:
            print('Batch Write Force Stop...')
            if self.video_writer is not None:
                self.video_writer.release()
                del self.video_writer
                self.video_writer = None

        if self.video_write_thread is not None:
            del self.video_write_thread
            self.video_write_thread = None


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

    def set_custom_save_param(self, folder_name, file_name, overwrite_bool = False):
        self.__custom_save_folder = str(folder_name)
        self.__custom_save_name = str(file_name)
        self.__custom_save_overwrite = overwrite_bool

    def Normal_Mode_Save(self, arr_1, arr_2 = None, auto_save = False): #Normal Camera Mode Save
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        img_arr = arr_1
        if isinstance(arr_2, np.ndarray) == True:
            img_arr = arr_2

        if auto_save == False:
            if True == self.__validate_rgb_img(img_arr) and False == self.__validate_mono_img(img_arr):
                if self.b_save == True and self.custom_b_save == False:
                    img_format = _cam_class.save_img_format_sel.get()
                    time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                    # time_id = str(datetime.now().strftime("%Y-%m-%d"))
                    save_folder = create_save_folder()

                    if self.trigger_mode == True:
                        sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\Trigger--' + time_id, duplicate = True)
                        # sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\Trigger--' + time_id, duplicate = False)
                    else:
                        sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\Camera--' + time_id, duplicate = True)
                        # sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\Camera--' + time_id, duplicate = False)

                    if str(img_format) == '.pdf':
                        _, id_index = PDF_img_save(sub_folder, img_arr, 'Colour', ch_split_bool = False)
                    else:
                        _, id_index = cv_img_save(sub_folder, img_arr, 'Colour', str(img_format))
                        cv_img_save(sub_folder, img_arr[:,:,0], 'Red-Ch' + '--id{}'.format(id_index), str(img_format), overwrite = True)
                        cv_img_save(sub_folder, img_arr[:,:,1], 'Green-Ch' + '--id{}'.format(id_index), str(img_format), overwrite = True)
                        cv_img_save(sub_folder, img_arr[:,:,2], 'Blue-Ch' + '--id{}'.format(id_index), str(img_format), overwrite = True)

                    self.img_save_folder = sub_folder
                    self.img_save_flag = True
                    self.b_save = False

                    self.__custom_save_folder = None
                    self.__custom_save_name = None
                    self.__custom_save_overwrite = False

                elif self.b_save == False and self.custom_b_save == True:
                    img_format = _cam_class.save_img_format_sel.get()
                    sub_folder = str(self.__custom_save_folder)
                    file_name = str(self.__custom_save_name)

                    if str(img_format) == '.pdf':
                        _, id_index = PDF_img_save(sub_folder, img_arr, file_name
                            , ch_split_bool = False
                            , kw_str = "(Colour)"
                            , overwrite = self.__custom_save_overwrite)
                    else:
                        _, id_index = cv_img_save(sub_folder, img_arr, file_name
                            , str(img_format)
                            , kw_str = "(Colour)"
                            , overwrite = self.__custom_save_overwrite)

                        cv_img_save(sub_folder, img_arr[:,:,0]
                            , file_name + '-(Red-Ch)' + '--id{}'.format(id_index)
                            , str(img_format), overwrite = True)

                        cv_img_save(sub_folder, img_arr[:,:,1]
                            , file_name + '-(Green-Ch)' + '--id{}'.format(id_index)
                            , str(img_format), overwrite = True)

                        cv_img_save(sub_folder, img_arr[:,:,2]
                            , file_name + '-(Blue-Ch)' + '--id{}'.format(id_index)
                            , str(img_format), overwrite = True)

                    self.img_save_folder = sub_folder
                    self.img_save_flag = True
                    self.custom_b_save = False

                    self.__custom_save_folder = None
                    self.__custom_save_name = None
                    self.__custom_save_overwrite = False


            elif False == self.__validate_rgb_img(img_arr) and True == self.__validate_mono_img(img_arr):
                if self.b_save == True and self.custom_b_save == False:
                    img_format = _cam_class.save_img_format_sel.get()
                    time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                    # time_id = str(datetime.now().strftime("%Y-%m-%d"))
                    save_folder = create_save_folder()
                    
                    if self.trigger_mode == True:
                        sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\Trigger--' + time_id, duplicate = True)
                        # sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\Trigger--' + time_id, duplicate = False)
                    else:
                        sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\Camera--' + time_id, duplicate = True)
                        # sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\Camera--' + time_id, duplicate = False)

                    if str(img_format) == '.pdf':
                        PDF_img_save(sub_folder, img_arr, 'Mono', ch_split_bool = False)
                    else:
                        cv_img_save(sub_folder, img_arr, 'Mono', str(img_format))

                    self.img_save_folder = sub_folder
                    self.img_save_flag = True
                    self.b_save = False

                    self.__custom_save_folder = None
                    self.__custom_save_name = None
                    self.__custom_save_overwrite = False

                elif self.b_save == False and self.custom_b_save == True:
                    img_format = _cam_class.save_img_format_sel.get()
                    sub_folder = str(self.__custom_save_folder)
                    file_name = str(self.__custom_save_name)

                    if str(img_format) == '.pdf':
                        PDF_img_save(sub_folder, img_arr, file_name
                            , ch_split_bool = False
                            , kw_str = "(Mono)"
                            , overwrite = self.__custom_save_overwrite)
                    else:
                        cv_img_save(sub_folder, img_arr, file_name
                            , str(img_format)
                            , kw_str = "(Mono)"
                            , overwrite = self.__custom_save_overwrite)
                    
                    self.img_save_folder = sub_folder
                    self.img_save_flag = True
                    self.custom_b_save = False

                    self.__custom_save_folder = None
                    self.__custom_save_name = None
                    self.__custom_save_overwrite = False
            
            else:
                self.b_save = False
                self.custom_b_save = False
                self.img_save_folder = None

                self.__custom_save_folder = None
                self.__custom_save_name = None
                self.__custom_save_overwrite = False

                _cam_class.clear_img_save_msg_box()


        elif auto_save == True:
            if True == self.__validate_rgb_img(img_arr) and False == self.__validate_mono_img(img_arr):
                img_format = _cam_class.save_img_format_sel.get()
                time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                # time_id = str(datetime.now().strftime("%Y-%m-%d"))
                save_folder = create_save_folder()
                sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\Trigger--' + time_id, duplicate = True)
                # sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\Trigger--' + time_id, duplicate = False)
                if str(img_format) == '.pdf':
                    _, id_index = PDF_img_save(sub_folder, img_arr, 'Colour', ch_split_bool = False)
                else:
                    _, id_index = cv_img_save(sub_folder, img_arr, 'Colour', str(img_format))
                    cv_img_save(sub_folder, img_arr[:,:,0], 'Red-Ch' + '--id{}'.format(id_index), str(img_format), overwrite = True)
                    cv_img_save(sub_folder, img_arr[:,:,1], 'Green-Ch' + '--id{}'.format(id_index), str(img_format), overwrite = True)
                    cv_img_save(sub_folder, img_arr[:,:,2], 'Blue-Ch' + '--id{}'.format(id_index), str(img_format), overwrite = True)

            elif False == self.__validate_rgb_img(img_arr) and True == self.__validate_mono_img(img_arr):
                img_format = _cam_class.save_img_format_sel.get()
                time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                # time_id = str(datetime.now().strftime("%Y-%m-%d"))
                save_folder = create_save_folder()
                sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\Trigger--' + time_id, duplicate = True)
                # sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\Trigger--' + time_id, duplicate = False)

                if str(img_format) == '.pdf':
                    PDF_img_save(sub_folder, img_arr, 'Mono', ch_split_bool = False)
                else:
                    cv_img_save(sub_folder, img_arr, 'Mono', str(img_format))


    def __validate_rgb_img(self, img_arr):
        if isinstance(img_arr, np.ndarray) == True and len(img_arr.shape) == 3:
            if img_arr.dtype is np.dtype(np.uint8):
                return True
            else:
                return False
        else:
            return False

    def __validate_mono_img(self, img_arr):
        if isinstance(img_arr, np.ndarray) == True and len(img_arr.shape) == 2:
            if img_arr.dtype is np.dtype(np.uint8):
                return True
            else:
                return False
        else:
            return False

    def check_cam_frame(self):
        '''check_cam_frame if self.numArray is None it means no frames were loaded from the camera'''
        if True == self.__validate_rgb_img(self.numArray) or True == self.__validate_mono_img(self.numArray):
            return True

        else:
            return False

    def Trigger_Mode_Save(self):
        if isinstance(self.freeze_numArray, np.ndarray) == True:
            img_arr = self.freeze_numArray
        else:
            img_arr = self.numArray

        self.Normal_Mode_Save(arr_1 = img_arr)

    def Cam_Disp_Thread(self):
        self.cam_display_bool = False

        while not self.cam_display_event.isSet():
            actual_frame_rate = self.Get_actual_framerate()
            cam_display_fps = np.divide(1, float(actual_frame_rate))
            if self.cam_display_bool == True:
                self.All_Mode_Cam_Disp()

            self.cam_display_event.wait(cam_display_fps)
        
        self.Normal_Mode_display_clear()
        self.SQ_Mode_display_clear()
        # print('Cam_Disp_Thread Stopped')

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
        if True == self.__validate_rgb_img(img_arr):
            try:
                display_func(_cam_class.cam_display_rgb, img_arr, _cam_class.cam_display_width, _cam_class.cam_display_height)
                display_func(_cam_class.cam_display_R, img_arr[:,:,0], _cam_class.cam_display_width, _cam_class.cam_display_height)
                display_func(_cam_class.cam_display_G, img_arr[:,:,1], _cam_class.cam_display_width, _cam_class.cam_display_height)
                display_func(_cam_class.cam_display_B, img_arr[:,:,2], _cam_class.cam_display_width, _cam_class.cam_display_height)
            
            except(tk.TclError):
                pass

    def Mono_display(self, img_arr):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        #Display for Normal Camera Mode
        if True == self.__validate_mono_img(img_arr):
            try:
                display_func(_cam_class.cam_display_rgb, img_arr, _cam_class.cam_display_width + _cam_class.cam_display_width +  10
                    , _cam_class.cam_display_height + _cam_class.cam_display_height + 50)

            except(tk.TclError):
                pass

    def Normal_Mode_display_clear(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        #Clear Display for Normal Camera Mode
        try:
            clear_display_func(_cam_class.cam_display_rgb
                , _cam_class.cam_display_R
                , _cam_class.cam_display_G
                , _cam_class.cam_display_B)
        except(tk.TclError):
            pass
        

    def popout_display(self, img_arr):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        if self.rgb_type == False and self.mono_type == True:
            _cam_class.popout_var_mode = 'original'
            try:
                _cam_class.sel_R_btn['state'] = 'disable'
                _cam_class.sel_G_btn['state'] = 'disable'
                _cam_class.sel_B_btn['state'] = 'disable'
            except (AttributeError, tk.TclError):
                pass

        elif self.rgb_type == True and self.mono_type == False:
            try:
                _cam_class.sel_R_btn['state'] = 'normal'
                _cam_class.sel_G_btn['state'] = 'normal'
                _cam_class.sel_B_btn['state'] = 'normal'
            except (AttributeError, tk.TclError):
                pass

        try:
            _cam_class.popout_cam_disp_func(img_arr)
        except(tk.TclError):
            pass


    def SQ_live_display(self, img_arr):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        #Display for SQ Camera Mode
        if True == self.__validate_rgb_img(img_arr) or True == self.__validate_mono_img(img_arr):
            try:
                display_func(_cam_class.cam_disp_current_frame, img_arr, _cam_class.cam_display_width, _cam_class.cam_display_height)
            
            except(tk.TclError):
                pass

    def SQ_Mode_display_clear(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        try:
            clear_display_func(_cam_class.cam_disp_current_frame)

        except(tk.TclError):
            pass

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

            img_format = _cam_class.save_img_format_sel.get()
            save_folder = create_save_folder()

            frame_index = 1
            pdf_img_list = []

            if len(self.sq_frame_save_list) > 0:
                time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                # time_id = str(datetime.now().strftime("%Y-%m-%d"))
                sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\SQ-Frames--' + time_id, duplicate = True)

                for images in self.sq_frame_save_list:
                    if str(img_format) == '.pdf':
                        pdf_img_list.append(np_to_PIL(images))

                    else:
                        if frame_index == 1:
                            _, id_index = cv_img_save(sub_folder, images, 'SQ-Frame-{}'.format(frame_index), str(img_format))
                            #We used id_index from 1st Frame, and used id_index to overwrite for the other frames. To ensure all frame(s) have the same id
                        else:
                            cv_img_save(sub_folder, images, 'SQ-Frame-{}--id{}'.format(frame_index, id_index), str(img_format), overwrite = True)

                    frame_index = frame_index + 1
            
                if str(img_format) == '.pdf':
                    if len(pdf_img_list) > 0:
                        PDF_img_list_save(folder = sub_folder, pdf_img_list = pdf_img_list, pdf_name = 'SQ-Frame--(Frame-1-to-{})'.format(frame_index-1))
                        
                        Info_Msgbox(message = 'All loaded SQ Frames Were Saved In' + '\n\n' + str(sub_folder), title = 'SQ Save'
                            , font = 'Helvetica 10', width = 400, height = 180)
                    else:
                        if os.path.isdir(sub_folder):
                            shutil.rmtree(sub_folder)# remove sub_folder dir and all contains
                else:
                    Info_Msgbox(message = 'All loaded SQ Frames Were Saved In' + '\n\n' + str(sub_folder), title = 'SQ Save'
                        , font = 'Helvetica 10', width = 400, height = 180)
        else:
            Warning_Msgbox(message = 'Please Ensure That All SQ Frames Were Loaded To Save', title = 'Warning SQ Save'
                , font = 'Helvetica 10', message_anchor = 'w')

    def Auto_Save_SQ_Frame(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        if _cam_class.SQ_auto_save_bool.get() == 1:
            img_format = _cam_class.save_img_format_sel.get()
            save_folder = create_save_folder()
            frame_index = 1
            pdf_img_list = []

            if len(self.sq_frame_save_list) > 0:
                # time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                # sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\SQ-Frames--' + time_id, duplicate = True)
                time_id = str(datetime.now().strftime("%Y-%m-%d"))
                sub_folder = create_save_folder(os.getcwd() + '\\TMS_Saved_Images\\SQ-Frames-(auto-save)--' + time_id, duplicate = False)

                for images in self.sq_frame_save_list:
                    if str(img_format) == '.pdf':
                        pdf_img_list.append(np_to_PIL(images))

                    else:
                        if frame_index == 1:
                            if self.__sq_save_next_id_index is not None and type(self.__sq_save_next_id_index) == int:
                                id_index = self.__sq_save_next_id_index
                                cv_img_save(sub_folder, images, 'SQ-Frame-{}--id{}'.format(frame_index, id_index), str(img_format), overwrite = True)
                                self.__sq_save_next_id_index += 1
                            else:
                                _, id_index = cv_img_save(sub_folder, images, 'SQ-Frame-{}'.format(frame_index), str(img_format))
                                self.__sq_save_next_id_index = int(id_index) + 1

                        #We used id_index from 1st Frame, and used id_index to overwrite for the other frames. To ensure all frame(s) have the same id
                        else:
                            cv_img_save(sub_folder, images, 'SQ-Frame-{}--id{}'.format(frame_index, id_index), str(img_format), overwrite = True)

                    frame_index = frame_index + 1

                if str(img_format) == '.pdf':
                    if len(pdf_img_list) > 0:
                        PDF_img_list_save(folder = sub_folder, pdf_img_list = pdf_img_list, pdf_name = 'SQ-Frame--(Frame-1-to-{})'.format(frame_index-1))
                    else:
                        pass

        elif _cam_class.SQ_auto_save_bool.get() == 0:
            self.__sq_save_next_id_index = None
            pass


    def Is_mono_data(self,enGvspPixelType):
        if PixelType_Gvsp_Mono8 == enGvspPixelType or PixelType_Gvsp_Mono10 == enGvspPixelType \
            or PixelType_Gvsp_Mono10_Packed == enGvspPixelType or PixelType_Gvsp_Mono12 == enGvspPixelType \
            or PixelType_Gvsp_Mono12_Packed == enGvspPixelType:
            return True
        else:
            return False

    def Is_color_data(self,enGvspPixelType):
        if PixelType_Gvsp_BayerGR8 == enGvspPixelType or PixelType_Gvsp_BayerRG8 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB8 == enGvspPixelType or PixelType_Gvsp_BayerBG8 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR10 == enGvspPixelType or PixelType_Gvsp_BayerRG10 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB10 == enGvspPixelType or PixelType_Gvsp_BayerBG10 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR12 == enGvspPixelType or PixelType_Gvsp_BayerRG12 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB12 == enGvspPixelType or PixelType_Gvsp_BayerBG12 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR10_Packed == enGvspPixelType or PixelType_Gvsp_BayerRG10_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGB10_Packed == enGvspPixelType or PixelType_Gvsp_BayerBG10_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGR12_Packed == enGvspPixelType or PixelType_Gvsp_BayerRG12_Packed== enGvspPixelType \
            or PixelType_Gvsp_BayerGB12_Packed == enGvspPixelType or PixelType_Gvsp_BayerBG12_Packed == enGvspPixelType \
            or PixelType_Gvsp_YUV422_Packed == enGvspPixelType or PixelType_Gvsp_YUV422_YUYV_Packed == enGvspPixelType:
            return True
        else:
            return False

    def Mono_numpy(self,data,nWidth,nHeight):
        data_ = np.frombuffer(data, count=int(np.multiply(nWidth, nHeight)), dtype=np.uint8, offset=0)
        data_mono_arr = data_.reshape(nHeight, nWidth)
        #numArray = np.zeros([nHeight, nWidth, 1],"uint8") 
        #numArray[:, :, 0] = data_mono_arr
        numArray = np.zeros([nHeight, nWidth],"uint8") 
        numArray[:, :] = data_mono_arr
        return numArray

    def Color_numpy(self,data,nWidth,nHeight):
        data_ = np.frombuffer(data, count=int(np.multiply(np.multiply(nWidth, nHeight),3)), dtype=np.uint8, offset=0)
        # print(len(data_))
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

        if _cam_class.auto_exposure_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("ExposureAuto", 2) #value of 2 is to activate Exposure Auto.
            if ret == 0:
                #print('Auto Exposure ON')
                _cam_class.btn_auto_exposure['image'] = _cam_class.toggle_ON_button_img
                _cam_class.entry_exposure['state'] = 'disabled'
                _cam_class.auto_exposure_toggle = True

                pass
            elif ret != 0:
                _cam_class.auto_exposure_toggle = False
                pass

        elif _cam_class.auto_exposure_toggle == True and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("ExposureAuto", 0)
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

        if _cam_class.auto_gain_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("GainAuto", 2) #value of 2 is to activate Exposure Auto.
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
            ret = self.obj_cam.MV_CC_SetEnumValue("GainAuto", 0)
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

    def Enable_Framerate(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        if _cam_class.framerate_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetBoolValue("AcquisitionFrameRateEnable", c_bool(True)) #value of 2 is to activate Exposure Auto.
            #print('Enabled', ret)
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
            ret = self.obj_cam.MV_CC_SetBoolValue("AcquisitionFrameRateEnable", c_bool(False))
            #print('Disabled', ret)
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

    def Auto_White(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui

        if _cam_class.auto_white_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("BalanceWhiteAuto", 1)
            if ret == 0:
                # print('Auto White ON')
                _cam_class.auto_white_toggle = True
                _cam_class.white_balance_btn_state()
                pass
            elif ret != 0:
                _cam_class.auto_white_toggle = False
                pass

        elif _cam_class.auto_white_toggle == True and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("BalanceWhiteAuto", 0)
            if ret == 0:
                # print('Auto White OFF')
                _cam_class.auto_white_toggle = False
                _cam_class.white_balance_btn_state()
                pass
            elif ret != 0:
                _cam_class.auto_white_toggle = True
                pass
        else:
            pass

    def Enable_Blacklevel(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        if _cam_class.black_lvl_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetBoolValue("BlackLevelEnable", c_bool(True)) #value of 2 is to activate Exposure Auto.
            if ret == 0:
                _cam_class.black_lvl_toggle = True
                _cam_class.black_lvl_btn_state()
                pass
            elif ret != 0:
                _cam_class.black_lvl_toggle = False
                pass

        elif _cam_class.black_lvl_toggle == True and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetBoolValue("BlackLevelEnable", c_bool(False))
            if ret == 0:
                _cam_class.black_lvl_toggle = False
                _cam_class.black_lvl_btn_state()
                pass
            elif ret != 0:
                _cam_class.black_lvl_toggle = True
                pass
        else:
            pass

    def Enable_Sharpness(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        if _cam_class.sharpness_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetBoolValue("SharpnessEnable", c_bool(True)) #value of 2 is to activate Exposure Auto.
            if ret == 0:
                _cam_class.sharpness_toggle = True
                _cam_class.sharpness_btn_state()
                pass
            elif ret != 0:
                _cam_class.sharpness_toggle = False
                pass

        elif _cam_class.sharpness_toggle == True and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetBoolValue("SharpnessEnable", c_bool(False))
            if ret == 0:
                _cam_class.sharpness_toggle = False
                _cam_class.sharpness_btn_state()
                pass
            elif ret != 0:
                _cam_class.sharpness_toggle = True
                pass
        else:
            pass

    def Get_parameter_exposure(self):
        if True == self.b_open_device:
            stFloatParam_exposureTime = MVCC_FLOATVALUE()
            memset(byref(stFloatParam_exposureTime), 0, sizeof(MVCC_FLOATVALUE))
            ret = self.obj_cam.MV_CC_GetFloatValue("ExposureTime", stFloatParam_exposureTime)
            if ret != 0:
                self.exposure_time = 28
            elif ret == 0:
                self.exposure_time = stFloatParam_exposureTime.fCurValue

    def Get_parameter_framerate(self):
        if True == self.b_open_device:
            stFloatParam_FrameRate =  MVCC_FLOATVALUE()
            memset(byref(stFloatParam_FrameRate), 0, sizeof(MVCC_FLOATVALUE))
            ret = self.obj_cam.MV_CC_GetFloatValue("AcquisitionFrameRate", stFloatParam_FrameRate)
            if ret != 0:
                self.frame_rate = 1
            elif ret == 0:
                self.frame_rate = stFloatParam_FrameRate.fCurValue

    def Get_actual_framerate(self):
        actual_FrameRate =  MVCC_FLOATVALUE()
        memset(byref(actual_FrameRate), 0, sizeof(MVCC_FLOATVALUE))
        ret = self.obj_cam.MV_CC_GetFloatValue("ResultingFrameRate", actual_FrameRate)
        if ret != 0:
            return 1
        else:
            return actual_FrameRate.fCurValue


    def Get_parameter_gain(self):
        if True == self.b_open_device:
            stFloatParam_gain = MVCC_FLOATVALUE()
            memset(byref(stFloatParam_gain), 0, sizeof(MVCC_FLOATVALUE))
            ret = self.obj_cam.MV_CC_GetFloatValue("Gain", stFloatParam_gain)
            if ret != 0:
                self.gain = 0
            elif ret ==0:
                self.gain = stFloatParam_gain.fCurValue

    def Get_parameter_brightness(self):
        st_brightness =  MVCC_INTVALUE()
        memset(byref(st_brightness), 0, sizeof(MVCC_INTVALUE))
        ret = self.obj_cam.MV_CC_GetIntValue("Brightness", st_brightness)
        #print('ret Get Brightness: ', ret)
        if ret != 0:
            self.brightness = 255
        elif ret ==0:
            self.brightness = st_brightness.nCurValue
        #print(self.brightness)

    def Get_parameter_white(self):
        st_red_ratio = MVCC_INTVALUE()
        st_green_ratio = MVCC_INTVALUE()
        st_blue_ratio = MVCC_INTVALUE()

        memset(byref(st_red_ratio), 0, sizeof(MVCC_INTVALUE))
        memset(byref(st_green_ratio), 0, sizeof(MVCC_INTVALUE))
        memset(byref(st_blue_ratio), 0, sizeof(MVCC_INTVALUE))

        # ret = self.obj_cam.MV_CC_SetEnumValueByString("BalanceRatioSelector", "Red")
        # print(ret)
        # ret = self.obj_cam.MV_CC_SetBalanceRatioRed(int(4095))

        ret = self.obj_cam.MV_CC_GetBalanceRatioRed(st_red_ratio)
        #print('balance_red: ', ret)
        if ret != 0:
            self.red_ratio = 1024
        elif ret ==0:
            self.red_ratio = st_red_ratio.nCurValue
            #print(self.red_ratio)
        ret = self.obj_cam.MV_CC_GetBalanceRatioGreen(st_green_ratio)
        #print('balance_green: ', ret)
        if ret != 0:
            self.green_ratio = 1000
        elif ret ==0:
            self.green_ratio = st_green_ratio.nCurValue

        ret = self.obj_cam.MV_CC_GetBalanceRatioBlue(st_blue_ratio)
        if ret != 0:
            self.blue_ratio = 1024
        elif ret ==0:
            self.blue_ratio = st_blue_ratio.nCurValue

        # print('self.red_ratio, self.green_ratio, self.blue_ratio: ', self.red_ratio, self.green_ratio, self.blue_ratio)

    def Get_parameter_black_lvl(self):
        st_black_lvl =  MVCC_INTVALUE()
        memset(byref(st_black_lvl), 0, sizeof(MVCC_INTVALUE))
        ret = self.obj_cam.MV_CC_GetIntValue("BlackLevel", st_black_lvl)
        #print('ret Get Black Level: ', ret)
        if ret != 0:
            self.black_lvl = 0
        elif ret ==0:
            self.black_lvl = st_black_lvl.nCurValue

    def Get_parameter_sharpness(self):
        st_sharpness =  MVCC_INTVALUE()
        memset(byref(st_sharpness), 0, sizeof(MVCC_INTVALUE))
        ret = self.obj_cam.MV_CC_GetIntValue("Sharpness", st_sharpness)
        #print('ret Get Sharpness: ', ret)
        if ret != 0:
            self.sharpness = 0
        elif ret ==0:
            self.sharpness = st_sharpness.nCurValue

    def Set_parameter_exposure(self, exposureTime):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetFloatValue("ExposureTime",float(exposureTime))
            if ret != 0:
                _cam_class.revert_val_exposure = True
                pass

    def Set_parameter_gain(self, gain):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetFloatValue("Gain",float(gain))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_gain = True
                pass

    def Set_parameter_framerate(self, frameRate):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui  
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetFloatValue("AcquisitionFrameRate",float(frameRate))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_framerate = True
                pass


    def Set_parameter_brightness(self, brightness):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetIntValue("Brightness",int(brightness))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_gain = True
                pass

    def Set_parameter_red_ratio(self, ratio):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetBalanceRatioRed(int(ratio))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_red_ratio = True
                pass

    def Set_parameter_green_ratio(self, ratio):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetBalanceRatioGreen(int(ratio))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_green_ratio = True
                pass

    def Set_parameter_blue_ratio(self, ratio):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetBalanceRatioBlue(int(ratio))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_blue_ratio = True
                pass

    def Set_parameter_black_lvl(self, val):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetIntValue("BlackLevel",int(val))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_black_lvl = True
                pass

    def Set_parameter_sharpness(self, val):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_cam_conn.active_gui
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetIntValue("Sharpness",int(val))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_sharpness = True
                pass