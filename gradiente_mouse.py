#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 23:16:55 2026

@author: macbook_vincenzo
"""

import tkinter as tk
from PIL import Image, ImageTk
import numpy as np

class InteractiveGradientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gradiente Interattivo a Mesh / Warp")
        
        self.width = 800
        self.height = 600
        
        # Creiamo un Canvas per gestire la grafica fluida
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, highlightthickness=0)
        self.canvas.pack()
        
        # Generiamo il gradiente iniziale centrato
        self.update_gradient(self.width // 2, self.height // 2)
        
        # Associamo gli eventi del mouse
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", self.on_mouse_leave)
        
    def update_gradient(self, mx, my):
        """Crea un gradiente dinamico basato sulla posizione del mouse (mx, my)"""
        # Creiamo una griglia di coordinate pixel
        x = np.arange(self.width)
        y = np.arange(self.height)
        xx, yy = np.meshgrid(x, y)
        
        # Calcoliamo la distanza euclidea di ogni pixel rispetto alla posizione attuale del mouse
        dist = np.sqrt((xx - mx)**2 + (yy - my)**2)
        
        # Normalizziamo la distanza per creare la transizione di colore (effetto warp)
        max_dist = np.sqrt(self.width**2 + self.height**2)
        t = np.clip(dist / (max_dist * 0.5), 0, 1)
        
        # Sfumatura di colori tra Arancione (255, 140, 0) e Verde (0, 128, 0)
        r = (1 - t) * 255 + t * 0
        g = (1 - t) * 140 + t * 128
        b = (1 - t) * 0 + t * 0
        
        # Uniamo i canali in un array NumPy RGB
        img_array = np.stack([r, g, b], axis=-1).astype(np.uint8)
        
        # Convertiamo in immagine PIL e poi in formato compatibile con Tkinter
        self.img_pil = Image.fromarray(img_array)
        self.img_tk = ImageTk.PhotoImage(self.img_pil)
        
        # Disegniamo l'immagine sul canvas aggiornandola al volo
        self.canvas.delete("gradient")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk, tag="gradient")
        
    def on_mouse_move(self,event):
        # Ogni volta che il mouse si muove, aggiorna il gradiente usando le coordinate (event.x, event.y)
        self.update_gradient(event.x, event.y)
        
    def on_mouse_leave(self,event):
        # Quando il mouse esce dalla finestra, riporta il gradiente al centro
        self.update_gradient(self.width // 2, self.height // 2)

if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveGradientApp(root)
    root.mainloop()