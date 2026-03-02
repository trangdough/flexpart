# FLEXPART Simulation Run Guide

## Build and compile

0. Install `gfortran` if not already installed

```bash
sudo apt install gfortran
```

1. Create a virtual environment

```bash
conda create --name myenv
```

2. Install ecCodes and netCDF

```bash
conda install conda-forge::eccodes
conda install conda-forge::netcdf-fortran
```

3. Export paths

```bash
export CPATH=$CONDA_PREFIX/include:$CPATH
export LIBRARY_PATH=$CONDA_PREFIX/lib:$LIBRARY_PATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
```

4. Compile FLEXPART

```bash
make -j -f makefile_gfortran eta=no
```

Use `eta=yes` when using ECMWF data that is on native model levels (eta coordinates).
Use `eta=no` when using data from other meteorological models like NCEP with no eta coords.

5. Run the executable

```bash
./FLEXPART
```

## Set up to run

1. `pathnames`