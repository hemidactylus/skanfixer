#!/usr/bin/env python

""" Skanfixer, semi-automatic handling of extracting photos from scanned
    pages. Author: hemidactylus
"""

import Tkinter as tk

from MainWindow import MainWindow

# main body
root=tk.Tk()
window=MainWindow(root,'Skanfixer')

root.mainloop()
