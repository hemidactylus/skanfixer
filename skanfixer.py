#!/usr/bin/env python

""" Skanfixer, semi-automatic handling of extracting photos from scanned
    pages. Author: hemidactylus
"""

# standard imports
import Tkinter as tk

# project imports
from misc_utils import isPicture, findRescaleFactor
from MainWindow import MainWindow

# main body
root=tk.Tk()
window=MainWindow(root,'Skanfixer')

root.mainloop()
