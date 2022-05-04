import os
import sys
import functools
import clr

abs_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abs_path)

import LC18Library

def validate_lib(lib):
    return isinstance(lib, LC18Library.LC18SQ)

def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # print ('Caught an exception in', f.__name__)
            pass
    return func

class LC18SQ_Control():
    def __init__(self, dll_LC18):
        self.dll_LC18 = dll_LC18
        # print(isinstance(self.dll_LC18, LC18Library.LC18SQ))
        self.fr_val_hashmap = {}

    @catch_exception
    def set_mode(self, mode_set):
        #mode_set: 0 = Constant, 1 = Strobe, 2 = Trigger
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetMode(mode_set)

    @catch_exception
    def set_multiplier(self, ch_set, multiplier_val): 
        # ch_set: Channel(1-4) which controls the lights.
        # multiplier_val: Current Multiplier(1-10)
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetMultiplier(ch_set, multiplier_val)

    @catch_exception
    def set_intensity(self, ch_set, intensity_val):
        # ch_set: Channel(1-4) which controls the lights.     
        # intensity_val: Colour intensity(0-255)
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetIntensity(ch_set, intensity_val)

    @catch_exception
    def set_strobe_width(self, ch_set, strobe_width):
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetStrobeWidth(ch_set, strobe_width)

    @catch_exception
    def strobe(self):
        #print('selected dll_lib: ', self.dll_LC18)
        if validate_lib(self.dll_LC18):
            self.dll_LC18.Strobe()

    @catch_exception
    def set_output_width(self, output_width):
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetOutputWidth(output_width)

    @catch_exception
    def set_output_delay(self, output_delay):
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetOutputDelay(output_delay)

    @catch_exception
    def select_address(self, addr):
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SelectAddress(addr)

    @catch_exception
    def save_function(self):
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SaveEEPROM()

    @catch_exception
    def read_multiplier(self, ch_index):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadMultiplier(ch_index)
            if val <= 10:
                return val
        return 1

    @catch_exception
    def read_mode(self):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadMode()
            if val <= 2:
                return val
        return 0

    @catch_exception
    def read_intensity(self, ch_index):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadIntensity(ch_index)
            if val <= 255:
                return val
        return 0

    @catch_exception
    def read_strobe_width(self, ch_index):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadStrobeWidth(ch_index)
            if val <= 9999:
                return val
        return 0

    @catch_exception
    def read_output_delay(self):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadOutputDelay()
            if val <= 9999:
                return val
        return 0

    @catch_exception
    def read_output_width(self):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadOutputWidth()
            if val <= 9999:
                return val
        return 0

    @catch_exception
    def read_frame_num(self):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadNoOfFrame()
            if val <= 10:
                return val
        return 1

    @catch_exception
    def read_frame_width(self):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadFrameWidth()
            if val <= 9999:
                return val
        return 0

    @catch_exception
    def SQ_read_frame(self):
        if validate_lib(self.dll_LC18):
            self.fr_val_hashmap.clear()
            for i in range(0, 10):
                self.fr_val_hashmap[str(i)] = 0
                val = self.dll_LC18.ReadFrame(i)
                if val <= 15:
                    self.fr_val_hashmap[str(i)] = val

            return self.fr_val_hashmap
        return {}

    @catch_exception
    def SQ_Trigger(self, mode):
        #mode: 0 (off) - 1 (on)
        if validate_lib(self.dll_LC18):
            self.dll_LC18.Trigger(mode)

    @catch_exception
    def SQ_SetFrame(self, int_fr, int_val):
        #int_fr: 0-9
        #int_val: 0-15
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetFrame(int_fr, int_val)

    @catch_exception
    def SQ_SetFrameWidth(self, fr_width):
        #fr_width: 0 - 9999
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetFrameWidth(fr_width)

    @catch_exception
    def SQ_SetNoOfFrame(self, fr_num):
        #fr_num: 1 - 10
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetNoOfFrame(fr_num)
            