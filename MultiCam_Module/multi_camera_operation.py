import os
from os import path
import sys

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
from misc_module.tk_canvas_display import display_func, clear_display_func

import inspect
import ctypes
from ctypes import *

import threading
import msvcrt

# code_PATH = os.getcwd()
# sys.path.append(code_PATH + '\\MVS-Python\\MvImport')

from MvCameraControl_class import *

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

class MultiCameraOp():
    def __init__(self,obj_cam,st_device_ID,n_connect_num=0,b_open_device=False,b_start_grabbing = False,h_thread_handle=None,\
                b_thread_closed=False,st_frame_info=None,buf_cache=None,b_exit=False,buf_save_image=None,\
                n_save_image_size=0,n_payload_size=0,frame_rate=1,exposure_time=28,gain=0, gain_mode = 0, exposure_mode = 0, framerate_mode = 0):

        self.obj_cam = obj_cam
        self.st_device_ID = st_device_ID
        self.n_connect_num = n_connect_num
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
        self.display_status = True

        self.trigger_mode = False
        
        self.bool_mode_switch = False #UPDATED 18-8-2021

        self.trigger_src = 0 #values: 0, 1, 2, 3, 4, 7

        self.nConnectionNum = None

        self.start_grabbing_event = threading.Event()
        self.start_grabbing_event.set()

        self.cam_display_thread = None
        self.cam_display_event = threading.Event()
        self.cam_display_event.set()
        self.cam_display_bool = False

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

    def Open_device(self):
        if False == self.b_open_device:
            # ch:选择设备并创建句柄 | en:Select device and create handle
            self.nConnectionNum = int(self.n_connect_num)
            
            #print('self.st_device_ID: ',self.st_device_ID)
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

            if None == self.buf_cache:
                self.buf_cache = (c_ubyte * self.n_payload_size)()
                #print(self.buf_cache)
            # ch:设置触发模式为off | en:Set trigger mode as off
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
            #print(MV_TRIGGER_MODE_OFF)
            if ret != 0:
                print ("set trigger mode fail! ret[0x%x]" % ret)

            # from main_GUI import main_GUI
            # print(main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum])
            # print(main_GUI.class_multi_cam_conn.toggle_ON_button_img)
            self.Init_Framerate_Mode()

            self.Init_Exposure_Mode()

            self.Init_Gain_Mode()

            self.Init_Balance_White_Mode()

            self.Init_Black_Level_Mode()

            self.Init_Sharpness_Mode()

            self.Get_Pixel_Format()
            
            return 0

    def Set_Pixel_Format(self, hex_val):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        self.Normal_Mode_display_clear()

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
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

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
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        stBool = c_bool(False)
        ret =self.obj_cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", byref(stBool))
        if ret != 0:
            print ("get acquisition frame rate enable fail! ret[0x%x]" % ret)

        _cam_class.framerate_toggle = stBool.value

    def Init_Exposure_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

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
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

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
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        st_white_mode = MVCC_ENUMVALUE()
        memset(byref(st_white_mode), 0, sizeof(MVCC_ENUMVALUE))
        ret = self.obj_cam.MV_CC_GetEnumValue("BalanceWhiteAuto", st_white_mode)
        self.white_mode = st_white_mode.nCurValue
        if self.white_mode == 1: #1 is continuous mode
            _cam_class.auto_white_toggle = True
        #elif self.white_mode == 2: #2 is once mode, #0 is off mode
        else:
            _cam_class.auto_white_toggle = False

    def Init_Black_Level_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        stBool = c_bool(False)
        ret =self.obj_cam.MV_CC_GetBoolValue("BlackLevelEnable", byref(stBool))
        if ret != 0:
            print ("get acquisition black level enable fail! ret[0x%x]" % ret)

        _cam_class.black_lvl_toggle = stBool.value

    def Init_Sharpness_Mode(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        stBool = c_bool(False)
        ret =self.obj_cam.MV_CC_GetBoolValue("SharpnessEnable", byref(stBool))
        #print(ret)
        if ret != 0:
            print ("get acquisition sharpness enable fail! ret[0x%x]" % ret)

        _cam_class.sharpness_toggle = stBool.value

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
               #print(self.start_grabbing_event)
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
            #print(self.start_grabbing_event)
            self.cam_display_event.set()

            if self.cam_display_thread is not None:
                try:
                    Stop_thread(self.cam_display_thread)
                except Exception:# as e:
                    # print("Force Stop Error: ", e)
                    pass
                del self.cam_display_thread
                self.cam_display_thread = None
                self.Normal_Mode_display_clear()

            self.cam_display_bool = False

            if True == self.b_thread_closed:
                try:
                    Stop_thread(self.h_thread_handle)
                except Exception:# as e:
                    # print("Force Stop Error: ", e)
                    pass
                del self.h_thread_handle
                self.h_thread_handle = None

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
        if True == self.b_open_device:
            #退出线程
            self.start_grabbing_event.set()
            if True == self.b_thread_closed:
                Stop_thread(self.h_thread_handle)
                #print(self.h_thread_handle)
                self.b_thread_closed = False

            ret = self.obj_cam.MV_CC_CloseDevice()
                
        # ch:销毁句柄 | Destroy handle
        self.b_open_device = False
        self.b_start_grabbing = False
        self.b_exit  = True
        
        self.freeze_numArray = None
        self.numArray = None

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
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]
        # ch:创建显示的窗口 | en:Create the window for display
        stFrameInfo = MV_FRAME_OUT_INFO_EX()  
        img_buff = None
        self.rgb_type = False
        self.mono_type = False

        trigger_mode = self.trigger_mode
        ext_sq_fr_init = False
        interrupt = False

        while not self.start_grabbing_event.isSet():
            if self.trigger_mode == True:
                if trigger_mode != self.trigger_mode:
                    trigger_mode = self.trigger_mode
                    interrupt = True
            else:
                trigger_mode = self.trigger_mode

            ret = self.obj_cam.MV_CC_GetOneFrameTimeout(byref(self.buf_cache), self.n_payload_size, stFrameInfo, 1000) #If Set to Trigger mode ret != 0 until trigger once is pressed.

            ################################################################
            ### Important lines: To prevent leaked frames when user switch camera mode
            if interrupt == True:
                self.start_grabbing_event.wait(0.3)
                # print("Mode Switching")
                interrupt = False
                ext_sq_fr_init = False
                continue
            ################################################################
            # print('Get Frame Error: ', self.To_hex_str(ret), trigger_mode)

            if ret == 0:
                #获取到图像的时间开始节点获取到图像的时间开始节点
                self.st_frame_info = stFrameInfo
                size = np.multiply(self.st_frame_info.nWidth, self.st_frame_info.nHeight)
                self.n_save_image_size = int(np.multiply(size, 3)) + 2048

                if img_buff is None:
                    img_buff = (c_ubyte * self.n_save_image_size)()

                pass
            else:
                continue

            #转换像素结构体赋值
            stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
            memset(byref(stConvertParam), 0, sizeof(stConvertParam))
            stConvertParam.nWidth = self.st_frame_info.nWidth
            stConvertParam.nHeight = self.st_frame_info.nHeight
            stConvertParam.pSrcData = self.buf_cache
            stConvertParam.nSrcDataLen = self.st_frame_info.nFrameLen
            stConvertParam.enSrcPixelType = self.st_frame_info.enPixelType 

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
                numArray = self.Color_numpy(img_buff,self.st_frame_info.nWidth, self.st_frame_info.nHeight)
                if _cam_class.flip_img_bool == True:
                    self.numArray = imutils.rotate(numArray, 180)
                else:
                    self.numArray = numArray

                self.mono_type = False
                self.rgb_type = True

                ################################################################

            if _cam_class.capture_img_status.get() == 1:
                if self.freeze_numArray is None:
                    self.freeze_numArray = self.numArray

            elif _cam_class.capture_img_status.get() == 0:
                self.freeze_numArray = None

            self.cam_display_bool = True

            if _cam_class.trigger_auto_save_bool.get() == 1 and trigger_mode == True:
                self.Normal_Mode_Save(self.numArray, self.freeze_numArray, auto_save = True, trigger_mode = trigger_mode)

            elif _cam_class.trigger_auto_save_bool.get() == 0 and trigger_mode == False:
                self.Normal_Mode_Save(self.numArray, self.freeze_numArray, auto_save = False, trigger_mode = trigger_mode)

            if self.b_exit == True:
                # print('breaking')
                break


    def Normal_Mode_Save(self, arr_1, arr_2 = None, auto_save = False, trigger_mode = False): #Normal Camera Mode Save
        img_arr = arr_1
        if isinstance(arr_2, np.ndarray) == True:
            img_arr = arr_2

        if auto_save == False:
            if True == self.__validate_rgb_img(img_arr) and False == self.__validate_mono_img(img_arr):
                if self.b_save == True:
                    from main_GUI import main_GUI
                    _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

                    img_format = _cam_class.save_img_format_sel.get()
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


            elif False == self.__validate_rgb_img(img_arr) and True == self.__validate_mono_img(img_arr):
                if self.b_save == True:
                    from main_GUI import main_GUI
                    _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

                    img_format = _cam_class.save_img_format_sel.get()
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
            
            else:
                self.b_save = False
                self.img_save_folder = None

                _cam_class.clear_img_save_msg_box()


        elif auto_save == True:
            if True == self.__validate_rgb_img(img_arr) and False == self.__validate_mono_img(img_arr):
                img_format = _cam_class.save_img_format_sel.get()
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
                img_format = _cam_class.save_img_format_sel.get()
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

    def Cam_Disp_Thread(self):
        self.cam_display_bool = False

        while not self.cam_display_event.isSet():
            actual_frame_rate = self.Get_actual_framerate()
            cam_display_fps = np.divide(1, float(actual_frame_rate))
            if self.cam_display_bool == True:
                self.All_Mode_Cam_Disp()

            self.cam_display_event.wait(cam_display_fps)

    def All_Mode_Cam_Disp(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        if self.rgb_type == True and self.mono_type == False:
            if _cam_class.popout_status == False:
                if self.freeze_numArray is None:
                    self.RGB_display(self.numArray)

                elif self.freeze_numArray is not None:
                    self.RGB_display(self.freeze_numArray)

                self.disp_clear_ALL_status = False

            elif _cam_class.popout_status == True:
                if self.disp_clear_ALL_status == False:
                    self.Normal_Mode_display_clear()
                    self.disp_clear_ALL_status = True
                
                if self.freeze_numArray is None:
                    self.popout_display(self.numArray)
                    self.home_GUI_display(self.numArray)

                elif self.freeze_numArray is not None:
                    self.popout_display(self.freeze_numArray)
                    self.home_GUI_display(self.freeze_numArray)

        elif self.rgb_type == False and self.mono_type == True:
            if _cam_class.popout_status == False:
                if self.freeze_numArray is None:
                    self.Mono_display(self.numArray)

                elif self.freeze_numArray is not None:
                    self.Mono_display(self.freeze_numArray)

                self.disp_clear_ALL_status = False

            elif _cam_class.popout_status == True:
                if self.disp_clear_ALL_status == False:
                    self.Normal_Mode_display_clear()
                    self.disp_clear_ALL_status = True
                
                if self.freeze_numArray is None:
                    self.popout_display(self.numArray)
                    self.home_GUI_display(self.numArray)

                elif self.freeze_numArray is not None:
                    self.popout_display(self.freeze_numArray)
                    self.home_GUI_display(self.freeze_numArray)

    def home_GUI_display(self, img_arr):
        from main_GUI import main_GUI
        _multicam_class = main_GUI.class_multi_cam_conn

        if img_arr is not None:
            try:
                display_func(_multicam_class.display_gui_list[self.nConnectionNum]
                    , img_arr, _multicam_class.cam_display_width, _multicam_class.cam_display_height)
            except Exception:
                pass

    def RGB_display(self, img_arr):
        #Display for Normal Camera Mode
        from main_GUI import main_GUI
        _multicam_class = main_GUI.class_multi_cam_conn
        #print(self.h_thread_handle ,_multicam_class.display_gui_list[self.nConnectionNum])
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]
        # print(self.nConnectionNum,': ', _cam_class)
        _home_mode = main_GUI.class_multi_cam_conn.home_mode


        if img_arr is not None:

            if _home_mode == False:
                try:
                    display_func(_cam_class.cam_display_rgb, img_arr, 'img')
                    display_func(_cam_class.cam_display_R, img_arr[:,:,0], 'img')
                    display_func(_cam_class.cam_display_G, img_arr[:,:,1], 'img')
                    display_func(_cam_class.cam_display_B, img_arr[:,:,2], 'img')
                
                except(tk.TclError):
                    pass

            elif _home_mode == True:
                try:
                    display_func(_multicam_class.display_gui_list[self.nConnectionNum]
                        , img_arr, 'img')
                except(tk.TclError):
                    pass

    def Mono_display(self, img_arr):
        #Display for Normal Camera Mode
        from main_GUI import main_GUI
        _multicam_class = main_GUI.class_multi_cam_conn
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]
        _home_mode = main_GUI.class_multi_cam_conn.home_mode

        if img_arr is not None:
            if _home_mode == False:
                display_func(_cam_class.cam_display_rgb, img_arr, 'img')

            elif _home_mode == True:
                try:
                    display_func(_multicam_class.display_gui_list[self.nConnectionNum]
                        , img_arr, 'img')
                except(tk.TclError):
                    pass

    def Normal_Mode_display_clear(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]
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
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        if self.rgb_type == False and self.mono_type == True:
            try:
                _cam_class.popout_var_mode = 'original'
                _cam_class.sel_R_btn['state'] = 'disable'
                _cam_class.sel_G_btn['state'] = 'disable'
                _cam_class.sel_B_btn['state'] = 'disable'
            except(tk.TclError):
                pass

        elif self.rgb_type == True and self.mono_type == False:
            try:
                _cam_class.sel_R_btn['state'] = 'normal'
                _cam_class.sel_G_btn['state'] = 'normal'
                _cam_class.sel_B_btn['state'] = 'normal'
            except(tk.TclError):
                pass

        try:
            _cam_class.popout_cam_disp_func(img_arr)
        except(tk.TclError):
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
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

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
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

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
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

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
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        if _cam_class.auto_white_toggle == False and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("BalanceWhiteAuto", 1)
            if ret == 0:
                #print('Auto White ON')
                _cam_class.auto_white_toggle = True
                _cam_class.white_balance_btn_state()
                pass
            elif ret != 0:
                _cam_class.auto_white_toggle = False
                pass

        elif _cam_class.auto_white_toggle == True and self.b_open_device == True:
            ret = self.obj_cam.MV_CC_SetEnumValue("BalanceWhiteAuto", 0)
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

    def Enable_Blacklevel(self):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

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
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

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
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetFloatValue("ExposureTime",float(exposureTime))
            if ret != 0:
                _cam_class.revert_val_exposure = True
                pass

    def Set_parameter_gain(self, gain):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetFloatValue("Gain",float(gain))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_gain = True
                pass

    def Set_parameter_framerate(self, frameRate):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetFloatValue("AcquisitionFrameRate",float(frameRate))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_framerate = True
                pass

    def Set_parameter_brightness(self, brightness):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetIntValue("Brightness",int(brightness))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_gain = True
                pass

    def Set_parameter_red_ratio(self, ratio):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetBalanceRatioRed(int(ratio))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_red_ratio = True
                pass

    def Set_parameter_green_ratio(self, ratio):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetBalanceRatioGreen(int(ratio))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_green_ratio = True
                pass

    def Set_parameter_blue_ratio(self, ratio):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetBalanceRatioBlue(int(ratio))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_blue_ratio = True
                pass

    def Set_parameter_black_lvl(self, val):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetIntValue("BlackLevel",int(val))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_black_lvl = True
                pass

    def Set_parameter_sharpness(self, val):
        from main_GUI import main_GUI
        _cam_class = main_GUI.class_multi_cam_conn.load_gui_class[self.nConnectionNum]

        if True == self.b_open_device:
            ret = self.obj_cam.MV_CC_SetIntValue("Sharpness",int(val))
            #print(ret)
            if ret != 0:
                _cam_class.revert_val_sharpness = True
                pass
