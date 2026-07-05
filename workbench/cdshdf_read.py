#!/usr/bin/env python3

import h5py

testf1='/Volumes/sandisk4TB/clima_data/202412-C3S2-L4_GHRSST-SSTdepth-ISTskin-DMIOI-GLOB_ICDR1.0_monthly-v02.0-fv01.0.nc'

hdft1 = h5py.File(testf1, 'r')

print("the keys: ", hdft1.keys())



