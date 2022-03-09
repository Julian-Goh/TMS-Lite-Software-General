import tkinter as tk

class WrappingLabel(tk.Label):
    '''a type of Label that automatically adjusts the wrap to the size'''
    def __init__(self, master, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))

class ToolTip(object):
    def __init__(self, widget, shift_x_disp = 0, shift_y_disp = 0, font = 'Tahoma 10', width = None, height = None, autofit = True):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.shift_x_disp = shift_x_disp
        self.shift_y_disp = shift_y_disp
        self.font = font
        
        self.width = width
        self.height = height

        self.autofit = autofit

        self.__pixel = tk.PhotoImage(width=1, height=1)

        if self.autofit == False and (self.width is None or self.height is None):
            raise Exception("If 'autofit' argument is set to False, please provide values for 'width' AND 'height' arguments, respectively!")

    def showtip(self, text):
        #"Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + self.shift_x_disp #+ 57
        # print(self.shift_x_disp)
        # print(x)

        y = y + cy + self.widget.winfo_rooty() + self.shift_y_disp #+27
        # print(self.shift_y_disp)
        # print(y)

        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.withdraw()

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font = self.font,
                      image = self.__pixel, compound = 'c')#font=("tahoma", "8", "normal"))

        label.image = self.__pixel
        label['anchor'] = 'nw'

        if self.autofit == True:
            label.place(relx = 0, rely= 0)
            label.update_idletasks()
            actual_lbl_width = label.winfo_width()
            label['width'] = actual_lbl_width
            label.update_idletasks()
            # print(label.winfo_width(), label.winfo_height())
            tw['width'] = label.winfo_width()

            tw.geometry("{}x{}+{}+{}".format(label.winfo_width(), label.winfo_height(), x, y))
            tw.deiconify()
            tw.attributes("-topmost", True)

        else:
            if self.width is not None and self.height is not None:
                label['width'] = self.width
                label['height'] = self.height
                label.place(relx = 0, rely= 0)
                tw['width'] = self.width
                tw['height'] = self.height

                tw.geometry("{}x{}+{}+{}".format(self.width, self.height, x, y))
                tw.deiconify()
                tw.attributes("-topmost", True)


    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text, shift_x_disp = 0, shift_y_disp = 0, font = 'Tahoma 10', width = None, height = None, autofit = True):
    toolTip = ToolTip(widget, shift_x_disp, shift_y_disp, font, width, height, autofit = autofit)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)