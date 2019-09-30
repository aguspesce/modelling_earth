"""
Create a temperature distribution for a subducting slab in 2D
"""
import numpy as np
import modelling_earth as me
import matplotlib.pyplot as plt

# Define a region of study and the number of nodes per axes
region = (0, 800e3, -300e3, 0)
shape = (251, 81)

# Define parameters for building the temperature distribution
oceanic_lid_depth = -100e3
continental_lid_depth = -150e3
slab_slope = 30
slab_xmin, slab_xmax = 300e3, 500e3
slab_thickness = abs(oceanic_lid_depth)

# Create an empty coordinates grid
coordinates = me.grid_coordinates(region, shape)

# Define the depth to LID boundary
# Because we are working with a 2D temperature grid, the LID boundary should be defined
# as a profile, with one depth value per x coordinate point. The profile must be defined
# as an xarray.DataArray in order to be passed to me.litho_astheno_temperatures().
# We can create a xarray.DataArray full of zeros and fix a single value of z
lid = me.create_grid(coordinates).sel(z=coordinates["z"][0])
# Compute the lid interface (this must be done with a proper interfaces function)
lid_points = (
    [region[0], slab_xmin, slab_xmax, region[1]],
    [
        oceanic_lid_depth,
        oceanic_lid_depth,
        continental_lid_depth,
        continental_lid_depth,
    ],
)
lid += np.interp(lid.x, *lid_points)

# Create a temperature distribution for a lithosphere and an asthenosphere passing the
# custom LID boundary
temperature = me.litho_astheno_temperatures(coordinates, lid_depth=lid)
print(temperature.dims)
temperature = me.subducting_slab_temperature(
    temperature, slab_slope, slab_thickness, slab_xmin, slab_xmax
)

print(temperature.dims)

# Plot temperature distribution
temperature.plot.pcolormesh(x="x", y="z")
plt.gca().set_aspect("equal")
plt.show()
