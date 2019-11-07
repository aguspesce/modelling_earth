"""
Functions to create 2D and 3D velocity distributions
"""

import numpy as np
import xarray as xr


def linear_velocity(coordinates, z_start, velocity_bottom=(0, 0, 0)):
    """
    Create a linear velocity distribution in the lateral boundaries where the velocity
    is zero for z > z_start and for z_min < z < z_start assume a linear increase of
    velocity until the bottom of the model.

    Parameters
    ----------
    coordinates : :class:`xarray.DataArrayCoordinates`
        Coordinates located on a regular grid where the temperature distribution will be
        created. Must be in meters and can be either 2D or 3D.
    z_start : float
        Depth value where the velocity condition changes in meters.
    velocity_bottom :
        Velocity at bottom boundary (z_min) on the x and z axes in m/ in m/s.

    Returns
    -------
    velocity : :class:`xarray.Dataset`
        Dataset containing the velocity distribution.
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
    # Check if velocity_bottom dims are in the correct order
    if len(velocity_bottom) != dimension:
        raise ValueError(
            "Invalid velocity_bottom dimensions '{}': ".format(len(velocity_bottom))
            + "must be '{}' for {}D.".format(expected_dims, dimension)
        )
    # Define the shape of the coordinates
    if dimension == 3:
        shape = (
            coordinates["x"].shape[0],
            coordinates["y"].shape[0],
            coordinates["z"].shape[0],
        )
    if dimension == 2:
        shape = (coordinates["x"].shape[0], coordinates["z"].shape[0])
    # Initialize the velocity dataset with zero values
    velocity = xr.Dataset(coords=coordinates)
    velocity["velocity_x"] = (coordinates, np.zeros(shape))
    velocity["velocity_z"] = (coordinates, np.zeros(shape))
    if dimension == 3:
        velocity["velocity_y"] = (coordinates, np.zeros(shape))
    # Calculate the velocity assume a linear increase with depth and add increasing
    # velocity values on the first and last column using a condition
    condition = np.logical_and(
        velocity.z < z_start,
        np.logical_or(velocity.x == velocity.x[0], velocity.x == velocity.x[-1]),
    )
    # Velocity in x axis
    lin_velocity_x = velocity_bottom[0] * (velocity.z - z_start) / velocity.z[0]
    velocity["velocity_x"] = velocity.velocity_x.where(~condition, lin_velocity_x)
    # Velocity in z and y axes
    if dimension == 2:
        lin_velocity_z = velocity_bottom[1] * (velocity.z - z_start) / velocity.z[0]
        velocity["velocity_z"] = velocity.velocity_z.where(~condition, lin_velocity_z)
    if dimension == 3:
        lin_velocity_y = velocity_bottom[1] * (velocity.z - z_start) / velocity.z[0]
        velocity["velocity_y"] = velocity.velocity_z.where(~condition, lin_velocity_y)
        lin_velocity_z = velocity_bottom[2] * (velocity.z - z_start) / velocity.z[0]
        velocity["velocity_z"] = velocity.velocity_z.where(~condition, lin_velocity_z)
    return velocity
