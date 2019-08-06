import numpy as np
import xarray as xr
import pandas as pd
import os
             
def coordenates(path, parameter_file):
    """
    Funtion to create arrays with the coordenate data.
    
    Parameters:
    ----------
    path : str
        Path to the parameter file.
        
    parameter_file_name : str 
        Name of the parameter file. 
   
    Returns :
    -------
    coordinate : tuple of arrays
        The coordenate (x, y, z) is in km.
    
    size : tuple (nx, ny, nz) 
        Number of point in the coordenates axis.
    """
    
    with open(os.path.join(path_parameter, 
                           parameter_file_name), "r") as f:
        line = f.readline()
        line = line.split()
        nx, ny, nz = int(line[0]), int(line[1]), int(line[2])
        line = f.readline()
        line = line.split()
        lx, ly, lz = float(line[0]), float(line[1]), float(line[2])

    # Generate the grid in km
    x = np.linspace(0, lx/1000, nx);
    y = np.linspace(-ly/1000, 0, ny);
    z = np.linspace(-lz/1000, 0, nz);
    size = (nx, ny, nz)
    coordenate = (x, y, z)
    
    return coordenate, size

