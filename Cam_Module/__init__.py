import os
from os import path
import sys

curr_dir     = os.path.dirname(os.path.abspath(__file__))
master_dir   = os.path.dirname(curr_dir)

mvs_module   = master_dir + '\\MVS-Python\\MvImport'
# print(master_dir)
if curr_dir not in sys.path:
    sys.path.append(curr_dir)

if master_dir not in sys.path:
    sys.path.append(master_dir)

if mvs_module not in sys.path:
    sys.path.append(mvs_module)
