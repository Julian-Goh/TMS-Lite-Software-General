import tkinter as tk
import numpy as np
import os
from os import path
from imageio import imread
from PIL import Image, ImageTk
import cv2

import openpyxl
import io

class PreviewDisp(object):
    def __init__(self, widget, shift_x_disp = 0, shift_y_disp = 0, font = 'Tahoma 10', width = None, height = None):
        self.widget = widget
        self.disp_window = None
        self.id = None
        self.x = self.y = 0
        self.shift_x_disp = shift_x_disp
        self.shift_y_disp = shift_y_disp
        self.font = font
        self.width = width
        self.height = height

    def show_disp(self, img):
        #"Display"
        self.img = img
        if self.disp_window:
            return

        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + self.shift_x_disp #+ 57
        # print(self.shift_x_disp)
        # print(x)

        y = y + cy + self.widget.winfo_rooty() + self.shift_y_disp #+27
        # print(self.shift_y_disp)
        # print(y)

        self.disp_window = disp = tk.Toplevel(self.widget)
        disp.wm_overrideredirect(1)
        if self.width is not None and self.height is not None:
            disp.geometry("{}x{}+{}+{}".format(self.width, self.height, x, y))
            disp.attributes("-topmost", True)
        else:
            disp.wm_geometry("+%d+%d" % (x, y))
            disp.attributes("-topmost", True)

        tk_canvas = tk.Canvas(disp, bg = 'white', highlightthickness = 0)
        tk_canvas.place(relx = 0, rely= 0, relheight = 1, relwidth = 1, anchor = 'nw')

        self.display_func(tk_canvas, img, self.width, self.height)

    def hide_disp(self):
        disp = self.disp_window
        self.disp_window = None
        if disp:
            disp.destroy()

    def display_func(self, display, ref_img, w, h):
        img_PIL = Image.fromarray(ref_img)
        # print(type(img_PIL))

        img_tk = ImageTk.PhotoImage(img_PIL)
        display.create_image(w/2, h/2, image=img_tk, anchor='center', tags='img')
        display.image = img_tk

def CreatePreviewDisp(widget, imdata, shift_x_disp = 0, shift_y_disp = 0, font = 'Tahoma 10', width = None, height = None):
    previewDisp = PreviewDisp(widget, shift_x_disp, shift_y_disp, font, width, height)

    # print(type(imdata))

    if type(imdata) == str and (path.exists(imdata)) == True:
        im_np = imread(imdata)

    elif isinstance(imdata, np.ndarray) == True:
        im_np = imdata

    elif isinstance(imdata, Image.Image) == True:
        im_np = np.array(imdata)

    elif isinstance(imdata, openpyxl.drawing.image.Image) == True:
        im_pil = Image.open(io.BytesIO(imdata._data()))
        im_np = np.array(im_pil)
        del im_pil

    else:
        raise TypeError("'imdata' must be PIL-type image, numpy.array image, or str-type image path")

    img = _image_resize(im_np, width, height, inter = cv2.INTER_NEAREST)

    del im_np, imdata

    def enter(event):
        previewDisp.show_disp(img)
    def leave(event):
        previewDisp.hide_disp()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def _image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    elif width is None and height is not None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = np.divide(height, float(h))
        dim = (int( np.multiply(w, r) ), height)

    # otherwise, the height is None
    elif width is not None and height is None:
        # calculate the ratio of the width and construct the
        # dimensions
        r = np.divide(width, float(w))
        dim = (width, int(np.multiply(h, r)))

    else:
        dim = (width, height)
    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized