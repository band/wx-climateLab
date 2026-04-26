scrippsco2 ()
{
    : retrieve latest CO2 reading from Scripps Mauna Loa Observatory
    : uses: curl, head, magick, rm, sed, tesseract
    : run:  source scrippsco2.sh
    : note: this script OCRs an image file - date of reading not available
    : to see the "canonical format", which scrippsco2
    : date: 2020-12-19 -- scripps url updated
    : date: 2021-02-10 -- display data source as Scripps
    : date: 2024-12-31 -- ImageMagick and tesseract updates
    : date: 2025-02-06 -- set curl connection timeout and proceed if no errors
    : date: 2025-04-19 -- use the co2_daily text file for data values
    set -- https://scripps.ucsd.edu/bluemoon/co2_400/daily_value.png
    if ! output=$(curl --connect-timeout 5 -q $1 > latestValue.png); then
        echo "$output" >&2
        return $?
    fi
    magick latestValue.png lValue.jpg
    tesseract lValue.jpg latestValue --oem 1 -l eng
    echo "Latest co2 concentration at Scripps Mauna Loa Observatory: $(head -n1 latestValue.txt | sed -e 's/^.*reading: // ; s/,/./')"
    rm latestValue.png lValue.jpg latestValue.txt
    set -- https://scripps.ucsd.edu/bluemoon/co2_400/co2_daily
    if ! output=$(curl --connect-timeout 5 -q $1 > co2_daily.txt); then
        echo "$output" >&2
        return $?
    fi
    echo "Latest co2 concentration at Scripps Mauna Loa Observatory: $(cat co2_daily.txt |sed 's/\(.*\), \(.*\)/\1 ppm, on \2/')"
    rm co2_daily.txt
    return
}
scrippsco2 2> /tmp/.latest.er
