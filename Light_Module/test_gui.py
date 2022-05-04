import os
from os import path
import sys
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

from LC_GUI_Lib.LC18_SQ    import LC18_SQ_GUI
from LC_GUI_Lib.LC18_16CH  import LC18_16CH_GUI
from LC_GUI_Lib.LC18_4CH   import LC18_4CH_GUI
from LC_GUI_Lib.LC18_OD    import LC18_OD_GUI
from LC_GUI_Lib.LC18_KP    import LC18_KP_GUI
from LC_GUI_Lib.LC18_RGBW  import LC18_RGBW_GUI
from LC_GUI_Lib.LC18_1CH   import LC18_1CH_GUI
from LC_GUI_Lib.LC18_2CH   import LC18_2CH_GUI

from LC_GUI_Lib.LC20_SQ    import LC20_SQ_GUI

import clr

crnt_dir    = os.path.dirname(os.path.abspath(__file__))
master_dir  = os.path.dirname(crnt_dir)

if crnt_dir not in sys.path:
    sys.path.append(crnt_dir)

if master_dir not in sys.path:
    sys.path.append(master_dir)

clr.AddReference("LC18Library")
import LC18Library

clr.AddReference("LC20Library")
import LC20Library

from Tk_Custom_Widget.ScrolledCanvas import ScrolledCanvas

class Root_Window(tk.Tk):
    def __init__(self,*args,**kw):
        tk.Tk.__init__(self,*args,**kw)
        self.withdraw() #hide the window
        self.after(0,self.deiconify) #as soon as possible (after app starts) show again
        
if __name__ == '__main__':
    tk_root = Root_Window()
    tk_root_width = 890
    tk_root_height = 600
    tk_root.resizable(True, True)
    tk_root.minsize(width=890, height=600)

    screen_width = tk_root.winfo_screenwidth()
    screen_height = tk_root.winfo_screenheight()

    x_coordinate = int((screen_width/2) - (tk_root_width/2))
    y_coordinate = int((screen_height/2) - (tk_root_height/2))

    tk_root.geometry("{}x{}+{}+{}".format(tk_root_width, tk_root_height, x_coordinate, y_coordinate))

    light_main_fr = ScrolledCanvas(master = tk_root, frame_w = 1150, frame_h = 980, 
            canvas_x = 0, canvas_y = 0, bg = 'white'
            , hbar_x = 0)
    light_main_fr.show()

    # light_interface = LC18_16CH_GUI(light_main_fr.window_fr, light_main_fr, None
    #     , bg = 'white')

    # light_interface = LC18_RGBW_GUI(light_main_fr.window_fr, light_main_fr, None
    #     , bg = 'white')

    # light_interface = LC18_OD_GUI(light_main_fr.window_fr, light_main_fr, None
    #     , bg = 'white')

    # light_interface = LC18_KP_GUI(light_main_fr.window_fr, light_main_fr, None
    #     , bg = 'white')

    # light_main_fr.resize_frame(width = 1150, height = 580)
    # light_interface = LC18_2CH_GUI(light_main_fr.window_fr, light_main_fr, None
    #     , bg = 'white')

    
    light_interface = LC18_SQ_GUI(light_main_fr.window_fr, light_main_fr, None
        , bg = 'white')

    # light_interface = LC20_SQ_GUI(light_main_fr.window_fr, light_main_fr, None
        # , bg = 'white')


    light_interface.place(x=0, y=0, anchor = 'nw', relwidth = 1, relheight = 1)
    # light_interface.grid(column = 0, row = 0, columnspan = 1, rowspan = 1, sticky = 'nw')

    tk_root.mainloop()