"""
===============================================================================
Relativity Visual Lab
main.py

Entry point principale dell'applicazione.

Responsabilità:
    1. caricare le simulazioni dal file JSON;
    2. creare gli oggetti Simulation tramite SimulationLoader;
    3. passare le simulazioni alla MainWindow;
    4. avviare l'interfaccia grafica.

===============================================================================
"""

from gui.simulation_loader import SimulationLoader
from gui.main_window import MainWindow


def main():

    # ---------------------------------------------------------
    # Caricamento delle simulazioni
    # ---------------------------------------------------------

    loader = SimulationLoader(
        "config/simulations.json"
    )

    loader.load()

    simulations = loader.get_simulations()

    # ---------------------------------------------------------
    # Creazione della finestra principale
    # ---------------------------------------------------------

    window = MainWindow(
        simulations
    )

    # ---------------------------------------------------------
    # Avvio GUI
    # ---------------------------------------------------------

    window.run()


if __name__ == "__main__":

    main()