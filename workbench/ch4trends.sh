ch4trends ()
{
    : retrieve latest, 1 year ago, and 10 year ago monthly average CH4 trend reading from NOAA;
    : uses: awk, basename, curl, grep, tail, rm, tr;
    : run:  source ch4trends.sh;
    : to see the "canonical format", declare -f ch4trends;
    #    set -- ftp://aftp.cmdl.noaa.gov/products/trends/ch4/ch4_trend_gl.txt
    set -- https://gml.noaa.gov/webdata/ccgg/trends/ch4/ch4_mm_gl.txt
    df=$(basename $1)
    curl -q $1 | tr -s ' ' > $df || { echo curl error  1>&2; return 1; }
    :
    set -- $(tail -n 1 $df) && yr=$1 && mo=$2
    :
    grep "$yr $mo " $df | awk '
    BEGIN { fmt = "Latest (%s-%02d) average marine ch4 trend value (NOAA):\t  %s ppb\t%s uncertainty\n" } 
          {  printf( fmt, $1, $2, $6, $7 )
          }
'
    grep "$(($yr-1)) $mo " $df | awk '
    BEGIN { fmt = "One year ago (%s-%02d) average marine ch4 trend value (NOAA):  %s ppb\t%s uncertainty\n" } 
          {  printf( fmt, $1, $2, $6, $7 )
          }
'
    grep "$(($yr-10)) $mo " $df | awk '
    BEGIN { fmt = "Ten years ago (%s-%02d) average marine ch4 trend value (NOAA): %s ppb\t%s uncertainty\n" } 
          {  printf( fmt, $1, $2, $6, $7 )
          }
'
#    rm $df
    return
}
ch4trends 2> /tmp/.daily.er


