#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 19:02:06 2024
Esercizio su PERCENTILE; suggerito da Google Gemini

@author: macbook_vincenzo
"""

import numpy as np
import matplotlib.pyplot as plt

# Genera un iarray nsieme di dati casuali, con distribuzione gaussiana normale
data = np.random.normal(loc=50, scale=10, size=1000)

# Calcola il 25° e il 75° percentile
percentile_25 = np.percentile(data, 25)
percentile_75 = np.percentile(data, 75)

# Visualizza i dati e i percentili
plt.hist(data, bins=30)
plt.axvline(percentile_25, color='red', linestyle='dotted', label='25° percentile: valori SOTTO la 25%') #linea di demarcazione 25
plt.axvline(percentile_75, color='green', linestyle='solid', label='75° percentile:valori SOTTO il 75%') #linea di demarcazione 75
plt.legend()
plt.show()

print(f"Il 25° percentile è: {percentile_25}")
print(f"Il 75° percentile è: {percentile_75}")