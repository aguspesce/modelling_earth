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
            - Viscosity [Pa s]
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
    # Create the coordinates dictionary containing the coordinates of the nodes, the
    # coordinates of the center of the finite elements, and the time and step arrays
    coords = {
        "time": times,
        "step": ("time", steps),
        "x": coordinates[0],
        "y": coordinates[1],
        "z": coordinates[2],
        "x_center": (coordinates[0][1:] + coordinates[0][:-1]) / 2,
        "y_center": (coordinates[1][1:] + coordinates[1][:-1]) / 2,
        "z_center": (coordinates[2][1:] + coordinates[2][:-1]) / 2,
    }
    # Create the data_vars dictionary
    dims = ("time", "x", "y", "z")
    data_vars = {
        scalar: (dims, _read_scalars(path, shape, steps, quantity=scalar))
        for scalar in SCALARS
    }
    # Add velocity components
    velocity_x, velocity_y, velocity_z = _read_velocity(path, shape, steps)
    data_vars["velocity_x"] = (dims, velocity_x)
    data_vars["velocity_y"] = (dims, velocity_y)
    data_vars["velocity_z"] = (dims, velocity_z)
    # Add viscosity values located on the center of the finite elements
    dims = ("time", "x_center", "y_center", "z_center")
    viscosity = _read_viscosity(path, steps, parameters)
    data_vars["viscosity"] = (dims, viscosity)
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
    parameters["viscosity_units"] = "Pa s"
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


def read_md3d_swarm(path):
    """
    Read swarm files generated by MD3D and return the positions of the particles in time

    Parameters
    ----------
    path : str
        Path to the folder where the MD3D output files are located.

    Returns
    -------
    swarm : :class:`pandas.DataFrame`
        DataFrame containing the particles positions for every time step. The positions
        of the particles are given by ``x``, ``y`` and ``z`` in meters. The ``cc0`` is
        the number assigned to each particle belonging to a finite element. The ``time``
        is given in Ma. The index of the :class:`pandas.DataFrame` correspond to the
        step number.
    """
    # Determine the number of time steps
    parameters = _read_parameters(path)
    print_step = parameters["print_step"]
    max_steps = parameters["stepMAX"]
    steps, times = _read_times(path, print_step, max_steps)
    # Get swarm files
    swarm_files = [i for i in os.listdir(path) if "step_" in i]
    # Initialize the list of dataframes that will be concatenated
    dataframes = []
    # Read the data
    for i, (step, time) in enumerate(zip(steps, times)):
        # Determine the rank value on the first step and check it for following steps
        step_files = [i for i in swarm_files if "step_{}-".format(step) in i]
        if i == 0:
            n_rank = len(step_files)
        else:
            if len(step_files) != n_rank:
                raise ValueError(
                    "Invalid number of ranks '{}' for step '{}'".format(
                        len(step_files), step
                    )
                )
        # Read particles positions for the current step
        dataframes.append(_read_md3d_single_swarm(path, step, time, n_rank))
    # Concatenate the dataframes
    swarm = pd.concat(dataframes)
    return swarm


def _read_md3d_single_swarm(path, step, time, n_rank):
    """
    Read swarm positions for a single time step from MD3D output files
    """
    x, y, z, cc0 = tuple(np.array([]) for i in range(4))
    for rank_i in range(n_rank):
        filename = "step_{}-rank{}.txt".format(step, rank_i)
        x_rank, y_rank, z_rank, cc0_rank = np.loadtxt(
            os.path.join(path, filename), unpack=True, usecols=(0, 1, 2, 3)
        )
        # Stack arrays in sequence horizontally
        cc0 = np.hstack((cc0, cc0_rank))
        x = np.hstack((x, x_rank))
        y = np.hstack((y, y_rank))
        z = np.hstack((z, z_rank))
    # Create a data frame for the current step
    data = {"x": x, "y": y, "z": z, "cc0": cc0, "time": time}
    df = pd.DataFrame(data=data, index=step * np.ones_like(x, dtype=int))
    return df


def _read_viscosity(path, steps, parameters):
    """
    Read the viscosity files generated by MD3D. The viscosity values are defined on the
    center of the finite elements instead of the nodes.

    Parameters
    ----------
    path : str
        Path to the folder where the MD3D output files are located.

    Returns
    -------
    viscosity : data: np.array
        Array containing the MD3D output scalar data.
    """
    # Determine the number of finite element centers per axes as the number of nodes per
    # axes minus one
    nx_centers, ny_centers, nz_centers = tuple(
        parameters[i] - 1 for i in ("nx", "ny", "nz")
    )
    # List all viscosity_files
    viscosity_files = [i for i in os.listdir(path) if "visc_" in i]
    # Initialize the viscosity array
    viscosity = np.zeros((steps.size, nx_centers, ny_centers, nz_centers), dtype=float)
    # Fill the viscosity array with elements read from the data files
    for step_index, step in enumerate(steps):
        # Determine the rank value on the first step and check it for following steps
        step_files = [i for i in viscosity_files if "visc_{}_".format(step) in i]
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
            i, j, k, visc = np.loadtxt(os.path.join(path, filename), unpack=True)
            i, j, k = tuple(indices.astype(int) for indices in (i, j, k))
            viscosity[step_index, i, j, k] = visc
    return viscosity
