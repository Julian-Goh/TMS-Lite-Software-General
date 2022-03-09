import os
from os import path
import sys
import numpy as np
from ctypes import *

code_PATH = os.getcwd()
#print(code_PATH)
sys.path.append(code_PATH)

#Crevis_dll = WinDLL("Crevis.VirtualFG40Library.dll")
Crevis_dll = WinDLL("VirtualFG40.dll")
#print(Crevis_dll)
#print(dir(Crevis_dll))
#print(dir(Crevis_dll._func_restype_))
#print(dir(Crevis_dll.ST_AcqStart))

class _CREVIS_PY_OBJECT_(Structure):
    pass
_CREVIS_PY_OBJECT_._fields_ = [
    ('PyObject', py_object),
]
CREVIS_PY_OBJECT = _CREVIS_PY_OBJECT_

class CrevisCamera():
    def __init__(self):
        # self._handle = c_void_p()
        # self.handle = pointer(self._handle)
        self.handle_device = c_int32()
        self.hdevice = pointer(self.handle_device)

        #print(Crevis_dll.ST_IsInitSystem)
    # @staticmethod
    def ST_InitSystem(self):
        #Crevis_dll.ST_InitSystem.argtype = c_void_p
        #return Crevis_dll.ST_InitSystem(self.handle)
        #Crevis_dll.ST_InitSystem.restype = c_uint
        return Crevis_dll.ST_InitSystem()

    def ExposureUpdateFeature(self):
        return Crevis_dll.ExposureUpdateFeature()

    def ST_FreeSystem(self):
        return Crevis_dll.ST_FreeSystem()

    def ST_UpdateDevice(self):
        return Crevis_dll.ST_UpdateDevice()

    def ST_IsInitSystem(self, pFlag):
        Crevis_dll.ST_IsInitSystem.argtype = (c_bool)
        Crevis_dll.ST_IsInitSystem.restype = c_int32
        return Crevis_dll.ST_IsInitSystem(byref(pFlag))

    def ST_GetAvailableCameraNum(self,pNum):
        Crevis_dll.ST_GetAvailableCameraNum.argtype = (c_uint32)
        Crevis_dll.ST_GetAvailableCameraNum.restype = c_int32
        return Crevis_dll.ST_GetAvailableCameraNum(byref(pNum))

    def ST_OpenDevice(self, enum, is_detail_log):
        Crevis_dll.ST_OpenDevice.argtype = (c_uint32, c_bool)
        Crevis_dll.ST_OpenDevice.restype = c_int32
        return Crevis_dll.ST_OpenDevice(enum, byref(self.hdevice), is_detail_log)

    def ST_IsOpenDevice(self, pFlag):
        Crevis_dll.ST_IsOpenDevice.argtype = (c_bool)
        Crevis_dll.ST_IsOpenDevice.restype = c_int32
        return Crevis_dll.ST_IsOpenDevice(self.hdevice, byref(pFlag))

    def ST_SetIntReg(self, node_name, val):
        Crevis_dll.ST_SetIntReg.argtype = (c_char, c_int32)
        Crevis_dll.ST_SetIntReg.restype = (c_int32)
        return Crevis_dll.ST_SetIntReg(self.hdevice, node_name, val)
    
    def ST_SetBoolReg(self, node_name, bval):
        Crevis_dll.ST_SetBoolReg.argtype = (c_char, c_bool)
        Crevis_dll.ST_SetBoolReg.restype = (c_int32)
        return Crevis_dll.ST_SetBoolReg(self.hdevice, node_name, bval)

    def ST_SetFloatReg(self, node_name, fval):
        Crevis_dll.ST_SetFloatReg.argtype = (c_char, c_double)
        Crevis_dll.ST_SetFloatReg.restype = (c_int32)
        return Crevis_dll.ST_SetFloatReg(self.hdevice, node_name, fval)

    def ST_SetEnumReg(self, node_name, val):
        Crevis_dll.ST_SetEnumReg.argtype = (c_char, c_char)
        Crevis_dll.ST_SetEnumReg.restype = (c_int32)
        return Crevis_dll.ST_SetEnumReg(self.hdevice, node_name, val)

    def ST_SetStrReg(self, node_name, val):
        Crevis_dll.ST_SetStrReg.argtype = (c_char, c_char)
        Crevis_dll.ST_SetStrReg.restype = (c_int32)
        return Crevis_dll.ST_SetStrReg(self.hdevice, node_name, val)

    def ST_SetCmdReg(self, node_name):
        Crevis_dll.ST_SetCmdReg.argtype = (c_char)
        Crevis_dll.ST_SetCmdReg.restype = (c_int32)
        return Crevis_dll.ST_SetCmdReg(self.hdevice, node_name)

    def ST_GetEnumDeviceInfo(self, enum, DeviceInfoCmd, pInfo, pSize):
        Crevis_dll.ST_GetEnumDeviceInfo.argtype = (c_uint32, c_int32, c_char, c_uint32)
        Crevis_dll.ST_GetEnumDeviceInfo.restype = (c_int32)
        return Crevis_dll.ST_GetEnumDeviceInfo(enum, DeviceInfoCmd, byref(pInfo), byref(pSize))

    def ST_GetIntReg(self, node_name, pVal):
        Crevis_dll.ST_GetIntReg.argtype = (c_char, c_int32)
        Crevis_dll.ST_GetIntReg.restype = (c_int32)
        return Crevis_dll.ST_GetIntReg(self.hdevice, node_name, byref(pVal))

    def ST_GetBoolReg(self, node_name, bVal):
        Crevis_dll.ST_GetBoolReg.argtype = (c_char, c_bool)
        Crevis_dll.ST_GetBoolReg.restype = (c_int32)
        return Crevis_dll.ST_GetBoolReg(self.hdevice, node_name, byref(bVal))

    def ST_GetFloatReg(self, node_name, fVal):
        Crevis_dll.ST_GetFloatReg.argtype = (c_char, c_double)
        Crevis_dll.ST_GetFloatReg.restype = (c_int32)
        return Crevis_dll.ST_GetFloatReg(self.hdevice, node_name, byref(fVal))

    def ST_GetEnumReg(self, node_name, pInfo, pSize):
        Crevis_dll.ST_GetEnumReg.argtype = (c_char, c_char, c_uint32)
        Crevis_dll.ST_GetEnumReg.restype = (c_int32)
        return Crevis_dll.ST_GetEnumReg(self.hdevice, node_name, byref(pInfo), byref(pSize))

    def ST_GetStrReg(self, node_name, pInfo, pSize):
        Crevis_dll.ST_GetStrReg.argtype = (c_char, c_char, c_uint32)
        Crevis_dll.ST_GetStrReg.restype = (c_int32)
        return Crevis_dll.ST_GetStrReg(self.hdevice, node_name, byref(pInfo), byref(pSize))

    def ST_AcqStart(self):
        return Crevis_dll.ST_AcqStart(self.hdevice)

    def ST_GrabImage(self, img_buff, buff_size): #pDest: output/destination (image)
        Crevis_dll.ST_GrabImage.argtype = (c_void_p, c_uint32)
        Crevis_dll.ST_GrabImage.restype = c_int32 #(c_void_p)
        return Crevis_dll.ST_GrabImage(self.hdevice, img_buff, buff_size)

    def ST_AcqStop(self):
        return Crevis_dll.ST_AcqStop(self.hdevice)


    def ST_CloseDevice(self):
        return Crevis_dll.ST_CloseDevice(self.hdevice)

