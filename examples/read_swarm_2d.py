"""
Read and plot swarm positions from 2D data
"""
import os
import modelling_earth as me
import matplotlib.pyplot as plt

# Get path to the MD3D output directory
script_path = os.path.dirname(os.path.abspath(__file__))
md3d_output_path = os.path.join(script_path, "data", "data_2d")

# Read the particles position
swarm = me.read_md3d_swarm(md3d_output_path)
# Reduce the number of particles to take only 2 particle per cell
swarm = swarm[swarm.cc0 < 2]

# Read the MD3D output files
dataset = me.read_md3d_data(md3d_output_path, datasets=["temperature"])

# Plot the particle position over the temperature for a fxed time step
# Define the time and the step to plot
time = dataset.time.values[1]
step = dataset.step.sel(time=time).values
# Plot
fig, ax = plt.subplots()
me.plot_scalar_2d(dataset.temperature.sel(time=time), ax=ax)
me.plot_swarm_2d(swarm.loc[step], ax=ax)
plt.show()

# Plot all temperatures and particle position for every time and save the figures
figs_dir = os.path.join(script_path, "_figures")
if not os.path.isdir(figs_dir):
    os.mkdir(figs_dir)
me.save_plots_2d(
    dataset,
    figs_dir,
    filename="temper_particle",
    swarm=swarm,
    scalar_to_plot="temperature",
    plot_velocity=False,
)
