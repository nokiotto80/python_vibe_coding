"""
=============================================================================
PROGETTO: MSN Messenger Amarcord - Sfondi Dinamici & Interfaccia Nostalgica
=============================================================================
Autore: Sviluppatore Appassionato (Ispirato agli anni d'oro di MSN 2006-2008)
Data Creazione: Ottobre 2023 (Aggiornato e Ottimizzato)
Versione: 3.6 (Correzione bug compatibilità colore trasparente su Tkinter)

SCOPO DELL'APPLICAZIONE:
Ricreare l'esperienza nostalgica (Amarcord) delle chat di MSN Messenger,
integrando funzionalità iconiche come il "Trillo" (con audio non bloccante),
la gestione di immagini di sfondo personalizzate, e introducendo gli amati 
"Sfondi Dinamici" animati in tempo reale (stile erba nera con fiori, onde
d'acqua e cieli stellati).

FUNZIONALITÀ IMPLEMENTATE:
1. Interfaccia grafica ispirata ai client MSN Messenger (Windows Live / Plus!).
2. Finestra di chat simulata con box messaggi e banner di stato online.
3. Funzione "Trillo" (Shake) con movimento fluido della finestra e riproduzione
   audio asincrona (tramite thread separati per evitare blocchi della GUI).
4. Caricamento di immagini di sfondo statiche (PNG, JPEG, JP2, TIFF, BMP, GIF)
   con ridimensionamento automatico (Responsive Canvas).
5. Pannello con 4 mini quadratini (swatches) alla base della finestra per il
   cambio rapido dei temi:
   - Sfondo 1: Gradiente Statico (Tramonto / Slate).
   - Sfondo 2: Animazione Dinamica "Erba Nera & Fiori" (Matrix Grass).
   - Sfondo 3: Animazione Dinamica "Onde d'Acqua Increspate" (Rippling Water).
   - Sfondo 4: Animazione Dinamica "Cielo Stellato" (Starfield).

TECNICA USATA PER ANIMARE GLI SFONDI:
A differenza dei vecchi formati proprietari o delle pesanti GIF animate di MSN,
questo script utilizza una tecnica di **Rendering Procedurale in Tempo Reale** 
sfruttando il widget `tk.Canvas` di Python e la libreria matematica `math`:
- Vengono calcolate funzioni trigonometriche (Seni e Coseni) a ogni fotogramma 
  (~30 FPS tramite il metodo non bloccante `master.after()`).
- Le coordinate dei vari elementi (steli d'erba, onde, stelle) vengono mutate 
  dinamicamente ad ogni ciclo per simulare il movimento fluido senza gravare 
  eccessivamente sulle risorse di sistema (CPU/RAM).

STORICO DELLE VERSIONI:
- v1.0: Finestra base Tkinter e funzione trillo iniziale.
- v1.5: Aggiunta del supporto audio asincrono con `threading` e `playsound`.
- v2.0: Risoluzione bug di blocco UI convertendo `time.sleep` in `window.after`.
- v3.0: Introduzione del widget `tk.Canvas` e caricamento immagini di sfondo.
- v3.5: Aggiunta dei 4 swatches interattivi e del motore di animazione procedurale.
- v3.6: Fix critico per TclError su macOS/Anaconda rimuovendo il colore "transparent" 
        non supportato dai frame nativi standard di Tkinter.
=============================================================================
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import random
import threading
import os
import math
from playsound import playsound
from PIL import Image, ImageTk

# --- Configurazione Globale ---
SOUND_FILE = "/Users/macbook_vincenzo/Python/sounds/bell-ringing.wav"


def play_sound_async():
    """
    Riproduce l'effetto sonoro del trillo in un thread separato.
    Evita il congelamento della interfaccia grafica (GUI) durante l'audio.
    """
    if not os.path.exists(SOUND_FILE):
        print(f"Attenzione: File audio non trovato in {SOUND_FILE}. Continuo in silenzio.")
        return
    try:
        playsound(SOUND_FILE)
    except Exception as e:
        print(f"Errore durante la riproduzione audio: {e}")


class MessengerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("MSN Messenger Amarcord - Sfondi Dinamici 2007")
        self.master.geometry("700x500")
        self.master.minsize(550, 420)

        # Stati della gestione sfondo: 'gradient', 'image', o 'dynamic_animation'
        self.bg_mode = 'gradient'
        
        # Colori per il gradiente statico di default
        self.grad_color1 = (20, 30, 48)     # Blu Notte
        self.grad_color2 = (44, 83, 100)    # Grigio Ardesia

        # Variabili per l'animazione dinamica
        self.animation_type = "matrix_grass"
        self.animation_job = None
        self.anim_step = 0

        # Variabili per le immagini statiche caricate dall'utente
        self.background_photo = None
        self.background_image_id = None
        self._current_original_image = None

        # Canvas principale che copre l'intera finestra come livello di disegno
        self.canvas = tk.Canvas(self.master, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Costruzione della GUI sopra il Canvas
        self.create_widgets()

        # Avvio del render iniziale dello sfondo
        self.render_background()

    def create_widgets(self):
        """Crea tutti gli elementi dell'interfaccia (Chat box, Header, Bottoni, Swatches)."""
        
        # 1. Header superiore stile MSN
        self.header_frame = tk.Frame(self.master, bg="#2d2d2d", height=55)
        self.header_window_id = self.canvas.create_window(0, 0, window=self.header_frame, anchor="nw", width=700)
        
        self.lbl_title = tk.Label(
            self.header_frame, 
            text="💬 Conversazione con: Amico_Nostalgico_2007 (Online)", 
            fg="#00FF66", 
            bg="#2d2d2d", 
            font=("Arial", 11, "bold")
        )
        self.lbl_title.pack(side="left", padx=15, pady=15)

        # 2. Area di chat simulata
        self.chat_frame = tk.Frame(self.master, bg="white", bd=2, relief="sunken")
        self.chat_window_id = self.canvas.create_window(30, 75, window=self.chat_frame, anchor="nw", width=640, height=210)

        self.chat_text = tk.Text(self.chat_frame, wrap="word", bg="#fcfcfc", fg="#0a0af5", font=("Arial", 10), state="normal", bd=0)
        self.chat_text.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        self.chat_text.insert(
            "end", 
            "Amico_Nostalgico_2007 scrive:\n"
            "Ehi! Ti ricordi quando passavamo i pomeriggi su MSN a mandare trilli e personalizzare gli sfondi con i temi dinamici?\n\n"
            "Tu rispondi:\n"
        )
        self.chat_text.config(state="disabled")

        # 3. Bottoni d'azione (Trillo e Carica Sfondo)
        self.btn_trillo = tk.Button(
            self.master, text="🛎️ INVIA TRILLO 🛎️", command=self.shake_window, 
            font=("Arial", 11, "bold"), bg="#ff4d4d", fg="#fc0303", 
            activebackground="#ff1a1a", relief="raised", bd=3, cursor="hand2"
        )
        self.btn_trillo_id = self.canvas.create_window(30, 310, window=self.btn_trillo, anchor="nw", width=150, height=36)

        self.btn_image = tk.Button(
            self.master, text="📁 Carica Immagine...", command=self.load_background_image, 
            font=("Arial", 10), bg="#e1e1e1", fg="#333333", 
            relief="raised", bd=2, cursor="hand2"
        )
        self.btn_image_id = self.canvas.create_window(195, 310, window=self.btn_image, anchor="nw", width=150, height=36)

        # 4. Sezione dei 4 Mini Quadratini (Swatches) per cambiare sfondo al volo
        self.swatch_label = tk.Label(
            self.master, text="Seleziona Sfondo (Statico / Dinamico 2006-2008):", 
            fg="#fc0303", bg="#1a1a1a", font=("Arial", 9, "bold")
        )
        self.swatch_label_id = self.canvas.create_window(30, 365, window=self.swatch_label, anchor="nw")

        # NOTA: Sostituito 'transparent' con un colore solido scuro (#1a1a1a) per evitare TclError su macOS
        self.swatches_container = tk.Frame(self.master, bg="#1a1a1a")
        self.swatches_window_id = self.canvas.create_window(30, 390, window=self.swatches_container, anchor="nw")

        # Definizione dei 4 preset richiesti
        presets = [
            {"name": "Gradiente Caldo", "type": "gradient", "c1": (238, 9, 121), "c2": (255, 106, 0), "box_color": "#ff6a00"},
            {"name": "Erba Nera & Fiori", "type": "dynamic", "anim": "matrix_grass", "box_color": "#00ff66"},
            {"name": "Onde Blu", "type": "dynamic", "anim": "rippling_water", "box_color": "#00a8ff"},
            {"name": "Cielo Stellato", "type": "dynamic", "anim": "starfield", "box_color": "#9b59b6"}
        ]

        for p in presets:
            btn = tk.Button(
                self.swatches_container, 
                bg=p["box_color"], 
                width=5, 
                height=2, 
                relief="ridge", 
                bd=2, 
                cursor="hand2",
                command=lambda preset=p: self.apply_preset(preset)
            )
            btn.pack(side="left", padx=8)

    def on_canvas_resize(self, event):
        """Gestisce il ridimensionamento responsivo degli elementi grafici sul Canvas."""
        width = event.width
        height = event.height

        if width < 100 or height < 100:
            return

        self.canvas.coords(self.header_window_id, 0, 0)
        self.header_frame.config(width=width)

        chat_w = max(300, width - 60)
        chat_h = max(140, height - 290)
        self.canvas.coords(self.chat_window_id, 30, 72)
        self.chat_frame.config(width=chat_w, height=chat_h)

        btn_y = height - 110
        self.canvas.coords(self.btn_trillo_id, 30, btn_y)
        self.canvas.coords(self.btn_image_id, 195, btn_y)

        self.canvas.coords(self.swatch_label_id, 30, btn_y + 45)
        self.canvas.coords(self.swatches_window_id, 30, btn_y + 68)

        self.render_background()

    def apply_preset(self, preset):
        """Applica il preset scelto tramite i quadratini in basso."""
        if self.animation_job:
            self.master.after_cancel(self.animation_job)
            self.animation_job = None

        if preset["type"] == "gradient":
            self.bg_mode = 'gradient'
            self.grad_color1 = preset["c1"]
            self.grad_color2 = preset["c2"]
            self.render_background()
        elif preset["type"] == "dynamic":
            self.bg_mode = 'dynamic_animation'
            self.animation_type = preset["anim"]
            self.anim_step = 0
            self.run_animation_loop()

    def render_background(self):
        """Disegna sfondi statici (Gradiente o Immagine fissa)."""
        if self.animation_job and self.bg_mode != 'dynamic_animation':
            self.master.after_cancel(self.animation_job)
            self.animation_job = None

        self.canvas.delete("bg_item")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1 or height <= 1:
            return

        if self.bg_mode == 'gradient':
            r1, g1, b1 = self.grad_color1
            r2, g2, b2 = self.grad_color2
            step = 4
            for y in range(0, height, step):
                factor = y / height
                r = int(r1 + (r2 - r1) * factor)
                g = int(g1 + (g2 - g1) * factor)
                b = int(b1 + (b2 - b1) * factor)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                self.canvas.create_line(0, y, width, y, fill=hex_color, width=step, tags="bg_item")
            self.canvas.tag_lower("bg_item")

        elif self.bg_mode == 'image' and self._current_original_image:
            self._resize_and_display_background_image()

    def run_animation_loop(self):
        """
        Motore principale per l'animazione procedurale degli sfondi dinamici.
        Aggiorna le forme geometriche a ~30 fotogrammi al secondo.
        """
        if self.bg_mode != 'dynamic_animation':
            return

        self.canvas.delete("bg_item")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            self.animation_job = self.master.after(50, self.run_animation_loop)
            return

        self.canvas.create_rectangle(0, 0, width, height, fill="#080808", outline="", tags="bg_item")

        if self.animation_type == "matrix_grass":
            r_seed = int(self.anim_step * 2.5)
            for i in range(0, width, 22):
                wave = math.sin((i + r_seed) * 0.04) * 35
                blade_h = 70 + wave
                x = i
                y1 = height
                y2 = height - blade_h
                self.canvas.create_line(x, y1, x + 4, y2, fill="#00ff66", width=2, tags="bg_item")
                
                if i % 66 == 0:
                    fx = x + 4
                    fy = y2 - (math.cos(self.anim_step * 0.1 + i) * 8)
                    self.canvas.create_oval(fx-3, fy-3, fx+3, fy+3, fill="#ff69b4", outline="#ffffff", tags="bg_item")

        elif self.animation_type == "rippling_water":
            for j in range(6):
                points = []
                base_y = (height / 7) * (j + 1) + math.sin(self.anim_step * 0.04 + j) * 12
                for x in range(0, width + 25, 25):
                    y = base_y + math.sin(x * 0.025 + self.anim_step * 0.06 + j) * 10
                    points.append((x, y))
                if len(points) >= 2:
                    flat_pts = [coord for pt in points for coord in pt]
                    self.canvas.create_line(flat_pts, fill="#00a8ff", width=3, smooth=True, tags="bg_item")

        elif self.animation_type == "starfield":
            random.seed(100)
            for i in range(50):
                sx = (i * 37 + self.anim_step * (0.4 + (i % 3))) % width
                sy = (i * 51) % height
                size = 1 + (i % 3)
                brightness = int(140 + 115 * math.sin(self.anim_step * 0.1 + i))
                hex_col = f"#{brightness:02x}{brightness:02x}{255:02x}"
                self.canvas.create_oval(sx, sy, sx + size, sy + size, fill=hex_col, outline="", tags="bg_item")

        self.canvas.tag_lower("bg_item")
        self.anim_step += 1

        self.animation_job = self.master.after(35, self.run_animation_loop)

    def load_background_image(self):
        """Permette di caricare un'immagine statica personalizzata (JPEG, PNG, TIFF, ecc.)."""
        file_path = filedialog.askopenfilename(
            title="Seleziona un'immagine di sfondo",
            filetypes=[("Immagini Supportate", "*.png *.jpg *.jpeg *.jp2 *.tiff *.bmp *.gif"), ("Tutti i file", "*.*")]
        )
        if not file_path:
            return

        try:
            if self.animation_job:
                self.master.after_cancel(self.animation_job)
                self.animation_job = None

            original_image = Image.open(file_path)
            self._current_original_image = original_image
            self.bg_mode = 'image'
            self.render_background()
        except Exception as e:
            messagebox.showerror("Errore Caricamento", f"Impossibile leggere l'immagine:\n{e}")

    def _resize_and_display_background_image(self):
        """Ridimensiona l'immagine caricata adattandola proporzionalmente al Canvas."""
        if self._current_original_image is None:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1 or height <= 1:
            return

        img_w, img_h = self._current_original_image.size
        canvas_aspect = width / height
        img_aspect = img_w / img_h

        if img_aspect > canvas_aspect:
            new_w = width
            new_h = int(new_w / img_aspect)
        else:
            new_h = height
            new_w = int(new_h * img_aspect)

        resized = self._current_original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(resized)

        if self.background_image_id:
            self.canvas.delete(self.background_image_id)

        self.background_image_id = self.canvas.create_image(width / 2, height / 2, image=self.background_photo, tags="bg_item")
        self.canvas.tag_lower("bg_item")

    def shake_window(self):
        """Funzione Trillo: Scuote la finestra casualmente e riproduce il suono in parallelo."""
        original_x = self.master.winfo_x()
        original_y = self.master.winfo_y()

        num_shakes = 15
        shake_intensity = 10

        sound_thread = threading.Thread(target=play_sound_async)
        sound_thread.start()

        for _ in range(num_shakes):
            new_x = original_x + random.randint(-shake_intensity, shake_intensity)
            new_y = original_y + random.randint(-shake_intensity, shake_intensity)
            self.master.geometry(f"+{new_x}+{new_y}")
            self.master.update_idletasks()
            self.master.after(45)

        self.master.geometry(f"+{original_x}+{original_y}")


if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("Errore critico: Libreria 'Pillow' mancante. Installa con: pip install Pillow")
        exit()

    root = tk.Tk()
    app = MessengerApp(root)
    root.mainloop()