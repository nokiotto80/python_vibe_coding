"""
================================================================================
PROJECT SYSTEM DOCUMENTATION & SPECIFICATIONS
================================================================================
File Name:       real_estate_ai_agent.py
Date:            May 22, 2026
Authors:         Vincenzo Pugliese (User) & Gemini AI (collaborative code) 
Purpose:         Deterministic AI Agent for Real Estate screening, entity 
                 extraction, validated data retrieval, and synthesis.
                 
Target Hardware: MacBook Intel Core i7, 16GB RAM, Radeon 560 4GB VRAM.
                 Optimized via local 3B parameter model to fit within VRAM limits.

--------------------------------------------------------------------------------
PACKAGES & DEPENDENCIES
--------------------------------------------------------------------------------
- langchain-core (v0.1.x+): Standard framework for AI orchestration & tools.
- langchain-community (v0.1.x+): Contains community integrations (Ollama).
- ollama (v0.2.x+): Local LLM runtime engine managing Llama 3.2 3B execution.
- json (Standard Library): Structural data serialized between tools and LLM.

--------------------------------------------------------------------------------
DATA PIPELINE ARCHITECTURE (WORKFLOW)
--------------------------------------------------------------------------------
[Phase 1: Ingestion & Intent Parsing (NER)]
    - Raw text input is processed via a zero-shot local LLM (Llama 3.2 3B).
    - System instructions force JSON serialization to extract Named Entities:
      `localita` (string) and `prezzo_max` (integer).

[Phase 2: Deterministic Data Retrieval (Tool Execution)]
    - The Python runtime bypasses LLM text generation.
    - Entities are mapped into explicit parameters for a standard DB query function.
    - Avoids LLM hallucinations by pulling facts directly from the database layer.

[Phase 3: Context-Injected Generation (Synthesis & Report)]
    - Retrieved structured JSON data is injected into an immutable System Prompt.
    - LLM acts as an editor/copywriter, generating a pros/cons report constrained 
      solely by the provided facts. Output style: Descriptive/Analytical.
================================================================================
"""

import json
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.llms import Ollama

# =====================================================================
# MODULE: COMPREHENSIVE LOCAL REAL ESTATE DATABASE
# =====================================================================

# Mocking a relational/document database containing properties in Rome
LOCAL_PROPERTY_DATABASE = [
    {
        "id": 1, "citta": "Roma", "prezzo": 285000, "mq": 75, "camere": 2,
        "piano": "3° senza ascensore", "stato": "Da ristrutturare", "zona": "Centocelle",
        "caratteristiche": "Balcone piccolo, riscaldamento autonomo, luminoso.",
        "immagini_meta": {"ha_giardino": False, "ha_terrazzo": False}
    },
    {
        "id": 2, "citta": "Roma", "prezzo": 245000, "mq": 60, "camere": 1,
        "piano": "Piano terra", "stato": "Buono stato", "zona": "Tuscolana",
        "caratteristiche": "Giardino privato di 40mq, vicino alla metropolitana Linea A.",
        "immagini_meta": {"ha_giardino": True, "ha_terrazzo": False}
    },
    {
        "id": 3, "citta": "Roma", "prezzo": 299000, "mq": 85, "camere": 3,
        "piano": "5° con ascensore", "stato": "Ottimo", "zona": "Monte Sacro",
        "caratteristiche": "Terrazzo abitabile, condizionatori installati, cucina abitabile.",
        "immagini_meta": {"ha_giardino": False, "ha_terrazzo": True}
    },
    {
        "id": 4, "citta": "Milano", "prezzo": 290000, "mq": 50, "camere": 1,
        "piano": "2° con ascensore", "stato": "Nuova costruzione", "zona": "Lambrate",
        "caratteristiche": "Finiture di pregio, classe energetica A4, domotica.",
        "immagini_meta": {"ha_giardino": False, "ha_terrazzo": False}
    },
    
    {
        "id": 5, "citta": "Padova", "prezzo": 365000, "mq": 125, "camere": 2,
        "piano": "4° senza ascensore", "stato": "RistrutturaTO", "zona": "Arcella",
        "caratteristiche": "Balcone grande, riscaldamento a pavimento, luminoso.",
        "immagini_meta": {"ha_giardino": True, "ha_terrazzo": False}
    },
    
    {
        "id": 6, "citta": "Torino", "prezzo": 405000, "mq": 102, "camere": 3,
        "piano": "2° con ascensore", "stato": "decente", "zona": "lungo Po'",
        "caratteristiche": "Cantina, riscaldamento autonomo, poco luminoso.",
        "immagini_meta": {"ha_giardino": False, "ha_terrazzo": False}
    }
    
    
    
]

