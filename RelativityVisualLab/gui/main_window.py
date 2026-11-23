"""
===============================================================================
Relativity Visual Lab
main_window.py

Finestra principale del progetto.

La MainWindow riceve una lista di oggetti Simulation e genera
dinamicamente un pulsante per ogni simulazione disponibile.

Per ora la GUI è volutamente semplice:
    - nessuna grafica astronomica;
    - nessun logo;
    - nessuna animazione;
    - nessun lancio dei moduli.

Questi elementi verranno aggiunti successivamente.

===============================================================================
"""
from simulations.simulation_manager import SimulationManager
import tkinter as tk


class MainWindow:

    def __init__(self, simulations):
        
        self.simulations = simulations
	    
        self.simulation_manager = SimulationManager()

        # ---------------------------------------------------------
        # Finestra principale
        # ---------------------------------------------------------

        self.root = tk.Tk()

        self.root.title("Relativity Visual Lab")

        self.root.geometry("700x500")

        # ---------------------------------------------------------
        # Titolo
        # ---------------------------------------------------------

        self.title_label = tk.Label(
            self.root,
            text="RELATIVITY VISUAL LAB",
            font=("Helvetica", 22, "bold")
        )

        self.title_label.pack(pady=25)

        # ---------------------------------------------------------
        # Sottotitolo
        # ---------------------------------------------------------

        self.subtitle_label = tk.Label(
            self.root,
            text="Visualizzazioni didattiche di relatività e spazio-tempo",
            font=("Helvetica", 12)
        )

        self.subtitle_label.pack(pady=5)

        # ---------------------------------------------------------
        # Contenitore dei pulsanti
        # ---------------------------------------------------------

        self.buttons_frame = tk.Frame(self.root)

        self.buttons_frame.pack(
            pady=30
        )

        # ---------------------------------------------------------
        # Generazione dinamica dei pulsanti
        # ---------------------------------------------------------

        self.create_simulation_buttons()

    # =================================================================
    # Creazione dinamica dei pulsanti
    # =================================================================

    def create_simulation_buttons(self):

        for simulation in self.simulations:

            button = tk.Button(

                self.buttons_frame,

                text=simulation.title,

                width=35,

                height=2,

                command=lambda sim=simulation:
                    self.open_simulation(sim)

            )

            button.pack(pady=8)

    # =================================================================
    # Azione del pulsante
    # =================================================================

    def open_simulation(self, simulation):

        print(
            f"Selezionata simulazione: "
            f"{simulation.id} | "
            f"{simulation.title} | "
            f"{simulation.module}"
    )

        self.simulation_manager.open(simulation)

    # =================================================================
    # Avvio GUI
    # =================================================================

    def run(self):

        self.root.mainloop()