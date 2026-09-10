#!/usr/bin/env python3
"""Retrieve the Climate Reanalyzer OISST v2.1 Niño 3.4 daily SST series.

Pulls the JSON feed and pulls out two series for comparison:

    current  — the "2026" series (this year to date)
    clim     — the "1991-2020" series (30-year daily climatology)

Note on the User-Agent: climatereanalyzer.org returns 403 to any request whose
UA contains "curl" or "wget". urllib's default ("Python-urllib/3.x") is fine,
but we send an explicit descriptive one anyway.
"""

import json
import urllib.request

URL = (
    "https://climatereanalyzer.org/clim/sst_daily/json_2clim/"
    "oisst2.1_nino3.4_sst_day.json"
)
UA = "Mozilla/5.0 (compatible; wx-climateLab/1.0)"

CURRENT_NAME = "2026"
CLIM_NAME = "1991-2020"


def fetch(url=URL, cache=None):
    """Return the parsed JSON list. If cache is a path, read/write it."""
    if cache:
        try:
            with open(cache) as fh:
                return json.load(fh)
        except FileNotFoundError:
            pass

    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")

    if cache:
        with open(cache, "w") as fh:
            fh.write(raw)

    return json.loads(raw)


def series(doc, name):
    """Return the last data_source named `name`.

    The feed has one entry per name today, but it is ordered, so taking the
    last match is the stable choice if a name is ever repeated.
    """
    matches = [d for d in doc if d.get("name") == name]
    if not matches:
        have = ", ".join(repr(d.get("name")) for d in doc)
        raise KeyError(f"no data_source named {name!r}; found: {have}")
    return matches[-1]


def load(cache=None):
    """Fetch and return (current, clim) — the two data_source dicts."""
    doc = fetch(cache=cache)
    return series(doc, CURRENT_NAME), series(doc, CLIM_NAME)


if __name__ == "__main__":
    current, clim = load()

    cur_vals = current["data"]
    clim_vals = clim["data"]

    # Values are day-of-year indexed into a 366-slot array. Trailing Nones in
    # the current year mark days not yet reported.
    observed = [v for v in cur_vals if v is not None]
    n = len(observed)

    print(f"current : {current['name']:>10}  {n:>3} days   source={current['data_source']}")
    print(f"clim    : {clim['name']:>10}  {len(clim_vals):>3} days   source={clim['data_source']}")
    print()
    print(f"latest day-of-year : {n}")
    print(f"latest SST         : {observed[-1]:.3f} degC")
    print(f"climatology        : {clim_vals[n - 1]:.3f} degC")
    print(f"anomaly            : {observed[-1] - clim_vals[n - 1]:+.3f} degC")
