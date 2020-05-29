"""
Creation of 2D model
====================

We want to create a 2D model ready to be passed as initial conditions to MANDYOC.
We will create a temperature distribution for lithosphere and asthenosphere, add
a subducting slab and a few different interfaces, each one with a different physical
parameters.
"""
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import modelling_earth as me

# Define a region of study and the number of nodes per axes
xmin, xmax, zmin, zmax = 0, 2000e3, -660e3, 0
region = (xmin, xmax, zmin, zmax)
shape = (251, 81)

# Define parameters for building the temperature distribution
oceanic_crust_depth = -10e3
oceanic_lid_depth = -100e3
continental_crust_depth = -35e3
continental_lid_depth = -150e3
slab_slope = 30
slab_xmin = 500e3
slab_xmax = slab_xmin + abs(continental_lid_depth) / np.tan(np.radians(slab_slope))
slab_thickness = abs(oceanic_lid_depth)
oceanic_crust_thickness = abs(oceanic_crust_depth)

# Create the coordinates for the region
coordinates = me.grid_coordinates(region, shape)


# Temperature
# ===========
# Lets create the LID for adding the subducting slab to the temperature distribution
# We will create it by interpolating the vertices of the desired LID.
lid_vertices = [
    [xmin, oceanic_lid_depth],
    [slab_xmin, oceanic_lid_depth],
    [slab_xmax, continental_lid_depth],
    [xmax, continental_lid_depth],
]
lid = me.interface_from_vertices(lid_vertices, coordinates)

# Create a temperature distribution for a lithosphere and an asthenosphere
temperature = me.litho_astheno_temperatures(coordinates, lid_depth=lid)

# Add the subducted slab to the temperature
temperature = me.subducting_slab_temperature(
    temperature, slab_slope, slab_thickness, slab_xmin, slab_xmax
)


# Interfaces
# ==========
# Lets create the interface for the true LID, i.e. the one that includes the subducting
# slab
lid = me.create_interface(coordinates)
lid.loc[dict(x=(lid.x < slab_xmin))] = oceanic_lid_depth
lid.loc[dict(x=(lid.x > slab_xmax))] = me.linear_depth(
    slab_xmax, slab_slope, (slab_xmin, oceanic_lid_depth)
)
x_slab = lid.x[(lid.x >= slab_xmin) & (lid.x <= slab_xmax)]
lid.loc[dict(x=x_slab)] = me.linear_depth(
    x_slab, slab_slope, (slab_xmin, oceanic_lid_depth)
)

# Now lets create the interface for the bottom of the oceanic crust
bottom_oceanic_crust = lid + slab_thickness - oceanic_crust_thickness
x_after_slab = dict(x=(lid.x > slab_xmax))
bottom_oceanic_crust.loc[x_after_slab] = lid.loc[x_after_slab]

# Top of the oceanic crust
top_oceanic_crust = bottom_oceanic_crust + oceanic_crust_thickness
top_oceanic_crust[x_after_slab] = lid.loc[x_after_slab]

# Bottom of continental lithosphere
bottom_continental_litho = top_oceanic_crust.copy()
bottom_continental_litho.loc[x_after_slab] = continental_lid_depth

# Bottom of the continental crust
bottom_continental_crust = xr.where(
    bottom_continental_litho < continental_crust_depth,
    continental_crust_depth,
    bottom_continental_litho,
)

# Lets merge the interfaces
interfaces = me.merge_interfaces(
    {
        "lid": lid,
        "bottom_oceanic_crust": bottom_oceanic_crust,
        "top_oceanic_crust": top_oceanic_crust,
        "bottom_continental_litho": bottom_continental_litho,
        "bottom_continental_crust": bottom_continental_crust,
    }
)


# Plot
# ====
# Plot temperature distribution
temperature.plot.pcolormesh(x="x", y="z")
# Plot the interfaces
for name, interface in interfaces.items():
    interface.plot.line(label=name)
plt.legend(loc="lower right", fontsize="x-small")
plt.ylabel("z")
plt.gca().set_aspect("equal")
# plt.savefig(os.path.join(run_dir, "Temper_0.png"), dpi=200)
plt.show()
