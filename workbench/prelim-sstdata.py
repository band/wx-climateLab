#!/usr/bin/env python3

import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from datetime import date, datetime, timedelta
import json
import traceback
import urllib.request

def daynum_to_date(year: int, daynum: int):
    d = datetime(year, 1, 1) + timedelta(daynum -1)
    return d.date()

URL = (
"https://climatereanalyzer.org/clim/sst_daily/json_2clim/"
"oisst2.1_nino3.4_sst_day.json"
)
UA = "Mozilla/5.0 (compatible; wx-climateLab/1.0)"

def main():
    try:
        req = urllib.request.Request(URL, headers={"User-Agent":UA})
        resp=urllib.request.urlopen(req,timeout=60)
        raw=resp.read().decode("utf-8")
        doc=json.loads(raw)
    except Exception as e:
        traceback.print_exc(e)
        logging.error(f"Error: {e}")
        
    predata=[l.get('data') for l in doc if l.get('name') == 'Preliminary'][0]
    first_idx = next((i for i, v in enumerate(predata) if v is not None), None)
    last_idx = next((i for i in range(len(predata) - 1, -1, -1) if predata[i] is not None), None)
#    print(first_idx, last_idx)

    data26=[l.get('data') for l in doc if l.get('name') == '2026'][0]
    climatology=[l.get('data') for l in doc if l.get('name') == '1991-2020'][0]

    print(f"NOAA OISST v2.1 Niño 3.4 preliminary SST data:\n")
    print(f"Latest date        :  {daynum_to_date(2026, last_idx)}")
    print(f"latest SST         :  {predata[last_idx]} degC")
    print(f"climatology        :  {climatology[last_idx]}")
    print(f"anomaly            :  {predata[last_idx] - climatology[last_idx]}")

if __name__ == "__main__":
    exit(main())

