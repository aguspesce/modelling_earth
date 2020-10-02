"""
Read and write data structured in regular grids
"""
import os
import numpy as np
import xarray as xr
import pandas as pd

from .utils import _read_parameters, _read_times, PARAMETERS_FILE

BASENAMES = {
    "temperature": "Temper",
    "density": "Rho",
    "radiogenic_heat": "H",
    "viscosity_factor": "Geoq",
    "strain": "strain",
    "pressure": "Pressure",
    "viscosity": "visc_",
    "velocity": "Veloc_fut",
}
DATASETS = (
    "temperature",
    "density",
    "radiogenic_heat",
    "viscosity_factor",
    "strain",
    "pressure",
    "viscosity",
    "velocity",
)
# Define which datasets are scalars meassured on the nodes of the grid, e.g. velocity is
# not a scalar, and viscosity is meassured on the center of the finite elements
SCALARS_ON_NODES = DATASETS[:6]


def read_mandyoc_data(path, parameters_file=PARAMETERS_FILE, datasets=DATASETS):
    """
    Read the MANDYOC output files

    Parameters
    ----------
    path : str
        Path to the folder where the MANDYOC output files are located.
    parameters_file : str (optional)
        Name of the parameters file. It must be located inside the ``path`` directory.
        Default to ``"param_1.5.3.txt"``.
    datasets : tuple (optional)
        Tuple containing the datasets that wants to be loaded.
        The available datasets are:
            - ``temperature``
            - ``density"``
            - ``radiogenic_heat``
            - ``viscosity_factor``
            - ``strain``
            - ``pressure``
            - ``viscosity``
            - ``velocity``
        By default, every dataset will be read.

    Returns
    -------
    dataset :  :class:`xarray.Dataset`
        Dataset containing data generated by MADYOC.
    """
    # Read parameters
    parameters = _read_parameters(os.path.join(path, parameters_file))
    # Build coordinates
    shape = parameters["shape"]
    coordinates = _build_coordinates(region=parameters["region"], shape=shape)
    # Get array of times and steps
    steps, times = _read_times(path, parameters["print_step"], parameters["stepMAX"])
    # Create the coordinates dictionary containing the coordinates of the nodes
    # and the time and step arrays. Then create data_vars dictionary containing the
    # desired scalars datasets. The number of coordiantes will depend on the dimension
    # of the read data.
    dimension = parameters["dimension"]
    coords = {"time": times, "step": ("time", steps)}
    if dimension == 2:
        dims = ("time", "x", "z")
        coords["x"], coords["z"] = coordinates[:]
    elif dimension == 3:
        dims = ("time", "x", "y", "z")
        coords["x"], coords["y"], coords["z"] = coordinates[:]

    # Create a dictionary containig the scalar data (no velocity nor viscosity)
    data_vars = {
        scalar: (dims, _read_scalars(path, shape, steps, quantity=scalar))
        for scalar in datasets
        if scalar in SCALARS_ON_NODES
    }

    # Read velocity if needed
    if "velocity" in datasets:
        velocities = _read_velocity(path, shape, steps)
        if dimension == 2:
            data_vars["velocity_x"] = (dims, velocities[0])
            data_vars["velocity_z"] = (dims, velocities[1])
        elif dimension == 3:
            data_vars["velocity_x"] = (dims, velocities[0])
            data_vars["velocity_y"] = (dims, velocities[1])
            data_vars["velocity_z"] = (dims, velocities[2])

    # Read viscosity if needed
    if "viscosity" in datasets:
        if dimension == 2:
            dims = ("time", "x_center", "z_center")
            # Add center coordinates of the finite elements to the coords
            coords["x_center"] = (coordinates[0][1:] + coordinates[0][:-1]) / 2
            coords["z_center"] = (coordinates[1][1:] + coordinates[1][:-1]) / 2
        elif dimension == 3:
            dims = ("time", "x_center", "y_center", "z_center")
            # Add center coordinates of the finite elements to the coords
            coords["x_center"] = (coordinates[0][1:] + coordinates[0][:-1]) / 2
            coords["y_center"] = (coordinates[1][1:] + coordinates[1][:-1]) / 2
            coords["z_center"] = (coordinates[2][1:] + coordinates[2][:-1]) / 2
        # Add viscosity values located on the center of the finite elements
        viscosity = _read_viscosity(path, steps, shape)
        data_vars["viscosity"] = (dims, viscosity)

    return xr.Dataset(data_vars, coords=coords, attrs=parameters)


def _build_coordinates(region, shape):
    """
    Create grid coordinates

    Parameters
    ----------
    region : tuple
        Boundary coordinates for each direction.
        If reading 3D data, they must be passed in the following order:
        ``x_min``, ``x_max``, ``y_min``, ``y_max``, ``z_min``, ``z_max``.
        If reading 2D data, they must be passed in the following order:
        ``x_min``, ``x_max``, ``z_min``, ``z_max``.
        All coordinates should be in meters.
    shape : tuple
        Number of points for each direction.
        If reading 3D data, they must be passed in the following order:
        ``nx``, ``ny``, ``nz``.
        If reading 2D data, they must be passed in the following order: ``nx``, ``nz``.

    Returns
    -------
    coordinates : tuple
        Tuple containing grid coordinates in the following order:
        ``x``, ``y``, ``z`` if 3D, or ``x``, ``z`` if 2D.
        All coordinates are in meters.
    """
    # Get number of dimensions
    dimension = len(shape)
    if dimension == 2:
        x_min, x_max, z_min, z_max = region[:]
        nx, nz = shape[:]
        x = np.linspace(x_min, x_max, nx)
        z = np.linspace(z_min, z_max, nz)
        return x, z
    elif dimension == 3:
        x_min, x_max, y_min, y_max, z_min, z_max = region[:]
        nx, ny, nz = shape[:]
        x = np.linspace(x_min, x_max, nx)
        y = np.linspace(y_min, y_max, ny)
        z = np.linspace(z_min, z_max, nz)
        return x, y, z


