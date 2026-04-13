# ==============================================================================
# Autore: MacBook Vincenzo + Gemini
# Data: Novembre 2025
# Scopo: Applicazione Desktop per la visualizzazione del meteo
# Funzionalità: Ottiene i dati meteo di una città tramite API esterne (Open-Meteo)
#               Implementa suggerimenti di autocompletamento e tooltip (post-it)
# Aggiornamento: Rimozione della funzionalità "Cerca su Mappa" e miglioramento
#                della gestione degli errori API per maggiore stabilità.
# Modo d'uso: Eseguire lo script e inserire il nome di una città italiana.
# ==============================================================================

import tkinter as tk
from tkinter import ttk
import requests
import json # Importato per una migliore gestione degli errori JSON

# Definisce le variabili globali per la gestione dell'interfaccia
data_labels = {}
frames = []
tooltip = None  # Variabile globale per il tooltip (post-it)
after_id = None # Variabile per l'identificativo del timer
api_status_label = None # Etichetta per visualizzare lo stato della connessione API

def get_weather_description(code):
    """
    Converte un codice meteo (WMO) in una descrizione testuale in italiano.
    """
    descriptions = {
        0: "Sereno", 1: "Principalmente sereno", 2: "Parzialmente nuvoloso",
        3: "Coperto", 45: "Nebbia", 48: "Ghiaccio depositato dalla nebbia",
        51: "Pioggerella leggera", 53: "Pioggerella moderata", 55: "Pioggerella intensa",
        56: "Pioggerella gelida leggera", 57: "Pioggerella gelida intensa",
        61: "Pioggia leggera", 63: "Pioggia moderata", 65: "Pioggia forte",
        66: "Pioggia gelida leggera", 67: "Pioggia gelida forte",
        71: "Nevischio leggero", 73: "Nevischio moderato", 75: "Nevischio forte",
        77: "Grandinata", 80: "Pioggia a debole intensità", 81: "Pioggia a moderata intensità",
        82: "Pioggia a forte intensità", 85: "Nevischio debole", 86: "Nevischio forte",
        95: "Temporale", 96: "Temporale con grandine leggera", 99: "Temporale con grandine forte",
    }
    return descriptions.get(code, "Sconosciuto")


def update_weather_display():
    """
    Ottiene i dati meteo da Open-Meteo e aggiorna le etichette dell'interfaccia.
    """
    city_name = city_entry.get()
    
    # Reimposta lo stato dell'API all'inizio della chiamata
    api_status_label.config(text="Stato API: in corso...", fg="blue")

    if not city_name:
        for label in data_labels.values():
            label.config(text="Nessuna città inserita")
        api_status_label.config(text="Stato API: pronto", fg="black")
        return

    # URL per la geocodifica (conversione nome città -> Lat/Lon) - Formato BASE corretto
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}"

    try:
        # 1. Chiamata per la geocodifica
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status() # Controlla errori HTTP (4xx o 5xx)
        
        # Prova a parsare la risposta JSON
        try:
            geo_data = geo_response.json()
        except json.JSONDecodeError:
            raise requests.exceptions.RequestException("Errore nel parsing JSON della Geo API.")

        # Verifica se sono stati trovati risultati per la città (punto critico)
        if not geo_data.get('results') or not geo_data['results']:
            for label in data_labels.values():
                label.config(text=f"Città '{city_name}' non trovata.")
            api_status_label.config(text=f"Stato API: Città non trovata", fg="red")
            return

        latitude = geo_data['results'][0]['latitude']
        longitude = geo_data['results'][0]['longitude']
        
        # 2. Chiamata per i dati meteo correnti - Formato BASE corretto
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}&"
            f"current=temperature_2m,relative_humidity_2m,weather_code,"
            f"apparent_temperature,wind_speed_10m,wind_direction_10m&"
            f"timezone=auto"
        )
        
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status() # Controlla errori HTTP
        
        # Prova a parsare la risposta JSON
        try:
            weather_data = weather_response.json()
        except json.JSONDecodeError:
            raise requests.exceptions.RequestException("Errore nel parsing JSON della Weather API.")
        
        # Estrazione dei dati
        current = weather_data['current']
        
        data_to_display = {
            "Descrizione": get_weather_description(current['weather_code']),
            "Temperatura": f"{current['temperature_2m']}°C",
            "Temp. percepita": f"{current['apparent_temperature']}°C",
            "Umidità": f"{current['relative_humidity_2m']}%",
            "Vento": f"{current['wind_speed_10m']} km/h",
            "Direzione vento": f"{current['wind_direction_10m']}°"
        }
        
        # Aggiorna le etichette con i nuovi dati
        for i, (key, value) in enumerate(data_to_display.items()):
            data_labels[key].config(text=f"{key}:\n{value}")
        
        # Lega gli eventi del mouse (tooltip) ai nuovi dati
        for label in data_labels.values():
            label.bind("<Enter>", lambda e, c=city_name: enter_weather_label(e, c))
            label.bind("<Leave>", leave_suggestion)

        api_status_label.config(text="Stato API: Successo", fg="green")

    # Gestione degli errori generici di connessione, HTTP o JSON
    except requests.exceptions.RequestException as e:
        error_message = f"Errore: Connessione o API fallita. Dettagli: {e}"
        print(error_message) # Stampa errore in console per debug
        for label in data_labels.values():
            label.config(text=f"Errore: Controlla la connessione o l'API")
        api_status_label.config(text="Stato API: Errore Critico", fg="red")

