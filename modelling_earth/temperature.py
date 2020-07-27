"""
Functions to create 2D and 3D temperature distributions
"""
import numpy as np
import xarray as xr
from warnings import warn

from .coordinates import create_grid
from .utilities import linear_depth

# Define default parameters for building temperature distributions
SURFACE_TEMPERATURE = 273.0
LID_TEMPERATURE = 1300.0
POTENTIAL_ASTHENO_SURFACE_TEMP = 1262.0
COEFF_THERMAL_EXPANSION = 3.28e-5
SPECIFIC_HEAT = 1250
GRAVITY_ACCELERATION = 9.8


def litho_astheno_temperatures(
    coordinates,
    lid_depth,
    surface_temperature=SURFACE_TEMPERATURE,
    lid_temperature=LID_TEMPERATURE,
    potential_astheno_surface_temp=POTENTIAL_ASTHENO_SURFACE_TEMP,
    coeff_thermal_expansion=COEFF_THERMAL_EXPANSION,
    specific_heat=SPECIFIC_HEAT,
    gravity_acceleration=GRAVITY_ACCELERATION,
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
    temperatures = create_grid(coordinates)
    # Convert lid_depth to xarray.DataArray if it's a float
    if type(lid_depth) is float or type(lid_depth) is int:
        lid_depth = xr.full_like(temperatures.sel(z=temperatures.z[0]), lid_depth)
    # Compute temperature distribution for lithosphere (linear)
    temperatures += (
        lid_temperature - surface_temperature
    ) / lid_depth * temperatures.z + surface_temperature
    # Add exponential temperature for the asthenosphere
    astheno_temperatures = potential_astheno_surface_temp * np.exp(
        (-1)
        * coeff_thermal_expansion
        * gravity_acceleration
        / specific_heat
        * temperatures.z
    )
    # Merge both distributions ensuring continuity
    temperatures = xr.where(
        temperatures > astheno_temperatures, astheno_temperatures, temperatures
    )
    return temperatures


def subducting_slab_temperature(
    temperatures,
    slope,
    thickness,
    h_min,
    h_max,
    top_temperature=SURFACE_TEMPERATURE,
    bottom_temperature=LID_TEMPERATURE,
    direction="x",
):
    """
    Create temperature distribution for a subducting slab as:

    .. math ::

        0.5 * (
               T(x, y, z) + (
                             T_{bottom}(x, y, z) - T_{top}(x, y, z)
                            ) * (z_{top} - z) / thickness + T_{top}(x, y, z)
              )

    Parameters
    ----------
    temperatures : :class:`xarray.DataArray`
        Array containing a temperature distribution.
    slope : float
        Slope of the subducting slab in degrees. A positive value creates a subducting
        slab whose top is located at ``h_min`` and its bottom on ``h_max``.
    thickness : float
        Thickness of the subducting slab in meters (must be always positive).
    h_min, h_max : float, float
        Minimum and maximum horizontal coordinates at which the subducting slab extends.
        The direction of the subduction is controlled by the ``direction`` argument.
    top_temperature : float (optional)
        Temperature at the surface of the subducting slab.
    bottom_temperature : float (optional)
        Temperature at the bottom of the subducting slab.
    direction : string (optional)
        Direction of the subduction. If working in 3D it can be either *"x"* or *"y"*.
        When working in 2D, it must be *"x"*.

    Returns
    -------
    temperatures : :class:`xarray.DataArray`
        Array containing the temperature distribution for the subducting slab on top of
        the passed ``temperatures`` distribution. Only the points inside the subducting
        slab have been overwritten.
    """
    if thickness < 0:
        raise ValueError(
            "Invalid thickness '{}': it must be always positive.".format(thickness)
        )
    # Compute top and bottom boundaries of the slab
    top = linear_depth(temperatures[direction], slope, (h_min, 0))
    bottom = top - thickness
    # Modify temperature values only inside the subducting slab
    temperatures = xr.where(
        (temperatures[direction] > h_min)
        & (temperatures[direction] < h_max)
        & (temperatures.z < top)
        & (temperatures.z > bottom),
        0.5
        * (
            temperatures
            + (bottom_temperature - top_temperature)
            * (top - temperatures.z)
            / thickness
            + top_temperature
        ),
        temperatures,
    )
    return temperatures
