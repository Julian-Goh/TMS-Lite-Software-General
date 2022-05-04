import numpy as np
import tkinter as tk
import re
from functools import partial

def validate_int_entry(d, P, S, only_positive = 'False'):
    # valid percent substitutions (from the Tk entry man page)
    # note: you only have to register the ones you need; this
    # example registers them all for illustrative purposes
    #
    # %d = Type of action (1=insert, 0=delete, -1 for others)
    # %i = index of char string to be inserted/deleted, or -1
    # %P = value of the entry if the edit is allowed
    # %s = value of entry prior to editing
    # %S = the text string being inserted or deleted, if any
    # %v = the type of validation that is currently set
    # %V = the type of validation that triggered the callback
    #      (key, focusin, focusout, forced)
    # %W = the tk name of the widget
    # print(only_positive, type(only_positive))
    # print('d = {} '.format(d), 'S = {} '.format(S), 'P = {}'.format(P))
    if only_positive == 'False':
        # if d == '1':
        if d != '0':
            if S == '-' and P == '-':
                return True
            if P == '-0':
                return False
            if len(P) > 1 and (P.split('0')[0]) == '':
                return False
            else:
                if is_int(P) == True:
                    return True
                else:
                    if P == '':
                        return True
                    else:
                        return False
        elif d == '0':
            return True

    elif only_positive == 'True':
        # if d == '1':
        if d != '0':
            if S == '-':
                return False
            if P == '-0':
                return False

            if len(P) > 1 and (P.split('0')[0]) == '':
                return False
            else:
                if is_int(P) == True:
                    return True
                else:
                    if P == '':
                        return True
                    else:
                        return False
        elif d == '0':
            return True

def validate_float_entry(d, P, S, decimal_places = 'None', only_positive = 'False'):
    # valid percent substitutions (from the Tk entry man page)
    # note: you only have to register the ones you need; this
    # example registers them all for illustrative purposes
    #
    # %d = Type of action (1=insert, 0=delete, -1 for others)
    # %i = index of char string to be inserted/deleted, or -1
    # %P = value of the entry if the edit is allowed
    # %s = value of entry prior to editing
    # %S = the text string being inserted or deleted, if any
    # %v = the type of validation that is currently set
    # %V = the type of validation that triggered the callback
    #      (key, focusin, focusout, forced)
    # %W = the tk name of the widget
    #print(decimal_places, type(decimal_places)) #decimal_places
    # print(d, S, P, decimal_places, only_positive, type(only_positive))

    if is_int(decimal_places) == True:
        if int(decimal_places) <= 0:
            decimal_places = int(2)
        else:
            decimal_places = int(decimal_places)
    else:
        decimal_places = int(2)
    
    if d != '0':
        if only_positive == 'False':
            if S == '-' and P == '-':
                return True
            else:
                if is_float(P) == True:
                    if len(P.split('.')) > 1 and len(P.split('.')[1]) > decimal_places: #Default decimal places is 2
                        return False
                    return True
                else:
                    if P == '':
                        return True
                    else:
                        return False

        else:
            if S == '-':
                return False
            else:
                if is_float(P) == True:
                    if len(P.split('.')) > 1 and len(P.split('.')[1]) > decimal_places: #Default decimal places is 2
                        return False
                    return True
                else:
                    if P == '':
                        return True
                    else:
                        return False
    else:
        return True

def is_number(value):
    if True == is_float(value):
        return True

    elif True == is_int(value):
        return True

    return False

