import os
from os import path

import sys
import winsound
import threading

import copy

import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

def _icon_load_resize(img_PATH, img_file, img_folder = None, img_scale = 0, img_width = 0, img_height = 0,
    img_conv = None, copy_bool = False):
    # print(img_PATH + "\\" + img_file)
    copy_img = None
    img = None

    if img_folder is not None and type(img_folder) == str:
        img = Image.open(img_PATH + "\\" + img_folder + "\\" + img_file)
    
    elif img_folder is None:
        img = Image.open(img_PATH + "\\" + img_file)

    if img_conv is not None:
        try:
            img = img.convert("RGBA")
        except Exception:
            pass
    #print(img_file, img.mode)

    if copy_bool == True:
        copy_img = copy.copy(img)

    if img_scale !=0 and (img_width == 0 and img_height == 0):
        img = img.resize((round(img.size[0]*img_scale), round(img.size[1]*img_scale)))
        # img = ImageTk.PhotoImage(img)

    if img_scale ==0 and (img_width != 0 and img_height != 0):
        img = img.resize((img_width, img_height))
        # img = ImageTk.PhotoImage(img)

    return img, copy_img

def _pil_resize(img, img_scale = 0, img_width = 0, img_height = 0):
    if img_scale !=0 and (img_width == 0 and img_height == 0):
        img = img.resize((round(img.size[0]*img_scale), round(img.size[1]*img_scale)))

    if img_scale ==0 and (img_width != 0 and img_height != 0):
        img = img.resize((img_width, img_height))

    return img

class WrappingLabel(tk.Label):
    '''a type of Label that automatically adjusts the wrap to the size'''
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))

class ResponsiveBtn(tk.Button):
    def __init__(self, master=None, **kwargs):
        tk.Button.__init__(self, master, **kwargs)
        bindings = {
                    '<FocusIn>': {'default':'active'},    # for Keyboard focus
                    '<FocusOut>': {'default': 'normal'},  
                    '<Enter>': {'state': 'active'},       # for Mouse focus
                    '<Leave>': {'state': 'normal'}
                    }
        for k, v in bindings.items():
            self.bind(k, lambda e, kwarg=v: e.widget.config(**kwarg))

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
# print(__location__)

ask_icon, ask_src_img = _icon_load_resize(img_PATH = __location__, img_file = "ask.png", img_width = 45, img_height = 45, copy_bool = True)
warning_icon, warn_src_img = _icon_load_resize(img_PATH = __location__, img_file = "warning.png", img_width = 50, img_height = 50, copy_bool = True)
error_icon, err_src_img = _icon_load_resize(img_PATH = __location__, img_file = "error.png", img_width = 50, img_height = 50, copy_bool = True)

msg_box_ask_icon = _pil_resize(ask_src_img, img_scale = 0.15)
msg_box_warn_icon = _pil_resize(warn_src_img, img_scale = 0.15)
msg_box_err_icon = _pil_resize(err_src_img, img_scale = 0.15)

del ask_src_img, warn_src_img, err_src_img

