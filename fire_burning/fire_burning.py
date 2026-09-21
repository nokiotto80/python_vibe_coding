import skimage.io as io
import numpy as np
import os
from PIL import Image, ImageTk
import tkinter as tk
import time
import threading
from playsound import playsound


def genera_frame_intermedio(img1_path, img2_path, t, target_size=(None, None)):
    """Genera un frame intermedio tra due immagini, ridimensionandole se necessario."""
    img1_pil = Image.open(img1_path).convert("RGBA") # Assicurati che abbiano il canale alpha
    img2_pil = Image.open(img2_path).convert("RGBA") # Assicurati che abbiano il canale alpha

    if target_size[0] is not None and target_size[1] is not None:
        # Ridimensiona a target_size (larghezza, altezza)
        img1_resized = img1_pil.resize(target_size, Image.LANCZOS) # LANCZOS per migliore qualità
        img2_resized = img2_pil.resize(target_size, Image.LANCZOS)
    else:
        # Se non specificata una dimensione target, usa la dimensione della prima immagine ridimensionata
        # per assicurare coerenza se la prima immagine è già stata ridimensionata altrove.
        # Oppure potremmo scegliere di usare la dimensione della prima immagine *originale*.
        # Per semplicità, qui assumiamo che target_size sia sempre fornito o che le originali siano uguali.
        # Per sicurezza, potremmo impostare target_size come la dimensione della prima immagine PIL.
        first_img_size = img1_pil.size # (width, height)
        img1_resized = img1_pil
        img2_resized = img2_pil.resize(first_img_size, Image.LANCZOS) # Ridimensiona la seconda alla prima

    # Converti in array NumPy
    img1_np = np.array(img1_resized)
    img2_np = np.array(img2_resized)

    # Verifica che le dimensioni siano ora le stesse
    if img1_np.shape != img2_np.shape:
        # Se c'è ancora una discrepanza, prova a forzare il ridimensionamento nuovamente
        # (questo non dovrebbe accadere se resize funziona correttamente)
        print(f"DEBUG: Dimensioni finali non corrispondenti prima dell'interpolazione: {img1_np.shape} vs {img2_np.shape}")
        # Forza un ulteriore ridimensionamento al massimo comune denominatore o al target_size
        if target_size[0] is not None and target_size[1] is not None:
            img1_np = np.array(img1_pil.resize(target_size, Image.LANCZOS))
            img2_np = np.array(img2_pil.resize(target_size, Image.LANCZOS))
        else:
            # Fallback per assicurarsi che le dimensioni siano le stesse anche senza target_size esplicito
            max_h = max(img1_np.shape[0], img2_np.shape[0])
            max_w = max(img1_np.shape[1], img2_np.shape[1])
            new_target_size = (max_w, max_h) # (width, height)
            img1_np = np.array(img1_pil.resize(new_target_size, Image.LANCZOS))
            img2_np = np.array(img2_pil.resize(new_target_size, Image.LANCZOS))

        if img1_np.shape != img2_np.shape: # Ultimo controllo dopo il tentativo di correzione
            raise ValueError(f"Le dimensioni delle immagini dopo il ridimensionamento persistono a non corrispondere: {img1_np.shape} vs {img2_np.shape}")


    # Esegui l'interpolazione
    # L'interpolazione lineare funziona bene per i pixel, ma fai attenzione con il canale alpha se non è già pre-moltiplicato.
    # Per semplicità, eseguiamo l'interpolazione su tutti i canali (RGB + Alpha)
    immagine_intermedia_np = ((1 - t) * img1_np + t * img2_np).astype(np.uint8)

    return Image.fromarray(immagine_intermedia_np) # Restituisci come oggetto PIL Image

# Il resto del codice (genera_frames_sequenza, AnimazioneFuoco, if __name__ == "__main__":) rimane come prima
# Assicurati di usare il codice completo che hai già, sostituendo solo questa funzione.



