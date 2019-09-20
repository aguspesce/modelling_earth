"""
Create a 2D temperature distribution
"""
import numpy as np
import modelling_earth as me
import matplotlib.pyplot as plt


# Define a region of study and the number of nodes per axes
region = (0, 2000e3, -660e3, 0)
shape = (251, 81)

# Create an empty coordinates grid
coordinates = me.grid_coordinates(region, shape)

# Define the depth to LID boundary
# Because we are working with a 2D temperature grid, the LID boundary should be defined
# as a profile, with one depth value per x coordinate point. The profile must be defined
# as an xarray.DataArray in order to be passed to me.litho_astheno_temperatures().
# We can create a xarray.DataArray full of zeros and fix a single value of z
lid = me.initialize_array(coordinates).sel(z=coordinates["z"][0])
# Then we can fill the LID profile with our values. For example, lets propose a LID
# boundary that oscilates in x
lid += -300e3
lid += 30e3 * np.sin(lid.x / 100e3)

# Create a temperature distribution for a lithosphere and an asthenosphere passing the
# custom LID boundary
temperature = me.litho_astheno_temperatures(coordinates, lid_depth=lid)

# Plot temperature distribution
temperature.plot.pcolormesh(x="x", y="z")
plt.gca().set_aspect("equal")
plt.show()
