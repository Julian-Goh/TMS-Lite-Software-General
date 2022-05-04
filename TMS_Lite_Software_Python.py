import os
from os import path
import sys

import ctypes

import tkinter as tk

from PIL import ImageTk, Image

from main_GUI import main_GUI

from misc_module.os_create_folder import create_save_folder

class Root_Window(tk.Tk):
    def __init__(self,*args,**kw):
        tk.Tk.__init__(self,*args,**kw)
        self.withdraw() #hide the window
        self.after(0,self.deiconify) #as soon as possible (after app starts) show again


if __name__ == '__main__':
    # # Query DPI Awareness (Windows 10 and 8)
    # awareness = ctypes.c_int()
    # errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
    # print(awareness.value)

    # # Set DPI Awareness  (Windows 10 and 8)
    # errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(0)
    # # the argument is the awareness level, which can be 0, 1 or 2:
    # # for 1-to-1 pixel control I seem to need it to be non-zero (I'm using level 2)

    # # Set DPI Awareness  (Windows 7 and Vista)
    # success = ctypes.windll.user32.SetProcessDPIAware()
    # # behaviour on later OSes is undefined, although when I run it on my Windows 10 machine, it seems to work with effects identical to SetProcessDpiAwareness(1)
    '''
    # typedef enum _PROCESS_DPI_AWARENESS { 
    # PROCESS_DPI_UNAWARE = 0,
    # /*  DPI unaware. This app does not scale for DPI changes and is
    #     always assumed to have a scale factor of 100% (96 DPI). It
    #     will be automatically scaled by the system on any other DPI
    #     setting. */

    # PROCESS_SYSTEM_DPI_AWARE = 1,
    # /*  System DPI aware. This app does not scale for DPI changes.
    #     It will query for the DPI once and use that value for the
    #     lifetime of the app. If the DPI changes, the app will not
    #     adjust to the new DPI value. It will be automatically scaled
    #     up or down by the system when the DPI changes from the system
    #     value. */

    # PROCESS_PER_MONITOR_DPI_AWARE = 2
    # /*  Per monitor DPI aware. This app checks for the DPI when it is
    #     created and adjusts the scale factor whenever the DPI changes.
    #     These applications are not automatically scaled by the system. */
    # } PROCESS_DPI_AWARENESS;
    '''

    tk_root = Root_Window()
    tk_root.title('TMS-Lite-Software-General.exe')

    tk_root.resizable(True, True)
    window_icon = ImageTk.PhotoImage(file = os.getcwd() + '\\TMS Icon\\' + 'logo4.ico')
    tk_root_width = 890
    tk_root_height = 600
    tk_root.minsize(width=890, height=600)

    screen_width = tk_root.winfo_screenwidth()
    screen_height = tk_root.winfo_screenheight()

    x_coordinate = int((screen_width/2) - (tk_root_width/2))
    y_coordinate = int((screen_height/2) - (tk_root_height/2))

    tk_root.geometry("{}x{}+{}+{}".format(tk_root_width, tk_root_height, x_coordinate, y_coordinate))
    tk_root.iconphoto(False, window_icon)

    img_save_dir    = os.path.join(os.environ['USERPROFILE'],  "TMS_Saved_Images")
    report_save_dir = os.path.join(os.environ['USERPROFILE'], "TMS_Saved_Reports")
    create_save_folder(folder_dir = img_save_dir)
    create_save_folder(folder_dir = report_save_dir)

    tk_main_gui = main_GUI(master = tk_root, window_icon = window_icon)

    tk_root.protocol("WM_DELETE_WINDOW", tk_main_gui.close_all)
    tk_root.mainloop()
