import os
import numpy as np
import xarray as xr


def coordinates(path):
    """
    Create grid coordinates from parameters file

    Parameters
    ----------
    path : str
        Path to the folder where the MD3D output files are located.

    Returns
    -------
    coordinate : tuple
        Coordinates in km (x, y, z).
    shape : tuple
        Total number of grid points along each direction: ``n_x``, ``n_y``, ``n_z``.
    """
    parameter_file = "param_1.5.3.txt"
    with open(os.path.join(path, parameter_file), "r") as f:
        line = f.readline()
        line = line.split()
        nx, ny, nz = int(line[0]), int(line[1]), int(line[2])
        line = f.readline()
        line = line.split()
        f.close()
        x_max, y_max, z_max = float(line[0]), float(line[1]), float(line[2])
    # Convert max coordinates to km
    x_max *= 1e-3
    y_max *= 1e-3
    z_max *= 1e-3
    # Generate the grid in km
    x = np.linspace(0, x_max, nx)
    y = np.linspace(-y_max, 0, ny)
    z = np.linspace(-z_max, 0, nz)
    shape = (nx, ny, nz)
    coordinate = (x, y, z)
    return coordinate, shape


def time_array(path, number, step):
    """
    Read the time file from the MD3D output to generate a time array

    Parameters
    ----------
    path : str
        Path to the folder where the MD3D output files are located.
    number : float
        Number of time files generated by MD3D.
    step : float
        Time step between time file.

    Returns
    -------
    time : numpy array
        Array of the time in Ma.
    """
    time = []
    for cont in range(0, number + step, step):
        filename = "Tempo_{}.txt".format(cont)
        with open(os.path.join(path, filename), "r") as f:
            tempo = float(f.readline().split()[1])
            f.close()
        # Divide by 1-6 to transform the time scale into Ma
        tempo *= 1e-6
        time = np.append(time, tempo)
    return time


def read_data(path, step, quantity):

    """
    Read the MD3D output data

    Parameters
    ----------
    path : str
        Path to the folder where the MD3D output files are located.
    parameter_file_name : str
        Name of the parameter file.
    step : float
        Time step between time file.
    quantity : str
        Output data to read

    Returns
    -------
    data: np.array or tuple
        If quantity is 'velocity', the data format is a tuple else it is an array.
    """
    quantities = {
        "temperature": "Temper",
        "velocity": "Veloc_fut",
        "density": "Rho",
        "radiogenic_heat": "H",
        "viscosity_factor": "Geoq",
        "strain": "strain",
    }

    # Obtain the shape
    coordinate, shape = coordinates(path)
    # Read data
    filename = "{}_{}.txt".format(quantities[quantity], step)

    data = np.loadtxt(
        os.path.join(path, filename), unpack=True, comments="P", skiprows=2
    )
    if quantity != "velocity":
        data[np.abs(data) < 1.0e-200] = 0
        # Reshape
        data_out = np.reshape(data, shape, order="F")
    else:
        data[np.abs(data) < 1.0e-200] = 0
        data_x, data_y, data_z = data[0::3], data[1::3], data[2::3]
        # Reshape
        data_x = np.reshape(data_x, shape, order="F")
        data_y = np.reshape(data_y, shape, order="F")
        data_z = np.reshape(data_z, shape, order="F")
        data_out = (data_x, data_y, data_z)
    return data_out


def read_md3d_data(path, step):
    """
    Generate a dataset of the output files from the MD3D for a given time step

    Parameters
    ----------
    path : str
        Path to the folder where the MD3D output files are located.
    step : float
        Time step.

    Returns
    -------
    dataset :  :class:`xarray.Dataset`
        Array containing data for a given time step.
        Available datasets:
            - Temperature
            - Velocity in x axis [m/s]
            - Velocity in z axis [m/s]
            - Velocity intensity [m/s]
            - Density [kg/m^3]
            - Radiogenic heat [W/m^3]
            - Viscosity factor
            - Stain
    """
    # Read the coordinate
    coordinate, size = coordinates(path)
    # Read the data
    temperature = read_data(path, step, quantity="temperature")
    velocity = read_data(path, step, quantity="velocity")
    density = read_data(path, step, quantity="density")
    radiogenic_heat = read_data(path, step, quantity="radiogenic_heat")
    viscosity_factor = read_data(path, step, quantity="viscosity_factor")
    strain = read_data(path, step, quantity="strain")
    # Create the dataset
    coords = {"z": coordinate[2], "y": coordinate[1], "x": coordinate[0]}
    data_vars = {
        "temperature": (["z", "y", "x"], temperature.T),
        "velocity_x": (["z", "y", "x"], velocity[0].T),
        "velocity_y": (["z", "y", "x"], velocity[1].T),
        "velocity_z": (["z", "y", "x"], velocity[2].T),
        "density": (["z", "y", "x"], density.T),
        "radiogenic_heat": (["z", "y", "x"], radiogenic_heat.T),
        "viscosity_factor": (["z", "y", "x"], viscosity_factor.T),
        "strain": (["z", "y", "x"], strain.T),
    }
    dataset = xr.Dataset(data_vars, coords=coords)
    return dataset
