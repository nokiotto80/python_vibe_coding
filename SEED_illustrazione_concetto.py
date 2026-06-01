# =============================================================================
# DATA: 17 Maggio 2026
# AUTORI: Utente & Gemini (Il tuo assistente AI)
# ARGOMENTO: Generazione deterministica di TIPI DI DATI eterogenei in Python
# FUNZIONI:
#   - Checkbox per switch modalità (Numeri vs Tutti i Tipi)
#   - Generatori di stringhe per: Tensori, DataFrame, Irrazionali, Stringhe, Pixel
#   - Gestione del suono tramite stringhe onomatopeiche/frequenze
# =============================================================================

import tkinter as tk
from tkinter import ttk
import random
import math

# --- GENERATORI DI TIPI DI DATI CASUALI ---

def gen_irrazionale():
    # Genera un'approssimazione di un irrazionale casuale (es. radici o pi greco)
    base = random.choice([math.pi, math.e, math.sqrt(2), math.sqrt(3), math.sqrt(5)])
    return f"Float (Irraz.):\n{base * random.randint(1, 5):.6f}..."

def gen_tensore():
    # Simula un tensore/matrice 3x3 (stile PyTorch/NumPy)
    righe = []
    for _ in range(3):
        riga = [str(random.randint(0, 9)) for _ in range(3)]
        righe.append(" " + " ".join(riga) + " ")
    return f"Tensor (3x3):\n[" + "\n".join(righe) + "]"

def gen_dataframe():
    # Simula un mini DataFrame Pandas
    col_name = random.choice(["Età", "Prezzo", "Score", "Temp"])
    return f"DataFrame (Pandas):\n   Idx | {col_name}\n   0   | {random.randint(10, 99)}\n   1   | {random.randint(10, 99)}"

def gen_stringa():
    # Genera una stringa casuale di caratteri (Stile Chiave Crittografica/Hash)
    caratteri = "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz0123456789"
    stringa = "".join(random.choice(caratteri) for _ in range(8))
    return f"Str (Hash):\n'{stringa}'"

def gen_suono():
    # Rappresentazione di un dato Audio (Frequenza o Onda)
    nota = random.choice(["Do", "Re", "Mi", "Fa", "Sol", "La", "Si"])
    freq = random.randint(220, 880)
    return f"Audio (Wave):\n🎵 {nota} ({freq}Hz)"

def gen_pixel():
    # Rappresentazione di un blocco di pixel RGB
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"Image (RGB):\n[{r},{g},{b}]"

# --- FUNZIONE PRINCIPALE DI RENDERING ---

def genera_nuvola():
    canvas.delete("all")
    seme = int(spin_seed.get())
    random.seed(seme)
    
    cx, cy = 400, 300 # Centro del nuovo canvas più grande
    
    # SEED Centrale
    canvas.create_text(cx, cy, text=f"SEED: {seme}", font=("Helvetica", 22, "bold"), fill="#1A5276")
    
    # Griglia distorta per evitare sovrapposizioni
    passo_x, passo_y = 180, 120
    punti = [(x, y) for x in range(-360, 361, passo_x) for y in range(-240, 241, passo_y)]
    random.shuffle(punti)
    
    # Lista dei nostri generatori "folli"
    generatori = [gen_irrazionale, gen_tensore, gen_dataframe, gen_stringa, gen_suono, gen_pixel]
    colori = ["#9B59B6", "#34495E", "#16A085", "#D35400", "#2980B9", "#27AE60"]
    
    for i in range(min(len(punti), 12)):
        base_x, base_y = punti[i]
        if abs(base_x) < 50 and abs(base_y) < 50: continue # Salta il centro
        
        offset_x = random.randint(-15, 15)
        offset_y = random.randint(-15, 15)
        
        # LOGICA DI SWITCH: Se la checkbox è attiva, deviamo dai semplici numeri
        if var_modalita.get() == 1:
            # Sceglie un tipo di dato a caso e lo esegue
            funzione_scelta = random.choice(generatori)
            testo_output = funzione_scelta()
            dimensione_font = 9  # Più piccolo perché c'è più testo da mostrare
            colore = random.choice(colori)
        else:
            # Vecchia modalità: solo numeri
            testo_output = f"Int:\n{random.randint(10, 99)}"
            dimensione_font = 14
            colore = "#566573"
            
        canvas.create_text(cx + base_x + offset_x, cy + base_y + offset_y, 
                           text=testo_output, 
                           font=("Courier New" if var_modalita.get()==1 else "Verdana", dimensione_font, "bold"), 
                           fill=colore, justify=tk.CENTER)

# --- INTERFACCIA GRAFICA ---

root = tk.Tk()
root.title("Il Seme nei Tipi di Dati Python")
root.geometry("850x750")
root.configure(bg="#F2F4F4")

info_text = (
    "Sperimentazione: Il SEED non genera solo numeri, ma governa la struttura stessa dei dati.\n"
    "Attiva 'Modalità Multitipo' per vedere la potenza e la varietà dei dati gestibili in Python,\n"
    "dai Tensori alle onde sonore, tutto generato matematicamente a partire dal Seme scelto."
)
lbl_info = tk.Label(root, text=info_text, font=("Segoe UI", 11, "italic"), bg="#F2F4F4", fg="#34495E", pady=15)
lbl_info.pack()

frame_ctrl = tk.Frame(root, bg="#F2F4F4")
frame_ctrl.pack(pady=10)

tk.Label(frame_ctrl, text="Seme:", bg="#F2F4F4", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
spin_seed = ttk.Spinbox(frame_ctrl, from_=0, to=9999, width=8)
spin_seed.set(42)
spin_seed.pack(side=tk.LEFT, padx=5)

# CHECKBOX per il cambio di funzionalità radicale
var_modalita = tk.IntVar()
chk_modalita = tk.Checkbutton(frame_ctrl, text="Attiva Modalità Multitipo (Mondo Python)", 
                              variable=var_modalita, onvalue=1, offvalue=0, 
                              command=genera_nuvola, bg="#F2F4F4", font=("Segoe UI", 10, "bold"), fg="#117A65")
chk_modalita.pack(side=tk.LEFT, padx=20)

btn_genera = ttk.Button(frame_ctrl, text="Aggiorna", command=genera_nuvola)
btn_genera.pack(side=tk.LEFT, padx=5)

# Canvas allargato per ospitare i blocchi di testo complessi
canvas = tk.Canvas(root, width=800, height=600, bg="#FFFFFF", highlightthickness=1, highlightbackground="#BDC3C7")
canvas.pack(pady=10)

genera_nuvola()
root.mainloop()