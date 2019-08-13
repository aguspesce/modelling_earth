# pylint: disable=missing-docstring
# Import functions/classes to make the public API
from ._version import get_versions
from .temperature import (
    add_subducting_slab, empty_temperature_grid, litho_astheno_temperatures,
)
from .io import read_md3d_data
from .swarms import swarm_read

# Get the version number through versioneer
__version__ = get_versions()['version']
del get_versions
