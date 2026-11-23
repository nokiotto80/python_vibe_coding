"""
===============================================================================
 Relativity Visual Lab

 simulation.py

 Rappresenta una simulazione disponibile nel laboratorio
 Iniziamo a ragionare per OGGETTI non piu per dizionari
 edit: trasformata in una DATA CLASS (anziche avere 20 righe di costruttore.
===============================================================================
"""


from dataclasses import dataclass

@dataclass
class Simulation:

    id: str
    title: str
    module: str
    icon: str
    category: str
    difficulty: int
    enabled: bool