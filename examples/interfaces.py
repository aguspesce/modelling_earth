"""
Create interfaces for a 2D temperature distrubution
"""

import modelling_earth as me
import matplotlib.pyplot as plt
import numpy as np

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
