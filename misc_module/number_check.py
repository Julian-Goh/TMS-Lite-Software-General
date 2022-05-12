import numpy as np
import re

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
        