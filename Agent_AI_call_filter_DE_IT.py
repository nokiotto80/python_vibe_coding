"""
================================================================================
PROJEKT-SYSTEMDOKUMENTATION & SPEZIFIKATIONEN
================================================================================
Dateiname:       bilingual_voice_gatekeeper.py
Datum:           30. Mai 2026
Autoren:         Software-Ingenieur (Du) & Gemini AI Collaborator
Zweck:           Bilingualer KI-Anruffilter-Prototyp (Deutsch / Italienisch).
                 Demonstriert dynamische UI-Lokalisierung (Localization Layer)
                 über ein Dictionary-Mapping zur Laufzeit ohne Neustart.
                 Integriert akustische Klingelsimulation via sounddevice.

--------------------------------------------------------------------------------
ABHÄNGIGKEITEN & PACKAGES
--------------------------------------------------------------------------------
- tkinter: UI-Rendering und Event-Handling für den Sprachwechsel.
- speech_recognition: Audio-Erfassung und STT (Google API mit de-DE / it-IT).
- pyttsx3: Lokale Sprachausgabe (TTS).
- threading: Entkopplung der Audio-Pipeline vom UI-Hauptthread.
- numpy / sounddevice: Erzeugung und Wiedergabe des Telefonklingelns.

--------------------------------------------------------------------------------
LOCALIZATION ARCHITECTURE (DYNAMISCHER SPRACHWECHSEL)
--------------------------------------------------------------------------------
Die Benutzeroberfläche liest alle Texte aus dem `LOCALIZATION_DICT`. 
Beim Klick auf ein Flaggen-Button (🇩🇪/🇮🇹) ändert eine globale Variable 
den Sprachschlüssel ('de' oder 'it') und stößt eine Update-Funktion an, 
die alle Widgets (`config(text=...)`) live neu beschriftet.
================================================================================
"""

import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
import pyttsx3
import threading
import numpy as np
import sounddevice as sd

import os
"""silenzia i warning di macoS non necessari """
os.environ["PYTHONWARNINGS"] = "ignore"
# =====================================================================
# LOKALISIERUNGSDATENBANK (Localization Dictionary)
# =====================================================================
LOCALIZATION_DICT = {
    "de": {
        "title": "ANRUF VON UNBEKANNT",
        "status_ringing": "Status: Telefon klingelt...",
        "status_speaking": "Status: Agent spricht...",
        "status_listening": "Status: Höre zu...",
        "status_transcribing": "Status: Transkription...",
        "status_no_answer": "Status: Keine Antwort",
        "status_audio_error": "Status: Audio unklar",
        "btn_delegate": "Anruf an KI-Agent delegieren",
        "lbl_transcription": "Echtzeit-Transkription des Anrufers:",
        "agent_intro": "Hallo. Ich bin der digitale Assistent meines Besitzers. Wer sind Sie und was ist der Grund Ihres Anrufs?",
        "agent_spam": "Nein danke, kein Interesse. Auf Wiederhören.",
        "agent_urgent": "Ich habe verstanden. Ich benachrichtige sofort meinen Besitzer.",
        "agent_regular": "Ihre Nachricht wurde aufgezeichnet. Einen schönen Tag noch.",
        "agent_no_audio": "Keine Antwort erkannt. Ich lege auf.",
        "agent_error_audio": "Ich habe Sie nicht verstanden. Auf Wiederhören.",
        "msg_urgent_title": "DRINGENDER ANRUF!",
        "msg_report_title": "Agenten-Bericht",
        "lang_code": "de-DE",
        "spam_keywords": ["angebot", "trading", "investition", "strom", "gas", "werbung", "gewonnen", "verkaufen"],
        "urgent_keywords": ["dringend", "notfall", "klempner", "paket", "post", "unfall", "mama", "chef"]
    },
    "it": {
        "title": "CHIAMATA DA SCONOSCIUTO",
        "status_ringing": "Stato: Telefono Squilla...",
        "status_speaking": "Stato: Agente in linea...",
        "status_listening": "Stato: Ascolto in corso...",
        "status_transcribing": "Stato: Trascrizione...",
        "status_no_answer": "Stato: Nessuna risposta",
        "status_audio_error": "Stato: Audio non chiaro",
        "btn_delegate": "Fai rispondere l'Agente IA",
        "lbl_transcription": "Trascrizione Real-time dell'interlocutore:",
        "agent_intro": "Pronto. Sono l'assistente digitale del mio proprietario. Identificati e dimmi brevemente il motivo della chiamata.",
        "agent_spam": "Grazie, non siamo interessati. Arrivederci.",
        "agent_urgent": "Ho capito. Avviso subito il mio proprietario.",
        "agent_regular": "Messaggio registrato. Buona giornata.",
        "agent_no_audio": "Nessuna risposta rilevata. Chiudo la comunicazione.",
        "agent_error_audio": "Non ho capito cosa hai detto. Riprova più tardi.",
        "msg_urgent_title": "CHIAMATA URGENTE!",
        "msg_report_title": "Resoconto Agente",
        "lang_code": "it-IT",
        "spam_keywords": ["offerte", "trading", "investimenti", "luce e gas", "promozione", "vinto"],
        "urgent_keywords": ["urgente", "idraulico", "pacco", "corriere", "incidente", "mamma"]
    }
}

