scrippsco2 ()
{
    : retrieve latest CO2 reading from Scripps Mauna Loa Observatory
    : uses: cat, curl, echo, rm, sed
    : run:  source scrippsco2.sh
    : to see the "canonical format", which scrippsco2
    : date: 2020-12-19 -- scripps url updated
    : date: 2021-02-10 -- display data source as Scripps
    : date: 2024-12-31 -- ImageMagick and tesseract updates
    : date: 2025-02-06 -- set curl connection timeout and proceed if no errors
    : date: 2025-04-19 -- use the co2_daily text file for data values
    : date: 2026-11-24 -- remove OCR code: magick, tesseract
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
