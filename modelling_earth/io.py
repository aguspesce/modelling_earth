import os
import numpy as np
import xarray as xr
import pandas as pd

PARAMETERS_FILE = "param_1.5.3.txt"
SCALARS = {
    "temperature": "Temper",
    "density": "Rho",
    "radiogenic_heat": "H",
    "viscosity_factor": "Geoq",
    "strain": "strain",
}


def read_md3d_data(path):
    """
    Read the MD3D output files

    Parameters
    ----------
    path : str
        Path to the folder where the MD3D output files are located.

    Returns
    -------
    dataset :  :class:`xarray.Dataset`
        Dataset containing data generated by MD3D.
        Available datasets:
            - Temperature [K]
            - Velocity in x axis [m/s]
            - Velocity in y axis [m/s]
            - Velocity in z axis [m/s]
            - Velocity intensity [m/s]
            - Density [kg/m^3]
            - Radiogenic heat [W/m^3]
            - Viscosity factor
            - Strain rate [1/s]
    """
    # Read parameters
    parameters = _read_parameters(path)
    # Build coordinates
    shape = tuple(parameters[i] for i in ("nx", "ny", "nz"))
    coordinates = _build_coordinates(
        max_coords=tuple(parameters[i] for i in ("x_max", "y_max", "z_max")),
        shape=shape,
    )
    # Get array of times and steps
    steps, times = _read_times(path, parameters["print_step"], parameters["stepMAX"])
    # Create the coordinates dictionary
    dims = ("time", "x", "y", "z")
    coords = {
        "time": times,
        "step": ("time", steps),
        "x": coordinates[0],
        "y": coordinates[1],
        "z": coordinates[2],
    }
    # Create the data_vars dictionary
    data_vars = {
        scalar: (dims, _read_scalars(path, shape, steps, quantity=scalar))
        for scalar in SCALARS
    }
    # Add velocity components
    velocity_x, velocity_y, velocity_z = _read_velocity(path, shape, steps)
    data_vars["velocity_x"] = (dims, velocity_x)
    data_vars["velocity_y"] = (dims, velocity_y)
    data_vars["velocity_z"] = (dims, velocity_z)
    # Create dataset
    dataset = xr.Dataset(data_vars, coords=coords, attrs=parameters)
    return dataset


def _read_parameters(path):
    """
    Read parameters file

    Parameters
    ----------
    path : str
        Path to the folder where the MD3D output files are located.

    Returns
    -------
    parameters : dict
        Dictionary containing the parameters of MD3D output files.
    """
    parameters = {}
    read_n_coords, read_max_coords = False, False
    with open(os.path.join(path, PARAMETERS_FILE), "r") as params_file:
        for line in params_file:
            # Skip blank lines
            if not line.strip():
                continue
            # Read number of coordinates per direction
            if not read_n_coords:
                parameters["nx"], parameters["ny"], parameters["nz"] = tuple(
                    int(i) for i in line.split()
                )
                read_n_coords = True
                continue
            # Read maximum coordinates per direction
            if not read_max_coords:
                parameters["x_max"], parameters["y_max"], parameters["z_max"] = tuple(
                    float(i) for i in line.split()
                )
                read_max_coords = True
                continue
            # Read more parameters
            key, value = line.split()
            if key in "print_step stepMAX".split():
                parameters[key] = int(value)
            elif key == "timeMAX":
                parameters[key] = float(value)
            else:
                parameters[key] = value
    # Add units
    parameters["coords_units"] = "m"
    parameters["times_units"] = "Ma"
    parameters["temperature_units"] = "C"
    parameters["density_units"] = "kg/m^3"
    parameters["heat_units"] = "W/m^3"
    parameters["viscosity_factor_units"] = "dimensionless"
    parameters["strain_rate_units"] = "s^(-1)"
    return parameters


def _build_coordinates(max_coords, shape):
    """
    Create grid coordinates

    Parameters
    ----------
    max_coords : tuple
        Maximum coordinates for each direction in the following order:
        ``x_max``, ``y_max``, ``z_max`` in meters.
    shape : tuple
        Number of points for each direction in the following order:
        ``nx``, ``ny``, ``nz``.

    Returns
    -------
    coordinates : tuple
        Tuple containing grid coordinates in the following order: ``x``, ``y``, ``z``.
        All coordinates are in meters.
    """
    x_max, y_max, z_max = max_coords[:]
    nx, ny, nz = shape[:]
    # The z axis points downwards and the y axis is inverted to keep a right handed
    # coordinate system.
    x = np.linspace(0, x_max, nx)
    y = np.linspace(-y_max, 0, ny)
    z = np.linspace(-z_max, 0, nz)
    return (x, y, z)


def _read_times(path, print_step, max_steps):
    """
    Read the time files from the MD3D output

    Parameters
    ----------
    path : str
        Path to the folder where the MD3D output files are located.
    print_step : int
        Only steps multiple of ``print_step`` are saved by MD3D.
    max_steps : int
        Maximum number of steps. MD3D could break computation before the ``max_steps``
        are run if the maximum time is reached. This quantity only bounds the number of
        time files.

    Returns
    -------
    steps : numpy array
        Array containing the saved steps.
    times : numpy array
        Array containing the time of each step in Ma.
    """
    steps, times = [], []
    for step in range(0, max_steps + print_step, print_step):
        filename = os.path.join(path, "Tempo_{}.txt".format(step))
        if not os.path.isfile(filename):
            break
        with open(filename, "r") as f:
            time = float(f.readline().split()[1])
        steps.append(step)
        times.append(time)
    # Transforms lists to arrays
    times = 1e-6 * np.array(times)  # convert time units into Ma
    steps = np.array(steps, dtype=int)
    return steps, times


