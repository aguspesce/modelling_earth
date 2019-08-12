import os
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

def quiver_velocity_2d(dataset, time, fil=4, temper_min,            
                       temper_max, temper_interval=10):
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
    temper_min : float
        Minimum temperature value to define the levels in the temperature plot.
    temper_max :  float
        Maximum temperature value to define the levels in the temperature plot.
    temper_interval : float
        Temperature interval to calculate the temperature level to plot
    '''
    f = fil
    # Extract the coordinate to grid
    xx, zz = np.meshgrid(dataset.x.values, dataset.z.values)
    # Plot the temperature
    plot_args = {'x': 'x', 'y': 'z'}
    temper_nevels = np.arange(temper_max, temper_max, temper_interval)
    dataset.temperature.sel(time=time,y=0).plot.pcolormesh(**plot_args, 
                            levels=temper_nevels)
    # Plot the velocity
    plt.quiver(xx[::f, ::f], zz[::f, ::f],
               dataset.velocity_x.sel(time=time, y=0).values[::f, ::f].T,
               dataset.velocity_z.sel(time=time, y=0).values[::f, ::f].T)
    plt.title('run/Time: %8.2f Ma'%time)


def save_velocity_2d(dataset, save_path, fil=4, temper_min,            
                     temper_max, temper_interval=10):
    '''
    Plot and save the 2D velocity field of arrows over the temperature field 
    for each time.     
    Parameter: 
    ---------
    dataset : :class:`xarray.Dataset`
        Array containing the velocity data.
    save_path : str
        Path to the directory to save the plots.
    fil : float
        Use to filter the number of arrows to plot.
    temper_min : float
        Minimum temperature value to define the levels in the temperature plot.
    temper_max : float
        Maximum temperature value to define the levels in the temperature plot.
    temper_interval : float
        Temperature interval to calculate the temperature level to plot    
    '''
    for i in dataset.time:
        # Plot the velocuty and the themperature
        plt.figure(figsize=(10 * 2, 2.5 * 2))
        quiver_velocity_2d(dataset, time=i, fil=4)
        # Calcule the step to create the nameof the plot
        k = dataset.step.values[dataset.time.values == i.values][0]
        plt.title('run/Time: %8.2f Ma'%i.values)
        filename = 'velocity' + str(k).zfill(5) +".png"
        # Save the plot
        plt.savefig(os.path.join(save_path, filename))
        plt.close()
    print('Velocity plot save in:', save_path)


