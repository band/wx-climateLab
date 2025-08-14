co2delta ()
{
    : retrieve latest yearly change
    : uses curl, egrep, sed
    if ! output=$(curl -q https://www.gosat.nies.go.jp/en/recent-global-co2.html > rg-co2.html); then
	echo "$output" >$2
	return $?
    fi
    local dates=$(egrep 'u44496-6' rg-co2.html | sed -n 's/.*&nbsp;\(.*\)<\/span>.*/\1/p')
    local value=$(egrep -A1 'u44497-4' rg-co2.html | egrep -v 'u44497-4' | egrep -o '<p>(.+)</p>' | sed 's/<[^>]*>//g')
    echo "CO2 growth in the past one year: " $dates $value
    return
}
co2delta 2> /tmp/.scraper.er

