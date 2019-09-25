"""
Save temperature distributions to ASCII files to be read by MD3D
"""
import os
import numpy as np

HEADER = "T1 \n T2 \n T3 \n T4"
FNAME = "Temper_0_3D.txt"


def save_temperature(temperatures, path, fname=FNAME):
    """
    Save temperatures grid as ASCII file ready to be read by MD3D

    The temperatures grid values are saved on a single column, following each axe on
    in crescent order, with the ``x`` indexes changing faster that the ``y``, and the
    ``y`` faster than the ``z``.

    Parameters
    ----------
    temperatures : :class:`xarray.DataArray`
        Array containing a temperature distribution. Can be either 2D or 3D.
    path : str
        Path to save the temperature file.
    fname : str (optional)
       Filename of the output ASCII file. Deault to ``Temper_0_3D.txt``.
    """
    # Check if temperatures is 2D or 3D
    dimension = len(temperatures.dims)
    if dimension == 3:
        expected_dims = ("x", "y", "z")
    elif dimension == 2:
        expected_dims = ("x", "z")
    else:
        raise ValueError(
            "Invalid temperatures array with dimension {}: ".format(dimension)
            + "must be either 2 or 3."
        )
    # Check if temperature dims are in the correct order
    if temperatures.dims != expected_dims:
        raise ValueError(
            "Invalid temperature dimensions '{}': ".format(temperatures.dims)
            + "must be '{}' for {}D temperatures.".format(expected_dims, dimension)
        )
    # Ravel and save temperatures
    # We will use order "F" on numpy.ravel in order to make the first index to change
    # faster than the rest
    # Will add a custom header required by MD3D
    np.savetxt(
        os.path.join(path, fname), temperatures.values.ravel(order="F"), header=HEADER
    )