def is_float(item):
    # A float is a float
    if isinstance(item, float) or isinstance(item, int):
        return True

    if isinstance(item, np.floating) or isinstance(item, np.integer):
        return True

    # Some strings can represent floats( i.e. a decimal )
    if isinstance(item, str):
        # Detect leading white-spaces
        if len(item) != len(item.strip()):
            return False

        float_pattern = re.compile("^-?([0-9])+\\.?[0-9]*$") ### This regular expression allows both int and float types.
        # print(float_pattern.match(item))
        if float_pattern.match(item):
            int_part  = item.split('.')[0] #### integer part: numbers before floating point
            ### frac_part = item.split('.')[1] #### fractional part: numbers after floating point
            search_lead_zeros = re.search("^(-0)?0*", int_part)

            if search_lead_zeros.span()[-1] > 1: ### More than 1 leading zeros
                if search_lead_zeros.group(0) == "-0":
                    return True
                else:
                    return False

            elif search_lead_zeros.span()[-1] == 1: ### 1 leading zeros
                if len(int_part) == 1: ### if length of string is 1, this means our string is '0'.
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False
    

    else: ### If the 'if' conditions above does not meet we return False
        return False

def is_int(item):
    # Ints are okay
    if isinstance(item, int):
        return True

    if isinstance(item, np.integer):
        return True

    # Some strings can represent ints ( i.e. a decimal )
    if isinstance(item, str):
        # Detect leading white-spaces
        if len(item) != len(item.strip()):
            return False

        
        int_pattern = re.compile("^-?[0-9]+$")
        # print(int_pattern.match(item))
        if int_pattern.match(item):
            search_lead_zeros = re.search("^(-0)?0*", item)
            # print(search_lead_zeros.span()[-1])
            if search_lead_zeros.span()[-1] > 1: ### More than 1 leading zeros
                return False

            elif search_lead_zeros.span()[-1] == 1: ### 1 leading zeros
                if len(item) == 1: ### if length of string is 1, this means our string is '0'.
                    return True
                else:
                    return False
            else: ### 0 leading zeros
                return True
        else:
            return False

    else: ### If the 'if' conditions above does not meet we return False
        return False

def round_float(value, place = 2):
    value = float(value)
    return float(f'{value:.{place}f}')

def str_float(value, place = 2):
    value = float(value)
    return f'{value:.{place}f}'


