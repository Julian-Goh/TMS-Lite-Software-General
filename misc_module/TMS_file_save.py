import os
from os import path

import cv2
import re
import numpy as np

from PIL import Image

def cv_img_save(folder, img_arr, img_name, img_format, kw_str = '', overwrite = False):
    index = 0

    if overwrite == False:
        if (isinstance(kw_str, str) == True) and len(kw_str) > 0:
            new_img_name = re.sub('-(\\'+ kw_str + '\\)' + '(--id)(\\d)' + '$', '', img_name)
            # new_img_name = re.sub('\\s{2,}', ' ', new_img_name) # Replace all double spaces with single spaces
            new_img_name = re.sub('\\s+$', '', new_img_name) #Remove trailing spaces
            loop = True
            while loop == True:
                img_path = folder + '\\'+ new_img_name + '-' + kw_str + '--id{}'.format(index) + img_format
                if (path.exists(img_path)) == True:
                    index = index + 1
                elif (path.exists(img_path)) == False:
                    loop = False

        else:
            loop = True
            while loop == True:
                img_path = folder + '\\'+ img_name + '--id{}'.format(index) + img_format
                if (path.exists(img_path)) == True:
                    index = index + 1
                elif (path.exists(img_path)) == False:
                    loop = False

    else:
        img_path = folder + '\\'+ img_name + img_format

    # print(img_path)
    if len(img_arr.shape) == 3:
        img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
    cv2.imwrite(img_path, img_arr)

    return img_path, index

def pil_img_save(folder, img_pil, img_name, img_format, kw_str = '', overwrite = False):
    index = 0

    if overwrite == False:
        if (isinstance(kw_str, str) == True) and len(kw_str) > 0:
            new_img_name = re.sub('-(\\'+ kw_str + '\\)' + '(--id)(\\d)' + '$', '', img_name)
            # new_img_name = re.sub('\\s{2,}', ' ', new_img_name) # Replace all double spaces with single spaces
            new_img_name = re.sub('\\s+$', '', new_img_name)
            loop = True
            while loop == True:
                img_path = folder + '\\'+ new_img_name + '-' + kw_str + '--id{}'.format(index) + img_format
                if (path.exists(img_path)) == True:
                    index = index + 1
                elif (path.exists(img_path)) == False:
                    loop = False

        else:
            loop = True
            while loop == True:
                img_path = folder + '\\'+ img_name + '--id{}'.format(index) + img_format
                if (path.exists(img_path)) == True:
                    index = index + 1
                elif (path.exists(img_path)) == False:
                    loop = False

    else:
        img_path = folder + '\\'+ img_name + img_format

    img_arr = np.array(img_pil)
    if len(img_arr.shape) == 3:
        img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
    cv2.imwrite(img_path, img_arr)

    return img_path, index
    
def PDF_img_save(folder, img_arr, pdf_name, ch_split_bool = True, kw_str = '', overwrite = False):
    index = 0
    if overwrite == False:
        if (isinstance(kw_str, str) == True) and len(kw_str) > 0:
            new_pdf_name = re.sub('-(\\'+ kw_str + '\\)' + '--(id)(\\d)' + '$', '', pdf_name)
            new_pdf_name = re.sub('\\s+$', '', new_pdf_name)
            loop = True
            while loop == True:
                pdf_path = folder + '\\'+ new_pdf_name + '-' + kw_str + '--id{}'.format(index) + ".PDF"
                if (path.exists(pdf_path)) == True:
                    index = index + 1
                elif (path.exists(pdf_path)) == False:
                    loop = False

        else:
            loop = True
            while loop == True:
                pdf_path = folder + '\\'+ pdf_name + '--id{}'.format(index) + ".PDF"
                if (path.exists(pdf_path)) == True:
                    index = index + 1
                elif (path.exists(pdf_path)) == False:
                    loop = False
    
    else:
        pdf_path = folder + '\\'+ pdf_name + ".PDF"

    pdf_img = np_to_PIL(img_arr)
    if len(img_arr.shape) == 3:
        if ch_split_bool == True:
            pdf_img_R = Image.fromarray(img_arr[:,:,0])
            pdf_img_G = Image.fromarray(img_arr[:,:,1])
            pdf_img_B = Image.fromarray(img_arr[:,:,2])
            pdf_img_list = [pdf_img, pdf_img_R, pdf_img_G, pdf_img_B]

        elif ch_split_bool == False:
            pdf_img_list = [pdf_img]
    else:
        pdf_img_list = [pdf_img]

    pdf_img_list[0].save(pdf_path, save_all=True, append_images= pdf_img_list[1:])

    return pdf_path, index

def PDF_img_list_save(folder, pdf_img_list, pdf_name):
    index = 0
    loop = True
    while loop == True:
        pdf_path = folder + '\\'+ pdf_name + '--id{}'.format(index) + ".PDF"
        if (path.exists(pdf_path)) == True:
            index = index + 1
        elif (path.exists(pdf_path)) == False:
            loop = False

    pdf_img_list[0].save(pdf_path, save_all=True, append_images= pdf_img_list[1:])

def np_to_PIL(img_arr):
    img_PIL = Image.fromarray(img_arr)

    return img_PIL