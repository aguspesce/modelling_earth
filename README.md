# Modelling Earth

Tools for building Earth models for geodynamics modelling.


## How to install

First clone the repository and navigate through the newly created directory.

### Dependencies

The package needs the following dependencies to run:

- numpy
- scipy
- xarray

Besides, some examples need `matplotlib` to be installed.

If you have an Anaconda Python distribution, you could install all the dependencies
through the `conda` package manager:

```
conda env create -f environment.yml
```

And then activate the environment:

```
conda activate modelling_earth
```

### Installing

We can install the package through pip:

```
pip install .
```

If you are a developer and want to modify the code, we recommend you to install it on
developer mode:

```
pip install -e .
```
