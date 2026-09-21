#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 16:47:43 2025

@author: macbook_vincenzo
"""

# importing only those functions which
# are needed
from tkinter import Tk, mainloop, TOP
from tkinter.ttk import Button

# time function used to calculate time
from time import time

# creating tkinter window
root = Tk()
root.title("PROVA FUNZIONE AFTER")

button = Button(root, text = 'prova AFTER')
button.pack(side = TOP, pady = 5)

print('in esecuzione...')
# Calculating starting time
start = time()

# in after method 5000 milliseconds
# is passed i.e after 5 seconds
# main window i.e root window will
# get destroyed
root.after(5000, root.destroy)

mainloop()

# calculating end time
end = time()
print('distrutto dopo % d secondi' % (end-start))