latestco2 ()
{
    : retrieve latest CO2 readings from Scripps and NOAA Mauna Loa Observatories;
    : uses: awk, basename, cat, curl, echo, sed, tail;
    : run:  source latestco2.sh;
    : to see the "canonical format", declare -f latestco2;
    : date: 2020-12-19 -- scripps url updated;
    : date: 2021-02-10 -- display data source as Scripps;
    : date: 2024-12-31 -- ImageMagick and tesseract updates;
    : date: 2025-01-24 -- get latest NOAA MLO value;
    : date: 2025-04-22 -- use Scripps MLO ASCII text data file; replace OCR code;
    : date: 2025-04-26 -- make iso_date an internal fn;
    : date: 2025-08-05 -- try NOAA MLO if Scripps fails;
    iso_date() {
	: convert DD-Mon-YYYY to ISO 8601 format YYYY-MM-DD;
	set -- $(echo $1 | sed 's/-/ /g')
	case $2 in
            (Jan) mo="01" ;;
            (Feb) mo="02" ;;
            (Mar) mo="03" ;;
            (Apr) mo="04" ;;
            (May) mo="05" ;;
            (Jun) mo="06" ;;
            (Jul) mo="07" ;;
            (Aug) mo="08" ;;
            (Sep) mo="09" ;;
            (Oct) mo="10" ;;
            (Nov) mo="11" ;;
            (Dec) mo="12" ;;
	esac
	# return as YYYY-MM-DD
	echo "$3-$mo-$1"
    }
    : retrieve daily CO2 reading from Scripps Mauna Loa Observatory;
    set -- https://scripps.ucsd.edu/bluemoon/co2_400/co2_daily
    if ! output=$(curl --connect-timeout 5 -q $1 > co2_daily.txt); then
        echo "$output" >&2
    else
	set -- $(cat co2_daily.txt | sed 's/, / /')
	echo "Latest ($(iso_date ${2})) Scripps Mauna Loa Observatory co2 value: $1 ppm"
	rm co2_daily.txt
    fi
    : retrieve lastest CO2 reading from NOAA Mauna Loa Observatory;
    set -- https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_daily_mlo.txt
    set -- $1 $(basename $1)
    curl -q $1 > $2 || { echo curl error 1>&2; return 1; }
    tail -n 1 $2 | awk '
    BEGIN { fmt = "Latest (%s-%02d-%02d) NOAA Mauna Loa Observatory co2 value: %s ppm\n" }
          { printf( fmt, $1, $2, $3, $5 ) }
    '
    rm $(basename $1)
    return $?
}
latestco2 2> /tmp/.latest.er