class Ask_Msgbox(tk.Toplevel):
    def __init__(self, message, parent, title = '', width = None, height = None, font = 'Helvetica 11',
        message_anchor = 'nw', message_justify = tk.LEFT, mode = 'default', parent_grab_set = False, ask_OK = True):

        tk.Toplevel.__init__(self, master = parent)
        self.parent = parent
        self.parent_grab_set = parent_grab_set
        
        if mode == 'warning':
            ask_tk_icon = ImageTk.PhotoImage(warning_icon)
            msg_box_tk_icon = ImageTk.PhotoImage(msg_box_warn_icon)

        elif mode == 'error':
            ask_tk_icon = ImageTk.PhotoImage(error_icon)
            msg_box_tk_icon = ImageTk.PhotoImage(msg_box_err_icon)

        else:
            ask_tk_icon = ImageTk.PhotoImage(ask_icon)
            msg_box_tk_icon = ImageTk.PhotoImage(msg_box_ask_icon)

        self.__result_bool = False #NO: False, YES: True

        self.resizable(0,0)
        default_bg = 'white'
        self['bg'] = default_bg
        self.title(title)
        toplvl_W = 300
        toplvl_H = 150

        if width is not None and type(width) == int:
            toplvl_W = max(width, toplvl_W)

        if height is not None and type(height) == int:
            toplvl_H = max(height, toplvl_H)

        self['width'] = toplvl_W
        self['height'] = toplvl_H

        self.msg_font = font
        
        self.minsize(width=toplvl_W, height=toplvl_H)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = int((screen_width/2) - (toplvl_W/2))
        y_coordinate = int((screen_height/2) - (toplvl_H/2))
        self.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
        self.protocol("WM_DELETE_WINDOW", self.destroy_protocol)
        self.iconphoto(False, msg_box_tk_icon)

        self.icon_frame = tk.Frame(self)
        self.icon_frame['width'] = 80
        self.icon_frame['bg'] = default_bg #'orange' # default_bg
        self.icon_frame.place(relx=0, rely=0, x=0, y=0, relheight = 1, height = -40)

        self.msg_frame = tk.Frame(self)
        self.msg_frame['bg'] = default_bg # 'purple' # default_bg
        self.msg_frame.place(relx=0, rely=0, x=80, y=0, relwidth = 1, relheight = 1, width = -80, height = -40)

        self.btn_frame = tk.Frame(self)
        self.btn_frame['height'] = 40
        self.btn_frame.place(relx=0, rely=1, x=0, y=-40, relwidth = 1)

        self.ask_tk_icon_canvas = tk.Canvas(self.icon_frame, width = 60, height = 60, highlightthickness = 0)
        self.ask_tk_icon_canvas['bg'] = default_bg
        self.ask_tk_icon_canvas.place(relx=0.5, rely=0.2, x=0, y=0, anchor = 'n')
        self.ask_tk_icon_canvas.update()
        self.ask_tk_icon_canvas.create_image(self.ask_tk_icon_canvas.winfo_width()/2, self.ask_tk_icon_canvas.winfo_height()/2, image=ask_tk_icon, anchor='center', tags='img')
        self.ask_tk_icon_canvas.image = ask_tk_icon

        self.ask_msg_var = tk.StringVar()
        self.ask_msg_label = WrappingLabel(self.msg_frame, font = self.msg_font, textvariable = self.ask_msg_var, anchor= message_anchor, justify = message_justify, bd = 0)
        self.ask_msg_label['bg'] = default_bg #'blue'
        self.ask_msg_label.place(relx=0, rely = 0 , x= 0, y = 10, relwidth = 1, relheight = 1, width = -15, height = -20, anchor = 'nw')
        self.ask_msg_var.set(message)

        self.yes_btn = ResponsiveBtn(self.btn_frame, text = 'YES', justify = tk.CENTER, relief = tk.GROOVE, font = 'Helvetica 10')
        self.yes_btn['width'] = 10
        self.yes_btn['activebackground'] = 'light cyan'
        self.yes_btn['highlightthickness'] = 2
        self.yes_btn['highlightcolor'] = 'dodger blue'
        self.yes_btn['command'] = lambda: self.update_ask_result(self.yes_btn)
        self.yes_btn.place(relx = 1, rely =0, x = -135, y = 5, anchor = 'ne')

        self.no_btn = ResponsiveBtn(self.btn_frame, text = 'NO', justify = tk.CENTER, relief = tk.GROOVE, font = 'Helvetica 10')
        self.no_btn['width'] = 10
        self.no_btn['activebackground'] = 'light cyan'
        self.no_btn['highlightthickness'] = 2
        self.no_btn['highlightcolor'] = 'dodger blue'
        self.no_btn['command'] = lambda: self.update_ask_result(self.no_btn)

        self.no_btn.place(relx = 1, rely =0, x = -35, y = 5, anchor = 'ne')

        # sound_thread_handle = threading.Thread(target=self.msgbox_sound, daemon = True)
        # sound_thread_handle.start()
        self.msgbox_sound()
        # sys.stdout.write('\a')
        # sys.stdout.flush()
        # print('\a')
        if ask_OK == True:
            self.yes_btn.focus_set()
        elif ask_OK == False:
            self.no_btn.focus_set()

        self.bind('<Return>', lambda event: self.return_callback(event))
        self.bind('<Tab>', lambda event: self.btn_shift_focus(event))
        self.bind('<Left>', lambda event: self.btn_shift_focus(event))
        self.bind('<Right>', lambda event: self.btn_shift_focus(event))
        self.lift()  # Puts Window on top
        self.attributes("-topmost", True)
        self.grab_set()  # Prevents other Tkinter windows from being used
        try:
            self.parent.wait_window(self)
        finally:
            self.grab_release()
            if self.parent.winfo_class() == 'Tk':
                self.parent.focus_force()

    def btn_shift_focus(self, event):
        if self.focus_get() == self.yes_btn:
            self.no_btn.focus_set()
        elif self.focus_get() == self.no_btn:
            self.yes_btn.focus_set()

        else:
            self.yes_btn.focus_set()

    def return_callback(self, event):
        # print(self.focus_get())
        if self.focus_get() == self.yes_btn:
            self.yes_btn.invoke()
        elif self.focus_get() == self.no_btn:
            self.no_btn.invoke()

    def msgbox_sound(self):
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
        # self.parent.bell() #if self.parent is tk.Root()

    def update_ask_result(self, btn_widget, event = None):
        if btn_widget == self.yes_btn:
            self.__result_bool = True
            self._destroy() #Close the Top-level window
        else:
            self.__result_bool = False
            self._destroy() #Close the Top-level window

    def ask_result(self):
        return self.__result_bool

    def _destroy(self, event = None):
        self.destroy()
        # print(self.parent.winfo_class())
        if self.parent.winfo_class() == 'Toplevel' and self.parent_grab_set == True:
            self.parent.grab_set()

        elif self.parent.winfo_class() == 'Tk':
            self.parent.focus_force()

    def destroy_protocol(self):
        self.__result_bool = False
        self._destroy()