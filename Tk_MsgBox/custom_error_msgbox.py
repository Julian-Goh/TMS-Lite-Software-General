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

error_icon, err_src_img = _icon_load_resize(img_PATH = __location__, img_file = "error.png", img_width = 50, img_height = 50, copy_bool = True)
msg_box_err_icon = _pil_resize(err_src_img, img_scale = 0.15)

del err_src_img

class Error_Msgbox(tk.Toplevel):
    def __init__(self, message, parent = None, title = 'Error', width = None, height = None, font = 'Helvetica 11',
        message_anchor = 'nw', message_justify = tk.LEFT, parent_grab_set = False):

        if parent is None:
            tk.Toplevel.__init__(self)
        elif parent is not None:
            tk.Toplevel.__init__(self, master = parent)

        self.parent = parent
        self.parent_grab_set = parent_grab_set
        
        error_tk_icon = ImageTk.PhotoImage(error_icon)
        msg_box_tk_icon = ImageTk.PhotoImage(msg_box_err_icon)

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

        self.error_tk_icon_canvas = tk.Canvas(self.icon_frame, width = 60, height = 60, highlightthickness = 0)
        self.error_tk_icon_canvas['bg'] = default_bg
        self.error_tk_icon_canvas.place(relx=0.5, rely=0.2, x=0, y=0, anchor = 'n')
        self.error_tk_icon_canvas.update()
        self.error_tk_icon_canvas.create_image(self.error_tk_icon_canvas.winfo_width()/2, self.error_tk_icon_canvas.winfo_height()/2, image=error_tk_icon, anchor='center', tags='img')
        self.error_tk_icon_canvas.image = error_tk_icon

        self.error_msg_var = tk.StringVar()
        self.error_msg_label = WrappingLabel(self.msg_frame, font = self.msg_font, textvariable = self.error_msg_var, anchor= message_anchor, justify = message_justify, bd = 0)
        self.error_msg_label['bg'] = default_bg #blue'
        self.error_msg_label.place(relx=0, rely = 0 , x= 0, y = 10, relwidth = 1, relheight = 1, width = -15, height = -20, anchor = 'nw')
        self.error_msg_var.set(message)

        self.ok_btn = ResponsiveBtn(self.btn_frame, text = 'OK', justify = tk.CENTER, relief = tk.GROOVE, font = 'Helvetica 10')
        self.ok_btn['width'] = 10
        self.ok_btn['activebackground'] = 'light cyan'
        self.ok_btn['highlightthickness'] = 2
        self.ok_btn['highlightcolor'] = 'dodger blue'
        self.ok_btn['command'] = self._destroy
        self.ok_btn.place(relx = 1, rely =0, x = -35, y = 5, anchor = 'ne')

        self.msgbox_sound()
        
        # sound_thread_handle = threading.Thread(target=self.msgbox_sound, daemon = True)
        # sound_thread_handle.start()
        # sys.stdout.write('\a')
        # sys.stdout.flush()
        # print('\a')
        self.ok_btn.focus_set()

        self.bind('<Return>', lambda event: self.return_callback(event))
        self.bind('<Tab>', lambda event: self.btn_shift_focus(event))
        self.bind('<Left>', lambda event: self.btn_shift_focus(event))
        self.bind('<Right>', lambda event: self.btn_shift_focus(event))
        self.lift()  # Puts Window on top
        self.attributes("-topmost", True)
        self.grab_set()  # Prevents other Tkinter windows from being used

    def btn_shift_focus(self, event):
        self.ok_btn.focus_set()

    def return_callback(self, event):
        # print(self.focus_get())
        if self.focus_get() == self.ok_btn:
            self.ok_btn.invoke()

    def msgbox_sound(self):
        winsound.MessageBeep(winsound.MB_ICONHAND)

    def _destroy(self, event = None):
        self.destroy()
        if self.parent is not None:
            if self.parent.winfo_class() == 'Toplevel' and self.parent_grab_set == True:
                self.parent.grab_set()

    def destroy_protocol(self):
        self._destroy()