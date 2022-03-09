import tkinter as tk
# from custom_error_msgbox import Error_Msgbox
# from custom_warning_msgbox import Warning_Msgbox
# from custom_ask_msgbox import Ask_Msgbox
# from custom_info_msgbox import Info_Msgbox
from custom_msgbox import Ask_Msgbox, Info_Msgbox, Error_Msgbox, Warning_Msgbox

if __name__ == '__main__':
    class Root_Window(tk.Tk):
        def __init__(self,*args,**kw):
            tk.Tk.__init__(self,*args,**kw)
            self.withdraw() #hide the window
            self.after(0,self.deiconify) #as soon as possible (after app starts) show again

    main_window = tk.Tk()
    main_window.title('Main.exe')
    main_window.resizable(True, True)
    main_window_width = 890 #1080 #1280 #1080 #760       #890
    main_window_height = 600 #640 #720 #640 #720 #600    #600
    main_window.minsize(width=890, height=600)

    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()

    x_coordinate = int((screen_width/2) - (main_window_width/2))
    y_coordinate = int((screen_height/2) - (main_window_height/2))

    main_window.geometry("{}x{}+{}+{}".format(main_window_width, main_window_height, x_coordinate, y_coordinate))

    def close_window():
        ask_msgbox = Ask_Msgbox('Do you want to quit?', parent = main_window, title = 'Quit')
        main_window.wait_window(ask_msgbox)
        if ask_msgbox.ask_result() == True:
            main_window.destroy()
        else:
            pass

    main_window.protocol("WM_DELETE_WINDOW", close_window)

    tk.Button(main_window, relief = tk.GROOVE, width = 12, text = 'Press Me~').place(relx = 0.5, rely= 0.5, anchor = 'c')

    # Error_Msgbox('Memory Usage reached 80%! Stopping Video Recording...'
    #             + '\n\n' + 'Options for Longer Video Recording: '
    #             + '\n' + 'a) Try reducing Video Resolution in the Video Setting.'
    #             + '\n' + 'b) Set Camera to Monochrome Mode.'
    #             + '\n' + 'c) Reduce Camera Framerate.', parent = main_window, width = 400, height = 200)

    # Error_Msgbox('Error Box 2', parent = main_window, width = 400, height = 200)
    # Info_Msgbox('Hello World. You are viewing my Info Msgbox.', parent = main_window, message_anchor = 'w')

    Warning_Msgbox('Memory Usage reached 80%! Stopping Video Recording...'
                + '\n\n' + 'Options for Longer Video Recording: '
                + '\n' + 'a) Try reducing Video Resolution in the Video Setting.'
                + '\n' + 'b) Set Camera to Monochrome Mode.'
                + '\n' + 'c) Reduce Camera Framerate.', parent = main_window, width = 400, height = 200)

    main_window.mainloop()
    
