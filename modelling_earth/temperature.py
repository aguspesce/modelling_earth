"""
Functions to create 3D temperature distributions
"""
import numpy as np
import xarray as xr
from warnings import warn


def empty_temperature_grid(region, shape):
    """
    Create an empty 2D or 3D temperature grid

    Parameters
    ----------
    region : tuple or list
        List containing the boundaries of the region of the grid. If the grid is 3D, the
        boundaries should be passed in the following order:
        ``x_min``, ``x_max``, ``y_min``, ``y_max``,``z_min``, ``z_max``.
        If the grid is 2D, the boundaries should be passed in the following order:
        ``x_min``, ``x_max``, ``z_min``, ``z_max``.
    shape : tuple
        Total number of grid points along each direction.
        If the grid is 3D, the tuple must be: ``n_x``, ``n_y``, ``n_z``.
        If the grid is 2D, the tuple must be: ``n_x``, ``n_z``.

    Returns
    -------
    temperature : :class:``xarray.DataArray``
        Array containing a grid with empty temperatures along with its coordinates.
    """
    if len(shape) == 2:
        nx, nz = shape[:]
        x_min, x_max, z_min, z_max = region[:]
        x = np.linspace(x_min, x_max, nx)
        z = np.linspace(z_min, z_max, nz)
        dims = ("x", "z")
        coords = {"x": x, "z": z}
    else:
        nx, ny, nz = shape[:]
        x_min, x_max, y_min, y_max, z_min, z_max = region[:]
        x = np.linspace(x_min, x_max, nx)
        y = np.linspace(y_min, y_max, ny)
        z = np.linspace(z_min, z_max, nz)
        dims = ("x", "y", "z")
        coords = {"x": x, "y": y, "z": z}
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
    lid_depth : float or :class:`xarray.DataArray`
        Depth to the surface boundary between lithosphere and asthenosphere in meters.
        Must be negative if the depth is bellow the surface. It can be a float for
        setting a constant LID depth or a custom surface (if temperature grid is 3D) or
        profile (if 2D). The surface and the profile must be passed as
        a :class:`xarray.DataArray` with ``x`` and ``y`` coordinates for the surface and
        only the horizontal coordinate for the profile.
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
    if np.any(lid_depth > 0):
        warn(
            "Passed lid_depth has positive values. "
            + "It must be negative in order the LID to be bellow the surface."
        )
    # Convert lid_depth to xarray.DataArray if it's a float
    if type(lid_depth) is float or int:
        lid_depth = xr.full_like(temperatures.sel(z=temperatures.z[0]), lid_depth)
    # Broadcast lid_depth and z coordinates to the full shape of temperatures and
    # convert them to numpy arrays
    _, lid_depth = xr.broadcast(temperatures, lid_depth)
    _, z = xr.broadcast(temperatures, temperatures.z)
    lid_depth, z = lid_depth.values, z.values
    # Add linear temperature to the lithosphere
    boolean = z > lid_depth
    temperatures.values[boolean] += (
        lid_temperature - surface_temperature
    ) / lid_depth[boolean] * z[boolean] + surface_temperature
    # Add exponential temperature for the asthenosphere
    boolean = z <= lid_depth
    temperatures.values[boolean] += lid_temperature * np.exp(
        (-1)
        * coeff_thermal_expansion
        * gravity_acceleration
        / specific_heat
        * (z[boolean] - lid_depth[boolean])
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
