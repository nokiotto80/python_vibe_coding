#
# Progetto: Theremin Digitale Interattivo
# Data Ultimo Aggiornamento: 31 Gennaio 2026
# Descrizione: Applicazione desktop in Python che simula un Theremin.
#              Include un effetto speciale "UFO" per simulare suoni Sci-Fi anni '50.
#
# Funzionalità:
# 1. Theremin Analogico: Controllo continuo di frequenza (X) e volume (Y).
# 2. Theremin Discreto: Mappatura della posizione su note musicali specifiche.
# 3. Effetto UFO 🛸: Genera un suono di accelerazione spaziale con animazione.
# 4. Correzione Bug: Utilizzo dell'attributo 'active' per lo stream audio.
#
# Librerie: tkinter, sounddevice, numpy, threading
#

import tkinter as tk
import math
import numpy as np
import sounddevice as sd
import threading
import time

class Theremin:
    def __init__(self, root):
        """
        Inizializza l'interfaccia e le componenti audio.
        """
        self.root = root
        self.root.title("Theremin Digitale - Sci-Fi Edition")
        self.root.geometry("600x680")
        self.root.resizable(False, False)
        self.root.configure(bg="#1A1A1A")

        # Area di interazione
        self.canvas = tk.Canvas(root, width=500, height=450, bg="black", highlightthickness=1, highlightbackground="#444")
        self.canvas.pack(pady=20, padx=20)

        # Frame controlli superiore
        self.control_frame = tk.Frame(root, bg="#1A1A1A")
        self.control_frame.pack(fill=tk.X, padx=20)

        # Switch Modalità
        self.switch_var = tk.BooleanVar()
        self.switch = tk.Checkbutton(
            self.control_frame,
            text="MODALITÀ DISCRETA",
            variable=self.switch_var,
            command=self.toggle_mode,
            font=("Helvetica", 10, "bold"),
            fg="#EEE",
            bg="#333",
            selectcolor="#444",
            indicatoron=False,
            relief="flat",
            padx=20,
            pady=10,
            activebackground="#555"
        )
        self.switch.pack(side=tk.LEFT)

        # Label Informazioni
        self.info_label = tk.Label(
            self.control_frame,
            text="Frequenza: --- Hz | Volume: ---",
            font=("Consolas", 11),
            fg="#00FF00",
            bg="#1A1A1A",
            padx=20
        )
        self.info_label.pack(side=tk.RIGHT)

        # Pulsante UFO 🛸
        self.ufo_button = tk.Button(
            root,
            text="EFFETTO UFO 🛸",
            command=self.trigger_ufo_effect,
            font=("Helvetica", 12, "bold"),
            fg="white",
            bg="#6200EE",
            activebackground="#3700B3",
            activeforeground="white",
            relief="raised",
            pady=10
        )
        self.ufo_button.pack(fill=tk.X, padx=40, pady=10)

        # Parametri Audio
        self.sample_rate = 44100
        self.min_freq = 220.0
        self.max_freq = 1200.0 # Aumentata un po' per effetti più acuti
        self.current_frequency = self.min_freq
        self.current_amplitude = 0.0
        self.phase = 0.0
        self.stream = None
        self.is_playing = False
        self.is_discrete = False
        self.points = []
        self.ufo_active = False

        # Eventi Mouse
        self.canvas.bind("<Button-1>", self.start_sound)
        self.canvas.bind("<B1-Motion>", self.update_params)
        self.canvas.bind("<ButtonRelease-1>", self.stop_sound)

        self.root.update_idletasks()
        self.generate_grid()

    def generate_grid(self):
        """Genera i punti per la modalità discreta."""
        self.points = []
        w, h = 500, 450
        step = 50
        for x in range(step, w, step):
            for y in range(step, h, step):
                self.points.append((x, y))

    def toggle_mode(self):
        """Passa da modalità continua a discreta."""
        self.is_discrete = self.switch_var.get()
        self.canvas.delete("all")
        if self.is_discrete:
            for x, y in self.points:
                self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="#555", outline="")
        self.update_info()

    def _audio_callback(self, outdata, frames, time, status):
        """Genera l'onda sinusoidale in tempo reale."""
        t = (self.phase + np.arange(frames)) / self.sample_rate
        samples = self.current_amplitude * np.sin(2 * np.pi * self.current_frequency * t)
        outdata[:] = samples.reshape(-1, 1)
        self.phase = (self.phase + frames) % self.sample_rate

    def start_sound(self, event):
        """Avvia lo stream audio."""
        if self.ufo_active: return # Non interrompere l'effetto UFO se attivo
        if not self.is_playing:
            try:
                self.stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='float32',
                    callback=self._audio_callback
                )
                self.stream.start()
                self.is_playing = True
                self.update_params(event)
            except Exception as e:
                print(f"Errore Audio: {e}")

    def update_params(self, event):
        """Aggiorna frequenza e volume in base alla posizione."""
        if not self.is_playing or self.ufo_active: return

        x, y = event.x, event.y
        w, h = 500, 450

        if self.is_discrete:
            dists = [math.dist((x, y), p) for p in self.points]
            idx = dists.index(min(dists))
            x, y = self.points[idx]
            
            self.canvas.delete("cursor")
            self.canvas.create_oval(x-6, y-6, x+6, y+6, outline="#00FF00", width=2, tags="cursor")
        
        nx = max(0, min(1, x / w))
        ny = max(0, min(1, y / h))

        self.current_frequency = self.min_freq + (self.max_freq - self.min_freq) * nx
        self.current_amplitude = 1.0 - ny 
        
        self.update_info()

    def update_info(self):
        """Aggiorna la label testuale."""
        if self.is_playing:
            text = f"Freq: {self.current_frequency:.1f} Hz | Vol: {self.current_amplitude:.2f}"
        elif self.ufo_active:
            text = "🛸 MANOVRA UFO IN CORSO..."
        else:
            text = "Frequenza: --- Hz | Volume: ---"
        self.info_label.config(text=text)

    def trigger_ufo_effect(self):
        """Avvia l'effetto sonoro e visivo dell'UFO."""
        if self.ufo_active: return
        self.stop_sound()
        self.ufo_active = True
        self.ufo_button.config(state=tk.DISABLED, bg="#333")
        threading.Thread(target=self._ufo_sequence, daemon=True).start()

    def _ufo_sequence(self):
        """Sequenza sonora di accelerazione UFO."""
        duration = 2.5 # secondi
        steps = 100
        sleep_time = duration / steps
        
        # Inizializza audio per l'effetto
        try:
            with sd.OutputStream(samplerate=self.sample_rate, channels=1, dtype='float32') as stream:
                # Creazione animazione sul canvas
                ufo_icon = self.canvas.create_text(0, 225, text="🛸", font=("Helvetica", 32), fill="white")
                
                start_f = 100.0
                end_f = 2000.0 # Frequenza che sale oltre i limiti umani per simulare l'allontanamento
                
                phase = 0.0
                for i in range(steps):
                    # Calcolo progressione non lineare (accelerazione esponenziale)
                    progress = i / steps
                    freq = start_f + (end_f - start_f) * (progress ** 2)
                    
                    # Volume che aumenta e poi svanisce (effetto passaggio)
                    vol = 0.5 * math.sin(math.pi * progress) 
                    
                    # Generazione piccolo chunk audio
                    num_frames = int(self.sample_rate * sleep_time)
                    t = (phase + np.arange(num_frames)) / self.sample_rate
                    chunk = vol * np.sin(2 * np.pi * freq * t)
                    stream.write(chunk.astype('float32'))
                    
                    phase += num_frames
                    
                    # Aggiornamento UI (manovra da sinistra a destra)
                    x_pos = progress * 550
                    self.canvas.coords(ufo_icon, x_pos, 225 - (progress * 100)) # Sale anche verso l'alto
                    time.sleep(0.01) # Piccolo delay per fluidità animazione

                self.canvas.delete(ufo_icon)
        except Exception as e:
            print(f"Errore effetto UFO: {e}")
        
        self.ufo_active = False
        self.root.after(0, lambda: self.ufo_button.config(state=tk.NORMAL, bg="#6200EE"))
        self.root.after(0, self.update_info)

    def stop_sound(self, event=None):
        """Ferma lo stream audio manuale."""
        if self.stream and self.stream.active:
            self.stream.stop()
            self.stream.close()
        self.stream = None
        self.is_playing = False
        self.canvas.delete("cursor")
        self.update_info()

if __name__ == "__main__":
    root = tk.Tk()
    app = Theremin(root)
    root.mainloop()