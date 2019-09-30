"""
Utilities functions to create the interfaces
"""

import numpy as np


def linear_depth(x, slope, point):
    r"""
    Evaluate a linear function for a given value ``x``. The parameters to define the
    function are determined through the slope (:math:`\alpha`) and values in a given
    point :math:`(x_p, z_p)`.
    The linear function is:

    .. math::
        z(x) = - \tan(\alpha) (x - x_p) + z_p

    Parameters
    ----------
    x : float or array
        Value in the ``x`` axis where the linear function will be evaluated
        to determine its value in the ``z`` axis.
    slope : float
        Slope of the linear function in degrees. A positive slop value make that the
        depth increase with the value of ``x``.
    point : tuple
        Coordinate of any point  that belongs to the linear function in the following order: (``x``, ``z``).

    Returns
    -------
    z : float or array
        Value in the ``z`` axis obtained from evaluating the linear function.
    """
    x_p, z_p = point[:]
    return -np.tan(np.radians(slope)) * (x - x_p) + z_p


def quadratic_depth(x, point_1, point_2):
    """
    Evaluate a quadratic function for a given value ``x``. The parameters to define the
    function are determined through the coordinates of two points (:math: (x_1, z_1)
    and :math: (x_2, z_2)).

    .. math ::
        z(x) = - a x^2 + b

    where,

    .. math::
         a = (z_2 - z_1) / (x_2^2 - x_1^2)

         b = z_1 - a x_1^2

    Parameters
    ----------
    x : float
        Value in the ``x`` axis where the quadratic function will be evaluated
        to determine its value in the ``z`` axis.
    point_1 : tuple
        Point where the values in the ``x`` and ``z`` axises are known.
    point_2 : tuple
        Point where the values in the ``x`` and ``z`` axises are known.

    Returns
    -------
    z : float
        Value in the ``z`` axis obtained from evaluating the quadratic function.
    """
    x_1, z_1 = point_1[:]
    x_2, z_2 = point_2[:]
    a = (z_2 - z_1) / (x_2 ** 2 - x_1 ** 2)
    b = z_1 - a * x_1 ** 2
    return a * x ** 2 + b
