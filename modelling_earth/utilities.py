"""
Utilities functions to create the interfaces
"""

import numpy as np


def lineal_depth(x, slope, point):
    r"""
    Evaluate a lineal function for a given value ``x``. The parameters to define the
    function are determined through the slope (:math: \alpha) and values in a given
    point :math: (x_p, z_p).
    The lineal function is:

    .. math::
        z(x) = \tan(\alpha) * x + (z_p - \tan(\alpha) * x_p)


    Parameters
    ----------
    x : float or array
        Value in the ``x`` axis where the linear function will be evaluated
        to determine its value in the ``z`` axis.
    slope : float
        Slope of the lineal function in degrees.
    point : tuple
        Point where the values in the ``x`` and ``z`` axises are known.

    Returns
    -------
    z : float or array
        Value in the ``z`` axis obtained from evaluating the linear function.
    """
    a = -np.tan(np.radians(slope))
    b = point[1] - a * point[0]
    z = a * x + b
    return z


def quadratic_function(x, point_1, point_2):
    """
    Evaluate a quadratic function for a given value ``x``. The parameters to define the
    function are determined through the coordinates of two point (:math: (x_1, z_1)
    and :math: (x_2, z_2)).

    .. math ::
        z(x) = - a * x^2 + b

    where,

    .. math::
         a = (z_2 - z_1) / (x_2^2 - x_1^2)

         b = z_1[1] - a * x_1^2

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
    a = (point_2[1] - point_1[1]) / (point_2[0] ** 2 - point_1[0] ** 2)
    b = point_1[1] - a * point_1[0] ** 2
    z = a * x ** 2 + b
    return z
