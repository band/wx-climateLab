nsatdaily ()
{
    : retrieve latest ERA5 daily near-surface air temperature from C3S CDS;
    : uses: basename, curl, grep, rm, tail;
    : run:  source nsatdaily.sh;
    : to see the "canonical format", declare -f nsatdaily;
    set -- https://sites.ecmwf.int/data/climatepulse/timeseries/csv/daily/timeseries_era5_t2m_daily_global.csv
    local df
    df=${$(basename $1):r}.txt
    :debug $df
    curl -q $1 > $df || { echo curl error  1>&2; return 1; }
    local line
    : take the latest FINAL row by its status column - skip preliminary rows;
    line=$(grep ',FINAL$' $df | tail -n 1)
    : echo $line
    local parts
    parts=("${(s/,/)line}")
    printf "Latest\t(${parts[1]}) ERA5 daily mean near-surface air temperature: ${parts[2]} degC\n"
    printf "\t(${parts[1]}) difference from 1991-2020 mean: ${parts[4]}\n"
    : columns: date,t2m,clim_1991_2020,anom_1991_2020,offset_1850_1900,anom_1850_1900,status;
    : the file starts with "#" comment lines - the FINAL grep above skips them;
    : anom_1850_1900 is computed by C3S as anom_1991_2020 + a per-day offset_1850_1900;
    printf "\t(${parts[1]}) difference from 1850-1900 mean: ${parts[6]}\n"
    rm $df
    return
}
nsatdaily 2> /tmp/.daily.er
