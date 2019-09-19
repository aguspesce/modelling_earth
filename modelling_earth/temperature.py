"""
Functions to create 2D and 3D temperature distributions
"""
import numpy as np
import xarray as xr
from warnings import warn

from .coordinates import initialize_array


def litho_astheno_temperatures(
    coordinates,
    lid_depth,
    surface_temperature=273.0,
    lid_temperature=1300.0,
    potential_astheno_surface_temp=1262.0,
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
    coordinates : :class:`xarray.DataArrayCoordinates`
        Coordinates located on a regular grid where the temperature distribution will be
        created. Must be in meters and can be either 2D or 3D.
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
    potential_astheno_surface_temp : float (optional)
        Potential temperature of asthenosphere if it were expanded up to the surface
        (in K). See Blom (2016).
    coeff_thermal_expansion : float (optional)
        Coefficient of thermal expansion in K^{-1}.
    specific_heat : float (optional)
        Specific heat of the asthenosphere in J/K/kg.
    gravity_acceleration : float (optional)
        Magnitude of the gravity acceleration in m/s^2.

    Returns
    -------
    temperatures : :class:`xarray.DataArray`
        Array containing the temperature distribution for the lithosphere and the
        asthenosphere.

    References
    ----------
    Blom (2016).
        State of the art numerical subduction modelling with ASPECT; thermo-mechanically
        coupled viscoplastic compressible rheology, free surface, phase changes, latent
        heat and open sidewalls. url: https://dspace.library.uu.nl/handle/1874/348133


    """
    if np.any(lid_depth > 0):
        warn(
            "Passed lid_depth has positive values. "
            + "It must be negative in order the LID to be bellow the surface."
        )
    # Initialize temperatures array
    temperatures = initialize_array(coordinates)
    # Convert lid_depth to xarray.DataArray if it's a float
    if type(lid_depth) is float or int:
        lid_depth = xr.full_like(temperatures.sel(z=temperatures.z[0]), lid_depth)
    # Broadcast lid_depth and z coordinates to the full shape of temperatures
    _, lid_depth = xr.broadcast(temperatures, lid_depth)
    _, z = xr.broadcast(temperatures, temperatures.z)
    # Compute temperature distribution for lithosphere (linear)
    temperatures += (
        lid_temperature - surface_temperature
    ) / lid_depth * z + surface_temperature
    # Add exponential temperature for the asthenosphere
    astheno_temperatures = potential_astheno_surface_temp * np.exp(
        (-1) * coeff_thermal_expansion * gravity_acceleration / specific_heat * z
    )
    # Merge both distributions ensuring continuity
    temperatures = xr.where(
        temperatures > astheno_temperatures, astheno_temperatures, temperatures
    )
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
