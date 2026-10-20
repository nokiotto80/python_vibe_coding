# -*- coding: utf-8 -*-
"""
===============================================================================
@PROGETTO     : Internet Live Stats Dashboard
@AUTORE       : Macbook_Vincenzo & AI Assistant
@DATA         : 23 Giugno 2026
@VERSIONE     : 1.0
@AMBIENTE     : Python 3.x (Ottimizzato per l'IDE SPYDER)
===============================================================================
@SCOPO_DEL_WORK:
Creare un'applicazione desktop performante che emuli visivamente e logicamente
il celebre sito web "Internet Live Stats". Il programma genera contatori in 
tempo reale basati su stime di crescita globale della rete, fornendo un impatto 
visivo immediato senza saturare la banda con chiamate API asincrone continue.

@PIPELINE_PROCESSUALE:
1. Inizializzazione della finestra principale (Root) con tema scuro cyberpunk.
2. Definizione del Data Core: dizionario strutturato contenente lo stato 
   numerico iniziale e il tasso di incremento algoritmico per millisecondo.
3. Generazione dinamica della griglia: posizionamento geometrico automatico dei 
   Frame quadrati tramite operazione di divisione intera (//) e modulo (%).
4. Rendering degli elementi testuali (Titolo, Contatore Neon, Unità di misura).
5. Avvio del ciclo ad eventi asincrono (.after) per l'aggiornamento costante 
   delle label a intervalli di 100ms senza bloccare il Thread grafico (Main Loop).

@PACKAGE_USATI:
- tkinter       : Libreria standard de-facto per la creazione di GUI in Python.
- tkinter.ttk   : Estensione per il controllo avanzato degli stili widget.

Evoluzione della dashboard con l'integrazione di un bordo perimetrale animato
ad effetto gradiente continuo (stile Times Square / Neon Cyberpunk).

02/09/2026: 
    - aumentato leggermente lo spessore dei bordi al neon(da 10 a 12)
    - aggiunte 3 statistiche: Storie Instagram, messaggi Whastapp e Telegram
===============================================================================
"""

import tkinter as tk
import colorsys

class InternetLiveStatsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("INTERNET LIVE STATS - NEON DASHBOARD")
        self.geometry("1150x750")
        self.configure(bg="#0b0f19")
        
        # Stato dell'animazione (angolo di fase del colore)
        self.colore_fase = 0.0
        
        # Spessore del bordo neon (circa 6 pixel / mezzo centimetro visivo)
        self.spessore_bordo = 12
        
        # Data Core   #DIZIONARIO: Key:Value: [valore iniziale: incremento]
        self.stats = {
            "EMAIL INVIATE OGGI": [2500000000, 340.0, "email inviate"],
            "RICERCHE SU GOOGLE": [55000000, 9.0, "query eseguite"],
            "PAGINE WEB VISITATE": [185400120, 120.0, "pagine visualizzate"],
            "TWEET INVIATI OGGI": [500000000, 0.92, "micro-post pubblicati"],
            "VIDEO VISTI SU YOUTUBE": [4500000000, 11.0, "riproduzioni video"],
            "TRAFFICO DATI GLOBALE": [12000000, 45.0, "GigaByte (GB) trasferiti"],
            "STORIE SU INSTAGRAM": [34000000, 25.0, "al minuto"],
            "MESSAGGI SU WHATSAPP": [671000000, 20.0, "al minuto"],
            "MESSAGGI SU TELEGRAM": [243000500, 20.0, "al minuto"]
        }
        
        self.labels_dinamiche = {}
        
        self.crea_interfaccia()
        self.aggiorna_contatori_live()
        self.disegna_cornice_neon() # Avvio del loop dell'animazione del bordo

    def crea_interfaccia(self):
        # --- CANVAS PER IL BORDO ANIMATO ---
        # Questo componente fa da sfondo totale e conterrà il disegno delle linee neon
        self.canvas_bordo = tk.Canvas(self, bg="#0b0f19", highlightthickness=0)
        self.canvas_bordo.pack(fill=tk.BOTH, expand=True)
        
        # Intercettiamo il ridimensionamento della finestra per riadattare la cornice
        self.canvas_bordo.bind("<Configure>", self.on_window_resize)
        
        # --- CONTENITORE PRINCIPALE (SOPRA IL CANVAS) ---
        # Usiamo .place() per sovrapporlo al canvas, lasciando scoperto il perimetro (il mezzo centimetro)
        self.main_container = tk.Frame(self.canvas_bordo, bg="#0b0f19")
        
        # --- INTESTAZIONE SUPERIORE ---
        frame_titolo = tk.Frame(self.main_container, bg="#0b0f19", pady=10)
        frame_titolo.pack(fill=tk.X)
        
        lbl_main_title = tk.Label(frame_titolo, text="INTERNET LIVE STATS", font=("Arial", 24, "bold"), fg="#00f2fe", bg="#0b0f19")
        lbl_main_title.pack()
        
        lbl_sub_title = tk.Label(frame_titolo, text="Simulazione algoritmica della rete con perimetro a gradiente continuo", font=("Arial", 10, "italic"), fg="#7289da", bg="#0b0f19")
        lbl_sub_title.pack(pady=(5, 0))

        # --- GRIGLIA STATISTICHE ---
        grid_frame = tk.Frame(self.main_container, bg="#0b0f19", padx=10, pady=10)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        COLONNE_MAX = 3
        for indice, (chiave, info) in enumerate(self.stats.items()):
            riga = indice // COLONNE_MAX
            colonna = indice % COLONNE_MAX
            
            # Frame quadrato con bordo doppio standard (groove)
            card_quadrata = tk.Frame(grid_frame, bg="#131a2c", bd=4, relief="groove", highlightbackground="#1e293b")
            card_quadrata.grid(row=riga, column=colonna, padx=15, pady=15, sticky="nsew")
            
            # NOTA: Usiamo expand=True per CENTRARE verticalmente i testi all'interno del quadrato
            lbl_nome = tk.Label(card_quadrata, text=chiave, font=("Arial", 11, "bold"), fg="#4facfe", bg="#131a2c")
            lbl_nome.pack(expand=True, anchor="center", padx=10, pady=(15, 0))
            
            lbl_valore = tk.Label(card_quadrata, text="", font=("Consolas", 22, "bold"), fg="#39ff14", bg="#131a2c")
            lbl_valore.pack(expand=True, anchor="center", padx=10)
            
            lbl_unita = tk.Label(card_quadrata, text=info[2], font=("Arial", 9), fg="#7289da", bg="#131a2c")
            lbl_unita.pack(expand=True, anchor="center", padx=10, pady=(0, 15))
            
            self.labels_dinamiche[chiave] = lbl_valore
            
        for i in range(3): grid_frame.rowconfigure(i, weight=1) #qui vanno le RIGHE; se aumentano, aumentare questo indice
        for j in range(COLONNE_MAX): grid_frame.columnconfigure(j, weight=1)

    def on_window_resize(self, event):
        """ Gestisce il posizionamento del pannello quando la finestra si allarga o stringe """
        w = event.width
        h = event.height
        # Posiziona il pannello interno scalato di "self.spessore_bordo" pixel per lato
        self.main_container.place(
            x=self.spessore_bordo, 
            y=self.spessore_bordo, 
            width=w - (self.spessore_bordo * 2), 
            height=h - (self.spessore_bordo * 2)
        )

    def disegna_cornice_neon(self):
        """
        Genera l'effetto Times Square calcolando i colori dello spettro a tempo continuo
        e disegnando 4 linee perimetrali spesse sul Canvas.
        """
        # Puliamo i vecchi disegni sul canvas per non accumulare memoria
        self.canvas_bordo.delete("neon")
        
        w = self.canvas_bordo.winfo_width()
        h = self.canvas_bordo.winfo_height()
        
        if w > 10 and h > 10:
            # Calcoliamo 4 colori diversi per i 4 angoli/lati per creare il gradiente di passaggio
            colori = []
            for i in range(4):
                # Spostiamo la tonalità (H) unendo la fase temporale ad uno sfasamento geometrico (i * 0.25)
                hue = (self.colore_fase + (i * 0.15)) % 1.0
                # Convertiamo da HSV a codice Esadecimale comprensibile da Tkinter
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                hex_color = f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'
                colori.append(hex_color)
            
            s = self.spessore_bordo / 2
            # Disegnamo i 4 lati con colori sfalsati per creare la transizione continua
            self.canvas_bordo.create_line(0, s, w, s, fill=colori[0], width=self.spessore_bordo, tags="neon") # Alto
            self.canvas_bordo.create_line(w-s, 0, w-s, h, fill=colori[1], width=self.spessore_bordo, tags="neon") # Destra
            self.canvas_bordo.create_line(w, h-s, 0, h-s, fill=colori[2], width=self.spessore_bordo, tags="neon") # Basso
            self.canvas_bordo.create_line(s, h, s, 0, fill=colori[3], width=self.spessore_bordo, tags="neon") # Sinistra
            
        # Incrementiamo la fase del colore. Più è alto questo valore, più è veloce lo shift cromatico
        self.colore_fase += 0.005
        if self.colore_fase > 1.0: 
            self.colore_fase = 0.0
            
        # Loop ultra-veloce (ogni 30ms) dedicato esclusivamente alla fluidità della luce neon
        self.after(30, self.disegna_cornice_neon)

    def aggiorna_contatori_live(self):
        """ Mantiene il refresh dei dati indipendentemente dalla grafica della cornice """
        for chiave, info in self.stats.items():
            info[0] += info[1]
            valore_formattato = f"{int(info[0]):,}".replace(",", ".")
            self.labels_dinamiche[chiave].config(text=valore_formattato)
            
        self.after(100, self.aggiorna_contatori_live)

if __name__ == "__main__":
    app = InternetLiveStatsApp()
    app.mainloop()
