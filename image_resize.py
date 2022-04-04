import PIL
from PIL import ImageTk, Image
import numpy as np
import cv2

import os
from os import path

import pathlib

def type_int(arg):
    if (type(arg)) == int or (isinstance(arg, np.integer) == True):
        return True
    else:
        return False

def type_float(arg):
    if (type(arg)) == float or (isinstance(arg, np.float) == True):
        return True
    else:
        return False

def img_resize_dim(ori_W, ori_H, new_W = None, new_H = None):
    if new_W is not None and new_H is None:
        return (new_W , np.multiply(np.divide(ori_H, ori_W), new_W))

    elif new_W is None and new_H is not None:
        return (np.multiply(np.divide(ori_W,ori_H), new_H), new_H)

    elif new_W is not None and new_H is not None:
        return (new_W , new_H)

    elif new_W is None and new_H is None:
        return (None, None)

def opencv_img_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    # print(image)
    (h, w) = image.shape[:2]
    # print(width, height)
    # if both the width and height are None, then return the
    # original image
    if type_int(width) == False and type_int(height) == False:
        return image

    elif type_int(width) == True and type_int(height) == False:
        dim = img_resize_dim(w, h, new_W = width)
        int_dim = (int(dim[0]), int(dim[1]))
        # resize the image
        resized = cv2.resize(image, int_dim, interpolation = inter)

        # return the resized image
        return resized

    elif type_int(width) == False and type_int(height) == True:
        dim = img_resize_dim(w, h, new_H = height)
        int_dim = (int(dim[0]), int(dim[1]))
        # resize the image
        resized = cv2.resize(image, int_dim, interpolation = inter)

        # return the resized image
        return resized

    elif type_int(width) == True and type_int(height) == True:
        dim = (width, height)
        int_dim = (int(dim[0]), int(dim[1]))
        # resize the image
        resized = cv2.resize(image, int_dim, interpolation = inter)

        # return the resized image
        return resized

def pil_img_resize(pil_img, img_scale = None, img_width = None, img_height = None
    , pil_filter = Image.BILINEAR):
    ### img_scale is given priority, if img_scale fits the if-else condition
    if (True == type_int(img_scale)) or (True == type_float(img_scale)):
        resize_w = round( np.multiply(pil_img.size[0], img_scale) )
        resize_h = round( np.multiply(pil_img.size[1], img_scale) )

        # print('img_scale: ', img_file, resize_w, resize_h)

        resize_img = pil_img.resize((resize_w, resize_h), pil_filter)
        return resize_img

    else:
        new_w_bool = (True == type_int(img_width) or True == type_float(img_width))
        new_h_bool = (True == type_int(img_height) or True == type_float(img_height))

        # print(img_file, new_w_bool, new_h_bool)
        if new_w_bool == True and new_h_bool == False:
            resize_w, resize_h = img_resize_dim(pil_img.width, pil_img.height, new_W = img_width)

            resize_img = pil_img.resize((int(resize_w), int(resize_h)), pil_filter)
            return resize_img

        elif new_w_bool == False and new_h_bool == True:
            resize_w, resize_h = img_resize_dim(pil_img.width, pil_img.height, new_H = img_height)
            
            resize_img = pil_img.resize((int(resize_w), int(resize_h)), pil_filter)
            return resize_img

        elif new_w_bool == True and new_h_bool == True:
            resize_w, resize_h = (img_width, img_height)
            
            resize_img = pil_img.resize((int(resize_w), int(resize_h)), pil_filter)
            return resize_img

        else:
            return pil_img


def pil_icon_resize(img_PATH, img_folder, img_file, img_scale = None, img_width = None, img_height = None
	, pil_filter = Image.BILINEAR, RGBA_format = False):
    # pil_filter, Image.: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
    img = Image.open(img_PATH + "\\" + img_folder + "\\" + img_file)
    if RGBA_format == True:
        try:
            img = img.convert("RGBA")
        except Exception:
            pass
    #print(img_file, img.mode)
    
    ### img_scale is given priority, if img_scale fits the if-else condition
    if (True == type_int(img_scale)) or (True == type_float(img_scale)):
        resize_w = round( np.multiply(img.size[0], img_scale) )
        resize_h = round( np.multiply(img.size[1], img_scale) )

        # print('img_scale: ', img_file, resize_w, resize_h)

        resize_img = img.resize((resize_w, resize_h), pil_filter)

        icon_tk = ImageTk.PhotoImage(resize_img)
        return icon_tk, img

    else:
        new_w_bool = (True == type_int(img_width) or True == type_float(img_width))
        new_h_bool = (True == type_int(img_height) or True == type_float(img_height))

        # print(img_file, new_w_bool, new_h_bool)
        if new_w_bool == True and new_h_bool == False:
            resize_w, resize_h = img_resize_dim(img.width, img.height, new_W = img_width)

            resize_img = img.resize((int(resize_w), int(resize_h)), pil_filter)
            icon_tk = ImageTk.PhotoImage(resize_img)
            return icon_tk, img

        elif new_w_bool == False and new_h_bool == True:
            resize_w, resize_h = img_resize_dim(img.width, img.height, new_H = img_height)
            
            resize_img = img.resize((int(resize_w), int(resize_h)), pil_filter)
            icon_tk = ImageTk.PhotoImage(resize_img)
            return icon_tk, img

        elif new_w_bool == True and new_h_bool == True:
            resize_w, resize_h = (img_width, img_height)
            
            resize_img = img.resize((int(resize_w), int(resize_h)), pil_filter)
            icon_tk = ImageTk.PhotoImage(resize_img)
            return icon_tk, img

        else:
            return None, img
        