# ==============================================================================
# Logica di Autocompletamento e Tooltip
# (Omessa per brevità, la funzione è la stessa del file precedente)
# ==============================================================================
# [Immersive content redacted for brevity.]
available_cities = [
    "Roma", "Milano", "Napoli", "Torino", "Palermo", "Genova", "Bologna",
    "Firenze", "Bari", "Catania", "Venezia", "Verona", "Messina", "Padova",
    "Trieste", "Taranto", "Brescia", "Prato", "Parma", "Modena", "Reggio Calabria",
    "Reggio Emilia", "Perugia", "Livorno", "Ravenna", "Cagliari", "Foggia",
    "Rimini", "Salerno", "Ferrara", "Sassari", "Siracusa", "Pescara", "Monza",
    "Latina", "Bergamo", "Forlì", "Trento", "Vicenza", "Bolzano", "Novara",
    "Pisa", "Piacenza", "Ancona", "Andria", "Udine", "Lecce", "Arezzo",
    "Terni", "Alessandria", "La Spezia", "Caserta", "Pistoia", "Cosenza",
    "Cremona", "Como", "Viterbo", "Massa", "Barletta", "Ragusa", "Sesto San Giovanni",
    "Lucca", "Fano", "Grosseto", "Pavia", "Brindisi", "Asti", "L'Aquila",
    "Busto Arsizio", "Caltanissetta", "Carrara", "Cuneo", "Gorizia", "Imola",
    "Lamezia Terme", "Mantova", "Matera", "Pordenone", "Potenza", "Rovigo",
    "Savona", "Siena", "Teramo", "Trani", "Varese", "Vercelli", "Aosta",
    "Benevento", "Biella", "Chiavari", "Civitavecchia", "Cosenza", "Ercolano",
    "Faenza", "Foligno", "Gallipoli", "Gela", "Ivrea", "Jesolo", "Lecce",
    "Molfetta", "Monopoli", "Montecatini Terme", "Olbia", "Orvieto", "Pesaro",
    "Portici", "Pozzuoli", "Sesto Fiorentino", "Sondrio", "Tivoli", "Torre del Greco",
    "Trapani", "Udine", "Vigevano", "Vittoria"
]

suggestion_labels = []

def create_tooltip(widget, text):
    """ Crea una piccola finestra a comparsa (tooltip) vicino al mouse. """
    global tooltip, after_id
    if tooltip:
        destroy_tooltip()
    
    tooltip = tk.Toplevel(widget)
    tooltip.wm_overrideredirect(True) # Rimuove i bordi
    
    # Calcola la posizione del tooltip
    x = widget.winfo_rootx() + 20
    y = widget.winfo_rooty() + 20
    tooltip.wm_geometry(f"+{x}+{y}")
    
    label = tk.Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1,
                     font=("Arial", 10))
    label.pack(padx=5, pady=5)
    
    # Imposta un timer per distruggere il tooltip dopo 3 secondi
    after_id = root.after(3000, destroy_tooltip)

def destroy_tooltip():
    """ Distrugge il tooltip e annulla il timer. """
    global tooltip, after_id
    if tooltip:
        if after_id:
            root.after_cancel(after_id)
            after_id = None
        
        tooltip.destroy()
        tooltip = None

def enter_suggestion(event, city):
    create_tooltip(event.widget, f"Meteo per {city}")

def leave_suggestion(event):
    destroy_tooltip()

def enter_weather_label(event, city_name):
    # Tooltip visualizzato quando il mouse è sulle caselle dei dati meteo
    create_tooltip(event.widget, f"Meteo per la città di {city_name}")

