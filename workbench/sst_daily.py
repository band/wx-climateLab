#!/usr/bin/env python3
"""Climate Reanalyzer OISST v2.1 daily sea-surface-temperature series.

Replaces nino34.py and world2.py: one reader, `--region` picks the box.

    ./sst_daily.py                      # Niño 3.4, live feed
    ./sst_daily.py --region world2      # 60S-60N world ocean
    ./sst_daily.py --list               # what regions exist, on which feed

Two feeds carry these series, and they are NOT the same document:

    current  /clim/sst_daily/json_2clim/...   live; what the site itself plots
    legacy   /clim/sst_daily/json/...         frozen upstream on 2024-09-22

They differ in schema, not just in vintage:

                      current                     legacy
    data_source key   present                     absent
    years             1981-present + Preliminary  1981-2024
    climatology       "1982-2010", "1991-2020"    "1982-2011 mean"
    2-sigma bands     absent                      "plus 2σ", "minus 2σ"
    region ids        natlan                      natlan1

Preliminary is off by default. On the current feed the calendar-year series
stops a couple of weeks back and the most recent days live in a separate
series named "Preliminary" -- disjoint from the year series, continuing at the
next day-of-year. Those provisional values get revised, and a provisional
record reads the same as a real one in a headline, so we report the last FINAL
day and merely note how many preliminary days are on offer. --preliminary
splices them in and labels every provisional day as such.

Note on the User-Agent: climatereanalyzer.org returns 403 to any request whose
UA contains "curl" or "wget". urllib's default ("Python-urllib/3.x") is fine,
but we send an explicit descriptive one anyway.

Note on 404s: the site answers a missing file with an HTML page under HTTP
200, so a bad region would surface as a baffling JSONDecodeError. We check the
payload actually looks like JSON and say something useful instead.
"""

import argparse
import datetime
import json
import urllib.request

BASE = "https://climatereanalyzer.org/clim/sst_daily"
FEEDS = {"current": "json_2clim", "legacy": "json"}
UA = "Mozilla/5.0 (compatible; wx-climateLab/1.0)"

# Transcribed from the site's own dm_meta registry (js/sst_daily.min.js), then
# each entry probed against both feeds. `legacy` is the id that feed uses for
# the same box, or None where the frozen feed never carried it.
REGIONS = {
    "world2":  {"label": "World (60°S–60°N, 0–360°E)",              "legacy": "world2"},
    "natlan":  {"label": "North Atlantic (0–60°N, 0–80°W)",         "legacy": "natlan1"},
    "natlsp":  {"label": "Subpolar North Atlantic (45–60°N, 20–45°W)", "legacy": None},
    "atlhmdr": {"label": "Atlantic Hurricane MDR (10–20°N, 20–85°W)",  "legacy": None},
    "gom":     {"label": "Gulf of Maine (42–45°N, 66–71°W)",        "legacy": "gom"},
    "gomex":   {"label": "Gulf of Mexico (20–30°N, 82–98°W)",       "legacy": None},
    "nino3.4": {"label": "Niño 3.4 (5°S–5°N, 120–170°W)",           "legacy": None},
}

# Climatology series names in preference order. The feeds spell theirs
# differently and neither offers all of these.
CLIM_NAMES = ("1991-2020", "1982-2011 mean", "1982-2010")

PLUS_2S, MINUS_2S = "plus 2σ", "minus 2σ"
PRELIM = "Preliminary"
DAYS = 366


def url_for(region, feed):
    """Build the feed URL, or explain why this pairing does not exist."""
    if region not in REGIONS:
        raise SystemExit(f"unknown region {region!r}; try --list")
    rid = region if feed == "current" else REGIONS[region]["legacy"]
    if rid is None:
        have = ", ".join(r for r, m in REGIONS.items() if m["legacy"])
        raise SystemExit(
            f"region {region!r} is not on the legacy feed (it carries only: {have})"
        )
    return f"{BASE}/{FEEDS[feed]}/oisst2.1_{rid}_sst_day.json"


def fetch(url, cache=None):
    """Return the parsed JSON list. If cache is a path, read/write it."""
    if cache:
        try:
            with open(cache) as fh:
                return json.load(fh)
        except FileNotFoundError:
            pass

    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")

    if not raw.lstrip().startswith("["):
        raise SystemExit(f"{url}\n  did not return JSON -- the region is probably wrong")

    if cache:
        with open(cache, "w") as fh:
            fh.write(raw)

    return json.loads(raw)


def series(doc, name):
    """Return the last data_source named `name`.

    Ordered feed, so the last match is the stable choice if a name repeats.
    """
    matches = [d for d in doc if d.get("name") == name]
    if not matches:
        raise KeyError(name)
    return matches[-1]


def latest_year(doc):
    """The newest series whose name is a year and which carries data.

    Discovered rather than hard-coded: the feeds disagree about how far "now"
    reaches, and the legacy one stops in 2024.
    """
    years = [
        d for d in doc
        if str(d.get("name", "")).isdigit() and any(v is not None for v in d["data"])
    ]
    if not years:
        raise SystemExit("no year series carries data")
    return max(years, key=lambda d: int(d["name"]))


