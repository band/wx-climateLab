scrapeco2 ()
{
    : retrieve latest monthly mean CO2 reading from GOSAT data
    : uses curl, egrep, head, sed
    if ! output=$(curl -q https://www.gosat.nies.go.jp/en/recent-global-co2.html > rg-co2.html); then
	echo "$output" >$2
	return $?
    fi
    set -- https://www.gosat.nies.go.jp/$(egrep -o 'href="\.\./assets/[^"]+"' rg-co2.html | head -1 | sed 's|href="\.\./\(.*\)"|\1|g')
    echo $1
    return
}
scrapeco2 2> /tmp/.scraper.er

