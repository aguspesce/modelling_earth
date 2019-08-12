"""
Read MD3D output files and plot temperature and velocity
"""
import os
import matplotlib.pyplot as plt
import modelling_earth as me
import numpy as np

# Get path to the MD3D output directory
script_path = os.path.dirname(os.path.abspath(__file__))
md3d_output_path = os.path.join(script_path, 'run')

# Read the MD3D output files
dataset = me.read_md3d_data(md3d_output_path)


#Plot and seve the figures of the temperature and the velocity with arrows
temper_levels = np.arange(0, 2000, 10)
me.save_velocity_2d(dataset, script_path, fil=4, temper_levels=temper_levels)





       

