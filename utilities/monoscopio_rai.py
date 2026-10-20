# -*- coding: utf-8 -*-
"""
===============================================================================
 MONOSCOPIO RAI anni '80 (carta di test tipo PM5544) - Python / Tkinter
===============================================================================
 Autori        : Utente (idea, specifiche, immagine di riferimento)
                 + Claude (Anthropic) - vibe coding
 Data          : 15/10/2026
 Ambiente      : Anaconda, IDE Spyder (eseguire con F5)

 Scopo         : Disegnare con le primitive di Tkinter (create_rectangle,
                 create_polygon, create_line, create_oval, create_text) il
                 monoscopio a colori preso come riferimento: griglia con
                 bordo a scacchi, barre colorate laterali, cerchio bianco
                 con barre dei colori, burst di frequenza, scala dei grigi,
                 barra gialla/rossa in basso. All'avvio viene emesso il
                 "bip" fastidioso: sinusoide pura a frequenza costante,
                 fase zero, durata 2.5 s.

 Pacchetti usati:
   - tkinter      (GUI, Canvas)             -> incluso in Anaconda
   - numpy        (generazione sinusoide)   -> incluso in Anaconda
   - wave, io, math, sys                    -> libreria standard
   - sounddevice  (OPZIONALE, audio multipiattaforma)
                    conda install -c conda-forge python-sounddevice
   - winsound     (fallback audio, solo Windows, libreria standard)

 Pipeline processuale:
   1. Parametri globali (larghezza W, formato 4:3, frequenza, durata, dB)
   2. Le coordinate del disegno sono espresse in "unita' di progetto"
      (466 x 350, cioe' la dimensione dell'immagine di riferimento) e
      moltiplicate per il fattore di scala F = W / 466
   3. Disegno statico sul Canvas principale, nell'ordine:
        a) sfondo grigio + quadrati neri del bordo + griglia bianca 27 x 20
        b) barre colorate laterali
        c) disco bianco centrale (create_oval)
        d) elementi interni al disco: ogni rettangolo viene ritagliato
           sul cerchio con l'algoritmo di Sutherland-Hodgman (cerchio
           approssimato da un poligono a 240 lati) e disegnato come
           poligono -> i bordi seguono la curva del cerchio
   4. Generazione del segnale: x(t) = A * sin(2*pi*f*t), A = 10^(dB/20)
   5. Conversione in PCM 16 bit (WAV in memoria per winsound / array
      float32 per sounddevice)
   6. Canvas secondario sotto: forma d'onda (altezza scala col volume)
   7. Pulsanti: VOL+ / VOL- (testo rosso), RIPRODUCI, STOP
   8. Avvio automatico del suono dopo l'apertura della finestra

 Storico modifiche:
   - v1.0  15/10/2026  Prima versione (disegno approssimato in bianco/nero)
   - v1.1  15/10/2026  Disegno rifatto sull'immagine di riferimento a
                       colori; ritaglio dei rettangoli sul cerchio; la
                       dimensione si cambia con il solo parametro W.

 Nota: le coordinate sono stimate a occhio sull'immagine di riferimento;
 per ritoccarle basta modificare i numeri in disegna_monoscopio().
===============================================================================
"""

import io
import math
import sys
import wave
import tkinter as tk

import numpy as np

# Backend audio: sounddevice se presente, altrimenti winsound (Windows)
try:
    import sounddevice as sd
    BACKEND = "sounddevice"
except Exception:
    sd = None
    try:
        import winsound
        BACKEND = "winsound"
    except Exception:
        winsound = None
        BACKEND = None

# ------------------------------ PARAMETRI -----------------------------------
W = 640                    # larghezza Canvas principale (px): cambiala a piacere
H = int(W * 3 / 4)         # altezza, formato 4:3
DW, DH = 466.0, 350.0      # dimensioni "di progetto" (immagine di riferimento)
F = W / DW                 # fattore di scala unita' di progetto -> pixel

TESTO_EMITTENTE = "RAI"    # scritta nella barra nera in alto ("" per toglierla)

