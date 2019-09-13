"""
Functions to create 3D temperature distributions
"""
import numpy as np
import xarray as xr
from warnings import warn


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
    temperatures = xr.DataArray(np.zeros(shape), coords=coords, dims=dims)
    return temperatures


def litho_astheno_temperatures(
    temperatures,
    lid_depth,
    surface_temperature=273.0,
    lid_temperature=1300.0,
    coeff_thermal_expansion=3.28e-5,
    specific_heat=1250,
    gravity_acceleration=9.8,
):
    """
    Create a temperature distribution for lithosphere and asthenosphere

    Assigns a linear temperature for the lithosphere and an adiabatic temperature on the
    asthenosphere.

    Parameters
    ----------
    temperatures : :class:`xarray.DataArray`
        Array containing temperatures. Use :func:`empty_temperature_grid` to
        create it if you haven't defined one. The new temperature distribution will be
        added to these values. Temperatures will be computed in K.
    lid_depth : float or array
        Depth to the surface boundary between lithosphere and asthenosphere in meters.
        Must be negative if the depth is bellow the surface.
    surface_temperature : float (optional)
        Temperature at the top of the lithosphere in K.
    lid_temperature : float (optional)
        Temperature at the LID in K.
    coeff_thermal_expansion : float (optional)
        Coefficient of thermal expansion in K^{-1}.
    specific_heat : float (optional)
        Specific heat of the asthenosphere in J/K/kg.
    gravity_acceleration : float (optional)
        Magnitude of the gravity acceleration in m/s^2
    """
    if lid_depth > 0:
        warn(
            "Passed lid_depth is positive. "
            + "It must be negative if you want the LID to be bellow the surface."
        )
    # Add linear temperature to the lithosphere
    boolean = {"z": slice(lid_depth, None)}
    temperatures.loc[boolean] += (
        lid_temperature - surface_temperature
    ) / lid_depth * temperatures.loc[boolean].z + surface_temperature
    # Add exponential temperature for the asthenosphere
    boolean = {"z": slice(None, lid_depth)}
    temperatures.loc[boolean] += lid_temperature * np.exp(
        (-1)
        * coeff_thermal_expansion
        * gravity_acceleration
        / specific_heat
        * (temperatures.loc[boolean].z - lid_depth)
    )


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
