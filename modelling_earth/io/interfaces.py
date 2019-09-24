"""
Save interfaces and layers data to ASCII files ready to be read by MD3D
"""
import numpy as np
import os

FLAGS = {
    "viscosity_factor": "C",
    "density": "rho",
    "radiogenic_heat": "H",
    "pre-factor": "A",
    "exponential_factor": "n",
    "activation_energy": "Q",
    "activation_volume": "V",
}
FNAME = "interface_creep.txt"


def save_interfaces(interfaces, layers_parameters, path, fname=FNAME):
    """
    Save the interface and the layer parameter as ASCII file

    Parameters
    ----------
    interfaces : :class:`xarray.Dataset`
        Dataset with the interfaces depth.
    layers_parameters : dict
        Dictionary with the parameters values for each layer:
        The parameters are:
            - ``viscosity factor``
            - ``density``
            - ``radiogenic_heat``
            - ``pre-factor``
            - ``exponential_factor``
            - ``activation_energy``
            - ``activation_volume``
    path : str
        Path to save the file.

    """
    # Check that the length of each parameter in layers_parameters are the same
    size = len(layers_parameters["density"])
    for parameter in layers_parameters:
        if len(layers_parameters[parameter]) != size:
            raise ValueError(
                "Invalid number of elements layer parameters. "
                + "All layer parameters must have the same number of elements."
            )
    # Check that the length of the parameters is equal to the length of
    # interfaces plus one
    if size != len(interfaces) + 1:
        raise ValueError(
            "Invalid number of layers ({}) for given interfaces ({}). ".format(
                size, len(interfaces)
            )
            + "The number of layers must be one more than the number of interfaces."
        )
    # Generate the header with the layers parameters
    header = ""
    for i, parameter in enumerate(layers_parameters):
        if i != 0:
            header += "\n"
        header += (
            FLAGS[parameter]
            + " "
            + " ".join(list(str(i) for i in layers_parameters[parameter]))
        )
    # Stack the interfaces from the dataset
    stacked_interfaces = np.hstack(
        list(interfaces[i].values[:, np.newaxis] for i in interfaces)
    )
    # Save the interface and the layers parameters
    np.savetxt(
        os.path.join(path, fname), stacked_interfaces, header=header, comments=""
    )
