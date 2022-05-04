import os
import sys
import functools
import clr
code_PATH = os.getcwd()
sys.path.append(code_PATH)

clr.AddReference("LC18Library")
import LC18Library

def validate_lib(lib):
    return isinstance(lib, LC18Library.LC18)


def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # print ('Caught an exception in', f.__name__)
            pass
    return func

class LC18_Control():
    def __init__(self, dll_LC18):
        self.dll_LC18 = dll_LC18
        
    @catch_exception
    def set_mode(self, ch_set, mode_set):
        #ch_set: Channel(1-4) which controls the lights.
        #mode_set: 0 = Constant, 1 = Strobe, 2 = Trigger
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetMode(ch_set, mode_set)

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
            self.dll_LC18.SetConstIntensity(ch_set, intensity_val)

    @catch_exception
    def set_strobe_width(self, ch_set, strobe_width):
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetStrobeWidth(ch_set, strobe_width)

    @catch_exception
    def set_strobe_delay(self, ch_set, strobe_delay):
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetStrobeDelay(ch_set, strobe_delay)

    @catch_exception
    def strobe(self, ch_set):
        #print('selected dll_lib: ', self.dll_LC18)
        if validate_lib(self.dll_LC18):
            self.dll_LC18.Strobe(ch_set)

    @catch_exception
    def set_output_width(self, ch_set, output_width):
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetOutputWidth(ch_set, output_width)

    @catch_exception
    def set_output_delay(self, ch_set, output_delay):
        if validate_lib(self.dll_LC18):
            self.dll_LC18.SetOutputDelay(ch_set, output_delay)

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
    def read_mode(self, ch_index):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadMode(ch_index) 
            if val <= 2:
                return val
        return 0

    @catch_exception
    def read_intensity(self, ch_index):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadConstIntensity(ch_index) 
            if val <= 255:
                return val
        return 0

    @catch_exception
    def read_strobe_delay(self, ch_index):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadStrobeDelay(ch_index) 
            if val <= 9999:
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
    def read_output_delay(self, ch_index):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadOutputDelay(ch_index) 
            if val <= 9999:
                return val
        return 0

    @catch_exception
    def read_output_width(self, ch_index):
        if validate_lib(self.dll_LC18):
            val = self.dll_LC18.ReadOutputWidth(ch_index) 
            if val <= 9999:
                return val
        return 0