FREQ_HZ = 500.0            # frequenza sinusoide (costante)
DURATA_S = 2.5             # durata in secondi
FS = 44100                 # frequenza di campionamento
VOL_DB_START = -12.0       # volume iniziale in dBFS
VOL_STEP_DB = 3.0          # passo dei tasti VOL+ / VOL-
VOL_MIN_DB, VOL_MAX_DB = -60.0, 0.0
WAVE_H = 90                # altezza canvas forma d'onda

# Colori
BIANCO, NERO, GRIGIO = "#ffffff", "#000000", "#808080"

# Disco centrale (unita' di progetto) e suo poligono per il ritaglio
CX, CY, RAD = 233.0, 174.0, 156.0
CIRC = [(CX + RAD * math.cos(2 * math.pi * k / 240),
         CY + RAD * math.sin(2 * math.pi * k / 240)) for k in range(240)]


# ------------------------------- AUDIO --------------------------------------
def genera_sinusoide(db):
    """Sinusoide pura, fase zero, ampiezza da dBFS. Ritorna float in [-1, 1]."""
    n = int(FS * DURATA_S)
    t = np.arange(n) / FS
    ampiezza = 10 ** (db / 20.0)
    return ampiezza * np.sin(2 * np.pi * FREQ_HZ * t)


def a_wav_bytes(x):
    """Converte float [-1,1] in WAV PCM 16 bit mono (in memoria)."""
    pcm = np.int16(np.clip(x, -1, 1) * 32767)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(FS)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


def ferma_audio():
    try:
        if BACKEND == "sounddevice":
            sd.stop()
        elif BACKEND == "winsound":
            winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass


def suona(db):
    """Riproduce la sinusoide (non bloccante)."""
    ferma_audio()
    x = genera_sinusoide(db)
    try:
        if BACKEND == "sounddevice":
            sd.play(x.astype(np.float32), FS)
        elif BACKEND == "winsound":
            winsound.PlaySound(a_wav_bytes(x),
                               winsound.SND_MEMORY | winsound.SND_ASYNC)
        else:
            print("Nessun backend audio disponibile.", file=sys.stderr)
    except Exception as e:
        print("Errore audio:", e, file=sys.stderr)


# ------------------------- PRIMITIVE DI DISEGNO ------------------------------
def R(c, x0, y0, x1, y1, fill):
    """Rettangolo pieno, coordinate in unita' di progetto."""
    c.create_rectangle(x0 * F, y0 * F, x1 * F, y1 * F, fill=fill, outline="")


def L(c, x0, y0, x1, y1, fill, spessore=1.5):
    """Linea, coordinate in unita' di progetto."""
    c.create_line(x0 * F, y0 * F, x1 * F, y1 * F, fill=fill,
                  width=max(1, round(spessore * F)))


def _dentro(p, a, b):
    """True se il punto p sta a sinistra (o sul)lo spigolo a->b."""
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0


def _interseca(s, e, a, b):
    """Intersezione del segmento s-e con la retta a-b."""
    x1, y1 = s
    x2, y2 = e
    x3, y3 = a
    x4, y4 = b
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def _ritaglia(soggetto, clip):
    """Sutherland-Hodgman: ritaglia il poligono 'soggetto' sul convesso 'clip'."""
    out = soggetto
    for i in range(len(clip)):
        a, b = clip[i], clip[(i + 1) % len(clip)]
        inp, out = out, []
        if not inp:
            break
        s = inp[-1]
        for e in inp:
            if _dentro(e, a, b):
                if not _dentro(s, a, b):
                    out.append(_interseca(s, e, a, b))
                out.append(e)
            elif _dentro(s, a, b):
                out.append(_interseca(s, e, a, b))
            s = e
    return out


def RC(c, x0, y0, x1, y1, fill):
    """Rettangolo pieno ritagliato sul disco centrale (poligono)."""
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    tutti_dentro = all((x - CX) ** 2 + (y - CY) ** 2 <= RAD ** 2 for x, y in pts)
    poly = pts if tutti_dentro else _ritaglia(pts, CIRC)
    if len(poly) >= 3:
        flat = []
        for x, y in poly:
            flat += [x * F, y * F]
        c.create_polygon(*flat, fill=fill, outline="")


