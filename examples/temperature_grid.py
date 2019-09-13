import numpy as np
import modelling_earth as me
import matplotlib.pyplot as plt

# Define a region of study and the number of nodes per axes
region = (0, 2000e3, 0, 4e3, -660e3, 0)
shape = (251, 2, 81)

# Create an empty temperature grid
temperature = me.empty_temperature_grid(region, shape)

# Define the depth to LID boundary
lid_depth = -150e3

# Create a temperature distribution for a lithosphere and an asthenosphere
me.litho_astheno_temperatures(
    temperature,
    lid_depth=lid_depth,
    lid_temperature=1262,
)

temperature.sel(y=0).plot.pcolormesh(x="x", y="z")
plt.gca().set_aspect("equal")
plt.show()
