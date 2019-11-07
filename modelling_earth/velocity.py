"""
Functions to create 2D and 3D velocity distributions
"""

import numpy as np
import xarray as xr
from .utilities import change_unit


def linear_velocity(coordinates, z_start, velocity_bottom=(0, 0)):
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
        Velocity at bottom boundary (z_min) on the x and z axes.

    Returns
    -------
    velocity : :class:`xarray.Dataset`
        Dataset containing the velocity distribution.
    """
    # Change the unit of the velocity from cm/years to m/s
    velocity_bottom_x, velocity_bottom_z = velocity_bottom[0], velocity_bottom[1]
    velocity_bottom_x = change_unit(velocity_bottom_x)
    velocity_bottom_z = change_unit(velocity_bottom_z)
    # Define the shape of the coordinates
    shape = (coordinates["x"].shape[0], coordinates["z"].shape[0])
    # Initialize the velocity dataset with zero values
    velocity = xr.Dataset(coords=coordinates)
    velocity["velocity_x"] = (coordinates, np.zeros(shape))
    velocity["velocity_z"] = (coordinates, np.zeros(shape))
    # Calculate the velocity assume a linear increase with depth
    lin_velocity_x = velocity_bottom_x * (velocity.z - z_start) / velocity.z[0]
    lin_velocity_z = velocity_bottom_z * (velocity.z - z_start) / velocity.z[0]
    # Add increasing velocity values on the first and last column
    condition = np.logical_and(
        velocity.z < z_start,
        np.logical_or(velocity.x == velocity.x[0], velocity.x == velocity.x[-1]),
    )
    velocity["velocity_x"] = velocity.velocity_x.where(~condition, lin_velocity_x)
    velocity["velocity_z"] = velocity.velocity_z.where(~condition, lin_velocity_z)
    return velocity
