"""
Read MD3D output files and plot temperature and velocity
"""
import os
import matplotlib.pyplot as plt
import modelling_earth as me


# Get path to the MD3D output directory
script_path = os.path.dirname(os.path.abspath(__file__))
md3d_output_path = os.path.join(script_path, 'run')

# Read the MD3D output files
data = me.read_md3d_data(md3d_output_path)

# Plot initial temperature
plot_args = {"x": "x", "y": "z"}
data.temperature.sel(time=0, y=0).plot.pcolormesh(**plot_args)
plt.show()

# Plot the temperature and velocity with arrows
fig, ax = plt.subplots()
ax.quiver(
    data.x,
    data.z,
    data.velocity_x.sel(time=0, y=0).T,
    data.velocity_z.sel(time=0, y=0).T
)
plt.show()
