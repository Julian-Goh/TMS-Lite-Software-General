import tkinter as tk

class CustomSingleText(tk.Text):
    def __init__(self, parent, *args, **kwargs):
        try:
            self._textvariable = kwargs.pop("textvariable")
        except KeyError:
            self._textvariable = None

        tk.Text.__init__(self, parent, *args, **kwargs)
        self['height'] = 1
        self['wrap'] = tk.NONE
        self['undo'] = True
        self['autoseparators'] = True
        self['maxundo'] = -1

        self.bind("<Return>", self.dummy_bind)
        self.bind("<Control-i>", self.dummy_bind)
        self.bind("<Tab>", self.focus_next_widget)
        self.bind("<Shift-Tab>", self.focus_previous_widget)

        # if the variable has data in it, use it to initialize
        # the widget
        if self._textvariable is not None:
            self.insert("1.0", self._textvariable.get())
            
        # this defines an internal proxy which generates a
        # virtual event whenever text is inserted or deleted
        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # if the contents changed, generate an event we can bind to
                if {([lindex $args 0] in {insert replace delete})} {
                    event generate $widget <<Change>> -when tail
                }
                # return the result from the real widget command
                return $result
            }
            ''')

        # this replaces the underlying widget with the proxy
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))

        # set up a binding to update the variable whenever
        # the widget changes
        self.bind("<<Change>>", self._on_widget_change)

        # set up a trace to update the text widget when the
        # variable changes
        if self._textvariable is not None:
            self._textvariable.trace("wu", self._on_var_change)

    def _on_var_change(self, *args):
        '''Change the text widget when the associated textvariable changes'''

        # only change the widget if something actually
        # changed, otherwise we'll get into an endless
        # loop
        text_current = self.get("1.0", "end-1c")
        var_current = self._textvariable.get()
        if text_current != var_current:
            self.delete("1.0", "end")
            self.insert("1.0", var_current)

    def _on_widget_change(self, event=None):
        '''Change the variable when the widget changes'''
        if self._textvariable is not None:
            self._textvariable.set(self.get("1.0", "end-1c"))

    def dummy_bind(self, event):
        return "break"

    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def focus_previous_widget(self, event):
        event.widget.tk_focusPrev().focus()
        return "break"
    
    def get_text(self):
        return self.get('1.0', 'end-1c')

    def set_text(self, text_str, reset_undo_stack = False):
        curr_state = str(self['state'])
        if curr_state == 'disabled':
            self['state'] = 'normal'

        self.delete("1.0", "end")
        self.insert("1.0", text_str)

        self['state'] = curr_state

        if self._textvariable is not None:
            self._textvariable.set(self.get("1.0", "end-1c")) 

        if reset_undo_stack == True:
            self.edit_reset()