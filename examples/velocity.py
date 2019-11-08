"""
Create a 2D initial velocity model
"""
import numpy as np
import modelling_earth as me
import matplotlib.pyplot as plt
import os

# Get path to the MD3D output directory
script_path = os.path.dirname(os.path.abspath(__file__))
md3d_input_path = os.path.join(script_path, "_input_data")
if not os.path.isdir(md3d_input_path):
    os.mkdir(md3d_input_path)

# Define a region of study and the number of nodes per axes
x_min, x_max, z_min, z_max = 0, 2000e3, -660e3, 0
region = (x_min, x_max, z_min, z_max)
shape = (251, 81)
# Create an empty coordinates grid
coordinates = me.grid_coordinates(region, shape)

# Create a linear velocity distribution in the lateral boundaries like this:
# velocity = 0 for z > -300 km and for -660 < z < -300 km assume a linear increase of
# velocity until the bottom of the model.
z_start = -300e3
velocity_bottom_x, velocity_bottom_z = 3 * 0.01 / (365 * 24 * 3600), 0

velocity = me.linear_velocity(
    coordinates, z_start, (velocity_bottom_x, velocity_bottom_z)
)

# Plot
fig, ax = plt.subplots()
scale = 2 * np.abs(velocity.velocity_x.values).max()
me.plot_velocity_2d(velocity, ax=ax, slice_grid=None, scale=scale)
ax.ticklabel_format(axis="both", style="sci", scilimits=(0, 0))
ax.set_aspect("equal")
plt.show()

# Save the velocity in ASCII file
me.save_velocity(velocity, md3d_input_path)
