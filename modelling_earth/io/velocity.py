"""
Save velocity distributions to ASCII files to be read by MD3D/MD2D
"""
import os
import numpy as np

HEADER = "V1 \n V2 \n V3 \n V4"
FNAME = "veloc_0_3D.txt"


def save_velocity(velocity, path, fname=FNAME):
    """
    Save velocity grid as ASCII file ready to be read by MD3D/MD2D

    The velocity grid values are saved on three column, following each axe on
    in crescent order, with the ``x`` indexes changing faster that the ``y``, and the
    ``y`` faster than the ``z``.

    Parameters
    ----------
    velocity : :class:`xarray.Dataset`
        Dataset containing the three velocity component distribution. Can be either 2D
        or 3D.
    path : str
        Path to save the velocity file.
    fname : str (optional)
       Filename of the output ASCII file. Default to ``veloc_0_3D.txt``.
    """
    dimension = len(velocity.dims)
    shape = velocity.velocity_x.shape
    size = np.array(shape).prod()
    if dimension == 3:
        components = (velocity.velocity_x, velocity.velocity_y, velocity.velocity_z)
    elif dimension == 2:
        components = (velocity.velocity_x, velocity.velocity_z)
    velocity_to_save = np.zeros((dimension, size))
    # Ravel the velocity components and save them to a single file
    # We will use order "F" on numpy.ravel in order to make the first index to change
    # faster than the rest
    for i, component in enumerate(components):
        velocity_to_save[i, :] = component.values.ravel(order="F")
    velocity_to_save = np.reshape(velocity_to_save.T, (np.size(velocity_to_save)))
    # Will add a custom header required by MD3D/MD2D
    return np.savetxt(os.path.join(path, fname), velocity_to_save, header=HEADER)
