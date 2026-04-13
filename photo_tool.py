"""
================================================================================
PROGETTO: Photo Editor Tool (V. 2.0)
================================================================================

AUTORI:
    - Sviluppatore Principale: MacbookVincenzo
    - Co-sviluppatore/Assistente AI: Google Gemini (Modello Flash 2.5)

DATA DI INIZIO PROGETTO:
    - 2024-05-10 (Data del primo scambio)

STORICO AGGIORNAMENTI PRINCIPALI:
    - 2024-05-15: Implementazione Filtro Canny (Rilevamento Bordi) e Punti.
    - 2024-05-20: Integrazione PyTorch per accelerazione GPU (MPS) su filtri.
    - 2024-05-25: Aggiunta Funzionalità Drag-and-Drop (tkdnd).
    - 2024-05-30: Implementazione Rilevamento e Sfocatura Volti/Targhe (OpenCV Haar Cascade).
    - 2024-06-05: Aggiunta Funzionalità Zoom Adattativo con mantenimento Aspect Ratio.
    - 2024-12-05: Aggiunta Gestione File Vettoriali SVG (Rasterizzazione con cairosvg).
    -2025-19-12:  AGGIUNGIAMO una palette (visualizza i colori realemnte usati) e sua gestione 

FUNZIONI E CAPACITÀ PRINCIPALI:
    - Gestione Multi-formato (Raster: JPG, PNG, Vettoriale: SVG).
    - Manipolazione Filtri Immagine (Bianco/Nero, Saturazione, Luminosità).
    - Effetti Artistici (Cartoonize, Warp/Distorsione).
    - Generazione Puzzle "Unisci i Puntini" con campionamento intelligente.
    - Rilevamento e Offuscamento Privacy (Volti, Targhe) tramite Haar Cascades.
    - Interfaccia Utente Reattiva: Zoom Adattativo e Drag-and-Drop.
    - Accelerazione dei calcoli complessi tramite GPU (MPS/PyTorch) con threading.

FUNZIONALITÀ NON RIUSCITE (e risolte/abbandonate):
    - Iniziale difficoltà con l'importazione di TkinterDnD2.
    - Iniziale rilevamento incompleto dei volti in prospettiva.
    - Iniziale blocco dell'UI dovuto a calcoli pesanti su CPU.

NOTE SULL'ARCHITETTURA:
    - Uso di Tkinter/ttk per la GUI.
    - Uso di PIL/Pillow per la manipolazione base delle immagini.
    - Uso di OpenCV (cv2) per la Computer Vision avanzata.
    - Uso di PyTorch per l'accelerazione GPU.
    - Uso di cairosvg per la gestione dei vettoriali.
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ExifTags,ImageDraw, ImageFont

#5/12/2025: introduciamo(con l'aiuto di San Gemini google) la funzione che permette di aprire e gestire
#i file di grafica vettoriale SVG

import cairosvg
from io import BytesIO  # Per gestire i dati binari in memoria


# import TkinterDnD2 as tkdnd
 
import os
import math
from playsound import playsound
import threading
import time

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from rembg import remove
import io
#2012026: per motion blur(foto mosse)
from PIL import ImageChops, ImageFilter

class PhotoEditorApp:
    def __init__(self, master):
        self.master = master
        master.title("Il Mio Photo Tool")

        self.image = None
        self.original_image_full = None # Questa è la variabile che conserva l'immagine originale non toccata
        # Queste variabili sotto sono usate per gestire lo stato corrente dell'immagine
        # o copie temporanee per specifiche operazioni.
        self.original_image_for_warp = None # Base PIL per il warp (quando non è attiva la GPU)
        self.original_color_image = None # Immagine base a colori per le operazioni interne (es. b/n toggle, warp)
        
        self.tk_image = None
        self.current_image_path = None
        self.zoom_level = 1.0
        self.blur_radius = 0
        self.alpha_level = 1.0
        
        self.warp_active = False
        # --- MODIFICHE PER EFFETTO "LENTE D'INGRANDIMENTO" ---
        self.warp_radius = 80  # Raggio più piccolo per un effetto più localizzato
        self.warp_strength = self.warp_radius*0.8 # Forza maggiore per un'ingrandimento più evidente, 25/12/2025: colllego anche la strenght, al radius selezionato
        # Puoi sperimentare con questi valori:
        # Per un raggio ancora più piccolo: 50
        # Per una forza ancora maggiore: 1.5 o 2.0
        # --- FINE MODIFICHE ---
        self.original_image_for_warp_tensor = None 
        
        #2012026: motion blur(foto mosse), variabile 
        self.motion_blur_intensity = tk.IntVar(value=10) # Intensità di default
        

        self.is_grayscale_active = tk.BooleanVar(value=False)

        self.warp_sound_path = "/Users/macbook_vincenzo/Python/sounds/213693__taira-komori__warp1.mp3"
        self.sound_thread = None
        self.sound_playing = False

        self.camera_active = False
        self.camera_capture = None
        self.camera_thread = None
        self.stop_camera_thread = threading.Event()
        self.current_camera_frame = None

        self.zoom_box_active = True
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        
        self.canvas_message_id = None 

        # --- VARIABILE PER IL DISPOSITIVO PYTORCH ---
        self.device = torch.device("cpu") 
        self.gpu_accelerated_active = False 
        
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            print(f"PyTorch utilizzerà il dispositivo: {self.device} (MPS)")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
            print(f"PyTorch utilizzerà il dispositivo: {self.device} (CUDA/ROCm)")
        else:
            print(f"PyTorch utilizzerà il dispositivo: {self.device} (CPU)")
        # --- FINE VARIABILE ---

        self.create_widgets()
        self.update_warp_status()
        self.on_grayscale_selection() 
        self.show_canvas_message("Clicca su 'APRI' per caricare un'immagine o 'ATTIVA FOTOCAMERA'")

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 16/11/2025 Associa l'evento di ridimensionamento della finestra alla funzione di resize
        self.master.bind('<Configure>', self.resize_image)
        # Aggiungi queste righe nel tuo metodo __init__

        # Dimensione fissa dei tuoi controlli laterali (stimali in base al tuo layout)
        self.controls_width = 250 # Ad esempio, 250 pixel
        # Altezza della barra di stato (stima)
        self.status_bar_height = 30 # Ad esempio, 30 pixel
        # Variabili per tracciare il ridimensionamento della finestra ed evitare loop
        self.last_width = 0
        self.last_height = 0

    def create_widgets(self):
        """
        Metodo riorganizzato il 25/12/2025. 
        Layout: Sidebar a sinistra, Canvas al centro/destra, Status bar sotto.
    """
        # --- 1. BARRE DI STATO (In basso) ---
        self.status_bar = tk.Label(self.master, text="Nessuna immagine caricata.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
        self.warp_status_bar = tk.Label(self.master, text="Warp: OFF", bd=1, relief=tk.FLAT, anchor=tk.E, bg="lightblue", fg="darkblue", font=('Helvetica', 10, 'bold'))
        self.warp_status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
        # --- 0. INIZIALIZZAZIONE VARIABILI DI CONTROLLO ---
        # Queste devono esistere PRIMA di creare gli slider
        if not hasattr(self, 'cartoonize_factor'):
            self.cartoonize_factor = tk.DoubleVar(value=0)
        # --- 2. SIDEBAR (Sinistra) ---
        # Usiamo un colore scuro per distinguere l'area dei comandi
        self.sidebar_frame = tk.Frame(self.master, width=250, bg="#2e2e2e", padx=5, pady=5)
        self.sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False) # Forza la larghezza a 250px
    
        # --- 3. AREA CONTENUTO PRINCIPALE (Destra/Centro) ---
        self.main_area = tk.Frame(self.master, bg="lightgrey")
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        # Canvas (figlio di main_area)
        self.canvas = tk.Canvas(self.main_area, bg="lightgrey", highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        self.image_label = self.canvas.create_image(0, 0, anchor="nw")
        self.canvas.bind('<Motion>', self.handle_mouse_motion)
        self.canvas.bind('<Leave>', self.handle_mouse_leave)
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
    
        # --- 4. POPOLAMENTO SIDEBAR (Comandi) ---
        
        # Gruppo WARP
        self.warp_toggle_button = tk.Button(self.sidebar_frame, text="ATTIVA WARP", command=self.toggle_warp)
        self.warp_toggle_button.pack(pady=5, fill=tk.X)
    
        self.warp_slider = tk.Scale(self.sidebar_frame, from_=10, to=200, orient=tk.HORIZONTAL, label="Raggio Warp", 
                                    command=self.update_warp_radius, variable=self.warp_radius, font=("Helvetica", 8), bg="#2e2e2e", fg="white")
        self.warp_slider.set(50)
        self.warp_slider.pack(pady=2, fill=tk.X)
    
        # Gruppo FOTOCAMERA
        self.toggle_camera_button = tk.Button(self.sidebar_frame, text="FOTOCAMERA ON/OFF", command=self.toggle_camera)
        self.toggle_camera_button.pack(pady=5, fill=tk.X)
        self.take_photo_button = tk.Button(self.sidebar_frame, text="SCATTA FOTO", command=self.take_photo, state=tk.DISABLED)
        self.take_photo_button.pack(pady=5, fill=tk.X)
    
        # Gruppo FILE (Apri/Chiudi vicini)
        file_frame = tk.Frame(self.sidebar_frame, bg="#2e2e2e")
        file_frame.pack(pady=5, fill=tk.X)
        tk.Button(file_frame, text="APRI", command=self.open_image).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(file_frame, text="CHIUDI", command=self.close_image).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
    
        # Gruppo RIPRISTINA
        try:
            icon_path = "/Users/macbook_vincenzo/Python/photo_tool_env/restore_icon.png" 
            self.restore_icon = Image.open(icon_path).resize((20, 20), Image.LANCZOS)
            self.restore_tk_icon = ImageTk.PhotoImage(self.restore_icon)
            self.restore_button = tk.Button(self.sidebar_frame, image=self.restore_tk_icon, text=" Ripristina", compound=tk.LEFT, command=self.restore_original_image)
        except:
            self.restore_button = tk.Button(self.sidebar_frame, text="Ripristina Originale", command=self.restore_original_image)
        self.restore_button.pack(pady=5, fill=tk.X)
    
        # Gruppo ZOOM
        zoom_frame = tk.Frame(self.sidebar_frame, bg="#2e2e2e")
        zoom_frame.pack(pady=5, fill=tk.X)
        tk.Button(zoom_frame, text="Z+", command=self.zoom_in).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(zoom_frame, text="Z-", command=self.zoom_out).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(self.sidebar_frame, text="RESET ZOOM", command=self.reset_zoom).pack(pady=2, fill=tk.X)
        
        
        ## bottone Ruota a destra 
    
        ##
        tk.Button(zoom_frame, text="Ruota ->", command=self.rotate_right).pack(fill=tk.X, pady=3)
        # bottone ruota a sinistra
        tk.Button(zoom_frame, text="Ruota <- ", command=self.rotate_left).pack(fill=tk.X, pady=3)

        
        
        # Gruppo EFFETTI (Blur, Alpha, BG)
        tk.Button(self.sidebar_frame, text="Sfoca Volti/Targhe", command=self.apply_privacy_blur).pack(pady=5, fill=tk.X)
        tk.Button(self.sidebar_frame, text="Rimuovi Sfondo AI", command=self.remove_ai_background).pack(pady=5, fill=tk.X)
        
        # Gruppo CARTOON
        self.cartoonize_slider = tk.Scale(self.sidebar_frame, from_=0, to=100, orient=tk.HORIZONTAL, label="Fattore Cartoon",
                                         command=self.update_cartoonize, variable=self.cartoonize_factor, bg="#2e2e2e", fg="white")
        self.cartoonize_slider.pack(fill=tk.X)
    
        # --- 5. SEZIONE PALETTE (Nuova 12/2025) ---
        tk.Frame(self.sidebar_frame, height=1, bg="grey").pack(fill=tk.X, pady=10) # Separatore
        
        self.show_palette_var = tk.BooleanVar(value=False)
        self.palette_check = tk.Checkbutton(
            self.sidebar_frame, 
            text="🎨 Visualizza Palette", 
            variable=self.show_palette_var,
            command=self.toggle_palette_view,
            bg="#2e2e2e", fg="white", selectcolor="#444", activebackground="#2e2e2e"
        )
        self.palette_check.pack(pady=5, anchor="w")
    
        # Frame per i quadratini della palette
        self.palette_container = tk.Frame(self.sidebar_frame, bg="#2e2e2e")
        # Viene mostrato/nascosto da toggle_palette_view
        
                # Sotto il gruppo Effetti nella sidebar
        self.motion_btn = tk.Button(
            self.sidebar_frame, 
            text="💫 Effetto Mosso (Ghost)", 
            command=self.apply_motion_effect,
            bg="#2e2e2e", fg="orange"
        )
        self.motion_btn.pack(pady=5, fill=tk.X)
        
            # --- 17/01/2026 PULSANTE FILTRO BELLEZZA (Per la cugina) ---
        self.beauty_btn = tk.Button(
            self.sidebar_frame, 
            text="✨ FILTRO RED CARPET", 
            command=self.apply_beauty_filter,
            bg="#ffc0cb", fg="black", font=("Helvetica", 10, "bold") # Un tocco di rosa per distinguerlo
        )
        self.beauty_btn.pack(pady=10, fill=tk.X)
        
        self.youth_btn = tk.Button(
            self.sidebar_frame, 
            text="✨ FILTRO GIOVINEZZA", 
            command=self.apply_eternal_youth,
            bg="#dfc3cd", fg="black", font=("Helvetica", 10, "bold") # Un tocco di ... per distinguerlo
        )
        self.beauty_btn.pack(pady=10, fill=tk.X)
        
        self.youth_btn.pack(pady=12, fill=tk.X)
         
    def update_warp_radius(self,val):

        # 'val' è il valore numerico (str o int) passato automaticamente da Tkinter
        
        # Non è necessario usare self.warp_radius.get(), perché 'val' contiene già il valore.
        # Se vuoi, puoi stamparlo per verifica.
        print(f"Il raggio del Warp è ora: {val}")
    
        # Puoi usare la variabile di controllo per altri scopi, ma non è necessario
        # aggiornarla qui perché è già aggiornata dal legame 'variable=self.warp_radius'
        
        # ... Inserisci qui la logica per l'effetto Warp ...
        
        # Questa riga era la causa dell'errore precedente e ora non serve più:
        # self.warp_radius.set(val)
                
    def open_image(self,file_path=None):
        if self.camera_active:
            self.stop_camera()
        
        if not file_path:
    # Se nessun percorso è stato passato, apri la finestra di dialogo
           # filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("All Files", "*.*")]
            filetypes = [("Tutti i File Immagine", "*.jpg *.jpeg *.png *.webp *.svg"),
                            ("Vettoriale", "*.svg","*.ai"),
                            ("Raster (JPG, PNG, ecc.)", "*.jpg *.jpeg *.png *.webp"),
                            ("Tutti i file", "*.*")]
            file_path = filedialog.askopenfilename(filetypes=filetypes)
        
        if file_path:
            
            try:
        # La tua logica esistente per caricare e processare l'immagine
                self.load_image(file_path)
            except Exception as e:
                self.update_status_bar(f"Errore: {e}")
 
    def load_image(self, file_path):
        try:
            pil_image = Image.open(file_path)
            if pil_image.mode not in ("RGB", "RGBA"):
                pil_image = pil_image.convert("RGB")
                
            self.original_image_full = pil_image.copy() # L'ORIGINALE PULITA VIENE SALVATA QUI
            self.original_image_for_warp = pil_image.copy()
            self.image = pil_image.copy()
            self.original_color_image = pil_image.copy()

            self.current_image_path = file_path
            self.zoom_level = 1.0
            self.blur_radius = 0
            self.alpha_level = 1.0
            self.gpu_accelerated_active = False 

            self.is_grayscale_active.set(False) 
            self.display_image()
            self.update_status_bar()
            self.hide_canvas_message()
            #GESTIONE Formato SVG
            if file_path:
                # Ottieni l'estensione del file in minuscolo
                ext = file_path.lower().split('.')[-1]
        
                if ext == 'svg':
                    try:
                        # *** INIZIO LOGICA SVG ***
                        
                        # Rasterizza il file SVG in un formato PNG binario in memoria
                        svg_data = open(file_path, 'rb').read()
                        png_output = BytesIO()
                        
                        # Usa cairosvg per la conversione
                        # Riduci l'output se necessario, o usa un'altra logica per la dimensione
                        cairosvg.svg2png(bytestring=svg_data, write_to=png_output, scale=3.0) 
                        
                        # Pillow può leggere i dati PNG binari da BytesIO
                        img = Image.open(png_output)
                        
                        # *** FINE LOGICA SVG ***
        
                    except Exception as e:
                        self.update_status_bar(f"Errore nella rasterizzazione SVG: {e}")
                        print(f"Errore nella rasterizzazione SVG: {e}")
                      
                        return
        
                else:
                        # Logica esistente per tutti gli altri formati raster (JPG, PNG, WEBP, ecc.)
                        try:
                            img = Image.open(file_path)
                        except Exception as e:
                            self.update_status_bar(f"Errore nell'apertura del file raster: {e}")
                            print(f"Errore nell'apertura del file raster: {e}")
                            
                            return
            
        except Exception as e:
            messagebox.showerror("Errore Caricamento Immagine", f"Non è stato possibile caricare l'immagine: {e}")
            self.image = None
            self.original_image_full = None
            self.original_image_for_warp = None
            self.original_color_image = None
            self.current_image_path = None
            self.gpu_accelerated_active = False 
            self.display_image()
            self.update_status_bar()
            self.show_canvas_message("Errore nel caricamento. Riprova.")
            
    def resize_image(self, event):
        # Ignora l'evento se non c'è un'immagine caricata
        if self.original_image_full is None:
            return
    
        # Evita il ricalcolo se l'evento è solo un cambio di posizione (non di dimensione)
        if event.widget == self.master and event.width == self.last_width and event.height == self.last_height:
            return
        
        # Aggiorna le ultime dimensioni
        self.last_width = event.width
        self.last_height = event.height
        
        # 1. Calcola le dimensioni disponibili per il canvas
        # Assumiamo che il canvas occupi tutto lo spazio rimanente
        # Togli l'area occupata dai controlli laterali (self.controls_width)
        new_canvas_width = event.width - self.controls_width 
        new_canvas_height = event.height - self.status_bar_height # Togli la barra di stato
        
        if new_canvas_width <= 0 or new_canvas_height <= 0:
            return
    
        # 2. Ottieni l'aspect ratio dell'immagine originale
        original_width, original_height = self.original_image_full.size
        aspect_ratio = original_width / original_height
    
        # 3. Calcola il nuovo ridimensionamento mantenendo l'aspect ratio
        # Opzione A: Adatta alla larghezza disponibile
        width_fit = int(new_canvas_width)
        height_fit = int(new_canvas_width / aspect_ratio)
    
        # Opzione B: Adatta all'altezza disponibile
        if height_fit > new_canvas_height:
            height_fit = int(new_canvas_height)
            width_fit = int(new_canvas_height * aspect_ratio)
    
        # 4. Ridimensiona l'immagine (solo se le dimensioni sono positive)
        if width_fit > 0 and height_fit > 0:
            self.image = self.original_image_full.resize((width_fit, height_fit), Image.LANCZOS)
            
            # Aggiorna le dimensioni del canvas per adattarsi all'immagine
            self.canvas.config(width=width_fit, height=height_fit)
            
            # Ridisegna l'immagine sul canvas
            self.display_image()
    
    def show_canvas_message(self, message):
        if self.canvas_message_id:
            self.canvas.delete(self.canvas_message_id)
        
        self.canvas.update_idletasks()
        cx = self.canvas.winfo_width() / 2
        cy = self.canvas.winfo_height() / 2

        self.canvas_message_id = self.canvas.create_text(
            cx, cy, 
            text=message, 
            fill="gray", 
            font=("Helvetica", 16, "bold"), 
            justify=tk.CENTER, 
            width=self.canvas.winfo_width() - 20 
        )

    def hide_canvas_message(self):
        if self.canvas_message_id:
            self.canvas.delete(self.canvas_message_id)
            self.canvas_message_id = None
            
    def display_image(self, img_to_display=None):
        self.hide_canvas_message() 

        if img_to_display is None:
            if self.image:
                base_image = self.image
            elif self.camera_active and self.current_camera_frame:
                base_image = self.current_camera_frame
            else:
                self.canvas.itemconfig(self.image_label, image="")
                self.tk_image = None
                self.show_canvas_message("Nessuna immagine selezionata. Clicca su 'APRI' o 'ATTIVA FOTOCAMERA'") 
                return
        else:
            base_image = img_to_display

        frame_width = self.canvas.winfo_width()
        frame_height = self.canvas.winfo_height()

        if frame_width == 0 or frame_height == 0:
            self.master.after(10, lambda: self.display_image(img_to_display))
            return

        img_width, img_height = base_image.size
        
        display_width = int(img_width * self.zoom_level)
        display_height = int(img_height * self.zoom_level)

        if display_width == 0 or display_height == 0:
            self.show_canvas_message("Immagine troppo piccola per essere visualizzata.")
            return

        scale_w = frame_width / display_width
        scale_h = frame_height / display_height
        scale = min(scale_w, scale_h)

        if scale > 1.0 and self.zoom_level >= 1.0:
             final_display_width = display_width
             final_display_height = display_height
        else:
            final_display_width = int(display_width * scale)
            final_display_height = int(display_height * scale)

        if final_display_width <= 0: final_display_width = 1
        if final_display_height <= 0: final_display_height = 1

        try:
            resized_image = base_image.resize((final_display_width, final_display_height), Image.LANCZOS)
        except ValueError:
            print(f"Warning: Invalid image size after resize attempt ({final_display_width}, {final_display_height}). Skipping resize.")
            resized_image = base_image
        
        if self.blur_radius > 0:
            resized_image = resized_image.filter(ImageFilter.GaussianBlur(self.blur_radius))

        if self.alpha_level < 1.0:
            # Crea un'immagine di sfondo bianca per la trasparenza (simulando alpha su RGB)
            background = Image.new("RGB", resized_image.size, (255, 255, 255))
            resized_image = Image.blend(background, resized_image, self.alpha_level)

        self.tk_image = ImageTk.PhotoImage(resized_image)
        
        x_pos = (frame_width - final_display_width) / 2
        y_pos = (frame_height - final_display_height) / 2
        self.canvas.coords(self.image_label, x_pos, y_pos)
        self.canvas.itemconfig(self.image_label, image=self.tk_image)

    def close_image(self):
        self.image = None
        self.original_image_full = None
        self.original_image_for_warp = None
        self.original_color_image = None
        self.tk_image = None
        self.current_image_path = None
        self.zoom_level = 1.0
        self.blur_radius = 0
        self.alpha_level = 1.0
        self.is_grayscale_active.set(False)
        self.gpu_accelerated_active = False 
        self.final_image=None
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = None
        self.start_x = None
        self.start_y = None

        self.display_image()
        self.update_status_bar()
        self.update_warp_status()
        self._stop_warp_sound()
        
        if self.camera_active:
            self.stop_camera()

    def zoom_in(self):
        if self.image:
            self.zoom_level *= 1.25
            self.gpu_accelerated_active = False 
            self.display_image()
            self.update_status_bar()
        else: 
            self.show_canvas_message("Carica un'immagine per zoomare.")

    def zoom_out(self):
        if self.image:
            self.zoom_level /= 1.25
            if self.zoom_level < 0.05:
                self.zoom_level = 0.05
            self.gpu_accelerated_active = False 
            self.display_image()
            self.update_status_bar()
        else: 
            self.show_canvas_message("Carica un'immagine per zoomare.")

    def restore_original_image(self):
        if self.original_image_full:
            self.image = self.original_image_full.copy()
            self.original_image_for_warp = self.original_image_full.copy()
            self.original_color_image = self.original_image_full.copy()
            self.zoom_level = 1.0
            self.blur_radius = 0
            self.alpha_level = 1.0
            self.is_grayscale_active.set(False) # Resetta anche la modalità colore
            self.gpu_accelerated_active = False # Resetta lo stato GPU
            
            # Applica la scala iniziale se l'immagine è troppo grande per il canvas
            # Questo è già gestito da display_image, che ridimensiona per adattarsi.
            self.display_image()
            self.update_status_bar("Immagine originale ripristinata.")
        else:
            self.show_canvas_message("Nessuna immagine originale da ripristinare.")


    def reset_zoom(self):
        # Questo metodo è simile a restore_original_image ma è chiamato "reset_zoom"
        # e le sue descrizioni non sono coerenti con l'effetto completo di "reset"
        # che invece è coperto da `restore_original_image`.
        # Se intendevi un reset che non tocca blur/alpha, andrebbe modificato.
        # Per ora, lo lascio come un reset parziale (solo zoom, blur, alpha).
        if self.original_image_full:
            # Reset solo di zoom, blur, alpha sul *current* self.image
            # Se vuoi ripartire dall'originale, usa self.restore_original_image
            # o imposta self.image = self.original_image_full.copy() qui.
            self.image = self.original_image_full.copy() # Lo imposto come un reset completo come il tuo `restore_original_image`
            self.original_image_for_warp = self.original_image_full.copy()
            self.original_color_image = self.original_image_full.copy()

            self.zoom_level = 1.0
            self.blur_radius = 0
            self.alpha_level = 1.0
            self.gpu_accelerated_active = False 
            
            if self.is_grayscale_active.get():
                self.image = self.image.convert("L").convert("RGB") 
            
            self.display_image()
            self.update_status_bar("Zoom, blur e alpha resettati.") # Modificato per riflettere il reset
        else:
            self.show_canvas_message("Nessuna immagine da ripristinare per lo zoom.")


    def blur_plus(self):
        if self.image:
            self.blur_radius += 1
            if self.blur_radius > 10: self.blur_radius = 10
            self.gpu_accelerated_active = False 
            self.display_image()
            self.update_status_bar(f"Blur: {self.blur_radius}")
        else:
            self.show_canvas_message("Carica un'immagine per applicare il blur.")

    def blur_minus(self):
        if self.image:
            self.blur_radius -= 1
            if self.blur_radius < 0: self.blur_radius = 0
            self.gpu_accelerated_active = False 
            self.display_image()
            self.update_status_bar(f"Blur: {self.blur_radius}")
        else:
            self.show_canvas_message("Carica un'immagine per applicare il blur.")

    def rotate_right(self):
        if self.image:
            self.image = self.image.rotate(-90, expand=True) 
            
            if self.original_image_for_warp: 
                self.original_image_for_warp = self.original_image_for_warp.rotate(-90, expand=True) 
            if self.original_image_full:
                self.original_image_full = self.original_image_full.rotate(-90, expand=True)
            if self.original_color_image:
                self.original_color_image = self.original_color_image.rotate(-90, expand=True)
            
            self.gpu_accelerated_active = False 
            self.display_image()
            self.update_status_bar("Ruotato di 90° a destra.")
        else:
            self.show_canvas_message("Carica un'immagine per ruotare.")

    def rotate_left(self):
        if self.image:
            self.image = self.image.rotate(90, expand=True) 
            
            if self.original_image_for_warp: 
                self.original_image_for_warp = self.original_image_for_warp.rotate(90, expand=True)
            if self.original_image_full:
                self.original_image_full = self.original_image_full.rotate(90, expand=True)
            if self.original_color_image:
                self.original_color_image = self.original_color_image.rotate(90, expand=True)

            self.gpu_accelerated_active = False 
            self.display_image()
            self.update_status_bar("Ruotato di 90° a sinistra.")
        else:
            self.show_canvas_message("Carica un'immagine per ruotare.")

    def alpha_plus(self):
        if self.image:
            self.alpha_level += 0.1
            if self.alpha_level > 1.0: self.alpha_level = 1.0
            self.gpu_accelerated_active = False 
            self.display_image()
            self.update_status_bar(f"Opacità (Alpha): {self.alpha_level:.1f}")
        else:
            self.show_canvas_message("Carica un'immagine per regolare l'opacità.")

    def alpha_minus(self):
        if self.image:
            self.alpha_level -= 0.1
            if self.alpha_level < 0.0: self.alpha_level = 0.0
            self.gpu_accelerated_active = False 
            self.display_image()
            self.update_status_bar(f"Opacità (Alpha): {self.alpha_level:.1f}")
        else:
            self.show_canvas_message("Carica un'immagine per regolare l'opacità.")

    def update_status_bar(self, message=None):
        grayscale_status = "B/N" if self.is_grayscale_active.get() else "Colori"
        gpu_status = f" | GPU: {'ON' if self.gpu_accelerated_active else 'OFF (CPU)'}" if self.device.type != 'cpu' else " | GPU: N/A (CPU Mode)"
        
        if message:
            self.status_bar.config(text=message + gpu_status)
        elif self.image:
            _, file_extension = os.path.splitext(self.current_image_path) if self.current_image_path else ("", "")
            self.status_bar.config(text=f"Immagine: {os.path.basename(self.current_image_path) if self.current_image_path else 'N/A'} "
                                         f"({self.image.width}x{self.image.height}px) | "
                                         f"dimensione in KB: ({self.image.size}| "
                                         f"Zoom: {self.zoom_level:.2f}x | Blur: {self.blur_radius} | "
                                         f"Alpha: {self.alpha_level:.1f} | "
                                         f"Warp: {'ON' if self.warp_active else 'OFF'} | "
                                         f"Colore: {grayscale_status}"
                                         f"{gpu_status}") 
        
        elif self.camera_active:
            
             self.status_bar.config(text="Fotocamera attiva..." + gpu_status)
        else:
            self.status_bar.config(text="Nessuna immagine caricata." + gpu_status)

    def update_warp_status(self):
        status = "ON" if self.warp_active else "OFF"
        self.warp_toggle_button.config(text=f"Warp: {status}")
        self.warp_status_bar.config(text=f"Warp: {status}")
        if self.warp_active:
            self.warp_status_bar.config(bg="lightcoral", fg="darkred")
        else:
            self.warp_status_bar.config(bg="lightblue", fg="darkblue")

    def toggle_camera(self):
        if not self.camera_active:
            self.start_camera()
        else:
            self.stop_camera()

    def start_camera(self):
        if self.image:
            self.close_image()
            
        self.camera_capture = cv2.VideoCapture(0)
        if not self.camera_capture.isOpened():
            messagebox.showerror("Errore Fotocamera", "Impossibile accedere alla fotocamera. Controlla che non sia già in uso e i permessi.")
            self.camera_active = False
            self.take_photo_button.config(state=tk.DISABLED)
            self.show_canvas_message("Fotocamera non disponibile.")
            return

        self.camera_active = True
        self.take_photo_button.config(state=tk.NORMAL)
        self.stop_camera_thread.clear()
        self.hide_canvas_message()
        self.gpu_accelerated_active = False 

        self.camera_thread = threading.Thread(target=self._camera_capture_loop)
        self.camera_thread.daemon = True
        self.camera_thread.start()

        self._update_camera_feed()

    def _camera_capture_loop(self):
        while not self.stop_camera_thread.is_set():
            ret, frame = self.camera_capture.read()
            if not ret:
                print("Errore nella lettura del frame dalla fotocamera.")
                self.show_canvas_message("Errore feed fotocamera.")
                break
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_camera_frame = Image.fromarray(frame_rgb)
        
        if self.camera_capture:
            self.camera_capture.release()
            print("Fotocamera rilasciata.")

    def _update_camera_feed(self):
        if self.camera_active and self.current_camera_frame:
            self.display_image(self.current_camera_frame)

        if self.camera_active:
            self.master.after(10, self._update_camera_feed)
        else:
            self.show_canvas_message("Nessuna immagine selezionata. Clicca su 'APRI' o 'ATTIVA FOTOCAMERA'")

    def stop_camera(self):
        if self.camera_active:
            self.camera_active = False
            self.stop_camera_thread.set()
            
            if self.camera_thread and self.camera_thread.is_alive():
                self.camera_thread.join(timeout=1.0)

            self.take_photo_button.config(state=tk.DISABLED)
            self.canvas.itemconfig(self.image_label, image="")
            self.tk_image = None
            self.current_camera_frame = None
            self.gpu_accelerated_active = False 
            print("Fotocamera disattivata.")
            self.show_canvas_message("Fotocamera disattivata.")

    def take_photo(self):
        if self.camera_active and self.current_camera_frame:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                photo_filename = f"scatto_{timestamp}.png"
                save_path = os.path.join(script_dir, photo_filename)

                self.stop_camera() 
                self.current_camera_frame.save(save_path)
                self.load_image(save_path)
                messagebox.showinfo("Successo", f"Foto salvata e caricata come: {photo_filename}")
            except Exception as e:
                messagebox.showerror("Errore Salvataggio", f"Impossibile salvare la foto: {e}")
        else:
            self.show_canvas_message("La fotocamera non è attiva o non ci sono frame da scattare.")
    
    def on_closing(self):
        self.stop_camera()
        self._stop_warp_sound()
        self.master.destroy()

    def on_mouse_down(self, event):
        if self.image and not self.camera_active and self.zoom_box_active and not self.warp_active:
            self.start_x = event.x
            self.start_y = event.y
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", dash=(4, 2), width=2)
            self.gpu_accelerated_active = False 
            self.update_status_bar()
        elif not self.image:
            self.show_canvas_message("Carica un'immagine per utilizzare gli strumenti.")
    
    def on_mouse_drag(self, event):
        if self.rect_id and self.image and not self.camera_active and self.zoom_box_active and not self.warp_active:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_mouse_up(self, event):
        if self.rect_id and self.image and not self.camera_active and self.zoom_box_active and not self.warp_active:
            end_x, end_y = event.x, event.y

            self.canvas.delete(self.rect_id)
            self.rect_id = None

            x1 = min(self.start_x, end_x)
            y1 = min(self.start_y, end_y)
            x2 = max(self.start_x, end_x)
            y2 = max(self.start_y, end_y)

            if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
                self.show_canvas_message("Area di selezione troppo piccola per lo zoom. Selezionare un'area più grande.")
                self.display_image()
                self.start_x = None
                self.start_y = None
                return

            current_image_tk_width = self.tk_image.width()
            current_image_tk_height = self.tk_image.height()
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            x_offset = (canvas_width - current_image_tk_width) / 2
            y_offset = (canvas_height - current_image_tk_height) / 2

            relative_x1 = x1 - x_offset
            relative_y1 = y1 - y_offset
            relative_x2 = x2 - x_offset
            relative_y2 = y2 - y_offset

            relative_x1 = max(0, relative_x1)
            relative_y1 = max(0, relative_y1)
            relative_x2 = min(current_image_tk_width, relative_x2)
            relative_y2 = min(current_image_tk_height, relative_y2)

            current_displayed_image_pixel_width, current_displayed_image_pixel_height = self.image.size
            
            scale_to_original_x = current_displayed_image_pixel_width / current_image_tk_width
            scale_to_original_y = current_displayed_image_pixel_height / current_image_tk_height

            crop_x1 = int(relative_x1 * scale_to_original_x)
            crop_y1 = int(relative_y1 * scale_to_original_y)
            crop_x2 = int(relative_x2 * scale_to_original_x)
            crop_y2 = int(relative_y2 * scale_to_original_y)
            
            crop_x1 = max(0, crop_x1)
            crop_y1 = max(0, crop_y1)
            crop_x2 = min(current_displayed_image_pixel_width, crop_x2)
            crop_y2 = min(current_displayed_image_pixel_height, crop_y2)

            if crop_x2 <= crop_x1 or crop_y2 <= crop_y1:
                self.show_canvas_message("Area di crop invalida o troppo piccola per lo zoom. Riprova.")
                self.display_image()
                self.start_x = None
                self.start_y = None
                return

            try:
                self.image = self.image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
                self.zoom_level = 1.0
                
                # Aggiorna la base colore e la base warp non-GPU con l'immagine croppata
                if self.original_color_image:
                    self.original_color_image = self.original_color_image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
                else: 
                     self.original_color_image = self.image.copy()

                self.original_image_for_warp = self.image.copy() 

                self.gpu_accelerated_active = False 
                self.display_image()
                self.update_status_bar(f"Zoom applicato all'area: ({crop_x1}, {crop_y1}) - ({crop_x2}, {crop_y2})")
            except Exception as e:
                messagebox.showerror("Errore Zoom", f"Impossibile applicare lo zoom: {e}") 
                self.display_image()
            
            self.start_x = None
            self.start_y = None

    def toggle_warp(self):
        if not self.image:
            self.show_canvas_message("Carica un'immagine per attivare l'effetto Warp.")
            return

        self.warp_active = not self.warp_active
        if self.warp_active:
            self.update_status_bar("Warp attivo. Clicca e trascina sull'immagine.")
            self._play_warp_sound()
            self.canvas.bind('<Button-1>', self._start_warp)
            self.canvas.bind('<B1-Motion>', self._apply_warp)
            self.canvas.bind('<ButtonRelease-1>', self._end_warp)
            self.zoom_box_active = False
            self.color_radio.config(state=tk.DISABLED)
            self.bw_radio.config(state=tk.DISABLED)
            self.gpu_accelerated_active = (self.device.type != 'cpu') 
        else:
            self.update_status_bar("Warp disattivato.")
            self._stop_warp_sound()
            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<B1-Motion>')
            self.canvas.unbind('<ButtonRelease-1>')
            self.canvas.bind('<Button-1>', self.on_mouse_down)
            self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
            self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
            
            if self.original_color_image:
                self.image = self.original_color_image.copy()
            
            if self.is_grayscale_active.get():
                self.image = self.image.convert("L").convert("RGB")

            self.gpu_accelerated_active = False 
            self.display_image()

            self.zoom_box_active = True
            self.color_radio.config(state=tk.NORMAL)
            self.bw_radio.config(state=tk.NORMAL)
        self.update_warp_status() 
        self.update_status_bar() 

    def _play_warp_sound(self):
        if not self.sound_playing:
            self.sound_playing = True
            self.sound_thread = threading.Thread(target=self._play_sound_loop)
            self.sound_thread.daemon = True
            self.sound_thread.start()


    def _play_sound_loop(self):
        """Riproduce il suono del warp in un loop finché self.sound_playing è True."""
        while self.sound_playing:
            try:
                playsound(self.warp_sound_path)
            except Exception as e:
                print(f"Errore nella riproduzione del suono warp: {e}")
                self.sound_playing = False # Ferma il loop in caso di errore
                break
            # Breve pausa per non sovraccaricare, se il suono è molto corto
            # o se vuoi che si ripeta con un piccolo intervallo.
            # Se il suono è lungo, non è necessario un time.sleep aggiuntivo.
            time.sleep(0.1) 

    def _stop_warp_sound(self):
        self.sound_playing = False
        if self.sound_thread and self.sound_thread.is_alive():
            # Aspetta che il thread del suono termini (se non è bloccato da playsound)
            # playsound può bloccare, quindi l'arresto non è sempre immediato.
            pass # Non fare join qui per non bloccare l'UI

    def _start_warp(self, event):
        if self.image:
            # Converte le coordinate del canvas in coordinate dell'immagine originale
            x_canvas, y_canvas = event.x, event.y
            img_x_offset = (self.canvas.winfo_width() - self.tk_image.width()) / 2
            img_y_offset = (self.canvas.winfo_height() - self.tk_image.height()) / 2

            x_tk_img = x_canvas - img_x_offset
            y_tk_img = y_canvas - img_y_offset

            # Scala le coordinate Tkinter alla dimensione dell'immagine originale PIL
            scale_x = self.image.width / self.tk_image.width()
            scale_y = self.image.height / self.tk_image.height()

            x_img = int(x_tk_img * scale_x)
            y_img = int(y_tk_img * scale_y)

            # Assicurati che le coordinate siano all'interno dei limiti dell'immagine
            x_img = max(0, min(x_img, self.image.width - 1))
            y_img = max(0, min(y_img, self.image.height - 1))
            
            # Salva la posizione iniziale del mouse per le operazioni di trascinamento
            self.last_warp_point = (x_img, y_img)

            # Prepara l'immagine originale per il warp (copia per GPU o CPU)
            if self.gpu_accelerated_active:
                # Se la GPU è attiva, converti l'immagine PIL in un tensore PyTorch
                # e spostala sul dispositivo GPU (MPS/CUDA).
                # Solo se non è già stata convertita o se l'immagine è cambiata.
                if self.original_image_for_warp_tensor is None or self.original_image_for_warp.size != self.image.size:
                    np_img = np.array(self.original_color_image.convert("RGB")) / 255.0
                    self.original_image_for_warp_tensor = torch.tensor(np_img, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0).to(self.device)
                self.current_gpu_warped_image_tensor = self.original_image_for_warp_tensor.clone() # Clona per le modifiche
            else:
                self.original_image_for_warp = self.image.copy() # Per il warp CPU, lavoriamo sulla copia corrente dell'immagine

            # Applica il warp immediatamente al click iniziale per mostrare l'effetto
            self._apply_warp(event)
        else:
            self.show_canvas_message("Carica un'immagine per applicare il warp.")

    def _apply_warp(self, event):
        if self.warp_active and self.image:
            x_canvas, y_canvas = event.x, event.y
            img_x_offset = (self.canvas.winfo_width() - self.tk_image.width()) / 2
            img_y_offset = (self.canvas.winfo_height() - self.tk_image.height()) / 2

            x_tk_img = x_canvas - img_x_offset
            y_tk_img = y_canvas - img_y_offset

            scale_x = self.image.width / self.tk_image.width()
            scale_y = self.image.height / self.tk_image.height()

            x_img = int(x_tk_img * scale_x)
            y_img = int(y_tk_img * scale_y)
            
            # Assicurati che le coordinate siano all'interno dei limiti dell'immagine
            x_img = max(0, min(x_img, self.image.width - 1))
            y_img = max(0, min(y_img, self.image.height - 1))

            if self.gpu_accelerated_active:
                self._apply_warp_gpu(x_img, y_img)
            else:
                self._apply_warp_cpu(x_img, y_img)
            self.update_status_bar()

    def _end_warp(self, event):
        # Quando il mouse viene rilasciato, l'immagine corrente diventa la nuova base per future modifiche
        if self.warp_active and self.image:
            # Se stiamo usando la GPU, dobbiamo convertire l'immagine warappata dal tensore
            # di nuovo in un'immagine PIL e assegnarla a self.image.
            if self.gpu_accelerated_active and self.current_gpu_warped_image_tensor is not None:
                img_array = self.current_gpu_warped_image_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
                self.image = Image.fromarray((img_array * 255).astype(np.uint8))
                self.original_image_for_warp_tensor = None # Resetta per ricaricare alla prossima attivazione del warp
            
            # Aggiorna anche l'immagine "originale a colori" che viene usata per il toggle B/N
            self.original_color_image = self.image.copy()
            # E l'immagine per il warp non-GPU
            self.original_image_for_warp = self.image.copy()
            
            self.display_image() # Aggiorna la visualizzazione finale
            self.update_status_bar("Warp applicato e finalizzato.")
        self.last_warp_point = None

    def _apply_warp_cpu(self, x, y):
        # Placeholder: Questa è l'implementazione del warp via CPU
        # Devi integrare qui la tua logica di warp.
        # Questo è un esempio molto semplificato di "pinch" o "bulge".
        if self.original_image_for_warp is None:
            self.original_image_for_warp = self.image.copy()

        img_np = np.array(self.original_image_for_warp)
        h, w, c = img_np.shape
        
        # Crea una mesh di coordinate
        coords = np.indices((h, w)).astype(np.float32)
        cy, cx = coords[0], coords[1]
        
        # Calcola la distanza dal punto centrale (x, y)
        dist_sq = (cx - x)**2 + (cy - y)**2
        
        # Maschera per l'area di effetto
        mask = dist_sq < self.warp_radius**2
        
        # Normalizza la distanza per il calcolo della forza
        normalized_dist = np.sqrt(dist_sq) / self.warp_radius
        normalized_dist[normalized_dist > 1] = 1 # Clampa a 1
        
        # Calcola il fattore di distorsione (inverso della distanza per effetto lente)
        # Il fattore di distorsione è massimo al centro e diminuisce verso il bordo
        # strength viene applicato in modo inverso per "magnify"
        # 1 - normalized_dist fa sì che sia 1 al centro e 0 al bordo
        # (1 - normalized_dist)**2 rende la transizione più morbida
        # Il self.warp_strength controlla quanto è forte l'ingrandimento
        distortion_factor = (1 - normalized_dist)**2 * self.warp_strength

        # Calcola lo spostamento delle coordinate
        delta_x = (cx - x) * distortion_factor
        delta_y = (cy - y) * distortion_factor

        # Applica lo spostamento, ma in direzione opposta per "ingrandire"
        # O per "spostare" i pixel verso il centro
        new_cx = cx - delta_x
        new_cy = cy - delta_y

        # Limita le nuove coordinate ai bordi dell'immagine
        new_cx = np.clip(new_cx, 0, w - 1)
        new_cy = np.clip(new_cy, 0, h - 1)
        
        # Usa remap di OpenCV per applicare la distorsione
        # Assicurati che new_cx e new_cy siano di tipo float32
        warped_img_np = cv2.remap(img_np, new_cx.astype(np.float32), new_cy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        
        self.image = Image.fromarray(warped_img_np.astype(np.uint8))
        self.display_image()

    def _apply_warp_gpu(self, x, y):
        # Placeholder: Questa è l'implementazione del warp via GPU (PyTorch)
        # Devi integrare qui la tua logica di warp PyTorch.
        # Questo è un esempio di "bulge" o "pinch" usando PyTorch.
        if self.original_image_for_warp_tensor is None:
            # Prepara il tensore dell'immagine se non è già pronto
            np_img = np.array(self.original_color_image.convert("RGB")) / 255.0
            self.original_image_for_warp_tensor = torch.tensor(np_img, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0).to(self.device)
        
        # Clona l'originale per non modificare la base
        img_tensor = self.original_image_for_warp_tensor.clone()
        _, _, H, W = img_tensor.shape

        # Crea una griglia di coordinate normalizzate (-1 a 1)
        # Queste sono le coordinate di output, stiamo cercando dove "prendere" i pixel
        # dalla sorgente per riempire la destinazione.
        grid_x, grid_y = torch.meshgrid(torch.linspace(-1, 1, W, device=self.device), 
                                        torch.linspace(-1, 1, H, device=self.device), indexing='xy')
        grid = torch.stack((grid_x, grid_y), dim=-1) # Shape: (H, W, 2)

        # Converte le coordinate del punto di warp da pixel a normalizzate
        center_x_norm = (x / W) * 2 - 1
        center_y_norm = (y / H) * 2 - 1

        # Calcola la distanza dal centro del warp in coordinate normalizzate
        # Usiamo il raggio in pixel, ma lo normalizziamo per il calcolo della distanza
        # rispetto alle dimensioni normalizzate della griglia.
        # Il raggio normalizzato sarà differente per X e Y se l'immagine non è quadrata,
        # ma per un effetto circolare, è meglio usare un raggio proporzionato alla dimensione minore.
        # Usiamo il raggio in pixel e lo normalizziamo rispetto alla dimensione maggiore
        # o alla media delle dimensioni per coerenza.
        # Per semplicità qui normalizzo rispetto a W (o H), assumendo un raggio circolare.
        radius_norm = (self.warp_radius / min(H, W)) * 2 # Approssimazione per il raggio in spazio normalizzato

        # Calcola la distanza di ogni punto della griglia dal centro del warp
        dist_from_center = torch.sqrt(
            (grid[:, :, 0] - center_x_norm)**2 + 
            (grid[:, :, 1] - center_y_norm)**2
        )

        # Crea una maschera per i pixel all'interno del raggio di influenza
        # Utilizza un raggio normalizzato per la maschera
        mask = dist_from_center < radius_norm

        # Calcola il fattore di distorsione
        # Vogliamo un effetto "ingrandimento", quindi i pixel vicino al centro si spostano meno
        # e quelli più lontani si spostano di più verso il centro (o l'originale)
        
        # Questa formula sposta i pixel dal centro verso l'esterno, creando un "bulge".
        # Per un effetto "lente d'ingrandimento" (pinch/ingrandimento al centro),
        # i pixel all'interno del raggio devono essere spostati *verso* il centro.
        # Un modo per farlo è calcolare il punto di origine inverso.
        
        # Calcola la "magnification factor" che è più forte al centro e diminuisce verso il bordo
        # (1 - (dist_from_center / radius_norm)) è 1 al centro, 0 al bordo.
        # Elevando a potenza si controlla la curva di attenuazione.
        magnification_factor = (1 - (dist_from_center / radius_norm)).pow(2) * self.warp_strength
        magnification_factor = magnification_factor * mask.float() # Applica solo nell'area di interesse

        # Sposta le coordinate dei pixel.
        # Per ingrandire, i pixel che stiamo *campionando* (quelli della griglia di lookup)
        # devono essere "schiacciati" verso il centro.
        # (original_coord - center_coord) è la distanza dal centro.
        # Moltiplicare per (1 - factor) li avvicina al centro.
        
        warped_grid_x = center_x_norm + (grid[:, :, 0] - center_x_norm) * (1 - magnification_factor)
        warped_grid_y = center_y_norm + (grid[:, :, 1] - center_y_norm) * (1 - magnification_factor)

        warped_grid = torch.stack((warped_grid_x, warped_grid_y), dim=-1).unsqueeze(0) # Aggiunge la dimensione batch

        # Applica la griglia warappata all'immagine originale
        # grid_sample richiede input NCHW e grid N H W 2
        warped_tensor = F.grid_sample(img_tensor, warped_grid, mode='bilinear', padding_mode='reflection', align_corners=True)

        # Aggiorna l'immagine visualizzata
        img_array = warped_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
        self.image = Image.fromarray((img_array * 255).astype(np.uint8))
        self.current_gpu_warped_image_tensor = warped_tensor # Salva per il trascinamento continuo

        self.display_image()


    def on_grayscale_selection(self):
        if self.image is None and not self.camera_active:
            # Se non c'è un'immagine caricata e non è attiva la fotocamera,
            # non fare nulla ma potresti voler mostrare un messaggio.
            # self.show_canvas_message("Carica un'immagine prima di cambiare modalità colore.")
            return

        if self.warp_active:
            # Se il warp è attivo, blocchiamo il cambio di colore
            self.is_grayscale_active.set(not self.is_grayscale_active.get()) # Reset dello stato precedente
            messagebox.showinfo("Avviso", "La modalità colore non può essere cambiata mentre il Warp è attivo.")
            return

        if self.is_grayscale_active.get():
            # Passa a bianco e nero
            if self.image:
                # Usa self.original_color_image come base per convertire in B/N
                # Questo assicura che il B/N sia sempre basato sull'immagine a colori originale
                # o sulla sua ultima versione modificata non-warp.
                self.image = self.original_color_image.convert("L").convert("RGB")
        else:
            # Passa a colori (ripristina l'immagine a colori originale)
            if self.image:
                self.image = self.original_color_image.copy()

        self.gpu_accelerated_active = False # Reset GPU status on color mode change
        self.display_image()
        self.update_status_bar()
        
    

    def handle_mouse_motion(self, event):
        if self.image:
            # Qui puoi aggiungere logica per mostrare coordinate o altre info
            # print(f"Mouse at: {event.x}, {event.y}")
            pass

    def handle_mouse_leave(self, event):
        # Azioni quando il mouse lascia il canvas (es. nascondere informazioni)
        pass
    
    def update_cartoonize(self, new_value):
        if self.original_image_full is None:
            return
    
        val = float(new_value)
        if val == 0:
            self.image = self.original_image_full.copy()
            self.show_image()
            return
        
        # Livelli discreti (1, 2, 3)
        level = int(val / 33) + 1
        
        # Converti in BGR
        img_bgr = cv2.cvtColor(np.array(self.original_image_full.convert("RGB")), cv2.COLOR_RGB2BGR)
    
        # --- 1. PRE-PROCESSING: KILL GRANULARITY ---
        # Usiamo un Median Blur potente per rimuovere ogni grana
        # Il kernel deve essere dispari e aumenta col livello
        k_size = 7 + (level * 2) 
        smoothed = cv2.medianBlur(img_bgr, k_size)
    
        # --- 2. SCHIARIMENTO E TONI ANNI '80 (HSV space) ---
        hsv = cv2.cvtColor(smoothed, cv2.COLOR_BGR2HSV).astype("float32")
        # Aumentiamo la Saturazione (S) e il Valore/Luminosità (V)
        hsv[:, :, 1] *= 1.4  # Colori più "vivi" alla Sampei
        hsv[:, :, 2] *= 1.2  # Schiarisce l'immagine senza "bruciarla"
        hsv = np.clip(hsv, 0, 255).astype("uint8")
        img_bright = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
        # --- 3. QUANTIZZAZIONE COLORE (K-Means per Tinte Piatte) ---
        # Per Lady Oscar vogliamo pochissimi colori (3 o 4 al massimo per area)
        k_colors = 7 - level 
        data = img_bright.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, label, center = cv2.kmeans(data, k_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        center = np.uint8(center)
        res = center[label.flatten()]
        img_flat = res.reshape((img_bright.shape))
    
        # --- 4. MORFOLOGIA (Unifica le "Hatch") ---
        # Elimina i rimasugli di pixel isolati fondendoli nella massa cromatica
        kernel_morph = np.ones((5, 5), np.uint8)
        img_flat = cv2.morphologyEx(img_flat, cv2.MORPH_OPEN, kernel_morph)
    
        # --- 5. BORDI SOTTILI (Inchiostrazione) ---
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(
            cv2.medianBlur(gray, 5), 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Rendiamo i bordi un po' meno pesanti per l'effetto 2D
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # --- 6. COMBINAZIONE FINALE ---
        # Applichiamo i bordi neri sulle tinte piatte schiarite
        img_final = cv2.bitwise_and(img_flat, edges)
    
        # Ritorno a PIL
        self.image = Image.fromarray(cv2.cvtColor(img_final, cv2.COLOR_BGR2RGB))
        self.show_image()
           
            
    
    def remove_ai_background(self):
        if self.image is None:
            self.show_canvas_message("Carica un'immagine per rimuovere lo sfondo.")
            return

        self.update_status_bar("Rimuovendo lo sfondo con AI... (potrebbe richiedere qualche istante)")
        self.master.update_idletasks() # Forza l'aggiornamento della UI

        try:
        # Converti PIL Image in bytes per rembg
           img_byte_arr = io.BytesIO()
           self.image.save(img_byte_arr, format='PNG') # PNG supporta l'alpha
           img_byte_arr = img_byte_arr.getvalue()

        # Usa rembg per la rimozione dello sfondo
        # rembg usa modelli ONNX, ma può sfruttare la GPU se onnxruntime-gpu è installato
        # Il parametro `g_model` seleziona il modello. 'u2net' è un buon default.
           output_bytes = remove(img_byte_arr,
                                 alpha_matting=True,
                                 alpha_matting_foreground_threshold=240,
                                 alpha_matting_background_threshold=10, 
                                 alpha_matting_erode_size=11,
                                 # Aggiungi il parametro providers qui:
                                 providers=['CoreMLExecutionProvider', 'CPUExecutionProvider']
                                 )

        # Converti i bytes di nuovo in PIL Image
           output_image = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
 
           self.image = output_image
           self.display_image()
           self.update_status_bar("Sfondo rimosso con AI.")
 
        except Exception as e:
               
            messagebox.showerror("Errore Rimozione Sfondo AI", f"Errore: {e}\nAssicurati di avere `rembg` installato correttamente.")
            self.update_status_bar("Rimozione sfondo AI fallita.")
            
            # richiamo funzione per CARTONIZZARE Assumi che self.original_image sia l'immagine originale (un oggetto PIL)
# e self.display_image() sia la funzione per aggiornare il canvas

 
    def apply_dot_to_dot_Gpu(self):
        if self.original_image_full is None:
            self.show_canvas_message("Carica un'immagine prima.")
            return
    
        # Invia un messaggio immediato sulla barra di stato
        self.crea_puntini_button.config(state=tk.DISABLED)
        self.update_status_bar("Elaborazione in corso... (GPU)")
        
        self.master.update_idletasks()
    
        # Avvia la logica di calcolo in un thread separato
        thread = threading.Thread(target=self._process_dots_on_gpu)
        thread.start()

    def _process_dots_on_gpu(self):
        try:
            # Verifica la disponibilità della GPU (MPS)
            if torch.backends.mps.is_available():
                device = torch.device("mps")
                self.master.after(0, lambda: self.update_status_bar("Utilizzo GPU: SI"))
            else:
                device = torch.device("cpu")
                self.master.after(0, lambda: self.update_status_bar("Utilizzo GPU: NO (CPU)"))
    
            # Conversione da PIL a Tensore PyTorch
             
            img_pil = self.original_image_full.convert("RGB")
            img_np = np.array(img_pil).astype(np.float32) / 255.0
            # Aggiunge una dimensione batch e converte in C x H x W
            img_tensor = torch.from_numpy(img_np).permute(2, 0, 1).unsqueeze(0).to(device)
    
            # 1. Conversione in scala di grigi sulla GPU
            gray_tensor = 0.2989 * img_tensor[:, 0:1, :, :] + 0.5870 * img_tensor[:, 1:2, :, :] + 0.1140 * img_tensor[:, 2:3, :, :]
            
            # 2. Applicazione del filtro Gaussian (sfocatura)
            gaussian_kernel = torch.tensor([
                [1., 2., 1.],
                [2., 4., 2.],
                [1., 2., 1.]
            ]).unsqueeze(0).unsqueeze(0) / 16.0
            gaussian_kernel = gaussian_kernel.to(device)
            
            # Per evitare problemi con i bordi, applichiamo un padding
            blurred_tensor = F.conv2d(gray_tensor, gaussian_kernel, padding=1)
    
            # 3. Rilevamento dei bordi con il filtro Sobel
            sobel_x_kernel = torch.tensor([[-1., 0., 1.], [-2., 0., 2.], [-1., 0., 1.]]).unsqueeze(0).unsqueeze(0).to(device)
            sobel_y_kernel = torch.tensor([[-1., -2., -1.], [0., 0., 0.], [1., 2., 1.]]).unsqueeze(0).unsqueeze(0).to(device)
    
            grad_x = F.conv2d(blurred_tensor, sobel_x_kernel, padding=1)
            grad_y = F.conv2d(blurred_tensor, sobel_y_kernel, padding=1)
            
            # Calcolo della magnitudine del gradiente (l'intensità dei bordi)
            edge_magnitude = torch.sqrt(grad_x**2 + grad_y**2)
    
            # 4. Semplice soglia per trovare i punti dei bordi (al posto di Canny)
            # La soglia può essere regolata a seconda dell'immagine
            threshold = 0.20
            edges_tensor = (edge_magnitude > threshold).squeeze().cpu().detach().numpy()
            
            # 5. Estrazione dei punti sulla CPU
            edge_points = np.argwhere(edges_tensor)
            
            if edge_points.size == 0:
                self.master.after(0, lambda: self.update_status_bar("Nessun bordo rilevato."))
                return
    
            # 6. Campionamento dei punti
            np.random.shuffle(edge_points)
            min_distance_sq = 60**2 
            sampled_points = []
            if len(edge_points) > 0:
                sampled_points.append(edge_points[0])
            
            for point in edge_points:
                is_far_enough = True
                for sampled_point in sampled_points:
                    dist_sq = np.sum((point - sampled_point)**2)
                    if dist_sq < min_distance_sq:
                        is_far_enough = False
                        break
                if is_far_enough:
                    sampled_points.append(point)
    
            # 7. Creazione dell'immagine finale nel thread principale
            final_image = Image.new('RGB', img_pil.size, 'white')
            draw = ImageDraw.Draw(final_image)
    
            for i, (y, x) in enumerate(sampled_points):
                draw.ellipse((x-2, y-2, x+2, y+2), fill='black')
                draw.text((x + 5, y - 5), str(i + 1), fill='black')
            
            self.final_image = final_image
            self.master.after(0, self._finish_dot_to_dot)
           
            

        
        except Exception as e:
            self.master.after(0, lambda: self.update_status_bar(f"Errore:"))
            print("eccezione nel processare i puntini con Pytorch, tensori, algoritmi di Gaussian,Sobel e tensori")
            print(e)
            import traceback
            traceback.print_exc()

    def _finish_dot_to_dot(self):
        self.image = self.final_image
        self.display_image()
        self.update_status_bar(f"Gioco 'Unisci i Puntini' generato con successo!")
        self.crea_puntini_button.config(state=tk.NORMAL) # Assicurati di usare tk.NORMAL, non tk.ENABLED(da errore)

        
        
        # NON FUNZIONA  per gestire il Drag&Drop
    def handle_drop(self, event):
        # L'oggetto 'event' contiene i dati del file droppato
        # event.data è una stringa che contiene i percorsi dei file
        # Separali se sono più di uno
        file_path = event.data.strip()
    
        # Le virgolette di Tkinter possono causare problemi, quindi rimuoviamole
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
    
        # Controlla se il percorso è valido e passalo alla funzione open_file
        if file_path:
            self.open_file(file_path)
            
     # Aggiungi questa funzione alla tua classe, ad esempio dopo il metodo open_file()
    def apply_privacy_blur(self):
        if self.image is None:
            self.show_canvas_message("Carica un'immagine prima di applicare la sfocatura.")
            return
    
        self.update_status_bar("Applicando la sfocatura per la privacy...")
        self.master.update_idletasks()
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.plate_cascade = cv2.CascadeClassifier('haarcascade_russian_plate_number.xml')
        
        try:
            # Percorsi dei classificatori Haar Cascade pre-addestrati
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            # Per le targhe, non esiste un classificatore Haar standard in OpenCV.
            # Dovresti scaricarne uno separato, ad esempio da GitHub
            plate_cascade_path = cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml'
            
            # Inizializza i classificatori.
            face_cascade = cv2.CascadeClassifier(face_cascade_path)
            plate_cascade = cv2.CascadeClassifier(plate_cascade_path)
    
            # Converti l'immagine da PIL a un array OpenCV (BGR)
            img_np = np.array(self.image.convert("RGB"))
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
            # Converti l'immagine in scala di grigi per il rilevamento
            img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
            # Esegui il rilevamento dei volti. I parametri possono essere ottimizzati.
            # `scaleFactor` e `minNeighbors` controllano la precisione del rilevamento.
            faces = face_cascade.detectMultiScale(img_gray, scaleFactor=1.02, minNeighbors=3,minSize=(30, 30),maxSize=(2500,2500))
            # Esegui il rilevamento delle targhe, se hai il classificatore
            plates = plate_cascade.detectMultiScale(img_gray, scaleFactor=1.02, minNeighbors=3)
    
            # Per ogni volto rilevato, applica la sfocatura
            for (x, y, w, h) in faces:
                # Estrai la regione del viso dall'immagine originale
                face_region = img_bgr[y:y+h, x:x+w]
                # Applica una sfocatura gaussiana a quella regione
                blurred_face = cv2.GaussianBlur(face_region, (99, 99), 0)
                # Sostituisci la regione originale con quella sfocata
                img_bgr[y:y+h, x:x+w] = blurred_face
            
            # Per ogni TARGA di motoveicoli rilevata, applica la sfocatura
            for (x, y, w, h) in plates:
                # Estrai la regione della targa dall'immagine originale
                plate_region = img_bgr[y:y+h, x:x+w]
                # Applica una sfocatura gaussiana a quella regione
                blurred_plates = cv2.GaussianBlur(plate_region, (99, 99), 0)
                # Sostituisci la regione originale con quella sfocata
                img_bgr[y:y+h, x:x+w] = blurred_plates
                self.update_status_bar("...APPLICAZIONE delle sfocature in corso...attendere prego")
            
            

    
            # Converti l'immagine BGR di nuovo in RGB per PIL
            final_img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            # Aggiorna il tuo canvas
            self.image = Image.fromarray(final_img_rgb)
            self.display_image()
    
            self.update_status_bar("Sfocatura per la privacy applicata con successo!")
    
        except Exception as e:
            self.update_status_bar(f"Errore nell'applicazione della sfocatura: {e}")
            import traceback
            traceback.print_exc()
            
    #19/12/25 STEP 2: La Funzione di Estrazione. Dobbiamo estrarre i colori dall'immagine attualmente caricata.
    def extract_colors(self, num_colors=64):
         if self.image is None:
            return []
        
        # Convertiamo in palette adattiva
         paletted_img = self.image.convert("P", palette=Image.ADAPTIVE, colors=num_colors)
        
        # Otteniamo i dati della palette (lista di 768 valori: 256 colori * 3 RGB)
         raw_palette = paletted_img.getpalette()
        
        # Estraiamo solo i primi N colori (R, G, B)
         colors = []
         for i in range(0, num_colors * 3, 3):
              colors.append((raw_palette[i], raw_palette[i+1], raw_palette[i+2]))
         return colors   
                
#19/12/25 STEP 3: visualizzazione TOggle(olivetta): quadratini dei colori, matrice rxn
    
    def toggle_palette_view(self):
        if self.show_palette_var.get():
            # Puliamo il container precedente
            for widget in self.palette_container.winfo_children():
                widget.destroy()
                
            colors = self.extract_colors(num_colors=16) # Estraiamo 16 colori
            
            # Creiamo una griglia 8x8
            for i, color in enumerate(colors):
                # Convertiamo RGB in esadecimale per Tkinter
                hex_color = '#%02x%02x%02x' % color
                
                lbl = tk.Label(self.palette_container, bg=hex_color, width=2, height=1, relief="sunken")
                lbl.grid(row=i // 8, column=i % 8, padx=2, pady=2)
                
            self.palette_container.pack(pady=5, fill=tk.X)
        else:
            self.palette_container.pack_forget()
            
    def apply_motion_effect(self):
        if self.image is None:
            return
    
        # 1. Creiamo una copia per il "Ghost"
        ghost = self.image.copy()
        
        # 2. Applichiamo una sfocatura direzionale o leggera al ghost
        # Pillow non ha un MotionBlur nativo avanzato, quindi usiamo un trucco:
        # Sfocatura + Traslazione
        ghost = ghost.filter(ImageFilter.GaussianBlur(radius=2))
        
        # 3. Trasliamo il ghost di 15 pixel a destra e 5 in basso
        # Questo crea l'illusione del movimento della camera
        ghost = ImageChops.offset(ghost, 15, 5)
        
        # 4. Fondiamo l'originale con il ghost (opacità 50%)
        self.image = Image.blend(self.image, ghost, alpha=0.5)
        
        self.show_image()
        self.update_status_bar("Effetto mosso applicato.")  
    
        
        
    def show_image(self):
        """Aggiorna il Canvas con l'immagine corrente (self.image)"""
        if self.image is None:
            return
    
        # 1. Convertiamo l'oggetto Image di Pillow in un formato che Tkinter capisce
        self.tk_image = ImageTk.PhotoImage(self.image)
    
        # 2. Aggiorniamo il canvas
        # 'self.image_label' è l'ID dell'immagine creata nel canvas durante create_widgets
        self.canvas.itemconfig(self.image_label, image=self.tk_image)
    
        # 3. Opzionale: diciamo al canvas quanto è grande la nuova immagine 
        # (utile se l'effetto cambia le dimensioni)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        
        #17/01/2026
        
    def apply_beauty_filter(self):
        if self.image is None:
            return
    
        # --- INIZIO: CARICAMENTO IN GPU (OpenCL) ---
        # Convertiamo l'immagine in un formato che OpenCV può processare sulla GPU se disponibile
        img_cpu = cv2.cvtColor(np.array(self.image.convert("RGB")), cv2.COLOR_RGB2BGR)
        img_gpu = cv2.UMat(img_cpu) # Sposta l'immagine nella memoria della GPU/OpenCL
    
        # --- FASE 1: FILTRO BILATERALE ---
        self.status_bar.config(text="✨ FASE 1: Attivazione Filtro Bilaterale (Pelle)...", fg="blue")
        self.master.update_idletasks() # Forza Tkinter ad aggiornare il testo subito
        
        # Esecuzione sulla GPU
        # Il filtro bilaterale è pesante, qui la GPU aiuta molto
        smoothed_gpu = cv2.bilateralFilter(img_gpu, d=15, sigmaColor=75, sigmaSpace=75)
    
        # --- FASE 2: LEVIGATURA E LUCE ---
        self.status_bar.config(text="✨ FASE 2: Levigatura profonda e ottimizzazione luce...", fg="purple")
        self.master.update_idletasks()
    
        # Passaggio a HSV per la luminosità
        hsv_gpu = cv2.cvtColor(smoothed_gpu, cv2.COLOR_BGR2HSV)
        
        # Nota: Le operazioni dirette sulle matrici UMat (GPU) sono più veloci
        # Dividiamo i canali, modifichiamo e riuniamo
        h, s, v = cv2.split(hsv_gpu)
        
        # Usiamo cv2.multiply per restare in GPU invece di operazioni numpy lente
        s = cv2.multiply(s, 1.2) # Aumenta saturazione
        v = cv2.multiply(v, 1.15) # Aumenta luminosità
        
        hsv_gpu = cv2.merge([h, s, v])
        img_bright_gpu = cv2.cvtColor(hsv_gpu, cv2.COLOR_HSV2BGR)
    
        # --- FASE 3: DETTAGLI E NITIDEZZA ---
        self.status_bar.config(text="✨ FASE 3: Definizione sguardo e contrasto finale...", fg="darkgreen")
        self.master.update_idletasks()
    
        # Unsharp Mask per ridare nitidezza agli occhi dopo la levigatura
        gaussian_gpu = cv2.GaussianBlur(img_bright_gpu, (0, 0), 3)
        # img_final = img_bright * 1.5 - gaussian * 0.5
        img_final_gpu = cv2.addWeighted(img_bright_gpu, 1.5, gaussian_gpu, -0.5, 0)
    
        # --- FINE: RITORNO DALLA GPU AL PROGRAMMA ---
        # Riportiamo il risultato dalla GPU alla CPU per poterlo mostrare in PIL
        img_final_cpu = img_final_gpu.get() 
        
        self.image = Image.fromarray(cv2.cvtColor(img_final_cpu, cv2.COLOR_BGR2RGB))
        
        self.show_image()
        self.status_bar.config(text="✅ Filtro Red Carpet applicato con successo (GPU Accelerated)", fg="black")
        self.update_status_bar("Pronto.")
        
    def apply_eternal_youth(self):
        if self.image is None:
            return
    
        # --- FASE 0: PREPARAZIONE ---
        img_cpu = cv2.cvtColor(np.array(self.image.convert("RGB")), cv2.COLOR_RGB2BGR)
        img_gpu = cv2.UMat(img_cpu)
    
        # --- FASE 1: MASCHERA PELLE ---
        self.status_bar.config(text="🔍 FASE 1: Analisi della pelle (viso, collo, spalle)...", fg="blue")
        self.master.update_idletasks()
    
        img_ycrcb = cv2.cvtColor(img_gpu, cv2.COLOR_BGR2YCrCb)
        lower_skin = np.array([0, 133, 77], dtype=np.uint8)
        upper_skin = np.array([255, 173, 127], dtype=np.uint8)
        mask_gpu = cv2.inRange(img_ycrcb, lower_skin, upper_skin)
        
        # Pulizia e sfocatura della maschera per transizioni morbide
        mask_gpu = cv2.GaussianBlur(mask_gpu, (25, 25), 0)
    
        # --- FASE 2: LEVIGATURA ---
        self.status_bar.config(text="💆 FASE 2: Eliminazione rughe e segni del tempo...", fg="purple")
        self.master.update_idletasks()
        
        # Filtro bilaterale potente (il nostro chirurgo estetico)
        skin_smooth_gpu = cv2.bilateralFilter(img_gpu, d=15, sigmaColor=75, sigmaSpace=75)
    
        # --- FASE 3: ARMONIZZAZIONE (FUSIONE SICURA) ---
        self.status_bar.config(text="🎨 FASE 3: Armonizzazione corpo e viso...", fg="darkgreen")
        self.master.update_idletasks()
    
        # Invece di moltiplicazioni complesse che mandano in crash la GPU,
        # usiamo la maschera per incollare la pelle liscia sull'originale.
        # Convertiamo la maschera in float 0-1
        mask_float = cv2.divide(cv2.UMat(mask_gpu.get().astype(np.float32)), 255.0)
        
        # Portiamo tutto in float32 per fare il calcolo matematico preciso
        img_f = cv2.UMat(img_gpu.get().astype(np.float32))
        smooth_f = cv2.UMat(skin_smooth_gpu.get().astype(np.float32))
        
        # Formula di blending: Risultato = (Liscio * Maschera) + (Originale * (1 - Maschera))
        # Questo assicura che solo la pelle venga ritoccata
        temp1 = cv2.multiply(smooth_f, cv2.cvtColor(mask_float, cv2.COLOR_GRAY2BGR))
        
        # Calcoliamo l'inverso della maschera (1 - maschera)
        inv_mask = cv2.subtract(1.0, cv2.cvtColor(mask_float, cv2.COLOR_GRAY2BGR))
        temp2 = cv2.multiply(img_f, inv_mask)
        
        # Sommiamo i due risultati
        img_final_f = cv2.add(temp1, temp2)
        
        # Torniamo al formato standard a 8 bit (0-255)
        img_final_gpu = cv2.convertScaleAbs(img_final_f)
    
        # --- FASE 4: RITORNO ---
        img_final_cpu = img_final_gpu.get()
        self.image = Image.fromarray(cv2.cvtColor(img_final_cpu, cv2.COLOR_BGR2RGB))
        
        self.show_image()
        self.status_bar.config(text="✅ Effetto Eterna Giovinezza applicato correttamente.", fg="black")
        if self.image is None:
            return
    
        # --- FASE 0: CARICAMENTO GPU ---
        img_cpu = cv2.cvtColor(np.array(self.image.convert("RGB")), cv2.COLOR_RGB2BGR)
        img_gpu = cv2.UMat(img_cpu)
    
        # --- FASE 1: CREAZIONE MASCHERA PELLE ---
        self.status_bar.config(text="🔍 FASE 1: Analisi della pelle (viso, collo, spalle)...", fg="blue")
        self.master.update_idletasks()
    
        # Convertiamo in YCrCb per isolare la pelle
        img_ycrcb = cv2.cvtColor(img_gpu, cv2.COLOR_BGR2YCrCb)
        # Range standard per la pelle umana
        lower_skin = np.array([0, 133, 77], dtype=np.uint8)
        upper_skin = np.array([255, 173, 127], dtype=np.uint8)
        mask_gpu = cv2.inRange(img_ycrcb, lower_skin, upper_skin)
        
        # Puliamo la maschera (rimuove i puntini isolati)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_gpu = cv2.morphologyEx(mask_gpu, cv2.MORPH_OPEN, kernel)
        mask_gpu = cv2.GaussianBlur(mask_gpu, (15, 15), 0) # Sfuma i bordi della maschera per non far vedere lo stacco
    
        # --- FASE 2: ELIMINAZIONE RUGHE (Smoothing Avanzato) ---
        self.status_bar.config(text="💆 FASE 2: Eliminazione rughe e segni del tempo...", fg="purple")
        self.master.update_idletasks()
    
        # Usiamo un filtro bilaterale molto potente per la "giovinezza"
        # d=25 rende la pelle liscissima
        skin_smooth_gpu = cv2.bilateralFilter(img_gpu, d=25, sigmaColor=90, sigmaSpace=90)
    
        # --- FASE 3: ARMONIZZAZIONE E FUSIONE ---
        self.status_bar.config(text="🎨 FASE 3: Armonizzazione corpo e viso...", fg="darkgreen")
        self.master.update_idletasks()
    
        # Trasformiamo la maschera in 3 canali per poterla moltiplicare
        mask_3ch = cv2.cvtColor(mask_gpu, cv2.COLOR_GRAY2BGR)
        mask_3ch = cv2.divide(mask_3ch, 255.0) # Normalizza tra 0 e 1
    
        # FONDIAMO: Dove c'è pelle usa 'skin_smooth', dove non c'è usa 'img_gpu' (originale)
        # Questo mantiene capelli, occhi e vestiti nitidissimi!
        img_final_gpu = cv2.add(
            cv2.multiply(skin_smooth_gpu, mask_3ch),
            cv2.multiply(img_gpu, cv2.subtract(cv2.UMat(np.ones(img_cpu.shape, dtype=np.float32)), mask_3ch), dtype=cv2.CV_8U)
        )
    
        # --- FASE 4: TOCCO DI LUCE ---
        # Un leggero aumento di contrasto per non far sembrare la foto sbiadita
        img_final_gpu = cv2.convertScaleAbs(img_final_gpu, alpha=1.05, beta=5)
    
        # --- RITORNO ---
        img_final_cpu = img_final_gpu.get()
        self.image = Image.fromarray(cv2.cvtColor(img_final_cpu, cv2.COLOR_BGR2RGB))
        
        self.show_image()
        self.status_bar.config(text="✅ Effetto Eterna Giovinezza armonizzato applicato.", fg="black")
    

if __name__ == "__main__":
   # La finestra principale deve essere un'istanza di tk.Tk()
    root = tk.Tk()
    app = PhotoEditorApp(root)
    root.mainloop()