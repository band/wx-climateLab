nastrends ()
{
    : retrieve latest, 1 year ago, and 10 year ago near-surface air temperature from C3S;
    : uses: awk, basename, curl, grep, tail, rm, tr;
    : run:  source nastrends.sh;
    : to see the "canonical format", declare -f co2trends;
    set -- https://sites.ecmwf.int/data/climatepulse/data/series/era5_daily_series_2t_global.csv
    local df
    df=${$(basename $1):r}.txt
    echo $df
    curl -q $1 > $df || { echo curl error  1>&2; return 1; }
    local line
    line=$(tail -n 2 $df | head -n 1)
    echo $line
    local parts
    parts=("${(s/,/)line}")
    echo $parts
    print $parts[1], $parts[2], $parts[4]
#    set -- $(tail -n 1 $df) && yr=$1 && mo=$2 && dy=$3
#    :
#    grep "$yr $mo $dy " $df | awk '
#    BEGIN { fmt = "Latest (%s-%02d-%02d) average global co2 trend value (NOAA):\t  %s ppm\n" } 
#          {  printf( fmt, $1, $2, $3, $5 )
#          }
#'
#    grep "$(($yr-1)) $mo $dy " $df | awk '
#    BEGIN { fmt = "One year ago (%s-%02d-%02d) average global co2 trend value (NOAA):  %s ppm\n" } 
#          {  printf( fmt, $1, $2, $3, $5 )
#          }
#'
#    grep "$(($yr-10)) $mo $dy " $df | awk '
#    BEGIN { fmt = "Ten years ago (%s-%02d-%02d) average global co2 trend value (NOAA): %s ppm\n" } 
#          {  printf( fmt, $1, $2, $3, $5 )
#          }
#'
#   rm $df
    return
}
nastrends 2> /tmp/.daily.er
