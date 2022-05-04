# -*- coding: utf-8 -*-
# Advanced zoom for images of various types from small to huge up to several GB
# EDITTED CODE TO ACCOMODATE IMAGES LOADED IN NUMPY ARRAYS (through open-cv, imageio etc)
import math
import warnings
import tkinter as tk
import tkinter.messagebox

import os

import cv2
import numpy as np
from tkinter import ttk
from tkinter.font import Font

from PIL import Image, ImageTk, ImageGrab, ImageDraw
from collections import Counter

from tesserocr import get_languages
from tesserocr import PyTessBaseAPI, PSM, OEM, RIL
import tesserocr

import time

import re

def convert_int(var):
    result = None
    try:
        result = int(var)
    except Exception:
        result = None
    return result

def int_type_bool(var):
    if (type(var)) == int or (isinstance(var, np.integer) == True):
        return True
    else:
        return False


class CanvasImage():
    # Image.MAX_IMAGE_PIXELS = 1000000000  # suppress DecompressionBombError for the big image
    Image.MAX_IMAGE_PIXELS = None  # suppress DecompressionBombError for the big image
    """ Display and zoom image """
    def __init__(self, placeholder, loaded_img = None, local_img_split = False, ch_index = 0, tess_api = None): 
        """ Initialize the ImageFrame """
        self.imscale = 1.0  # scale for the canvas image zoom, public for outer classes
        self.delta = 1.3  # zoom magnitude
        self.filter = Image.NEAREST  # could be: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
        self.previous_state = 0  # previous state of the keyboard
        self.pyramid = []

        self.canvas_init_bool = False
        self.canvas_hide_img = False #Updated 13-10-2021: Prevent image from being displayed if canvas_clear() is instantiated.
        self.canvas_keybind_lock = False #Updated 13-10-2021: Prevents any keybind event from occuring if canvas_clear() is instantiated.

        self.loaded_img = loaded_img #EDITTED loaded_img is in numpy array form
        
        self.local_img_split = local_img_split #Option for user to perform channel splitting in this local Class if 3-channel image is being passed.
        #Local Split is mainly used for histogram plotting. Histogram plotting will refer to self.loaded_img, but user will be able to display 1 Channel if Local Split is True.
        self.ch_index = ch_index

        self.draw_save_img = None
        self.crop_offset = None
        self.crop_img = None

        self.ivs_mode = None
        self.roi_item = None
        self.roi_bbox_label = None

        self.roi_bbox_img = None
        self.roi_bbox_exist = False

        self.roi_line_pixel_mono = []
        self.roi_line_pixel_R = []
        self.roi_line_pixel_G = []
        self.roi_line_pixel_B = []
        self.roi_line_pixel_index = []
        self.roi_line_exist = False

        self.text_font = Font(family="Times New Roman", size=10)
        # print(tesserocr.tesseract_version())
        self.tess_api = tess_api #None
        # print(self.tess_api.oem())
        '''
        tess_dependency_path = os.getcwd() + '\\tessdata' #'C:\\Users\\User\\AppData\\Local\\Programs\\Tesseract-OCR\\tessdata'
        # print(tess_dependency_path)
        get_languages(tess_dependency_path)
        lang_param = 'eng' #'fra' #'eng'
        psm_param = PSM.SINGLE_BLOCK #PSM.SINGLE_CHAR #PSM.SINGLE_CHAR
        oem_param = OEM.TESSERACT_LSTM_COMBINED

        # self.tess_api = PyTessBaseAPI(path = tess_dependency_path
        #     , lang = lang_param
        #     , psm = psm_param, oem = oem_param)

        # print(dir(self.tess_api))

        self.Tesseract_API_load(tess_dependency_path, lang_param, psm_param, oem_param)
        '''
        #GOOD RESULTS tested so far: SINGLE BLOCK, SINGLE_CHAR

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

        ###################################################################################################
        # IVS Parameter Array(s):
        self.ivs_start_bool = False
        self.ivs_threshold_bool = False

        self.process_cancel = False

        self.ivs_th_param = np.empty((4,), dtype = object)
        self.ivs_th_param[0] = np.array([0, 0, 255], dtype = np.uint8) #Mono: simple th, double th lower, double th upper
        self.ivs_th_param[1] = np.array([0, 0, 255], dtype = np.uint8) #Red: simple th, double th lower, double th upper
        self.ivs_th_param[2] = np.array([0, 0, 255], dtype = np.uint8) #Green: simple th, double th lower, double th upper
        self.ivs_th_param[3] = np.array([0, 0, 255], dtype = np.uint8) #Blue: simple th, double th lower, double th upper


        self.ivs_blob_param = np.zeros((5),dtype=np.uint32) #index:- 0: min blob size, 1: max blob size, 2: lower threshold, 3: upper threshold, 4: bbox outline
        self.ivs_ocr_label_param = np.zeros((3),dtype=np.int32) #index:- 0: shift_x, 1: shift_y, 2: font size, 3: font thickness

        self.np_arr_blob_init()
        self.np_arr_ocr_init()


        self.__ivs_bbox_func_dict = {} ### Dictionary to store callable/function objects
        ### Init self.__ivs_bbox_func_dict
        self.__ivs_bbox_func_dict['Gain'] = []
        self.__ivs_bbox_func_dict['Threshold'] = []

        ###################################################################################################
        self.container = None
        self.ref_img_src = {}
        # Create ImageFrame in placeholder widget
        self.imframe = ttk.Frame(placeholder)  # placeholder of the ImageFrame object
        # Vertical and horizontal scrollbars for canvas
        hbar = ttk.Scrollbar(self.imframe, orient='horizontal')
        vbar = ttk.Scrollbar(self.imframe, orient='vertical')

        # Create canvas and bind it with scrollbars. Public for outer classes
        self.canvas = tk.Canvas(self.imframe, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)#, bg = 'pink')
        #self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.place(x=0, y=0, relheight=1, relwidth=1, anchor = 'nw')

        self.canvas.update_idletasks()  # wait till canvas is created
        hbar.configure(command=self.scroll_x)  # bind scrollbars to the canvas
        vbar.configure(command=self.scroll_y)
        # Bind events to the Canvas
        # self.imframe.bind('<Enter>', print_hello)
        # self.imframe.bind('<Leave>', print_hello)
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)

        if (isinstance(self.loaded_img, np.ndarray)) == True:
            self.canvas_init_load(local_img_split, ch_index)

        else:
            self.loaded_img = None
            pass

    def canvas_clear(self, init = True):
        if init == True: #Require Init after clear
            self.imscale = 1.0  # scale for the canvas image zoom, public for outer classes
            self.delta = 1.3  # zoom magnitude
            self.previous_state = 0  # previous state of the keyboard
            self.canvas_init_bool = False

            self.canvas_keybind_lock = True
            self.canvas_hide_img = True
            del self.loaded_img
            self.loaded_img = None
            self.canvas.delete("all")

        elif init == False:
            self.canvas_init_bool = True
            self.canvas_keybind_lock = True
            self.canvas_hide_img = True
            del self.loaded_img
            self.loaded_img = None

            self.canvas.delete('img')

    def canvas_clear_img(self):
        self.canvas.delete('img')

    def canvas_default_load(self, img = None, local_img_split = False, ch_index = 0
        , fit_to_display_bool = False, display_width = None, display_height = None
        , hist_img_src = None):

        display_width = convert_int(display_width)
        display_height = convert_int(display_height)

        if (isinstance(img, np.ndarray)) == True:
            new_width = img.shape[1]
            new_height = img.shape[0]

            fit_err = False

            if (isinstance(self.loaded_img, np.ndarray)) == True:
                if self.imwidth != new_width and self.imheight != new_height:
                    self.canvas_init_load(img = img, local_img_split = local_img_split, ch_index = ch_index, hist_img_src = hist_img_src)
                    if fit_to_display_bool == True:
                        if int_type_bool(display_width) == True and int_type_bool(display_height) == True:
                            if display_width > 0 and display_height > 0:
                                self.fit_to_display(display_width, display_height)
                            else:
                                fit_err = True
                        else:
                            fit_err = True

                else:
                    if self.canvas_init_bool == True:
                        self.canvas_reload(img = img, local_img_split = local_img_split, ch_index = ch_index, hist_img_src = hist_img_src)
                    elif self.canvas_init_bool == False:
                        self.canvas_init_load(img = img, local_img_split = local_img_split, ch_index = ch_index, hist_img_src = hist_img_src)
                        if fit_to_display_bool == True:
                            if int_type_bool(display_width) == True and int_type_bool(display_height) == True:
                                if display_width > 0 and display_height > 0:
                                    self.fit_to_display(display_width, display_height)
                                else:
                                    fit_err = True
                            else:
                                fit_err = True

            else:
                self.canvas_init_load(img = img, local_img_split = local_img_split, ch_index = ch_index, hist_img_src = hist_img_src)
                if fit_to_display_bool == True:
                    if int_type_bool(display_width) == True and int_type_bool(display_height) == True:
                        if display_width > 0 and display_height > 0:
                            self.fit_to_display(display_width, display_height)
                        else:
                            fit_err = True
                    else:
                        fit_err = True
            
            if fit_err == True:
                raise Exception("Could not perform fit to display function. Ensure that both 'display_width' and 'display_height' parameter are integers > 0.")
        else:
            raise Exception("Input 'img' is not a numpy array-type image!")

    def canvas_init_load(self, img = None, local_img_split = False, ch_index = 0, hist_img_src = None):
        self.canvas_init_bool = False

        if (isinstance(img, np.ndarray)) == True:
            self.loaded_img = img

        if (isinstance(self.loaded_img, np.ndarray)) == True:
            self.imscale = 1.0  # scale for the canvas image zoom, public for outer classes
            self.delta = 1.3  # zoom magnitude
            self.previous_state = 0  # previous state of the keyboard

            self.canvas.bind('<Configure>', lambda event: self.show_image())  # canvas is resized
            self.canvas.bind('<ButtonPress-1>', self.move_from)  # remember canvas position
            self.canvas.bind('<B1-Motion>',     self.move_to)  # move canvas to the new position

            self.canvas_keybind_lock = False

            # self.canvas.bind('<MouseWheel>', self.wheel)  # zoom for Windows and MacOS, but not Linux
            # self.canvas.bind('<Button-5>',   self.wheel)  # zoom for Linux, wheel scroll down
            # self.canvas.bind('<Button-4>',   self.wheel)  # zoom for Linux, wheel scroll up
            # Handle keystrokes in idle mode, because program slows down on a weak computers,
            # when too many key stroke events in the same time

            self.canvas.bind('<Key>', lambda event: self.canvas.after_idle(self.key_stroke, event))

            self.canvas.delete("all")

            self.local_img_split = local_img_split
            self.ch_index = ch_index

            with warnings.catch_warnings():  # suppress DecompressionBombWarning
                warnings.simplefilter('ignore')
                if self.local_img_split == True and len(self.loaded_img.shape) > 2:
                    self._IMG = Image.fromarray(self.loaded_img[:,:, self.ch_index])
                else:
                    self._IMG = Image.fromarray(self.loaded_img)

                if isinstance(hist_img_src, np.ndarray) == True:
                    if self.loaded_img.shape[0] == hist_img_src.shape[0] and self.loaded_img.shape[1] == hist_img_src.shape[1]:
                        self.ref_img_src['data'] = Image.fromarray(hist_img_src)
                    else:
                        self.ref_img_src['data'] = Image.fromarray(self.loaded_img)
                else:    
                    self.ref_img_src['data'] = Image.fromarray(self.loaded_img)

            self.imwidth, self.imheight = self._IMG.size  # public for outer classes

            self.min_side = min(self.imwidth, self.imheight)  # get the smaller image side

            # Create image pyramid
            self.pyramid *= 0
            self.pyramid.append(self._IMG)

            # Set ratio coefficient for image pyramid
            self.ratio = 1.0
            self.curr_img = 0  # current image from the pyramid
            self.scale_factor = np.multiply(self.imscale, self.ratio)  # image pyramide scale
            self.reduction = 2  # reduction degree of image pyramid


            w, h = self.pyramid[-1].size
            while w > 512 and h > 512:  # top pyramid image is around 512 pixels in size
                w = np.divide(w, self.reduction)  # divide on reduction degree
                h = np.divide(h, self.reduction)  # divide on reduction degree
                self.pyramid.append(self.pyramid[-1].resize((int(w), int(h)), self.filter))
            # Put image into container rectangle and use it to set proper coordinates to the image
            self.container = self.canvas.create_rectangle((0, 0, self.imwidth, self.imheight), width=0)

            self.canvas_hide_img = False
            self.show_image()  # show image on the canvas
            #self.canvas.focus_set()  # set focus on the canvas
            #NOTE if focus is not set, cannot use AWSD or left,up,down,right arrow key to move the image
            self.canvas_init_bool = True

    def canvas_reload(self, img = None, local_img_split = False, ch_index = 0, hist_img_src = None):
        if self.canvas_init_bool == False:
            raise Exception("Please initialize canvas using 'canvas_init_load' function, before using 'canvas_reload' function.")

        elif self.canvas_init_bool == True:
            if (isinstance(img, np.ndarray)) == True:
                self.loaded_img = img

            if (isinstance(self.loaded_img, np.ndarray)) == True:
                self.local_img_split = local_img_split
                self.ch_index = ch_index

                self.canvas_keybind_lock = False

                with warnings.catch_warnings():  # suppress DecompressionBombWarning
                    warnings.simplefilter('ignore')
                    if self.local_img_split == True and len(self.loaded_img.shape) > 2:
                        self._IMG = Image.fromarray(self.loaded_img[:,:, self.ch_index])
                    else:
                        self._IMG = Image.fromarray(self.loaded_img)
                    
                    if isinstance(hist_img_src, np.ndarray) == True:
                        if self.loaded_img.shape[0] == hist_img_src.shape[0] and self.loaded_img.shape[1] == hist_img_src.shape[1]:
                            self.ref_img_src['data'] = Image.fromarray(hist_img_src)
                        else:
                            self.ref_img_src['data'] = Image.fromarray(self.loaded_img)
                    else:    
                        self.ref_img_src['data'] = Image.fromarray(self.loaded_img)

                self.imwidth, self.imheight = self._IMG.size  # public for outer classes
                self.min_side = min(self.imwidth, self.imheight)  # get the smaller image side

                self.pyramid *= 0
                self.pyramid.append(self._IMG)

                w, h = self.pyramid[-1].size
                while w > 512 and h > 512:  # top pyramid image is around 512 pixels in size
                    w = np.divide(w, self.reduction)  # divide on reduction degree
                    h = np.divide(h, self.reduction)  # divide on reduction degree
                    self.pyramid.append(self.pyramid[-1].resize((int(w), int(h)), self.filter))

                self.canvas_hide_img = False
                self.show_image()  # show image on the canvas

                if self.roi_item is not None:
                    self.canvas.itemconfig(self.roi_item)

            #self.canvas.focus_set()  # set focus on the canvas
            #NOTE if focus is not set, cannot use AWSD or left,up,down,right arrow key to move the image

    def redraw_figures(self):
        """ Dummy function to redraw figures in the children classes """
        pass

    def place(self, **kw):
        self.imframe.place(**kw)

    def place_forget(self):
        self.imframe.place_forget()

    # noinspection PyUnusedLocal
    def scroll_x(self, *args, **kwargs):
        """ Scroll canvas horizontally and redraw the image """
        self.canvas.xview(*args)  # scroll horizontally
        self.show_image()  # redraw the image

    # noinspection PyUnusedLocal
    def scroll_y(self, *args, **kwargs):
        """ Scroll canvas vertically and redraw the image """
        self.canvas.yview(*args)  # scroll vertically
        self.show_image()  # redraw the image

    def dummy_bind(self, event = None):
        pass

    def move_from(self, event):
        if self.canvas_keybind_lock == False:
            """ Remember previous coordinates for scrolling with the mouse """
            self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        if self.canvas_keybind_lock == False:
            """ Drag (move) canvas to the new position """
            self.canvas.scan_dragto(event.x, event.y, gain=1)
            self.show_image()  # zoom tile and show it on the canvas

    def outside(self, x, y):
        """ Checks if the point (x,y) is outside the image area """
        bbox = self.canvas.coords(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            return False  # point (x,y) is inside the image area
        else:
            return True  # point (x,y) is outside the image area

    def _bound_to_mousewheel(self,event):
        # print('scroll active')
        self.canvas.bind_all('<MouseWheel>', self.wheel)  # zoom for Windows and MacOS, but not Linux
        self.canvas.bind_all('<Button-5>',   self.wheel)  # zoom for Linux, wheel scroll down
        self.canvas.bind_all('<Button-4>',   self.wheel)  # zoom for Linux, wheel scroll up

    def _unbound_to_mousewheel(self, event):
        # print('scroll disable')
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-5>")
        self.canvas.unbind_all("<Button-4>")

    def wheel(self, event):
        if self.canvas_keybind_lock == False:
            if (isinstance(self.loaded_img, np.ndarray)) == True:
                """ Zoom with mouse wheel """
                #print('Scrolling')
                x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
                y = self.canvas.canvasy(event.y)
                if self.outside(x, y):
                    return  # zoom only inside image area
                scale = 1.0
                # Respond to Linux (event.num) or Windows (event.delta) wheel event
                if event.num == 5 or event.delta == -120:  # scroll down, smaller
                    if round(self.min_side * self.imscale) < 30: return  # image is less than 30 pixels
                    self.imscale /= self.delta
                    scale        /= self.delta
                if event.num == 4 or event.delta == 120:  # scroll up, bigger
                    i = min(self.canvas.winfo_width(), self.canvas.winfo_height()) >> 1
                    if i < self.imscale: return  # 1 pixel is bigger than the visible area
                    self.imscale *= self.delta
                    scale        *= self.delta
                # Take appropriate image from the pyramid
                # k = self.imscale * self.ratio  # temporary coefficient
                # self.curr_img = min((-1) * int(math.log(k, self.reduction)), len(self.pyramid) - 1)    
                # self.scale_factor = k * math.pow(self.reduction, max(0, self.curr_img))

                # print('self.imscale: ', self.imscale)
                k = np.multiply(self.imscale, self.ratio) # temporary coefficient
                self.curr_img = min(-int(math.log(k, self.reduction)), len(self.pyramid) - 1)
                self.scale_factor = np.multiply(k, math.pow(self.reduction, max(0, self.curr_img)) )

                self.canvas.scale('all', x, y, scale, scale)  # rescale all objects
                # Redraw some figures before showing image on the screen
                self.show_image()

    def fit_to_display(self, disp_W, disp_H):
        # print('self.imwidth, self.imheight', self.imwidth, self.imheight)
        # print('disp_W, disp_H: ', disp_W, disp_H)
        if ((isinstance(self.loaded_img, np.ndarray)) == True) and self.canvas_hide_img == False:
            if self.imwidth > self.imheight:
                ref_disp_measure = disp_W
                ref_img_measure = self.imwidth
            elif self.imheight >= self.imwidth:
                ref_disp_measure = disp_H
                ref_img_measure = self.imheight

            set_img_measure = np.multiply(self.imscale,ref_img_measure)
            if ref_disp_measure < set_img_measure:
                # print('Zoom Out')
                if round(self.min_side * self.imscale) < 30: return
                while True:
                    set_img_measure = np.multiply(self.imscale,ref_img_measure)
                    if set_img_measure <= ref_disp_measure:
                        break

                    scale = 1.0
                    scale /= self.delta
                    self.imscale /= self.delta
                    k = np.multiply(self.imscale, self.ratio) # temporary coefficient
                    self.curr_img = min(-int(math.log(k, self.reduction)), len(self.pyramid) - 1)
                    self.scale_factor = np.multiply(k, math.pow(self.reduction, max(0, self.curr_img)) )

                    self.canvas.scale('all', 0, 0, scale, scale)
                    self.show_image()

            elif ref_disp_measure > set_img_measure:
            # elif ref_disp_measure > ref_img_measure:
                # print('Zoom In')
                self.canvas.update_idletasks()
                i = min(self.canvas.winfo_width(), self.canvas.winfo_height()) >> 1
                if i < self.imscale: return  # 1 pixel is bigger than the visible area
                # scale *= self.delta
                while True:
                    set_img_measure = np.multiply(self.imscale,ref_img_measure)
                    if set_img_measure > ref_disp_measure:
                        scale = 1.0
                        scale /= self.delta
                        self.imscale /= self.delta
                        k = np.multiply(self.imscale, self.ratio) # temporary coefficient
                        self.curr_img = min(-int(math.log(k, self.reduction)), len(self.pyramid) - 1)
                        self.scale_factor = np.multiply(k, math.pow(self.reduction, max(0, self.curr_img)) )

                        self.canvas.scale('all', 0, 0, scale, scale)
                        self.show_image()
                        break
                    elif set_img_measure == ref_disp_measure:
                        break

                    scale = 1.0
                    scale *= self.delta
                    self.imscale *= self.delta
                    k = np.multiply(self.imscale, self.ratio) # temporary coefficient
                    self.curr_img = min(-int(math.log(k, self.reduction)), len(self.pyramid) - 1)
                    self.scale_factor = np.multiply(k, math.pow(self.reduction, max(0, self.curr_img)) )

                    self.canvas.scale('all', 0, 0, scale, scale)
                    self.show_image()

            _offset_x = int(self.canvas.canvasx(0)) - int(self.box_image[0])
            _offset_y = int(self.canvas.canvasy(0)) - int(self.box_image[1])
            _centre_offset_x = int(np.divide((disp_W - int(self.box_image[2]-self.box_image[0]) ), 2))
            _centre_offset_y = int(np.divide((disp_H - int(self.box_image[3]-self.box_image[1]) ), 2))

            # print('self.imscale: ', self.imscale)

            self.canvas.scan_mark(0, 0)
            self.canvas.scan_dragto(_offset_x + _centre_offset_x, _offset_y +_centre_offset_y, gain=1)
            self.show_image()

    def key_stroke(self, event):
        if self.canvas_keybind_lock == False:
            """ Scrolling with the keyboard.
                Independent from the language of the keyboard, CapsLock, <Ctrl>+<key>, etc. """
            if event.state - self.previous_state == 4:  # means that the Control key is pressed
                pass  # do nothing if Control key is pressed
            else:
                self.previous_state = event.state  # remember the last keystroke state

                if event.keycode in [68, 39, 102]:  # scroll right: keys 'D', 'Right' or 'Numpad-6'
                    self.scroll_x('scroll',  -1, 'unit', event=event)
                elif event.keycode in [65, 37, 100]:  # scroll left: keys 'A', 'Left' or 'Numpad-4'
                    self.scroll_x('scroll', 1, 'unit', event=event)
                elif event.keycode in [87, 38, 104]:  # scroll up: keys 'W', 'Up' or 'Numpad-8'
                    self.scroll_y('scroll', 1, 'unit', event=event)
                elif event.keycode in [83, 40, 98]:  # scroll down: keys 'S', 'Down' or 'Numpad-2'
                    self.scroll_y('scroll',  -1, 'unit', event=event)


    def crop(self, bbox):
        """ Crop rectangle from the image and return it """
        #print('cropping')
        return self.pyramid[0].crop(bbox)

    def destroy(self):
        """ ImageFrame destructor """
        self._IMG.close()
        map(lambda i: i.close, self.pyramid)  # close all pyramid images
        del self.pyramid[:]  # delete pyramid list
        del self.pyramid  # delete pyramid variable
        self.canvas.destroy()
        self.imframe.destroy()

    def show_image(self):
        """ Show image on the Canvas. Implements correct image zoom almost like in Google Maps """
        self.crop_offset = None
        if self.container is not None and self.canvas_hide_img == False:
            self.box_image = self.canvas.coords(self.container)  # get image area
            #print('self.box_image: ', self.box_image)
            box_canvas = (self.canvas.canvasx(0),  # get visible area of the canvas
                          self.canvas.canvasy(0),
                          self.canvas.canvasx(self.canvas.winfo_width()),
                          self.canvas.canvasy(self.canvas.winfo_height()))
            box_img_int = tuple(map(int, self.box_image))  # convert to integer or it will not work properly
            # print('box_canvas: ', box_canvas)
            # print('self.box_image: ', self.box_image)
            # print('box_img_int: ', box_img_int)
            if len(self.box_image) > 0 and len(box_img_int) >= 4: # To prevent Index Error if empty.
                # Get scroll region box
                box_scroll = [min(box_img_int[0], box_canvas[0]), min(box_img_int[1], box_canvas[1]),
                              max(box_img_int[2], box_canvas[2]), max(box_img_int[3], box_canvas[3])]

                # Horizontal part of the image is in the visible area
                if  box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
                    box_scroll[0]  = box_img_int[0]
                    box_scroll[2]  = box_img_int[2]
                # Vertical part of the image is in the visible area
                if  box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
                    box_scroll[1]  = box_img_int[1]
                    box_scroll[3]  = box_img_int[3]

                x1 = max(box_canvas[0] - self.box_image[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
                y1 = max(box_canvas[1] - self.box_image[1], 0)
                x2 = min(box_canvas[2], self.box_image[2]) - self.box_image[0]
                y2 = min(box_canvas[3], self.box_image[3]) - self.box_image[1]
                
                try:
                    if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
                        image = self.pyramid[max(0, self.curr_img)].crop(  # crop current img from pyramid
                                            (int(np.divide(x1, self.scale_factor)), int(np.divide(y1, self.scale_factor)),
                                             int(np.divide(x2, self.scale_factor)), int(np.divide(y2, self.scale_factor)) ))

                        self.crop_offset = (int(np.divide(x1, self.scale_factor)), int(np.divide(y1, self.scale_factor)),
                                             int(np.divide(x2, self.scale_factor)), int(np.divide(y2, self.scale_factor)) )

                        # print('offset normal img: ', self.crop_offset)

                        if str(image.mode) != 'RGB':
                            self.draw_save_img = self._IMG.convert('RGB')# image.convert('RGB')

                        elif str(image.mode) == 'RGB':
                            self.draw_save_img = self._IMG.copy()# image
                            
                        imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1)), self.filter))
                        imageid = self.canvas.create_image(max(box_canvas[0], box_img_int[0]),
                                                           max(box_canvas[1], box_img_int[1]),
                                                           anchor='nw', image=imagetk, tags = 'img')

                        self.imageid = imageid
                        self.canvas.lower(imageid)  # set image into background
                        self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

                except Exception:# as e:
                    # print('Custom Zoom Class, show image() Error: ', e)
                    pass


    def ROI_disable(self):
        self.ROI_draw_clear()
        self.canvas.bind('<ButtonPress-3>', self.dummy_bind)
        self.canvas.bind('<ButtonRelease-3>', self.dummy_bind)
        self.canvas.bind('<B3-Motion>', self.dummy_bind)
        self.ROI_line_param_init()
        self.ROI_box_param_init()
        self.roi_line_exist = False
        self.roi_bbox_exist =  False

    def ROI_draw_clear(self):
        found = self.canvas.find_all()
        for iid in found:
            #print('iid: ', iid)
            if iid == self.container:
                pass
            else:
                if self.canvas.type(iid) == 'rectangle' or self.canvas.type(iid) == 'line':
                    self.canvas.delete(iid)

        if self.roi_bbox_label is not None:
            self.canvas.delete(self.roi_bbox_label)

    def ROI_box_enable(self, ivs_mode = None, func_list = []):
        _enable_status = False
        if ((isinstance(self.loaded_img, np.ndarray)) == True) and self.canvas_hide_img == False:
            self.canvas.bind('<ButtonPress-3>', self.ROI_box_mouse_down)
            self.canvas.bind('<ButtonRelease-3>', self.ROI_box_mouse_up)
            self.ROI_draw_clear()
            self.ROI_box_param_init()
            self.roi_bbox_exist =  False
            self.ivs_mode = ivs_mode

            if isinstance(func_list, list) == True:
                self.__ivs_bbox_func_dict[str(self.ivs_mode)] = None
                self.__ivs_bbox_func_dict[str(self.ivs_mode)] = func_list

            _enable_status = True

        return _enable_status


    def ROI_box_param_init(self):
        self.roi_bbox_img = None
        self.roi_bbox_hist_mono = None
        self.roi_bbox_hist_R = None
        self.roi_bbox_hist_G = None
        self.roi_bbox_hist_B = None
        pass

    def ROI_box_mouse_down(self, event):
        self.canvas.bind('<B3-Motion>', self.ROI_box_mouse_drag)

        if self.roi_bbox_exist == True:
            if self.ivs_mode == 'Camera':
                from main_GUI import main_GUI
                _cam_class = main_GUI.class_cam_conn.active_gui
                _cam_class.histogram_stop_auto_update()
                _cam_class.profile_stop_auto_update()
                if self.ivs_start_bool == True:
                    self.process_cancel = True
                    try:
                        ivs_class = _cam_class.ivs_tesseract_class
                        ivs_class.blob_num_detect_var.set(0)
                        ivs_class.blob_num_detect_label['fg'] = 'black'
                    except (AttributeError, tk.TclError):
                        pass
                    # _cam_class.IVS_delete_tk_draw()
                    try:
                        _cam_class.ivs_tesseract_class.IVS_delete_tk_draw()
                    except (AttributeError, tk.TclError):
                        pass
                    

            if self.ivs_mode == 'IVS-Blob':
                from main_GUI import main_GUI
                _imgproc_class = main_GUI.class_imgproc_gui
                _imgproc_class.ivs_ocr_win.IVS_OCR_clear()


        if self.roi_item is not None:
            found = event.widget.find_all()
            #print('found: ',found)
            for iid in found:
                #print('iid: ', iid)
                if iid == self.container:
                    pass
                else:
                    if event.widget.type(iid) == 'rectangle':
                        #print(iid)
                        event.widget.delete(iid)
                #THIS FUNCTION MUST HAVE DELETED THE ZOOM FUNCTION iid
        
        if self.roi_bbox_label is not None:
            self.canvas.delete(self.roi_bbox_label)

        self.roi_bbox_exist = False

        self.anchor = (event.widget.canvasx(event.x),
                       event.widget.canvasy(event.y))
        #print('self.anchor: ',self.anchor)
        self.roi_item = None
        self.roi_bbox_label = None


    def ROI_box_mouse_drag(self, event):        
        roi_bbox = self.anchor + (event.widget.canvasx(event.x),
                              event.widget.canvasy(event.y))
        #print('roi_bbox: ',roi_bbox)
        if self.roi_item is None:
            self.roi_item = event.widget.create_rectangle(roi_bbox, outline="yellow", activeoutline = "red", width = 2)

        else:
            event.widget.coords(self.roi_item, *roi_bbox)

    def ROI_box_mouse_up(self, event):        
        if self.roi_item:
            self.ROI_box_mouse_drag(event)
            self.roi_bbox_exist = True

            self.ROI_box_param_init()
            #print(event.widget)
            self.roi_box = tuple((int(round(v)) for v in event.widget.coords(self.roi_item)))
            # print('self.roi_box: ',self.roi_box)
            # print('self.imscale: ', self.imscale)
            # print(self.loaded_img.shape[1], self.loaded_img.shape[0])
            self.roi_box = list(self.roi_box)
            roi_label_x  = self.roi_box[0]
            roi_label_y  = self.roi_box[1]
            # print('self.roi_box before normalize: ', self.roi_box)

            self.roi_box[0] = max(int( np.divide((self.roi_box[0] - self.box_image[0]), self.imscale)), 0)
            self.roi_box[1] = max(int( np.divide((self.roi_box[1] - self.box_image[1]), self.imscale)), 0)
            self.roi_box[2] = min(int( np.divide((self.roi_box[2] - self.box_image[0]), self.imscale)), self.imwidth) 
            self.roi_box[3] = min(int( np.divide((self.roi_box[3] - self.box_image[1]), self.imscale)), self.imheight)
            self.roi_box = tuple(self.roi_box)
            # print('self.roi_box after normalize: ', self.roi_box)

            # print('self.box_image: ', self.box_image)

            roi_size = np.multiply(self.roi_box[2] - self.roi_box[0], self.roi_box[3] - self.roi_box[1])

            if self.roi_box[0] == self.roi_box[2] or self.roi_box[1] == self.roi_box[3]:
                self.ROI_draw_clear()
                self.roi_bbox_exist = False

            else:
                if self.roi_bbox_label is None:
                    self.roi_bbox_label =\
                        self.canvas.create_text(roi_label_x, roi_label_y, activefill = "red", fill="yellow", font = 'Helvetica', anchor = 'sw', text = 'ROI Size: ' + str(roi_size) + ' pix.')

                if self.ivs_mode == 'Gain':
                    if self.ivs_mode in self.__ivs_bbox_func_dict:
                        for func_obj in self.__ivs_bbox_func_dict[self.ivs_mode]:
                            if callable(func_obj) == True:
                                func_obj()

                elif self.ivs_mode == 'Camera':
                    from main_GUI import main_GUI
                    _cam_class = main_GUI.class_cam_conn.active_gui
                    if _cam_class.curr_graph_view == 'histogram':
                        _cam_class.histogram_auto_update()

                elif self.ivs_mode == 'IVS-Blob':
                    # print(self.ivs_mode)
                    from main_GUI import main_GUI
                    _imgproc_class = main_GUI.class_imgproc_gui
                    _imgproc_class.ivs_ocr_win.IVS_OCR_func()

                elif self.ivs_mode == 'Threshold':
                    # print(self.__ivs_bbox_func_dict)
                    if self.ivs_mode in self.__ivs_bbox_func_dict:
                        for func_obj in self.__ivs_bbox_func_dict[self.ivs_mode]:
                            if callable(func_obj) == True:
                                func_obj()

    def ROI_box_pixel_update(self):
        # print(self.ivs_mode)
        hist_return_list = []
        self.roi_bbox_crop = self.ref_img_src['data'].crop(self.roi_box)
        # print(self.ref_img_src['data'].mode)
        self.roi_bbox_img = np.array(self.roi_bbox_crop) #convert to numpy array to display in open cv
        #print(self.roi_bbox_img)
        if len(self.roi_bbox_img.shape) == 2:
            self.roi_bbox_hist_mono = cv2.calcHist([self.roi_bbox_img],[0],None,[256],[0,256])
            hist_return_list.append(self.roi_bbox_hist_mono)

        elif len(self.roi_bbox_img.shape) == 3:
            self.roi_bbox_hist_R = cv2.calcHist([self.roi_bbox_img[:,:,0]],[0],None,[256],[0,256])
            self.roi_bbox_hist_G = cv2.calcHist([self.roi_bbox_img[:,:,1]],[0],None,[256],[0,256])
            self.roi_bbox_hist_B = cv2.calcHist([self.roi_bbox_img[:,:,2]],[0],None,[256],[0,256])

            hist_return_list.append(self.roi_bbox_hist_R)
            hist_return_list.append(self.roi_bbox_hist_G)
            hist_return_list.append(self.roi_bbox_hist_B)

        return hist_return_list


    def ROI_box_img_update(self):
        if (isinstance(self.roi_box, tuple) == True) and (len(self.roi_box) == 4):
            self.roi_bbox_crop = self.ref_img_src['data'].crop(self.roi_box)
            self.roi_bbox_img = np.array(self.roi_bbox_crop) #convert to numpy array to display in open cv
            # cv2.imshow('self.roi_bbox_img', self.roi_bbox_img)


            #self.roi_box[0]: canvas_offset_x
            #self.roi_box[1]: canvas_offset_y
            #self.roi_bbox_img: ROI image
            #self.imscale: current zoom-state of image in canvas
            #self.box_image[0]: img_offset_x
            #self.box_image[1]: img_offset_y
            return_list = [self.roi_box[0], self.roi_box[1], self.roi_bbox_img, self.imscale, self.box_image[0], self.box_image[1]]
            return return_list

        return None


    def ROI_line_param_init(self):
        self.roi_line_pixel_mono *= 0
        self.roi_line_pixel_R *= 0
        self.roi_line_pixel_G *= 0
        self.roi_line_pixel_B *= 0
        self.roi_line_pixel_index *= 0
        self.roi_line_hist_mono = np.zeros((256, 1), dtype = np.uint16)
        self.roi_line_hist_R = np.zeros((256, 1), dtype = np.uint16)
        self.roi_line_hist_G = np.zeros((256, 1), dtype = np.uint16)
        self.roi_line_hist_B = np.zeros((256, 1), dtype = np.uint16)
        

    def ROI_line_enable(self, ivs_mode = None, func_list = []):
        _enable_status = False
        if ((isinstance(self.loaded_img, np.ndarray)) == True) and self.canvas_hide_img == False:
            self.canvas.bind('<ButtonPress-3>', self.ROI_line_mouse_down)
            self.canvas.bind('<ButtonRelease-3>', self.ROI_line_mouse_up)
            self.ROI_draw_clear()
            self.ROI_line_param_init()
            self.roi_line_exist = False
            self.ivs_mode = ivs_mode

            if isinstance(func_list, list) == True:
                self.__ivs_bbox_func_dict[str(self.ivs_mode)] = None
                self.__ivs_bbox_func_dict[str(self.ivs_mode)] = func_list

            _enable_status = True

        return _enable_status

    def ROI_line_mouse_down(self, event):
        self.canvas.bind('<B3-Motion>', self.ROI_line_mouse_drag)

        if self.roi_item != None:
            found = event.widget.find_all()
            #print('found: ',found)
            for iid in found:
                #print('iid: ', iid)
                if iid == self.container:
                    pass
                else:
                    if event.widget.type(iid) == 'line':
                        #print(iid)
                        event.widget.delete(iid)

        self.roi_line_exist = False

        self.anchor = (event.widget.canvasx(event.x),
                       event.widget.canvasy(event.y))
        #print('self.anchor: ',self.anchor)
        self.roi_item = None

        if self.ivs_mode == 'Camera':
            from main_GUI import main_GUI
            main_GUI.class_cam_conn.active_gui.histogram_stop_auto_update()
            main_GUI.class_cam_conn.active_gui.profile_stop_auto_update()

    def ROI_line_mouse_drag(self, event):        
        roi_draw_line = self.anchor + (event.widget.canvasx(event.x),
                              event.widget.canvasy(event.y))
        #print('roi_draw_line: ',roi_draw_line)

        if self.roi_item is None:
            self.roi_item = event.widget.create_line(roi_draw_line, fill="yellow", arrow = tk.LAST, arrowshape = (12, 15, 5))
        else:
            event.widget.coords(self.roi_item, *roi_draw_line)

    def ROI_line_mouse_up(self, event):
        if self.roi_item:
            self.ROI_line_mouse_drag(event)
            self.roi_line_exist = True
            #print(event.widget)
            roi_line = tuple((int(round(v)) for v in event.widget.coords(self.roi_item)))
            #print('roi_line: ',roi_line)
            # print('self.imscale: ', self.imscale)
            roi_line = list(roi_line)
            roi_line[0] = int( np.divide((roi_line[0] - self.box_image[0]), self.imscale))
            roi_line[1] = int( np.divide((roi_line[1] - self.box_image[1]), self.imscale))
            roi_line[2] = int( np.divide((roi_line[2] - self.box_image[0]), self.imscale))
            roi_line[3] = int( np.divide((roi_line[3] - self.box_image[1]), self.imscale))
            roi_start_point = (roi_line[0], roi_line[1])
            roi_end_point = (roi_line[2], roi_line[3])
            #roi_line = tuple(roi_line)
            #print('roi_line: ',roi_line)
            self.ROI_line_param_init()

            ref_img = np.array(self.ref_img_src['data'])

            line_mask_arr = np.zeros(ref_img.shape, ref_img.dtype)
            if len(ref_img.shape) == 2:
                #print('mono')
                line_mask_img = cv2.line(line_mask_arr, roi_start_point, roi_end_point, color=(255), thickness=1)
                line_mask_coor = np.argwhere(line_mask_img == 255)
                #print(line_mask_coor)
                self.roi_line_coor = self.ROI_line_coor_sort(line_mask_coor, roi_line)

                for i in range (self.roi_line_coor.shape[0]):
                    self.roi_line_pixel_mono.append(ref_img[ self.roi_line_coor[i][0] ] [ self.roi_line_coor[i][1]])
                    self.roi_line_pixel_index.append(i)
                    #self.roi_line_pixel_index.append(( self.roi_line_coor[i][1], self.roi_line_coor[i][0]))

                pixel_dict = Counter(self.roi_line_pixel_mono)
                for key, value in pixel_dict.items():
                    self.roi_line_hist_mono[key] = value
                
                #print(self.roi_line_hist_mono)
                #print(self.roi_line_pixel_index)

            elif len(ref_img.shape) == 3:
                line_mask_img = cv2.line(line_mask_arr, roi_start_point, roi_end_point, color=(255,255,255), thickness=1)
                line_mask_coor = np.argwhere(line_mask_img == 255)
                #print(line_mask_coor[:,[0,1]])
                line_mask_coor = line_mask_coor[:,[0,1]]
                #print(line_mask_coor)
                self.roi_line_coor = self.ROI_line_coor_sort(line_mask_coor, roi_line)

                for i in range (self.roi_line_coor.shape[0]):
                    self.roi_line_pixel_R.append((ref_img[:,:,0] )[ self.roi_line_coor[i][0] ] [ self.roi_line_coor[i][1]])
                    self.roi_line_pixel_G.append((ref_img[:,:,1] )[ self.roi_line_coor[i][0] ] [ self.roi_line_coor[i][1]])
                    self.roi_line_pixel_B.append((ref_img[:,:,2] )[ self.roi_line_coor[i][0] ] [ self.roi_line_coor[i][1]])
                    self.roi_line_pixel_index.append(i)

                pixel_dict = Counter(self.roi_line_pixel_R)
                for key, value in pixel_dict.items():
                    self.roi_line_hist_R[key] = value

                pixel_dict = Counter(self.roi_line_pixel_G)
                for key, value in pixel_dict.items():
                    self.roi_line_hist_G[key] = value

                pixel_dict = Counter(self.roi_line_pixel_B)
                for key, value in pixel_dict.items():
                    self.roi_line_hist_B[key] = value
            #print(self.roi_line_pixel_R)
            #print(self.roi_line_pixel_mono)
            #print(self.roi_line_pixel_index)

            if self.ivs_mode == 'Gain':
                if self.ivs_mode in self.__ivs_bbox_func_dict:
                    for func_obj in self.__ivs_bbox_func_dict[self.ivs_mode]:
                        if callable(func_obj) == True:
                            func_obj()

            elif self.ivs_mode == 'Camera':
                from main_GUI import main_GUI
                _cam_class = main_GUI.class_cam_conn.active_gui
                if _cam_class.curr_graph_view == 'histogram':
                    _cam_class.histogram_auto_update()

                elif _cam_class.curr_graph_view == 'profile':
                    _cam_class.profile_auto_update()

            elif self.ivs_mode == 'Threshold':
                # print(self.__ivs_bbox_func_dict)
                if self.ivs_mode in self.__ivs_bbox_func_dict:
                    for func_obj in self.__ivs_bbox_func_dict[self.ivs_mode]:
                        if callable(func_obj) == True:
                            func_obj()

            del ref_img
            
    def ROI_line_pixel_update(self):
        hist_return_list = []
        self.ROI_line_param_init()

        ref_img = np.array(self.ref_img_src['data'])

        if len(ref_img.shape) == 2:
            for i in range (self.roi_line_coor.shape[0]):
                self.roi_line_pixel_mono.append(ref_img[ self.roi_line_coor[i][0] ] [ self.roi_line_coor[i][1]])
                self.roi_line_pixel_index.append(i)

            pixel_dict = Counter(self.roi_line_pixel_mono)
            for key, value in pixel_dict.items():
                self.roi_line_hist_mono[key] = value

            hist_return_list.append(self.roi_line_hist_mono)

        elif len(ref_img.shape) == 3:
            for i in range (self.roi_line_coor.shape[0]):
                self.roi_line_pixel_R.append((ref_img[:,:,0] )[ self.roi_line_coor[i][0] ] [ self.roi_line_coor[i][1]])
                self.roi_line_pixel_G.append((ref_img[:,:,1] )[ self.roi_line_coor[i][0] ] [ self.roi_line_coor[i][1]])
                self.roi_line_pixel_B.append((ref_img[:,:,2] )[ self.roi_line_coor[i][0] ] [ self.roi_line_coor[i][1]])
                self.roi_line_pixel_index.append(i)

            pixel_dict = Counter(self.roi_line_pixel_R)
            for key, value in pixel_dict.items():
                self.roi_line_hist_R[key] = value

            pixel_dict = Counter(self.roi_line_pixel_G)
            for key, value in pixel_dict.items():
                self.roi_line_hist_G[key] = value

            pixel_dict = Counter(self.roi_line_pixel_B)
            for key, value in pixel_dict.items():
                self.roi_line_hist_B[key] = value

            hist_return_list.append(self.roi_line_hist_R)
            hist_return_list.append(self.roi_line_hist_G)
            hist_return_list.append(self.roi_line_hist_B)

        del ref_img
        
        return (self.roi_line_pixel_index, self.roi_line_pixel_mono, self.roi_line_pixel_R, self.roi_line_pixel_G, self.roi_line_pixel_B
            , hist_return_list)

    def ROI_line_coor_sort(self, coor_arr, roi_coor):
        dist_x = np.linalg.norm(roi_coor[0] - roi_coor[2])
        dist_y = np.linalg.norm(roi_coor[1] - roi_coor[3])
        #print(dist_x, dist_y)
        if dist_x >= dist_y:
            sort_arr = coor_arr[coor_arr[:,1].argsort()]
            if roi_coor[0] < roi_coor[2]:
                pass
            elif roi_coor[0] > roi_coor[2]:
                sort_arr = sort_arr[::-1]

        elif dist_x < dist_y:
            sort_arr = coor_arr[coor_arr[:,0].argsort()]
            if roi_coor[1] < roi_coor[3]:
                pass
            elif roi_coor[1] > roi_coor[3]:
                sort_arr = sort_arr[::-1]

        return sort_arr

    ###################################################################################################################
    #IVS FUNCTIONS
    def np_arr_blob_init(self):
        self.ivs_blob_param[0] = 100 #min size
        self.ivs_blob_param[1] = 1000 #max size
        self.ivs_blob_param[2] = 0 #lower th
        self.ivs_blob_param[3] = 0 #upper th
        self.ivs_blob_param[4] = 2 #bbox outline

    def np_arr_ocr_init(self):
        self.ivs_ocr_label_param[0] = 0 #shift x
        self.ivs_ocr_label_param[1] = 0 #shift y
        self.ivs_ocr_label_param[2] = 18 #font size

    def Check_Tesseract_API(self):
        return isinstance(self.tess_api, PyTessBaseAPI)

    def Tesseract_API_load(self, tessdata_path = os.getcwd() + '\\tessdata', lang = 'eng', psm = PSM.SINGLE_BLOCK, oem = OEM.TESSERACT_LSTM_COMBINED):
        # print('tessdata_path, lang, psm, oem: ', tessdata_path, lang, psm, oem)
        # print(dir(PyTessBaseAPI))
        if isinstance(self.tess_api, PyTessBaseAPI) == False:
            try:
                os.environ['OMP_THREAD_LIMIT'] = '1' ## Comment: Limit OpenMP number of threads
                get_languages(tessdata_path)
                self.tess_api = PyTessBaseAPI(path = tessdata_path
                    , lang = lang
                    , psm = psm, oem = oem)
            except Exception:
                del self.tess_api
                self.tess_api = None

        elif isinstance(self.tess_api, PyTessBaseAPI) == True:
            try:
                self.tess_api.End()
                os.environ['OMP_THREAD_LIMIT'] = '1' ## Comment: Limit OpenMP number of threads
                get_languages(tessdata_path)
                self.tess_api = PyTessBaseAPI(path = tessdata_path
                    , lang = lang
                    , psm = psm, oem = oem)

            except Exception:
                del self.tess_api
                self.tess_api = None

        return self.tess_api


    def ROI_Box_Blob_Morphology(self, morph_data_dict, morph_widget_name_list, morph_type_list, kernel_type_list, _img = None):
        # print(morph_data_dict)
        # print(morph_widget_name_list)
        if type(morph_data_dict) == dict:
            if len(morph_data_dict) > 0 and _img is not None and (isinstance(_img, np.ndarray)) == True:
                name_list = morph_widget_name_list
                try:
                    for _, data in morph_data_dict.items():
                        if self.ivs_start_bool == False:
                            break
                        if self.process_cancel == True:
                            # print('Process Interrupt: ROI_Box_Blob_Morphology')
                            break

                        tk_widget = data[0]
                        morph_type = data[1]

                        morph_kernel = None
                        kernel_size = None
                        # print(tk_widget)
                        # print(morph_type)
                        # print(tk_widget[name_list[2]])
                        # print(tk_widget[name_list[1]])
                        try:
                            kernel_size = int(tk_widget[name_list[2]].get())
                        except Exception:
                            kernel_size = None

                        if kernel_size is None:
                            continue

                        kernel_type = tk_widget[name_list[1]].get()

                        # print(kernel_size, kernel_type)

                        if kernel_type == kernel_type_list[0]:
                            morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(kernel_size, kernel_size))

                        elif kernel_type == kernel_type_list[1]:
                            morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(kernel_size, kernel_size))

                        elif kernel_type == kernel_type_list[2]:
                            morph_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(kernel_size, kernel_size))
                        # print(kernel_size)

                        # print(morph_kernel)

                        if morph_kernel is not None and morph_type_list is not None:
                            if morph_type == morph_type_list[0]:
                                _img = cv2.dilate(_img, morph_kernel, iterations = 1)

                            elif morph_type == morph_type_list[1]:
                                _img = cv2.erode(_img, morph_kernel, iterations = 1)

                            elif morph_type == morph_type_list[2]:
                                _img = cv2.morphologyEx(_img, cv2.MORPH_CLOSE, morph_kernel)

                            elif morph_type == morph_type_list[3]:
                                _img = cv2.morphologyEx(_img, cv2.MORPH_OPEN, morph_kernel)


                except Exception as e:
                    print('Exception, ROI_Box_Blob_Morphology error: ', e)
                    return _img            
                
                return _img

        return _img

    def opencv_blob_binarize(self, gray_img, th_lo_val, th_hi_val, black_on_white = True
        , morph_data_dict = None, morph_widget_name_list = None, morph_type_list = None, kernel_type_list = None):

        if len(gray_img.shape) == 2:
            bin_img = cv2.inRange(gray_img, th_lo_val, th_hi_val)
            #pixel values between th_lo_val and th_hi_val will be binarize to 255.
            # morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(10,10))

            if th_lo_val == th_hi_val:
                bin_img[:] = 0

            #cnt_img: to find the blob using open-cv contour
            #out_img: to find the apply tesseract OCR. 
            #While tesseract version 3.05 (and older) handle inverted image (dark background and light text) without problem, for 4.x version use dark text on light background.

            if black_on_white == False: # input img is white foreground, black background
                bin_img = cv2.bitwise_not(bin_img)
                ################################################################################
                #MORPHOLOGY OPERATION (ADDED 13-9-2021)
                if morph_data_dict is not None and type(morph_data_dict) == dict:
                    if len(morph_data_dict) > 0:
                        bin_img = self.ROI_Box_Blob_Morphology(morph_data_dict, morph_widget_name_list, morph_type_list, kernel_type_list, bin_img)
                ################################################################################
                cnt_img = bin_img.copy()
                out_img = bin_img.copy()
                # out_img = cv2.bitwise_not(bin_img) 

            elif black_on_white == True: # input img is black foreground, white background
                ################################################################################
                #MORPHOLOGY OPERATION (ADDED 13-9-2021)
                if morph_data_dict is not None and type(morph_data_dict) == dict:
                    if len(morph_data_dict) > 0:
                        bin_img = self.ROI_Box_Blob_Morphology(morph_data_dict, morph_widget_name_list, morph_type_list, kernel_type_list, bin_img)
                ################################################################################
                cnt_img = bin_img.copy()
                out_img = bin_img.copy()
                # out_img = cv2.bitwise_not(bin_img)

            # cv2.imshow('cnt_img', cnt_img)
            # cv2.imshow('out_img', out_img)
            return cnt_img, out_img

        else:
            return None, None

    def opencv_blob_search(self, cnt_img, bin_img):
        blob_bbox = []
        out_cnt = []
        if isinstance(cnt_img, np.ndarray) == True and isinstance(bin_img, np.ndarray) == True:
            contours = cv2.findContours(cnt_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # contours = cv2.findContours(cnt_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cnts = contours[0] if len(contours) == 2 else contours[1]
            out_img = np.zeros([bin_img.shape[0], bin_img.shape[1]],"uint8")
            # print('----------------------\nContour Found~\n', len(cnts))
            # cv2.drawContours(out_img, cnts, -1, 255, -1)
            # print(len(cnts))
            if len(cnts) > 5000:
                out_img = bin_img
                del blob_bbox
                blob_bbox = None

            else:
                for cnt in cnts:
                    if self.ivs_start_bool == False:
                        break
                    if self.process_cancel == True:
                        # print('Process Interrupt: opencv_blob_search')
                        break
                    x,y,w,h = cv2.boundingRect(cnt)

                    pix_size = np.multiply(w, h)

                    if self.ivs_blob_param[0] <= pix_size <= self.ivs_blob_param[1]:
                        out_cnt.append(cnt)
                        blob_bbox.append((x,y,x + w, y + h))

                # print(len(blob_bbox))
                if 0 < len(blob_bbox) <= 1000:
                    cv2.drawContours(out_img, out_cnt, -1, 255, -1)
                    out_img = cv2.bitwise_and(out_img, bin_img)
                    
                    pass
                elif len(blob_bbox) == 0:
                    out_img = bin_img
                    pass
                else:
                    out_img = bin_img
                    del blob_bbox
                    blob_bbox = None

            # cv2.imshow('Contour', out_img)
        
        return blob_bbox, out_img


    def ROI_Box_Blob(self, roi_img = None, black_on_white = True, morph_data_dict = None, morph_widget_name_list = None, morph_type_list = None, kernel_type_list = None):
        # blob_results = None
        # print(roi_img)
        if self.roi_bbox_exist == True:
            if (int(self.ivs_blob_param[3]) < int(self.ivs_blob_param[2])) \
            or (int(self.ivs_blob_param[1]) < int(self.ivs_blob_param[0])):
                pass

            else:
                if len(roi_img.shape) == 2:
                    gray_img = roi_img

                    cnt_img, bin_img = self.opencv_blob_binarize(gray_img, int(self.ivs_blob_param[2]), int(self.ivs_blob_param[3]), black_on_white
                        , morph_data_dict, morph_widget_name_list, morph_type_list, kernel_type_list)

                    # cv2.imshow('Bin img', bin_img)

                    blob_bbox, bin_img = self.opencv_blob_search(cnt_img, bin_img)

                    #While tesseract version 3.05 (and older) handle inverted image (dark background and light text) without problem, for 4.x version use dark text on light background.
                    bin_img = cv2.bitwise_not(bin_img)

                    return bin_img, blob_bbox

                elif len(roi_img.shape) > 2:
                    if roi_img.shape[2] == 3:
                        gray_img = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)

                        cnt_img, bin_img = self.opencv_blob_binarize(gray_img, int(self.ivs_blob_param[2]), int(self.ivs_blob_param[3]), black_on_white
                            , morph_data_dict, morph_widget_name_list, morph_type_list, kernel_type_list)

                        blob_bbox, bin_img = self.opencv_blob_search(cnt_img, bin_img)

                        #While tesseract version 3.05 (and older) handle inverted image (dark background and light text) without problem, for 4.x version use dark text on light background.
                        bin_img = cv2.bitwise_not(bin_img)

                        return bin_img, blob_bbox

                    elif roi_img.shape[2] == 4:
                        gray_img = cv2.cvtColor(roi_img, cv2.COLOR_BGRA2GRAY)
                        
                        cnt_img, bin_img = self.opencv_blob_binarize(gray_img, int(self.ivs_blob_param[2]), int(self.ivs_blob_param[3]), black_on_white
                            , morph_data_dict, morph_widget_name_list, morph_type_list, kernel_type_list)

                        blob_bbox, bin_img = self.opencv_blob_search(cnt_img, bin_img)

                        #While tesseract version 3.05 (and older) handle inverted image (dark background and light text) without problem, for 4.x version use dark text on light background.
                        bin_img = cv2.bitwise_not(bin_img)

                        return bin_img, blob_bbox

        return None, None

    def ROI_Box_Tess_OCR(self, input_img, ocr_result, canvas_offset_y, ocr_timeout = 0, ocr_index = 0, confidence_enable = True):
        if isinstance(self.tess_api, PyTessBaseAPI) == True:
            try:
                self.tess_api.Clear()
                if self.ivs_start_bool == True and self.process_cancel == False:
                    # self.tess_api.Clear()
                    _data_list = []
                    pil_img = Image.fromarray(input_img)
                    self.tess_api.SetImage(pil_img)
                    # print(str(self.tess_api.GetUTF8Text()))
                    level = RIL.SYMBOL
                    """
                    RIL MODE:
                    RIL.SYMBOL #for Symbol/character within a word
                    RIL.BLOCK #for Block of text/image/separator line
                    RIL.PARA #for Paragraph within a block
                    RIL.TEXTLINE #for Line within a paragraph
                    RIL.WORD #for Word within a textline
                    """
                    # print('Recognize Start...', 'timeout: ', ocr_timeout)
                    self.tess_api.Recognize(ocr_timeout) #This is time consuming if binary image has various pixel noise.
                    #Recognize parameter: timeout(msec)
                    # print('Recognize Done...')

                    ri = self.tess_api.GetIterator()
                    # print(dir(ri))

                    if confidence_enable == True:
                        _confidence = ri.Confidence(level)
                        # print('confidence threshold: ', _confidence)
                        if float(_confidence) >= 85:
                            boxes = ri.BoundingBox(level)
                            _ocr_str = ri.GetUTF8Text(level)
                            _ocr_str = re.sub("[\s\n\r]+", "", _ocr_str)
                            # print(_ocr_str, _confidence, np.multiply(boxes[2] - boxes[0], boxes[3] - boxes[1]))
                            if _ocr_str != '':
                                _data_list.append([_ocr_str, boxes])

                    elif confidence_enable == False:
                        _ocr_str = ri.GetUTF8Text(level)
                        _ocr_str = re.sub("[\s\n\r]+", "", _ocr_str)
                        boxes = ri.BoundingBox(level)
                        if _ocr_str != '':
                            _data_list.append([_ocr_str, boxes])

                    while(ri.Next(level)):
                        if self.ivs_start_bool == False:
                            break
                        if self.process_cancel == True:
                            # print('Process Interrupt: ROI_Box_Tess_OCR')
                            break
                        if confidence_enable == True:
                            _confidence = ri.Confidence(level)
                            if float(_confidence) >= 85:
                                boxes = ri.BoundingBox(level)
                                _ocr_str = ri.GetUTF8Text(level)
                                _ocr_str = re.sub("[\s\n\r]+", "", _ocr_str)
                                # print(_ocr_str, _confidence, np.multiply(boxes[2] - boxes[0], boxes[3] - boxes[1]))
                                if _ocr_str != '':
                                    _data_list.append([_ocr_str, boxes])

                        elif confidence_enable == False:
                            _ocr_str = ri.GetUTF8Text(level)
                            _ocr_str = re.sub("[\s\n\r]+", "", _ocr_str)
                            boxes = ri.BoundingBox(level)
                            if _ocr_str != '':
                                _data_list.append([_ocr_str, boxes])

                    # print('detected ocr lst: ', _data_list)
                    if len(_data_list) == 0:
                        return None

                    elif len(_data_list) > 0:
                        for _data in _data_list:
                            if self.ivs_start_bool == False:
                                break
                            if self.process_cancel == True:
                                # print('Process Interrupt: ROI_Box_Tess_OCR')
                                break
                            dict_id = 'id ' + str(ocr_index)
                            ocr_result[dict_id] = [_data[0], 
                            ( int(_data[1][0]), int(_data[1][1]), int(_data[1][2]), int(_data[1][3]) )]
                            ocr_index = ocr_index + 1

                        # print(ocr_result)
                        return ocr_result


                else:
                    return None
            except Exception:# as e:
                # print('Exception ROI_Box_Tess_OCR: ', e)
                return None

        else:
            return None


    def Draw_Blob_Detection(self, blob_results = None, canvas_offset_x = 0, canvas_offset_y = 0, imscale = 1, img_offset_x = 0, img_offset_y = 0):
        if self.roi_bbox_exist == True:
            if blob_results is not None and type(blob_results) == list:
                if len(blob_results) > 0:
                    blob_bbox_tk_list = []
                    blob_number = int(len(blob_results))

                    for index in range(blob_number):
                        if self.ivs_start_bool == False:
                            break
                        if self.process_cancel == True:
                            break
                        start_coor = (int(blob_results[index][0] + canvas_offset_x), int(blob_results[index][1] + canvas_offset_y))
                        end_coor = (int(blob_results[index][2] + canvas_offset_x), 
                            int(blob_results[index][3] + canvas_offset_y))

                        box_x1 = np.multiply(start_coor[0], imscale) + img_offset_x
                        box_y1 = np.multiply(start_coor[1], imscale) + img_offset_y
                        box_x2 = np.multiply(end_coor[0], imscale) + img_offset_x
                        box_y2 = np.multiply(end_coor[1], imscale) + img_offset_y

                        canvas_blob_bbox = (box_x1, box_y1, box_x2, box_y2)
                        try:
                            self.canvas.create_rectangle(canvas_blob_bbox, outline="red", width = self.ivs_blob_param[4], tags = 'blob_box')
                        except (AttributeError, tk.TclError):# as e:
                            #print('Error Draw_Blob_Detection: ', e)
                            pass


    def Tess_Draw_OCR_Tag(self, ocr_result = None, canvas_offset_x = 0, canvas_offset_y = 0, imscale = 1, img_offset_x = 0, img_offset_y = 0):
        if (ocr_result is not None and type(ocr_result) == dict):
            if len(ocr_result) > 0:
                
                font_size = str(self.ivs_ocr_label_param[2])
                self.text_font.configure(size= int(font_size))

                for _, ocr_data in ocr_result.items():
                    if self.ivs_start_bool == False:
                        break
                    if self.process_cancel == True:
                        break

                    midpoint_x = np.multiply(0.7, (ocr_data[1][2] - ocr_data[1][0]))

                    text_x = np.multiply(ocr_data[1][0] + midpoint_x + canvas_offset_x + self.ivs_ocr_label_param[0]
                        , imscale) + img_offset_x

                    text_y = np.multiply(ocr_data[1][3] + canvas_offset_y + self.ivs_ocr_label_param[1]
                        , imscale) + img_offset_y

                    try:
                        self.canvas.create_text(text_x, text_y, fill="red", font = self.text_font, anchor = 'n', text = ocr_data[0], tags = 'ocr_tag')
                    except (AttributeError, tk.TclError):# as e:
                        # print('Error Tess_Draw_OCR_Tag: ', e)
                        pass