def _read_scalars(path, shape, steps, quantity):
    """
    Read MD3D output scalar data

    Read ``temperature``, ``density``, ``radiogenic_heat``, ``viscosity_factor`` and
    ``strain``.

    Parameters
    ----------
    path : str
        Path to the folder where the MD3D output files are located.
    shape: tuple
        Shape of the expected grid.
    steps : array
        Array containing the saved steps.
    quantity : str
        Type of scalar data to be read.

    Returns
    -------
    data: np.array
        Array containing the MD3D output scalar data.
    """
    data = []
    for step in steps:
        filename = "{}_{}.txt".format(SCALARS[quantity], step)
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
    Read MD3D output velocity data

    Parameters
    ----------
    path : str
        Path to the folder where the MD3D output files are located.
    shape: tuple
        Shape of the expected grid.
    steps : array
        Array containing the saved steps.

    Returns
    -------
    data: tuple of arrays
        Tuple containing the components of the velocity vector.
    """
    velocity_x, velocity_y, velocity_z = [], [], []
    for step in steps:
        filename = "{}_{}.txt".format("Veloc_fut", step)
        velocity = np.loadtxt(
            os.path.join(path, filename), unpack=True, comments="P", skiprows=2
        )
        # Convert very small numbers to zero
        velocity[np.abs(velocity) < 1.0e-200] = 0
        # Separate velocity into their three components
        velocity_x.append(velocity[0::3].reshape(shape, order="F"))
        velocity_y.append(velocity[1::3].reshape(shape, order="F"))
        velocity_z.append(velocity[2::3].reshape(shape, order="F"))
    velocity_x = np.array(velocity_x)
    velocity_y = np.array(velocity_y)
    velocity_z = np.array(velocity_z)
    return (velocity_x, velocity_y, velocity_z)


def read_swarm(path):
    """
    Read swarm files and return a list with the positions of the particles

    Parameters
    ----------
    path : str
        Path to the folder where the MD3D program output files are located.

    Returns
    -------
    swarm : dict
        Dictionary with the time, step and the particles positions.
        The ``time`` and ``step`` are numpy arrays. ``time`` contains the time of
        each step in Ma linked to the index of the ``positions`` list.
        ``positions`` is a list of :class:`pandas.DataFrame` which contains the
        coordinates `x`, `y` and `z` (in meters) and the flag `cc0` for each time step.
    """
    # Define variable and parameters
    positions = []
    parameters = _read_parameters(path)
    print_step = parameters["print_step"]
    max_steps = parameters["stepMAX"]
    # Determine the number of time steps
    steps, time = _read_times(path, print_step, max_steps)
    # Get swarm files
    swarm_files = [i for i in os.listdir(path) if "step_" in i]
    # Read the data
    for step_i in range(0, steps.max() + print_step, print_step):
        # Determine the rank value on the first step and check it for following steps
        step_files = [i for i in swarm_files if "step_{}-".format(step_i) in i]
        if step_i == 0:
            n_rank = len(step_files)
        else:
            if len(step_files) != n_rank:
                raise ValueError(
                    "Invalid number of ranks '{}' for step '{}'".format(
                        len(step_files), step_i
                    )
                )
        # Initialize the arrays to store the data for each step
        x, y, z, cc0 = np.array([]), np.array([]), np.array([]), np.array([])
        for rank_i in range(n_rank):
            filename = "step_{}-rank{}.txt".format(step_i, rank_i)
            x1, y1, z1, c0 = np.loadtxt(
                os.path.join(path, filename), unpack=True, usecols=(0, 1, 2, 3)
            )
            # Stack arrays in sequence horizontally
            cc0 = np.hstack((cc0, c0))
            x = np.hstack((x, x1))
            y = np.hstack((y, y1))
            z = np.hstack((z, z1))
        # Create a data frame for the current step
        data = {"x": x, "y": y, "z": z, "cc0": cc0}
        frame = pd.DataFrame(data=data)
        # Append the data frame  to the list of the particle positions
        positions.append(frame)
    # Create a dictionary
    swarm = {"time": time, "step": steps, "positions": positions}
    return swarm


def save_swarm(swarm, basename, save_path, verbose=False, **kwargs):
    """
    Save the particle position as a HDF5 file for each time step

    Parameters:
    -----------
    swarm : dict
        Dictionary with the time, step and the particles positions.
        The ``time`` and ``step`` are numpy arrays. ``time`` contains the time of
        each step in Ma linked to the index of the ``positions`` list.
        ``positions`` is a list of :class:`pandas.DataFrame`s that contain the
        coordinates `x`, `y` and `z` (in meters) and the flag `cc0` for each time step.
    basename : str
        Basename for the output files where the swarm data will be saved.
    save_path : str or None
        Path to the folder to save the particle position.
    verbose : bool (optional)
        If True, a printed message will be prompted after all files have been
        sucessfully saved. Default False.
    kwargs :
        Keyword arguments that will be passed to :meth:`pandas.DataFrame.to_hdf`. By
        default the ``mode`` will be always set to ``"w"``, and ``key`` will be
        ``swarm`` if it's not specified on ``kwargs``.
    """
    # Define time steps and the particle positions
    steps = swarm["step"]
    positions = swarm["positions"]
    # Get max number of digits on steps
    number_of_digits = len(str(steps.max()))
    # Define kwargs if missing
    kwargs["mode"] = "w"
    if "key" not in kwargs:
        kwargs["key"] = "swarm"
    # Loop to save the particle position for each time step
    for index in range(len(positions)):
        filename = "{}_{}.h5".format(
            basename, str(steps[index]).zfill(number_of_digits)
        )
        positions[index].to_hdf(os.path.join(save_path, filename), **kwargs)
    if verbose:
        print(
            "All particle positions have been successfully saved on '{}'".format(
                save_path
            )
        )
