ch4delta ()
{
    : retrieve latest yearly change
    : uses curl, egrep, sed
    if ! output=$(curl -q https://www.gosat.nies.go.jp/en/recent-global-ch4.html > rg-ch4.html); then
	echo "$output" >$2
	return $?
    fi
    local dates=$(egrep 'u43333-8' rg-ch4.html | sed -n 's/.*&nbsp;\(.*\)<\/span>.*/\1/p')
    local value=$(egrep -A1 'u43334-4' rg-ch4.html | egrep -v 'u44497-4' | egrep -o '<p>(.+)</p>' | sed 's/<[^>]*>//g')
    echo "CH4 growth in the past one year: " $dates $value
    return
}
ch4delta 2> /tmp/.scraper.er