# ----------------------------- DISEGNO --------------------------------------
def disegna_monoscopio(c):
    """Disegna il monoscopio sul Canvas c (W x H)."""

    # ---- a) sfondo, bordo a scacchi, griglia -------------------------------
    R(c, 0, 0, DW, DH, GRIGIO)
    COLS, ROWS = 27, 20
    cw, ch = DW / COLS, DH / ROWS
    for i in range(COLS):
        for j in range(ROWS):
            sul_bordo = i in (0, COLS - 1) or j in (0, ROWS - 1)
            if sul_bordo and (i + j) % 2 == 0:
                R(c, i * cw, j * ch, (i + 1) * cw, (j + 1) * ch, NERO)
    for i in range(COLS + 1):
        L(c, i * cw, 0, i * cw, DH, BIANCO)
    for j in range(ROWS + 1):
        L(c, 0, j * ch, DW, j * ch, BIANCO)

    # ---- b) barre colorate laterali ------------------------------------------
    barre = [
        (43, 35, 66, 172, "#00c8a0"),    # sinistra: verde acqua
        (43, 175, 66, 312, "#cc3366"),   # sinistra: magenta scuro
        (67, 35, 91, 58, "#6699ff"),     # sinistra: azzurro
        (67, 265, 91, 312, "#cc6600"),   # sinistra: arancio
        (399, 35, 423, 172, "#669933"),  # destra: verde oliva
        (399, 175, 423, 312, "#6666ff"), # destra: blu violetto
        (375, 35, 398, 58, "#6699ff"),   # destra: azzurro
        (375, 265, 398, 312, "#cc6600"), # destra: arancio
    ]
    for x0, y0, x1, y1, col in barre:
        R(c, x0, y0, x1, y1, col)
    L(c, 67, 85, 67, 312, BIANCO)
    L(c, 399, 85, 399, 312, BIANCO)

    # ---- c) disco bianco ---------------------------------------------------
    c.create_oval((CX - RAD) * F, (CY - RAD) * F, (CX + RAD) * F, (CY + RAD) * F,
                  fill=BIANCO, outline="")

    # ---- d) elementi interni al disco (ritagliati sul cerchio) -------------
    # barra nera in alto con scritta
    RC(c, 183, 35, 285, 57, NERO)
    if TESTO_EMITTENTE:
        c.create_text(234 * F, 46 * F, text=TESTO_EMITTENTE, fill=BIANCO,
                      font=("Helvetica", -int(15 * F), "bold"))
    # due rettangoli neri e riga sottile a sinistra
    RC(c, 124, 60, 156, 82, NERO)
    RC(c, 167, 60, 169, 82, NERO)
    RC(c, 311, 60, 346, 82, NERO)

    # fascia merlata nero / grigio chiaro
    RC(c, 80, 85, 386, 108, NERO)
    for k in range(10):
        if k % 2 == 1:
            x0 = 105 + 25.6 * k
            RC(c, x0, 85, x0 + 25.6, 108, "#b8b8b8")

    # fondo nero sotto le barre dei colori
    RC(c, 70, 108, 396, 262, NERO)

    # sei barre dei colori
    colori = ["#ffff00", "#00ffff", "#40ff00", "#ff00ff", "#ff0000", "#0000ff"]
    for k, col in enumerate(colori):
        RC(c, 80 + 51 * k, 108, 80 + 51 * (k + 1), 162, col)

    # reticolo: due righe orizzontali e tacche verticali
    RC(c, 70, 163, 396, 165, BIANCO)
    RC(c, 70, 176, 396, 177.5, BIANCO)
    for k in range(-9, 10):
        x = CX + k * (DW / COLS)
        RC(c, x - 0.7, 165, x + 0.7, 176, BIANCO)

    # burst di frequenza: strisce sempre piu' fitte, ultimo tratto grigio
    sezioni = [(108, 156, 8.0), (156, 204, 6.0), (204, 252, 4.4), (252, 310, 3.2)]
    for xa, xb, periodo in sezioni:
        x = xa
        while x < xb:
            RC(c, x, 182, min(x + periodo / 2, xb), 240, BIANCO)
            x += periodo
    RC(c, 310, 182, 360, 240, GRIGIO)

    # blocco nero centrale (disegnato dopo il burst: ne interrompe le strisce)
    RC(c, 221, 137, 245, 213, NERO)
    L(c, 70, 170.5, 396, 170.5, BIANCO, 1.0)

    # scala dei grigi (5 gradini; a sinistra resta il nero, a destra il bianco)
    limiti = [132, 182, 232, 284, 335, 386]
    grigi = ["#484848", "#808080", "#acacac", "#d9d9d9", BIANCO]
    for k, g in enumerate(grigi):
        RC(c, limiti[k], 240, limiti[k + 1], 262, g)

    # barra nera sotto la scala dei grigi
    RC(c, 155, 262, 308, 288, NERO)

    # parte bassa: giallo con rettangolo rosso al centro
    RC(c, 100, 289, 366, 340, "#ffff00")
    RC(c, 220, 289, 246, 340, "#ff0000")


