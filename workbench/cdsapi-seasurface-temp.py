#!/usr/bin/env python3
"""Download ESA CCI OSTIA SST monthly files straight to the external disk.

Usage:
    ./cdsapi-seasurface-temp.py            # fetch the month after the newest on disk
    ./cdsapi-seasurface-temp.py 2026 06    # fetch a specific YEAR MONTH
    ./cdsapi-seasurface-temp.py --triad    # ensure the 3 comparison months exist:
                                           #   newest on disk, one year prior, ten
                                           #   years prior (downloads only the gaps)

Pulls one monthly file (~60 MB) rather than whole years, downloads the CDS zip
into DATA_DIR on the external disk, extracts the .nc alongside the existing
data (where ssthdf.py reads it), and removes the zip. Requires ~/.cdsapirc.

The --triad mode mirrors the three rows ssthdf.py prints, so running it then
ssthdf.py gives a complete latest / -1yr / -10yr readout.
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


def fetch_month(client, year, month):
    """Download and extract one month if it isn't already on disk.

    Returns 0 on success / already-present / not-yet-published (all benign),
    1 only when a download arrived but contained no .nc file.
    """
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
    try:
        client.retrieve(DATASET, request, zip_path)
    except requests.exceptions.HTTPError as exc:
        # CDS returns 400 "invalid combination" when a month isn't in the
        # catalog (not published yet, or before the record starts). That's the
        # normal "no data" case, not an error.
        status = getattr(exc.response, 'status_code', None)
        if status == 400:
            print(f'{year}-{month:02d} is not available on CDS; '
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


def triad_months(data_dir):
    """The (year, month) triad ssthdf.py reports: newest, -1yr, -10yr."""
    latest = latest_on_disk(data_dir)
    if latest is None:
        return None
    year, month = latest
    return [(year, month), (year - 1, month), (year - 10, month)]


def main():
    if len(sys.argv) == 2 and sys.argv[1] == '--triad':
        triad = triad_months(DATA_DIR)
        if triad is None:
            print('No data on disk; specify YEAR MONTH explicitly.',
                  file=sys.stderr)
            return 1
        client = cdsapi.Client()
        rc = 0
        for year, month in triad:
            rc |= fetch_month(client, year, month)
        return rc

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

    return fetch_month(cdsapi.Client(), year, month)


if __name__ == '__main__':
    sys.exit(main())
