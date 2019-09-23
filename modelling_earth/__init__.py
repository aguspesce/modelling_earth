# pylint: disable=missing-docstring
# Import functions/classes to make the public API
from ._version import get_versions
from .coordinates import grid_coordinates, initialize_array
from .temperature import subducting_slab_temperature, litho_astheno_temperatures
from .io.grids import read_md3d_data
from .io.swarm import read_md3d_swarm
from .io.temperature import save_temperature
from .plot import plot_velocity_2d, plot_scalar_2d, save_plots_2d, plot_swarm_2d
from .interfaces import interfaces

# Get the version number through versioneer
__version__ = get_versions()["version"]
del get_versions
