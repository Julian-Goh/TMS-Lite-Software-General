from .LC_GUI_Lib import LC18_SQ
from .LC_GUI_Lib import LC18_16CH
from .LC_GUI_Lib import LC18_4CH
from .LC_GUI_Lib import LC18_OD
from .LC_GUI_Lib import LC18_KP
from .LC_GUI_Lib import LC18_RGBW
from .LC_GUI_Lib import LC18_1CH
from .LC_GUI_Lib import LC18_2CH

from .LC_GUI_Lib import LC20_SQ


import os
from os import path
import clr
import sys

curr_dir     = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curr_dir)

clr.AddReference("LC18Library")
import LC18Library

clr.AddReference("LC20Library")
import LC20Library
