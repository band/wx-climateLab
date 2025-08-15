dailyco2 ()
{
    : retrieve latest average CO2 reading from NOAA
    : uses: awk, basename, curl, echo, tail
    : run:  source dailyco2.sh   
    : note: a change to echo messages onto STDERR.
    : to see the "canonical format", declare -f dailyco2
    : date: 2020-07-20 -- do not leave data files in cwd
    : date: 2021-02-10 -- display data source is NOAA
    : date: 2025-02-07 -- set curl connection timeout
    set -- ftp://aftp.cmdl.noaa.gov/products/trends/co2/co2_trend_gl.txt
    set -- $1 $(basename $1)
    curl --connect-timeout 5 -q $1 > $2 || { echo curl error 1>&2; return 1; }
    :
    tail -n 1 $2 | awk '

    BEGIN { fmt = "Latest (%s-%02d-%02d) NOAA average global co2 value: %s ppm\n" }
          { printf( fmt, $1, $2, $3, $4 ) }
    '
    rm $(basename $1)
    return
}
dailyco2 2> /tmp/.daily.er
