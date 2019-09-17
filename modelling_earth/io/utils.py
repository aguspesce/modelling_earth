"""
Utility functions for reading and writing data from/to files
"""
import os
import numpy as np

TIMES_BASENAME = "Tempo_"
PARAMETERS_FILE = "param_1.5.3.txt"


def _read_parameters(parameters_file):
    """
    Read parameters file

    Parameters
    ----------
    parameters_file : str
        Path to the location of the parameters file.

    Returns
    -------
    parameters : dict
        Dictionary containing the parameters of MD3D output files.
    """
    parameters = {}
    read_n_coords, read_max_coords = False, False
    with open(parameters_file, "r") as params_file:
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
        filename = os.path.join(path, "{}{}.txt".format(TIMES_BASENAME, step))
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