def climatology(doc, want=None):
    """The requested climatology, else the best available by CLIM_NAMES."""
    have = [d.get("name") for d in doc]
    for name in ([want] if want else CLIM_NAMES):
        if name in have:
            return series(doc, name)
    raise SystemExit(
        f"no climatology {want!r} in this feed; it offers: "
        + ", ".join(n for n in have if not str(n).isdigit())
    )


def observed(doc, year, preliminary=False):
    """The year series, optionally extended with Preliminary.

    Returns (values, prelim_from, n_prelim). `values` is a 366-slot list;
    `n_prelim` counts the provisional days the feed offers whether or not we
    used them; `prelim_from` is the 1-based day-of-year at which spliced
    provisional data begins, or None when none was spliced.
    """
    values = list(year["data"])
    try:
        extra = series(doc, PRELIM)["data"]
    except KeyError:
        return values, None, 0

    # Provisional days are only ever the ones the year series has not filled.
    gaps = [i for i, v in enumerate(extra) if v is not None and values[i] is None]
    if not (gaps and preliminary):
        return values, None, len(gaps)

    for i in gaps:
        values[i] = extra[i]
    return values, gaps[0] + 1, len(gaps)


def last_day(values):
    """1-based day-of-year of the last reported value."""
    filled = [i for i, v in enumerate(values) if v is not None]
    if not filled:
        raise SystemExit("no observations in the current series")
    return filled[-1] + 1


def calendar_date(year, doy):
    """Day-of-year (1-based) to a date. Slot 366 is simply null in non-leap
    years, so the index is the calendar day-of-year in every year."""
    return datetime.date(int(year), 1, 1) + datetime.timedelta(days=doy - 1)


def report(region="nino3.4", feed="current", clim=None, preliminary=False, cache=None):
    """Everything the display needs, as a plain dict."""
    url = url_for(region, feed)
    doc = fetch(url, cache=cache)

    year = latest_year(doc)
    cser = climatology(doc, clim)
    values, prelim_from, n_prelim = observed(doc, year, preliminary=preliminary)
    doy = last_day(values)

    have = {d.get("name") for d in doc}
    band = None
    if {PLUS_2S, MINUS_2S} <= have:
        band = (series(doc, MINUS_2S)["data"][doy - 1],
                series(doc, PLUS_2S)["data"][doy - 1])

    return {
        "region": region, "label": REGIONS[region]["label"], "feed": feed, "url": url,
        "year": year["name"], "source": year.get("data_source", "NOAA OISST 2.1"),
        "clim_name": cser["name"], "doy": doy, "date": calendar_date(year["name"], doy),
        "sst": values[doy - 1], "clim": cser["data"][doy - 1],
        "n_final": sum(v is not None for v in year["data"]),
        "prelim_from": prelim_from, "n_prelim": n_prelim, "band": band,
    }


def show(r):
    tail = ""
    if r["n_prelim"]:
        used = "spliced" if r["prelim_from"] else "not shown"
        tail = f" + {r['n_prelim']} preliminary ({used})"

    print(f"region  : {r['label']}")
    print(f"feed    : {r['feed']}  {r['url']}")
    print(f"current : {r['year']:>14}  {r['n_final']:>3} days{tail}   source={r['source']}")
    print(f"clim    : {r['clim_name']:>14}")
    print()

    flag = ", preliminary" if r["prelim_from"] and r["doy"] >= r["prelim_from"] else ""
    print(f"latest day-of-year : {r['doy']}  ({r['date']:%Y-%m-%d}{flag})")
    print(f"latest SST         : {r['sst']:.3f} degC")
    print(f"climatology        : {r['clim']:.3f} degC")
    print(f"anomaly            : {r['sst'] - r['clim']:+.3f} degC")

    if r["band"]:
        lo, hi = r["band"]
        where = ("above +2σ" if r["sst"] > hi else
                 "below -2σ" if r["sst"] < lo else "inside")
        print(f"2-sigma envelope   : {lo:.3f} .. {hi:.3f} degC  ({where})")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--region", default="nino3.4", metavar="ID",
                    help="region id (default: nino3.4); see --list")
    ap.add_argument("--feed", choices=sorted(FEEDS), default="current")
    ap.add_argument("--clim", metavar="NAME",
                    help="climatology series name (default: best available)")
    ap.add_argument("--preliminary", action="store_true",
                    help="splice in the provisional days after the last final one")
    ap.add_argument("--cache", metavar="PATH", help="read/write the raw JSON here")
    ap.add_argument("--list", action="store_true", help="list regions and exit")
    args = ap.parse_args()

    if args.list:
        print(f"{'region':10} {'legacy id':10} label")
        for rid, meta in REGIONS.items():
            print(f"{rid:10} {meta['legacy'] or '--':10} {meta['label']}")
        return

    show(report(region=args.region, feed=args.feed, clim=args.clim,
                preliminary=args.preliminary, cache=args.cache))


if __name__ == "__main__":
    main()
