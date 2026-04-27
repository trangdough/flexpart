import argparse
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cf
import numpy as np
import os
from matplotlib.colors import LogNorm
import imageio.v2 as imageio
import matplotlib.ticker as ticker

def main():
    # =========================
    # Argument Parsing
    # =========================
    parser = argparse.ArgumentParser(description="Plot FLEXPART dispersion frames based on OUTGRID configurations.")
    
    # File and Directory arguments
    # Replace --dir-path with your own working directory
    parser.add_argument("--dir-path", default="/scratch/scholar/do47/flexpart/output/2017v5", type=str, help="Path to the grid_conc NetCDF mother directory.")
    # Replace --site-code with your working TRI release site
    parser.add_argument("--site-code", default="70805FRMSPGULFS", type=str, help="Site code of the facility for the plot title.")
    parser.add_argument("--release-date", required=True, type=str, help="Date of the release.")
    
    # Grid and Location arguments
    # Replace below release information with your OUTGRID configurations
    parser.add_argument("--release-lon", default=-91.185503, type=float, help="Longitude of the release site.")
    parser.add_argument("--release-lat", default=30.498083, type=float, help="Latitude of the release site.")
    parser.add_argument("--dxout", default=0.05, type=float, help="Grid distance in X direction (degrees).")
    parser.add_argument("--dyout", default=0.05, type=float, help="Grid distance in Y direction (degrees).")
    parser.add_argument("--numxgrid", default=201, type=int, help="Number of grid points in X direction.")
    parser.add_argument("--numygrid", default=201, type=int, help="Number of grid points in Y direction.")
    
    args = parser.parse_args()

    # =========================
    # Calculate Canvas Extent
    # =========================
    # Total width/height of the grid in degrees
    lon_span = (args.numxgrid - 1) * args.dxout
    lat_span = (args.numygrid - 1) * args.dyout

    # Calculate bounding box assuming the release site is the dead-center of the OUTGRID
    min_lon = args.release_lon - (lon_span / 2.0)
    max_lon = args.release_lon + (lon_span / 2.0)
    min_lat = args.release_lat - (lat_span / 2.0)
    max_lat = args.release_lat + (lat_span / 2.0)

    fixed_extent = [min_lon, max_lon, min_lat, max_lat]
    print(f"Calculated Canvas Extent based on OUTGRID math: {fixed_extent}")

    # =========================
    # User settings (Visuals)
    # =========================
    cmap = plt.cm.viridis_r
    vmin = 1e-6

    # =========================
    # Load data
    # =========================
    file_path = os.path.join(args.dir_path, args.site_code, args.release_date)

    conc_file_path = os.path.join(file_path, f"grid_conc_{args.release_date}000000.nc")
    print(f"Opening {conc_file_path}")
    ds = xr.open_dataset(conc_file_path)

    # Coordinates
    lon = ds["longitude"].values
    lat = ds["latitude"].values
    heights = ds["height"].values
    num_heights = len(heights)

    # Concentration field
    data_var = ds["spec001_mr"]

    # Time steps
    time_steps = ds["time"].values
    num_times = len(time_steps)
    t0 = time_steps[0]

    # Global vmax for consistent coloring across ALL frames and ALL heights
    global_max = float(
        data_var.isel(nageclass=0).sum(dim="pointspec").max().values
    )
    vmax = max(global_max, vmin * 10)

    levels = np.logspace(np.log10(vmin), np.log10(vmax), 50)

    # =========================
    # Plot frames
    # =========================
    frame_files = []
    lonnew, latnew = np.meshgrid(lon, lat)

    for t_idx in range(num_times):
        print(f"Processing time step {t_idx+1}/{num_times}")

        # Set up a figure with 1 row and `num_heights` columns
        fig, axes = plt.subplots(
            1, num_heights, 
            figsize=(6 * num_heights, 6), 
            subplot_kw={'projection': ccrs.PlateCarree()}
        )
        
        # Ensure axes is iterable even if there's only 1 height somehow
        if num_heights == 1:
            axes = [axes]

        for h_idx in range(num_heights):
            ax = axes[h_idx]
            height_val = float(heights[h_idx])
            
            data = (
                data_var
                .isel(nageclass=0, time=t_idx, height=h_idx)
                .sum(dim="pointspec")
                .values
            )
            data_plot = np.where(data > vmin, data, np.nan)
            
            ax.add_feature(cf.COASTLINE, linewidth=0.8)
            ax.add_feature(cf.BORDERS, linewidth=0.6)
            ax.add_feature(cf.STATES, linewidth=0.7, linestyle=':')
            ax.set_extent(fixed_extent, crs=ccrs.PlateCarree())

            # Plot concentration
            if not np.all(np.isnan(data_plot)):
                c = ax.contourf(
                    lonnew, latnew, data_plot,
                    cmap=cmap,
                    levels=levels,
                    norm=LogNorm(vmin=vmin, vmax=vmax),
                    extend="max",
                    transform=ccrs.PlateCarree(),
                    zorder=0
                )
                # show under-range as white (and NaNs are transparent)
                c.cmap.set_under("white")

            # Mark release site location
            ax.scatter(
                args.release_lon, args.release_lat,
                facecolor="red", edgecolor="white",
                marker="*", s=260, linewidth=1.6,
                label="Release Site",
                transform=ccrs.PlateCarree(),
                zorder=10
            )
            
            ax.set_title(f"Layer top: {height_val:.0f} m", fontsize=13)

            if h_idx == 0:
                ax.legend(loc="lower left", fontsize=10)

        # Add a unified, locked colorbar spanning all subplots
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=LogNorm(vmin=vmin, vmax=vmax))
        sm.set_array([]) 
        
        cb = fig.colorbar(
            sm, ax=axes, orientation="horizontal", 
            fraction=0.05, pad=0.08, aspect=50,
            extend="max"
        )
        
        # Explicitly set the locator and formatter for the log scale to clear up the labels
        cb.locator = ticker.LogLocator(base=10.0, subs=(1.0,), numticks=10)
        cb.formatter = ticker.LogFormatterMathtext()
        cb.update_ticks()
        
        cb.set_label("Concentration (ng m$^{-3}$)", fontsize=12)
        cb.ax.tick_params(labelsize=11)

        # Super title for the whole figure
        hours_since_first_output = (time_steps[t_idx] - t0) / np.timedelta64(1, "h")
        fig.suptitle(
            f"{args.site_code}\n"
            f"Valid: {np.datetime_as_string(time_steps[t_idx], unit='h')} "
            f"({hours_since_first_output:.0f} hours since first output)",
            fontsize=15, y=1.02
        )

        # Save frame (Replaced spaces with underscores for safer file management)
        output_path = os.path.join(file_path, "results")
        os.makedirs(output_path, exist_ok=True)
        frame_path = os.path.join(output_path, f"{args.site_code}_{args.release_date}_{t_idx:02d}h.png")
        
        # Use bbox_inches to ensure the title and colorbar aren't cut off
        plt.savefig(frame_path, dpi=200, bbox_inches='tight')
        plt.close(fig)
        frame_files.append(frame_path)

    print("Finished generating frames.")

if __name__ == "__main__":
    main()
