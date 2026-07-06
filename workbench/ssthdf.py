#!/usr/bin/env python3
"""Global-mean sea surface temperature from ESA CCI GHRSST OSTIA monthly files.

Reads the `analysed_sst` field (kelvin, 0.05 deg global grid), masks land/ice
fill values, converts to Celsius, and reduces it to a single area-weighted
global-mean value (weighting each grid cell by cos(latitude), since cells shrink
toward the poles). Prints the latest month and the same month one year earlier,
in the style of the NOAA CO2 trend readout.
"""

import glob
import os
import sys

import h5py
import numpy as np

# ESA CCI OSTIA v3.0 (ICDR) monthly product. Same product across years so the
# comparison is apples-to-apples (do not mix in the C3S2 DMIOI product).
DATA_DIR = '/Volumes/sandisk4TB/clima_data/793fc0b8'
KELVIN = 273.15


def find_file(data_dir, year, month):
    """Return the .nc path for a given year/month, or None if absent."""
    hits = glob.glob(os.path.join(data_dir, f'{year}{month:02d}-*.nc'))
    return hits[0] if hits else None


def global_mean_sst_celsius(path):
    """Area-weighted global-mean analysed_sst for one monthly file, in Celsius."""
    with h5py.File(path, 'r') as f:
        sst = f['analysed_sst'][0]                 # (lat, lon), kelvin, float32
        fill = f['analysed_sst'].attrs['_FillValue'][0]
        lat = f['lat'][:]

    # Mask land/ice fill and anything outside physical SST bounds (kelvin).
    valid = (sst != fill) & np.isfinite(sst) & (sst > 200.0) & (sst < 350.0)

    # cos(lat) area weights, broadcast across longitude, zeroed on masked cells.
    w = np.cos(np.radians(lat))[:, None]
    weights = np.where(valid, w, 0.0)

    mean_kelvin = np.sum(sst * weights) / np.sum(weights)
    return mean_kelvin - KELVIN


def latest_year_month(data_dir):
    """Most recent (year, month) present in the product directory."""
    stamps = []
    for p in glob.glob(os.path.join(data_dir, '*.nc')):
        name = os.path.basename(p)
        if len(name) >= 6 and name[:6].isdigit():
            stamps.append((int(name[:4]), int(name[4:6])))
    return max(stamps) if stamps else None


def report(label, year, month, path):
    if path is None:
        print(f'{label} ({year}-{month:02d}) global-mean SST: '
              f'(no data file on disk)')
        return
    value = global_mean_sst_celsius(path)
    print(f'{label} ({year}-{month:02d}) global-mean SST (ESA CCI OSTIA): '
          f'{value:7.2f} \N{DEGREE SIGN}C')


def main():
    latest = latest_year_month(DATA_DIR)
    if latest is None:
        print(f'No data files found in {DATA_DIR}', file=sys.stderr)
        return 1
    year, month = latest

    report('Latest       ', year, month, find_file(DATA_DIR, year, month))
    report('One year ago ', year - 1, month, find_file(DATA_DIR, year - 1, month))
    report('Ten years ago', year - 10, month, find_file(DATA_DIR, year - 10, month))
    return 0


if __name__ == '__main__':
    sys.exit(main())
