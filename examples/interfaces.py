"""
Create interfaces for a 2D temperature distrubution
"""

import modelling_earth as me
import matplotlib.pyplot as plt
import numpy as np
import os

# Get path to the MD3D output directory
script_path = os.path.dirname(os.path.abspath(__file__))
md3d_input_path = os.path.join(script_path, "_input_data")
if not os.path.isdir(md3d_input_path):
    os.mkdir(md3d_input_path)

# Define a region of study and the number of nodes per axes
region = (0, 2000e3, -660e3, 0)
shape = (251, 81)

# Create an empty coordinates grid
coordinates = me.grid_coordinates(region, shape)

# Create a temperature distribution
lid = me.initialize_array(coordinates).sel(z=coordinates["z"][0])
lid += -300e3
temperature = me.litho_astheno_temperatures(coordinates, lid_depth=lid)

# Create the interfaces vertices
vertices = [
    [[0, -300e3], [2000e3, -300e3]],
    [[0, -20e3], [500e3, -20e3], [1000e3, -45e3], [2000e3, -45e3]],
]
names = ["lid", "crust"]
interfaces = me.interfaces(vertices, coordinates, names)

# Plot temperature distribution
temperature.plot.pcolormesh(x="x", y="z")
plt.gca().set_aspect("equal")
# Plot the interfaces
interfaces.crust.plot()
interfaces.lid.plot()
plt.show()

# Create layers data to create the layers file for MD3D
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
me.save_interfaces(interfaces, layers, md3d_input_path)
