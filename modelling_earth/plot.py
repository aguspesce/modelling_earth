import os
import numpy as np
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
        **kwargs,
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


def save_plots_2d(
    dataset,
    save_path,
    filename="figure",
    scalar_to_plot=None,
    plot_velocity=True,
    scalar_kwargs=None,
    velocity_kwargs=None,
    figure_format="png",
    dpi=300,
    show=False,
    **kwargs,
):
    """
    Save a profile plot for each time step of the dataset into a file

    Parameters
    ----------
    dataset : :class:`xarray.Dataset`
        Dataset containing values of scalar and/or velocity data. It must have only
        three dimensions:``x``, ``z`` and ``time``.
    save_path : str
        Path to the directory where the figures will be saved.
    filename : str (optional)
        Base for the filename of the figures. Default to ``figure``.
    scalar_to_plot : str or None
        Name of the scalar dataset that will be plotted. If ``None``, no scalar will be
        plotted. Default to ``None``.
    plot_velocity : bool (optional)
        If ``True`` the velocities will be plotted. Default ``True``.
    scalar_kwargs : dict (optional)
        Keyword arguments passed to :func:`modelling_earth.plot_scalar_2d`.
    velocity_kwargs : dict (optional)
        Keyword arguments passed to :func:`modelling_earth.plot_velocity_2d`.
    figure_format : str (optional)
        Image format. Default ``png``.
    dpi : int (optional)
        Dots per pixel for the saved image. Default 300.
    show : bool (optional)
        If ``True`` each figure will be shown after saved. Default ``False``.
    kwargs : dict (optional)
        Keyword arguments for :func:`matplotlib.pyplot.subplots` function.

    """
    if not os.path.isdir(save_path):
        raise OSError("Directory '{}' does not exist.".format(save_path))
    if velocity_kwargs is None:
        velocity_kwargs = {}
    if scalar_kwargs is None:
        scalar_kwargs = {}
    # Get levels
    if scalar_to_plot:
        min_scalar = getattr(dataset, scalar_to_plot).min()
        max_scalar = getattr(dataset, scalar_to_plot).max()
        levels = np.linspace(min_scalar, max_scalar, 256)
    # Get max number of digits on steps
    number_of_digits = len(str(dataset.step.values.max()))
    # Initialize quiver to None
    quiver = None
    # Generate figure
    for step, time in zip(dataset.step, dataset.time):
        fig, ax = plt.subplots(**kwargs)
        if scalar_to_plot:
            plot_scalar_2d(
                getattr(dataset.sel(time=time), scalar_to_plot),
                ax=ax,
                levels=levels,
                **scalar_kwargs,
            )
        if plot_velocity:
            if quiver is None:
                scale = None
            else:
                scale = quiver.scale
            quiver = plot_velocity_2d(
                dataset.sel(time=time), ax=ax, scale=scale, **velocity_kwargs
            )
        # Configure plot
        ax.set_aspect("equal")
        ax.ticklabel_format(axis="both", style="sci", scilimits=(0, 0))
        plt.tight_layout()
        # Save the plot
        figure_name = "{}_{}.{}".format(
            filename, str(step.values).zfill(number_of_digits), figure_format
        )
        plt.savefig(os.path.join(save_path, figure_name), dpi=dpi)
        if show:
            plt.show()
        plt.clf()
    print("All figures have been succesfully saved on {}".format(save_path))
