sstdaily ()
{
    : retrieve latest ERA5 daily mean sea surface temperature from C3S CDS;
    : uses: basename, curl, tail, rm;
    : run:  source sstdaily.sh;
    : to see the "canonical format", declare -f sstdaily;
    set -- https://sites.ecmwf.int/data/climatepulse/data/series/era5_daily_series_sst_60S-60N_ocean.csv
    local df
    df=${$(basename $1):r}.txt
    :debug $df
    curl -q $1 > $df || { echo curl error  1>&2; return 1; }
    local line
    line=$(tail -n 1 $df)
    : echo $line
    local parts
    parts=("${(s/,/)line}")
    printf "Latest\t(${parts[1]}) ERA5 daily mean sea surface temperature: ${parts[2]} degC\n"
    printf "\t(${parts[1]}) difference from 1991-2020 mean: ${parts[4]}\n"
    rm $df
    return
}
sstdaily 2> /tmp/.daily.er
