"""
Create a 3D temperature distribution
"""
import numpy as np
import modelling_earth as me
import matplotlib.pyplot as plt

# Define a region of study and the number of nodes per axes
region = (0, 2000e3, 0, 4e3, -660e3, 0)
shape = (251, 2, 81)

# Create an empty coordinates grid
coordinates = me.grid_coordinates(region, shape)

# Define the depth to LID boundary
# Because we are working with a 3D temperature grid, the LID boundary should be defined
# as a surface, with one depth value per (x, y) coordinate pair.
# The surface must be defined as an xarray.DataArray in order to be passed to
# me.litho_astheno_temperatures().
# We can create a xarray.DataArray full of zeros by copying the temperature grid while
# fixing a single value of z, in order to create a surface, rather than copying the
# entire grid:
lid = me.initialize_array(coordinates).sel(z=coordinates["z"][0])
# Then we can fill the LID surface with our values. For example, we can set two constant
# depths for different regions in x:
lid[lid.x < 500e3] = -150e3
lid[lid.x >= 500e3] = -300e3

# Create a temperature distribution for a lithosphere and an asthenosphere passing the
# custom LID boundary
temperature = me.litho_astheno_temperatures(coordinates, lid_depth=lid)

# Plot temperature distribution
temperature.sel(y=0).plot.pcolormesh(x="x", y="z")
plt.gca().set_aspect("equal")
plt.show()
