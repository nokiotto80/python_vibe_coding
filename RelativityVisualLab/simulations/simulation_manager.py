"""
===============================================================================
Relativity Visual Lab
simulation_manager.py

Gestisce l'apertura delle simulazioni.

La MainWindow non deve conoscere direttamente i moduli delle singole
simulazioni. Questa classe funge da intermediario tra GUI e simulazioni.

===============================================================================
"""


class SimulationManager:

    def __init__(self):

        self.available_simulations = {
            "minkowski": self.open_minkowski,
            "tesseract": self.open_tesseract,
            "black_hole": self.open_black_hole,
            "wormhole": self.open_wormhole,
        }

    def open(self, simulation):

        simulation_function = self.available_simulations.get(
            simulation.module
        )

        if simulation_function is None:

            print(
                f"Modulo non disponibile: {simulation.module}"
            )

            return

        simulation_function()

    # ============================================================
    # Simulazioni
    # ============================================================
    
    def open_minkowski(self):
        """
        Avvia il modulo Minkowski come applicazione separata.
    
        Il modulo viene eseguito tramite l'interprete Python
        attualmente utilizzato dal progetto.
        """
    
        import subprocess
        import sys
        from pathlib import Path
    
        print("Apertura Diagramma di Minkowski...")
    
        # Cartella principale del progetto:
        # RelativityVisualLab/
        project_root = Path(__file__).resolve().parent.parent
    
        # Avvia il modulo Python come processo indipendente.
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "simulations.minkowski"
            ],
            cwd=project_root
        )

    def open_tesseract(self):

        print("Apertura Tesseract")

        print(">>> Modulo Tesseract non ancora collegato")

    def open_black_hole(self):

        print("Apertura Curvatura dello spazio-tempo")

        print(">>> Modulo Black Hole non ancora collegato")

    def open_wormhole(self):

        print("Apertura Wormhole")

        print(">>> Modulo Wormhole non ancora collegato")