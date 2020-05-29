"""
Read and plot swarm positions from 3D data
"""
import os
import modelling_earth as me
import matplotlib.pyplot as plt

# Get path to the MANDYOC output directory
script_path = os.path.dirname(os.path.abspath(__file__))
mandyoc_output_path = os.path.join(script_path, "run")

# Read the particles position
swarm = me.read_mandyoc_swarm(mandyoc_output_path)
# Reduce the number of particles to take only 2 particle per cell
swarm = swarm[swarm.cc0 < 2]

# Read the MANDYOC output files
dataset = me.read_mandyoc_data(mandyoc_output_path)

# Plot the particle position over the temperature for a fxed time step
# Define the time and the step to plot
time = dataset.time.values[1]
step = dataset.step.sel(time=time).values
# Plot
fig, ax = plt.subplots()
me.plot_scalar_2d(dataset.temperature.sel(time=time, y=0), ax=ax)
me.plot_swarm_2d(swarm.loc[step], ax=ax)
plt.show()

# Plot all temperatures and particle position for every time and save the figures
figs_dir = os.path.join(script_path, "_figures")
if not os.path.isdir(figs_dir):
    os.mkdir(figs_dir)
me.save_plots_2d(
    dataset.sel(y=0),
    figs_dir,
    filename="temper_particle",
    swarm=swarm,
    scalar_to_plot="temperature",
    plot_velocity=False,
)
