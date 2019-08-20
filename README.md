# Modelling Earth

[![Travis CI](http://img.shields.io/travis/aguspesce/modelling_earth/master.svg?style=flat-square&label=TravisCI)](https://travis-ci.org/aguspesce/modelling_earth)

Tools for building Earth models for geodynamics modelling.


## How to install

First clone the repository and navigate through the newly created directory.

### Dependencies

The package needs the following dependencies to run:

- numpy
- scipy
- xarray
- pandas

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

We can install the package through pip by using the `Makefile`:

```
make install
```
