# Implementazione grafica del CIFRARIO di Cesare,
# un primo e semplice algoritmo di CODIFICA e decodifica testo
# a partire da una chiave, N, di spostamento di lettere (es se n=4,
# si deve spostare di 4 lettere, la A diventa D, la B diventa F ecc).
# L'interfaccia grafica è realizzata con la libreria Tkinter.

import tkinter as tk
from tkinter import Label, Entry, Canvas
import math

# Variabile globale per tenere traccia dell'ID del cerchietto corrente
# Lo inizializziamo a None per il primo avvio del programma.
cerchietto_corrente = None
# Definiamo l'alfabeto come stringa
alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Funzione per codificare una singola lettera
def codifica_lettera(lettera, spostamento):
    """Codifica una lettera applicando uno spostamento."""
    indice = alfabeto.find(lettera.upper())
    nuovo_indice = (indice + spostamento) % 26
    return alfabeto[nuovo_indice]

# Funzione per codificare o decodificare un intero testo
def codifica_decodifica_testo(testo, spostamento, operazione):
    """Applica la codifica o decodifica ad una stringa di testo."""
    risultato = ""
    for lettera in testo:
        if lettera.isalpha():
            if operazione == "cifra":
                risultato += codifica_lettera(lettera, spostamento)
            else:
                risultato += codifica_lettera(lettera, -spostamento)  # Per decodificare, si usa uno spostamento negativo
        else:
            risultato += lettera
    return risultato