if __name__ == '__main__':
    import cv2
    crevis_class = CrevisCamera()
    print(crevis_class.handle_device)
    crevis_class.ST_FreeSystem()
    print(crevis_class.ST_InitSystem())
    #print(crevis_class.ST_FreeSystem())
    init_check = c_bool(False)
    print(crevis_class.ST_IsInitSystem(init_check), init_check)

    cam_num = c_uint32(0)
    ret = crevis_class.ST_GetAvailableCameraNum(cam_num)
    print(ret)
    print(cam_num)
    
    # handle_device = c_int32()
    # hdevice = pointer(handle_device)
    crevis_class.ST_OpenDevice(0, False)
    #print(hdevice)

    open_check = c_bool()
    crevis_class.ST_IsOpenDevice(open_check)
    print(open_check)

    pSize = c_uint32(256)
    pInfo = (c_ubyte * 16)()
    ret = Crevis_dll.ST_GetEnumDeviceInfo(c_uint32(0), c_int32(10001), byref(pInfo), byref(pSize))
    print('ST_GetEnumDeviceInfo: ', ret)
    print(bytes(pInfo).decode("utf-8"))
    
    pSize = c_uint32(256)
    pInfo = (c_ubyte * 8)()
    ret = crevis_class.ST_GetEnumReg('PixelFormat'.encode('utf-8'), pInfo, pSize)
    print('Pixel Format: ', bytes(pInfo).decode("utf-8"))
    #print(pSize)
    print('get_pixel_format: ', ret)

    pSize = c_uint32(256)
    pInfo = (c_ubyte * 8)()
    ret = crevis_class.ST_GetStrReg('DeviceModelName'.encode('utf-8'), pInfo, pSize)
    print('Device Model Name: ', bytes(pInfo).decode("utf-8"))
    #print(pSize)
    print('get_device_model_name: ', ret)


    # n_payload_size = c_uint32()
    # ret = crevis_class.ST_GetIntReg('PayloadSize'.encode('utf-8'), n_payload_size)
    # print('n_payload_size: ', n_payload_size)
    # print('get_payload_size: ', ret)


    cam_width = c_int32()
    #print(cam_width)
    cam_height = c_int32()
    #width_char = c_wchar_p('Width')
    #print(width_char)
    #print('Width'.encode('utf-8'))
    crevis_class.ST_GetIntReg('Width'.encode('utf-8') , cam_width)
    print(cam_width)
    crevis_class.ST_GetIntReg('Height'.encode('utf-8') , cam_height)
    print(cam_height)

    buff_size = cam_height.value * cam_width.value
    print(buff_size)
    buf_cache = (c_ubyte * buff_size)()
    print(buf_cache)

    ret = crevis_class.ST_AcqStart()
    print('acq_start: ', ret)

    ret = crevis_class.ST_SetEnumReg('TriggerMode'.encode('utf-8'), 'On'.encode('utf-8'))
    print('Trigger Mode: ', ret)

    ret = crevis_class.ST_SetEnumReg('TriggerSource'.encode('utf-8'), 'Software'.encode('utf-8'))
    print('Trigger Source: ', ret)
    # pSize = c_uint32(256)
    # pInfo = (c_ubyte * 8)()
    # ret = crevis_class.ST_GetEnumReg('TriggerMode'.encode('utf-8'), pInfo, pSize)
    # print('Trigger Mode Status: ', bytes(pInfo).decode("utf-8"))
    # print('get_Trigger Mode Status: ', ret)

    if str(open_check) == str(c_bool(True)):
        while (True):
            pSize = c_uint32(256)
            pInfo = (c_ubyte * 8)()
            ret = crevis_class.ST_GetEnumReg('TriggerMode'.encode('utf-8'), pInfo, pSize)
            status = (bytes(pInfo).decode("utf-8")).strip().strip('\x00')
            print(status)
            if status == 'On':
                ret = crevis_class.ST_SetCmdReg('TriggerSoftware'.encode('utf-8'))
                print(ret)
                
            ret = crevis_class.ST_GrabImage(byref(buf_cache), buff_size)
            print(ret)
            if ret != 0:
                continue
            #print(buf_cache)
            data_ = np.frombuffer(buf_cache, dtype=np.uint8, offset=0, count=-1)#int(buff_size*3))
            #print(data_, data_.shape)

            data_mono_arr = data_.reshape(cam_height.value, cam_width.value)
            numArray = np.zeros([cam_height.value, cam_width.value],"uint8") 
            numArray[:, :] = data_mono_arr

            # data_r = data_[0:int(buff_size*3):3]
            # data_g = data_[1:int(buff_size*3):3]
            # data_b = data_[2:int(buff_size*3):3]

            # data_r_arr = data_r.reshape(int(cam_height.value), int(cam_width.value))
            # data_g_arr = data_g.reshape(int(cam_height.value), int(cam_width.value))
            # data_b_arr = data_b.reshape(int(cam_height.value), int(cam_width.value))
            # numArray = np.zeros([int(cam_height.value), int(cam_width.value), 3],"uint8")

            # numArray[:, :, 0] = data_r_arr
            # numArray[:, :, 1] = data_g_arr
            # numArray[:, :, 2] = data_b_arr

            #print(numArray)
            cv2.imshow('Crevis Disp', numArray)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if ret != 0 :
                break
    #cv2.waitKey(0)
    ret = crevis_class.ST_AcqStop()
    print('acq_stop: ', ret)

    ret = crevis_class.ST_CloseDevice()
    print('close_device: ', ret)