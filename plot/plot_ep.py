import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cf
import numpy as np
import os
from matplotlib.colors import LogNorm
import imageio.v2 as imageio

# =========================
# User settings
# =========================
file_path = "/home/do47/eco/flexpart/output/grid_conc_20230203000000.nc"
output_dir = "/home/do47/eco/flexpart/output/figures"
os.makedirs(output_dir, exist_ok=True)

# Release location (East Palestine OH)
release_lon = -80.5227
release_lat = 40.8360

height_idx = 0

fixed_extent = [-84.5, -77.0, 38.5, 43.5]  # [min_lon, max_lon, min_lat, max_lat]

cmap = plt.cm.Blues

# Log scaling
vmin = 1e-6

# If True, compute a fixed extent from the plume over all times (instead of using fixed_extent)
auto_extent = True
extent_threshold = 1e-5  # used only if auto_extent=True (to avoid one-cell noise)

# =========================
# Load data
# =========================
print(f"Opening {file_path}")
ds = xr.open_dataset(file_path)

# Coordinates
lon = ds["longitude"].values
lat = ds["latitude"].values

# Concentration field (units in your file: ng m-3)
data_var = ds["spec001_mr"]

# Time steps
time_steps = ds["time"].values
num_times = len(time_steps)
t0 = time_steps[0]

# Global vmax for consistent coloring across frames
global_max = float(
    data_var.isel(nageclass=0, pointspec=0, height=height_idx).max().values
)
vmax = max(global_max, vmin * 10)

levels = np.logspace(np.log10(vmin), np.log10(vmax), 50)

# Frame extent
if auto_extent:
    field_all = data_var.isel(nageclass=0, pointspec=0, height=height_idx)  # time, lat, lon
    mask = field_all > extent_threshold

    if bool(mask.any()):
        mask_any = mask.any(dim="time")
        lat_idx, lon_idx = np.where(mask_any.values)

        min_lat = float(lat[lat_idx.min()])
        max_lat = float(lat[lat_idx.max()])
        min_lon = float(lon[lon_idx.min()])
        max_lon = float(lon[lon_idx.max()])
    else:
        min_lon, max_lon = release_lon - 2, release_lon + 2
        min_lat, max_lat = release_lat - 2, release_lat + 2

    min_lon = min(min_lon, release_lon)
    max_lon = max(max_lon, release_lon)
    min_lat = min(min_lat, release_lat)
    max_lat = max(max_lat, release_lat)

    pad_lon, pad_lat = 1.0, 1.0
    fixed_extent = [min_lon - pad_lon, max_lon + pad_lon, min_lat - pad_lat, max_lat + pad_lat]
    print("Auto fixed extent:", fixed_extent)
else:
    print("Using fixed extent:", fixed_extent)

# =========================
# Plot frames
# =========================
frame_files = []

for t_idx in range(num_times):
    print(f"Processing time step {t_idx+1}/{num_times}")

    data = (
        data_var
        .isel(nageclass=0, pointspec=0, time=t_idx, height=height_idx)
        .values
    )
    data_plot = np.where(data > vmin, data, np.nan)
    fig = plt.figure(figsize=(12, 9))
    
    ax = plt.subplot(111, projection=ccrs.PlateCarree())
    ax.add_feature(cf.COASTLINE, linewidth=0.8)
    ax.add_feature(cf.BORDERS, linewidth=0.6)
    ax.add_feature(cf.STATES, linewidth=0.7, linestyle=':')
    ax.set_extent(fixed_extent, crs=ccrs.PlateCarree())

    # Plot concentration
    if not np.all(np.isnan(data_plot)):
        lonnew, latnew = np.meshgrid(lon, lat)

        cbt = ax.contourf(
            lonnew, latnew, data_plot,
            cmap=cmap,
            levels=levels,
            norm=LogNorm(vmin=vmin, vmax=vmax),
            extend="max",
            transform=ccrs.PlateCarree(),
            zorder=0
        )

        # show under-range as white (and NaNs are transparent)
        cbt.cmap.set_under("white")

        cb = plt.colorbar(cbt, orientation="vertical", fraction=0.046, pad=0.04, shrink=0.75)
        cb.set_label("Concentration (ng m$^{-3}$)", fontsize=12)
        cb.ax.tick_params(labelsize=12)

    # Mark release site location
    ax.scatter(
        release_lon, release_lat,
        facecolor="red", edgecolor="white",
        marker="*", s=260, linewidth=1.6,
        label="Release Site",
        transform=ccrs.PlateCarree(),
        zorder=10
    )

    ax.legend(loc="lower right", fontsize=12)

    # Timestamp in title
    hours_since_first_output = (time_steps[t_idx] - t0) / np.timedelta64(1, "h")
    ax.set_title(
        "FLEXPART Simulation: East Palestine OH\n"
        f"Valid: {np.datetime_as_string(time_steps[t_idx], unit='h')} "
        f"({hours_since_first_output:.0f} hours since first output)\n"
        f"Layer top: {float(ds['height'].values[height_idx]):.0f} m",
        fontsize=14
    )

    # Save frame
    frame_path = os.path.join(output_dir, f"ep_concentration_map_{t_idx:02d}h.png")
    plt.tight_layout()
    plt.savefig(frame_path, dpi=150)
    plt.close(fig)
    frame_files.append(frame_path)

print("Finished generating frames.")

# =========================
# Make GIF
# =========================

make_gif = True
gif_name = "ep_concentration.gif"
fps = 1  # GIF speed

if make_gif:
    gif_path = os.path.join(output_dir, gif_name)
    duration = 5 / fps

    with imageio.get_writer(gif_path, mode="I", duration=duration, loop=0) as writer:
        for f in frame_files:
            writer.append_data(imageio.imread(f))

    print(f"GIF saved to: {gif_path}")