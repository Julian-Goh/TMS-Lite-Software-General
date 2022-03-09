class LC18_Control():
    def __init__(self, dll_LC18):
        self.dll_LC18 = dll_LC18

        self.dll_ID = str(self.dll_LC18)
        #print(self.dll_ID)

    def set_mode(self, ch_set, mode_set):
        #ch_set: Channel(1-4) which controls the lights.
        #mode_set: 0 = Constant, 1 = Strobe, 2 = Trigger
        if self.dll_ID == 'LC18Library.LC18SQ':
            self.dll_LC18.SetMode(mode_set)
        else:
            self.dll_LC18.SetMode(ch_set, mode_set)

    def set_multiplier(self, ch_set, multiplier_val): 
        # ch_set: Channel(1-4) which controls the lights.
        # multiplier_val: Current Multiplier(1-10)
        self.dll_LC18.SetMultiplier(ch_set, multiplier_val)

    def set_const_intensity(self, ch_set, intensity_val):
        # ch_set: Channel(1-4) which controls the lights.     
        # intensity_val: Colour intensity(0-255)
        if self.dll_ID == 'LC18Library.LC18SQ':
            self.dll_LC18.SetIntensity(ch_set, intensity_val)
        else:
            self.dll_LC18.SetConstIntensity(ch_set, intensity_val)

    def set_strobe_width(self, ch_set, strobe_width):
        self.dll_LC18.SetStrobeWidth(ch_set, strobe_width)

    def set_strobe_delay(self, ch_set, strobe_delay):
        self.dll_LC18.SetStrobeDelay(ch_set, strobe_delay)

    def strobe(self, ch_set):
        #print('selected dll_lib: ', self.dll_LC18)
        if self.dll_ID == 'LC18Library.LC18SQ':
            #print('Strobing LC18SQ')
            self.dll_LC18.Strobe()
        else:
            self.dll_LC18.Strobe(ch_set)

    def set_output_width(self, ch_set, output_width):
        if self.dll_ID == 'LC18Library.LC18SQ':
            self.dll_LC18.SetOutputWidth(output_width)
        else:
            self.dll_LC18.SetOutputWidth(ch_set, output_width)

    def set_output_delay(self, ch_set, output_delay):
        if self.dll_ID == 'LC18Library.LC18SQ':
            self.dll_LC18.SetOutputDelay(output_delay)
        else:
            self.dll_LC18.SetOutputDelay(ch_set, output_delay)

    def select_address(self, addr):
        self.dll_LC18.SelectAddress(addr)

    def save_function(self):
        self.dll_LC18.SaveEEPROM()

    def read_function(self, ch_arr, ch_index):
        if self.dll_LC18.ReadMultiplier(ch_index) <= 10:
            ch_arr[0] = self.dll_LC18.ReadMultiplier(ch_index)
        if self.dll_LC18.ReadMode(ch_index) <= 2:
            ch_arr[6] = self.dll_LC18.ReadMode(ch_index)
        if self.dll_LC18.ReadConstIntensity(ch_index) <= 255:
            ch_arr[1] = self.dll_LC18.ReadConstIntensity(ch_index)
        if self.dll_LC18.ReadStrobeDelay(ch_index) <= 9999:
            ch_arr[2] = self.dll_LC18.ReadStrobeDelay(ch_index)
        if self.dll_LC18.ReadStrobeWidth(ch_index) <= 9999:
            ch_arr[3] = self.dll_LC18.ReadStrobeWidth(ch_index)
        if self.dll_LC18.ReadOutputDelay(ch_index) <= 9999:
            ch_arr[4] = self.dll_LC18.ReadOutputDelay(ch_index)
        if self.dll_LC18.ReadOutputWidth(ch_index) <= 9999:
            ch_arr[5] = self.dll_LC18.ReadOutputWidth(ch_index)
        else:
            pass

    def SQ_read_function(self, ch_arr, ch_index):
        if self.dll_LC18.ReadMultiplier(ch_index) <= 10:
            ch_arr[0] = self.dll_LC18.ReadMultiplier(ch_index)
        if self.dll_LC18.ReadMode() <= 2:
            ch_arr[6] = self.dll_LC18.ReadMode()
        if self.dll_LC18.ReadIntensity(ch_index) <= 255:
            ch_arr[1] = self.dll_LC18.ReadIntensity(ch_index)
        if self.dll_LC18.ReadStrobeWidth(ch_index) <= 9999:
            ch_arr[3] = self.dll_LC18.ReadStrobeWidth(ch_index)
        if self.dll_LC18.ReadOutputDelay() <= 9999:
            ch_arr[4] = self.dll_LC18.ReadOutputDelay()
        if self.dll_LC18.ReadOutputWidth() <= 9999:
            ch_arr[5] = self.dll_LC18.ReadOutputWidth()

    def SQ_read_frame_function(self, fr_arr, fr_int_arr):
        if self.dll_LC18.ReadNoOfFrame() <= 10:
            fr_arr[0] = self.dll_LC18.ReadNoOfFrame()
        if self.dll_LC18.ReadFrameWidth() <= 9999:
            fr_arr[1] = self.dll_LC18.ReadFrameWidth()


        if self.dll_LC18.ReadFrame(0) <= 15:
            fr_int_arr[0] = self.dll_LC18.ReadFrame(0)
        if self.dll_LC18.ReadFrame(1) <= 15:
            fr_int_arr[1] = self.dll_LC18.ReadFrame(1)
        if self.dll_LC18.ReadFrame(2) <= 15:
            fr_int_arr[2] = self.dll_LC18.ReadFrame(2)
        if self.dll_LC18.ReadFrame(3) <= 15:
            fr_int_arr[3] = self.dll_LC18.ReadFrame(3)
        if self.dll_LC18.ReadFrame(4) <= 15:
            fr_int_arr[4] = self.dll_LC18.ReadFrame(4)

        if self.dll_LC18.ReadFrame(5) <= 15:
            fr_int_arr[5] = self.dll_LC18.ReadFrame(5)
        if self.dll_LC18.ReadFrame(6) <= 15:
            fr_int_arr[6] = self.dll_LC18.ReadFrame(6)
        if self.dll_LC18.ReadFrame(7) <= 15:
            fr_int_arr[7] = self.dll_LC18.ReadFrame(7)
        if self.dll_LC18.ReadFrame(8) <= 15:
            fr_int_arr[8] = self.dll_LC18.ReadFrame(8)
        if self.dll_LC18.ReadFrame(9) <= 15:
            fr_int_arr[9] = self.dll_LC18.ReadFrame(9)

        else:
            pass


    def SQ_Trigger(self, mode):
        #mode: 0 (off) - 1 (on)
        self.dll_LC18.Trigger(mode)

    def SQ_SetFrame(self, int_fr, int_val):
        #int_fr: 0-9
        #int_val: 0-15
        #print('selected dll_lib: ', self.dll_LC18)
        #print('dll_LC18SQ: ', int_fr, int_val)
        
        self.dll_LC18.SetFrame(int_fr, int_val)
        pass

    def SQ_SetFrameWidth(self, fr_width):
        #fr_width: 0 - 9999
        self.dll_LC18.SetFrameWidth(fr_width)
        pass

    def SQ_SetNoOfFrame(self, fr_num):
        #fr_num: 1 - 10
        
        self.dll_LC18.SetNoOfFrame(fr_num)
        pass