"""Variabile globale per contenere la lingua attiva di runtime"""
"""Globale Variable für die aktuelle Runtime-Sprache"""
current_lang = "de"

"""Inizializzazione del motore di sintesi vocale locale"""
"""Initialisierung der lokalen Text-to-Speech-Engine"""
engine = pyttsx3.init()
engine.setProperty('rate', 145)


def sprechen(text):
    """Esegue la riproduzione audio del testo passato"""
    """Führt die Audioausgabe des übergebenen Textes aus"""
    engine.say(text)
    engine.runAndWait()

# =====================================================================
# BILINGUALE CORE-LOGIK
# =====================================================================
def analysiere_anruf_bilingual(text_input, lang):
    """Analizza il testo usando le keyword della lingua selezionata"""
    """Analysiert den Text mithilfe der Keywords der ausgewählten Sprache"""
    text_lower = text_input.lower()
    lang_data = LOCALIZATION_DICT[lang]
    
    if any(k in text_lower for k in lang_data["spam_keywords"]):
        return "SPAM"
    elif any(k in text_lower for k in lang_data["urgent_keywords"]):
        return "URGENTE"
    else:
        return "REGOLARE"

def starte_anruffilter_bilingual():
    """Ferma il suono intermittente della campanella del telefono"""
    """Stoppt das intermittierende Klingeln des Telefons"""
    sd.stop()
    
    """Esegue la pipeline di ascolto usando la lingua attiva runtime"""
    """Führt die Audio-Pipeline in der aktiven Runtime-Sprache aus"""
    lang_data = LOCALIZATION_DICT[current_lang]
    
    def run():
        """Disabilita il bottone per evitare attivazioni multiple concorrenti"""
        """Deaktiviert den Button, um gleichzeitige Mehrfachaktivierungen zu verhindern"""
        btn_delegate.config(state=tk.DISABLED)
        
        print(f"\n[PIPELINE] Language active: {lang_data['lang_code']}")
        lbl_status.config(text=lang_data["status_speaking"], fg="blue")
        sprechen(lang_data["agent_intro"])
        
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            lbl_status.config(text=lang_data["status_listening"], fg="orange")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                lbl_status.config(text=lang_data["status_transcribing"], fg="blue")
                
                """Riconoscimento linguistico dinamico (de-DE o it-IT)"""
                """Dynamische Spracherkennung (de-DE oder it-IT)"""
                text_ergebnis = recognizer.recognize_google(audio_data, language=lang_data["lang_code"])
                
                txt_transkription.delete("1.0", tk.END)
                txt_transkription.insert(tk.END, text_ergebnis)
                
                kategorie = analysiere_anruf_bilingual(text_ergebnis, current_lang)
                
                if kategorie == "SPAM":
                    lbl_status.config(text=f"BLOCKED / BLOCCATO ({kategorie})", fg="red")
                    sprechen(lang_data["agent_spam"])
                elif kategorie == "URGENTE":
                    lbl_status.config(text=f"WARNING / AVVISO ({kategorie})", fg="green")
                    sprechen(lang_data["agent_urgent"])
                    messagebox.showwarning(lang_data["msg_urgent_title"], text_ergebnis)
                else:
                    lbl_status.config(text=f"SAVED / SALVATO ({kategorie})", fg="gray")
                    sprechen(lang_data["agent_regular"])
                    
                messagebox.showinfo(lang_data["msg_report_title"], f"Result: {kategorie}\nText: {text_ergebnis}")
                
            except sr.WaitTimeoutError:
                lbl_status.config(text=lang_data["status_no_answer"], fg="red")
                sprechen(lang_data["agent_no_audio"])
            except sr.UnknownValueError:
                lbl_status.config(text=lang_data["status_audio_error"], fg="red")
                sprechen(lang_data["agent_error_audio"])
                
    threading.Thread(target=run).start()

