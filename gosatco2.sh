gosatco2 ()
{
    : retrieve latest monthly mean CO2 readings from GOSAT observation data
    : uses: awk, basename, curl, echo, egrep, head, sed, tail, tr, unzip
    : run:  source gosatco2.sh
    : to see the "canonical format", which gosatco2
    if ! output=$(curl -q https://www.gosat.nies.go.jp/en/recent-global-co2.html > rg-co2.html); then
	echo "$output" >$2
	return $?
    fi
    data_link=$(egrep -o 'href="\.\./assets/[^"]+"' rg-co2.html | head -1 | sed 's|href="\.\./\(.*\)"|\1|g')
    set -- https://www.gosat.nies.go.jp/$data_link
    local wamm_zip="$(basename $1)"
    echo $wamm_zip
    if ! output=$(curl --connect-timeout 5 -q $1 > $wamm_zip); then
        echo "$output" >&2
        return $?
    fi
    unzip -qo $wamm_zip
    local wamm_text=$(basename $wamm_zip .zip)
    echo "Whole-atmosphere monthly mean CO2 concentration based on GOSAT observations:"
    tail -n 1 $wamm_text | tr -d '\r\n' | awk '
    	 { fmt = "Latest %s-%02d monthly CO2 mean value: %s (ppm) | trend value: %s (ppm)\n" }
         { printf( fmt, $1, $2, $3, $4 ) }
    '
    local dates=$(egrep 'u44496-6' rg-co2.html | sed -n 's/.*&nbsp;\(.*\)<\/span>.*/\1/p')
    local value=$(egrep -A1 'u44497-4' rg-co2.html | egrep -v 'u44497-4' | egrep -o '<p>(.+)</p>' | sed 's/<[^>]*>//g')
    echo "CO2 growth in the past one year: " $dates $value
    rm rg-co2.html $wamm_zip $wamm_text
    return
}
gosatco2 2> /tmp/.latest.er