def autocompletamento(event):
    """
    Gestisce l'evento di rilascio del tasto per fornire suggerimenti.
    Filtra l'elenco `available_cities`.
    """
    prefix = city_entry.get().lower()
    
    # Cancella i suggerimenti precedenti
    for label in suggestion_labels:
        label.destroy()
    suggestion_labels.clear()

    if not prefix:
        return

    # Trova le città che corrispondono al prefisso
    matching_cities = [city for city in available_cities if city.lower().startswith(prefix)]

    # Mostra i primi 3 suggerimenti
    for city in matching_cities[:3]:
        suggestion_label = tk.Label(suggestions_frame, text=city, font=("Arial", 10, "italic"), fg="blue", cursor="hand2")
        suggestion_label.pack(fill=tk.X, padx=5)
        # Lega un evento click per copiare la città nell'Entry
        suggestion_label.bind("<Button-1>", lambda e, c=city: on_suggestion_click(c))
        suggestion_label.bind("<Enter>", lambda e, c=city: enter_suggestion(e, c))
        suggestion_label.bind("<Leave>", leave_suggestion)
        suggestion_labels.append(suggestion_label)

def on_suggestion_click(city):
    """ Riempie la casella di input con la città selezionata. """
    city_entry.delete(0, tk.END)
    city_entry.insert(0, city)
    # Cancella i suggerimenti
    for label in suggestion_labels:
        label.destroy()
    suggestion_labels.clear()
    destroy_tooltip()


# ==============================================================================
# Creazione dell'Interfaccia Grafica (GUI)
# ==============================================================================

# Creazione della finestra principale
root = tk.Tk()
root.title("App Meteo")
root.geometry("600x450")
root.resizable(False, False)

# 1. Frame per l'input e il pulsante
input_frame = tk.Frame(root, pady=10)
input_frame.pack(fill=tk.X)

tk.Label(input_frame, text="Inserisci la città:").pack(side=tk.LEFT, padx=5)

city_entry = tk.Entry(input_frame, width=25)
city_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
# Lega l'evento di rilascio del tasto per l'autocompletamento
city_entry.bind("<KeyRelease>", autocompletamento)

search_button = tk.Button(input_frame, text="Cerca", command=update_weather_display)
search_button.pack(side=tk.LEFT, padx=5)


# 1b. Frame per i suggerimenti, posto sotto l'input
suggestions_frame = tk.Frame(root)
suggestions_frame.pack(fill=tk.X, padx=10)

# 2. Canvas principale (un Frame) per le informazioni meteo
main_canvas = tk.Frame(root, bg="gray90", borderwidth=2, relief="raised")
main_canvas.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

# Configurazione del layout a griglia 2x3
main_canvas.grid_columnconfigure(0, weight=1)
main_canvas.grid_columnconfigure(1, weight=1)
main_canvas.grid_rowconfigure(0, weight=1)
main_canvas.grid_rowconfigure(1, weight=1)
main_canvas.grid_rowconfigure(2, weight=1)
main_canvas.grid_rowconfigure(3, weight=0) # Riga per l'etichetta di stato

data_keys = ["Descrizione", "Temperatura", "Temp. percepita", "Umidità", "Vento", "Direzione vento"]

# Creazione dei 6 riquadri informativi
for i in range(2):
    for j in range(3):
        index = i + j * 2
        key = data_keys[index]
        
        color = "lightblue" if (i+j)%2 == 0 else "lightgray"
        
        frame = tk.Frame(main_canvas, bg=color, borderwidth=1, relief="sunken")
        frame.grid(row=j, column=i, padx=5, pady=5, sticky="nsew")
        frames.append(frame)

        label = tk.Label(frame, text=f"{key}:\nIn attesa...", bg=color, font=("Arial", 12))
        label.pack(expand=True)
        data_labels[key] = label

# 3. Etichetta di stato dell'API (nella riga 3 del main_canvas)
api_status_label = tk.Label(main_canvas, text="Stato API: pronto", fg="black", font=("Arial", 9, "italic"))
api_status_label.grid(row=3, column=0, columnspan=2, pady=5)


# 4. Frame per i pulsanti di controllo
button_frame = tk.Frame(root, pady=10)
button_frame.pack(fill=tk.X)

tk.Button(button_frame, text="Esci", command=root.destroy).pack(side=tk.LEFT, expand=True)

# Avvio del loop principale di Tkinter
root.mainloop()