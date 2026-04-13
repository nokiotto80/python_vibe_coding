#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 19:24:15 2025
Crea una rubrica con funzioni C.R.U.D. (Create Read Update and Delete)
-dapprima a LISTVIEW

-poi convertita in TreeView


@author: macbook_vincenzo
"""

import tkinter as tk
from tkinter import Toplevel, messagebox,ttk
from PIL import Image, ImageTk  # Per gestire immagini (potrebbe essere necessario installare: pip install Pillow)
import random
import sqlite3
import os

class RubricaTelefonica:
    def __init__(self, root):
        self.root = root
        self.root.title("Phone Book")

        # Connessione al database
        self.conn = sqlite3.connect("rubrica.db")
        self.cursor = self.conn.cursor()

        # Creazione della tabella se non esiste
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contatti (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                telefono TEXT,
                email TEXT
            )
        """)
        self.conn.commit()
        
        
        # Configura il ridimensionamento della finestra principale (root)
      # La colonna 1 (quella con le entry e la listbox) si espanderà
        self.root.columnconfigure(1, weight=1)
     # La riga 4 (quella con la listbox) si espanderà
        self.root.rowconfigure(4, weight=1)

        # Interfaccia grafica
        self.crea_interfaccia()
        self.visualizza_contatti()

    def crea_interfaccia(self):
        # ... (Tutto il codice per le etichette, i campi di input e i bottoni rimane lo stesso) ...
       # Campi di input
       tk.Label(self.root, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
       self.nome_entry = tk.Entry(self.root, width=40)
       self.nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew") # Modifica: aggiunto sticky="ew"

       tk.Label(self.root, text="Telefono:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
       self.telefono_entry = tk.Entry(self.root, width=40)
       self.telefono_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew") # Modifica: aggiunto sticky="ew"

       tk.Label(self.root, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
       self.email_entry = tk.Entry(self.root, width=40)
       self.email_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew") # Modifica: aggiunto sticky="ew"

       # Bottoni. Aggiunti i PadX per migliore layout fisico della finestra
       button_frame = tk.Frame(self.root)
       button_frame.grid(row=3, column=0, columnspan=2, pady=10)

       tk.Button(button_frame, text="Aggiungi", command=self.aggiungi_contatto).pack(side=tk.LEFT, padx=5)
       tk.Button(button_frame, text="Visualizza Tutti", command=self.visualizza_contatti).pack(side=tk.LEFT, padx=5)
       tk.Button(button_frame, text="Aggiorna", command=self.aggiorna_contatto).pack(side=tk.LEFT, padx=5)
       tk.Button(button_frame, text="Elimina", command=self.elimina_contatto).pack(side=tk.LEFT, padx=5)
       tk.Button(button_frame, text="Pulisci Campi", command=self.pulisci_campi).pack(side=tk.LEFT, padx=5)

           # Lista contatti. Aggiunte opzioni 'sticky="nswe"' per consentire l'agganciare 
        # Con queste righe per il Treeview:
       self.lista_contatti = ttk.Treeview(self.root, columns=("Nome", "Telefono", "Email"), show="headings")
       self.lista_contatti.heading("Nome", text="Nome")
       self.lista_contatti.heading("Telefono", text="Telefono")
       self.lista_contatti.heading("Email", text="Email")
            
            # Imposta anche le larghezze delle colonne (opzionale)
       self.lista_contatti.column("Nome", width=150)
       self.lista_contatti.column("Telefono", width=150)
       self.lista_contatti.column("Email", width=200)
            
       self.lista_contatti.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nswe")
               # Scrollbar per la list
              

       # # Collega la selezione della Listbox
       # E sostituiscila con questa
       self.lista_contatti.bind('<<TreeviewSelect>>', self.selected_item)
      
       scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.lista_contatti.yview)
       scrollbar.grid(row=4, column=2, sticky="ns")
       
       # Collega il Treeview allo Scrollbar.
           
       self.lista_contatti.configure(yscrollcommand=scrollbar.set) # Questa riga è cruciale e mancava nel tuo codice.

    def aggiungi_contatto(self):
        nome = self.nome_entry.get()
        telefono = self.telefono_entry.get()
        email = self.email_entry.get()
       
        # Verifica che i campi essenziali non siano vuoti 
        if not nome or not telefono:
           tk.messagebox.showwarning("Errore", "Nome e Telefono sono campi obbligatori!")
           return
        # 1. Esegui una query SELECT per cercare un contatto esistente
 #    Usiamo il telefono come criterio di unicità.
        self.cursor.execute("SELECT COUNT(*) FROM contatti WHERE telefono = ?", (telefono,))
       
        # 2. Ottieni il risultato della query. fetchone() restituisce una tupla.
        count = self.cursor.fetchone()[0]
        # 3. Controlla se il risultato è maggiore di zero
        if count > 0:
            # 4. Se il contatto esiste, mostra un avviso
            tk.messagebox.showwarning("Contatto esistente", "Un contatto con questo numero di telefono esiste già.")
        else:
            # Se il contatto non esiste, mostra il CAPTCHA
            self.mostra_captcha()

    def mostra_captcha(self):
        # Percorso della cartella delle immagini
        IMMAGINI_FOLDER = "/Users/macbook_vincenzo/Python/captcha/output"

        # Funzione per caricare i file da una cartella con un dato prefisso
        def get_images_from_folder(folder_path, prefix):
            images = []
            if not os.path.exists(folder_path):
                return images
            for filename in os.listdir(folder_path):
                if filename.startswith(prefix) and (filename.endswith(".png") or filename.endswith(".jpg")):
                    images.append(os.path.join(folder_path, filename))
            return images

        # Genera le liste di immagini basate sui file
        immagini_gatti = get_images_from_folder(IMMAGINI_FOLDER, "gatto")
        immagini_cani = get_images_from_folder(IMMAGINI_FOLDER, "cane")
        immagini_orologi = get_images_from_folder(IMMAGINI_FOLDER, "orologio")
        
        immagini_misti = get_images_from_folder(IMMAGINI_FOLDER, "misti")

        if not immagini_gatti or not immagini_cani or not immagini_misti:
            messagebox.showerror("Errore CAPTCHA", f"Impossibile trovare le immagini del CAPTCHA. Controlla il percorso: '{IMMAGINI_FOLDER}'")
            return

        num_cani = random.choice([3, 4])
        num_orologi = random.choice([3, 4])
        num_altri = 9 - num_orologi
        
        self.captcha_corrette = random.sample(immagini_orologi, k=num_orologi)
        
        # Unisci i due dataset SBAGLIATI (es se voglio mostrare gli orologi, mischio i cani, i gatti e i misti)
        immagini_sbagliate_pool = immagini_cani + immagini_gatti + immagini_misti
        self.captcha_totali = self.captcha_corrette + random.sample(immagini_sbagliate_pool, k=num_altri)
        random.shuffle(self.captcha_totali)

        self.captcha_window = Toplevel(self.root)
        self.captcha_window.title("Verifica di sicurezza")
        self.captcha_window.geometry("300x370")
        
        tk.Label(self.captcha_window, text=f"Seleziona tutte le caselle con un OROLOGIO ({num_orologi} in totale)", font=("Helvetica", 12, "bold")).pack(pady=10)

        self.selezione_utente = [tk.BooleanVar(value=False) for _ in range(9)]
        grid_frame = tk.Frame(self.captcha_window)
        grid_frame.pack()
        
        self.captcha_photos = []
        self.checkbuttons = []

        def toggle_border(index):
            if self.selezione_utente[index].get():
                self.checkbuttons[index].config(relief=tk.SUNKEN, highlightbackground="green", highlightcolor="green")
            else:
                self.checkbuttons[index].config(relief=tk.RAISED, highlightbackground="white", highlightcolor="white")

        for i in range(9):
            img_path = self.captcha_totali[i]
            try:
                img = Image.open(img_path)
                img = img.resize((80, 80), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.captcha_photos.append(photo)

                btn = tk.Checkbutton(grid_frame, image=photo, indicatoron=False, onvalue=True, offvalue=False,
                                     variable=self.selezione_utente[i],
                                     command=lambda idx=i: toggle_border(idx),
                                     relief=tk.RAISED, highlightthickness=3, highlightbackground="white")
                btn.image = photo
                btn.grid(row=i // 3, column=i % 3, padx=2, pady=2)
                self.checkbuttons.append(btn)
            except Exception as e:
                print(f"Errore caricamento immagine {img_path}: {e}")

        tk.Button(self.captcha_window, text="Conferma", command=self.verifica_captcha).pack(pady=10)
    def verifica_captcha(self):
        # Ottieni le posizioni delle immagini corrette
        posizioni_corrette = [i for i, img in enumerate(self.captcha_totali) if img in self.captcha_corrette]
        
        # Ottieni le posizioni selezionate dall'utente
        posizioni_selezionate = [i for i, var in enumerate(self.selezione_utente) if var.get()]

        if sorted(posizioni_corrette) == sorted(posizioni_selezionate):
            # CAPTCHA superato, procedi con l'inserimento del contatto
            self.captcha_window.destroy()
            try:
                # Ora recuperi i dati e li inserisci nel database
                nome = self.nome_entry.get()
                telefono = self.telefono_entry.get()
                email = self.email_entry.get()
                
                self.cursor.execute("INSERT INTO contatti (nome, telefono, email) VALUES (?, ?, ?)", (nome, telefono, email))
                self.conn.commit()
                self.pulisci_campi()
                self.visualizza_contatti()
                tk.messagebox.showinfo("Successo", "Contatto aggiunto correttamente.")
            except Exception as e:
                tk.messagebox.showerror("Errore", f"Si è verificato un errore durante l'aggiunta: {e}")

    def visualizza_contatti(self):
        # Pulisci il Treeview
        for item in self.lista_contatti.get_children():
            self.lista_contatti.delete(item)
    
        self.cursor.execute("SELECT id, nome, telefono, email FROM contatti ORDER BY nome")
        
        for row in self.cursor.fetchall():
            # Inserisci i dati nelle colonne specificando la tupla 'values'
            # Salviamo l'ID in un attributo nascosto 'iid' o 'text'
            self.lista_contatti.insert("", tk.END, iid=row[0], values=(row[1], row[2], row[3]))
            

    def aggiorna_contatto(self):
        # 1 Implementa la logica per aggiornare un contatto selezionato
      print("Funzione aggiorna_contatto chiamata.") # Primo punto di controllo
  #1. Recupera i valori dai campi di input

      nome = self.nome_entry.get()
      telefono = self.telefono_entry.get()
      email = self.email_entry.get()
      
      
        # 2. Ottieni l'ID del contatto selezionato dalla Listbox
      selected_indices = self.lista_contatti._selection()
      if not selected_indices:
            print("DEBUG: Nessun contatto selezionato.")
            tk.messagebox.showwarning("Attenzione", "Seleziona un contatto dalla lista per aggiornare.")
            return

      index = selected_indices[0]
      selected_text = self.lista_contatti.get(index)   
      
      try:
            # Estrai l'ID dal testo
            id_start = selected_text.rfind("(ID: ")
            if id_start != -1:
                contact_id = int(selected_text[id_start + 5:-1])
            else:
                tk.messagebox.showerror("Errore", "Impossibile trovare l'ID del contatto selezionato. Assicurati che il formato della lista includa l'ID.")
                return # Questo return è corretto, interrompe la funzione solo in caso di errore.
      except ValueError:
            tk.messagebox.showerror("Errore", "Formato ID non valido nel testo selezionato.")
            return # Questo return è corretto, interrompe la funzione solo in caso di errore.

        # 3. Controlla che i campi essenziali non siano vuoti (opzionale ma consigliato)
      if not nome or not telefono:
          tk.messagebox.showwarning("Errore", "Nome e Telefono sono campi obbligatori e non possono essere vuoti per l'aggiornamento.")
          return
      # 4. Esegui la query di aggiornamento
      try:
            print("DEBUG: Query di aggiornamento in esecuzione.")
            self.cursor.execute("UPDATE contatti SET nome = ?, telefono = ?, email = ? WHERE id = ?",
                                (nome, telefono, email, contact_id))

            self.conn.commit()

            # 5. Pulisci i campi e aggiorna la visualizzazione
            self.pulisci_campi()
            self.visualizza_contatti()
            tk.messagebox.showinfo("Successo", "Contatto aggiornato correttamente.")


      except Exception as e:
            tk.messagebox.showerror("Errore di aggiornamento", f"Si è verificato un errore: {e}")
            print(f"Erroraccio nell'aggiornare i contatti': {e}")
            print(e)
# fine funzione AGGIORNA CONTATTO

    def elimina_contatto(self):
      nome = self.nome_entry.get()
      telefono = self.telefono_entry.get()

      self.cursor.execute("DELETE FROM contatti WHERE nome = ? AND telefono = ?", (nome, telefono))
      self.conn.commit()
      selected_checkboxs = self.lista_contatti.curselection() 
   
      for selected_checkbox in selected_checkboxs[::-1]: 
               self.lista_contatti.delete(selected_checkbox) 
      
      self.visualizza_contatti()

    def __del__(self): #chiudi la connessione
        self.conn.close()
        
    def pulisci_campi(self):
          self.nome_entry.delete(0, tk.END)
          self.telefono_entry.delete(0, tk.END)
          self.email_entry.delete(0, tk.END)

  
    def selected_item(self, event=None):
    # Ottieni l'elemento selezionato. `selection()` restituisce una tupla di iid.
        selected_item = self.lista_contatti.selection()
    
        if selected_item:
            self.pulisci_campi()
            
            # Recupera l'ID e i dati del contatto selezionato
            item_id = selected_item[0] # Prende il primo (e unico) iid dalla selezione
            contact_id = int(item_id)
            
            # Fai la query al database usando l'ID corretto
            self.cursor.execute("SELECT nome, telefono, email FROM contatti WHERE id = ?", (contact_id,))
            contact_data = self.cursor.fetchone()
            
            # Inserisci i dati recuperati nei campi di testo
            if contact_data:
                nome, telefono, email = contact_data
                self.nome_entry.insert(0, nome)
                self.telefono_entry.insert(0, telefono)
                self.email_entry.insert(0, email)
        else:
            # Se non c'è NESSUN elemento selezionato, pulisci i campi.
            # Questo gestisce il caso in cui l'utente deseleziona tutto.
            self.pulisci_campi()
                    
        def pulisci_campi(self):
            self.nome_entry.delete(0, tk.END)
            self.telefono_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
    
if __name__ == "__main__":
    root = tk.Tk()
    app = RubricaTelefonica(root)
    root.mainloop()