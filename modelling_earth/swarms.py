import numpy as np
import pandas as pd
import os
from .io import _read_parameters


def read_swarm(path, rank=4):
    """
    Create a list of dataframe with the position of the particle.
    
    Parameters: 
    -----------
    path : str
        Path to the folder where the MD3D program output files are located.
    rank : float
        Number of processors used in the simulation.
    Returns: 
    -------
    list_frame
 : list
        List of `xarray.Dataset` which contains the coordinate `x`, `y` and `z`
       for each time step.
    """
    x, y, z, cc, cc0 = [], [], [], [], []
    list_frame = []
    parameters = _read_parameters(path)
    print_step = parameters["print_step"]
    max_steps = parameters["stepMAX"]
    # Red the data
    for step in range(0, max_steps + print_step, print_step):
        # Read data
        for rank in range(rank):
            filename = "step_{}-rank{}.txt".format(step, rank)
            x1, y1, z1, c0, c1, c2, c3, c4 = np.loadtxt(
                os.path.join(path, filename), unpack=True
            )
            cc0 = np.append(cc0, c0)
            cc = np.append(cc, c1)
            x = np.append(x, x1)
            y = np.append(y, y1)
            z = np.append(z, z1)
            # Filter the number of points
            xx = x[cc0 % 10 == 0]
            yy = y[cc0 % 10 == 0]
            zz = z[cc0 % 10 == 0]
            # Create a data frame |
            data = {"x": xx, "y": yy, "z": zz}
            frame = pd.DataFrame(data=data)
        # Create a list with the frame
        list_frame.append(frame)
    return list_frame