def genera_frames_sequenza(lista_immagini_paths, num_frames_intermedie=5, output_dir="intermediate_frames", target_size=(None, None)):
    """Genera una sequenza di frames intermedi tra le immagini in una lista."""
    os.makedirs(output_dir, exist_ok=True)
    nuovi_paths = []
    for i in range(len(lista_immagini_paths) - 1):
        path1 = lista_immagini_paths[i]
        path2 = lista_immagini_paths[i+1]
        nome_base1 = os.path.splitext(os.path.basename(path1))[0]
        nome_base2 = os.path.splitext(os.path.basename(path2))[0]

        for j in range(1, num_frames_intermedie + 1):
            t = j / (num_frames_intermedie + 1)
            frame_intermedio_pil = genera_frame_intermedio(path1, path2, t, target_size)
            nome_file = os.path.join(output_dir, f"{nome_base1}_to_{nome_base2}_intermedio_{j}.png")
            frame_intermedio_pil.save(nome_file) # Salva usando Pillow
            nuovi_paths.append(nome_file)
    return nuovi_paths

class AnimazioneFuoco:
    def __init__(self, master, immagini_paths, suono_path):
        self.master = master
        master.title("Animazione Fuoco")

        self.immagini_paths = immagini_paths
        self.immagini_tk = []
        self.current_index = 0
        self.label = tk.Label(master)
        self.label.pack()

        self.suono_path = suono_path
        self.suono_thread = None

        self.load_immagini()
        self.mostra_frame()
        self.play_suono() # Avvia la riproduzione del suono all'inizio

        master.bind('<Escape>', self.chiudi)

    def load_immagini(self):
        for path in self.immagini_paths:
            try:
                img = Image.open(path)
                img_tk = ImageTk.PhotoImage(img)
                self.immagini_tk.append(img_tk)
            except FileNotFoundError:
                print(f"Errore: Immagine non trovata: {path}")
                self.master.destroy()
                exit()

    def mostra_frame(self):
        if self.immagini_tk:
            self.label.config(image=self.immagini_tk[self.current_index])
            self.current_index = (self.current_index + 1) % len(self.immagini_tk)
            self.master.after(400, self.mostra_frame)

    def play_suono(self):
        def play_sound_threaded():

            
            try: 
             while True:  #suono in riproduzione  CONTINUA
                       playsound(self.suono_path)
                
            except Exception as e:
                print(f"Errore playsound nel thread: {e}")

        self.suono_thread = threading.Thread(target=play_sound_threaded, daemon=True)
        self.suono_thread.start()

    def chiudi(self, event):
        self.master.destroy()


    
if __name__ == "__main__":
    root = tk.Tk()
    percorsi_immagini_originali = ["fire.png", "fire2.png", "fire3.png", "fire4.png", "fire5.png"]
    firesound = os.path.join("/Users/macbook_vincenzo/Python/sounds", "28314__pcaeldries__fireburning.wav")

    # Genera i frames intermedi
    nuovi_frames = genera_frames_sequenza(percorsi_immagini_originali, num_frames_intermedie=10) # Esempio: 10 frames intermedi tra ogni coppia

    # Crea la lista completa dei percorsi delle immagini
    percorsi_immagini_completi = []
    for i in range(len(percorsi_immagini_originali) - 1):
        percorsi_immagini_completi.append(percorsi_immagini_originali[i])
        # Aggiungi i frames intermedi generati tra questa e la prossima immagine
        nome_base1 = os.path.splitext(os.path.basename(percorsi_immagini_originali[i]))[0]
        nome_base2 = os.path.splitext(os.path.basename(percorsi_immagini_originali[i+1]))[0]
        for j in range(1, 11): # Assumendo 10 frames intermedi
            percorsi_immagini_completi.append(os.path.join("intermediate_frames", f"{nome_base1}_to_{nome_base2}_intermedio_{j}.png"))
    percorsi_immagini_completi.append(percorsi_immagini_originali[-1]) # Aggiungi l'ultima immagine originale

    animazione = AnimazioneFuoco(root, percorsi_immagini_completi, firesound)
    root.mainloop()