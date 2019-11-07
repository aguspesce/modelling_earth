"""
Create a 2D initial velocity model
"""
import modelling_earth as me
import matplotlib.pyplot as plt


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
velocity_bottom_x, velocity_bottom_z = 3, 0

velocity = me.linear_velocity(
    coordinates,
    z_start,
    (velocity_bottom_x, velocity_bottom_z),
)
print(velocity.velocity_x.values.min(), velocity.velocity_x.values.max())
print(velocity.velocity_x.loc[velocity.x==velocity.x.values.max()])

# Plot
fig, ax = plt.subplots()

me.plot_velocity_2d(velocity, ax=ax, slice_grid=(4, 3))
ax.ticklabel_format(axis="both", style="sci", scilimits=(0, 0))
ax.set_aspect("equal")
#ax.set_xlim(0, 5000e3)
plt.show()
