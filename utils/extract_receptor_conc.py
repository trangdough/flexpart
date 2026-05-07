#!/usr/bin/env python3
"""
Extract hourly receptor concentrations from all FLEXPART simulation dates
in /scratch/scholar/do47/flexpart/output/2017v4/<SITE_CODE>/ and write to a
single CSV.

New-run layout (v4):
    /scratch/scholar/do47/flexpart/output/2017v4/<SITE_CODE>/YYYYMMDD/receptor_conc.nc
Old-run layout (v3, for reference):
    /scratch/scholar/do47/flexpart/output/2017v3/YYYYMMDD/receptor_conc_YYYYMMDD000000.nc

Output columns:
    simulation_date  – the date folder (YYYYMMDD)
    datetime         – full timestamp of each hourly output
    concentration    – Vinyl Chloride concentration at the receptor (ng/m3)
    uncertainty      – receptor concentration uncertainty (ng/m3)
    npart            – number of particles contributing to the receptor estimate
    kernel           – average kernel weight at the receptor

Usage:
    python extract_receptor_conc.py [--site-code CODE] [--base-dir PATH]

    If --base-dir is omitted, it defaults to
    /scratch/scholar/do47/flexpart/output/2017v6/<site-code>/
"""

import argparse
import os
from datetime import datetime, timedelta

import netCDF4 as nc
import numpy.ma as ma
import csv

DEFAULT_SITE_CODE = "70805FRMSPGULFS"
DEFAULT_OUTPUT_ROOT = "/scratch/scholar/do47/flexpart/output/2017v6"
DEFAULT_BASE_DIR = os.path.join(DEFAULT_OUTPUT_ROOT, DEFAULT_SITE_CODE, "")

SPECIES_VAR = "Vinyl Chlo"


def main():
    parser = argparse.ArgumentParser(
        description="Extract hourly receptor concentrations from FLEXPART receptor_conc.nc files."
    )
    parser.add_argument(
        "--site-code",
        default=DEFAULT_SITE_CODE,
        help=f"Facility site code (default: {DEFAULT_SITE_CODE}).",
    )
    parser.add_argument(
        "--base-dir",
        default=None,
        metavar="PATH",
        help=(
            "Directory containing YYYYMMDD simulation folders. "
            f"If omitted, uses {DEFAULT_BASE_DIR!r} with <site-code> substituted."
        ),
    )
    args = parser.parse_args()

    base_dir = args.base_dir or os.path.join(DEFAULT_OUTPUT_ROOT, args.site_code, "")
    base_dir = os.path.abspath(os.path.expanduser(base_dir))
    if not base_dir.endswith(os.sep):
        base_dir += os.sep

    output_csv = os.path.join(
        base_dir, f"receptor_conc_2017_{args.site_code}.csv"
    )

    date_dirs = sorted(
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and d.isdigit() and len(d) == 8
    )

    rows = []

    for sim_date in date_dirs:
        nc_path = os.path.join(base_dir, sim_date, f"receptor_conc_{sim_date}000000.nc")
        if not os.path.exists(nc_path):
            print(f"WARNING: missing {nc_path}, skipping")
            continue

        ds = nc.Dataset(nc_path, "r")

        time_var = ds.variables["time"]
        time_seconds = time_var[:]
        base_dt = datetime.strptime(sim_date, "%Y%m%d")

        conc = ds.variables[SPECIES_VAR][:]
        uncert = ds.variables[f"{SPECIES_VAR}_uncert"][:]
        npart = ds.variables["npart"][:]
        kernel = ds.variables["kernel"][:]

        for i in range(len(time_seconds)):
            if ma.is_masked(time_seconds[i]):
                continue
            dt = base_dt + timedelta(seconds=int(time_seconds[i]))
            rows.append({
                "simulation_date": sim_date,
                "datetime": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "concentration_ng_m3": f"{conc[i]:.6f}",
                "uncertainty_ng_m3": f"{uncert[i]:.6f}",
                "npart": f"{npart[i]:.1f}",
                "kernel": f"{kernel[i]:.3f}",
            })

        ds.close()
        print(f"Processed {sim_date}: {len(time_seconds)} hourly records")

    fieldnames = [
        "simulation_date",
        "datetime",
        "concentration_ng_m3",
        "uncertainty_ng_m3",
        "npart",
        "kernel",
    ]

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. Wrote {len(rows)} rows to {output_csv}")


if __name__ == "__main__":
    main()
