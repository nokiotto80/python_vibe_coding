"""
===============================================================================
PROGETTO: Glockenspiel Didattico Virtuale AI
DATA ULTIME MODIFICHE: 16 Maggio 2026
AUTORI: Utente & Gemini (Google AI)
FRAMEWORK & LIBRERIE PRINCIPALI:
  - Pygame: Gestione della finestra grafica, del ciclo degli eventi (Loop),
            del rendering delle componenti e del mixaggio audio.
  - Numpy:  Generazione matematica dell'onda sinusoidale pura in tempo reale
            e applicazione dell'inviluppo ADSR (Decay) simulato.
  - Sys:    Integrazione per la terminazione pulita del processo su macOS.
===============================================================================
"""

import pygame
import numpy as np
import sys

# Inizializzazione Pygame e sottosistema Audio
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Configurazione Schermo
WIDTH, HEIGHT = 1000, 550
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Glockenspiel Didattico AI - Multitouch & Keyboard")

# Palette Colori (Stile valigetta giocattolo azzurra)
BACKGROUND = (41, 171, 226)
METAL_COLOR = (240, 240, 240)
PRESSED_COLOR = (200, 200, 200)
TEXT_COLOR = (50, 50, 50)
HAND_COLOR = (255, 219, 172)  # Colore pelle chiaro per le manine stilizzate

# Frequenze delle note (Fila inferiore: Note Naturali da Do4 a Sol5)
# Frequenze delle note (Fila inferiore: Note Naturali da Do3 a Sol4 - Notazione Didattica Italiana)
NOTES_DATA = [
    {"note": "DO 3", "freq": 261.63, "key": pygame.K_a},          # Tasto A
    {"note": "RE 3", "freq": 293.66, "key": pygame.K_s},          # Tasto S
    {"note": "MI 3", "freq": 329.63, "key": pygame.K_d},          # Tasto D
    {"note": "FA 3", "freq": 349.23, "key": pygame.K_f},          # Tasto F
    {"note": "SOL 3", "freq": 392.00, "key": pygame.K_g},         # Tasto G
    {"note": "LA 3", "freq": 440.00, "key": pygame.K_h},          # Tasto H
    {"note": "SI 3", "freq": 493.88, "key": pygame.K_j},          # Tasto J
    {"note": "DO 4", "freq": 523.25, "key": pygame.K_k},          # Tasto K
    {"note": "RE 4", "freq": 587.33, "key": pygame.K_l},          # Tasto L
    {"note": "MI 4", "freq": 659.25, "key": pygame.K_SEMICOLON},  # Tasto Ò (su Mac mappa spesso come semicolon)
    {"note": "FA 4", "freq": 698.46, "key": pygame.K_QUOTE},      # Tasto À (su Mac mappa spesso come quote)
    {"note": "SOL 4", "freq": 783.99, "key": pygame.K_LESS}       # Tasto < (a sinistra della Z, comodo per chiudere la scala)
]

def generate_xylophone_sound(freq, duration=1.5):
    """
    Sintesi sonora tramite Numpy.
    Genera un'onda sinusoidale accoppiata a un inviluppo esponenziale decrescente
    per emulare il tipico attacco e rilascio (ADSR percussivo) del metallofono.
    """
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Onda sinusoidale base
    wave = np.sin(2 * np.pi * freq * t)
    
    # Inviluppo: Attacco istantaneo, Decadimento (Decay) rapido
    envelope = np.exp(-5 * t) 
    
    # Normalizzazione a 16-bit PCM
    audio = (wave * envelope * 32767).astype(np.int16)
    
    # Raddoppio del canale per output Stereo
    stereo_audio = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo_audio)