class Validate_Int():
    __kp_event = False
    def __init__(self, tk_widget, tk_var, only_positive = False, lo_limit = None, hi_limit = None):
        if isinstance(tk_widget, tk.Entry) == True or isinstance(tk_widget, tk.Spinbox) == True:
            pass
        else:
            raise AttributeError("tk_widget must be a tkinter.Entry or tkinter.Spinbox class object")

        """
        1st we check if lo_limit & hi_limit are integers/strings which can be convert to integers.
        """
        int_err = np.zeros((2,), dtype = bool)

        if is_int(lo_limit) == True:
            int_err[0] = False

        elif is_int(lo_limit) == False:
            int_err[0] = True

        if is_int(hi_limit) == True:
            int_err[1] = False

        elif is_int(hi_limit) == False:
            int_err[1] = True

        if np.any(int_err) == True:
            raise ValueError("'lo_limit' & 'hi_limit' arguments must be a int-type value/data")

        elif np.any(int_err) == False:
            if is_int(lo_limit) == True and is_int(hi_limit) == True:
                if lo_limit > hi_limit:
                    raise ValueError("'lo_limit' must be > 'hi_limit'")

                else: ## Else if lo_limit >= hi_limit, we will check if it suits the condition of only_positive.
                    if only_positive != False and lo_limit < 0:
                        only_positive = False ## We set only_positive to False, indicating that the validation allows negative numbers

            elif is_int(lo_limit) == True and is_int(hi_limit) == False:
                if only_positive != False and lo_limit < 0:
                    only_positive = False ## We set only_positive to False, indicating that the validation allows negative numbers

            elif is_int(lo_limit) == False and is_int(hi_limit) == True:
                if only_positive != False and hi_limit < 0:
                    only_positive = False ## We set only_positive to False, indicating that the validation allows negative numbers

        self.__tk_widget = tk_widget
        self.__tk_var = tk_var
        self.__only_positive = only_positive
        self.__lo_limit = int(lo_limit)
        self.__hi_limit = int(hi_limit)

        self.__tk_widget['validate'] = 'key'
        self.__tk_widget['vcmd'] = (self.__tk_widget.register(validate_int_entry), '%d', '%P', '%S', str(self.__only_positive))

        self.__custom_tag = "validate--{}".format( re.sub(".!", "", str(self.__tk_widget)) )
        self.__tk_var.trace('wu', lambda var_name, var_index, operation: self.__trace_event())

        # print(tk.Entry.__name__)
        # print(dir(self.__tk_widget), type(self.__tk_widget))
        # print(self.__tk_widget.__class__.__name__)

        bindtags = list(self.__tk_widget.bindtags())

        if self.__custom_tag in bindtags:
            bindtags.remove(self.__custom_tag)
            self.__tk_widget.bindtags(tuple(bindtags))

        # if isinstance(self.__tk_widget, tk.Spinbox) == True:
        #     index = bindtags.index("Spinbox")
        # elif isinstance(self.__tk_widget, tk.Entry) == True:
        #     index = bindtags.index("Entry")
        index = bindtags.index(str(self.__tk_widget))

        bindtags.insert(index, self.__custom_tag)
        self.__tk_widget.bindtags(tuple(bindtags))
        del bindtags

        self.__tk_widget.bind_class(self.__custom_tag, "<KeyPress>"  , partial(self.__del_lead_zero, tk_wid = self.__tk_widget, only_positive = self.__only_positive), add = "+")
        self.__tk_widget.bind_class(self.__custom_tag, "<KeyPress>"  , self.__validate_keyp, add = "+")
        self.__tk_widget.bind_class(self.__custom_tag, "<KeyRelease>", self.__keyrelease, add = "+")

        # print(self.__tk_widget.bindtags())

    def __trace_event(self):
        # print("Trace", Validate_Int.__kp_event)
        if Validate_Int.__kp_event == False:
            tk_str = self.__tk_var.get()
            if is_int(tk_str) == False:
                self.__tk_var.set("")

            elif is_int(tk_str) == True:
                if is_int(self.__lo_limit) == True and is_int(self.__hi_limit) == True:
                    if self.__lo_limit <= int(tk_str) <= self.__hi_limit:
                        pass
                    else:
                        self.__tk_var.set("")

                elif is_int(self.__lo_limit) == True and is_int(self.__hi_limit) == False:
                    if int(tk_str) < self.__lo_limit:
                        self.__tk_var.set("")

                elif is_int(self.__lo_limit) == False and is_int(self.__hi_limit) == True:
                    if int(tk_str) > self.__hi_limit:
                        self.__tk_var.set("")

        cursor_index = self.__tk_widget.index(tk.INSERT)
        if cursor_index == len(str(self.__tk_var.get())):
            self.__tk_widget.xview_moveto('1')

        self.__tk_widget['validate'] = 'key'
        self.__tk_widget['vcmd'] = (self.__tk_widget.register(validate_int_entry), '%d', '%P', '%S', str(self.__only_positive))

    def __bool_highlight(self):
        if isinstance(self.__tk_widget, tk.Spinbox) or isinstance(self.__tk_widget, tk.Entry):
            try:
                self.__tk_widget.selection_get()
                return True
            except (tk.TclError):
                ### print("No highlighted texts")
                pass

        return False

    def __del_highlight(self, _bool, char):
        if _bool == True:
            self.__tk_widget.delete("sel.first", "sel.last")
            s = self.__tk_widget.get()
            s_list = list(s)
            cursor_index = self.__tk_widget.index(tk.INSERT)
            s_list.insert(cursor_index, char)
            new_str = "".join(s_list)
            # print(new_str)
            del s_list
            ### Try to check if the inserted character is passable
            if is_int(self.__lo_limit) == True and is_int(self.__hi_limit) == True:
                if self.__lo_limit <= int(new_str) <= self.__hi_limit:
                    pass
                else:
                    return
            elif is_int(self.__lo_limit) == True and is_int(self.__hi_limit) == False:
                if int(new_str) < self.__lo_limit:
                    return
            elif is_int(self.__lo_limit) == False and is_int(self.__hi_limit) == True:
                if int(new_str) > self.__hi_limit:
                    return
            self.__tk_widget.insert(cursor_index, char)

    def __validate_keyp(self, event):
        Validate_Int.__kp_event = True
        if event.char.isprintable() and event.char != '':
            curr_str = self.__tk_widget.get()
            s_list = list(curr_str)
            cursor_index = self.__tk_widget.index(tk.INSERT)
            s_list.insert(cursor_index, event.char)
            new_str = "".join(s_list)
            del s_list
            # print(new_str, curr_str, cursor_index)
            highlight = self.__bool_highlight()

            int_bool = is_int(new_str)
            if int_bool == True:
                if is_int(self.__lo_limit) == True and is_int(self.__hi_limit) == True:
                    if self.__lo_limit <= int(new_str) <= self.__hi_limit:
                        pass
                    else:
                        self.__del_highlight(highlight, event.char)
                        return "break"

                elif is_int(self.__lo_limit) == True and is_int(self.__hi_limit) == False:
                    if int(new_str) < self.__lo_limit:
                        self.__del_highlight(highlight, event.char)
                        return "break"

                elif is_int(self.__lo_limit) == False and is_int(self.__hi_limit) == True:
                    if int(new_str) > self.__hi_limit:
                        self.__del_highlight(highlight, event.char)
                        return "break"

            elif int_bool == False:
                if self.__only_positive == False:
                    if new_str == '-':
                        pass
                    else:
                        if is_int(curr_str) == False:
                            self.__tk_widget.delete("0", tk.END)

                elif self.__only_positive == True:
                    if is_int(curr_str) == False:
                        self.__tk_widget.delete("0", tk.END)

    def __keyrelease(self, event):
        Validate_Int.__kp_event = False


    def __del_lead_zero(self, event, tk_wid, only_positive = True):
        if only_positive == False:
            if str(event.char).isnumeric() == True or str(event.char) == '-':
                if str(tk_wid.get()) == '0':
                    if isinstance(tk_wid, tk.Spinbox) == True:
                        tk_wid.selection_clear()
                        tk_wid.focus_set()
                        tk_wid.selection('range', 0, tk.END)

                    elif isinstance(tk_wid, tk.Entry) == True:
                        tk_wid.selection_clear()
                        tk_wid.focus_set()
                        tk_wid.selection_range(0, tk.END)
        else:
            if str(event.char).isnumeric() == True:
                if str(tk_wid.get()) == '0':
                    if isinstance(tk_wid, tk.Spinbox) == True:
                        tk_wid.selection_clear()
                        tk_wid.focus_set()
                        tk_wid.selection('range', 0, tk.END)
                        
                    elif isinstance(tk_wid, tk.Entry) == True:
                        tk_wid.selection_clear()
                        tk_wid.focus_set()
                        tk_wid.selection_range(0, tk.END)

    def update_limit(self, only_positive = False, lo_limit = None, hi_limit = None):

        if is_int(lo_limit) == True and is_int(hi_limit) == True:
            if lo_limit > hi_limit:
                raise ValueError("'lo_limit' must be > 'hi_limit'")

            else: ## Else if lo_limit >= hi_limit, we will check if it suits the condition of only_positive.
                if only_positive != False and lo_limit < 0:
                    only_positive = False ## We set only_positive to False, indicating that the validation allows negative numbers

        elif is_int(lo_limit) == True and is_int(hi_limit) == False:
            if only_positive != False and lo_limit < 0:
                only_positive = False ## We set only_positive to False, indicating that the validation allows negative numbers

        elif is_int(lo_limit) == False and is_int(hi_limit) == True:
            if only_positive != False and hi_limit < 0:
                only_positive = False ## We set only_positive to False, indicating that the validation allows negative numbers

        self.__only_positive = only_positive
        self.__lo_limit = int(lo_limit)
        self.__hi_limit = int(hi_limit)



