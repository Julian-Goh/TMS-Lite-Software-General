class LC20_Control():
    def __init__(self, dll_LC20):
        self.dll_LC20 = dll_LC20

        self.dll_ID = str(self.dll_LC20)
        #print(self.dll_ID)

    def set_mode(self, mode_set):
        #ch_set: Channel(1-16) which controls the lights.
        #mode_set: 0 = Constant, 1 = Strobe
        self.dll_LC20.SetMode(mode_set)

    def set_multiplier(self, ch_set, multiplier_val): 
        # ch_set: Channel(1-16) which controls the lights.
        # multiplier_val: Current Multiplier(1-10)
        self.dll_LC20.SetMultiplier(ch_set, multiplier_val)

    def set_const_intensity(self, ch_set, intensity_val):
        # ch_set: Channel(1-16) which controls the lights.     
        # intensity_val: Colour intensity(0-255)
        self.dll_LC20.SetConstIntensity(ch_set, intensity_val)

    def set_strobe_intensity(self, ch_set, intensity_val):
        # ch_set: Channel(1-16) which controls the lights.     
        # intensity_val: Colour intensity(0-1023)
        self.dll_LC20.SetStrobeIntensity(ch_set, intensity_val)

    def set_strobe_width(self, ch_set, strobe_width):
        # ch_set: Channel(1-16) which controls the lights.     
        # strobe_width: Strobe Width(0-99999)
        self.dll_LC20.SetStrobeWidth(ch_set, strobe_width)

    def strobe(self):
        #print('selected dll_lib: ', self.dll_LC20)
        self.dll_LC20.Strobe()

    def set_output_width(self, output_width):
        # output_width: Strobe Width(0-99999)
        self.dll_LC20.SetOutputWidth(output_width)

    def set_output_delay(self, output_delay):
        # output_delay: Strobe Width(0-99999)
        self.dll_LC20.SetOutputDelay(output_delay)


    def SetFrame(self, int_fr, int_val):
        #int_fr: 0-16
        #int_val: 0-65535
        self.dll_LC20.SetFrame(int_fr, int_val)
        #print('frame no: ', int_fr)
        #print('frame val: ', int_val)
        pass

    def SetFrameWidth(self, fr_width):
        #fr_width: 0 - 99999
        self.dll_LC20.SetFrameWidth(fr_width)
        pass

    def SetNoOfFrame(self, fr_num):
        #fr_num: 1 - 16
        self.dll_LC20.SetNoOfFrame(fr_num)
        pass


    def save_function(self):
        self.dll_LC20.SaveEEPROM()

    def SQ_read_ch(self, ch_arr, ch_index):
        if self.dll_LC20.ReadMultiplier(ch_index) <= 10:
            ch_arr[0] = self.dll_LC20.ReadMultiplier(ch_index)

        if self.dll_LC20.ReadConstIntensity(ch_index) <= 255:
            ch_arr[1] = self.dll_LC20.ReadConstIntensity(ch_index)

        if self.dll_LC20.ReadStrobeIntensity(ch_index) <= 1023:
            ch_arr[2] = self.dll_LC20.ReadStrobeIntensity(ch_index)

        if self.dll_LC20.ReadStrobeWidth(ch_index) <= 99999:
            ch_arr[3] = self.dll_LC20.ReadStrobeWidth(ch_index)
        else:
            pass

    def SQ_read_output_mode(self, ch_arr):
        if self.dll_LC20.ReadMode() <= 1:
            ch_arr[2] = self.dll_LC20.ReadMode()
        if self.dll_LC20.ReadOutputDelay() <= 99999:
            ch_arr[0] = self.dll_LC20.ReadOutputDelay()
        if self.dll_LC20.ReadOutputWidth() <= 99999:
            ch_arr[1] = self.dll_LC20.ReadOutputWidth()
        else:
            pass

    def SQ_read_frame(self, fr_arr, fr_int_arr):
        if self.dll_LC20.ReadNoOfFrame() <= 16:
            fr_arr[0] = self.dll_LC20.ReadNoOfFrame()
        if self.dll_LC20.ReadFrameWidth() <= 99999:
            fr_arr[1] = self.dll_LC20.ReadFrameWidth()

        #print('ctrl_LC20_lib --> SQ_read_frame: ',self.dll_LC20.ReadFrame(0))
        if self.dll_LC20.ReadFrame(0) <= 65535:
            fr_int_arr[0] = self.dll_LC20.ReadFrame(0)
        if self.dll_LC20.ReadFrame(1) <= 65535:
            fr_int_arr[1] = self.dll_LC20.ReadFrame(1)
        if self.dll_LC20.ReadFrame(2) <= 65535:
            fr_int_arr[2] = self.dll_LC20.ReadFrame(2)
        if self.dll_LC20.ReadFrame(3) <= 65535:
            fr_int_arr[3] = self.dll_LC20.ReadFrame(3)
        if self.dll_LC20.ReadFrame(4) <= 65535:
            fr_int_arr[4] = self.dll_LC20.ReadFrame(4)

        if self.dll_LC20.ReadFrame(5) <= 65535:
            fr_int_arr[5] = self.dll_LC20.ReadFrame(5)
        if self.dll_LC20.ReadFrame(6) <= 65535:
            fr_int_arr[6] = self.dll_LC20.ReadFrame(6)
        if self.dll_LC20.ReadFrame(7) <= 65535:
            fr_int_arr[7] = self.dll_LC20.ReadFrame(7)
        if self.dll_LC20.ReadFrame(8) <= 65535:
            fr_int_arr[8] = self.dll_LC20.ReadFrame(8)
        if self.dll_LC20.ReadFrame(9) <= 65535:
            fr_int_arr[9] = self.dll_LC20.ReadFrame(9)

        if self.dll_LC20.ReadFrame(10) <= 65535:
            fr_int_arr[10] = self.dll_LC20.ReadFrame(10)
        if self.dll_LC20.ReadFrame(11) <= 65535:
            fr_int_arr[11] = self.dll_LC20.ReadFrame(11)
        if self.dll_LC20.ReadFrame(12) <= 65535:
            fr_int_arr[12] = self.dll_LC20.ReadFrame(12)
        if self.dll_LC20.ReadFrame(13) <= 65535:
            fr_int_arr[13] = self.dll_LC20.ReadFrame(13)
        if self.dll_LC20.ReadFrame(14) <= 65535:
            fr_int_arr[14] = self.dll_LC20.ReadFrame(14)

        if self.dll_LC20.ReadFrame(15) <= 65535:
            fr_int_arr[15] = self.dll_LC20.ReadFrame(15)

        else:
            pass

        #print(fr_int_arr)