# Funzione per calcolare lo spostamento in base alla posizione del clic sul disco
def calcola_spostamento(x, y):
    """Calcola lo spostamento del cifrario in base alle coordinate del clic sul disco esterno."""
    # DEBUG: Mostra le coordinate del clic
    print("DEBUG: calcola_spostamento avviato con x, y =", x, y)
    
    # Centro dell'ovale
    centro_x, centro_y = 300, 300
    
    # Calcola l'angolo in radianti del clic rispetto al centro
    angolo = math.atan2(y - centro_y, x - centro_x)
    
    # Converti l'angolo da radianti a gradi
    angolo_gradi = math.degrees(angolo)
    
    # Aggiungi 360 gradi se l'angolo è negativo per mantenere il range [0, 360)
    if angolo_gradi < 0:
        angolo_gradi += 360
        
    # DEBUG: Mostra l'angolo in gradi
    print("DEBUG: angolo_gradi =", angolo_gradi)
    
    # Dividi il cerchio in 26 sezioni per le 26 lettere dell'alfabeto
    numero_sezioni = 26
    ampiezza_sezione = 360 / numero_sezioni
    
    # Calcola l'indice della sezione in base all'angolo
    indice_sezione = int(angolo_gradi // ampiezza_sezione)
    
    # DEBUG: Mostra l'indice della sezione calcolato
    print("DEBUG: indice_sezione =", indice_sezione)
    
    # Lo spostamento corrisponde all'indice della sezione
    spostamento = indice_sezione
    
    return spostamento

# Funzione separata per gestire la visualizzazione del cerchietto di evidenziazione
def crea_cerchietto(spostamento):
    """Crea un cerchietto semitrasparente sulla sezione cliccata, rimuovendo il precedente."""
    global cerchietto_corrente
    
    # Calcola l'angolo di inizio della sezione
    angolo_inizio = spostamento * 360 / 26
    
    # Calcola le coordinate del centro della sezione per posizionare il cerchietto
    x_cerchietto = centro_x + raggio_esterno * 0.8 * math.cos(math.radians(angolo_inizio + (180/26)))
    y_cerchietto = centro_y + raggio_esterno * 0.8 * math.sin(math.radians(angolo_inizio + (180/26)))
    
    # DEBUG: Mostra le coordinate dove verrà disegnato il cerchietto
    print("DEBUG: Coordinate del cerchietto:", x_cerchietto, y_cerchietto)
    
    # Rimuovi il cerchietto precedente se esiste
    if cerchietto_corrente is not None:
        w.delete(cerchietto_corrente)
        print("DEBUG: Cerchietto eliminato")
        
    # Crea un nuovo cerchietto. A causa di un errore nella versione di Tkinter,
    # non possiamo usare la trasparenza. Usiamo un colore solido più chiaro.
    cerchietto_corrente = w.create_oval(x_cerchietto - 15, y_cerchietto - 15,
                                          x_cerchietto + 15, y_cerchietto + 15,
                                          outline="", fill="#FF6347") # "Tomato"
    w.tag_raise(cerchietto_corrente)
    print("DEBUG: Cerchietto creato")

# Funzione per gestire il clic sul disco
def clicca_sul_disco(event):
    """Funzione principale per gestire il clic sul disco esterno."""
    print("DEBUG: clicca_sul_disco avviato")
    
    # Calcola lo spostamento in base al clic
    spostamento = calcola_spostamento(event.x, event.y)
    
    # Chiama la funzione per creare il cerchietto di evidenziazione
    crea_cerchietto(spostamento)
    
    # Ottieni il testo dal campo di input
    testo_chiaro = entry_testo.get()
    
    # Seleziona l'operazione (cifra o decifra)
    operazione = var.get()

    # Codifica o decodifica il testo
    risultato = codifica_decodifica_testo(testo_chiaro, spostamento, operazione)
    
    # Visualizza il risultato nel label
    label_risultato.config(text=risultato)

# --- Impostazioni dell'interfaccia grafica ---

# Dimensione del Canvas
canvas_width = 600
canvas_height = 600

# Creazione della finestra principale
master = tk.Tk()
master.title("Cifrario di Cesare con Disco Rotante")

# Creazione del Canvas
w = Canvas(master, width=canvas_width, height=canvas_height, background="Yellow")
w.pack()

# Parametri per disegnare gli ovali
centro_x, centro_y = 300, 300
raggio_interno = 100
raggio_esterno = 150

# Creazione degli ovali concentrici
ovale_interno = w.create_oval(centro_x - raggio_interno, centro_y - raggio_interno,
                              centro_x + raggio_interno, centro_y + raggio_interno,
                              fill="blue")
ovale_esterno = w.create_oval(centro_x - raggio_esterno, centro_y - raggio_esterno,
                              centro_x + raggio_esterno, centro_y + raggio_esterno,
                              fill="lightgray")

# Disegno delle sezioni e delle lettere
numero_sezioni = 26
for i in range(numero_sezioni):
    angolo_inizio = i * 360 / numero_sezioni
    
    # Calcola le coordinate del centro della sezione per posizionare la lettera
    x = centro_x + raggio_esterno * 0.8 * math.cos(math.radians(angolo_inizio + 180 / numero_sezioni))
    y = centro_y + raggio_esterno * 0.8 * math.sin(math.radians(angolo_inizio + 180 / numero_sezioni))
    
    # Disegna l'arco che delimita la sezione
    w.create_arc(centro_x - raggio_esterno, centro_y - raggio_esterno, 
                 centro_x + raggio_esterno, centro_y + raggio_esterno, 
                 start=angolo_inizio, extent=360/numero_sezioni, 
                 style=tk.ARC, outline="black")
                 
    # Disegna la lettera al centro della sezione
    w.create_text(x, y, text=alfabeto[i])

# --- Elementi dell'interfaccia utente ---

# Campo di input per il testo
entry_testo = Entry(master, width=50)
entry_testo.pack(pady=10)

# Label per visualizzare il risultato
label_risultato = Label(master, text="", font=("Helvetica", 14), bg="white", relief="sunken", width=40)
label_risultato.pack(pady=10)

# Pulsanti radio per scegliere tra cifratura e decifratura
var = tk.StringVar(value="cifra")
radio_cifra = tk.Radiobutton(master, text="Cifra", variable=var, value="cifra")
radio_decifra = tk.Radiobutton(master, text="Decifra", variable=var, value="decifra")
radio_cifra.pack(side="left", padx=20)
radio_decifra.pack(side="right", padx=20)

# Associa l'evento clic all'ovale esterno
w.tag_bind(ovale_esterno, "<Button-1>", clicca_sul_disco)

# Avvio del ciclo principale di Tkinter
master.mainloop()