class Validate_Float():
    __kp_event = False
    def __init__(self, tk_widget, tk_var, decimal_places = None, only_positive = False, lo_limit = None, hi_limit = None):
        """
        1st we check if lo_limit & hi_limit are integers/strings which can be convert to floats.
        """
        if isinstance(tk_widget, tk.Entry) == True or isinstance(tk_widget, tk.Spinbox) == True:
            pass
        else:
            raise AttributeError("tk_widget must be a tkinter.Entry or tkinter.Spinbox class object")

        float_err = np.zeros((2,), dtype = bool)

        if is_float(lo_limit) == True:
            float_err[0] = False

        elif is_float(lo_limit) == False:
            float_err[0] = True

        if is_float(hi_limit) == True:
            float_err[1] = False

        elif is_float(hi_limit) == False:
            float_err[1] = True

        if float_err[0] == True and float_err[1] == True:
            raise ValueError("'lo_limit' or 'hi_limit' arguments must be a float-type value/data")

        else:
            if is_float(lo_limit) == True and is_float(hi_limit) == True:
                if lo_limit > hi_limit:
                    raise ValueError("'lo_limit' must be > 'hi_limit'")

                else: ## Else if lo_limit >= hi_limit, we will check if it suits the condition of only_positive.
                    if only_positive != False and lo_limit < 0:
                        only_positive = False ## We set only_positive to False, indicating that the validation allows negative numbers

            elif is_float(lo_limit) == True and is_float(hi_limit) == False:
                if only_positive != False and lo_limit < 0:
                    only_positive = False ## We set only_positive to False, indicating that the validation allows negative numbers

            elif is_float(lo_limit) == False and is_float(hi_limit) == True:
                if only_positive != False and hi_limit < 0:
                    only_positive = False ## We set only_positive to False, indicating that the validation allows negative numbers

        self.__tk_widget = tk_widget
        self.__tk_var = tk_var
        self.__decimal_places = decimal_places
        self.__only_positive = only_positive
        self.__lo_limit = float(lo_limit)
        self.__hi_limit = float(hi_limit)


        if 0 < self.__lo_limit < 1:
            self.__unit_lo = True
        else:
            self.__unit_lo = False
        ### Setting a special case for KeyPress event is important in the case where a floating number of 0 < n < 1.
        ### self.__unit_lo is used to identify whether self.__lo_limit is an unit interval [0, 1]
        ### because the 1st value user is going to press is 0

        self.__tk_widget['validate'] = 'key'
        self.__tk_widget['vcmd'] = (self.__tk_widget.register(validate_float_entry), '%d', '%P', '%S', str(self.__decimal_places), str(self.__only_positive))


        self.__custom_tag = "validate--{}".format( re.sub(".!", "", str(self.__tk_widget)) )
        self.__tk_var.trace('wu', lambda var_name, var_index, operation: self.__trace_event())

        bindtags = list(self.__tk_widget.bindtags())
        if self.__custom_tag in bindtags:
            bindtags.remove(self.__custom_tag)
            self.__tk_widget.bindtags(tuple(bindtags))

        # if isinstance(self.__tk_widget, tk.Spinbox) == True:
        #     index = bindtags.index("Spinbox")
        # elif isinstance(self.__tk_widget, tk.Entry) == True:
        #     index = bindtags.index("Entry")
        index = bindtags.index(str(self.__tk_widget))

        bindtags.insert(index, self.__custom_tag)
        self.__tk_widget.bindtags(tuple(bindtags))
        del bindtags

        self.__tk_widget.bind_class(self.__custom_tag, "<KeyPress>"  , partial(self.__del_lead_zero, tk_wid = self.__tk_widget, only_positive = self.__only_positive), add = "+")
        self.__tk_widget.bind_class(self.__custom_tag, "<KeyPress>"  , self.__validate_keyp, add = "+")
        self.__tk_widget.bind_class(self.__custom_tag, "<KeyRelease>", self.__keyrelease, add = "+")
        self.__tk_widget.bind_class(self.__custom_tag, "<Return>"    , self.__check_lo_limit, add = "+")
        self.__tk_widget.bind_class(self.__custom_tag, "<FocusOut>"  , self.__check_lo_limit, add = "+")

        # print(self.__tk_widget.bindtags())
        
    def __trace_event(self):
        # print("Trace Check")
        if Validate_Float.__kp_event == False:
            tk_str = self.__tk_var.get()
            if is_float(tk_str) == False:
                self.__tk_var.set("")

            elif is_float(tk_str) == True:
                if is_float(self.__lo_limit) == True and is_float(self.__hi_limit) == True:
                    if self.__lo_limit <= float(tk_str) <= self.__hi_limit:
                        pass
                    else:
                        self.__tk_var.set("")

                elif is_float(self.__lo_limit) == True and is_float(self.__hi_limit) == False:
                    if float(tk_str) < self.__lo_limit:
                        self.__tk_var.set("")

                elif is_float(self.__lo_limit) == False and is_float(self.__hi_limit) == True:
                    if float(tk_str) > self.__hi_limit:
                        self.__tk_var.set("")

        cursor_index = self.__tk_widget.index(tk.INSERT)
        if cursor_index == len(str(self.__tk_var.get())):
            self.__tk_widget.xview_moveto('1')

        self.__tk_widget['validate'] = 'key'
        self.__tk_widget['vcmd'] = (self.__tk_widget.register(validate_float_entry), '%d', '%P', '%S', str(self.__decimal_places), str(self.__only_positive))

    def __bool_highlight(self):
        if isinstance(self.__tk_widget, tk.Spinbox) or isinstance(self.__tk_widget, tk.Entry):
            try:
                self.__tk_widget.selection_get()
                return True
            except (tk.TclError):
                ### print("No highlighted texts")
                pass

        return False

    def __del_highlight(self, _bool, char):
        if _bool == True:
            self.__tk_widget.delete("sel.first", "sel.last")
            s = self.__tk_widget.get()
            s_list = list(s)
            cursor_index = self.__tk_widget.index(tk.INSERT)
            s_list.insert(cursor_index, char)
            new_str = "".join(s_list)
            # print(new_str)
            del s_list
            ### Try to check if the inserted character is passable
            if is_float(self.__lo_limit) == True and is_float(self.__hi_limit) == True:
                if self.__lo_limit <= float(new_str) <= self.__hi_limit:
                    pass
                else:
                    if self.__unit_lo == True:
                        if str(new_str) == "0." or str(new_str) == "0": ### we only allow user to key in "0." or "0"
                            pass
                        else:
                            return
                    else:
                        return
            elif is_float(self.__lo_limit) == True and is_float(self.__hi_limit) == False:
                if float(new_str) < self.__lo_limit:
                    if self.__unit_lo == True:
                        if str(new_str) == "0." or str(new_str) == "0": ### we only allow user to key in "0." or "0"
                            pass
                        else:
                            return
                    else:
                        return
            elif is_float(self.__lo_limit) == False and is_float(self.__hi_limit) == True:
                if float(new_str) > self.__hi_limit:
                    return
            self.__tk_widget.insert(cursor_index, char)

    def __validate_keyp(self, event):
        # print(event.char, event.char.isprintable(), event.char == '')
        Validate_Float.__kp_event = True
        if event.char.isprintable() and event.char != '':
            # print("Keypress Check")
            curr_str = self.__tk_widget.get()
            s_list = list(curr_str)
            cursor_index = self.__tk_widget.index(tk.INSERT)
            s_list.insert(cursor_index, event.char)
            new_str = "".join(s_list)
            del s_list
            # print('cursor_index: ', cursor_index)
            # print('new_str: ', new_str)
            highlight = self.__bool_highlight()

            float_bool = is_float(new_str)
            if float_bool == True:
                if is_float(self.__lo_limit) == True and is_float(self.__hi_limit) == True:
                    if self.__lo_limit <= float(new_str) <= self.__hi_limit:
                        pass

                    else:
                        if self.__unit_lo == True:
                            if str(new_str) == "0." or str(new_str) == "0": ### we only allow user to key in "0." or "0"
                                pass
                            else:
                                self.__del_highlight(highlight, event.char)
                                return "break"
                        else:
                            self.__del_highlight(highlight, event.char)
                            return "break"

                elif is_float(self.__lo_limit) == True and is_float(self.__hi_limit) == False:
                    if float(new_str) < self.__lo_limit:
                        if self.__unit_lo == True:
                            if str(new_str) == "0." or str(new_str) == "0": ### we only allow user to key in "0." or "0"
                                pass
                            else:
                                self.__del_highlight(highlight, event.char)
                                return "break"
                        else:
                            self.__del_highlight(highlight, event.char)
                            return "break"

                elif is_float(self.__lo_limit) == False and is_float(self.__hi_limit) == True:
                    if float(new_str) > self.__hi_limit:
                        self.__del_highlight(highlight, event.char)
                        return "break"

            elif float_bool == False:
                if self.__only_positive == False:
                    if new_str == '-':
                        pass
                    else:
                        if is_float(curr_str) == False:
                            self.__tk_widget.delete("0", tk.END)

                elif self.__only_positive == True:
                    if is_float(curr_str) == False:
                        self.__tk_widget.delete("0", tk.END)

    def __keyrelease(self, event):
        Validate_Float.__kp_event = False

    def __check_lo_limit(self, event):
        if self.__unit_lo == True:
            if is_float(self.__tk_widget.get()) == True:
                if float(self.__tk_widget.get()) < self.__lo_limit:
                    print("Checking low limit")
                    self.__tk_widget.delete("0", tk.END)
                    self.__tk_widget.insert("0", self.__lo_limit)

    def __del_lead_zero(self, event, tk_wid, only_positive = True):
        if only_positive == False:
            if str(event.char).isnumeric() == True or str(event.char) == '-':
                if str(tk_wid.get()) == '0':
                    if isinstance(tk_wid, tk.Spinbox) == True:
                        tk_wid.selection_clear()
                        tk_wid.focus_set()
                        tk_wid.selection('range', 0, tk.END)

                    elif isinstance(tk_wid, tk.Entry) == True:
                        tk_wid.selection_clear()
                        tk_wid.focus_set()
                        tk_wid.selection_range(0, tk.END)
        else:
            if str(event.char).isnumeric() == True:
                if str(tk_wid.get()) == '0':
                    if isinstance(tk_wid, tk.Spinbox) == True:
                        tk_wid.selection_clear()
                        tk_wid.focus_set()
                        tk_wid.selection('range', 0, tk.END)
                        
                    elif isinstance(tk_wid, tk.Entry) == True:
                        tk_wid.selection_clear()
                        tk_wid.focus_set()
                        tk_wid.selection_range(0, tk.END)

    def update_limit(self, decimal_places = None, only_positive = False, lo_limit = None, hi_limit = None):

        if is_float(lo_limit) == True and is_float(hi_limit) == True:
            if lo_limit > hi_limit:
                raise ValueError("'lo_limit' must be > 'hi_limit'")

            else: ## Else if lo_limit >= hi_limit, we will check if it suits the condition of only_positive.
                if only_positive != False and lo_limit < 0:
                    only_positive = False ## We set only_positive to False, indicating that the validation allows negative numbers

        elif is_float(lo_limit) == True and is_float(hi_limit) == False:
            if only_positive != False and lo_limit < 0:
                only_positive = False ## We set only_positive to False, indicating that the validation allows negative numbers

        elif is_float(lo_limit) == False and is_float(hi_limit) == True:
            if only_positive != False and hi_limit < 0:
                only_positive = False ## We set only_positive to False, indicating that the validation allows negative numbers

        self.__decimal_places = decimal_places
        self.__only_positive = only_positive
        self.__lo_limit = float(lo_limit)
        self.__hi_limit = float(hi_limit)

        if 0 < self.__lo_limit < 1:
            self.__unit_lo = True
        else:
            self.__unit_lo = False
        ### Setting a special case for KeyPress event is important in the case where a floating number of 0 < n < 1.
        ### self.__unit_lo is used to identify whether self.__lo_limit is an unit interval [0, 1]
        ### because the 1st value user is going to press is 0
    