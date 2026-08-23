nsatdaily ()
{
    : retrieve latest ERA5 daily near-surface air temperature from C3S CDS;
    : uses: basename, curl, head, tail, rm;
    : run:  source nsatdaily.sh;
    : to see the "canonical format", declare -f nsatdaily;
    set -- https://sites.ecmwf.int/data/climatepulse/data/series/era5_daily_series_2t_global.csv
    local df
    df=${$(basename $1):r}.txt
    :debug $df
    curl -q $1 > $df || { echo curl error  1>&2; return 1; }
    local line
    line=$(tail -n 2 $df | head -n 1)
    : echo $line
    local parts
    parts=("${(s/,/)line}")
    printf "Latest\t(${parts[1]}) ERA5 daily mean near-surface air temperature: ${parts[2]} degC\n"
    printf "\t(${parts[1]}) difference from 1991-2020 mean: ${parts[4]}\n"
    rm $df
    return
}
nsatdaily 2> /tmp/.daily.er
