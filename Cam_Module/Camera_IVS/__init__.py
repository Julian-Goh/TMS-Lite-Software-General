import os
import sys

curr_dir    = os.path.dirname(os.path.abspath(__file__))
prnt_dir    = os.path.dirname(curr_dir)
master_dir  = os.path.dirname(prnt_dir)

if curr_dir not in sys.path:
    sys.path.append(curr_dir)

if prnt_dir not in sys.path:
    sys.path.append(prnt_dir)

if master_dir not in sys.path:
    sys.path.append(master_dir)
