#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 22:13:05 2025

@author: ignoted,not me, downloaded from GitHub
"""

import tkinter as tk
import time
import math



class AnalogClock(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        tk.Canvas.__init__(self, parent, *args, **kwargs)
        self.width = self.winfo_reqwidth()
        self.height = self.winfo_reqheight()
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        self.face = self.create_oval(0, 0, self.width, self.height, fill='white')
        self.update_clock()
    

    def update_clock(self):
        self.delete(tk.ALL)
        self.face = self.create_oval(0, 0, self.width, self.height, fill='white')
        
        self.draw_ticks() #disegna i vari elementi
        self.draw_numbers()
        self.draw_hands()
        
        self.after(200, self.update_clock)

    def draw_numbers(self):
        self.create_text(self.center_x, self.center_y - 0.8 * self.center_y, text='12', font=('TkDefaultFont', 16))
        for i in range(1, 12):
            angle = i * (360 / 12)
            x = self.center_x + 0.8 * self.center_y * math.sin(math.radians(angle))
            y = self.center_y - 0.8 * self.center_y * math.cos(math.radians(angle))
            self.create_text(x, y, text=str(i), font=('Courier', 16))

    def draw_hands(self):
        now = time.localtime()
        hour = now.tm_hour % 12
        minute = now.tm_min
        second = now.tm_sec
        hour_angle = hour * (360 / 12) + minute * (360 / (12 * 60))
        minute_angle = minute * (360 / 60)
        second_angle = second * (360 / 60)
        
        #20/09/2026: lancette di doppiezza diverse:

        self.draw_hand(hour_angle, 0.5 * self.center_x, 'red', width=6)    # Ore: più spessa
        self.draw_hand(minute_angle, 0.7 * self.center_x, 'blue', width=4)  # Minuti: intermedia
        self.draw_hand(second_angle, 0.9 * self.center_x, 'green', width=1) # Secondi: più sottile

    def draw_hand(self, angle, length, color,width=2):
        x = self.center_x + length * math.sin(math.radians(angle))
        y = self.center_y - length * math.cos(math.radians(angle))
        self.create_line(self.center_x, self.center_y, x, y, fill=color, width=width)
        
    # aggiornamneto 24/09/2026: create le tacchette, ogni 5 minuti, una tacchetta piu doppia
    def draw_ticks(self):
        for i in range(1, 61):
            angle = i * (360 / 60)  # 6 gradi per ogni minuto
            
            # Se i è un multiplo di 5 (es. 5, 10, 15...) la tacca è più lunga
            if i % 5 == 0:
                outer_r = 0.95 * self.center_y  # Inizio vicino al bordo
                inner_r = 0.85 * self.center_y  # Entra più dentro
                thickness = 3
                color = 'black'
            else:
                outer_r = 0.95 * self.center_y
                inner_r = 0.90 * self.center_y  # Tacca più corta
                thickness = 1
                color = 'gray'
    
            # Calcolo punto esterno e punto interno della lineetta
            x_out = self.center_x + outer_r * math.sin(math.radians(angle))
            y_out = self.center_y - outer_r * math.cos(math.radians(angle))
            
            x_in = self.center_x + inner_r * math.sin(math.radians(angle))
            y_in = self.center_y - inner_r * math.cos(math.radians(angle))
    
            # Disegna il segnetto
            self.create_line(x_in, y_in, x_out, y_out, fill=color, width=thickness)
            

root = tk.Tk()
root.title("Orologio con Lancette")
clock = AnalogClock(root, width=400, height=400)
clock.pack()
        # ---> AGGIUNGI QUESTA RIGA PER BLOCCARLA IN FOREGROUND <---
root.attributes('-topmost', True)

root.mainloop()
