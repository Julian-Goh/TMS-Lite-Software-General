import tkinter as tk

class ScrolledCanvas():
    def __init__(self, master, frame_w, frame_h, canvas_x = 0, canvas_y = 0, window_bg = 'SystemButtonFace'
        , canvas_bg = 'SystemButtonFace', canvas_highlightthickness = 2, hbar_x = 0, hbar_y = 0, vbar_x = 0, vbar_y = 0):

        self.master = master
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.canvas_x = canvas_x
        self.canvas_y = canvas_y

        self.hbar_x = hbar_x
        self.hbar_y = hbar_y
        self.vbar_x = vbar_x
        self.vbar_y = vbar_y

        self.__bar_w = 18 #width of a typical scrollbar

        self.window_bg = window_bg
        self.canvas_bg = canvas_bg

        self.resize_event_w = frame_w #During init we set this equal to frame_w
        self.resize_event_h = frame_h #During init we set this equal to frame_h

        self.scrolly_lock = False
        
        self.canvas = tk.Canvas(self.master, highlightcolor = 'white', highlightthickness = canvas_highlightthickness, bg = self.canvas_bg)
        self.canvas['width'] = frame_w
        self.canvas['height'] = frame_h
        #self.canvas.place(x=self.canvas_x, y=self.canvas_y,  relheight=1, relwidth=1, anchor = 'nw')
        self.window_fr = tk.Frame(self.canvas, highlightthickness = 0, bg = self.window_bg)
        self.window_fr['width'] = frame_w
        self.window_fr['height'] = frame_h
        self.window_fr.bind('<Configure>', lambda e: self.canvas.configure(scrollregion= self.canvas.bbox("all")))

        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)

        self.window_id = self.canvas.create_window(0,0, window = self.window_fr, anchor='nw')
        #self.canvas.create_window(0,0, window = self.window_fr, anchor='nw')

        self.scrolly = tk.Scrollbar(self.master, command= self.canvas.yview)
        self.scrolly.place(relx=1, rely=0, relheight=1, x = self.vbar_x, y = self.vbar_y, anchor='ne')

        self.scrollx = tk.Scrollbar(self.master, command= self.canvas.xview, orient='horizontal')
        self.scrollx.place(relx=0, rely=1, relwidth=1, width = -self.__bar_w-self.hbar_x, x = self.hbar_x, y = self.hbar_y, anchor = 'sw')

        # self.canvas.configure(yscrollcommand= self.scrolly.set)

        self.canvas.configure(yscrollcommand= self.scrolly_handle)
        self.canvas.configure(xscrollcommand= self.scrollx_handle)

        # self.canvas.update_idletasks()
        # self.canvas.yview_moveto(0)
        # self.canvas.xview_moveto(0)

    def scrolly_handle(self, y0, y1):
        self.scrolly.set(y0, y1)

    def scrollx_handle(self, x0, x1):
        self.scrollx.set(x0, x1)

    def on_resize(self, event):
        # print('self.frame_w, self.frame_h: ', self.frame_w, self.frame_h)
        # print(event)
        # print('event.width, event.height: ', event.width, event.height)
        self.resize_event_h = int(event.height)
        self.resize_event_w = int(event.width)

        if self.frame_h <= event.height:
            self.window_fr['height'] = event.height
            self.canvas['height'] = event.height
            self.scrolly_lock = True

        elif self.frame_h > event.height:
            self.window_fr['height'] = self.frame_h
            self.canvas['height'] = self.frame_h
            self.scrolly_lock = False

        if self.frame_w <= event.width:
            self.window_fr['width'] = event.width
            self.canvas['width'] = event.width

        elif self.frame_w > event.width:
            self.window_fr['width'] = self.frame_w
            self.canvas['width'] = self.frame_w

        # print('On Resize Event')
        # print('self.scrolly_lock: ', self.scrolly_lock)
        # print('self.window_fr: ', self.window_fr['width'], self.window_fr['height'])
        # print('-------------------------------------------------')

    def invoke_resize(self):
        # print('self.frame_h, self.resize_event_h: ', self.frame_h, self.resize_event_h)
        # print('self.frame_w, self.resize_event_w: ', self.frame_w, self.resize_event_w)
        # print('Scroll Lock: ', self.scrolly_lock)

        if self.frame_h <= self.resize_event_h:
            self.window_fr['height'] = self.resize_event_h
            self.canvas['height'] = self.resize_event_h
            self.scrolly_lock = True

        elif self.frame_h > self.resize_event_h:
            self.window_fr['height'] = self.frame_h
            self.canvas['height'] = self.frame_h
            self.scrolly_lock = False

        if self.frame_w <= self.resize_event_w:
            self.window_fr['width'] = self.resize_event_w
            self.canvas['width'] = self.resize_event_w

        elif self.frame_w > self.resize_event_w:
            self.window_fr['width'] = self.frame_w
            self.canvas['width'] = self.frame_w

        # print('Invoke...')
        # self.canvas.update()
        # self.window_fr.update()
        # print(self.window_fr['width'], self.canvas['width'])

    def _bound_to_mousewheel(self,event):
        # print('Enter')
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        #print('Leave')
        # self.canvas.unbind_all("<MouseWheel>")
        self.canvas.bind_all("<MouseWheel>", self.dummy_callback)

    def dummy_callback(self, event = None):
        pass

    def _on_mousewheel(self, event):
        if self.scrolly_lock == False:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            # print(event.delta)
            
    def forget_all_func(self):
        # self.canvas.unbind_all("<MouseWheel>") 
        self.canvas.place_forget()
        self.scrolly.place_forget()
        self.scrollx.place_forget()

    def rmb_all_func(self, scroll_x = True, scroll_y = True):
        # self._bound_to_mousewheel(event=None)
        # self.canvas.place(x=self.canvas_x, y=self.canvas_y,  relheight=1, relwidth=1, anchor = 'nw'
        #     , width = -self.canvas_x, height = -self.canvas_y)

        # print((type(scroll_x) == bool and type(scroll_y)==bool))
        if (type(scroll_x) == bool and type(scroll_y)==bool):
            if scroll_x == True and scroll_y == True:
                self.scrollx.place(relx=0, rely=1, relwidth=1, width = -self.__bar_w-self.hbar_x, x = self.hbar_x, y = self.hbar_y, anchor = 'sw')
                self.scrolly.place(relx=1, rely=0, relheight=1, x = self.vbar_x, y = self.vbar_y, anchor='ne')
                self.canvas.place(x=self.canvas_x, y=self.canvas_y,  relheight=1, relwidth=1, anchor = 'nw'
                    , width = -self.__bar_w-self.canvas_x, height = -self.__bar_w-self.canvas_y)

            elif scroll_x == True and scroll_y == False:
                self.scrollx.place(relx=0, rely=1, relwidth=1, width = -self.hbar_x, x = self.hbar_x, y = self.hbar_y, anchor = 'sw')
                self.scrolly.place_forget()
                self.canvas.place(x=self.canvas_x, y=self.canvas_y,  relheight=1, relwidth=1, anchor = 'nw'
                    , width = -self.canvas_x, height = -self.__bar_w-self.canvas_y)

            elif scroll_x == False and scroll_y == True:
                self.scrollx.place_forget()
                self.scrolly.place(relx=1, rely=0, relheight=1, x = self.vbar_x, y = self.vbar_y, anchor='ne')
                self.canvas.place(x=self.canvas_x, y=self.canvas_y,  relheight=1, relwidth=1, anchor = 'nw'
                    , width = -self.__bar_w-self.canvas_x, height = -self.canvas_y)

            elif scroll_x == False and scroll_y == False:
                self.scrollx.place_forget()
                self.scrolly.place_forget()
                self.canvas.place(x=self.canvas_x, y=self.canvas_y,  relheight=1, relwidth=1, anchor = 'nw'
                    , width = -self.canvas_x, height = -self.canvas_y)

        elif not(type(scroll_x) == bool and type(scroll_y)==bool):
            raise Exception("scroll_x and scroll_y parameter(s) has/have to be a type-bool.")

        # print('self.frame_h, self.resize_event_h: ', self.frame_h, self.resize_event_h)
        # print('self.frame_w, self.resize_event_w: ', self.frame_w, self.resize_event_w)

    def resize_frame(self, width = None, height = None):
        frame_1 = self.canvas #self.window_fr
        frame_2 = self.window_fr
        if height is not None:
            try:
                height = int(height)
                self.frame_h = height
                frame_1['height'] = height
                frame_2['height'] = height

            except Exception:
                height = None

        if width is not None:
            try:
                width = int(width)
                self.frame_w = width
                frame_1['width'] = width
                frame_2['width'] = width
                
            except Exception:
                width = None

        if height is None and width is None:
            raise ValueError("User must provide 'width' or 'height' value, and those values must be a positive non-zero integer.")

        # self.scrolly_lock_check()
        self.invoke_resize()
        # print('RESIZE self.frame_w, self.frame_h: ', self.frame_w, self.frame_h)

    def get_frame_size(self):
        return self.frame_w, self.frame_h

    def scrolly_lock_check(self):
        if  self.frame_h <= self.resize_event_h: 
            self.scrolly_lock = True
        elif self.frame_h > self.resize_event_h:
            self.scrolly_lock = False

    def scroll_reset(self):
        self.canvas.yview_moveto(0)
        self.canvas.xview_moveto(0)