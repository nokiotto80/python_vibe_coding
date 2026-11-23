"""
simulation_loader.py

Legge il file simulations.json
e restituisce la lista delle simulazioni disponibili
come oggetti della classe Simulation.
"""

import json

from simulations.simulations import Simulation


class SimulationLoader:

    def __init__(self, json_path):

        self.json_path = json_path
        self.data = {}

    def load(self):

        with open(
            self.json_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.data = json.load(file)

    def get_simulations(self):

        simulations = []

        for item in self.data["simulations"]:

            simulation = Simulation(

                id=item["id"],
                title=item["title"],
                module=item["module"],
                icon=item["icon"],
                category=item["category"],
                difficulty=item["difficulty"],
                enabled=item["enabled"]

            )

            simulations.append(simulation)

        return simulations