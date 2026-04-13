#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 16:49:48 2025

@author: macbook_vincenzo
A.I. created by Google Gemini 
successively modified
MODIFICARE, AGGIUNGERE LA DATA SOTTO, usando i "pezzi" da lui generati. possibilemnte SENZA chiedere
a GEMINI,,,un po di esercizio non guasta!
"""

import tkinter as tk
import time
from tkinter import PhotoImage
from PIL import Image, ImageTk # Aggiungi queste importazioni se vuoi usare PNG con trasparenza


class DigitalClock:
    def __init__(self, root):
        
        self.root = root
        self.root.title("Orologio Digitale 7 Segmenti")
        self.root.geometry("700x270") # Dimensione della finestra
        self.root.resizable(False, False) # Non ridimensionabile

        self.segment_color_on = "red"  # Colore dei segmenti accesi
        self.segment_color_off = "#330000" # Colore dei segmenti spenti (grigio scuro/rosso molto scuro)
        self.bg_color = "black" # Colore di sfondo del display

        self.segment_width = 10 # Spessore dei segmenti
        self.digit_width = 60 # Larghezza di una singola cifra
        self.digit_height = 100 # Altezza di una singola cifra
        self.padding = 10 # Spazio tra le cifre
        self.colon_width = 15 # Larghezza dei punti dei due punti
        

        # Definizioni dei segmenti per ogni numero (0-9)
        # Ogni tuple rappresenta (segment_A, segment_B, ..., segment_G)
        # True = segmento acceso, False = segmento spento
        self.segments_map = {
            '0': (True, True, True, True, True, True, False),  # A B C D E F G
            '1': (False, True, True, False, False, False, False),
            '2': (True, True, False, True, True, False, True),
            '3': (True, True, True, True, False, False, True),
            '4': (False, True, True, False, False, True, True),
            '5': (True, False, True, True, False, True, True),
            '6': (True, False, True, True, True, True, True),
            '7': (True, True, True, False, False, False, False),
            '8': (True, True, True, True, True, True, True),
            '9': (True, True, True, True, False, True, True),
            ' ': (False, False, False, False, False, False, False) # Per spazio vuoto
        }
        
        self.segments_map_lettere = {
            # Lettere standard
            'A': (True, True, True, False, True, True, True),  # A B C D E F G (A maiuscola)
            'b': (False, False, True, True, True, True, True), # (B minuscola per chiarezza)
            'C': (True, False, False, True, True, True, False), # (C maiuscola)
            'd': (False, True, True, True, True, False, True), # (D minuscola per chiarezza)
            'E': (True, False, False, True, True, True, True), # (E maiuscola)
            'F': (True, False, False, False, True, True, True), # (F maiuscola)
            'G': (True, False, True, True, True, True, False), # (G maiuscola)
            'H': (False, True, True, False, True, True, True), # (H maiuscola)
            'I': (False, False, False, False, True, False, False), # (Trattino centrale orizzontale)
            'L': (False, False, False, True, True, True, False), # (L maiuscola)
            'N': (False, True, True, False, True, False, True), # (N maiuscola con G laterale spento)
            'O': (True, True, True, True, True, True, False),  # (O maiuscola - come cifra 0)
            'P': (True, True, False, False, True, True, True), # (P maiuscola)
            'r': (False, False, False, False, True, False, True), # (r minuscola per chiarezza)
            
            'S': (True, False, True, True, False, True, True),  # (S maiuscola - come cifra 5)
            'T': (False, False, False, True, True, True, True), # (T/t minuscola, simile a 7 senza A)
            'U': (False, True, True, True, True, True, False),  # (U maiuscola)
            'V': (False, False, True, False, True, False, True), #(V maiuscola)
            'Y': (False, True, True, True, False, True, True),  # (Y maiuscola)
        
            # Lettera per lo spazio vuoto
            ' ': (False, False, False, False, False, False, False)
        }
        # Creazione del Canvas principale per il display dell'orologio
        self.canvas = tk.Canvas(root, bg=self.bg_color, highlightthickness=2)
       
        self.canvas.pack(expand=True, fill="both")
        
        # --- INIZIO MODIFICHE PER L'ICONA ---
        try:
      # Per supportare i file PNG con trasparenza, è consigliabile usare Pillow (PIL).
      # Assicurati di averla installata: pip install Pillow
      
      # Carica l'immagine usando Pillow
         original_image = Image.open("/Users/macbook_vincenzo/Python/clock_icon.png")
         original_image2= Image.open("/Users/macbook_vincenzo/Python/calendar.png")
      
      # Ridimensiona l'immagine se necessario (es. a 60x60 pixel)
       # Puoi regolare queste dimensioni in base a quanto vuoi che sia grande l'icona
         resized_image = original_image.resize((50, 50), Image.LANCZOS) # o Image.LANCZOS per migliore qualità
         resized_image2=original_image2.resize((50,50),Image.LANCZOS)
       
      # Converte l'immagine Pillow in un formato che Tkinter può usare
         self.clock_icon = ImageTk.PhotoImage(resized_image)
         self.date_icon = ImageTk.PhotoImage(resized_image2)
      
      # Mostra l'icona dell'orologio prima dell'ora
      # Le coordinate (x, y) definiscono il centro dell'immagine per anchor="center"
      # O (x, y) definiscono il punto sinistro per anchor="w" (West)
      # Regola le coordinate 50, 50 in base a dove vuoi posizionare l'icona
      # Il 50 in X è una posizione di esempio, potresti volerlo più a sinistra
         self.canvas.create_image(25, self.digit_height / 2 + self.padding, anchor="w",image=self.clock_icon)
         self.canvas.create_image(25, self.digit_height / 2 + self.padding +150, anchor="w",image=self.date_icon)
      
        except FileNotFoundError:
         print("Errore: Immagine 'clock_icon.png' non trovata. Assicurati che il percorso sia corretto.")
        except Exception as e:
         print(f"Si è verificato un errore durante il caricamento dell'immagine: {e}")
  # --- FINE MODIFICHE PER L'ICONA ---

        # Memorizzeremo gli oggetti Canvas per ogni cifra (ore, minuti, secondi) , per i due punti e le lettere
        self.digits = []
        self.letters = []
        self.colons = []

        # Posizionamento delle cifre e dei due punti
        # Ore
        self.digits.append(self.create_digit_display(self.padding)) # Prima cifra ore
        self.digits.append(self.create_digit_display(self.padding + self.digit_width + self.padding)) # Seconda cifra ore

        # Primo gruppo di due punti
        self.colons.append(self.create_colon_display(self.padding + 2 * (self.digit_width + self.padding)))

        # Minuti
        self.digits.append(self.create_digit_display(self.padding + 2 * (self.digit_width + self.padding) + self.colon_width + self.padding)) # Prima cifra minuti
        self.digits.append(self.create_digit_display(self.padding + 3 * (self.digit_width + self.padding) + self.colon_width + self.padding)) # Seconda cifra minuti

        # Secondo gruppo di due punti (opzionale, se vuoi anche i secondi)
        self.colons.append(self.create_colon_display(self.padding + 4 * (self.digit_width + self.padding) + self.colon_width + self.padding))

        # Secondi (opzionale)
        self.digits.append(self.create_digit_display(self.padding + 4 * (self.digit_width + self.padding) + 2 * self.colon_width + 2 * self.padding)) # Prima cifra secondi
        self.digits.append(self.create_digit_display(self.padding + 5 * (self.digit_width + self.padding) + 2 * self.colon_width + 2 * self.padding)) # Seconda cifra secondi
         
     ##TEST visualizzazione lettera
        BASE_Y_OFFSET = self.padding + self.digit_height + 50 #la Y(altezza) NON cambia, è la X (orizzontale) che varia
        
        # --- PRIMA LETTERA (N) ---
        x_offset_lettera1 = self.padding 
        self.letters.append(self.create_digit_display(x_offset_lettera1, y_offset=BASE_Y_OFFSET))
        
        # --- SECONDA LETTERA (O) ---
        # X: Spostati a destra del primo display (larghezza + padding)
        x_offset_lettera2 = x_offset_lettera1 + self.digit_width + self.padding
        # Y: Usa lo stesso offset BASE_Y_OFFSET
        self.letters.append(self.create_digit_display(x_offset_lettera2, y_offset=BASE_Y_OFFSET))
        
        # --- TERZA LETTERA (V) ---
        # X: Spostati a destra del secondo display
        x_offset_lettera3 = x_offset_lettera2 + self.digit_width + self.padding
        # Y: Usa lo stesso offset BASE_Y_OFFSET
        self.letters.append(self.create_digit_display(x_offset_lettera3, y_offset=BASE_Y_OFFSET))
        
        ## FINE TEST
        # --- SPAZIO (Display 4) ---
        x_offset_spazio = x_offset_lettera3 + self.digit_width + self.padding
        self.letters.append(self.create_digit_display(x_offset_spazio, y_offset=BASE_Y_OFFSET))
        
        # --- GIORNO DECINA (Display 5) ---
        x_offset_giorno1 = x_offset_spazio + self.digit_width + self.padding
        self.letters.append(self.create_digit_display(x_offset_giorno1, y_offset=BASE_Y_OFFSET))
        
        # --- GIORNO UNITÀ (Display 6) ---
        x_offset_giorno2 = x_offset_giorno1 + self.digit_width + self.padding
        self.letters.append(self.create_digit_display(x_offset_giorno2, y_offset=BASE_Y_OFFSET))
  
                # Update: 2012026 SECONDO SPAZIO (Display 7, Indice [6]) ---
        x_offset_spazio2 = x_offset_giorno2 + self.digit_width + self.padding
        self.letters.append(self.create_digit_display(x_offset_spazio2, y_offset=BASE_Y_OFFSET))
        
        # Update: 2012026 ANNO DECINA (Display 8, Indice [7]) ---
        x_offset_anno1 = x_offset_spazio2 + self.digit_width + self.padding
        self.letters.append(self.create_digit_display(x_offset_anno1, y_offset=BASE_Y_OFFSET))
        
        # --- ANNO UNITÀ (Display 9, Indice [8]) ---
        x_offset_anno2 = x_offset_anno1 + self.digit_width + self.padding
        self.letters.append(self.create_digit_display(x_offset_anno2, y_offset=BASE_Y_OFFSET))
        
            # 2. SOLO ORA CHIAMA L'AGGIORNAMENTO
        # Questa riga deve essere DOPO tutti gli append!
        self.update_clock()

    # Funzione per creare un display per una singola cifra (7 segmenti)
    def create_digit_display(self, x_offset,y_offset=None):
        digit_segments = []
        
        x_offset = x_offset +70
        base_y = y_offset if y_offset is not None else self.padding
        
        # Le coordinate sono relative all'inizio del canvas della singola cifra
        # Segmento A (top)
        digit_segments.append(self.canvas.create_rectangle(
            x_offset + self.segment_width, base_y,
            x_offset + self.digit_width - self.segment_width, base_y+ self.segment_width,
            fill=self.segment_color_off, outline=self.segment_color_off
        ))
        
        # Segmento B (top-right)
        digit_segments.append(self.canvas.create_rectangle(
            x_offset + self.digit_width - self.segment_width, base_y+ self.segment_width,
            x_offset + self.digit_width, base_y + self.digit_height / 2 - self.segment_width / 2,
            fill=self.segment_color_off, outline=self.segment_color_off
        ))

        # Segmento C (bottom-right)
        digit_segments.append(self.canvas.create_rectangle(
            x_offset + self.digit_width - self.segment_width, base_y+ self.digit_height / 2 + self.segment_width / 2,
            x_offset + self.digit_width, base_y + self.digit_height - self.segment_width,
            fill=self.segment_color_off, outline=self.segment_color_off
        ))
        
        # Segmento D (bottom)
        digit_segments.append(self.canvas.create_rectangle(
            x_offset + self.segment_width, base_y + self.digit_height - self.segment_width,
            x_offset + self.digit_width - self.segment_width, base_y + self.digit_height,
            fill=self.segment_color_off, outline=self.segment_color_off
        ))

        # Segmento E (bottom-left)
        digit_segments.append(self.canvas.create_rectangle(
            x_offset, base_y + self.digit_height / 2 + self.segment_width / 2,
            x_offset + self.segment_width, base_y + self.digit_height - self.segment_width,
            fill=self.segment_color_off, outline=self.segment_color_off
        ))

        # Segmento F (top-left)
        digit_segments.append(self.canvas.create_rectangle(
            x_offset, base_y + self.segment_width,
            x_offset + self.segment_width, base_y + self.digit_height / 2 - self.segment_width / 2,
            fill=self.segment_color_off, outline=self.segment_color_off
        ))

        # Segmento G (middle)
        digit_segments.append(self.canvas.create_rectangle(
            x_offset + self.segment_width, base_y + self.digit_height / 2 - self.segment_width / 2,
            x_offset + self.digit_width - self.segment_width, base_y + self.digit_height / 2 + self.segment_width / 2,
            fill=self.segment_color_off, outline=self.segment_color_off
        ))
        
        return digit_segments

    # Funzione per creare i punti dei due punti (colons)
    def create_colon_display(self, x_offset):
        x_offset = x_offset +70
        colon_dots = []
        dot_radius = self.segment_width / 2
        dot_padding_y = self.digit_height / 4

        # Punto superiore
        colon_dots.append(self.canvas.create_oval(
            x_offset, self.padding + dot_padding_y - dot_radius,
            x_offset + self.colon_width, self.padding + dot_padding_y + dot_radius,
            fill=self.segment_color_on, outline=self.segment_color_on
        ))

        # Punto inferiore
        colon_dots.append(self.canvas.create_oval(
            x_offset, self.padding + 3 * dot_padding_y - dot_radius,
            x_offset + self.colon_width, self.padding + 3 * dot_padding_y + dot_radius,
            fill=self.segment_color_on, outline=self.segment_color_on
        ))
        
        return colon_dots

    # Funzione per impostare i segmenti di una cifra in base al numero
    def set_digit(self, digit_segments, number_char):
        segment_states = self.segments_map.get(number_char, self.segments_map[' ']) # Ottiene lo stato dei segmenti per il carattere
        
        for i, state in enumerate(segment_states):
            color = self.segment_color_on if state else self.segment_color_off
            self.canvas.itemconfig(digit_segments[i], fill=color, outline=color)
            
    ###TEST Visualizzazione lettera

    def set_letters(self, digit_segments, letter_char):
            segment_states = self.segments_map_lettere.get(letter_char, self.segments_map_lettere[' ']) # Ottiene lo stato dei segmenti per il carattere
            
            for i, state in enumerate(segment_states):
                color = self.segment_color_on if state else self.segment_color_off
                self.canvas.itemconfig(digit_segments[i], fill=color, outline=color)    
        
        
    # Funzione per aggiornare l'orologio
    def update_clock(self):
      
        current_time = time.strftime("%H%M%S") # Formato HHMMSS
        current_data = time.strftime("%d%m%y") # Formato GGMMYY
        current_hour = int(current_time[0:2]) # Estrai l'ora come intero
        current_minute = int(current_time[2:4]) # Estrai i minuti come intero
        current_second = int(current_time[4:6]) # Estrai i secondi come intero
        
        
        # Aggiorna le cifre delle ore
        self.set_digit(self.digits[0], current_time[0]) # Prima cifra ora
        self.set_digit(self.digits[1], current_time[1]) # Seconda cifra ora

        # Aggiorna le cifre dei minuti
        self.set_digit(self.digits[2], current_time[2]) # Prima cifra minuto
        self.set_digit(self.digits[3], current_time[3]) # Seconda cifra minuto

        # Aggiorna le cifre dei secondi
        self.set_digit(self.digits[4], current_time[4]) # Prima cifra secondo
        self.set_digit(self.digits[5], current_time[5]) # Seconda cifra secondo
        
        # # Aggiorna le cifre de giorno della DATA
        # self.set_digit(self.date_digits[0], current_data[0]) # Prima cifra del giorno
        # self.set_digit(self.date_digits[1], current_data[1]) # Seconda cifra del giorno
        
        # Recupera il giorno corrente (es. "02")
        current_day = time.strftime("%d") 
        
        # Recupera l'anno corrente (es. "26")
        current_year = time.strftime("%y") 
        
       # 1. Recupera il numero del mese corrente (01, 02, ... 12)
        month_number = int(time.strftime("%m"))
        
        # 2. Crea il dizionario dei mesi
        months_map = {
            1: "GEN", 2: "FEB", 3: "MAr", 4: "APr",
            5: "MAG", 6: "GIU", 7: "LUG", 8: "AGO",
            9: "SET", 10: "OTT", 11: "NOV", 12: "DIC"
        }
        
        # 3. Prendi la stringa corrispondente (es. "GEN")
        current_month_str = months_map[month_number]
        
        
        # 3. Imposta le cifre del GIORNO (5° e 6° display, indici [4] e [5])
        # Usiamo set_digit perché sono numeri!
        self.set_digit(self.letters[0], current_day[0]) # Decina del giorno
        self.set_digit(self.letters[1], current_day[1]) # Unità del giorno
        
        # 2. Imposta lo SPAZIO (il 4° display, indice [3])
        # Assicurati di avere ' ': (False, False, False, False, False, False, False) nella mappa
        self.set_letters(self.letters[2], ' ') 
        
        
        # 4. Invia le lettere ai primi 3 display
        self.set_letters(self.letters[3], current_month_str[0]) # Prima lettera MESE
        self.set_letters(self.letters[4], current_month_str[1]) # Seconda lettera MESE
        self.set_letters(self.letters[5], current_month_str[2]) # Terza lettera MESE
        
   
 
        
        # A questo punto, completo ,con la stessa logica, array, 
        #con un altro spazio e l'ANNO pure vai!
        # In questo:
        self.set_letters(self.letters[6], ' ')
        
        # 3. Imposta le cifre per l'ANNO (5° e 6° display, indici [7] e [8])
        # Usiamo set_digit perché sono numeri!
        self.set_digit(self.letters[7], current_year[0]) # Decina dell'ANNO
        self.set_digit(self.letters[8], current_year[1]) # Unità dell'ANNO

        #################FINE TEST


            # --- INIZIO MODIFICA PER IL LAMPEGGIO DEI DUE PUNTI ---
        # Il sesto carattere di current_time (current_time[5]) è il secondo corrente.
        # Controlliamo se il secondo è pari o dispari per farli lampeggiare.
        if int(current_time[5]) % 2 == 0:
            # Secondi pari: i due punti sono accesi
            colon_color = self.segment_color_on
        else:
            # Secondi dispari: i due punti sono spenti (colore del background o segment_color_off)
            colon_color = self.bg_color # O self.segment_color_off se preferisci un rosso scuro

        for dot in self.colons[1]: # Itera sui singoli punti all'interno di un gruppo
                self.canvas.itemconfig(dot, fill=colon_color, outline=colon_color)
        # --- FINE MODIFICA PER IL LAMPEGGIO DEI SECONDI DUE PUNTI ---
        
        # --- Gestione del lampeggio del PRIMO gruppo di due punti (tra ore e minuti) ---
        # Lampeggia solo allo scatto da un'ora alla successiva.
        # Il lampeggio avviene per un solo secondo (quando i minuti e i secondi sono 00)
        if current_minute == 0 and current_second == 0 and self.last_hour != current_hour:
            # Se è scattata una nuova ora (e solo per un secondo)
            self.last_hour = current_hour # Aggiorna l'ultima ora per evitare lampeggi continui
            hours_colon_color = self.segment_color_on # Accendi i punti
        elif current_minute == 0 and current_second == 1 and self.last_hour == current_hour:
            # Dopo un secondo, li spegni per dare l'effetto di un singolo lampo
            hours_colon_color = self.bg_color
        else:
            # In tutti gli altri momenti, i punti sono accesi
            hours_colon_color = self.segment_color_on
            # Assicurati che last_hour sia aggiornato se il minuto è > 0, per reset della condizione
            if current_minute > 0 or current_second > 1: # Resetta last_hour se non siamo all'inizio dell'ora
                self.last_hour = current_hour 

        # Applica il colore al primo gruppo di due punti (self.colons[0])
        for dot in self.colons[0]:
            self.canvas.itemconfig(dot, fill=hours_colon_color, outline=hours_colon_color)
            
        # Chiamata ricorsiva dopo 1 secondo
        self.root.after(1000, self.update_clock)

# Funzione principale per l'esecuzione
if __name__ == "__main__":
    root = tk.Tk()
    clock = DigitalClock(root)
    root.mainloop()