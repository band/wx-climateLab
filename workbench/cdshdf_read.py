#!/usr/bin/env python3

# setup logging
import logging, os
log_level = os.environ.get('LOGLEVEL', 'INFO').upper()

logging.basicConfig(
    level=getattr(logging, log_level, 'INFO'),
    format="%(asctime)s - %(name)s - %(levelname)s: %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger('cds_hdf')

import traceback

import h5py

def main():
    try:
        testf1='/Volumes/sandisk4TB/clima_data/62232c72/202412-C3S2-L4_GHRSST-SSTdepth-ISTskin-DMIOI-GLOB_ICDR1.0_monthly-v02.0-fv01.0.nc'

        testf2='/Volumes/sandisk4TB/clima_data/793fc0b8/202201-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_ICDR3.0-v02.0-fv01.0.nc'

        testf3='/Volumes/sandisk4TB/clima_data/999477d0/202605-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_ICDR3.0-v02.0-fv01.0.nc'

        hdft1 = h5py.File(testf1, 'r')
        logger.info(f"hdft1 keys: {hdft1.keys()}")

        hdft2 = h5py.File(testf2, 'r')
        logger.info(f"hdft2 keys: {hdft2.keys()}")

        hdft3 = h5py.File(testf3, 'r')
        logger.info(f"hdft3 keys: {hdft3.keys()}")
    except Exception as e:
        traceback.print_exc(e)
        logging.error(f"Error: {e}")

# run this script
if __name__ == "__main__":
    exit(main())




