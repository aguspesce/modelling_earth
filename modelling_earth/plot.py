import os
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

def quiver_velocity_2d(dataset, time, fil=4, temper_levels=None):
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
    temper_levels : array
        Array with the levels values to plot the temperature.
    '''
    f = fil
    # Extract the coordinate to grid
    xx, zz = np.meshgrid(dataset.x.values, dataset.z.values)
    # Plot the temperature
    plot_args = {'x': 'x', 'y': 'z'}
    dataset.temperature.sel(time=time,y=0).plot.pcolormesh(**plot_args,
                            levels=temper_levels)
    # Plot the velocity
    plt.quiver(xx[::f, ::f], zz[::f, ::f],
               dataset.velocity_x.sel(time=time, y=0).values[::f, ::f].T,
               dataset.velocity_z.sel(time=time, y=0).values[::f, ::f].T)
    plt.title('run/Time: %8.2f Ma'%time)


def save_velocity_2d(dataset, save_path, fil=4, temper_levels=None):
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
    temper_levels : array
        Array with the levels values to plot the temperature.
    '''
    for i in dataset.time:
        # Plot the velocity and the temperature
        plt.figure(figsize=(10 * 2, 2.5 * 2))
        quiver_velocity_2d(dataset, time=i, fil=4, temper_levels=temper_levels)
        # Calculate the step to create the name of the plot
        k = dataset.step.values[dataset.time.values == i.values][0]
        plt.title('run/Time: %8.2f Ma'%i.values)
        filename = 'velocity' + str(k).zfill(5) +".png"
        # Save the plot
        plt.savefig(os.path.join(save_path, filename))
        plt.close()
    print('Velocity plot save in:', save_path)


def plot_data_2d(dataset_data, data, save_path, data_levels):
    '''
    Plot and save the 2D data for each time.                                                Parameter:
    ---------
    dataset_data : :class:`xarray.Dataset`
        Array containing the data to plot.
    data : str
        Name of the data to plot and save.
    save_path : str
        Path to the directory to save the plots.
    data_levels : array
        Array with the levels values to plot the data.
    '''
    for i in dataset_data.time:
        # Plot the data
        plt.figure(figsize=(10 * 2, 2.5 * 2))
        plot_args = {'x': 'x', 'y': 'z'}
        dataset_data.sel(time=i,y=0).plot.pcolormesh(**plot_args,
                         levels=data_levels)
        # Calculate the step to create the name of the plot
        k = dataset_data.step.values[dataset_data.time.values == i.values][0]
        plt.title('run/Time: %8.2f Ma'%i.values)
        filename = data + str(k).zfill(5) +".png"
        # Save the plot
        plt.savefig(os.path.join(save_path, filename))
        plt.close()
    print(data, 'plot save in:', save_path)

