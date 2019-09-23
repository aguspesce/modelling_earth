"""
Function to create interfaces using interpolation function
"""
import numpy as np
import xarray as xr


def interfaces(vertices, coordinates, names=None):
    """
    Create a set of interfaces by interpolating their vertices

    It works only for building interfaces in 2D as profiles.

    Parameters
    ----------
    vertices : list
        List of vertices for each interface.
    coordinates : :class:`xarray.DataArrayCoordinates`
        Two dimensional coordinates located on a regular grid.
    names : list or None
        List that contains the name of each interface in the same order that `vertices`.
        If None the name will be named automatically set by using the number of each
        interface. Default None.

    Returns
    -------
    interfaces : :class:`xarray.Dataset`
        Dataset with the interfaces depth
    """
    # Check if the coordinates are 2D
    if len(coordinates.dims) != 2:
        raise ValueError(
            "Invalid coordinates with dimension '{}': they must be 2D.".format(
                len(coordinates.dims)
            )
        )
    # Check if the number of items in interfaces name is equal to interfaces
    if len(names) != len(vertices):
        raise ValueError(
            "The number of elements in interfaces names "
            + "('{}') and interfaces ('{}') must be equal".format(
                len(names), len(interfaces)
            )
        )
    dims = "x"
    data_vars = {}
    x_min, x_max = coordinates["x"].min(), coordinates["x"].max()
    for i, nodes in enumerate(vertices):
        nodes = np.array(nodes)
        _check_boundary_vertices(nodes, x_min, x_max)
        interface = np.interp(coordinates["x"], nodes[:, 0], nodes[:, 1])
        # Define the name of each interface
        if names:
            name = names[i]
        else:
            name = "interface_{}".format(i)
        data_vars[name] = (dims, interface)
    return xr.Dataset(data_vars, coords={"x": coordinates["x"]})


def _check_boundary_vertices(vertices, x_min, x_max):
    """
    Check if boundary vertices matches the boundary of the coordinates
    """
    x = vertices[:, 0]
    if not np.allclose(x_min, x.min()) or not np.allclose(x_max, x.max()):
        raise ValueError(
            "Invalid vertices for creating the interfaces: {}. ".format(vertices)
            + "Remember to include boundary nodes that matches the coordinates "
            + "boundaries '{}.'".format((x_min, x_max))
        )
