import tkinter as tk
from functools import partial
import re

class CustomSpinbox(tk.Spinbox):
    def __init__(self, master, input_rate = 40, *args, **kwargs):
        tk.Spinbox.__init__(self, master, *args, **kwargs)
        """Add bind events to bind_class if you want to effectively use the special keypress events. Use tag self.__custom_tag in the bind_class"""
        self.__kp_time      = 0 ## kp: keypress
        self.__kp_event_id  = None
        self.__input_rate   = input_rate ##update rate of the keypress event
        self.__curr_item    = self.get()

        self.__custom_tag = re.sub(".!", "", str(self))
        # print(self.winfo_name())
        bindtags = list(self.bindtags())
        # print(bindtags)
        # index = bindtags.index(str(self))
        index = bindtags.index("Spinbox")
        # print(index)
        self.__btn_event_tag = "input_rate--{}".format(self.__custom_tag)
        bindtags.insert(index + 1, self.__btn_event_tag)
        bindtags.insert(index + 2, self.__custom_tag)
        # print(bindtags)
        self.bindtags(tuple(bindtags))

        self.bind_class(self.__btn_event_tag, "<ButtonPress-1>"     , partial(self.__event_press)    , add = "+")
        self.bind_class(self.__btn_event_tag, "<ButtonRelease-1>"   , partial(self.__event_release)  , add = "+")

        self.bind('<KeyPress-Up>', self.__break_event)
        self.bind('<KeyPress-Down>', self.__break_event)

    def __break_event(self, event):
        return "break"

    def get_tag(self):
        """Get the custom tag for bind_class events"""
        return self.__custom_tag

    def __event_press(self, event):
        self.__curr_item = self.get()
        self.__kp_time += 1
        if self.__kp_time <= 3: #increases speed if button has been hold for 0.75 seconds
            self.__kp_event_id = self.after(250, self.__event_press, event)
        else:
            self.config(repeatdelay = 1, repeatinterval = self.__input_rate)

        # print(self.__kp_time, self.__kp_event_id)
    
    def __event_release(self, event):
        if self.__kp_event_id is not None:
            self.after_cancel(self.__kp_event_id)
            self.config(repeatdelay = 400, repeatinterval = 100)
            if self.__kp_time <= 1:
                self.__kp_time = 0
                if self.get() == self.__curr_item:
                    return "break" ### This will explicitly break the self.__custom_tag bind tags
            else:
                self.__kp_time = 0

        self.__kp_time = 0

    def update_input_rate(self, value):
        self.__input_rate = value


    def test(self):
        print("Hello Errbody")
