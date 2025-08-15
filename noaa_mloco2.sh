latestnoaaco2 ()
{
    : retrieve latest CO2 readings from Scripps and NOAA Mauna Loa Observatories;
    : uses: awk, basename, curl, tail;
    : run:  source latestnoaaco2.sh;
    : to see the "canonical format", declare -f latestnoaaco2;
    : date: 2025-08-05 -- get latest NOAA MLO value;
    : retrieve lastest CO2 reading from NOAA Mauna Loa Observatory;
    set -- https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_daily_mlo.txt
    set -- $1 $(basename $1)
    curl -q $1 > $2 || { echo curl error 1>&2; return 1; }
    tail -n 1 $2 | awk '
    BEGIN { fmt = "Latest (%s-%02d-%02d) NOAA Mauna Loa Observatory co2 value: %s ppm\n" }
          { printf( fmt, $1, $2, $3, $5 ) }
    '
    rm $(basename $1)
    return
}
latestnoaaco2 2> /tmp/.latest.er