@tool
def ricerca_prezzi(localita: str, prezzo_max: int) -> str:
    """
    Interroga il database immobiliare locale. Filtra gli annunci in base 
    alla citta e verifica che il prezzo sia minore o uguale al budget inserito.
    """
    # Query di filtraggio deterministica ad alta affidabilità (No LLM reasoning qui)
    risultati = [
        immobile for immobile in LOCAL_PROPERTY_DATABASE 
        if immobile["citta"].lower() == localita.lower() and immobile["prezzo"] <= prezzo_max
    ]
    
    if risultati:
        # Restituisce l'intera lista di match serializzata in JSON per il contesto dell'LLM
        return json.dumps(risultati, indent=2)
    return "Nessun immobile trovato nel database corrispondente ai criteri inseriti."

# =====================================================================
# AGENTE IA INTERFACE & LOGIC ENGINE
# =====================================================================

def run_real_estate_pipeline(user_query: str):
    """
    Esegue la pipeline sequenziale dell'Agente IA controllando il flusso
    di input, l'estrazione delle entità, la query al DB e la sintesi finale.
    """
    # Inizializzazione del LLM Locale tramite Ollama (Llama 3.2 3B ottimizzato per 4GB VRAM)
    llm = Ollama(model="llama3.2", temperature=0.0) # Temperature 0.0 massimizza la precisione deterministica
    
    print(f"\n[PIPELINE PHASE 1] Analisi richiesta utente: '{user_query}'")
    
    # Costruzione del prompt di sistema per Named Entity Recognition (NER) strutturato
    ner_system_prompt = (
        "Sei un modulo software di estrazione dati. Il tuo unico scopo è analizzare il testo dell'utente "
        "ed estrarre la città e il prezzo massimo richiesti.\n"
        "Rispondi ESCLUSIVAMENTE con un oggetto JSON valido contenente queste due chiavi:\n"
        "- 'localita' (valore stringa, capitalizza la prima lettera)\n"
        "- 'prezzo_max' (valore intero puro, senza punti o simboli valuta)\n"
        "Non inserire saluti, spiegazioni o testo Markdown oltre al codice JSON."
    )
    
    ner_output = llm.invoke(f"{ner_system_prompt}\nUtente: {user_query}")
    
    # Parsing ingegneristico dell'output con gestione delle eccezioni (Sailsafe fallback)
    try:
        # Pulisce eventuali spazi o caratteri spuri prima del parsing
        cleaned_json_string = ner_output.strip().replace("```json", "").replace("```", "")
        entities = json.loads(cleaned_json_string)
        localita = entities.get("localita", "Roma")
        prezzo_max = entities.get("prezzo_max", 300000)
    except Exception as e:
        print(f"   [!] Errore nel parsing JSON dell'LLM: {e}. Applicazione parametri di fallback.")
        localita, prezzo_max = "Roma", 300000
        
    print(f"   -> Entità Estratte: Località = {localita} | Budget Massimo = {prezzo_max} €")
    
    # Fase 2: Chiamata allo strumento di ricerca deterministico
    print("\n[PIPELINE PHASE 2] Interrogazione del Database Locale tramite Tool...")
    db_context = ricerca_prezzi.invoke({"localita": localita, "prezzo_max": prezzo_max})
    print("   -> Dati estratti con successo dal database strutturato.")
    
    # Fase 3: Sintesi e generazione condizionata (Evita allucinazioni)
    print("\n[PIPELINE PHASE 3] Generazione del report finale in corso...")
    synthesis_prompt = (
        "Sei un consulente immobiliare esperto e analitico.\n"
        "Basandoti UNICAMENTE ed ESCLUSIVAMENTE sui dati reali degli immobili forniti nel blocco JSON sottostante, "
        "redigi un report professionale per il cliente elencando i Pro e i Contro di ciascuna opzione trovata.\n"
        "Regole ferree: Non inventare caratteristiche, non aggiungere dettagli di quartiere se non menzionati, "
        "e attieniti strettamente ai dati fisici e descrittivi forniti.\n\n"
        f"DATA SOURCE IN JSON:\n{db_context}\n\n"
        "Scrivi il report Pro/Contro strutturato:"
    )
    
    final_report = llm.invoke(synthesis_prompt)
    return final_report

# =====================================================================
# EXECUTION ENTRY POINT
# =====================================================================
if __name__ == "__main__":
    query_cliente = "Trova una casa a Roma sotto i 300.000€ e scrivimi un riassunto dei pro e contro."
    report_output = run_real_estate_pipeline(query_cliente)
    
    print("\n" + "="*70)
    print("OUTPUT GENERATO DALL'AGENTE IA IN LOCALE")
    print("="*70)
    print(report_output)