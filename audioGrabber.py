# ==============================================================================
# Autore: AI Assistant (Basato su Richieste Utente)
# Data: Ottobre 2025
# Sistema Operativo: Multi-piattaforma (Windows, macOS, Linux)
# Finalità del Programma: Interfaccia grafica (GUI) per scaricare e processare
#                         contenuti multimediali da piattaforme di streaming
#                         (come YouTube) utilizzando yt-dlp e Tkinter.
# Funzioni Principali:
# - Estrai Solo Audio: Scarica la traccia audio e la converte in formato (es. MP3)
#                       con bitrate selezionabile, utilizzando ffmpeg.
# - Scarica Video Completo: Scarica e unisce (muxing) il miglior flusso audio
#                           e video disponibile, mantenendo la qualità originale.
# - Interfaccia Utente: Tkinter GUI con radio button per la selezione della modalità
#                       e visualizzazione dello stato del download.
# - Apri Cartella: Pulsante per aprire la directory di salvataggio finale.
# ==============================================================================

import tkinter as tk
from tkinter import messagebox, filedialog
import yt_dlp
import os
import threading
import subprocess # Necessario per aprire cartelle in modo cross-platform

# ==============================================================================
# 1. FUNZIONI DI DOWNLOAD (CORE LOGIC)
# ==============================================================================

def update_status(app_instance, text):
    """Aggiorna la label di stato nell'interfaccia grafica."""
    app_instance.status_var.set(text)
    app_instance.update_idletasks() 

def start_download_thread(app_instance, url, mode, output_dir, format_output="mp3", bitrate="192k"):
    """Avvia la funzione di download in un thread separato."""
    
    if not url:
        messagebox.showerror("Errore di Input", "L'URL del video non può essere vuoto.")
        return
        
    app_instance.download_button.config(state=tk.DISABLED)
    update_status(app_instance, "Stato: Avvio download in corso...")
    
    thread = threading.Thread(
        target=run_download, 
        args=(app_instance, url, mode, output_dir, format_output, bitrate)
    )
    thread.start()

def run_download(app_instance, url, mode, output_dir, format_output, bitrate):
    """Contiene la logica di yt-dlp per il download e la conversione."""
    try:
        if not os.path.isdir(output_dir):
             os.makedirs(output_dir, exist_ok=True)
             
        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '0%')
                speed = d.get('_speed_str', '')
                update_status(app_instance, f"Stato: Download in corso - {percent} {speed}")
            elif d['status'] == 'finished':
                update_status(app_instance, "Stato: Download completato. Avvio conversione/unione...")

        # Configurazione base yt-dlp (FFmpeg path fisso come da richiesta utente)
        ydl_opts = {
            'noplaylist': True,
            'ffmpeg_location': '/usr/local/bin/ffmpeg', # PATH fornito dall'utente (macOS Homebrew)
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),

    
    # 💡 NUOVA OPZIONE 1: Maschera l'agente utente
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    
    # 💡 NUOVA OPZIONE 2: Usa un server proxy per cambiare IP (vedi Sezione 2)
    # 'proxy': 'http://<IP>:<PORTA>', 
    
    # 💡 IDEA per NUOVA OPZIONE 3: inviare dei Cookie di Sessione fasulli, verosomimil ma non provenienti
    # dal mio pc, vedere come fare...
}
        
        if mode == 1: 
            update_status(app_instance, f"Stato: Preparazione Estrazione Audio ({format_output}@{bitrate})...")
            ydl_opts.update({
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': format_output,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format_output,
                    'preferredquality': bitrate,
                }],
            })

        elif mode == 2: 
            update_status(app_instance, "Stato: Preparazione Download Video Completo...")
            ydl_opts.update({
                'format': 'bestvideo*+bestaudio/best', 
                'merge_output_format': 'mp4',
            })

        # Esecuzione del download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        update_status(app_instance, f"✅ Download completato. File salvato in: {output_dir}")
        messagebox.showinfo("Successo", f"Operazione completata e salvata in:\n{output_dir}")

    except Exception as e:
        error_msg = str(e).split('\n')[0] 
        update_status(app_instance, f"❌ Errore: {error_msg}")
        messagebox.showerror("Errore Operazione", f"Si è verificato un errore:\n{error_msg}\n\nVerifica che:\n1. L'URL sia corretto.\n2. 'ffmpeg' sia installato e nel tuo PATH.")
        print("Errore Operazione", f"Si è verificato un errore:\n{error_msg}\n\nVerifica che:\n1. L'URL sia corretto.\n2. 'ffmpeg' sia installato e nel tuo PATH.")
    finally:
        app_instance.download_button.config(state=tk.NORMAL)


# ==============================================================================
# 2. CLASSE PER L'INTERFACCIA TKINTER
# ==============================================================================

class DownloaderApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Audio/Video Grabber (yt-dlp + Tkinter)")
        self.geometry("600x400")
        self.resizable(False, False)

        # Variabili di controllo
        self.mode_var = tk.IntVar(value=1)
        self.status_var = tk.StringVar(value="Pronto. Seleziona la modalità e inserisci l'URL.")
        self.output_dir_var = tk.StringVar(value=os.getcwd())
        
        self.create_widgets()
        self.update_audio_controls() 

    # --- NUOVO METODO PER APRIRE LA CARTELLA ---
    def open_output_directory(self):
        """Apre la directory di salvataggio usando il comando di sistema appropriato."""
        
        # Ottiene il percorso corrente dalla variabile Tkinter
        directory_path = self.output_dir_var.get()
        
        # Controlla se il percorso esiste
        if not os.path.exists(directory_path):
            messagebox.showerror("Errore", f"Il percorso non esiste:\n{directory_path}")
            return
            
        try:
            if os.name == 'nt': # Windows
                os.startfile(directory_path)
            elif os.uname().sysname == 'Darwin': # macOS
                subprocess.run(['open', directory_path])
            else: # Linux (comune)
                subprocess.run(['xdg-open', directory_path])
                
        except Exception as e:
            messagebox.showerror("Errore Apertura Cartella", f"Impossibile aprire la cartella:\n{directory_path}\nErrore: {e}")
            
    # --- METODI ESISTENTI ---
    
    def create_widgets(self):
        # Frame Principale (padding)
        main_frame = tk.Frame(self, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sezione 1: Modalità di Download (Radio Buttons)
        mode_frame = tk.LabelFrame(main_frame, text="Modalità di Download", padx=10, pady=5)
        mode_frame.pack(fill=tk.X, pady=10)

        tk.Radiobutton(mode_frame, text="Estrai Solo Audio (Default)", variable=self.mode_var, value=1, command=self.update_audio_controls).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="Scarica Video Completo (Audio + Video)", variable=self.mode_var, value=2, command=self.update_audio_controls).pack(side=tk.LEFT, padx=10)

        # Sezione 2: Controlli Audio/Video (URL e Parametri)
        tk.Label(main_frame, text="URL del Video:").pack(fill=tk.X, pady=(10, 0))
        self.url_entry = tk.Entry(main_frame, width=80)
        self.url_entry.pack(fill=tk.X)

        self.audio_params_frame = tk.Frame(main_frame)
        
        # Formato Audio
        tk.Label(self.audio_params_frame, text="Formato Audio:").pack(side=tk.LEFT, padx=(0, 5))
        self.format_var = tk.StringVar(value="mp3")
        formats = ['mp3', 'aac', 'm4a', 'ogg', 'wav']
        self.format_menu = tk.OptionMenu(self.audio_params_frame, self.format_var, *formats)
        self.format_menu.config(width=5)
        self.format_menu.pack(side=tk.LEFT, padx=(0, 15))

        # Bitrate
        tk.Label(self.audio_params_frame, text="Bitrate:").pack(side=tk.LEFT, padx=(0, 5))
        self.bitrate_var = tk.StringVar(value="192k")
        bitrates = ['128k', '192k', '256k', '320k']
        self.bitrate_menu = tk.OptionMenu(self.audio_params_frame, self.bitrate_var, *bitrates)
        self.bitrate_menu.config(width=5)
        self.bitrate_menu.pack(side=tk.LEFT)

        # Sezione 3: Directory di Output e Pulsanti Download/Apri Cartella
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=15)
        
        tk.Label(output_frame, text="Cartella di Salvataggio:").pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=self.output_dir_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # 🔴 CORREZIONE 1: Rimuovere le parentesi da self.select_output_directory()
        tk.Button(output_frame, text="Sfoglia", command=self.select_output_directory).pack(side=tk.LEFT) 
        
        # 🔴 MODIFICA CHIAVE: Creazione di un Frame per affiancare i due pulsanti
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Pulsante 1: AVVIA DOWNLOAD (rimpicciolito in larghezza)
        self.download_button = tk.Button(
            button_frame, 
            text="AVVIA DOWNLOAD", 
            command=self.on_download_click, 
            bg='blue', 
            fg='orange',
            height=2
        )
        # Uso side=tk.LEFT e fill=tk.X per riempire lo spazio disponibile
        self.download_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5)) 

        # Pulsante 2: APRI CARTELLA FILE
        self.open_directory_button = tk.Button(
            button_frame, 
            text="Apri Cartella", 
            command=self.open_output_directory, # Chiama il nuovo metodo
            bg='blue', 
            fg='orange', 
            height=2
        )
        self.open_directory_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Sezione 4: Barra di Stato
        tk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w').pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

    def update_audio_controls(self):
        """Mostra/nasconde i controlli di formato e bitrate in base al Radio Button."""
        if self.mode_var.get() == 1:
            self.audio_params_frame.pack(fill=tk.X, pady=10)
        else:
            self.audio_params_frame.pack_forget()

    def select_output_directory(self):
        """Apre la finestra di dialogo per selezionare la cartella."""
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir_var.set(folder)

    def on_download_click(self):
        """Raccoglie i dati e avvia il download."""
        url = self.url_entry.get()
        mode = self.mode_var.get()
        output_dir = self.output_dir_var.get()
        
        format_output = self.format_var.get()
        bitrate = self.bitrate_var.get()
        
        start_download_thread(self, url, mode, output_dir, format_output, bitrate)

# ==============================================================================
# 3. ESECUZIONE
# ==============================================================================

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()