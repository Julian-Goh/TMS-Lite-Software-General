import tkinter as tk

from PIL import ImageTk, Image, ImageDraw, ImageFont
import os 
from os import path
import pathlib

from datetime import datetime
import math

from tkinter import ttk
from tkinter import filedialog
import numpy as np
import cv2

from tesserocr import get_languages
from tesserocr import PyTessBaseAPI, PSM, OEM, RIL
import tesserocr

import threading

from functools import partial
from imageio import imread
import imutils

from Tk_Custom_Widget.ScrolledCanvas import ScrolledCanvas
from Tk_Custom_Widget.custom_zoom_class import CanvasImage

from Tk_MsgBox.custom_msgbox import Ask_Msgbox, Info_Msgbox, Error_Msgbox, Warning_Msgbox

from misc_module.os_create_folder import create_save_folder
from misc_module.tool_tip import CreateToolTip
from misc_module.TMS_file_save import cv_img_save, pil_img_save, PDF_img_save, PDF_img_list_save, np_to_PIL

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
root_path = os.getcwd()

def pil_padding_constant(pil_img, pad_left = 0, pad_top = 0, pad_right = 0, pad_btm = 0):
    np_img = np.array(pil_img)
    pad_left, pad_top, pad_right, pad_btm = abs(pad_left), abs(pad_top), abs(pad_right), abs(pad_btm)

    if len(np_img.shape) > 2:
        if np_img.shape[2] == 3:
            np_img = cv2.copyMakeBorder(np_img,
            left = pad_left, top = pad_top, right = pad_right, bottom = pad_btm,
            borderType = cv2.BORDER_CONSTANT, value=[255, 255, 255])

        elif np_img.shape[2] == 4:
            np_img = cv2.cvtColor(np_img, cv2.COLOR_BGRA2BGR)
            np_img = cv2.copyMakeBorder(np_img,
            left = pad_left, top = pad_top, right = pad_right, bottom = pad_btm,
            borderType = cv2.BORDER_CONSTANT, value=[255, 255, 255])

    else:
        np_img = cv2.copyMakeBorder(np_img,
        left = pad_left, top = pad_top, right = pad_right, bottom = pad_btm,
        borderType = cv2.BORDER_CONSTANT, value=[255])

    pil_img = Image.fromarray(np_img)
    return pil_img

def validate_int_entry(d, P, S, only_positive = 'False'):
    # valid percent substitutions (from the Tk entry man page)
    # note: you only have to register the ones you need; this
    # example registers them all for illustrative purposes
    #
    # %d = Type of action (1=insert, 0=delete, -1 for others)
    # %i = index of char string to be inserted/deleted, or -1
    # %P = value of the entry if the edit is allowed
    # %s = value of entry prior to editing
    # %S = the text string being inserted or deleted, if any
    # %v = the type of validation that is currently set
    # %V = the type of validation that triggered the callback
    #      (key, focusin, focusout, forced)
    # %W = the tk name of the widget
    #print(only_positive, type(only_positive))
    if only_positive == 'False':
        if d == '1':
            if S == '-' and P == '-':
                return True 
            if P == '-0':
                return False
            if len(P) > 1 and (P.split('0')[0]) == '':
                return False
            else:
                try:
                    int(P)
                    return True
                except:
                    if P == '':
                        return True
                    else:
                        return False
        elif d == '0':
            return True

    elif only_positive == 'True':
        if d == '1':
            if len(P) > 1 and (P.split('0')[0]) == '':
                return False
            else:
                try:
                    int(P)
                    return True
                except:
                    if P == '':
                        return True
                    else:
                        return False
        elif d == '0':
            return True

def validate_float_entry(d, P, S, decimal_places = None):
    # valid percent substitutions (from the Tk entry man page)
    # note: you only have to register the ones you need; this
    # example registers them all for illustrative purposes
    #
    # %d = Type of action (1=insert, 0=delete, -1 for others)
    # %i = index of char string to be inserted/deleted, or -1
    # %P = value of the entry if the edit is allowed
    # %s = value of entry prior to editing
    # %S = the text string being inserted or deleted, if any
    # %v = the type of validation that is currently set
    # %V = the type of validation that triggered the callback
    #      (key, focusin, focusout, forced)
    # %W = the tk name of the widget
    #print(decimal_places, type(decimal_places)) #decimal_places
    try:
        int(decimal_places)
        if int(decimal_places) == 0: #decimal places cannot be 0
            decimal_places = None
    except (ValueError, TypeError):
        decimal_places = None
    #print('decimal_places: ',decimal_places)
    if decimal_places is None:
        if d == '1':
            try:
                #print(P)
                float(P)
                if float(P) >= 0 and S != '-': 
                    if len(P.split('.')) > 1 and len(P.split('.')[1]) > 2: #Default decimal places is 2
                        return False
                    return True
                else:
                    return False
            except ValueError:
                if not P:
                    return True
                else:
                    return False
        # elif d =='0':
        #     if i == '0' and P != '' and (P.split('.'))[0] == '': #Prevent user from deleting the 1st and only digit in front of a decimal point
        #         return False
        #     return True
        else:
            return True

    elif decimal_places is not None: #float check with significant figure check
        if d == '1':
            try:
                float(P)
                if float(P) >= 0 and S != '-':
                    if len(P.split('.')) > 1 and len(P.split('.')[1]) > int(decimal_places):
                        return False
                    return True
                else:
                    return False
            except ValueError:
                if not P:
                    return True
                else:
                    return False
        else:
            return True

def focusout_func(widget, val):
    if widget.get() == '':
        widget.insert(0, str(val))
    else:
        pass

