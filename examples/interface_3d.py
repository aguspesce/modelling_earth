"""
Create interfaces for a 3D temperature distrubution
"""

import modelling_earth as me
import matplotlib.pyplot as plt
import numpy as np
import os

# Get path to the MANDYOC output directory
script_path = os.path.dirname(os.path.abspath(__file__))
mandyoc_input_path = os.path.join(script_path, "_input_data")
if not os.path.isdir(mandyoc_input_path):
    os.mkdir(mandyoc_input_path)

# Define a region of study and the number of nodes per axes
region = (0, 2000e3, 0, 80e3, -660e3, 0)
shape = (251, 9, 81)

# Create an empty coordinates grid
coordinates = me.grid_coordinates(region, shape)

# Create the lid and a temperature distribution
vertices = [[0, -100e3], [500e3, -100e3], [1000e3, -200e3], [2000e3, -200e3]]
lid = me.interface_from_vertices(vertices, coordinates)

temperature = me.litho_astheno_temperatures(coordinates, lid_depth=lid)

# Create one interface from its vertices
vertices = [[0, -20e3], [500e3, -20e3], [1000e3, -45e3], [2000e3, -45e3]]
crust = me.interface_from_vertices(vertices, coordinates)

# Merge all interfaces
interfaces = me.merge_interfaces({"lid": lid, "crust": crust})

# Plot temperature distribution
temperature.sel(y=0).plot.pcolormesh(x="x", y="z")
# Plot the interfaces
# interfaces.crust.plot()
interfaces.sel(y=0).lid.plot()
plt.gca().set_aspect("equal")
plt.show()

# Create layers data to create the layers file for MANDYOC
layers = {
    "viscosity_factor": [5, 100, 1000],
    "density": [3300, 3000, 2900],
    "radiogenic_heat": [0e-12, 0e-12, 1e-12],
    "pre-factor": [1.393e-14, 1.393e-14, 2.4168e-15],
    "exponential_factor": [3, 3, 3.5],
    "activation_energy": [429e3, 429e3, 540e3],
    "activation_volume": [15e-6, 15e-6, 25e-6],
}

# Save the interfaces to an ASCII file
me.save_interfaces(interfaces, layers, mandyoc_input_path)

# Save temperatures to an ASCII file
me.save_temperature(temperature, mandyoc_input_path)
