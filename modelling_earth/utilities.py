"""
Utilities functions to create the interfaces and the temperature for a subduction zone
"""

import numpy as np


def z_from_lineal_function(slope, point, x):
    r"""
    Calculate the value (:math: z(x)) in the ``z`` axis from a given value (:math: x)
    in the ``x`` axis for a linear function using the slope (:math: \alpha) and values
    in a given point :math: (x_p, z_p).
    The lineal function is:

    .. math::
        z(x) = \tan(\alpha) * x + (z_p - \tan(\alpha) * x_p)


    Parameters
    ----------
    slope : float
        Slope of the lineal function in degrees.
    point : tuple
        Point where the values in the ``x`` and ``z`` axises are known.
    x : float
        Value in the ``x`` axis where the linear function will be evaluated
        to determine its value in the ``z`` axis.

    Return
    ------
    z : float
        Value in the ``z`` axis obtained from evaluating the linear function.
    """
    a = -np.tan(np.radians(slope))
    b = point[1] - a * point[0]
    z = a * x + b
    return z


def x_from_lineal_function(slope, point, z):
    r"""
    Calculate the value (:math: x) in the ``x`` axis from a given value (:math: z)
    in the ``z`` axis for a linear function using the slope (:math: \alpha) and values
    in a given point :math: (x_p, z_p).
    The lineal function is:

    .. math::
        z = \tan(\alpha) * x + (z_p - \tan(\alpha) * x_p)

    Therefore the value of :math: x for a given value of :math: z is:

    .. math ::
        x = (z - z_p + \tan(\alpha) * x_p) / \tan(\alpha)

    Parameters
    ----------
    slope : float
        Slope of the lineal function in degrees.
    point : tuple
        Point where the values in the ``x`` and ``z`` axises are known.
    z : float
        Value in the ``z`` axis to determine its associated value in the ``z`` axis.

    Return
    ------
    x : float
        Value in the ``x`` axis.
    """
    a = -np.tan(np.radians(slope))
    x = (z - point[1] + a * point[0]) / a
    return x


def quadratic_function(point_1, point_2, x):
    """
    Evaluate a quadratic function (:math: z(x)). The function is created through the
    coordinates of two point (:math: (x_1, z_1) and :math: (x_2, z_2)).

    .. math ::
        z(x) = - a * x^2 + b

    where,

    .. math::
         a = (z_2 - z_1) / (x_2^2 - x_1^2)

         b = z_1[1] - a * x_1^2

    Parameters
    ----------
    point_1 : tuple
        Point where the values in the ``x`` and ``z`` axises are known.
    point_2 : tuple
        Point where the values in the ``x`` and ``z`` axises are known.
    x : float
        Value in the ``x`` axis where the quadratic function will be evaluated
        to determine its value in the ``z`` axis.

    Return
    ------
    z : float
        Value in the ``z`` axis obtained from evaluating the quadratic function.
    """
    a = (point_2[1] - point_1[1]) / (point_2[0] ** 2 - point_1[0] ** 2)
    b = point_1[1] - a * point_1[0] ** 2
    z = a * x ** 2 + b
    return z