# =====================================================================
# DYNAMISCHER STRATEGIE-WECHSEL (La funzione di localizzazione)
# =====================================================================
def switch_language(lang_code):
    """Cambia la lingua attiva e aggiorna istantaneamente tutti i testi della GUI"""
    """Wechselt die aktive Sprache und aktualisiert sofort alle GUI-Texte"""
    global current_lang
    current_lang = str(lang_code)
    data = LOCALIZATION_DICT[current_lang]
    
    """Aggiornamento dinamico dei widget Tkinter"""
    """Dynamische Aktualisierung der Tkinter-Widgets"""
    lbl_title.config(text=data["title"])
    lbl_status.config(text=data["status_ringing"])
    btn_delegate.config(text=data["btn_delegate"])
    lbl_trans.config(text=data["lbl_transcription"])
    
    """Feedback visivo sui bottoni delle bandiere (attivo/disattivo)"""
    """Visuelles Feedback auf den Flaggen-Buttons (aktiv/deaktiviert)"""
    if current_lang == "de":
        btn_flag_de.config(relief=tk.SUNKEN, bg="#d0d0d0")
        btn_flag_it.config(relief=tk.RAISED, bg="#f5f5f5")
    else:
        btn_flag_de.config(relief=tk.RAISED, bg="#f5f5f5")
        btn_flag_it.config(relief=tk.SUNKEN, bg="#d0d0d0")
        
    print(f"[SYSTEM] Switched language to: {current_lang.upper()}")

# =====================================================================
# MACCHINA A STATI: FUNZIONE DI RESET
# =====================================================================
def reset_system():
    """Ripristina lo stato iniziale, pulisce l'interfaccia e fa risuonare la campanella"""
    """Stellt den Anfangszustand wieder her, leert die GUI und startet das Klingeln neu"""
    sd.stop()
    lang_data = LOCALIZATION_DICT[current_lang]
    
    """Svuota il box di testo della trascrizione"""
    """Leert das Textfeld für die Transkription"""
    txt_transkription.delete("1.0", tk.END)
    
    """Ripristina il testo dello stato sul valore iniziale del dizionario"""
    """Setzt den Statustext auf den Anfangswert des Wörterbuchs zurück"""
    lbl_status.config(text=lang_data["status_ringing"], fg="green")
    
    """Riattiva il bottone principale bloccato durante l'ascolto dell'agente"""
    """Aktiviert den Haupt-Button wieder, der während des Zuhörens gesperrt war"""
    btn_delegate.config(state=tk.NORMAL)
    
    """Fa ripartire il suono asincrono della campanella inserito dall'utente"""
    """Startet den vom Benutzer hinzugefügten asynchronen Klingelton neu"""
    sd.play(generate_klingel(False), 44100)
    print("[RESET] System state restored. Telephone ringing restarted.")

