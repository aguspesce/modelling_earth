import numpy as np
import xarray as xr
import pandas as pd
import os
             
def coordinates(path, parameter_file):
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
    coordinate : tuple of arrays (x, y, z)
        The coordenate is in km.
    
    size : tuple (nx, ny, nz) 
        Number of point in the coordenates axis.
    """
    
    with open(os.path.join(path, parameter_file), 'r') as f:
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


def time_array(path, number, step):
    time = []
    for cont in range(0, number + step, step):
        filename = 'Tempo_' + str(cont) + '.txt'
        ft = open(os.path.join(path, filename), 'r')
        tempo = float(ft.readline().split()[1])/1000000.0
        time = np.append(time, tempo)
        
    return time
    
    
def dataset_2d(path, parameter_file, step):
    """
    Generates a dataset of the output files from the md3d program for a given 
    time step.
    
    Parameters: 
    -----------
    path : str
        Path to the parameter file.
        
    parameter_file_name : str 
        Name of the parameter file. 
    
    step : 
        Time step.
        
    Returns: 
    -------
        dataset : xr.Dataset
            Dataset for a given time step.
            Data: 
                * Temperature
                * Velocity in x axis [m/s]
                * Velocity in z axis [m/s]
                * Velocity intensity [m/s]
                * Density [kg/m^3]
                * Radiogenic heat
                * Viscosity factor
                * Stain
    """
    coordinate, size = coordinates(path, parameter_file)
    coords = {'z': coordinate[2], 'x': coordinate[0]}

    # Temperature
    filename = 'Temper_{}.txt'.format(step)
    a = np.loadtxt(os.path.join(path, filename), unpack=True, 
                   comments='P', skiprows=2)
    tt = a*1.0
    tt[np.abs(tt) < 1.0E-200] = 0
    tt = np.reshape(tt, size, order='F')
    ttt = tt[:, 0, :]
    temperature = ttt.T
   
    # Velocity    
    filename = 'Veloc_fut_{}.txt'.format(step) 
    vel = np.loadtxt(os.path.join(path, filename), unpack=True,  
                     comments='P', skiprows=2)
    tt = vel*1.0
    tt[np.abs(tt) < 1.0E-200] = 0
    v_x, v_y, v_z = tt[0::3], tt[1::3], tt[2::3]
    v_x = np.reshape(v_x, size, order='F')
    v_y = np.reshape(v_y, size, order='F')
    v_z = np.reshape(v_z, size, order='F')
    
    slicey = size[1]//2
    vv_x = v_x[:, slicey, :]
    vv_y = v_y[:, slicey, :]
    vv_z = v_z[:, slicey, :]
    velocity_x = vv_x.T
    velocity_y = vv_y.T
    velocity_z = vv_z.T
    velocity = np.sqrt(velocity_x**2 + velocity_y**2 + velocity_z**2)
   
    # Density
    filename = 'Rho_{}.txt'.format(step)
    a = np.loadtxt(os.path.join(path, filename), unpack=True,
                   comments='P', skiprows=2)
    tt = a*1.0
    tt[np.abs(tt) < 1.0E-200] = 0
    tt = np.reshape(tt, size, order='F')
    ttt = tt[:, 0, :]
    density = ttt.T
  
    # Radiogenic heat
    filename = 'H_{}.txt'.format(step)
    a = np.loadtxt(os.path.join(path, filename), unpack=True, 
                   comments='P', skiprows=2)
    tt = a*1.0
    tt[np.abs(tt) < 1.0E-200] = 0
    tt = np.reshape(tt, size, order='F')
    ttt = tt[:, 0, :]
    radiogenic = ttt.T
   
    # Viscosity factor
    filename = 'Geoq_{}.txt'.format(step)
    a = np.loadtxt(os.path.join(path, filename), unpack=True, 
                   comments='P', skiprows=2)
    tt = a*1.0
    tt[np.abs(tt) < 1.0E-200] = 0
    tt = np.reshape(tt, size, order='F')
    ttt = tt[:, 0, :]
    viscosity_factor = ttt.T
   
    # Strain
    filename = 'strain_{}.txt'.format(step)
    a = np.loadtxt(os.path.join(path, filename), unpack=True,
                   comments='P', skiprows=2)
    tt = a*1.0
    tt[np.abs(tt) < 1.0E-200] = 0
    tt = np.reshape(tt, size, order='F')
    ttt = tt[:, 0, :]
    strain = ttt.T
    
    # Create the dataset
    data_vars = {'temperature': (['z', 'x'], temperature),
                 'velocity_x': (['z', 'x'], velocity_x),
                 'velocity_z': (['z', 'x'], velocity_z),
                 'velocity':(['z', 'x'], velocity),
                 'density': (["z", "x"], density), 
                 'radiogenic_heat': (['z', 'x'], radiogenic),
                 'viscosity_factor': (['z', 'x'], viscosity_factor),
                 'stain': (['z', 'x'], strain)}
   
    dataset = xr.Dataset(data_vars, coords=coords)
    
    return dataset


def lagrangian_point_2d(path, step, rank=4):
    """
    Generates a dataset of the lagrangiane particle position generated by the  
    md3d program for a given time step.
    
    Parameters: 
    -----------
    path : str
        Path to the parameter file.
        
    step : 
        Time step.
    
    rank : 
        Number of processors used in the simulation.
    
    Returns: 
    -------
        dataset : xr.Dataset
            Dataset for a given time step. It contains the position (x,y,z) of 
            each particle in km. 
    """ 
   
    x, y, z, cc, cc0 =[], [], [], [], []
    for rank in range(rank):
        filename ='step_{}-rank{}.txt'.format(step,rank)
        x1, y1, z1, c0, c1, c2, c3, c4 = np.loadtxt(os.path.join(path,
                                                                 filename), 
                                                    unpack=True)
        cc0 = np.append(cc0,c0)
        cc = np.append(cc,c1)
        x = np.append(x,x1)
        y = np.append(y,y1)
        z = np.append(z,z1)
    
    xx = x[cc0%10==0]/1000  
    yy = y[cc0%10==0]/1000    
    zz = z[cc0%10==0]/1000     
    
    point = np.linspace(0, zz.shape[0]-1,zz.shape[0])
    print(zz.shape, point.shape)
        
    # Create the dataset    
    data = {'x_position': (['point'],  xx), 'y_position': (['point'], yy),
            'z_position': (['point'], zz)}
    coords={'point': (['point'], point)}
    ds = xr.Dataset(data, coords=coords)
    
    return ds
   
