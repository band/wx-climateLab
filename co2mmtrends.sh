co2mmtrends ()
{
    : retrieve latest, 1 year ago, 10, 20, 30, and 40 year ago monthly average CO2 trend values from NOAA
    : uses: awk, basename, curl, grep, tail, tr
    : run:  source co2mmtrends.sh
    : to see the "canonical format", declare -f co2mmtrends
    : date: 2025-02-11 -- set curl connection timeout
    : date: 2025-08-14 -- display monthly trend data
    set -- https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.txt
    local df=$(basename $1)
    curl --connect-timeout 5 -q $1 | tr -s ' ' > $df || { echo curl error 1>&2; return 1; }
    :
    set -- $(tail -n 1 $df) && yr=$1 && mo=$2
    :
    grep "$yr $mo " $df | awk '
    BEGIN { fmt = "\nLatest (%s-%02d) average monthly global co2 trend value (NOAA):\t\t  %s ppm\n" } 
          {  printf( fmt, $1, $2, $6 )
          }
'
    grep "$(($yr-1)) $mo " $df | awk '
    BEGIN { fmt = "\nOne year ago (%s-%02d) average monthly global co2 trend value (NOAA): \t  %s ppm\n" } 
          {  printf( fmt, $1, $2, $6 )
          }
'
    grep "$(($yr-10)) $mo " $df | awk '
    BEGIN { fmt = "Ten years ago (%s-%02d) average monthly global co2 trend value (NOAA): \t  %s ppm\n" } 
          {  printf( fmt, $1, $2, $6 )
          }
'
    grep "$(($yr-20)) $mo " $df | awk '
    BEGIN { fmt = "Twenty years ago (%s-%02d) average monthly global co2 trend value (NOAA): %s ppm\n" } 
          {  printf( fmt, $1, $2, $6 )
          }
'
    grep "$(($yr-30)) $mo " $df | awk '
    BEGIN { fmt = "Thirty years ago (%s-%02d) average monthly global co2 trend value (NOAA): %s ppm\n" } 
          {  printf( fmt, $1, $2, $6 )
          }
'
    grep "$(($yr-40)) $mo " $df | awk '
    BEGIN { fmt = "Forty years ago (%s-%02d) average monthly global co2 trend value (NOAA):  %s ppm\n\n" } 
          {  printf( fmt, $1, $2, $6 )
          }
'
     rm $df
    return
}
co2mmtrends 2> /tmp/.daily.er