class Key:
    """Rappresenta la singola barra metallica dello strumento dello xilofono"""
    def __init__(self, note, freq, key_code, x, y, w, h):
        self.note = note
        self.freq = freq
        self.key_code = key_code
        self.rect = pygame.Rect(x, y, w, h)
        self.sound = generate_xylophone_sound(freq)
        self.is_pressed = False

    def draw(self, surface):
        # Effetto dinamico "Incavato": se premuto si sposta in basso di 6px
        draw_rect = self.rect.copy()
        if self.is_pressed:
            draw_rect.y += 6
            color = PRESSED_COLOR
        else:
            color = METAL_COLOR

        # Disegno corpo piastra e bordi di rifinitura
        pygame.draw.rect(surface, color, draw_rect, border_radius=6)
        pygame.draw.rect(surface, (130, 130, 130), draw_rect, 2, border_radius=6)
        
        # Viti di fissaggio tipiche dello strumento (superiore e inferiore)
        pygame.draw.circle(surface, (80, 80, 80), (draw_rect.centerx, draw_rect.y + 15), 4)
        pygame.draw.circle(surface, (80, 80, 80), (draw_rect.centerx, draw_rect.bottom - 15), 4)

        # Scrittura della Nota stampata sulla barra
        font = pygame.font.SysFont("Arial", 16, bold=True)
        txt = font.render(self.note, True, TEXT_COLOR)
        surface.blit(txt, (draw_rect.centerx - 10, draw_rect.bottom - 40))

    def play(self):
        self.sound.play()
        self.is_pressed = True

def draw_hand(surface, pos):
    """Disegna una manina stilizzata vettoriale per evitare problemi di font/emoji"""
    x, y = pos
    # Palmo della mano
    pygame.draw.circle(surface, HAND_COLOR, (x, y), 20)
    # Segno delle dita (linee spesse)
    for i in range(-2, 3):
        pygame.draw.line(surface, HAND_COLOR, (x + i*7, y), (x + i*7, y - 25), 6)
    # Pollice
    pygame.draw.line(surface, HAND_COLOR, (x, y), (x - 15, y - 5), 6)

# Generazione dinamica della tastiera (Misure scalate progressivamente)
keys = []
start_x = 70
key_w = 60
base_h = 280

for i, data in enumerate(NOTES_DATA):
    current_h = base_h - (i * 8)
    x_pos = start_x + (i * (key_w + 12))
    keys.append(Key(data["note"], data["freq"], data["key"], x_pos, 100, key_w, current_h))

# Coordinate iniziali di riposo per le Mani
hand_L_pos = [WIDTH // 3, 450]
hand_R_pos = [2 * WIDTH // 3, 450]

# Ciclo principale dell'applicazione (Main Loop)
running = True
while running:
    screen.fill(BACKGROUND)
    
    # Rendering dei componenti di sfondo e tasti
    for key in keys:
        key.draw(screen)

    # Disegno delle mani vettoriali (senza dipendenza da font)
    draw_hand(screen, hand_L_pos)
    draw_hand(screen, hand_R_pos)

    # CATTURA E CONTROLLO EVENTI
    for event in pygame.event.get():
        # 1. Chiusura pulita della finestra
        if event.type == pygame.QUIT:
            running = False
            
        # 2. Input via MOUSE / TOUCH SINGOLO
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for key in keys:
                if key.rect.collidepoint(event.pos):
                    key.play()
                    # Muove la mano destra sul tasto cliccato
                    hand_R_pos = [event.pos[0], event.pos[1] + 40]
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            for key in keys:
                key.is_pressed = False

        # 3. Input via TASTIERA
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                
            for idx, key in enumerate(keys):
                if event.key == key.key_code:
                    key.play()
                    # Sposta la mano corrispondente sopra il tasto per colpirlo
                    if idx < len(keys) // 2:
                        hand_L_pos = [key.rect.centerx, key.rect.bottom + 30]
                    else:
                        hand_R_pos = [key.rect.centerx, key.rect.bottom + 30]

        elif event.type == pygame.KEYUP:
            for key in keys:
                if event.key == key.key_code:
                    key.is_pressed = False

        # 4. Input MULTITOUCH nativo (per schermi touch compatibili)
        elif event.type == pygame.FINGERDOWN:
            touch_x = event.x * WIDTH
            touch_y = event.y * HEIGHT
            for key in keys:
                if key.rect.collidepoint(touch_x, touch_y):
                    key.play()

        elif event.type == pygame.FINGERUP:
            for key in keys:
                key.is_pressed = False

    pygame.display.flip()

# Chiusura formale dei sistemi e del thread per evitare blocchi su macOS / Spyder
pygame.quit()
sys.exit()