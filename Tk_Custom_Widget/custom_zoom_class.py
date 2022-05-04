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
    def __init__(self, placeholder, loaded_img = None, local_img_split = False, ch_index = 0): 
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


                if self.ivs_mode == 'Camera':
                    from main_GUI import main_GUI
                    _cam_class = main_GUI.class_cam_conn.active_gui
                    if _cam_class.curr_graph_view == 'histogram':
                        _cam_class.histogram_auto_update()


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

            if self.ivs_mode == 'Camera':
                from main_GUI import main_GUI
                _cam_class = main_GUI.class_cam_conn.active_gui
                if _cam_class.curr_graph_view == 'histogram':
                    _cam_class.histogram_auto_update()

                elif _cam_class.curr_graph_view == 'profile':
                    _cam_class.profile_auto_update()

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
