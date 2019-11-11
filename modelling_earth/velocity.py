"""
Functions to create 2D and 3D velocity distributions
"""

import numpy as np
import xarray as xr


def linear_velocity(coordinates, z_start, velocity_bottom, direction="x"):
    """
    Hotizontal velocity distribution along a define direction.
    The velocity will be zero above the z_start and will linearly increase bellow that
    depth until the bottom of the grid. The velocity distribution will be defined on
    both lateral boundaries.

    Parameters
    ----------
    coordinates : :class:`xarray.DataArrayCoordinates`
        Coordinates located on a regular grid where the temperature distribution will be
        created. Must be in meters and can be either 2D or 3D.
    z_start : float
        Depth value where the velocity condition changes in meters.
    velocity_bottom : float
        Velocity at bottom boundary (z_min) on the x and z axes in m/s.
    direction : string (optional)
        Direction of the subduction. If working in 3D it can be either *"x"* or *"y"*.
        When working in 2D, it must be *"x"*.

    Returns
    -------
    velocity : :class:`xarray.Dataset`
        Dataset containing the velocity distribution.
    """
    # Check if coordinates is 2D or 3D and if velocity dims are corrected
    dimension, expected_dims = _check_velocity(coordinates, velocity_bottom)
    # Define the shape of the coordinates
    shape = tuple(coordinates[i].size for i in expected_dims)
    # Initialize the velocity dataset with zero values
    velocity = xr.Dataset(coords=coordinates)
    for i in expected_dims:
        velocity["velocity_{}".format(i)] = (coordinates, np.zeros(shape))

    # Calculate the velocity.
    # Assume a linear increase with depth where where the velocity is 0 for
    # coordines.z > z_start and for coordinates.z[0] < z < z_start.
    # These velocity values must be added on the first and last column.
    # Define the condition to calculate the velocity
    condition = np.logical_and(
        velocity.z < z_start,
        np.logical_or(velocity.x == velocity.x[0], velocity.x == velocity.x[-1]),
    )
    # Calculate the linear increase
    linear_increase = _linear_velocity_calculation(velocity, z_start, velocity_bottom)
    # Add the linear increase along the direction if subduction according the condition
    velocity["velocity_{}".format(direction)] = velocity[
        "velocity_{}".format(direction)
    ].where(~condition, linear_increase)
    return velocity


def _check_velocity(coordinates, velocity_value):
    """
    Check if coordinates is 2D or 3D.
    """
    # Check if coordinates is 2D or 3D
    dimension = len(coordinates.dims)
    if dimension == 3:
        expected_dims = ("x", "y", "z")
    elif dimension == 2:
        expected_dims = ("x", "z")
    else:
        raise ValueError(
            "Invalid coordinates with dimension {}: ".format(dimension)
            + "must be either 2 or 3."
        )
    return dimension, expected_dims


def _linear_velocity_calculation(velocity, z_start, velocity_bottom):
    """
    Calculation of the velocity assuming a liner increase with depth
    """
    lin_velocity = velocity_bottom * (velocity.z - z_start) / velocity.z[0]
    return lin_velocity
