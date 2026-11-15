nsatdaily ()
{
    : retrieve latest ERA5 daily near-surface air temperature from C3S CDS;
    : uses: basename, curl, grep, rm, tail;
    : run:  source nsatdaily.sh;
    : to see the "canonical format", declare -f nsatdaily;
    set -- https://sites.ecmwf.int/data/climatepulse/data/series/era5_daily_series_2t_global.csv
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
    : 1850-1900 offset: C3S defines the 1850-1900 global mean as 0.88 degC below 1991-2020;
    : a fixed constant, not in the data file - 0.19 ERA5 1991-2020 minus 1981-2010, plus 0.01 for IPCC AR6;
    : source: https://climate.copernicus.eu/climate-indicators/about-data#Temperatureindicator;
    printf "\t(${parts[1]}) difference from 1850-1900 mean: %.3f\n" $(( parts[4] + 0.88 ))
    rm $df
    return
}
nsatdaily 2> /tmp/.daily.er
