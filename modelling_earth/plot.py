import os
import matplotlib.pyplot as plt


def plot_velocity_2d(dataset, ax, slice_grid=4, **kwargs):
    """
    Plot a quiver velocity field on a profile

    Parameters
    ----------
    dataset : :class:`xarray.Dataset`
        Dataset containing the velocity data. It must have only two dimensions given by
        ``x`` and ``z`` coordinates and contain the components of the velocity for each
        grid point given by ``velocity_x`` and ``velocity_z``
        :class:`xarray.DataArray`s.
    ax : :class:`matplotlib:Axes`
        Axe where the plot will be added.
    slice_grid : int, tuple or None (optional)
        Slice the grid coordinates to reduce the number of arrows that will be plotted.
        If ``slice_grid`` is 4, then only one array every four grid points will be
        shown. The number of arrows can be specified by axes, passing ``slice_grid`` as
        a tuple, where the first and second elements correspond to the number of arrows
        on the ``x`` and ``z`` directions, respectively. Default to 4.
    kwargs : dict
        Keyword arguments passed to :meth:`matplotlib.Axes.quiver`.
    """
    # Slice the dataset
    if slice_grid is not None:
        if type(slice_grid) is int:
            slice_x, slice_z = slice_grid, slice_grid
        elif type(slice_grid) is tuple:
            slice_x, slice_z = slice_grid[:]
        else:
            raise ValueError(
                "Invalid arguement slice_grid '{}'."
                + " Must be an integer or tuple of integers".format(slice_grid)
            )
        dataset = dataset[
            dict(x=slice(None, None, slice_x), z=slice(None, None, slice_z))
        ]
    # Plot the velocity
    ax.quiver(
        dataset.x,
        dataset.z,
        dataset.velocity_x.values.T,
        dataset.velocity_z.values.T,
        **kwargs
    )


def plot_scalar_2d(dataarray, ax, **kwargs):
    """
    Plot a pcolormesh of a scalar array on a profile

    Parameters
    ----------
    dataarray : :class:`xarray.DataArray`
        Array containing values of the scalar data. It must have only two dimensions
        given by ``x`` and ``z`` coordinates.
    ax : :class:`matplotlib:Axes`
        Axe where the plot will be added.
    kwargs : dict
        Keyword arguments passed to :func:`xarray.plot.pcolormesh`.

    Returns
    -------
    artist :
        The same type of primitive artist that the :func:`matplotlib.Axes.pcolormesh`
        function returns.
    """
    return dataarray.plot.pcolormesh(ax=ax, x="x", y="z", **kwargs)


def save_velocity_2d(dataset, save_path, fil=4, temper_levels=None):
    """
    Plot and save the 2D velocity field of arrows over the temperature field
    for each time.

    Parameters
    ----------
    dataset : :class:`xarray.Dataset`
        Array containing the velocity data.
    save_path : str
        Path to the directory to save the plots.
    fil : float
        Use to filter the number of arrows to plot.
    temper_levels : array
        Array with the levels values to plot the temperature.
    """
    for i in dataset.time:
        # Plot the velocity and the temperature
        plt.figure(figsize=(10 * 2, 2.5 * 2))
        plot_velocity_2d(dataset, time=i, fil=4, temper_levels=temper_levels)
        # Calculate the step to create the name of the plot
        k = dataset.step.values[dataset.time.values == i.values][0]
        plt.title("run/Time: %8.2f Ma" % i.values)
        filename = "velocity" + str(k).zfill(5) + ".png"
        # Save the plot
        plt.savefig(os.path.join(save_path, filename))
        plt.close()
    print("Velocity plot save in:", save_path)


def plot_data_2d(dataset_data, data, save_path, data_levels):
    """
    Plot and save the 2D data for each time.

    Parameters
    ----------
    dataset_data : :class:`xarray.Dataset`
        Array containing the data to plot.
    data : str
        Name of the data to plot and save.
    save_path : str
        Path to the directory to save the plots.
    data_levels : array
        Array with the levels values to plot the data.
    """
    for i in dataset_data.time:
        # Plot the data
        plt.figure(figsize=(10 * 2, 2.5 * 2))
        plot_args = {"x": "x", "y": "z"}
        dataset_data.sel(time=i, y=0).plot.pcolormesh(**plot_args, levels=data_levels)
        # Calculate the step to create the name of the plot
        k = dataset_data.step.values[dataset_data.time.values == i.values][0]
        plt.title("run/Time: %8.2f Ma" % i.values)
        filename = data + str(k).zfill(5) + ".png"
        # Save the plot
        plt.savefig(os.path.join(save_path, filename))
        plt.close()
    print(data, "plot save in:", save_path)
