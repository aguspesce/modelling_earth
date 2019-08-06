"""
Functions to create 3D temperature distributions
"""
import numpy as np
import xarray as xr


def empty_temperature_grid(region, shape):
    """
    Create an empty 3D temperature grid

    Parameters
    ----------
    region : tuple or list
        List containing the boundaries of the region of the grid in the following order:
        ``x_min``, ``x_max``, ``y_min``, ``y_max``,``z_min``, ``z_max``.
    shape : tuple
        Total number of grid points along each direction: ``n_x``, ``n_y``, ``n_z``.

    Returns
    -------
    temperature : :class:``xarray.DataArray``
        Array containing a grid with empty temperatures along with its coordinates.
    """
    nx, ny, nz = shape[:]
    x_min, x_max, y_min, y_max, z_min, z_max = region[:]
    x = np.linspace(x_min, x_max, nx)
    y = np.linspace(y_min, y_max, ny)
    z = np.linspace(z_min, z_max, nz)
    coords = [x, y, z]
    dims = ("x", "y", "z")
    temperatures = xr.DataArray(np.nan * np.ones(shape), coords=coords, dims=dims)
    return temperatures


def litho_astheno_temperatures(temperatures, boundary_depth, lithosphere_gradient=1300):
    """
    Create a temperature distribution for lithosphere and asthenosphere

    Parameters
    ----------
    temperatures : :class:`xarray.DataArray`
        Array containing null temperatures. Use :func:`empty_temperature_grid` to create
        it.
    boundary_depth : float
        Depth to the boundary between lithosphere and asthenosphere
    linear_gradient : float
        Gradient of linear temperature profile on lithosphere.

    Returns
    -------
    temperatures : :class:`xarray.DataArray`
        Array containing the temperature distribution of lithosphere and asthenosphere.
    """
    linear = temperatures.copy()
    exponential = temperatures.copy()
    # Create linear temperature (model for the lithosphere)
    linear[:] = temperatures.z / boundary_depth * lithosphere_gradient
    # Create exponential temperature (model for the asthenosphere)
    exponential[:] = 1262 / np.exp(-10 * 3.28e-5 * temperatures.z * 1000 / 1250)
    temperatures = xr.where(linear > exponential, exponential, linear)
    return temperatures


def add_subducting_slab(
    temperatures, xmin, xmax, slope, thickness, lithosphere_gradient=1300
):
    """
    Add temperature of a subducting slab to a temperature grid
    """
    top = np.tan(np.radians(slope)) * (temperatures.x - xmin)
    bottom = top - thickness
    temperatures_with_slab = xr.where(
        (temperatures.coords["x"] < xmax)
        & (temperatures.coords["x"] > xmin)
        & (temperatures.coords["z"] < top)
        & (temperatures.coords["z"] > bottom),
        (temperatures + lithosphere_gradient * (temperatures.z - top) / 100.0) / 2,
        temperatures,
    )
    return temperatures_with_slab
