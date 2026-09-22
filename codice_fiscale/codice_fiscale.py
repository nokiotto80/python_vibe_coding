#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programma: Calcolo Codice Fiscale in Python con Tkinter
Autore: macbook_vincenzo & AI Assistant (Gemini)
Data creazione: 16/04/2025
Ultima modifica: 02/09/2026

Funzionalità implementate:
- Interfaccia grafica con Tkinter.
- Caricamento dati da file CSV esterni tramite Pandas (Comuni e Province).
- Selezione a cascata: prima la Provincia, che filtra dinamicamente i Comuni associati.
- Layout corretto con Provincia e Comune posizionati sulla stessa riga logica.
- Abilitazione dinamica del pulsante di calcolo solo a campi completati.

Bug corretti e Storico versioni:
- v1.0: Struttura base del form e gestione errori di codifica UTF-8 per i file CSV.
- v1.1: Corretto l'ordine di creazione della finestra principale (root) per evitare errori di runtime delle variabili Tkinter.
- v1.2 (Corrente): Aggiunta la gestione della Provincia con menu a cascata filtrato sui comuni, riposizionamento dei campi di input sulla stessa riga e tracciamento della provincia selezionata.
"""

# 1) Import delle librerie necessarie
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import pandas as pd  # Per la gestione dei dati dei comuni e province

# 2) Caricamento dei dati territoriali da file CSV
try:
    df_comuni = pd.read_csv('/Users/macbook_vincenzo/Python/codice_fiscale/Elenco-comuni-italiani.csv', sep=';')
    df_province = pd.read_csv('/Users/macbook_vincenzo/Python/codice_fiscale/Elenco-province.csv', sep=';')
   
    lista_province = sorted(df_province['Denominazione in italiano'].tolist())
   
    # Creazione di un dizionario per mappare comune -> codice catastale e provincia
    # Assicurati che nel file dei comuni esistano le colonne adeguate (es. 'Sigla Provincia' o simile)
    codici_comuni = dict(zip(df_comuni['Denominazione in italiano'], df_comuni['Codice Catastale del comune']))
    
except FileNotFoundError as e:
    print(f"Errore nel caricamento dei file CSV: {e}")
    lista_comuni = []
    codici_comuni = {}
    lista_province = []

# 3) Creazione finestra principale
root = tk.Tk()  
root.title("Calcolo Codice Fiscale - v1.2")
    
# 4) Creazione VARIABILI
nome_var = tk.StringVar()
cognome_var = tk.StringVar()

sesso_var = tk.StringVar(value="Maschio") #automaticamente selezionato,basta cambiare
data_nascita_var = tk.StringVar()
provincia_var = tk.StringVar()
comune_var = tk.StringVar()
codice_fiscale_var = tk.StringVar()

# 5) Funzione per filtrare i comuni in base alla provincia selezionata
def aggiorna_comuni(*args):
    provincia_scelta = provincia_var.get()
    if provincia_scelta:
        comuni_filtrati = df_comuni[df_comuni['Provincia'].astype(str).str.contains(provincia_scelta, case=False, na=False)]
        lista_filtrata = sorted(comuni_filtrati['Denominazione in italiano'].tolist())
        comune_combo['values'] = lista_filtrata
        if lista_filtrata:
                comune_var.set(lista_filtrata[0]) # Seleziona automaticamente il primo comune
        else:
                comune_var.set('')
    else:
            comune_combo['values'] = []
            comune_var.set('')

provincia_var.trace_add("write", aggiorna_comuni)

# 6) Creazione delle ETICHETTE e dei campi di INPUT
tk.Label(root, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
nome_entry = tk.Entry(root, textvariable=nome_var)
nome_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

tk.Label(root, text="Cognome:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
cognome_entry = tk.Entry(root, textvariable=cognome_var)
cognome_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

tk.Label(root, text="Sesso:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
sesso_combo = ttk.Combobox(root, textvariable=sesso_var, values=["Maschio", "Femmina"], state="readonly")
sesso_combo.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

tk.Label(root, text="Data di Nascita:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
data_nascita_picker = DateEntry(root, textvariable=data_nascita_var, date_pattern='dd/mm/yyyy')
data_nascita_picker.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

# RIGA CONDIVISA: Provincia e Comune di Nascita sulla stessa riga
tk.Label(root, text="Provincia:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
provincia_combo = ttk.Combobox(root, textvariable=provincia_var, values=lista_province, state="normal", width=15)
provincia_combo.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

def filtra_province(event):
    valore = provincia_var.get().upper()
    if valore:
        filtrate = [p for p in lista_province if p.upper().startswith(valore)]
        provincia_combo['values'] = filtrate
    else:
        provincia_combo['values'] = lista_province

provincia_combo.bind('<KeyRelease>', filtra_province)

tk.Label(root, text="Comune:").grid(row=4, column=2, padx=5, pady=5, sticky="w")
comune_combo = ttk.Combobox(root, textvariable=comune_var, values=[], state="normal", width=25)
comune_combo.grid(row=4, column=3, padx=5, pady=5, sticky="ew")

def filtra_comuni_testo(event):
    valore = comune_var.get().upper()
    provincia_scelta = provincia_var.get()
    if provincia_scelta:
        colonna_provincia = None
        for col in df_comuni.columns:
            if any(p in col.lower() for p in ['provincia', 'territoriale', 'sigla']):
                colonna_provincia = col
                break
        comuni_filtrati = df_comuni[df_comuni[colonna_provincia].astype(str).str.contains(provincia_scelta, case=False, na=False)]
        lista_base = sorted(comuni_filtrati['Denominazione in italiano'].dropna().tolist())
        if valore:
            filtrati = [c for c in lista_base if c.upper().startswith(valore)]
            comune_combo['values'] = filtrati
        else:
            comune_combo['values'] = lista_base

comune_combo.bind('<KeyRelease>', filtra_comuni_testo)

tk.Label(root, text="Codice Fiscale:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
risultato_label = tk.Label(root, textvariable=codice_fiscale_var, font=("Arial", 16, "bold"),fg="#fc2c03",)
risultato_label.grid(row=6, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

# 7) Creazione dei PULSANTI
calcola_button = tk.Button(root, text="Calcola codice fiscale", command=lambda: calcola_codice(), state=tk.DISABLED)
calcola_button.grid(row=5, column=0, columnspan=2, pady=10)

annulla_button = tk.Button(root, text="Annulla", command=lambda: reset_campi())
annulla_button.grid(row=5, column=2, columnspan=2, pady=10)

# 8) Funzione che ABILITA o DISABILITA il pulsante "CALCOLA"
def verifica_campi(*args):
    if (nome_var.get() and cognome_var.get() and sesso_var.get() and
        data_nascita_var.get() and provincia_var.get() and comune_var.get()):
        calcola_button.config(state=tk.NORMAL)
    else:
        calcola_button.config(state=tk.DISABLED)

nome_var.trace_add("write", verifica_campi)
cognome_var.trace_add("write", verifica_campi)
sesso_var.trace_add("write", verifica_campi)
data_nascita_var.trace_add("write", verifica_campi)
provincia_var.trace_add("write", verifica_campi)
comune_var.trace_add("write", verifica_campi)

# 9) Funzione del calcolo CODICE FISCALE
def calcola_codice():
    nome = nome_var.get().upper()
    cognome = cognome_var.get().upper()
    sesso = sesso_var.get()
    data_nascita_str = data_nascita_var.get()
    comune_selezionato = comune_var.get()

    # 03/09/2026Applicazione delle regole ufficiali per le terzine di cognome e nome
    codice_cognome = elabora_cognome(cognome)
    codice_nome = elabora_nome(nome)
    cf_parziale = codice_cognome + codice_nome
    anno = data_nascita_str[8:10]
    mese_map = {"01": "A", "02": "B", "03": "C", "04": "D", "05": "E", "06": "H",
                "07": "L", "08": "M", "09": "P", "10": "R", "11": "S", "12": "T"}
    mese = mese_map.get(data_nascita_str[3:5], "")
    giorno = int(data_nascita_str[:2])
    if sesso == "Femmina":
        giorno += 40
    giorno_str = str(giorno).zfill(2)

    codice_comune = codici_comuni.get(comune_selezionato, "XXXX")
    # Primi 15 caratteri del codice fiscale parziale
    cf_15 = cf_parziale + anno + mese + giorno_str + codice_comune
    
    # Calcolo dinamico del carattere di controllo tramite la funzione dedicata
    carattere_controllo = calcola_carattere_controllo(cf_15)

    codice_fiscale_calcolato = cf_15 + carattere_controllo
    codice_fiscale_var.set(codice_fiscale_calcolato)

    codice_fiscale_calcolato = cf_parziale + anno + mese + giorno_str + codice_comune + carattere_controllo
    codice_fiscale_var.set(codice_fiscale_calcolato)
    
# 10) Funzione per resettare i campi
def reset_campi():
    nome_var.set("")
    cognome_var.set("")
    sesso_var.set("")
    data_nascita_var.set("")
    provincia_var.set("")
    comune_var.set("")
    comune_combo['values'] = []
    codice_fiscale_var.set("")
    calcola_button.config(state=tk.DISABLED)
    
    
def calcola_carattere_controllo(cf_15):
    # Tabelle di conversione per il calcolo del carattere di controllo
    valori_dispari = {
        '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8': 19, '9': 21,
        'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17, 'I': 19, 'J': 21,
        'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14,
        'U': 16, 'V': 10, 'W': 22, 'X': 25, 'Y': 24, 'Z': 23
    }
    
    valori_pari = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
        'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19,
        'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25
    }
    
    somma = 0
    for i, char in enumerate(cf_15.upper(), start=1):
        if i % 2 != 0:  # Posizione dispari (1-based: 1, 3, 5...)
            somma += valori_dispari.get(char, 0)
        else:           # Posizione pari (1-based: 2, 4, 6...)
            somma += valori_pari.get(char, 0)
            
    # Il carattere di controllo è il resto della divisione per 26 convertito in lettera (A=0, Z=25)
    resto = somma % 26
    return chr(ord('A') + resto)

#funzioni rigorosew per estrarre nome, cognome e far combaciare il carattere di controllo
def estrai_lettere(testo):
    # Estrae solo i caratteri alfabetici maiuscoli
    testo_pulito = ''.join(c for c in testo.upper() if c.isalpha())
    consonanti = ''.join([c for c in testo_pulito if c not in 'AEIOU'])
    vocali = ''.join([c for c in testo_pulito if c in 'AEIOU'])
    return consonanti, vocali

def elabora_cognome(cognome):
    c, v = estrai_lettere(cognome)
    # 3 consonanti, se mancano si aggiungono le vocali, se mancano ancora si mettono 'X'
    risultato = (c + v + 'XXX')[:3]
    return risultato

def elabora_nome(nome):
    c, v = estrai_lettere(nome)
    # Se il nome ha 4 o più consonanti, si prendono la 1ª, la 3ª e la 4ª
    if len(c) >= 4:
        risultato = c[0] + c[2] + c[3]
    else:
        risultato = (c + v + 'XXX')[:3]
    return risultato
      
# 11) Esecuzione della finestra principale
root.mainloop()