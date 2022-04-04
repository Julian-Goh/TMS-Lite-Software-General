"""
Contains a SheetImageLoader class that allow you to loadimages from a sheet
"""
import io
import string
import operator
from PIL import Image

from openpyxl.utils.cell import get_column_letter
from collections import OrderedDict

import numpy as np


custom_col_char_dict = {}
curr_char = 'A'
for i in range(0, 26):
    custom_col_char_dict[curr_char] = i + 1
    curr_char = chr(ord(curr_char) + 1)

del curr_char

def xl_col_label_num(char):
    col_num = None
    try:
        if len(char) == 1:
            col_num = custom_col_char_dict[char]

        elif 1 < len(char) <= 3:
            col_num = 0
            for order, c in enumerate(char[::-1]):
                # print(c)
                col_num = col_num + np.multiply(custom_col_char_dict[c], np.power(26, order))

        else:
            raise KeyError

        return int(col_num)

    except KeyError:
        # print('KeyError')
        col_num = None
        return col_num

def xl_col_label_char(num):
    col_char = None
    if (type(num) == int or isinstance(num, np.integer) == True):
        if num > 0:
            char_list = []
            while num > 0:
                num, remainder = divmod(num, 26)
                # check for exact division and borrow if needed
                if remainder == 0:
                    remainder = 26
                    num -= 1

                char_list.append(chr(remainder+64))

            col_char = ''.join(reversed(char_list))

        else:
            raise ValueError("'num' argument must be a non-zero positive int-type data")

    else:
        raise ValueError("'num' argument must be a non-zero positive int-type data")

    return col_char

class SheetImageLoader():
    """Loads all images in a sheet"""
    # _images = {} #Bad method of initializing a variable. Will cause previous data from previous sheet to carry over if SheetImageLoader class is used more than once. 
    def __init__(self, sheet, sort_col_bool = False, sort_row_bool = False):
        """Loads all sheet images"""
        if type(sort_col_bool) != bool or type(sort_row_bool) != bool:
            raise ValueError("both 'sort_col_bool' and 'sort_row_bool' must be bool-type(s), respectively.")

        sheet_images = sheet._images
        sort_bool = operator.xor(sort_col_bool, sort_row_bool)

        if sort_bool == True:
            __temp = {}
            __sort_row_id = {}
            __sort_col_id = {}

            for image in sheet_images:
                row = image.anchor._from.row + 1
                # print('image.anchor._from.col: ', image.anchor._from.col)
                col = xl_col_label_char(image.anchor._from.col + 1)
                __temp[f'{col}{row}'] = image
                __sort_col_id[f'{col}{row}'] = image.anchor._from.col + 1
                __sort_row_id[f'{col}{row}'] = image.anchor._from.row + 1

            __sort_col_id = {k: v for k, v in sorted(__sort_col_id.items(), key=lambda item: item[1])}
            __sort_row_id = {k: v for k, v in sorted(__sort_row_id.items(), key=lambda item: item[1])}
            
            # print(__sort_col_id)
            # print(__sort_row_id)
            if sort_col_bool == True and sort_row_bool == False:
                self._images = OrderedDict(sorted(__temp.items(),       key = lambda row_id:__sort_row_id[row_id[0]]))
                self._images = OrderedDict(sorted(self._images.items(), key = lambda col_id:__sort_col_id[col_id[0]]))

            elif sort_col_bool == False and sort_row_bool == True:
                self._images = OrderedDict(sorted(__temp.items(),       key = lambda col_id:__sort_col_id[col_id[0]]))
                self._images = OrderedDict(sorted(self._images.items(), key = lambda row_id:__sort_row_id[row_id[0]]))

            # print(list(self._images.keys()))

            del sheet_images, __sort_col_id, __sort_row_id, __temp

        else:
            if sort_col_bool == True and sort_row_bool == True:
                raise Exception("Cannot perform sorting. Both 'sort_col_bool' and 'sort_row_bool' CANNOT be True at a time.")

            self._images = {}
            for image in sheet_images:
                # print(image.anchor._from.row, image.anchor._from.col)
                # print(dir(image))
                # print(dir(image.anchor))
                # print(image.ref)
                # print(image.format)
                # print(image.width, image.height)
                row = image.anchor._from.row + 1
                col = xl_col_label_char(image.anchor._from.col + 1)

                self._images[f'{col}{row}'] = image

            del sheet_images

    def image_in(self, cell):
        """Checks if there's an image in specified cell"""
        exist_bool = cell in self._images
        imobj = None
        imsize = None

        if exist_bool == True:
            imobj = self._images[cell]
            imsize = (imobj.width, imobj.height)

        elif exist_bool == False:
            imobj = None
            imsize = None

        return exist_bool, imsize, imobj

    def get(self, cell):
        """Retrieves image data from a cell"""
        if cell not in self._images:
            raise ValueError("Cell {} doesn't contain an image".format(cell))
        else:
            __imdata = self._images[cell]._data
            image = io.BytesIO(__imdata())
            return Image.open(image)