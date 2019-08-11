import os
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

def quiver_velocity_2d(dataset, time, fil=4 ):
    '''
    Plot a 2D velocity field of arrows over the temperature. 
        
    Parameter: 
    ---------
    dataset : :class:`xarray.Dataset`
        Array containing the velocity data.
    all_time : 
    time : float
        Time to generate the plot.
    fil : float
        Use to filter the number of arrows to plot.
    '''
    f = fil
    # Extract the coordinate to grid
    x = dataset.x.values
    z = dataset.z.values
    xx, zz = np.meshgrid(x,z)
    # Plot the temperature
    plot_args = {'x': 'x', 'y': 'z'}
    dataset.temperature.sel(time=time,y=0).plot.pcolormesh(**plot_args)
    # Plot the velocity
    plt.quiver(xx[::f, ::f], zz[::f, ::f],
               dataset.velocity_x.sel(time=time, y=0).values[::f, ::f].T,
               dataset.velocity_z.sel(time=time, y=0).values[::f, ::f].T)
    plt.title('run/Time: %8.2f Ma'%time)
            