def disegna_onda(c, db):
    """Disegna ~5 periodi della sinusoide sul canvas secondario."""
    c.delete("all")
    w = int(c["width"])
    h = int(c["height"])
    c.create_rectangle(0, 0, w, h, fill="#101010", outline="")
    c.create_line(0, h // 2, w, h // 2, fill="#404040")
    ampiezza = 10 ** (db / 20.0) * (h / 2 - 8)
    pts = []
    for x in range(w):
        t = x / w * 5  # 5 periodi visibili
        y = h / 2 - ampiezza * math.sin(2 * math.pi * t)
        pts += [x, y]
    c.create_line(*pts, fill="#00ff66", width=2)
    c.create_text(8, 6, anchor="nw", fill="#a0a0a0",
                  text="Sinusoide %.0f Hz  |  %.1f dBFS  |  %.1f s" % (FREQ_HZ, db, DURATA_S))


# ------------------------------ APPLICAZIONE --------------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("Monoscopio RAI anni '80")
        root.configure(bg="#202020")
        root.resizable(False, False)
        self.db = VOL_DB_START

        # Canvas principale: monoscopio
        self.main = tk.Canvas(root, width=W, height=H, highlightthickness=0, bg=GRIGIO)
        self.main.pack(padx=8, pady=(8, 4))
        disegna_monoscopio(self.main)

        # Canvas secondario: forma d'onda
        self.wave = tk.Canvas(root, width=W, height=WAVE_H, highlightthickness=0)
        self.wave.pack(padx=8, pady=4)

        # Barra comandi: testo ROSSO su sfondo chiaro (niente fg bianco)
        bar = tk.Frame(root, bg="#202020")
        bar.pack(pady=(4, 10))
        stile = dict(width=10, font=("Helvetica", 12, "bold"),
                     bg="#f0f0f0", activebackground="#dddddd")
        tk.Button(bar, text="VOL -", fg="red", command=self.vol_meno, **stile).grid(row=0, column=0, padx=6)
        self.lbl = tk.Label(bar, text="", fg="red", bg="#202020",
                            font=("Helvetica", 12, "bold"), width=14)
        self.lbl.grid(row=0, column=1, padx=6)
        tk.Button(bar, text="VOL +", fg="red", command=self.vol_piu, **stile).grid(row=0, column=2, padx=6)
        tk.Button(bar, text="RIPRODUCI", fg="red", command=self.riproduci, **stile).grid(row=0, column=3, padx=(24, 6))
        tk.Button(bar, text="STOP", fg="red", command=ferma_audio, **stile).grid(row=0, column=4, padx=6)

        self.aggiorna()
        root.protocol("WM_DELETE_WINDOW", self.chiudi)
        # suono all'avvio, dopo che la finestra e' visibile
        root.after(400, self.riproduci)

    def aggiorna(self):
        self.lbl.config(text="Volume: %.0f dB" % self.db)
        disegna_onda(self.wave, self.db)

    def riproduci(self):
        suona(self.db)

    def vol_piu(self):
        self.db = min(VOL_MAX_DB, self.db + VOL_STEP_DB)
        self.aggiorna()
        self.riproduci()

    def vol_meno(self):
        self.db = max(VOL_MIN_DB, self.db - VOL_STEP_DB)
        self.aggiorna()
        self.riproduci()

    def chiudi(self):
        ferma_audio()
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