# =====================================================================
# GUI SETUP
# =====================================================================

def generate_klingel(continuo=True, durata=10, fs=44100):
    """Genera l'onda matematica sinusoidale per simulare lo squillo del telefono"""
    """Generiert die mathematische Sinuswelle, um das Telefonklingeln zu simulieren"""
    t = np.linspace(0, durata, int(fs * durata), endpoint=False)
    freq_base = 1500
    onda = 0.6 * np.sin(2 * np.pi * freq_base * t) + 0.3 * np.sin(2 * np.pi * freq_base * 2.1 * t) + 0.1 * np.sin(2 * np.pi * freq_base * 3.5 * t)
    impulso = (np.sin(2 * np.pi * 16 * t) > 0.7).astype(float)
    suono = onda * impulso * np.exp(-5 * ((t * 16) % 1.0))
    if not continuo: suono *= (np.sin(2 * np.pi * 0.5 * t) > 0).astype(float)
    return (suono / np.max(np.abs(suono))).astype(np.float32)


root = tk.Tk()
root.title("KI Voice Gatekeeper - Bilingual Prototyp")
root.geometry("420x560")  # Aumentata l'altezza per alloggiare il pannello inferiore di reset
root.config(bg="#f5f5f5")

# --- FRAME DELLE BANDIERE (In alto a destra) ---
frame_flags = tk.Frame(root, bg="#f5f5f5")
frame_flags.pack(anchor="ne", padx=10, pady=10)

btn_flag_de = tk.Button(frame_flags, text="🇩🇪 DE", font=("Helvetica", 11), command=lambda: switch_language("de"))
btn_flag_de.pack(side=tk.LEFT, padx=2)

btn_flag_it = tk.Button(frame_flags, text="🇮🇹 IT", font=("Helvetica", 11), command=lambda: switch_language("it"))
btn_flag_it.pack(side=tk.LEFT, padx=2)

# --- ELEMENTI DI TESTO ---
lbl_title = tk.Label(root, text="", font=("Helvetica", 14, "bold"), bg="#f5f5f5", fg="#222")
lbl_title.pack(pady=10)

lbl_status = tk.Label(root, text="", font=("Helvetica", 12), bg="#f5f5f5", fg="green")
lbl_status.pack(pady=10)

btn_delegate = tk.Button(root, text="", font=("Helvetica", 11, "bold"), bg="#4CD964", fg="black", padx=10, pady=10,
                         command=starte_anruffilter_bilingual)
btn_delegate.pack(pady=15)

lbl_trans = tk.Label(root, text="", font=("Helvetica", 10, "italic"), bg="#f5f5f5")
lbl_trans.pack(pady=5)

txt_transkription = tk.Text(root, height=5, width=42, font=("Helvetica", 11))
txt_transkription.pack(pady=10)

# --- FRAME CONTENITORE PER RESET (In basso a destra) ---
"""Crea una sezione invisibile sul fondo per posizionare il bottone di riavvio"""
"""Erstellt einen unsichtbaren Bereich unten, um den Reset-Button zu platzieren"""
frame_bottom = tk.Frame(root, bg="#f5f5f5")
frame_bottom.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=15)

"""Iniezione del bottone quadrato con l'emoji delle frecce verdi rotanti"""
"""Einfügen des quadratischen Buttons mit dem grünen rotierenden Pfeil-Emoji"""
btn_reset = tk.Button(frame_bottom, text="🔄", font=("Helvetica", 22), 
                      width=3, height=1, bg="#E0E0E0", fg="black", 
                      relief=tk.RAISED, command=reset_system)
btn_reset.pack(side=tk.RIGHT)


# Avvia l'applicazione attivando il Tedesco come default
switch_language("de")

if __name__ == "__main__":
    print("[SYSTEM] Booting Bilingual Agent GUI...")
    """Esegue lo squillo iniziale della campanella all'apertura del programma"""
    """Spielt das erste Telefonklingeln beim Öffnen des Programms ab"""
    sd.play(generate_klingel(False), 44100)
    root.mainloop()