class tk_Tesseract(tk.Frame):
    def __init__(self, master, scroll_class = None
        , window_icon = None, inspect_icon = None
        , help_icon = None
        , fit_to_display_icon = None
        , add_icon = None, minus_icon = None
        , **kwargs):

        tk.Frame.__init__(self, master, highlightthickness = 0, **kwargs)
        self.img_format_list = [("All Files","*.bmp *.jpg *.jpeg *.png *.tiff"),
                                ('BMP file', '*.bmp'),
                                ('JPG file', '*.jpg'),
                                ('JPEG file', '*.jpeg'),
                                ('PNG file', '*.png'),
                               ('TIFF file', '*.tiff')]
                               
        self.window_icon = window_icon
        self.inspect_icon = inspect_icon
        self.help_icon = help_icon
        self.fit_to_display_icon = fit_to_display_icon
        self.add_icon = add_icon
        self.minus_icon = minus_icon

        self.img_disp_frame = tk.Frame(self)

        # self.img_disp_frame.place(x=0, y=30, relwidth = 0.45, relheight = 1,anchor = 'nw')
        
        # self.ctrl_panel_scroll_class = scroll_class
        # self.ctrl_panel_frame = tk.Frame(self, bg = 'white')
        # self.ctrl_panel_frame.place(relx= 0.475, y= 30, relheight = 1, relwidth = 0.525, anchor = 'nw')

        self.img_disp_frame.place(x=0, y=30, relwidth = 0.55, relheight = 1,anchor = 'nw')
        
        self.ctrl_panel_scroll_class = scroll_class
        self.ctrl_panel_frame = tk.Frame(self, bg = 'white')
        self.ctrl_panel_frame.place(relx= 0.55, rely = 0, x= 20, y= 30, relheight = 1, relwidth = 0.45, anchor = 'nw')

        self.img_file = None
        self.img_imageio = None

        self.new_img_bool = False
        self.img_disp = None
        self.ivs_roi_img_toplvl = None
        self.roi_disp = None
        self.curr_roi_mode = None

        self.__save_dir = os.path.join(os.environ['USERPROFILE'],  "TMS_Saved_Images")
        self.__load_curr_dir = os.path.join(os.environ['USERPROFILE'],  "TMS_Saved_Images")
        #######################################################################################
        tessdata_path = root_path + '\\tessdata\\'
        lang = 'eng'
        psm = PSM.SINGLE_BLOCK
        oem = OEM.TESSERACT_LSTM_COMBINED #OEM.LSTM_ONLY #OEM.TESSERACT_LSTM_COMBINED
        os.environ['OMP_THREAD_LIMIT'] = '1' ## Comment: Limit OpenMP number of threads
        get_languages(tessdata_path)
        self.tess_api = PyTessBaseAPI(path = tessdata_path
                    , lang = lang
                    , psm = psm, oem = oem)

        """psm = An enum that defines all available page segmentation modes.
        Attributes:
            OSD_ONLY: Orientation and script detection only.
            AUTO_OSD: Automatic page segmentation with orientation and script detection. (OSD)
            AUTO_ONLY: Automatic page segmentation, but no OSD, or OCR.
            AUTO: Fully automatic page segmentation, but no OSD. (:mod:`tesserocr` default)
            SINGLE_COLUMN: Assume a single column of text of variable sizes.
            SINGLE_BLOCK_VERT_TEXT: Assume a single uniform block of vertically aligned text.
            SINGLE_BLOCK: Assume a single uniform block of text.
            SINGLE_LINE: Treat the image as a single text line.
            SINGLE_WORD: Treat the image as a single word.
            CIRCLE_WORD: Treat the image as a single word in a circle.
            SINGLE_CHAR: Treat the image as a single character.
            SPARSE_TEXT: Find as much text as possible in no particular order.
            SPARSE_TEXT_OSD: Sparse text with orientation and script det.
            RAW_LINE: Treat the image as a single text line, bypassing hacks that are Tesseract-specific.
            COUNT: Number of enum entries.
        """

        """oem: An enum that defines available OCR engine modes.
        Attributes:
            TESSERACT_ONLY: Run Tesseract only - fastest
            LSTM_ONLY: Run just the LSTM line recognizer. (>=v4.00)
            TESSERACT_LSTM_COMBINED: Run the LSTM recognizer, but allow fallback
                to Tesseract when things get difficult. (>=v4.00)
            CUBE_ONLY: Specify this mode when calling Init*(), to indicate that
                any of the above modes should be automatically inferred from the
                variables in the language-specific config, command-line configs, or
                if not specified in any of the above should be set to the default
                `OEM.TESSERACT_ONLY`.
            TESSERACT_CUBE_COMBINED: Run Cube only - better accuracy, but slower.
            DEFAULT: Run both and combine results - best accuracy.
        """

        self.ivs_ocr_enable_bool = False
        self.ivs_save_bool = False
        ##########################################
        #These 2 parameters are only used for IVS_OCR_tag_adjust function to move around the OCR tag in the display
        self.ocr_tag_param_list = None
        self.ocr_draw_bool = False
        ##########################################
        self.previous_morph_kernel = 0 #0: Rectangle, 1: Ellipse, or 2: Cross
        #######################################################################################
        self.roi_widget()

        self.roi_checkbtn['state'] = 'disable'
        self.ctrl_panel_widget()

        self.img_disp = CanvasImage(self.img_disp_frame, tess_api = self.tess_api)
        self.img_disp.place(x=0, y=0, relwidth = 1, relheight = 1, anchor = 'nw')

        try:
            self.img_disp.canvas.bind('<Leave>', self.ctrl_panel_scroll_class._bound_to_mousewheel)
        except Exception:
            pass

        self.np_arr_blob_load()
        self.np_arr_ocr_load()

        # self.fit_to_display_btn = tk.Button(self, relief = tk.GROOVE, width = 2, height = 1)
        self.fit_to_display_btn = tk.Button(self, relief = tk.GROOVE, image = self.fit_to_display_icon
            ,bd = 0, bg = 'white')
        CreateToolTip(self.fit_to_display_btn, 'Fit-to-Screen'
                    , 30, 0, width = 80, height = 20)
        self.fit_to_display_btn['command'] = None
        self.fit_to_display_btn.place(x=210, y = 0 + 2)

        self.help_widget = tk.Label(self, bg = 'white', image = self.help_icon)
        CreateToolTip(self.help_widget, '1. LEFT-CLICK Mouse & Drag\n   to Move Image inside Image Display.\n' +
                                        '2. RIGHT-CLICK Mouse & Drag\n   to Draw ROI Box (with ROI enabled).\n' +
                                        '3. MOUSEWHEEL-UP to Zoom In.\n' +
                                        '4. MOUSEWHEEL-DOWN to Zoom Out.'
                    ,30, 0, width = 240, height = 100)
        # self.help_widget.place(relx = 0.3, y = 0 + 2)
        self.help_widget.place(x = 240, y = 0 + 2)

    def np_arr_blob_load(self):
        if self.img_disp is not None:
            self.ivs_blob_min_size_var.set(self.img_disp.ivs_blob_param[0]) #min size
            self.ivs_blob_max_size_var.set(self.img_disp.ivs_blob_param[1]) #max size
            self.ivs_blob_lo_th_var.set(self.img_disp.ivs_blob_param[2]) #lower th
            self.ivs_blob_hi_th_var.set(self.img_disp.ivs_blob_param[3]) #upper th
            self.ivs_bbox_outline_var.set(self.img_disp.ivs_blob_param[4]) #Box outline thickness

        if self.img_disp is None:
            self.ivs_blob_min_size_var.set(100) #min size
            self.ivs_blob_max_size_var.set(1000) #max size
            self.ivs_blob_lo_th_var.set(0) #lower th
            self.ivs_blob_hi_th_var.set(0) #upper th
            self.ivs_bbox_outline_var.set(2) #upper th

        self.ivs_blob_min_size_spinbox['validate']='key'
        self.ivs_blob_min_size_spinbox['vcmd']=(self.ivs_blob_min_size_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)
        self.ivs_blob_max_size_spinbox['validate']='key'
        self.ivs_blob_max_size_spinbox['vcmd']=(self.ivs_blob_max_size_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)
        self.ivs_blob_lo_th_spinbox['validate']='key'
        self.ivs_blob_lo_th_spinbox['vcmd']=(self.ivs_blob_lo_th_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)
        self.ivs_blob_hi_th_spinbox['validate']='key'
        self.ivs_blob_hi_th_spinbox['vcmd']=(self.ivs_blob_hi_th_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)
        self.ivs_bbox_outline_spinbox['validate']='key'
        self.ivs_bbox_outline_spinbox['vcmd']=(self.ivs_bbox_outline_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)

    def np_arr_ocr_load(self):
        if self.img_disp is not None:
            self.OCR_shift_x_var.set(int(self.img_disp.ivs_ocr_label_param[0])) #shift x
            self.OCR_shift_y_var.set(int(self.img_disp.ivs_ocr_label_param[1])) #shift y
            self.OCR_font_size_var.set(self.img_disp.ivs_ocr_label_param[2]) #font size

        if self.img_disp is None:
            self.OCR_shift_x_var.set(0) #shift x
            self.OCR_shift_y_var.set(0) #shift y
            self.OCR_font_size_var.set(18) #font size

        self.OCR_shift_x_spinbox['validate']='key'
        self.OCR_shift_x_spinbox['vcmd']=(self.OCR_shift_x_spinbox.register(validate_int_entry), '%d', '%P', '%S', False)
        self.OCR_shift_y_spinbox['validate']='key'
        self.OCR_shift_y_spinbox['vcmd']=(self.OCR_shift_y_spinbox.register(validate_int_entry), '%d', '%P', '%S', False)
        self.OCR_font_size_spinbox['validate']='key'
        self.OCR_font_size_spinbox['vcmd']=(self.OCR_font_size_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)

    def ctrl_panel_widget(self):
        self.load_img_stringvar = tk.StringVar(value = 'Image File: ')
        tk.Label(self.ctrl_panel_frame, font = 'Helvetica 11', textvariable = self.load_img_stringvar, bg = 'white').place(x = 120, y = 3)
        self.load_img_btn = tk.Button(self.ctrl_panel_frame, relief = tk.GROOVE, font = 'Helvetica 11', text = 'Load Image')
        self.load_img_btn['bd'] = 2
        self.load_img_btn['width'] = 12
        self.load_img_btn.place(x = 0, y = 0)
        self.load_img_btn['command'] = self.load_img_func

        self.save_img_btn = tk.Button(self.ctrl_panel_frame, relief = tk.GROOVE, font = 'Helvetica 11', text = 'Save Image')
        self.save_img_btn['bd'] = 2
        self.save_img_btn['width'] = 12
        self.save_img_btn.place(x = 0, y = 33)
        self.save_img_btn['command'] = self.save_img_func

        label_save_img_format = tk.Label(self.ctrl_panel_frame, text = 'Image Format: ', font = 'Helvetica 11', bg = 'white')
        self.save_img_format_list = ['.bmp', '.png', '.jpg', '.tiff', '.pdf']
        self.ctrl_panel_frame.option_add('*TCombobox*Listbox.font', ('Helvetica', '11'))
        self.save_img_format_sel = ttk.Combobox(self.ctrl_panel_frame, values=self.save_img_format_list, width=5, state='readonly', font = 'Helvetica 11')
        self.save_img_format_sel.unbind_class("TCombobox", "<MouseWheel>")
        self.save_img_format_sel.current(0)
        label_save_img_format.place(x=120,  y=36)
        self.save_img_format_sel.place(x=220, y=36)

        self.blob_panel_init()

        self.ivs_ocr_enable_bool_var = tk.IntVar(value = 0) 
        self.ivs_ocr_enable_checkbtn = tk.Checkbutton(self.ctrl_panel_frame, text='OCR Enable', bg = 'white'
            , variable = self.ivs_ocr_enable_bool_var, onvalue=1, offvalue=0, font = 'Helvetica 10')
        self.ivs_ocr_enable_checkbtn['command'] = partial(self.OCR_enable_func, self.ivs_ocr_enable_bool_var)

        self.ivs_ocr_enable_checkbtn.place(x=0, y = 130-60 + 250 + 40)

        self.morph_panel_init()

        self.result_panel_init()

        self.ocr_setting_widget_forget()

    def ocr_setting_widget_forget(self):
        self.ivs_morph_panel.place_forget()
        self.ivs_ocr_result_frame.place_forget()

    def ocr_setting_widget_place(self):
        self.ivs_morph_panel.place(relx=0, rely = 0, x = 0, y = 30 + 250 + 40 + 40 + 40)
        self.ivs_ocr_result_frame.place(relx=0, rely = 0, x = 0, y = 30 + 250 + 250 + 40 + 40 + 40)

    def OCR_enable_func(self, bool_tk_var):
        if bool_tk_var.get() == 0:
            self.ocr_setting_widget_forget()
            self.ivs_ocr_enable_bool = False

            self.IVS_OCR_start()

        elif bool_tk_var.get() == 1:
            self.ocr_setting_widget_place()
            self.ivs_ocr_enable_bool = True

            self.IVS_OCR_start()

    def popout_roi_gen(self,toplvl_W, toplvl_H, toplvl_title):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.ivs_roi_img_toplvl)
            if check_bool == 0:
                self.ivs_roi_img_toplvl = tk.Toplevel(self, width = toplvl_W, height = toplvl_H)
                self.ivs_roi_img_toplvl.resizable(0,0)
                self.ivs_roi_img_toplvl['bg'] = 'white'
                self.ivs_roi_img_toplvl.title(toplvl_title)
                self.ivs_roi_img_toplvl.minsize(width=toplvl_W, height=toplvl_H)

                screen_width = self.ivs_roi_img_toplvl.winfo_screenwidth()
                screen_height = self.ivs_roi_img_toplvl.winfo_screenheight()
                x_coordinate = int((screen_width/2) - (toplvl_W/2))
                y_coordinate = int((screen_height/2) - (toplvl_H/2))
                self.ivs_roi_img_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
                self.ivs_roi_img_toplvl.attributes("-topmost", True)
                try:
                    self.ivs_roi_img_toplvl.iconphoto(False, self.window_icon)
                except Exception:
                    pass

                self.popout_roi_init()
                self.IVS_OCR_start()

            else:
                self.ivs_roi_img_toplvl.deiconify()
                self.ivs_roi_img_toplvl.lift()
                

        except (AttributeError, tk.TclError):
            self.ivs_roi_img_toplvl = tk.Toplevel(self, width = toplvl_W, height = toplvl_H)
            self.ivs_roi_img_toplvl.resizable(0,0)
            self.ivs_roi_img_toplvl['bg'] = 'white'
            self.ivs_roi_img_toplvl.title(toplvl_title)
            self.ivs_roi_img_toplvl.minsize(width=toplvl_W, height=toplvl_H)

            screen_width = self.ivs_roi_img_toplvl.winfo_screenwidth()
            screen_height = self.ivs_roi_img_toplvl.winfo_screenheight()
            x_coordinate = int((screen_width/2) - (toplvl_W/2))
            y_coordinate = int((screen_height/2) - (toplvl_H/2))
            self.ivs_roi_img_toplvl.geometry("{}x{}+{}+{}".format(toplvl_W, toplvl_H, x_coordinate, y_coordinate))
            self.ivs_roi_img_toplvl.attributes("-topmost", True)

            try:
                self.ivs_roi_img_toplvl.iconphoto(False, self.window_icon)
            except Exception:
                pass

            self.popout_roi_init()
            self.IVS_OCR_start()

    def popout_roi_init(self):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.ivs_roi_img_toplvl)
            if check_bool == 0:
                pass
            else:
                self.roi_disp = CanvasImage(self.ivs_roi_img_toplvl)
                self.roi_disp.place(x=0, y=28, relwidth = 1, relheight = 1, anchor = 'nw')
                # self.roi_fit_to_screen_btn = tk.Button(self.ivs_roi_img_toplvl, relief = tk.GROOVE, width = 2, height  =1)
                self.roi_fit_to_screen_btn = tk.Button(self.ivs_roi_img_toplvl, relief = tk.GROOVE, image = self.fit_to_display_icon
                    , bd = 0, bg = 'white')
                CreateToolTip(self.roi_fit_to_screen_btn, 'Fit-to-Screen'
                    , 30, 0, width = 80, height = 20)

                self.roi_fit_to_screen_btn['command'] = lambda: self.roi_disp.fit_to_display(self.ivs_roi_img_toplvl.winfo_width(), self.ivs_roi_img_toplvl.winfo_height()-28)

                self.roi_fit_to_screen_btn.place(x=2,y=0 + 2)

        except (AttributeError, tk.TclError) as e:
            print('tk_Tesseract, popout_roi_init(): ', e)
            pass
    
    def popout_roi_load_disp(self, img_array):
        try:
            check_bool = tk.Toplevel.winfo_exists(self.ivs_roi_img_toplvl)
            if check_bool == 0:
                pass
            else:

                self.roi_disp.canvas_default_load(img = img_array
                    , fit_to_display_bool = True, display_width = self.ivs_roi_img_toplvl.winfo_width(), display_height = self.ivs_roi_img_toplvl.winfo_height()-28)

        except (AttributeError, tk.TclError):# as e:
            # print('tk_Tesseract, popout_roi_load_disp(): ', e)
            pass

    def blob_panel_init(self):
        self.ivs_blob_frame = tk.Frame(self.ctrl_panel_frame, highlightthickness = 1, highlightbackground = 'black')
        self.ivs_blob_frame['width'] = 270 +25
        self.ivs_blob_frame['height'] = 120 + 10 + 30 + 30 + 30 + 30 + 30
        self.ivs_blob_frame.place(x=0, y = 130 - 60)

        frame = self.ivs_blob_frame

        # self.ivs_roi_popout_btn = tk.Button(frame, relief = tk.GROOVE, width =2 , height= 1)
        self.ivs_roi_popout_btn = tk.Button(frame, relief = tk.GROOVE, image = self.inspect_icon)
        CreateToolTip(self.ivs_roi_popout_btn, 'Inspect ROI Image'
                    , 30-10, -20, width = 110, height = 20)
        self.ivs_roi_popout_btn['command'] = lambda : self.popout_roi_gen(330, 230, 'ROI Image')
        self.ivs_roi_popout_btn.place(x = 120 - 20, y = 2 + 2)

        tk.Label(frame, text = 'Blob Search:', font = 'Helvetica 11').place(x=0 ,y=0)

        tk.Label(frame, font = 'Helvetica 10 bold italic', text = 'No. of Blob Detected:').place(x=10, y = 27)
        self.blob_num_detect_var = tk.StringVar(value = 0)
        self.blob_num_detect_label = tk.Label(frame, font = 'Helvetica 11 bold', textvariable = self.blob_num_detect_var)
        self.blob_num_detect_label.place(x=145, y=26)

        tk.Label(frame, text = 'Min. Blob Size (Pixel):', font = 'Helvetica 10').place(x=10 ,y= 49+10)
        tk.Label(frame, text = 'Max. Blob Size (Pixel):', font = 'Helvetica 10').place(x=10 ,y=49 + 30+10)
        tk.Label(frame, text = 'Lower Binary Threshold:', font = 'Helvetica 10').place(x=10 ,y=49 + 30 + 30+10)
        tk.Label(frame, text = 'Upper Binary Threshold:', font = 'Helvetica 10').place(x=10 ,y=49 + 30 + 30 + 30+10)
        tk.Label(frame, text = 'Detection Box Outline:', font = 'Helvetica 10').place(x=10 ,y=49 + 30+30+30+30+30+30+10)


        self.ivs_blob_min_size_var = tk.StringVar(value = 100)
        self.ivs_blob_min_size_spinbox = tk.Spinbox(frame, width = 7, textvariable = self.ivs_blob_min_size_var ,from_= 0, to = 1000000, increment = 1
                                    , highlightbackground="black", highlightthickness=1, font = 'Helvetica 10')
        self.ivs_blob_min_size_spinbox['validate']='key'
        self.ivs_blob_min_size_spinbox['vcmd']=(self.ivs_blob_min_size_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)

        self.ivs_blob_min_size_spinbox['command'] = lambda: self.BLOB_spinbox_func(self.ivs_blob_min_size_spinbox, self.ivs_blob_min_size_var, 1, 1000000, only_positive = True, np_index = 0)

        self.ivs_blob_min_size_spinbox.bind('<Tab>', lambda event: self.BLOB_spinbox_func(self.ivs_blob_min_size_spinbox, self.ivs_blob_min_size_var, 1, 1000000, only_positive = True, np_index = 0))
        self.ivs_blob_min_size_spinbox.bind('<Return>', lambda event: self.BLOB_spinbox_func(self.ivs_blob_min_size_spinbox, self.ivs_blob_min_size_var, 1, 1000000, only_positive = True, np_index = 0))
        self.ivs_blob_min_size_spinbox.bind('<KeyRelease>', lambda event: self.BLOB_spinbox_func(self.ivs_blob_min_size_spinbox, self.ivs_blob_min_size_var, 1, 1000000, only_positive = True, np_index = 0))
        self.ivs_blob_min_size_spinbox.bind('<FocusOut>', lambda event: self.BLOB_spinbox_focus_out(self.ivs_blob_min_size_var))

        self.ivs_blob_max_size_var = tk.StringVar(value = 1000)
        self.ivs_blob_max_size_spinbox = tk.Spinbox(frame, width = 7, textvariable = self.ivs_blob_max_size_var ,from_= 0, to = 1000000, increment = 1
                                    , highlightbackground="black", highlightthickness=1, font = 'Helvetica 10')
        self.ivs_blob_max_size_spinbox['validate']='key'
        self.ivs_blob_max_size_spinbox['vcmd']=(self.ivs_blob_max_size_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)

        self.ivs_blob_max_size_spinbox['command'] = lambda: self.BLOB_spinbox_func(self.ivs_blob_max_size_spinbox, self.ivs_blob_max_size_var, 1, 1000000, only_positive = True, np_index = 1)

        self.ivs_blob_max_size_spinbox.bind('<Tab>', lambda event: self.BLOB_spinbox_func(self.ivs_blob_max_size_spinbox, self.ivs_blob_max_size_var, 1, 1000000, only_positive = True, np_index = 1))
        self.ivs_blob_max_size_spinbox.bind('<Return>', lambda event: self.BLOB_spinbox_func(self.ivs_blob_max_size_spinbox, self.ivs_blob_max_size_var, 1, 1000000, only_positive = True, np_index = 1))
        self.ivs_blob_max_size_spinbox.bind('<KeyRelease>', lambda event: self.BLOB_spinbox_func(self.ivs_blob_max_size_spinbox, self.ivs_blob_max_size_var, 1, 1000000, only_positive = True, np_index = 1))
        self.ivs_blob_max_size_spinbox.bind('<FocusOut>', lambda event: self.BLOB_spinbox_focus_out(self.ivs_blob_max_size_var))

        self.ivs_blob_lo_th_var = tk.StringVar(value = 0)
        self.ivs_blob_lo_th_spinbox = tk.Spinbox(frame, width = 7, textvariable = self.ivs_blob_lo_th_var ,from_= 0, to = 255, increment = 1
                                    , highlightbackground="black", highlightthickness=1, font = 'Helvetica 10')
        self.ivs_blob_lo_th_spinbox['validate']='key'
        self.ivs_blob_lo_th_spinbox['vcmd']=(self.ivs_blob_lo_th_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)

        self.ivs_blob_lo_th_spinbox['command'] = lambda: self.BLOB_spinbox_func(self.ivs_blob_lo_th_spinbox, self.ivs_blob_lo_th_var, 0, 255, only_positive = True, np_index = 2)

        self.ivs_blob_lo_th_spinbox.bind('<Tab>', lambda event: self.BLOB_spinbox_func(self.ivs_blob_lo_th_spinbox, self.ivs_blob_lo_th_var, 0, 255, only_positive = True, np_index = 2))
        self.ivs_blob_lo_th_spinbox.bind('<Return>', lambda event: self.BLOB_spinbox_func(self.ivs_blob_lo_th_spinbox, self.ivs_blob_lo_th_var, 0, 255, only_positive = True, np_index = 2))
        self.ivs_blob_lo_th_spinbox.bind('<KeyRelease>', lambda event: self.BLOB_spinbox_func(self.ivs_blob_lo_th_spinbox, self.ivs_blob_lo_th_var, 0, 255, only_positive = True, np_index = 2))
        self.ivs_blob_lo_th_spinbox.bind('<FocusOut>', lambda event: self.BLOB_spinbox_focus_out(self.ivs_blob_lo_th_var))

        self.ivs_blob_hi_th_var = tk.StringVar(value = 0)
        self.ivs_blob_hi_th_spinbox = tk.Spinbox(frame, width = 7, textvariable = self.ivs_blob_hi_th_var ,from_= 0, to = 255, increment = 1
                                    , highlightbackground="black", highlightthickness=1, font = 'Helvetica 10')
        self.ivs_blob_hi_th_spinbox['validate']='key'
        self.ivs_blob_hi_th_spinbox['vcmd']=(self.ivs_blob_hi_th_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)

        self.ivs_blob_hi_th_spinbox['command'] = lambda: self.BLOB_spinbox_func(self.ivs_blob_hi_th_spinbox, self.ivs_blob_hi_th_var, 0, 255, only_positive = True, np_index = 3)

        self.ivs_blob_hi_th_spinbox.bind('<Tab>', lambda event: self.BLOB_spinbox_func(self.ivs_blob_hi_th_spinbox, self.ivs_blob_hi_th_var, 0, 255, only_positive = True, np_index = 3))
        self.ivs_blob_hi_th_spinbox.bind('<Return>', lambda event: self.BLOB_spinbox_func(self.ivs_blob_hi_th_spinbox, self.ivs_blob_hi_th_var, 0, 255, only_positive = True, np_index = 3))
        self.ivs_blob_hi_th_spinbox.bind('<KeyRelease>', lambda event: self.BLOB_spinbox_func(self.ivs_blob_hi_th_spinbox, self.ivs_blob_hi_th_var, 0, 255, only_positive = True, np_index = 3))
        self.ivs_blob_hi_th_spinbox.bind('<FocusOut>', lambda event: self.BLOB_spinbox_focus_out(self.ivs_blob_hi_th_var))

        self.ivs_blob_min_size_spinbox.place(x= 160,y=49+10)
        self.ivs_blob_max_size_spinbox.place(x= 160,y=49 + 30+10)
        self.ivs_blob_lo_th_spinbox.place(x= 160,y=49 + 30+30+10)
        self.ivs_blob_hi_th_spinbox.place(x= 160,y=49 + 30+30+30+10)

        self.ivs_black_on_white_bool = tk.IntVar(value = 1)
        self.ivs_black_on_white_checkbtn = tk.Checkbutton(frame, text='Light Background'
            , variable = self.ivs_black_on_white_bool, onvalue=1, offvalue=0, font = 'Helvetica 10')

        self.ivs_white_on_black_checkbtn = tk.Checkbutton(frame, text='Dark Background'
            , variable = self.ivs_black_on_white_bool, onvalue=0, offvalue=1, font = 'Helvetica 10')

        self.ivs_black_on_white_checkbtn['command'] = self.BLOB_bg_check
        self.ivs_white_on_black_checkbtn['command'] = self.BLOB_bg_check

        self.ivs_black_on_white_checkbtn['disabledforeground'] = 'black'
        self.ivs_white_on_black_checkbtn['disabledforeground'] = 'black'

        self.BLOB_bg_check()

        self.ivs_black_on_white_checkbtn.place(x= 10,y=49 + 30+30+30+30+10)
        self.ivs_white_on_black_checkbtn.place(x= 10,y=49 + 30+30+30+30+30+10)


        self.ivs_bbox_outline_var = tk.StringVar(value = 2)
        self.ivs_bbox_outline_spinbox = tk.Spinbox(frame, width = 7, textvariable = self.ivs_bbox_outline_var ,from_= 1, to = 15, increment = 1
                                    , highlightbackground="black", highlightthickness=1, font = 'Helvetica 10')
        self.ivs_bbox_outline_spinbox['validate']='key'
        self.ivs_bbox_outline_spinbox['vcmd']=(self.ivs_bbox_outline_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)

        self.ivs_bbox_outline_spinbox['command'] = lambda: self.BLOB_spinbox_func(self.ivs_bbox_outline_spinbox, self.ivs_bbox_outline_var, 1, 15, only_positive = True, np_index = 4)
        self.ivs_bbox_outline_spinbox.bind('<Tab>', lambda event: self.BLOB_spinbox_func(self.ivs_bbox_outline_spinbox, self.ivs_bbox_outline_var, 1, 15, only_positive = True, np_index = 4))
        self.ivs_bbox_outline_spinbox.bind('<Return>', lambda event: self.BLOB_spinbox_func(self.ivs_bbox_outline_spinbox, self.ivs_bbox_outline_var, 1, 15, only_positive = True, np_index = 4))
        self.ivs_bbox_outline_spinbox.bind('<KeyRelease>', lambda event: self.BLOB_spinbox_func(self.ivs_bbox_outline_spinbox, self.ivs_bbox_outline_var, 1, 15, only_positive = True, np_index = 4))

        self.ivs_bbox_outline_spinbox.place(x= 160,y=49 + 30+30+30+30+30+30+10)

    def custom_scroll_inner_bound(self, event):
        # print(event.type)
        # print(dir(event))
        self.ivs_morph_scroll_class.canvas.bind_all("<MouseWheel>", self.custom_inner_scrolly)

    def custom_inner_scrolly(self, event):
        if self.ivs_morph_scroll_class.scrolly_lock == False:
            self.ivs_morph_scroll_class.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            # print('custom_inner_scrolly: ',event.delta)
            y0_inner = float(self.ivs_morph_scroll_class.canvas.yview()[0])
            y1_inner = float(self.ivs_morph_scroll_class.canvas.yview()[1])
            # print(y0_inner, y1_inner)
            if 0 <= y1_inner < 1:
                if y0_inner == 0: #inner scroll: Start point
                    if event.delta > 0: #scroll up
                        self.ctrl_panel_scroll_class.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            elif y1_inner == 1:
                if 0<= y0_inner < 1: #inner scroll: End point
                    if event.delta < 0: #scroll down
                        self.ctrl_panel_scroll_class.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def morph_panel_init(self):
        self.ivs_morph_panel = tk.Frame(self.ctrl_panel_frame, highlightthickness = 1, highlightbackground = 'black')
        self.ivs_morph_panel['width'] = 270 + 25
        self.ivs_morph_panel['height'] = 120 + 30 + 30 + 30 + 30

        self.ivs_morph_panel_curr_height = 230+200 #variable to keep track of the window height (when user add more morph process, window height will increase)
        # self.ivs_morph_panel_init_height = 230+200

        parent = self.ivs_morph_panel
        self.ivs_morph_scroll_class = ScrolledCanvas(master = parent, frame_w = 260 + 25, frame_h = 230 + 200)
        self.ivs_morph_scroll_class.show()

        self.ivs_morph_scroll_class.scrollx.place_forget()

        self.ivs_morph_scroll_class.canvas.bind('<Enter>', self.custom_scroll_inner_bound)
        try:
            self.ivs_morph_scroll_class.canvas.bind('<Leave>', self.ctrl_panel_scroll_class._bound_to_mousewheel)
        except Exception:
            pass

        frame = self.ivs_morph_scroll_class.window_fr

        tk.Label(frame, text = 'Blob Morphology:', font = 'Helvetica 11').place(x=0 ,y=0)
        tk.Label(frame, text = 'Type:', font = 'Helvetica 10').place(x=10 ,y= 30)

        frame.option_add('*TCombobox*Listbox.font', ('Helvetica', '10'))

        self.morph_type_list = ['Dilation', 'Erosion', 'Closing', 'Opening']
        self.kernel_type_list = ['Rectangle', 'Ellipse', 'Cross']
        self.morph_sel_combobox = ttk.Combobox(frame, values=self.morph_type_list, width=12, state='readonly', font = 'Helvetica 10')
        self.morph_sel_combobox.unbind_class("TCombobox", "<MouseWheel>")
        self.morph_sel_combobox.current(0)

        self.morph_sel_combobox.place(x= 55,y=30)

        self.ivs_morph_process_dict = {}
        self.ivs_morph_widget_coor = {}
        self.ivs_morph_widget_name_list = ['_morph_type_label', '_kernel_type_combobox', '_kernel_spinbox_var', '_kernel_spinbox', '_remove_btn']

        # self.ivs_add_morph_btn = tk.Button(frame, relief = tk.GROOVE, width = 2, height = 1, bg = 'green')
        self.ivs_add_morph_btn = tk.Button(frame, relief = tk.GROOVE, image = self.add_icon
            , bd = 0)

        self.ivs_add_morph_btn['command'] = lambda: self.BLOB_add_morph_widget(frame)
        self.ivs_add_morph_btn.place(x=180, y =28 + 2)

        tk.Label(frame, text = 'Process:', font = 'Helvetica 11 bold').place(x=10 ,y= 65)

        # _dict = {'2': 9, '1': 5, '3':2, '4':12}
        # print(_dict)
        # _dict_item = _dict.items()
        # _sorted_dict = dict(sorted(_dict_item))
        # print(_sorted_dict)

        # tk.Label(frame, text = 'Dilation:', font = 'Helvetica 10').place(x=10 ,y= 49)
        # tk.Label(frame, text = 'Erosion:', font = 'Helvetica 10').place(x=10 ,y=49 + 30)
        # tk.Label(frame, text = 'Closing:', font = 'Helvetica 10').place(x=10 ,y=49 + 30 + 30)
        # tk.Label(frame, text = 'Opening:', font = 'Helvetica 10').place(x=10 ,y=49 + 30 + 30 + 30)

    def BLOB_add_morph_widget(self, parent):
        y_spacing = np.multiply(len(self.ivs_morph_process_dict), 30)
        _morph_type = self.morph_sel_combobox.get()

        _morph_type_label = tk.Label(parent, text = self.morph_sel_combobox.get() + ':', font = 'Helvetica 11')

        _kernel_type_combobox = ttk.Combobox(parent, values = self.kernel_type_list, width = 9, state='readonly', font = 'Helvetica 10')
        _kernel_type_combobox.unbind_class("TCombobox", "<MouseWheel>")
        _kernel_type_combobox.bind("<<ComboboxSelected>>", partial(self.BLOB_morph_kernel_sel, _kernel_type_combobox, self.kernel_type_list))

        _kernel_type_combobox.current(self.previous_morph_kernel)

        _kernel_spinbox_var = tk.StringVar(value = 1)
        _kernel_spinbox = tk.Spinbox(parent, width = 4, textvariable = _kernel_spinbox_var ,from_= 1, to = 100, increment = 1
            , highlightbackground="black", highlightthickness=1, font = 'Helvetica 10')

        _kernel_spinbox['validate']='key'
        _kernel_spinbox['vcmd']=(_kernel_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)

        _kernel_spinbox['command'] = partial(self.BLOB_spinbox_func, _kernel_spinbox, _kernel_spinbox_var, 1, 100, True)
        # _kernel_spinbox.bind('<FocusOut>', partial(self.BLOB_spinbox_func, _kernel_spinbox, _kernel_spinbox_var, 1, 100, True))
        _kernel_spinbox.bind('<Tab>', partial(self.BLOB_spinbox_func, _kernel_spinbox, _kernel_spinbox_var, 1, 100, True))
        _kernel_spinbox.bind('<Return>', partial(self.BLOB_spinbox_func, _kernel_spinbox, _kernel_spinbox_var, 1, 100, True))
        _kernel_spinbox.bind('<KeyRelease>', partial(self.BLOB_spinbox_func, _kernel_spinbox, _kernel_spinbox_var, 1, 100, True))

        # _kernel_spinbox['command'] = lambda: self.BLOB_spinbox_func(_kernel_spinbox, _kernel_spinbox_var, 1, 100, only_positive = True)
        # _kernel_spinbox.bind('<FocusOut>', lambda event: self.BLOB_spinbox_func(_kernel_spinbox, _kernel_spinbox_var, 1, 100, only_positive = True))
        # _kernel_spinbox.bind('<Tab>', lambda event: self.BLOB_spinbox_func(_kernel_spinbox, _kernel_spinbox_var, 1, 100, only_positive = True))
        # _kernel_spinbox.bind('<Return>', lambda event: self.BLOB_spinbox_func(_kernel_spinbox, _kernel_spinbox_var, 1, 100, only_positive = True))
        # _kernel_spinbox.bind('<KeyRelease>', lambda event: self.BLOB_spinbox_func(_kernel_spinbox, _kernel_spinbox_var, 1, 100, only_positive = True))

        # _remove_btn = tk.Button(parent, relief = tk.GROOVE, text = str(len(self.ivs_morph_process_dict) + 1), width = 2, height = 1, bg = 'red')
        _remove_btn = tk.Button(parent, relief = tk.GROOVE, image = self.minus_icon
            , bd = 0)

        _morph_type_label.place(x=10 ,y=95 + y_spacing)
        _kernel_type_combobox.place(x=80, y = 95+y_spacing)
        _kernel_spinbox.place(x=80+95 ,y=95 + y_spacing)
        _remove_btn.place(x = 80+95+55, y=93 + y_spacing + 2)

        new_process_id = len(self.ivs_morph_process_dict) + 1

        # tk_widget_name_list = ['_morph_type_label', '_kernel_type_combobox', '_kernel_spinbox_var', '_kernel_spinbox', '_remove_btn']
        tk_widget_name_list = self.ivs_morph_widget_name_list
        tk_widget_list = [_morph_type_label, _kernel_type_combobox, _kernel_spinbox_var, _kernel_spinbox, _remove_btn]
        tk_widget_dict = {}

        for i, widget in enumerate(tk_widget_list):
            tk_widget_dict[tk_widget_name_list[i]] = widget

        # print(tk_widget_dict)

        # self.ivs_morph_process_dict[str(new_process_id)] = \
        # dict(tk_label=_morph_type_label, tk_spinbox_var = _kernel_spinbox_var, tk_spinbox = _kernel_spinbox, tk_btn = _remove_btn)

        self.ivs_morph_process_dict[str(new_process_id)] = [tk_widget_dict, _morph_type]

        self.ivs_morph_widget_coor[str(new_process_id)] = [(10, 95 + y_spacing), (80, 95 + y_spacing), (80+95, 95 + y_spacing), (80+95+55, 93 + y_spacing + 2)]

        _remove_btn['command'] = partial(self.BLOB_remove_morph_widget, new_process_id, tk_widget_name_list, self.ivs_morph_process_dict[str(new_process_id)][0])

        del tk_widget_dict
        del tk_widget_list

        _height_chg = 95 + y_spacing + 30
        if _height_chg > self.ivs_morph_panel_curr_height:
            self.ivs_morph_panel_curr_height = _height_chg
            self.ivs_morph_scroll_class.resize_frame(height = self.ivs_morph_panel_curr_height)

        self.IVS_OCR_start()
        # if len(self.ivs_morph_process_dict):

        # print('self.ivs_morph_process_dict: ', self.ivs_morph_process_dict[str(new_process_id)]['tk_btn'])
        # print('self.ivs_morph_widget_coor: ', self.ivs_morph_widget_coor[str(new_process_id)])
        # print('self.ivs_morph_widget_coor: ', self.ivs_morph_widget_coor[str(new_process_id)][0])

    def BLOB_remove_morph_widget(self, dict_id, name_list, tk_args = {}):

        for tk_id, widget in tk_args.items():
            if tk_id == name_list[2]:
                del widget
            else:
                widget.destroy()

        # del self.ivs_morph_process_dict[str(dict_id)]
        self.ivs_morph_process_dict = self.remove_key(self.ivs_morph_process_dict, dict_id)

        _last_element = len(self.ivs_morph_widget_coor)
        del self.ivs_morph_widget_coor[str(_last_element)]

        # print('Updated dictionary: ', self.ivs_morph_process_dict)
        # print('Updated dictionary: ', self.ivs_morph_widget_coor)

        for key, args in self.ivs_morph_process_dict.items():
            # print(args[1])
            tk_args = args[0]
            # print(tk_args['tk_btn'], key)
            tk_args[name_list[-1]]['command'] = partial(self.BLOB_remove_morph_widget, int(key), name_list, self.ivs_morph_process_dict[key][0])

            if int(key) < dict_id:
                continue
            else:
                for tk_id, widget in self.ivs_morph_process_dict[key][0].items():
                    if tk_id == name_list[0]:
                        _load_coor = self.ivs_morph_widget_coor[key][0]
                        widget.place(x=_load_coor[0] , y=_load_coor[1])

                    elif tk_id == name_list[1]:
                        _load_coor = self.ivs_morph_widget_coor[key][1]
                        widget.place(x=_load_coor[0] , y=_load_coor[1])

                    elif tk_id == name_list[3]:
                        _load_coor = self.ivs_morph_widget_coor[key][2]
                        widget.place(x=_load_coor[0] , y=_load_coor[1])

                    elif tk_id == name_list[-1]:
                        _load_coor = self.ivs_morph_widget_coor[key][-1]
                        widget.place(x=_load_coor[0] , y=_load_coor[1])
                pass

        _height_chg = 95 + np.multiply(len(self.ivs_morph_process_dict), 30)
        if  self.ivs_morph_panel_curr_height > _height_chg:
            if _height_chg > 430:
                self.ivs_morph_panel_curr_height = _height_chg
                self.ivs_morph_scroll_class.resize_frame(height = self.ivs_morph_panel_curr_height)

            else:
                self.ivs_morph_scroll_class.resize_frame(height = 430)

        self.IVS_OCR_start()

    def remove_key(self, ref_dict, del_key):
        new_dict = {}
        for key, val in ref_dict.items():
            if int(key) < del_key:
                new_dict[key] = val
            elif int(key) > del_key:
                new_dict[str(int(key)-1)] = val
            else: # key == del_key
                continue
        return new_dict

    def BLOB_morph_kernel_sel(self, widget, sel_list, event = None):
        if widget.get() == sel_list[0]:
            self.previous_morph_kernel = 0
            self.IVS_OCR_start()

        elif widget.get() == sel_list[1]:
            self.previous_morph_kernel = 1
            self.IVS_OCR_start()

        elif widget.get() == sel_list[2]:
            self.previous_morph_kernel = 2
            self.IVS_OCR_start()

    def BLOB_morph_kernel_spinbox_func(self, widget, tk_var, min_val, max_val, only_positive = False):
        _type = None
        try:
            int(tk_var.get())
            _type = 'int'
        except Exception:
            pass
        if _type == 'int':
            if int(tk_var.get()) < min_val:
                tk_var.set(min_val)
                widget['validate']='key'
                widget['vcmd']=(widget.register(validate_int_entry), '%d', '%P', '%S', only_positive)
            elif int(tk_var.get()) > max_val:
                tk_var.set(max_val)
                widget['validate']='key'
                widget['vcmd']=(widget.register(validate_int_entry), '%d', '%P', '%S', only_positive)

            self.IVS_OCR_start()

    def BLOB_bg_check(self):
        # print(bool(self.ivs_black_on_white_bool.get()))
        if bool(self.ivs_black_on_white_bool.get()) == True:
            self.ivs_black_on_white_checkbtn['state'] = 'disable'
            self.ivs_white_on_black_checkbtn['state'] = 'normal'

        elif bool(self.ivs_black_on_white_bool.get()) == False:
            self.ivs_black_on_white_checkbtn['state'] = 'normal'
            self.ivs_white_on_black_checkbtn['state'] = 'disable'

        self.IVS_OCR_start()

    def BLOB_spinbox_func(self, widget, tk_var, min_val, max_val, only_positive = False, np_index = None):
        _type = None
        try:
            int(tk_var.get())
            _type = 'int'
        except Exception:
            pass
        if _type == 'int':
            if int(tk_var.get()) < min_val:
                tk_var.set(min_val)
                widget['validate']='key'
                widget['vcmd']=(widget.register(validate_int_entry), '%d', '%P', '%S', only_positive)
            elif int(tk_var.get()) > max_val:
                tk_var.set(max_val)
                widget['validate']='key'
                widget['vcmd']=(widget.register(validate_int_entry), '%d', '%P', '%S', only_positive)

        if self.img_disp is not None:
            if np_index is not None:
                try:
                    self.img_disp.ivs_blob_param[np_index] = int(tk_var.get())

                except Exception:
                    pass

            self.IVS_OCR_start()

    def BLOB_spinbox_focus_out(self, tk_var):
        if tk_var.get() == '':
            self.np_arr_blob_load()

    def OCR_spinbox_focus_out(self, tk_var):
        if tk_var.get() == '' or tk_var.get() == '-':
            self.np_arr_ocr_load()

    def result_panel_init(self):
        self.ivs_ocr_result_frame = tk.Frame(self.ctrl_panel_frame, highlightthickness = 1, highlightbackground = 'black')
        self.ivs_ocr_result_frame['width'] = 270 +25
        self.ivs_ocr_result_frame['height'] = 120 + 30

        frame = self.ivs_ocr_result_frame

        tk.Label(frame, text = 'OCR Result Tag(s):', font = 'Helvetica 11').place(x=0 ,y=0)
        tk.Label(frame, text = 'Shift-X:', font = 'Helvetica 10').place(x=10 ,y= 49)
        tk.Label(frame, text = 'Shift-Y:', font = 'Helvetica 10').place(x=10 ,y=49 + 30)#+ 45)
        tk.Label(frame, text = 'Font Size:', font = 'Helvetica 10', anchor = 'w').place(x=10 ,y=49 + 30 + 30)#+ 45)

        self.OCR_shift_x_var = tk.StringVar(value = 0)
        self.OCR_shift_x_spinbox = tk.Spinbox(frame, width = 6, textvariable = self.OCR_shift_x_var ,from_= -10000, to = 10000, increment = 1
                                    , highlightbackground="black", highlightthickness=1, font = 'Helvetica 10')
        self.OCR_shift_x_spinbox['validate']='key'
        self.OCR_shift_x_spinbox['vcmd']=(self.OCR_shift_x_spinbox.register(validate_int_entry), '%d', '%P', '%S', False)

        self.OCR_shift_x_spinbox['command'] = lambda: self.OCR_spinbox_func(self.OCR_shift_x_spinbox, self.OCR_shift_x_var, -10000, 10000, only_positive = False, np_index = 0)
        self.OCR_shift_x_spinbox.bind('<Tab>', lambda event: self.OCR_spinbox_func(self.OCR_shift_x_spinbox, self.OCR_shift_x_var, -10000, 10000, only_positive = False, np_index = 0))
        self.OCR_shift_x_spinbox.bind('<Return>', lambda event: self.OCR_spinbox_func(self.OCR_shift_x_spinbox, self.OCR_shift_x_var, -10000, 10000, only_positive = False, np_index = 0))
        self.OCR_shift_x_spinbox.bind('<KeyRelease>', lambda event: self.OCR_spinbox_func(self.OCR_shift_x_spinbox, self.OCR_shift_x_var, -10000, 10000, only_positive = False, np_index = 0))
        self.OCR_shift_x_spinbox.bind('<FocusOut>', lambda event: self.OCR_spinbox_focus_out(self.OCR_shift_x_var))

        self.OCR_shift_x_spinbox.place(x= 70,y=49)

        self.OCR_shift_y_var = tk.StringVar(value = 0)
        self.OCR_shift_y_spinbox = tk.Spinbox(frame, width = 6, textvariable = self.OCR_shift_y_var ,from_= -10000, to = 10000, increment = 1
                                    , highlightbackground="black", highlightthickness=1, font = 'Helvetica 10')
        self.OCR_shift_y_spinbox['validate']='key'
        self.OCR_shift_y_spinbox['vcmd']=(self.OCR_shift_y_spinbox.register(validate_int_entry), '%d', '%P', '%S', False)

        self.OCR_shift_y_spinbox['command'] = lambda: self.OCR_spinbox_func(self.OCR_shift_y_spinbox, self.OCR_shift_y_var, -10000, 10000, only_positive = False, np_index = 1)
        self.OCR_shift_y_spinbox.bind('<Tab>', lambda event: self.OCR_spinbox_func(self.OCR_shift_y_spinbox, self.OCR_shift_y_var, -10000, 10000, only_positive = False, np_index = 1))
        self.OCR_shift_y_spinbox.bind('<Return>', lambda event: self.OCR_spinbox_func(self.OCR_shift_y_spinbox, self.OCR_shift_y_var, -10000, 10000, only_positive = False, np_index = 1))
        self.OCR_shift_y_spinbox.bind('<KeyRelease>', lambda event: self.OCR_spinbox_func(self.OCR_shift_y_spinbox, self.OCR_shift_y_var, -10000, 10000, only_positive = False, np_index = 1))
        self.OCR_shift_y_spinbox.bind('<FocusOut>', lambda event: self.OCR_spinbox_focus_out(self.OCR_shift_y_var))

        self.OCR_shift_y_spinbox.place(x= 70,y=49 + 30)

        self.OCR_font_size_var = tk.StringVar(value = 18)
        self.OCR_font_size_spinbox = tk.Spinbox(frame, width = 6, textvariable = self.OCR_font_size_var ,from_= 1, to = 100, increment = 1
                                    , highlightbackground="black", highlightthickness=1, font = 'Helvetica 10')
        self.OCR_font_size_spinbox['validate']='key'
        self.OCR_font_size_spinbox['vcmd']=(self.OCR_font_size_spinbox.register(validate_int_entry), '%d', '%P', '%S', True)

        self.OCR_font_size_spinbox['command'] = lambda: self.OCR_spinbox_func(self.OCR_font_size_spinbox, self.OCR_font_size_var, 1, 100, only_positive = True, np_index = 2)
        self.OCR_font_size_spinbox.bind('<Tab>', lambda event: self.OCR_spinbox_func(self.OCR_font_size_spinbox, self.OCR_font_size_var, 1, 100, only_positive = True, np_index = 2))
        self.OCR_font_size_spinbox.bind('<Return>', lambda event: self.OCR_spinbox_func(self.OCR_font_size_spinbox, self.OCR_font_size_var, 1, 100, only_positive = True, np_index = 2))
        self.OCR_font_size_spinbox.bind('<KeyRelease>', lambda event: self.OCR_spinbox_func(self.OCR_font_size_spinbox, self.OCR_font_size_var, 1, 100, only_positive = True, np_index = 2))
        self.OCR_font_size_spinbox.bind('<FocusOut>', lambda event: self.OCR_spinbox_focus_out(self.OCR_font_size_var))

        self.OCR_font_size_spinbox.place(x= 70 + 10,y=49 + 30 + 30)

    def OCR_spinbox_func(self, widget, tk_var, min_val, max_val, only_positive = False, np_index = None):
        _type = None
        try:
            int(tk_var.get())
            _type = 'int'
        except Exception:
            # print('OCR_spinbox_func Error: ', e)
            pass
        if _type == 'int':
            if int(tk_var.get()) < min_val:
                tk_var.set(min_val)
                widget['validate']='key'
                widget['vcmd']=(widget.register(validate_int_entry), '%d', '%P', '%S', only_positive)
            elif int(tk_var.get()) > max_val:
                tk_var.set(max_val)
                widget['validate']='key'
                widget['vcmd']=(widget.register(validate_int_entry), '%d', '%P', '%S', only_positive)


            if self.img_disp is not None:
                if np_index is not None:
                    try:
                        self.img_disp.ivs_ocr_label_param[np_index] = int(tk_var.get())
                    except Exception:
                        # print('OCR_spinbox_func Error: ', e)
                        pass

                # self.IVS_OCR_start()
                self.IVS_OCR_tag_adjust()

    def roi_widget(self):
        self.roi_status_var = tk.IntVar()
        self.roi_checkbtn = tk.Checkbutton(self, text='ROI Enable', variable = self.roi_status_var, onvalue=1, offvalue=0, highlightthickness = 0, bg = 'white')
        self.roi_checkbtn['command'] = self.roi_checkbtn_click
        self.roi_checkbtn.place(x=10,y=30-30)

        self.roi_type_list = ['BOX'] #['BOX', 'LINE']
        self.option_add('*TCombobox*Listbox.font', ('Helvetica', '10'))
        self.roi_type_combobox = ttk.Combobox(self, values=self.roi_type_list, width=10, state='readonly', font = 'Helvetica 10')
        self.roi_type_combobox.unbind_class("TCombobox", "<MouseWheel>")
        self.roi_type_combobox.bind('<<ComboboxSelected>>', self.roi_type_sel)
        self.roi_type_combobox.current(0)
        self.roi_type_combobox['state'] = 'disable'
        self.roi_type_combobox.place(x=100, y=32-30)

    def roi_checkbtn_click(self):
        if self.roi_status_var.get() == 0:
            self.roi_type_combobox['state'] = 'disable'
            self.img_disp.ROI_disable()
            self.curr_roi_mode = None
            self.IVS_OCR_clear()

            try:
                check_bool = tk.Toplevel.winfo_exists(self.ivs_roi_img_toplvl)
                if check_bool == 0:
                    pass
                else:
                    self.ivs_roi_img_toplvl.destroy()
            except (AttributeError, tk.TclError):
                pass

        elif self.roi_status_var.get() == 1:
            self.roi_type_combobox['state'] = 'readonly'
            self.roi_type_sel()

    def roi_type_sel(self,event = None):
        #print('self.roi_type_combobox.get(): ', self.roi_type_combobox.get())
        if self.roi_type_combobox.get() == 'BOX':
            if self.roi_type_combobox.get() != self.curr_roi_mode:
                self.curr_roi_mode = self.roi_type_combobox.get()
                self.img_disp.ROI_box_enable('IVS-Blob')

    def load_img_func(self):
        file = filedialog.askopenfilename(initialdir = self.__load_curr_dir, title="Select file", defaultextension = self.img_format_list, filetypes=self.img_format_list)
        #print(self.img_file)
        if file == '':
            #print('empty directory')
            pass
        else:
            self.img_file = file
            self.__load_curr_dir = str((pathlib.Path(file)).parent)

            self.load_img_stringvar.set('Image File: ' + os.path.basename(self.img_file))
            self.img_imageio = imread(self.img_file)

            self.new_img_bool = True

            if len(self.img_imageio.shape) > 2:
                if self.img_imageio.shape[2] == 3:
                    self.img_imageio = cv2.cvtColor(self.img_imageio, cv2.COLOR_BGR2GRAY)
                elif self.img_imageio.shape[2] == 4:
                    self.img_imageio = cv2.cvtColor(self.img_imageio, cv2.COLOR_BGRA2GRAY)

            # self.img_disp = CanvasImage(self.img_disp_frame, loaded_img = self.img_imageio, tess_api = self.tess_api)
            self.img_disp.canvas_default_load(img = self.img_imageio
                , fit_to_display_bool = True, display_width = self.img_disp_frame.winfo_width(), display_height = np.divide(self.img_disp_frame.winfo_height(), 2) -30 -30)

            self.fit_to_display_btn['command'] = lambda : self.img_disp.fit_to_display(self.img_disp_frame.winfo_width(), np.divide(self.img_disp_frame.winfo_height(), 2) -30 -30)

            self.np_arr_blob_load()
            self.np_arr_ocr_load()
            self.img_disp.ivs_start_bool = True

            self.roi_checkbtn['state'] = 'normal'
            self.curr_roi_mode = None
            self.roi_checkbtn_click()

            self.IVS_OCR_clear()

    def IVS_OCR_clear(self):

        self.IVS_delete_tk_draw()
        self.blob_num_detect_var.set(0)

        try:
            check_bool = tk.Toplevel.winfo_exists(self.ivs_roi_img_toplvl)
            if check_bool == 0:
                pass
            else:
                self.roi_disp.canvas_clear()
        except (AttributeError, tk.TclError):
            pass

    def IVS_OCR_start(self):
        self.IVS_OCR_func()

    def save_img_func(self):
        self.save_img_btn['state'] = 'disable'
        self.save_img_format_sel['state'] = 'disable'
        (canvas_offset_x, canvas_offset_y, imscale, roi_img, blob_bbox, ocr_result) = self.IVS_OCR_func()
        # print(imscale)
        if type(blob_bbox) == list and len(blob_bbox) > 0 :
            img_arr = None
            try:
                roi_cv = cv2.cvtColor(roi_img, cv2.COLOR_GRAY2BGR)
                roi_cv = cv2.resize(roi_cv, None, fx = imscale, fy = imscale
                                , interpolation = cv2.INTER_LINEAR) #cv2.INTER_CUBIC

                pil_img = Image.fromarray(roi_cv)
                _draw = ImageDraw.Draw(pil_img)
                _bb_box_outline = int(self.img_disp.ivs_blob_param[4])
                # print(_bb_box_outline)

                for blob_data in blob_bbox:

                    x1 = int( np.multiply(blob_data[0], imscale) )
                    x2 = int( np.multiply(blob_data[2], imscale) )

                    y1 = int( np.multiply(blob_data[1], imscale) )
                    y2 = int( np.multiply(blob_data[3], imscale) )

                    _draw.rectangle([x1, y1, x2, y2]
                            , outline = "red", width = _bb_box_outline)

                if self.ivs_ocr_enable_bool == True:
                    if ocr_result is not None and type(ocr_result) == dict:
                        if len(ocr_result) > 0:
                            padding_dict = dict(pad_left = 0, pad_top = 0, pad_right = 0, pad_btm = 0)

                            font = ImageFont.truetype(root_path + "\\Font\\" + "TIMES.ttf", int(self.img_disp.ivs_ocr_label_param[2]))
                            target_pixel_size = round(int(self.img_disp.ivs_ocr_label_param[2]) * 1.33, 0 )
                            curr_font_size = int(self.img_disp.ivs_ocr_label_param[2])
                            ### THIS WHILE LOOP IS TO FIND THE CORRECT curr_font_size TO CALCULATE font pixel size RELATIVE TO THE IMG.
                            while font.getsize('0')[1] < target_pixel_size:
                                curr_font_size += 1
                                font = ImageFont.truetype(root_path + "\\Font\\" + "TIMES.ttf", curr_font_size)

                            font_height = font.getsize('0')[1] + font.getmetrics()[1]
                            font_width = font.getsize('0')[0]

                            for _, ocr_data in ocr_result.items():
                                midpoint_x = np.multiply(0.7, (ocr_data[1][2] - ocr_data[1][0]))

                                text_x = np.multiply( (ocr_data[1][0] + midpoint_x + self.img_disp.ivs_ocr_label_param[0]), imscale)
                                text_y = np.multiply( (ocr_data[1][3] + self.img_disp.ivs_ocr_label_param[1]), imscale)

                                text_width_midpoint = round(np.divide(int(font.getsize(ocr_data[0])[0]), 2), 0)
                                # Display on Tk GUI: anchor of text is set to 'n'
                                text_x = text_x - text_width_midpoint

                                #To check top and btm padding;
                                font_check_top = text_y - padding_dict['pad_top']
                                font_check_btm = (pil_img.size[1] - abs(padding_dict['pad_top'])) - text_y
                                #remove top padding before calc. the pix dist of point-y from height of img with previous btm padding


                                #To check left and right padding;
                                font_check_left = text_x - padding_dict['pad_left']
                                font_check_right = (pil_img.size[0] - abs(padding_dict['pad_left'])) - text_x

                                # print(font_check_btm, text_y, pil_img.size[1])
                                # print('Check Top Padding: ', font_check_top, text_y, padding_dict)
                                if font_check_top < font_height:
                                    if font_check_top > 0:
                                        add_pad = 0

                                    elif font_check_top < 0:
                                        add_pad = int (abs(font_check_top))
                                        pil_img = pil_padding_constant(pil_img, pad_top = add_pad)

                                    else:
                                        add_pad = 0

                                    _draw = ImageDraw.Draw(pil_img)
                                    padding_dict['pad_top'] = padding_dict['pad_top'] + (-add_pad)

                                if font_check_btm < font_height:
                                    if font_check_btm > 0:
                                        add_pad = int(font_height - abs(font_check_btm))
                                        pil_img = pil_padding_constant(pil_img, pad_btm = add_pad)
                                    elif font_check_btm < 0:
                                        add_pad = int (abs(font_check_btm) + font_height)
                                        pil_img = pil_padding_constant(pil_img, pad_btm = add_pad)

                                    else:
                                        add_pad = (font_height)
                                        pil_img = pil_padding_constant(pil_img, pad_btm = add_pad)

                                    _draw = ImageDraw.Draw(pil_img)
                                    padding_dict['pad_btm'] = padding_dict['pad_btm'] + add_pad

                                if font_check_left < font_width:
                                    if font_check_left > 0:
                                        add_pad = 0

                                    elif font_check_left < 0:
                                        add_pad = int (abs(font_check_left))
                                        pil_img = pil_padding_constant(pil_img, pad_left = add_pad)

                                    else:
                                        add_pad = 0

                                    _draw = ImageDraw.Draw(pil_img)
                                    padding_dict['pad_left'] = padding_dict['pad_left'] + (-add_pad)

                                if font_check_right < font_width:
                                    if font_check_right > 0:
                                        add_pad = int(font_width - abs(font_check_right))
                                        pil_img = pil_padding_constant(pil_img, pad_right = add_pad)

                                    elif font_check_right < 0:
                                        add_pad = int (abs(font_check_right) + font_width)
                                        pil_img = pil_padding_constant(pil_img, pad_right = add_pad)

                                    else:
                                        add_pad = (font_width)
                                        pil_img = pil_padding_constant(pil_img, pad_right = add_pad)

                                    _draw = ImageDraw.Draw(pil_img)
                                    padding_dict['pad_right'] = padding_dict['pad_right'] + add_pad

                                _draw.text((text_x + abs(padding_dict['pad_left']), text_y + abs(padding_dict['pad_top'])), ocr_data[0], font=font, fill='red')


                # save_folder = create_save_folder(folder_dir = self.__save_dir)
                # time_id = str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
                time_id = str(datetime.now().strftime("%Y-%m-%d"))
                save_folder = create_save_folder(folder_dir = self.__save_dir)
                # sub_folder = create_save_folder(save_folder + '\\IVS-Blob-OCR--' + time_id, duplicate = True)
                sub_folder = create_save_folder(save_folder + '\\IVS-Blob-OCR--' + time_id, duplicate = False)

                img_format = self.save_img_format_sel.get()

                if img_format == '.pdf':
                    img_arr = np.array(pil_img)
                    PDF_img_save(sub_folder, img_arr, 'IVS-Blob-OCR', ch_split_bool = False)

                elif img_format != '.pdf':
                    pil_img_save(sub_folder, pil_img, 'IVS-Blob-OCR', str(img_format))

                Info_Msgbox(message = 'Save IVS Image Success!' + '\n\n' + str(sub_folder), title = 'IVS Save'
                    , font = 'Helvetica 10', message_anchor = 'c', width = 400, height = 180)

            except Exception as e:
                # print('Error in Saving: ', e)
                Error_Msgbox(message = 'Error in Saving Blob/OCR Image.\nDetected Error: {}'.format(e), title = 'IVS Save Error'
                    , font = 'Helvetica 11', message_anchor = 'c', width = 400, height = 180)

        else:
            Info_Msgbox(message = 'No Blob Detected. Image is Not Saved!', title = 'IVS Save Fail'
                , font = 'Helvetica 11', message_anchor = 'c', message_justify = tk.LEFT)

        self.save_img_format_sel['state'] = 'readonly'
        self.save_img_btn['state'] = 'normal'

    
    def IVS_delete_tk_draw(self):
        try:
            self.img_disp.canvas.delete('blob_box')
        except Exception:# as e:
            #print(e)
            pass

        try:
            self.img_disp.canvas.delete('ocr_tag')
        except Exception:# as e:
            # print(e)
            pass

    def IVS_OCR_tag_adjust(self):
        if self.ocr_draw_bool == True:
            # self.ocr_tag_param_list = [ocr_result, canvas_offset_x, canvas_offset_y, imscale, img_offset_x, img_offset_y]
            if (isinstance(self.ocr_tag_param_list, list) == True) and (len(self.ocr_tag_param_list) == 6):

                roi_box_update = self.img_disp.ROI_box_img_update()
                if (isinstance(roi_box_update, list) == True) and (len(roi_box_update) == 6):
                    self.ocr_tag_param_list[1] = roi_box_update[0]
                    self.ocr_tag_param_list[2] = roi_box_update[1]
                    self.ocr_tag_param_list[3] = roi_box_update[3]
                    self.ocr_tag_param_list[4] = roi_box_update[4]
                    self.ocr_tag_param_list[5] = roi_box_update[5]

                ocr_param = self.ocr_tag_param_list
                try:
                    self.img_disp.canvas.delete('ocr_tag')
                except Exception:# as e:
                    # print(e)
                    pass

                self.img_disp.Tess_Draw_OCR_Tag(ocr_result = ocr_param[0], canvas_offset_x = ocr_param[1], canvas_offset_y = ocr_param[2]
                    , imscale = ocr_param[3], img_offset_x = ocr_param[4], img_offset_y = ocr_param[5])



    def IVS_OCR_func(self, event = None):
        # print('Start Process')
        # print(self.winfo_width(), self.winfo_height())
        ocr_result = {}
        canvas_offset_x = None
        canvas_offset_y = None
        imscale = None
        roi_img = None
        blob_bbox = None

        if self.img_disp is not None:
            if self.img_disp.roi_bbox_exist == True:
                self.ocr_draw_bool = False

                self.IVS_delete_tk_draw()

                roi_box_update = self.img_disp.ROI_box_img_update()
                if (isinstance(roi_box_update, list) == True) and (len(roi_box_update) == 6):
                    canvas_offset_x = roi_box_update[0]
                    canvas_offset_y = roi_box_update[1]
                    roi_img = roi_box_update[2]
                    imscale = roi_box_update[3]
                    img_offset_x = roi_box_update[4]
                    img_offset_y = roi_box_update[5]


                    bin_img, blob_bbox = self.img_disp.ROI_Box_Blob(roi_img, bool(self.ivs_black_on_white_bool.get())
                        , self.ivs_morph_process_dict, self.ivs_morph_widget_name_list, self.morph_type_list, self.kernel_type_list)

                    if bin_img is not None and (isinstance(bin_img, np.ndarray)) == True:
                        _disp_img = cv2.bitwise_not(bin_img)
                        self.popout_roi_load_disp(_disp_img)
                        del _disp_img

                    ##### IF blob_bbox is an empty list, means 0 blob detected. IF blob_bbox is None it means blob detected is more than the limit (limit --> 1000 blobs).
                    if (blob_bbox is not None and type(blob_bbox) == list):
                        try:
                            self.blob_num_detect_var.set(str(len(blob_bbox)))
                            self.blob_num_detect_label['fg'] = 'black'
                        except (AttributeError, tk.TclError):
                            pass

                    elif blob_bbox is None:
                        try:
                            self.blob_num_detect_var.set('> 1000 (limit)')
                            self.blob_num_detect_label['fg'] = 'red'
                        except (AttributeError, tk.TclError):
                            pass

                    self.img_disp.Draw_Blob_Detection(blob_results = blob_bbox, canvas_offset_x = canvas_offset_x, canvas_offset_y = canvas_offset_y
                            , imscale = imscale, img_offset_x = img_offset_x, img_offset_y = img_offset_y)

                    if self.ivs_ocr_enable_bool == True:
                        # print('OCR Processing...')
                        if (bin_img is not None and isinstance(bin_img, np.ndarray) == True) and (blob_bbox is not None and type(blob_bbox) == list):
                            if len(blob_bbox) > 0:
                                ocr_result = self.img_disp.ROI_Box_Tess_OCR(bin_img, ocr_result, canvas_offset_y, ocr_timeout = 1000)

                    if type(ocr_result) == dict and len(ocr_result) > 0:
                        self.img_disp.Tess_Draw_OCR_Tag(ocr_result = ocr_result, canvas_offset_x = canvas_offset_x, canvas_offset_y = canvas_offset_y
                            , imscale = imscale, img_offset_x = img_offset_x, img_offset_y = img_offset_y)
                        self.ocr_draw_bool = True
                        
                    
                    if self.ocr_draw_bool == True:
                        del self.ocr_tag_param_list
                        self.ocr_tag_param_list = [ocr_result, canvas_offset_x, canvas_offset_y, imscale, img_offset_x, img_offset_y]
                    elif self.ocr_draw_bool == False:
                        del self.ocr_tag_param_list
                        self.ocr_tag_param_list = None


        return (canvas_offset_x, canvas_offset_y, imscale, roi_img, blob_bbox, ocr_result)
