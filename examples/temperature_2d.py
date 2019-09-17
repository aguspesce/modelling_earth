"""
Create a 2D temperature distribution
"""
import numpy as np
import modelling_earth as me
import matplotlib.pyplot as plt


# Define a region of study and the number of nodes per axes
region = (0, 2000e3, -660e3, 0)
shape = (251, 81)

# Create an empty temperature grid
temperature = me.empty_temperature_grid(region, shape)

# Define the depth to LID boundary
# Because we are working with a 2D temperature grid, the LID boundary should be defined
# as a profile, with one depth value per x coordinate point. The profile must be defined
# as an xarray.DataArray in order to be passed to me.litho_astheno_temperatures()
# We can create a xarray.DataArray full of zeros by copying the temperature grid while
# fixing a single value of z, in order to create a profile, rather than copying the
# entire grid:
lid = 0 * temperature.sel(z=temperature.z[0])
# Then we can fill the LID profile with our values. For example, lets propose a LID
# boundary that oscilates in x
lid += -300e3
lid += 30e3 * np.sin(lid.x / 20e3)

# Create a temperature distribution for a lithosphere and an asthenosphere passing the
# custom LID boundary
me.litho_astheno_temperatures(
    temperature,
    lid_depth=lid,
    lid_temperature=1262,
)

# Plot temperature distribution
temperature.plot.pcolormesh(x="x", y="z")
plt.gca().set_aspect("equal")
plt.show()
