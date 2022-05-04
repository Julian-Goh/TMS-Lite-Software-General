import os
from os import path

import tkinter as tk
import tkinter.messagebox

from PIL import Image, ImageTk

from functools import partial

from tkinter import ttk
from tkinter import filedialog
import numpy as np

from IVS_GUI.Gain_Offset import Gain_Offset
from IVS_GUI.Img_Threshold import Img_Threshold

from IVS_GUI.tk_tesseract import tk_Tesseract

from Tk_Custom_Widget.ScrolledCanvas import ScrolledCanvas
from Tk_Custom_Widget.tk_custom_combobox import CustomBox

from misc_module.os_create_folder import open_save_folder
from misc_module.image_resize import img_resize_dim, opencv_img_resize, pil_img_resize, open_pil_img
from misc_module.tk_img_module import to_tk_img
from misc_module.tool_tip import CreateToolTip

class ImgProc_GUI(tk.Frame):
    def __init__(self, master, scroll_class = None
        , gui_graphic = {}
        , tk_gui_bbox = None, **tk_kwargs):

        tk.Frame.__init__(self, master, **tk_kwargs)
        self.gui_fr = self

        self.tk_gui_bbox = tk_gui_bbox

        self.scroll_class = scroll_class

        self.gui_graphic = dict(  window_icon = None, popout_icon = None, fit_to_display_icon = None
                                , inspect_icon = None, help_icon = None
                                , add_icon = None, minus_icon = None, folder_icon = None
                                , toggle_on_icon = None, toggle_off_icon = None
                                , img_icon = None)

        for key, item in gui_graphic.items():
            if key in self.gui_graphic:
                self.gui_graphic[key] = item

        self.window_icon            = self.gui_graphic['window_icon']

        self.popout_icon            = to_tk_img(pil_img_resize(self.gui_graphic['popout_icon'], img_scale = 0.1))
        self.fit_to_display_icon    = to_tk_img(pil_img_resize(self.gui_graphic['fit_to_display_icon'], img_width = 22, img_height =22))
        self.inspect_icon           = to_tk_img(pil_img_resize(self.gui_graphic['inspect_icon'], img_scale = 0.025))
        self.help_icon              = to_tk_img(pil_img_resize(self.gui_graphic['help_icon'], img_width = 20, img_height =20))
        self.add_icon               = to_tk_img(pil_img_resize(self.gui_graphic['add_icon'], img_width = 18, img_height =18))
        self.minus_icon             = to_tk_img(pil_img_resize(self.gui_graphic['minus_icon'], img_width = 18, img_height =18))

        self.img_icon               = self.gui_graphic['img_icon']

        self.folder_icon            = to_tk_img(pil_img_resize(self.gui_graphic['folder_icon'], img_width = 24, img_height = 24))

        self.toggle_on_icon         = to_tk_img(pil_img_resize(self.gui_graphic['toggle_on_icon'], img_scale = 0.06))
        self.toggle_off_icon        = to_tk_img(pil_img_resize(self.gui_graphic['toggle_off_icon'], img_scale = 0.06))

        del self.gui_graphic
        

        ImgProc_GUI.gain_offset_win = Gain_Offset(self.gui_fr, self.scroll_class, popout_icon = self.popout_icon, fit_to_display_icon = self.fit_to_display_icon
            , img_icon = self.img_icon)

        ImgProc_GUI.threshold_win = Img_Threshold(self.gui_fr, self.scroll_class, popout_icon = self.popout_icon, fit_to_display_icon = self.fit_to_display_icon
            , toggle_on_icon = self.toggle_on_icon, toggle_off_icon = self.toggle_off_icon
            , img_icon = self.img_icon)

        ImgProc_GUI.ivs_ocr_win = tk_Tesseract(self.gui_fr, scroll_class = self.scroll_class
            , window_icon = self.window_icon, inspect_icon = self.inspect_icon
            , help_icon = self.help_icon
            , fit_to_display_icon = self.fit_to_display_icon
            , add_icon = self.add_icon, minus_icon = self.minus_icon
            , bg='white', bd = 0)
        
        self.__tool_gui_list = [ImgProc_GUI.gain_offset_win
            , ImgProc_GUI.threshold_win
            , ImgProc_GUI.ivs_ocr_win]

        self.__gui_switch_ret_arr = np.zeros((len(self.__tool_gui_list),), dtype = bool) ### array to store all switch protocol return values. If any value is True, we can prompt a msgbox. Currently, no plans to prompt a msgbox.

        self.mode_list = ['Gain/Offset', 'Threshold', 'IVS Blob + OCR']
        self.mode_select = CustomBox(self.gui_fr, values=self.mode_list, width=13, state='readonly', font = 'Helvetica 14')
        self.mode_select.unbind_class("TCombobox", "<MouseWheel>")
        self.mode_select.bind('<<ComboboxSelected>>', self.mode_select_func)

        self.mode_select.update_idletasks()

        self.mode_select.current(0)
        self.__curr_tool_id = 0 ### Initial value is 0 because mode select is 0

        self.mode_select.place(x=5, y=5)

        self.folder_dir_btn = tk.Button(self.gui_fr, relief = tk.GROOVE)#, width = 2, height = 1)
        self.folder_dir_btn['bg'] = 'gold'
        self.folder_dir_btn['command'] = partial(open_save_folder, folder_path = os.path.join(os.environ['USERPROFILE'],  "TMS_Saved_Images"), create_bool = True)
        self.folder_dir_btn['image'] = self.folder_icon
        CreateToolTip(self.folder_dir_btn, 'Open Save Folder'
            , 32, -5, font = 'Tahoma 11')
        self.folder_dir_btn.place(relx = 0, rely = 0, x = 180, y = 5, anchor = 'nw')

        self.mode_select_func()
        self.__tool_gui_list[self.__curr_tool_id].gui_resize_func()
        # ImgProc_GUI.gain_offset_win.place(x = 0, y = 30, relwidth = 1, relheight = 1, height = -30)
    
    def mode_select_func(self, event = None):
        switch_ret = False

        for i, tool_gui in enumerate(self.__tool_gui_list):
            try:
                self.__gui_switch_ret_arr[i] = self.__tool_gui_list[i].gui_switch_protocol()
            except AttributeError:
                self.__gui_switch_ret_arr[i] = 0
        
        switch_ret = np.any(self.__gui_switch_ret_arr)

        if switch_ret == False:
            if self.mode_select.get() == self.mode_list[0]: 
                """ GAIN/OFFSET TOOL """
                self.gui_fr['bg'] = 'SystemButtonFace'
                self.default_scroll_config()
                self.default_scroll_bind()

                id_num = int(0)
                self.interface_btn_control(self.__tool_gui_list, id_num
                    , dict(x=0, y=40, relwidth = 1, relheight = 1, height = -40))

                self.tk_gui_bbox.bind('<Configure>', lambda tk_event: self.__tool_gui_list[id_num].gui_bbox_event(event = tk_event))
                self.__tool_gui_list[id_num].gui_check_resize(tk_bbox = self.tk_gui_bbox)

                self.__curr_tool_id = id_num

            elif self.mode_select.get() == self.mode_list[1]:
                """ THRESHOLD TOOL """
                self.gui_fr['bg'] = 'SystemButtonFace'
                self.default_scroll_config()
                self.default_scroll_bind()

                id_num = int(1)
                self.interface_btn_control(self.__tool_gui_list, id_num
                    , dict(x=0, y=40, relwidth = 1, relheight = 1, height = -40))
                
                self.tk_gui_bbox.bind('<Configure>', lambda tk_event: self.__tool_gui_list[id_num].gui_bbox_event(event = tk_event))
                self.__tool_gui_list[id_num].gui_check_resize(tk_bbox = self.tk_gui_bbox)

                self.__curr_tool_id = id_num
                

            elif self.mode_select.get() == self.mode_list[2]:
                """ IVS BLOB+OCR TOOL """
                self.gui_fr['bg'] = 'white'
                self.default_scroll_config()
                self.default_scroll_bind()

                self.scroll_class.resize_frame(width = 970, height = 900)
                self.scroll_class.invoke_resize()

                id_num = int(2)

                self.interface_btn_control(self.__tool_gui_list, id_num
                    , dict(x=0, y=40, relwidth = 1, relheight = 1, height = -40))

                self.tk_gui_bbox.bind('<Configure>', lambda event: self.dummy_callback(event = event))

                self.__curr_tool_id = id_num

        else:
            self.mode_select.current(self.__curr_tool_id)


    def dummy_callback(self, event):
        pass

    def default_scroll_config(self):
        self.scroll_class.canvas.configure(yscrollcommand= self.scroll_class.scrolly.set)
        self.scroll_class.canvas.configure(xscrollcommand= self.scroll_class.scrollx.set)

    def default_scroll_bind(self):
        self.scroll_class.canvas.bind('<Enter>', self.scroll_class._bound_to_mousewheel)
        self.scroll_class.canvas.bind('<Leave>', self.scroll_class._unbound_to_mousewheel)

    def interface_btn_control(self, imgproc_gui_list, window_id, tk_place = {}):
        target_window = None

        try:
            target_window = imgproc_gui_list[window_id]
        except Exception:
            target_window = None

        if target_window is not None:
            for gui_window in imgproc_gui_list:
                if gui_window != target_window:
                    try:
                        gui_window.place_forget()
                    except (AttributeError, tk.TclError):
                        continue

                elif gui_window == target_window:
                    try:
                        if gui_window.winfo_exist()== 1:
                            pass
                        else:
                            if window_id == 0:
                                gui_window.place(tk_place)
                            else:
                                gui_window.place(tk_place)

                    except (AttributeError, tk.TclError):
                        if window_id == 0:
                            gui_window.place(tk_place)
                        else:
                            gui_window.place(tk_place)
