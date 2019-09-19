"""
Read output files from 3D modelling and plot
"""
import os
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import modelling_earth as me

# Get path to the MD3D output directory
script_path = os.path.dirname(os.path.abspath(__file__))
md3d_output_path = os.path.join(script_path, "data", "data_3d")

# Read the MD3D output files
dataset = me.read_md3d_data(md3d_output_path)
print(dataset)

# Plot single frame (for t=0)
fig, ax = plt.subplots()
# Plot temeprature and velocity
me.plot_scalar_2d(dataset.temperature.sel(time=0, y=0), ax=ax)
me.plot_velocity_2d(dataset.sel(time=0, y=0), ax=ax, slice_grid=(4, 3))
ax.ticklabel_format(axis="both", style="sci", scilimits=(0, 0))
ax.set_aspect("equal")
plt.show()
# Plot the viscosity
# me.plot_scalar_2d(dataset.viscosity.sel(time=0, y_center=0), ax=ax)
fig, ax = plt.subplots()
dataset.viscosity.sel(time=0, y_center=2000).plot.pcolormesh(
    ax=ax, x="x_center", y="z_center", norm=LogNorm()
)
ax.ticklabel_format(axis="both", style="sci", scilimits=(0, 0))
ax.set_aspect("equal")
plt.show()

# Plot all temperatures and velocities for every time and save the figures
# Create filter to get only the y=0 profile of the dataset
filter_profile = {"y": 0}
figs_dir = os.path.join(script_path, "_figures")
if not os.path.isdir(figs_dir):
    os.mkdir(figs_dir)
me.save_plots_2d(dataset.sel(**filter_profile), figs_dir, scalar_to_plot="temperature")
