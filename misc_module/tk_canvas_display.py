import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from misc_module.image_resize import img_resize_dim, opencv_img_resize, pil_img_resize, open_pil_img
import cv2

def display_func(display, ref_img, tag, resize_status = True, interpolation = cv2.INTER_LINEAR, force_update = False):
    if isinstance(display, tk.Canvas):
        display.update_idletasks()
        if display.winfo_ismapped() == False and force_update == True:
            display.update()

        if display.winfo_ismapped() == True:
            disp_width = display.winfo_width()
            disp_height = display.winfo_height()
            disp_aspect = np.divide(disp_width, disp_height)
            # print(disp_width, disp_height, disp_aspect)

            imheight, imwidth = ref_img.shape[:2]
            img_aspect = np.divide(imwidth, imheight)
            # print(imwidth, imheight, img_aspect)

            if resize_status == True:
                if img_aspect > disp_aspect:
                    img_resize = opencv_img_resize(ref_img, width = min(disp_width, disp_height), inter = interpolation)

                elif img_aspect < disp_aspect:
                    img_resize = opencv_img_resize(ref_img, height = min(disp_width, disp_height), inter = interpolation)

                else:
                    img_resize = opencv_img_resize(ref_img, width = disp_width, height = disp_height, inter = interpolation)

                img_PIL = Image.fromarray(img_resize)
            
            else:
                img_PIL = Image.fromarray(ref_img)

            img_tk = ImageTk.PhotoImage(img_PIL)
            img_tuple = display.find_withtag(tag)
            if len(img_tuple) == 1:
                display.itemconfig(img_tuple[0], image = img_tk)
                display.coords(img_tuple[0], disp_width/2, disp_height/2)
                display.image = img_tk

            elif len(img_tuple) == 0:
                display.create_image(disp_width/2, disp_height/2, image=img_tk, anchor='center', tags=tag)
                display.image = img_tk
            else:
                display.delete("all")
                display.create_image(disp_width/2, disp_height/2, image=img_tk, anchor='center', tags=tag)
                display.image = img_tk

def clear_display_func(*canvas_widgets):
    for widget in canvas_widgets:
        widget.delete('all')
        