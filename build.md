# FLEXPART Build and Compile Guide

**0. System Prerequisites**
Ensure GNU Fortran compiler is installed.

```bash
sudo apt update
sudo apt install gfortran make
```

**1. Create and Activate a Virtual Environment**
Use Conda to manage the required Fortran libraries without interfering with system-wide packages.

```bash
conda create --name flexpart_env
conda activate flexpart_env
```

**2. Install Dependencies**

```bash
conda install conda-forge::eccodes
conda install conda-forge::netcdf-fortran
```

**3. Export Environment Paths**
Link the Conda environment's libraries so the compiler can find them during the build process.

```bash
export CPATH=$CONDA_PREFIX/include:$CPATH
export LIBRARY_PATH=$CONDA_PREFIX/lib:$LIBRARY_PATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
```

**4. Compile FLEXPART**
Navigate to the `src/` directory of your FLEXPART download and compile the model.

```bash
make -j -f makefile_gfortran eta=no
```

* **Use `eta=yes` (or omit the flag)** when using ECMWF data that is on native model levels (eta coordinates).
* **Use `eta=no`** when using data from other meteorological models (like NCEP GFS/FNL) that do not use eta coordinates.

This process will generate an executable named `FLEXPART` in your current directory.

## Set Up the Run Environment

**1. Configure the `pathnames` file**
Create or edit the `pathnames` file in your working directory. This file must contain exactly four lines pointing to your simulation directories. It usually looks like this:

```text
../options/
../output/
../inputs/
../AVAILABLE
```

*(Make sure these directories actually exist in your workspace. If not, create them using `mkdir options output inputs`).*

**2. Download NCEP Data**
Navigate to your inputs folder and run your data download script.

```bash
cd ~/flexpart/inputs/
chmod 755 download_ncep_fnl.csh
./download_ncep_fnl.csh
```

**3. Format Meteorological Filenames**
This is a lazy workaround. We need to rename file namings so it fits the character-limit format in `AVAILABLE`:
At this step, you shoudld be inside `~/flexpart/inputs/`

```bash
for f in gdas1.*.grib2; do
  mv "$f" "${f#gdas1.}"
done
```

## Configure Simulation Scenario

To change the parameters of your simulation, you will need to modify the files inside the `options/` directory and update your `AVAILABLE` file.

* **`options/COMMAND`**: Simulation start and end times, the output time intervals, the direction of the run (forward for dispersion, backward for receptor modeling), and turns specific physical parameterizations (like convection or deposition) on or off.
* **`options/RELEASES`**: Defines emission sources. This file dictates exactly *where* (longitude, latitude, altitude), *when* (start and end times), and *how much* mass or how many particles are released into the simulation.
* **`options/OUTGRID`**: Defines the spatial grid for the output data. It specifies the geographical domain (bounding box), the horizontal grid resolution, and the vertical height levels where concentrations or residence times will be calculated.
* **`AVAILABLE`**: A text index file that acts as a bridge between the model and your meteorological data. It lists all available weather files in your `inputs/` directory, mapping the specific dates and times of the simulation to the corresponding `.grib2` file names.

## Run the Model

Set optimal memory usage

```bash
export OMP_PLACES=cores
export OMP_PROC_BIND=true
```

```bash
./FLEXPART
```

## Plot Simulation Results

Install dependencies:

```bash
conda install conda-forge::xarray
conda install conda-forge::matplotlib
```

```bash
python plot/plot_ep.py
```
