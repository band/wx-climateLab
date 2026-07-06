#!/usr/bin/env python3
"""Download a SINGLE month of ESA CCI OSTIA SST straight to the external disk.

Usage:
    ./cdsapi-seasurface-temp.py            # fetch the month after the newest on disk
    ./cdsapi-seasurface-temp.py 2026 06    # fetch a specific YEAR MONTH

Pulls one monthly file (~60 MB) rather than whole years, downloads the CDS zip
into DATA_DIR on the external disk, extracts the .nc alongside the existing
data (where ssthdf.py reads it), and removes the zip. Requires ~/.cdsapirc.
"""

import glob
import os
import sys
import zipfile

import cdsapi
import requests

# Same OSTIA product directory ssthdf.py reads from; new months extend it.
DATA_DIR = '/Volumes/sandisk4TB/clima_data/793fc0b8'
DATASET = 'satellite-sea-surface-temperature'


def latest_on_disk(data_dir):
    """Most recent (year, month) already present, or None."""
    stamps = []
    for p in glob.glob(os.path.join(data_dir, '*.nc')):
        name = os.path.basename(p)
        if len(name) >= 6 and name[:6].isdigit():
            stamps.append((int(name[:4]), int(name[4:6])))
    return max(stamps) if stamps else None


def next_month(year, month):
    return (year + 1, 1) if month == 12 else (year, month + 1)


def main():
    if len(sys.argv) == 3:
        year, month = int(sys.argv[1]), int(sys.argv[2])
    else:
        latest = latest_on_disk(DATA_DIR)
        if latest is None:
            print('No data on disk; specify YEAR MONTH explicitly.',
                  file=sys.stderr)
            return 1
        year, month = next_month(*latest)
        print(f'Newest on disk is {latest[0]}-{latest[1]:02d}; '
              f'fetching {year}-{month:02d}.')

    if glob.glob(os.path.join(DATA_DIR, f'{year}{month:02d}-*.nc')):
        print(f'{year}-{month:02d} already present in {DATA_DIR}; nothing to do.')
        return 0

    request = {
        'variable': 'all',
        'processinglevel': 'level_4',
        'sensor_on_satellite': 'combined_product',
        'version': '3_0',
        'temporal_resolution': 'monthly',
        'year': [str(year)],
        'month': [f'{month:02d}'],
        'data_format': 'zip',
        'download_format': 'archived',
    }

    zip_path = os.path.join(DATA_DIR, f'{year}{month:02d}-download.zip')
    print(f'Requesting {year}-{month:02d} from CDS -> {zip_path}')
    client = cdsapi.Client()
    try:
        client.retrieve(DATASET, request, zip_path)
    except requests.exceptions.HTTPError as exc:
        # CDS returns 400 "invalid combination" when a month isn't published
        # yet. That's the normal "no new data" case, not an error.
        status = getattr(exc.response, 'status_code', None)
        if status == 400:
            print(f'{year}-{month:02d} is not published on CDS yet; '
                  f'nothing to download.')
            return 0
        raise

    extracted = []
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            if name.endswith('.nc'):
                z.extract(name, DATA_DIR)
                extracted.append(name)
    os.remove(zip_path)

    if not extracted:
        print('Warning: no .nc file found in the downloaded archive.',
              file=sys.stderr)
        return 1
    for name in extracted:
        print(f'Extracted {name} to {DATA_DIR}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
