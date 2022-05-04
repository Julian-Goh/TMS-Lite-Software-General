import tkinter as tk
from tkinter import ttk
import numpy as np
from functools import partial

def type_int(arg):
    if (type(arg)) == int or (isinstance(arg, np.integer) == True):
        return True
    else:
        return False

class CustomToplvl(tk.Toplevel):
    def __init__(self, parent, toplvl_title = 'Toplevel', min_w = None, min_h = None, icon_img = None
        , topmost_bool = False
        , *args, **kwargs):
        #   initialisation of the Toplevel
        tk.Toplevel.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.title(toplvl_title)

        if (min_w is not None) and (min_h is not None):
            if type_int(min_w) == True and type_int(min_h) == True:
                self.minsize(width=max(0, min_w), height=max(0, min_h))
            else:
                raise TypeError("'min_w' and 'min_h' has to be an int-type value.")

        self.__local_after_events = []

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind('<Map>', partial(self.__topmost_event))

        self.withdraw()

        self.__open_bool = False

        self.__topmost_bool = topmost_bool

        try:
            self.iconphoto(False, icon_img)
        except Exception:
            pass

        self.update_idletasks()

    def __topmost_event(self, event):
        window_state = str(self.wm_state())
        if window_state == 'normal':
            if self.__topmost_bool == True:
                self.deiconify()
                self.attributes('-topmost', True)
            else:
                self.attributes('-topmost', False)

        elif window_state == 'zoomed':
            if self.__topmost_bool == True:
                self.attributes('-topmost', False)
            else:
                self.attributes('-topmost', False)

    def check_open(self):
        return self.__open_bool

    def open(self):
        self.deiconify()
        self.__open_bool = True
        if self.__topmost_bool == True:
            self.attributes('-topmost', True)
        else:
            self.attributes('-topmost', False)

    def show(self):
        window_state = str(self.wm_state())
        if window_state == 'normal':
            self.__open_bool = True
            self.deiconify()
            if self.__topmost_bool == True:
                self.attributes('-topmost', True)
            else:
                self.attributes('-topmost', False)

        elif window_state == 'zoomed':
            self.__open_bool = True
            self.deiconify()
            self.attributes('-topmost', False)

        else:
            self.__open_bool = True
            self.deiconify()
            if self.__topmost_bool == True:
                self.attributes('-topmost', True)
            else:
                self.attributes('-topmost', False)

    def custom_lift(self):
        self.lift()
        self.attributes('-topmost', True)
        self.after(15, self.__custom_lift_release)

    def __custom_lift_release(self):
        self.attributes('-topmost', False)
        self.deiconify()

    def close(self):
        self.grab_release()
        self.withdraw()
        self.__open_bool = False

        # Stop all CustomToplvl after event(s) when closing the CustomToplvl window.
        for event_id in self.__local_after_events:
            self.after_cancel(event_id)


    def custom_after(self, delay, func, *args):
        tk_thread_id = self.after(delay, func, *args)

        self.__local_after_events.append(tk_thread_id)
        all_after_events = list(self.tk.call('after', 'info')) # Will return ALL after events which are 'binded' to all existing widget(s).

        # Compare which after event(s) belong to CustomToplvl
        self.__local_after_events = [after_event for after_event in self.__local_after_events if after_event in all_after_events]

        return tk_thread_id


    def custom_after_idle(self, delay, func, *args):
        tk_thread_id = self.after_idle(delay, func, *args)
        
        self.__local_after_events.append(tk_thread_id)
        all_after_events = list(self.tk.call('after', 'info')) # Will return ALL after events which are 'binded' to all existing widget(s).

        # Compare which after event(s) belong to CustomToplvl
        self.__local_after_events = [after_event for after_event in self.__local_after_events if after_event in all_after_events]

        return tk_thread_id
        