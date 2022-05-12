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

from misc_module.TMS_file_save import cv_img_save, pil_img_save, PDF_img_save, PDF_img_list_save, np_to_PIL
from misc_module.os_create_folder import create_save_folder
# from misc_module.image_resize import img_resize_dim, opencv_img_resize, pil_img_resize, open_pil_img
from misc_module.tk_canvas_display import display_func, clear_display_func

from Hikvision_GUI import Hikvision_GUI
from Light_Connect import Light_Connect


import inspect
import ctypes
from ctypes import *

import threading
import msvcrt

# code_PATH = os.getcwd()
# sys.path.append(code_PATH + '\\MVS-Python\\MvImport')

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
    def __init__(self, obj_cam, st_device_ID = None, b_open_device=False, b_start_grabbing = False, h_thread_handle=None
        , b_thread_closed=False, st_frame_info=None, buf_cache=None, b_exit=False, buf_save_image=None
        , n_save_image_size=0, n_payload_size=0, frame_rate=1, exposure_time=28, gain=0, gain_mode = 0, exposure_mode = 0, framerate_mode = 0):

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

        self.__save_dir = os.path.join(os.environ['USERPROFILE'],  "TMS_Saved_Images")

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

        self.trigger_mode    = False

        self.trigger_src = 0 #values: 0, 1, 2, 3, 4, 7

        self.start_grabbing_event = threading.Event()
        self.start_grabbing_event.set()
        
        self.record_init = False
        self.video_file = None
        self.video_writer = None

        self.sq_frame_img_list = []
        self.sq_frame_save_list = []
        self.__sq_save_next_id_index = None
        #EXTERNAL SQ STROBE FRAME PARAMETER(S)

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

        self.__light_class =  None ### Class for Light Control Tool GUI. This is specifically for LC18 SQ and LC20 SQ
        self.__cam_class   =  None ### Class for Camera Control Tool GUI. To invoke class instances from Camera Class GUI.

    def load_gui_class(self, light_class, cam_class):
        self.__light_class = light_class
        self.__cam_class   = cam_class

    def check_gui_class(self):
        def check_cam_class(obj):
            try:
                if type(obj.__class__) == type(Hikvision_GUI):
                    if obj.__class__.__name__ == Hikvision_GUI.__name__:
                        return True
                return False
            except Exception:
                return False

        def check_light_class(obj):
            try:
                if type(obj.__class__) == type(Light_Connect):
                    if obj.__class__.__name__ == Light_Connect.__name__:
                        return True
                return False
            except Exception:
                return False

        if True == check_light_class(self.__light_class) and True == check_cam_class(self.__cam_class):
            return True

        return False

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
        if self.check_gui_class() == False:
            raise Exception("Please load the 'light_class' and 'cam_class' using 'load_gui_class' class-function " 
                + "before attempting to connect to the camera device!\n\n"
                + "'light_class' must be a <class 'Light_Connect.Light_Connect'> class object\n"
                + "'cam_class' must be a <class 'Hikvision_GUI.Hikvision_GUI'> class object.")

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

        return 1 ### If not 0 it means there is an error

    def Set_Pixel_Format(self, hex_val):
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
                self.__cam_class.entry_red_ratio['state'] = 'disable'
                self.__cam_class.entry_green_ratio['state'] = 'disable'
                self.__cam_class.entry_blue_ratio['state'] = 'disable'
                self.__cam_class.btn_auto_white['image'] = self.__cam_class.toggle_OFF_button_img
                self.__cam_class.btn_auto_white['state'] = 'disable'
                self.__cam_class.auto_white_toggle = False

            elif True == self.Pixel_Format_Color(pixel_str_id):
                self.__cam_class.btn_auto_white['state'] = 'normal'
                self.Init_Balance_White_Mode()
                self.__cam_class.white_balance_btn_state()
                if self.__cam_class.auto_white_handle is not None:
                    self.__cam_class.stop_auto_white()
                    self.__cam_class.get_parameter_white()
                elif self.__cam_class.auto_white_handle is None:
                    self.__cam_class.get_parameter_white()
                pass
        else:
            self.Get_Pixel_Format()
            pixel_str_id = self.Pixel_Format_Str_ID(hex_val)
            Error_Msgbox(message = 'Current Camera Does Not Support Pixel Format: ' + pixel_str_id, title = 'Pixel Format Error', message_anchor = 'w')
            pass

        return setpixel_ret


    def Get_Pixel_Format(self):
        st_pixel_format = MVCC_ENUMVALUE()
        memset(byref(st_pixel_format), 0, sizeof(MVCC_ENUMVALUE))
        ret = self.obj_cam.MV_CC_GetEnumValue("PixelFormat", st_pixel_format)

        pixel_format_int = st_pixel_format.nCurValue
        self.__cam_class.get_pixel_format(pixel_format_int) #Update the HikVision Camera GUI
        # print(int2Hex(pixel_format_int))

        pixel_str_id = self.Pixel_Format_Str_ID(pixel_format_int)
        # print(pixel_str_id)

        if True == self.Pixel_Format_Mono(pixel_str_id):
            # print('Mono Detected')
            self.__cam_class.entry_red_ratio['state'] = 'disable'
            self.__cam_class.entry_green_ratio['state'] = 'disable'
            self.__cam_class.entry_blue_ratio['state'] = 'disable'
            self.__cam_class.btn_auto_white['image'] = self.__cam_class.toggle_OFF_button_img
            self.__cam_class.btn_auto_white['state'] = 'disable'
            # print('Mono Detected')
            self.__cam_class.auto_white_toggle = False

        elif True == self.Pixel_Format_Color(pixel_str_id):
            self.__cam_class.btn_auto_white['state'] = 'normal'
            # print('Color Detected')
            self.Init_Balance_White_Mode()
            self.__cam_class.white_balance_btn_state()
            if self.__cam_class.auto_white_handle is not None:
                self.__cam_class.stop_auto_white()
                self.__cam_class.get_parameter_white()
            elif self.__cam_class.auto_white_handle is None:
                self.__cam_class.get_parameter_white()
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
        stBool = c_bool(False)
        ret =self.obj_cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", byref(stBool))
        if ret != 0:
            print ("get acquisition frame rate enable fail! ret[0x%x]" % ret)

        self.__cam_class.framerate_toggle = stBool.value

    def Init_Exposure_Mode(self):
        st_exposure_mode = MVCC_ENUMVALUE()
        memset(byref(st_exposure_mode), 0, sizeof(MVCC_ENUMVALUE))
        ret = self.obj_cam.MV_CC_GetEnumValue("ExposureAuto", st_exposure_mode)

        self.exposure_mode = st_exposure_mode.nCurValue
        if self.exposure_mode == 2: #2 is continuous mode
            self.__cam_class.auto_exposure_toggle = True
        #elif self.exposure_mode == 1: #1 is once mode, #0 is off mode
        else:
            self.__cam_class.auto_exposure_toggle = False

    def Init_Gain_Mode(self):
        st_gain_mode = MVCC_ENUMVALUE()
        memset(byref(st_gain_mode), 0, sizeof(MVCC_ENUMVALUE))
        ret = self.obj_cam.MV_CC_GetEnumValue("GainAuto", st_gain_mode)
        self.gain_mode = st_gain_mode.nCurValue
        if self.gain_mode == 2: #2 is continuous mode
            self.__cam_class.auto_gain_toggle = True
        #elif self.gain_mode == 1: #1 is once mode, #0 is off mode
        else:
            self.__cam_class.auto_gain_toggle = False

    def Init_Balance_White_Mode(self):
        st_white_mode = MVCC_ENUMVALUE()
        memset(byref(st_white_mode), 0, sizeof(MVCC_ENUMVALUE))
        ret = self.obj_cam.MV_CC_GetEnumValue("BalanceWhiteAuto", st_white_mode)
        self.white_mode = st_white_mode.nCurValue
        if self.white_mode == 1: #1 is continuous mode
            self.__cam_class.auto_white_toggle = True
        #elif self.white_mode == 2: #2 is once mode, #0 is off mode
        else:
            self.__cam_class.auto_white_toggle = False

    def Init_Black_Level_Mode(self):
        stBool = c_bool(False)
        ret =self.obj_cam.MV_CC_GetBoolValue("BlackLevelEnable", byref(stBool))
        if ret != 0:
            print ("get acquisition black level enable fail! ret[0x%x]" % ret)

        self.__cam_class.black_lvl_toggle = stBool.value

    def Init_Sharpness_Mode(self):
        stBool = c_bool(False)
        ret =self.obj_cam.MV_CC_GetBoolValue("SharpnessEnable", byref(stBool))
        #print(ret)
        if ret != 0:
            print ("get acquisition sharpness enable fail! ret[0x%x]" % ret)

        self.__cam_class.sharpness_toggle = stBool.value

    def Start_grabbing(self):
        ret = None
        # print(self.__light_class.hmap_light_gui['SQ'].hmap_sq_param['frame_num']['value'])
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

            self.Normal_Mode_display_clear()
            self.SQ_Mode_display_clear()
                
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

        self.sq_frame_img_list *= 0

        self.obj_cam.MV_CC_DestroyHandle()
        #print(self.obj_cam)
        print ("close device successfully!")

    def Set_trigger_mode(self,strMode):
        if True == self.b_open_device:
            if "continuous" == strMode: 
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode",0)
                self.trigger_mode = False

                if ret != 0:
                    Error_Msgbox(message = 'Set Continuous Mode fail!\nError('+ self.To_hex_str(ret)+')', title = 'Camera Mode Error', message_anchor = 'w')

            if "triggermode" == strMode:
                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode",1)
                if ret != 0:
                    Error_Msgbox(message = 'Set Trigger Mode fail!\nError('+ self.To_hex_str(ret)+')', title = 'Camera Mode Error', message_anchor = 'w')
                    self.trigger_mode = False

                elif ret == 0:
                    self.trigger_mode = True

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
        light_gui = self.__light_class.hmap_light_gui

        # ch:创建显示的窗口 | en:Create the window for display
        stFrameInfo = MV_FRAME_OUT_INFO_EX()  
        img_buff = None
        self.rgb_type = False
        self.mono_type = False

        trigger_mode = self.trigger_mode
        ext_sq_fr_init = False

        while not self.start_grabbing_event.isSet():
            start_time = time.time()
            trigger_mode = self.trigger_mode

            ret = self.obj_cam.MV_CC_GetOneFrameTimeout(byref(self.buf_cache), self.n_payload_size, stFrameInfo, 1000) #If Set to Trigger mode ret != 0 until trigger once is pressed.

            ################################################################
            # print('Get Frame Error: ', self.To_hex_str(ret))
            stop_time = time.time()
            elapsed_time = stop_time - start_time
            ideal_delay = np.divide(1, self.Get_actual_framerate())
            actual_delay = ideal_delay - elapsed_time
            if actual_delay < 0:
                actual_delay = 0
            self.start_grabbing_event.wait(actual_delay)
            del start_time, stop_time, elapsed_time, ideal_delay, actual_delay

            if ret == 0:
                #获取到图像的时间开始节点获取到图像的时间开始节点
                self.st_frame_info = stFrameInfo
                # print(stFrameInfo.nFrameCounter)
                size = np.multiply(self.st_frame_info.nWidth, self.st_frame_info.nHeight)

                self.n_save_image_size = int(np.multiply(size, 3)) + 2048

                if img_buff is None:
                    img_buff = (c_ubyte * self.n_save_image_size)()

            else:
                if trigger_mode == True and ext_sq_fr_init == True: #SQ Frame Function already started but not complete.
                    sq_bool = False
                    if True == self.SQ_Connect_Bool('SQ') and False == self.SQ_Connect_Bool('LC20'):
                        max_fr = light_gui['SQ'].hmap_sq_param['frame_num']['value']
                        sq_bool = True
                    elif True == self.SQ_Connect_Bool('LC20') and True == self.SQ_Connect_Bool('SQ'):
                        max_fr = light_gui['LC20'].hmap_sq_param['frame_num']['value']
                        sq_bool = True

                    if sq_bool == True:
                        if len(self.sq_frame_img_list) < max_fr:
                            self.External_SQ_Fr_Disp()
                            self.Auto_Save_SQ_Frame()

                    del sq_bool

                    ext_sq_fr_init = False


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
                if self.__cam_class.flip_img_bool == True:
                    self.numArray = imutils.rotate(numArray, 180)
                else:
                    self.numArray = numArray

                # print(self.numArray)
                self.mono_type = True
                self.rgb_type = False


            # RGB直接显示
            elif PixelType_Gvsp_RGB8_Packed == self.st_frame_info.enPixelType:
                numArray = self.Color_numpy(self.buf_cache,self.st_frame_info.nWidth,self.st_frame_info.nHeight)
                if self.__cam_class.flip_img_bool == True:
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
                if self.__cam_class.flip_img_bool == True:
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
                numArray = self.Color_numpy(img_buff,self.st_frame_info.nWidth, self.st_frame_info.nHeight)
                if self.__cam_class.flip_img_bool == True:
                    self.numArray = imutils.rotate(numArray, 180)
                else:
                    self.numArray = numArray

                self.mono_type = False
                self.rgb_type = True

                #print('color')
                ################################################################

            if self.__cam_class.capture_img_status.get() == 1:
                if self.freeze_numArray is None:
                    self.freeze_numArray = self.numArray

            elif self.__cam_class.capture_img_status.get() == 0:
                self.freeze_numArray = None

            # stop_time = time.time()
            # elapsed_time = stop_time - start_time
            # print('FPS: ', 1/elapsed_time)

            if trigger_mode == True:
                sq_bool = False
                if True == self.SQ_Connect_Bool('SQ') and False == self.SQ_Connect_Bool('LC20'):
                    max_fr = light_gui['SQ'].hmap_sq_param['frame_num']['value']
                    sq_bool = True
                elif True == self.SQ_Connect_Bool('LC20') and True == self.SQ_Connect_Bool('SQ'):
                    max_fr = light_gui['LC20'].hmap_sq_param['frame_num']['value']
                    sq_bool = True

                if sq_bool == True:
                    if ext_sq_fr_init == False:
                        self.sq_frame_img_list *= 0
                        # print('SQ Frame Clear: ', len(self.sq_frame_img_list))
                        ext_sq_fr_init = True

                    elif ext_sq_fr_init == True:
                        pass
                    
                    ## len(list) empty = 0, sq_fr_arr[0] is the frame num: 1 - 10
                    self.sq_frame_img_list.append(self.numArray)
                    # print('Sq Frame: ',len(self.sq_frame_img_list))
                    if len(self.sq_frame_img_list) ==  max_fr:
                        self.External_SQ_Fr_Disp()
                        self.Auto_Save_SQ_Frame()
                        ext_sq_fr_init = False

                    elif len(self.sq_frame_img_list) > max_fr:
                        # print('SQ Frame Overflow')
                        # print('Reset list')
                        ext_sq_fr_init = False

                del sq_bool

            if self.__cam_class.trigger_auto_save_bool.get() == 1 and trigger_mode == True:
                self.Normal_Mode_Save(self.numArray, self.freeze_numArray, auto_save = True, trigger_mode = trigger_mode)

            elif self.__cam_class.trigger_auto_save_bool.get() == 0 and trigger_mode == False:
                self.Normal_Mode_Save(self.numArray, self.freeze_numArray, auto_save = False, trigger_mode = trigger_mode)


            # stop_time = time.time()
            # elapsed_time = stop_time - start_time
            # print('FPS: ', 1/elapsed_time)

            if self.__cam_class.record_bool == False:
                self.record_init = False

            elif self.__cam_class.record_bool == True:
                if self.video_record_thread is None:
                    self.video_record_event.clear()
                    isColor = False
                    if len(self.numArray.shape) == 3:
                        isColor = True 

                    self.video_record_thread = threading.Thread(target=self.OpenCV_Record_Func, args=(self.st_frame_info.nWidth,self.st_frame_info.nHeight, isColor), daemon = True)
                    print('Record Started')
                    self.video_record_thread.start()

            # self.All_Mode_Cam_Disp()

            # stop_time = time.time()
            # elapsed_time = stop_time - start_time
            # print('FPS: ', 1/elapsed_time)

            self.All_Mode_Cam_Disp()

            if self.b_exit == True:
                #print('breaking')
                break

    def SQ_Connect_Bool(self, model_str):
        light_gui   = self.__light_class.hmap_light_gui
        str_list = ['SQ', 'LC20']

        if model_str in str_list:
            if self.__light_class.light_conn_status == True:
                if self.__light_class.fw_model_sel == model_str:
                    if (self.trigger_src == 0 and light_gui[model_str].updating_bool == False):
                        return True
                return False

            return False

        return False

    def OpenCV_Record_Init(self, frame_w, frame_h, isColor):
        if self.record_init == False:
            if self.frame_queue is not None:
                del self.frame_queue
                self.frame_queue = None

            save_folder = create_save_folder(folder_dir = self.__save_dir)
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

    def OpenCV_Record_Func(self, frame_w, frame_h, isColor): #(self, resultant_fps):
        video_size = self.__cam_class.rec_setting_param[1]
        resize_w = int(np.multiply(frame_w, video_size))
        resize_h = int(np.multiply(frame_h, video_size))

        resultant_fps = self.OpenCV_Record_Init(resize_w, resize_h, isColor)

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
                                    self.__cam_class.time_lapse_var.set(time_convert(self.elapse_time))

                                if self.frame_queue.qsize() > 0:
                                    # print('Memory Tracker: ', self.frame_queue.qsize(), psutil.virtual_memory().percent)
                                    if self.video_write_thread is None:
                                        self.video_write_thread = threading.Thread(target=self.OpenCV_video_write_batch, args=(None,), daemon = True)
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
                                self.__cam_class.time_lapse_var.set(time_convert(self.elapse_time))


                            if self.frame_queue.qsize() > 0:
                                # print('Memory Tracker: ', self.frame_queue.qsize(), psutil.virtual_memory().percent)
                                if self.video_write_thread is None:
                                    self.video_write_thread = threading.Thread(target=self.OpenCV_video_write_batch, args=(None,), daemon = True)
                                    self.video_write_thread.start()

                    if self.b_start_grabbing == False:
                        time_update = time.time()
                        self.pause_record_duration = int(time_update - self.start_record_time) - self.elapse_time
                        # print('Pause: ', self.pause_record_duration)

                else:
                    self.__cam_class.record_stop_func()
                    self.record_warning_flag = True
                    

            elif self.record_init == False:
                self.__cam_class.record_btn_1['state'] = 'disable'

                if self.__queue_start == True:
                    #To Flush All the contents in frame Queue
                    if self.video_write_thread is None:
                        self.video_write_thread = threading.Thread(target=self.OpenCV_video_write_full, daemon = True)
                        self.video_write_thread.start()

                elif self.__queue_start == False:
                    self.video_record_event.set()

            self.video_record_event.wait(delay)

            # print(self.frame_queue.qsize())
        del self.video_record_thread
        self.video_record_thread = None

        if self.__cam_class.cam_conn_status == True:
            self.__cam_class.record_setting_btn['state'] = 'normal'
            if self.__cam_class.cam_mode_var.get() == 'continuous':
                self.__cam_class.record_btn_1['state'] = 'normal'
            self.__cam_class.time_lapse_var.set('')

        elif self.__cam_class.cam_conn_status == False:
            self.__cam_class.record_btn_1['state'] = 'disable'
            self.__cam_class.record_setting_btn['state'] = 'disable'
            self.__cam_class.time_lapse_var.set('')

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


    def OpenCV_video_write_full(self):
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


    def OpenCV_video_write_batch(self, batch_num = None):
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
        self.__cam_class.clear_display_GUI_2()

        self.SQ_frame_display(self.sq_frame_img_list)

        # print("Save: ", self.sq_frame_save_list)

        self.__cam_class.SQ_fr_popout_load_list(sq_frame_img_list = self.sq_frame_img_list)
        self.__cam_class.SQ_fr_popout_disp_func(sq_frame_img_list = self.sq_frame_img_list)

        self.__cam_class.SQ_fr_sel.bind('<<ComboboxSelected>>', 
            lambda event: self.__cam_class.SQ_fr_popout_disp_func(sq_frame_img_list = self.sq_frame_img_list))

        self.__cam_class.cam_sq_frame_cache *= 0
        self.__cam_class.cam_sq_frame_cache = self.sq_frame_img_list[:]

    def set_custom_save_param(self, folder_name, file_name, overwrite_bool = False):
        self.__custom_save_folder = str(folder_name)
        self.__custom_save_name = str(file_name)
        self.__custom_save_overwrite = overwrite_bool

    def Normal_Mode_Save(self, arr_1, arr_2 = None, auto_save = False, trigger_mode = False): #Normal Camera Mode Save
        img_arr = arr_1
        if isinstance(arr_2, np.ndarray) == True:
            img_arr = arr_2

        if auto_save == False:
            if True == self.__validate_rgb_img(img_arr) and False == self.__validate_mono_img(img_arr):
                if self.b_save == True and self.custom_b_save == False:
                    img_format = self.__cam_class.save_img_format_sel.get()
                    time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                    # time_id = str(datetime.now().strftime("%Y-%m-%d"))
                    save_folder = create_save_folder(folder_dir = self.__save_dir)

                    if trigger_mode == True:
                        sub_folder = create_save_folder(save_folder + '\\Trigger--' + time_id, duplicate = True)
                    else:
                        sub_folder = create_save_folder(save_folder + '\\Camera--' + time_id, duplicate = True)

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
                    img_format = self.__cam_class.save_img_format_sel.get()
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
                    img_format = self.__cam_class.save_img_format_sel.get()
                    time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                    # time_id = str(datetime.now().strftime("%Y-%m-%d"))
                    save_folder = create_save_folder(folder_dir = self.__save_dir)

                    if self.trigger_mode == True:
                        sub_folder = create_save_folder(save_folder + '\\Trigger--' + time_id, duplicate = True)
                    else:
                        sub_folder = create_save_folder(save_folder + '\\Camera--' + time_id, duplicate = True)

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
                    img_format = self.__cam_class.save_img_format_sel.get()
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

                self.__cam_class.clear_img_save_msg_box()


        elif auto_save == True:
            if True == self.__validate_rgb_img(img_arr) and False == self.__validate_mono_img(img_arr):
                img_format = self.__cam_class.save_img_format_sel.get()
                time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                # time_id = str(datetime.now().strftime("%Y-%m-%d"))

                save_folder = create_save_folder(folder_dir = self.__save_dir)
                sub_folder = create_save_folder(save_folder + '\\Trigger--' + time_id, duplicate = True)

                if str(img_format) == '.pdf':
                    _, id_index = PDF_img_save(sub_folder, img_arr, 'Colour', ch_split_bool = False)
                else:
                    _, id_index = cv_img_save(sub_folder, img_arr, 'Colour', str(img_format))
                    cv_img_save(sub_folder, img_arr[:,:,0], 'Red-Ch' + '--id{}'.format(id_index), str(img_format), overwrite = True)
                    cv_img_save(sub_folder, img_arr[:,:,1], 'Green-Ch' + '--id{}'.format(id_index), str(img_format), overwrite = True)
                    cv_img_save(sub_folder, img_arr[:,:,2], 'Blue-Ch' + '--id{}'.format(id_index), str(img_format), overwrite = True)

            elif False == self.__validate_rgb_img(img_arr) and True == self.__validate_mono_img(img_arr):
                img_format = self.__cam_class.save_img_format_sel.get()
                time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                # time_id = str(datetime.now().strftime("%Y-%m-%d"))
                save_folder = create_save_folder(folder_dir = self.__save_dir)
                sub_folder = create_save_folder(save_folder + '\\Trigger--' + time_id, duplicate = True)

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
        if self.trigger_mode == True:
            if isinstance(self.freeze_numArray, np.ndarray) == True:
                img_arr = self.freeze_numArray
            else:
                img_arr = self.numArray

            self.Normal_Mode_Save(arr_1 = img_arr, trigger_mode = self.trigger_mode)


    def All_Mode_Cam_Disp(self):
        if self.rgb_type == True and self.mono_type == False:
            if self.__cam_class.popout_status == False:
                if self.freeze_numArray is None:
                    self.RGB_display(self.numArray)
                    self.SQ_live_display(self.numArray)

                elif self.freeze_numArray is not None:
                    self.RGB_display(self.freeze_numArray)
                    self.SQ_live_display(self.freeze_numArray)

                self.disp_clear_ALL_status = False

            elif self.__cam_class.popout_status == True:
                if self.disp_clear_ALL_status == False:
                    self.Normal_Mode_display_clear()
                    self.SQ_Mode_display_clear()
                    self.disp_clear_ALL_status = True
                
                if self.freeze_numArray is None:
                    self.popout_display(self.numArray)
                elif self.freeze_numArray is not None:
                    self.popout_display(self.freeze_numArray)


        elif self.rgb_type == False and self.mono_type == True:
            if self.__cam_class.popout_status == False:
                if self.freeze_numArray is None:
                    self.Mono_display(self.numArray)
                    self.SQ_live_display(self.numArray)

                elif self.freeze_numArray is not None:
                    self.Mono_display(self.freeze_numArray)
                    self.SQ_live_display(self.freeze_numArray)

                self.disp_clear_ALL_status = False

            elif self.__cam_class.popout_status == True:
                if self.disp_clear_ALL_status == False:
                    self.Normal_Mode_display_clear()
                    self.SQ_Mode_display_clear()
                    self.disp_clear_ALL_status = True
                
                if self.freeze_numArray is None:
                    self.popout_display(self.numArray)
                elif self.freeze_numArray is not None:
                    self.popout_display(self.freeze_numArray)


    def RGB_display(self, img_arr):
        #Display for Normal Camera Mode
        if True == self.__validate_rgb_img(img_arr):
            try:
                display_func(self.__cam_class.cam_display_rgb, img_arr, 'img')
                display_func(self.__cam_class.cam_display_R, img_arr[:,:,0], 'img')
                display_func(self.__cam_class.cam_display_G, img_arr[:,:,1], 'img')
                display_func(self.__cam_class.cam_display_B, img_arr[:,:,2], 'img')
            
            except(tk.TclError):
                pass

    def Mono_display(self, img_arr):
        #Display for Normal Camera Mode
        if True == self.__validate_mono_img(img_arr):
            try:
                display_func(self.__cam_class.cam_display_rgb, img_arr, 'img')
                
            except(tk.TclError):
                pass

    def Normal_Mode_display_clear(self):
        #Clear Display for Normal Camera Mode
        try:
            clear_display_func(self.__cam_class.cam_display_rgb
                , self.__cam_class.cam_display_R
                , self.__cam_class.cam_display_G
                , self.__cam_class.cam_display_B)
        except(tk.TclError):
            pass
        

    def popout_display(self, img_arr):
        if self.rgb_type == False and self.mono_type == True:
            self.__cam_class.popout_var_mode = 'original'
            try:
                self.__cam_class.sel_R_btn['state'] = 'disable'
                self.__cam_class.sel_G_btn['state'] = 'disable'
                self.__cam_class.sel_B_btn['state'] = 'disable'
            except (AttributeError, tk.TclError):
                pass

        elif self.rgb_type == True and self.mono_type == False:
            try:
                self.__cam_class.sel_R_btn['state'] = 'normal'
                self.__cam_class.sel_G_btn['state'] = 'normal'
                self.__cam_class.sel_B_btn['state'] = 'normal'
            except (AttributeError, tk.TclError):
                pass

        try:
            self.__cam_class.popout_cam_disp_func(img_arr)
        except(tk.TclError):
            pass


    def SQ_live_display(self, img_arr):
        #Display for SQ Camera Mode
        if True == self.__validate_rgb_img(img_arr) or True == self.__validate_mono_img(img_arr):
            try:
                display_func(self.__cam_class.cam_disp_sq_live, img_arr, 'img')
            
            except(tk.TclError):
                pass

    def SQ_Mode_display_clear(self):
        try:
            clear_display_func(self.__cam_class.cam_disp_sq_live)

        except(tk.TclError):
            pass

    def SQ_frame_display(self, img_data):
        tk_sq_disp_list = self.__cam_class.tk_sq_disp_list
        # print(tk_sq_disp_list)
        self.sq_frame_save_list *=0

        if type(img_data) == list:
            if len(img_data) > 0:
                for i, img_arr in enumerate(img_data):

                    try:
                        display_func(tk_sq_disp_list[i], img_arr, 'img')
                        self.sq_frame_save_list.append(img_arr)
                    except(tk.TclError):
                        pass

                if self.rgb_type == True and self.mono_type == False:
                    self.RGB_display(img_data[-1])
                    self.SQ_live_display(img_data[-1])

                elif self.rgb_type == False and self.mono_type == True:
                    self.Mono_display(img_data[-1])
                    self.SQ_live_display(img_data[-1])


    def Save_SQ_Frame(self):
        if len(self.sq_frame_save_list) != 0:
            img_format = self.__cam_class.save_img_format_sel.get()
            save_folder = create_save_folder(folder_dir = self.__save_dir)

            frame_index = 1
            pdf_img_list = []

            if len(self.sq_frame_save_list) > 0:
                time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                # time_id = str(datetime.now().strftime("%Y-%m-%d"))
                sub_folder = create_save_folder(save_folder + '\\SQ-Frames--' + time_id, duplicate = True)

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
        if self.__cam_class.SQ_auto_save_bool.get() == 1:
            img_format = self.__cam_class.save_img_format_sel.get()
            save_folder = create_save_folder(folder_dir = self.__save_dir)
            frame_index = 1
            pdf_img_list = []

            if len(self.sq_frame_save_list) > 0:
                # time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                time_id = str(datetime.now().strftime("%Y-%m-%d"))
                sub_folder = create_save_folder(save_folder + '\\SQ-Frames-(auto-save)--' + time_id, duplicate = False)

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

        elif self.__cam_class.SQ_auto_save_bool.get() == 0:
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
        if self.__cam_class.auto_exposure_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("ExposureAuto", 2) #value of 2 is to activate Exposure Auto.
            if ret == 0:
                #print('Auto Exposure ON')
                self.__cam_class.btn_auto_exposure['image'] = self.__cam_class.toggle_ON_button_img
                self.__cam_class.entry_exposure['state'] = 'disabled'
                self.__cam_class.auto_exposure_toggle = True

                pass
            elif ret != 0:
                self.__cam_class.auto_exposure_toggle = False
                pass

        elif self.__cam_class.auto_exposure_toggle == True and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("ExposureAuto", 0)
            if ret == 0:
                #print('Auto Exposure OFF')                
                self.__cam_class.btn_auto_exposure['image'] = self.__cam_class.toggle_OFF_button_img
                self.__cam_class.entry_exposure['state'] = 'normal'
                self.__cam_class.auto_exposure_toggle = False
                pass
            elif ret != 0:
                self.__cam_class.auto_exposure_toggle = True
                pass
        else:
            pass

    def Auto_Gain(self):
        if self.__cam_class.auto_gain_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("GainAuto", 2) #value of 2 is to activate Exposure Auto.
            if ret == 0:
                #print('Auto Gain ON')
                
                self.__cam_class.btn_auto_gain['image'] = self.__cam_class.toggle_ON_button_img
                self.__cam_class.entry_gain['state'] = 'disabled'
                self.__cam_class.auto_gain_toggle = True
                pass
            elif ret != 0:
                self.__cam_class.auto_gain_toggle = False
                pass

        elif self.__cam_class.auto_gain_toggle == True and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("GainAuto", 0)
            if ret == 0:
                #print('Auto Gain OFF')
                
                self.__cam_class.btn_auto_gain['image'] = self.__cam_class.toggle_OFF_button_img
                self.__cam_class.entry_gain['state'] = 'normal'
                self.__cam_class.auto_gain_toggle = False
                pass
            elif ret != 0:
                self.__cam_class.auto_gain_toggle = True
                pass
        else:
            pass

    def Enable_Framerate(self):
        if self.__cam_class.framerate_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetBoolValue("AcquisitionFrameRateEnable", c_bool(True)) #value of 2 is to activate Exposure Auto.
            #print('Enabled', ret)
            if ret == 0:
                #print('Framerate Enabled')
                
                self.__cam_class.btn_enable_framerate['image'] = self.__cam_class.toggle_ON_button_img
                self.__cam_class.entry_framerate['state'] = 'normal'
                self.__cam_class.framerate_toggle = True

                pass
            elif ret != 0:
                self.__cam_class.framerate_toggle = False
                pass

        elif self.__cam_class.framerate_toggle == True and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetBoolValue("AcquisitionFrameRateEnable", c_bool(False))
            #print('Disabled', ret)
            if ret == 0:
                #print('Framerate Disabled')
                
                self.__cam_class.btn_enable_framerate['image'] = self.__cam_class.toggle_OFF_button_img
                self.__cam_class.entry_framerate['state'] = 'disabled'
                self.__cam_class.framerate_toggle = False
                pass
            elif ret != 0:
                self.__cam_class.framerate_toggle = True
                pass
        else:
            pass

    def Auto_White(self):
        if self.__cam_class.auto_white_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("BalanceWhiteAuto", 1)
            if ret == 0:
                # print('Auto White ON')
                self.__cam_class.auto_white_toggle = True
                self.__cam_class.white_balance_btn_state()
                pass
            elif ret != 0:
                self.__cam_class.auto_white_toggle = False
                pass

        elif self.__cam_class.auto_white_toggle == True and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("BalanceWhiteAuto", 0)
            if ret == 0:
                # print('Auto White OFF')
                self.__cam_class.auto_white_toggle = False
                self.__cam_class.white_balance_btn_state()
                pass
            elif ret != 0:
                self.__cam_class.auto_white_toggle = True
                pass
        else:
            pass

    def Enable_Blacklevel(self):
        if self.__cam_class.black_lvl_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetBoolValue("BlackLevelEnable", c_bool(True)) #value of 2 is to activate Exposure Auto.
            if ret == 0:
                self.__cam_class.black_lvl_toggle = True
                self.__cam_class.black_lvl_btn_state()
                pass
            elif ret != 0:
                self.__cam_class.black_lvl_toggle = False
                pass

        elif self.__cam_class.black_lvl_toggle == True and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetBoolValue("BlackLevelEnable", c_bool(False))
            if ret == 0:
                self.__cam_class.black_lvl_toggle = False
                self.__cam_class.black_lvl_btn_state()
                pass
            elif ret != 0:
                self.__cam_class.black_lvl_toggle = True
                pass
        else:
            pass

    def Enable_Sharpness(self):
        if self.__cam_class.sharpness_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetBoolValue("SharpnessEnable", c_bool(True)) #value of 2 is to activate Exposure Auto.
            if ret == 0:
                self.__cam_class.sharpness_toggle = True
                self.__cam_class.sharpness_btn_state()
                pass
            elif ret != 0:
                self.__cam_class.sharpness_toggle = False
                pass

        elif self.__cam_class.sharpness_toggle == True and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetBoolValue("SharpnessEnable", c_bool(False))
            if ret == 0:
                self.__cam_class.sharpness_toggle = False
                self.__cam_class.sharpness_btn_state()
                pass
            elif ret != 0:
                self.__cam_class.sharpness_toggle = True
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
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetFloatValue("ExposureTime",float(exposureTime))
            if ret != 0:
                self.__cam_class.revert_val_exposure = True
                pass

    def Set_parameter_gain(self, gain):
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetFloatValue("Gain",float(gain))
            #print(ret)
            if ret != 0:
                self.__cam_class.revert_val_gain = True
                pass

    def Set_parameter_framerate(self, frameRate):
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetFloatValue("AcquisitionFrameRate",float(frameRate))
            #print(ret)
            if ret != 0:
                self.__cam_class.revert_val_framerate = True
                pass


    def Set_parameter_brightness(self, brightness):
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetIntValue("Brightness",int(brightness))
            #print(ret)
            if ret != 0:
                self.__cam_class.revert_val_gain = True
                pass

    def Set_parameter_red_ratio(self, ratio):
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetBalanceRatioRed(int(ratio))
            #print(ret)
            if ret != 0:
                self.__cam_class.revert_val_red_ratio = True
                pass

    def Set_parameter_green_ratio(self, ratio):
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetBalanceRatioGreen(int(ratio))
            #print(ret)
            if ret != 0:
                self.__cam_class.revert_val_green_ratio = True
                pass

    def Set_parameter_blue_ratio(self, ratio):
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetBalanceRatioBlue(int(ratio))
            #print(ret)
            if ret != 0:
                self.__cam_class.revert_val_blue_ratio = True
                pass

    def Set_parameter_black_lvl(self, val):
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetIntValue("BlackLevel",int(val))
            #print(ret)
            if ret != 0:
                self.__cam_class.revert_val_black_lvl = True
                pass

    def Set_parameter_sharpness(self, val):
        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetIntValue("Sharpness",int(val))
            #print(ret)
            if ret != 0:
                self.__cam_class.revert_val_sharpness = True
                pass