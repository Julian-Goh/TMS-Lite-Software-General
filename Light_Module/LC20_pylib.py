import os
import sys
import functools
import clr

abs_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abs_path)

import LC20Library

def validate_lib(lib):
    return isinstance(lib, LC20Library.LC20SQ)

def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # print ('Caught an exception in', f.__name__)
            pass
    return func

class LC20_Control():
    def __init__(self, dll_LC20):
        self.dll_LC20 = dll_LC20
        # print(isinstance(self.dll_LC20, LC20Library.LC20SQ))
        self.fr_val_hashmap = {}

    @catch_exception    
    def set_mode(self, mode_set):
        #ch_set: Channel(1-16) which controls the lights.
        #mode_set: 0 = Constant, 1 = Strobe
        if validate_lib(self.dll_LC20):
            self.dll_LC20.SetMode(mode_set)

    @catch_exception
    def set_multiplier(self, ch_set, multiplier_val): 
        # ch_set: Channel(1-16) which controls the lights.
        # multiplier_val: Current Multiplier(1-10)
        if validate_lib(self.dll_LC20):
            self.dll_LC20.SetMultiplier(ch_set, multiplier_val)

    @catch_exception
    def set_intensity(self, ch_set, intensity_val):
        # ch_set: Channel(1-16) which controls the lights.     
        # intensity_val: Colour intensity(0-255)
        if validate_lib(self.dll_LC20):
            self.dll_LC20.SetConstIntensity(ch_set, intensity_val)

    @catch_exception
    def set_strobe_intensity(self, ch_set, intensity_val):
        # ch_set: Channel(1-16) which controls the lights.     
        # intensity_val: Colour intensity(0-1023)
        if validate_lib(self.dll_LC20):
            self.dll_LC20.SetStrobeIntensity(ch_set, intensity_val)

    @catch_exception
    def set_strobe_width(self, ch_set, strobe_width):
        # ch_set: Channel(1-16) which controls the lights.     
        # strobe_width: Strobe Width(0-99999)
        if validate_lib(self.dll_LC20):
            self.dll_LC20.SetStrobeWidth(ch_set, strobe_width)

    @catch_exception
    def strobe(self):
        #print('selected dll_lib: ', self.dll_LC20)
        if validate_lib(self.dll_LC20):
            self.dll_LC20.Strobe()

    @catch_exception
    def set_output_width(self, output_width):
        # output_width: Strobe Width(0-99999)
        if validate_lib(self.dll_LC20):
            self.dll_LC20.SetOutputWidth(output_width)

    @catch_exception
    def set_output_delay(self, output_delay):
        # output_delay: Strobe Width(0-99999)
        if validate_lib(self.dll_LC20):
            self.dll_LC20.SetOutputDelay(output_delay)

    @catch_exception
    def SQ_SetFrame(self, int_fr, int_val):
        #int_fr: 0-16
        #int_val: 0-65535
        if validate_lib(self.dll_LC20):
            self.dll_LC20.SetFrame(int_fr, int_val)
        #print('frame no: ', int_fr)
        #print('frame val: ', int_val)

    @catch_exception
    def SQ_SetFrameWidth(self, fr_width):
        #fr_width: 0 - 99999
        if validate_lib(self.dll_LC20):
            self.dll_LC20.SetFrameWidth(fr_width)

    @catch_exception
    def SQ_SetNoOfFrame(self, fr_num):
        #fr_num: 1 - 16
        if validate_lib(self.dll_LC20):
            self.dll_LC20.SetNoOfFrame(fr_num)

    @catch_exception
    def save_function(self):
        if validate_lib(self.dll_LC20):
            self.dll_LC20.SaveEEPROM()

    @catch_exception
    def read_multiplier(self, ch_index):
        if validate_lib(self.dll_LC20):
            val = self.dll_LC20.ReadMultiplier(ch_index)
            if val <= 10:
                return val
        return 1

    @catch_exception
    def read_intensity(self, ch_index):
        if validate_lib(self.dll_LC20):
            val = self.dll_LC20.ReadConstIntensity(ch_index)
            if val <= 255:
                return val
        return 0

    @catch_exception
    def read_strobe_intensity(self, ch_index):
        if validate_lib(self.dll_LC20):
            val = self.dll_LC20.ReadStrobeIntensity(ch_index)
            if val <= 1023:
                return val
        return 0

    @catch_exception
    def read_strobe_width(self, ch_index):
        if validate_lib(self.dll_LC20):
            val = self.dll_LC20.ReadStrobeWidth(ch_index)
            if val <= 99999:
                return val
        return 0

    @catch_exception
    def read_mode(self):
        if validate_lib(self.dll_LC20):
            val = self.dll_LC20.ReadMode()
            if val <= 1:
                return val
        return 0

    @catch_exception
    def read_output_delay(self):
        if validate_lib(self.dll_LC20):
            val = self.dll_LC20.ReadOutputDelay()
            if val <= 99999:
                return val
        return 0

    @catch_exception
    def read_output_width(self):
        if validate_lib(self.dll_LC20):
            val = self.dll_LC20.ReadOutputWidth()
            if val <= 99999:
                return val
        return 0

    @catch_exception
    def read_frame_num(self):
        if validate_lib(self.dll_LC20):
            val = self.dll_LC20.ReadNoOfFrame()
            if val <= 16:
                return val
        return 1

    @catch_exception
    def read_frame_width(self):
        if validate_lib(self.dll_LC20):
            val = self.dll_LC20.ReadFrameWidth()
            if val <= 99999:
                return val
        return 1

    @catch_exception
    def SQ_read_frame(self):
        if validate_lib(self.dll_LC20):
            self.fr_val_hashmap.clear()
            for i in range(0, 16):
                self.fr_val_hashmap[str(i)] = 0
                val = self.dll_LC20.ReadFrame(i)
                if val <= 65535:
                    self.fr_val_hashmap[str(i)] = val

            return self.fr_val_hashmap
        return {}