def _read_scalars(path, shape, steps, quantity):
    """
    Read MADYOC output scalar data

    Read ``temperature``, ``density``, ``radiogenic_heat``, ``viscosity_factor``,
    ``strain`` and ``pressure``.

    Parameters
    ----------
    path : str
        Path to the folder where the MADYOC output files are located.
    shape: tuple
        Shape of the expected grid.
    steps : array
        Array containing the saved steps.
    quantity : str
        Type of scalar data to be read.

    Returns
    -------
    data: np.array
        Array containing the MADYOC output scalar data.
    """
    data = []
    for step in steps:
        filename = "{}_{}.txt".format(BASENAMES[quantity], step)
        data_step = np.loadtxt(
            os.path.join(path, filename), unpack=True, comments="P", skiprows=2
        )
        # Convert very small numbers to zero
        data_step[np.abs(data_step) < 1.0e-200] = 0
        # Reshape data_step
        data_step = data_step.reshape(shape, order="F")
        # Append data_step to data
        data.append(data_step)
    data = np.array(data)
    return data


def _read_velocity(path, shape, steps):
    """
    Read MADYOC output velocity data

    Parameters
    ----------
    path : str
        Path to the folder where the MADYOC output files are located.
    shape: tuple
        Shape of the expected grid.
    steps : array
        Array containing the saved steps.

    Returns
    -------
    data: tuple of arrays
        Tuple containing the components of the velocity vector.
    """
    # Determine the dimension of the velocity data
    dimension = len(shape)
    velocity_x, velocity_z = [], []
    if dimension == 3:
        velocity_y = []
    for step in steps:
        filename = "{}_{}.txt".format(BASENAMES["velocity"], step)
        velocity = np.loadtxt(os.path.join(path, filename), comments="P", skiprows=2)
        # Convert very small numbers to zero
        velocity[np.abs(velocity) < 1.0e-200] = 0
        # Separate velocity into their three components
        if dimension == 2:
            velocity_x.append(velocity[0::dimension].reshape(shape, order="F"))
            velocity_z.append(velocity[1::dimension].reshape(shape, order="F"))
        elif dimension == 3:
            velocity_x.append(velocity[0::dimension].reshape(shape, order="F"))
            velocity_y.append(velocity[1::dimension].reshape(shape, order="F"))
            velocity_z.append(velocity[2::dimension].reshape(shape, order="F"))
    # Transform the velocity_* lists to arrays
    velocity_x = np.array(velocity_x)
    velocity_z = np.array(velocity_z)
    if dimension == 3:
        velocity_y = np.array(velocity_y)
        return (velocity_x, velocity_y, velocity_z)
    return (velocity_x, velocity_z)


def _read_viscosity(path, steps, shape):
    """
        Read the viscosity files generated by MADYOC. The viscosity values are defined on
    the
        center of the finite elements instead of the nodes.

        Parameters
        ----------
        path : str
            Path to the folder where the MADYOC output files are located.

        Returns
        -------
        viscosity : data: np.array
            Array containing the MADYOC output scalar data.
    """
    # Get the dimension of the data
    dimension = len(shape)
    # The number of finite elements per axe is the number of nodes minus one
    shape_centers = tuple(i - 1 for i in shape)
    # List all viscosity_files
    viscosity_files = [i for i in os.listdir(path) if BASENAMES["viscosity"] in i]
    # Initialize the viscosity array with the proper shape: (n_steps, nx, ...)
    full_shape = tuple([steps.size] + list(shape_centers))
    viscosity = np.zeros(full_shape, dtype=float)
    # Fill the viscosity array with elements read from the data files
    for step_index, step in enumerate(steps):
        # Determine the rank value on the first step and check it for following steps
        step_files = [
            i
            for i in viscosity_files
            if "{}{}_".format(BASENAMES["viscosity"], step) in i
        ]
        if step_index == 0:
            n_rank = len(step_files)
        else:
            if len(step_files) != n_rank:
                raise ValueError(
                    "Invalid number of ranks '{}' for step '{}'".format(
                        len(step_files), step
                    )
                )
        # Read rank file for this step and add the viscosity results to viscosity array
        for rank in range(n_rank):
            filename = "visc_{}_{}.txt".format(step, rank)
            if dimension == 2:
                i, k, visc = np.loadtxt(os.path.join(path, filename), unpack=True)
                i, k = i.astype(int), k.astype(int)
                viscosity[step_index, i, k] = visc
            elif dimension == 3:
                i, j, k, visc = np.loadtxt(os.path.join(path, filename), unpack=True)
                i, j, k = i.astype(int), j.astype(int), k.astype(int)
                viscosity[step_index, i, j, k] = visc
    return viscosity
