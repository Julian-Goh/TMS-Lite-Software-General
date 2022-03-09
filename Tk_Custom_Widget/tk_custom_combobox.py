import tkinter as tk
from tkinter import ttk

class CustomBox(ttk.Combobox):
    def __init__(self, *args, **kwargs):
        #   initialisation of the combobox entry
        super().__init__(*args, **kwargs)
        #   "initialisation" of the combobox popdown
        self._handle_popdown_font()

    def _handle_popdown_font(self):
        """ Handle popdown font
        Note: https://github.com/nomad-software/tcltk/blob/master/dist/library/ttk/combobox.tcl#L270
        """
        #   grab (create a new one or get existing) popdown
        popdown = self.tk.eval('ttk::combobox::PopdownWindow %s' % self)
        #   configure popdown font
        self.tk.call('%s.f.l' % popdown, 'configure', '-font', self['font'])

    def configure(self, cnf=None, **kw):
        """Configure resources of a widget. Overridden!

        The values for resources are specified as keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method keys.
        """

        #   default configure behavior
        self._configure('configure', cnf, kw)
        #   if font was configured - configure font for popdown as well
        if 'font' in kw or 'font' in cnf:
            self._handle_popdown_font()