import tkinter as tk
from PIL import ImageTk, Image
from misc_module.image_resize import *

def to_tk_img(pil_img):
    if isinstance(pil_img, Image.Image):
        return ImageTk.PhotoImage(pil_img)
    else:
        return None

def tk_img_insert(widget, pil_img, *resize_args, **resize_kwargs):
    """ pil_img_resize(pil_img, img_scale = None, img_width = None, img_height = None, pil_filter = Image.BILINEAR)
        # pil_filter, Image.: NEAREST, BILINEAR, BICUBIC and ANTIALIAS
    """
    if isinstance(pil_img, Image.Image):
        tk_img = to_tk_img( pil_img_resize(pil_img, *resize_args, **resize_kwargs) )
        widget['image'] = tk_img
        widget.Image = tk_img
        return tk_img
    else:
        return None
        