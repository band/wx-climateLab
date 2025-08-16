# laboratory workbench folder for some weather and climate data explorations


## 2024-02-25
 - find the data files for NOAA global co2 trends and the NOAA Mauna Loa daily readings  
 - the data files can be found here:  
   https://gml.noaa.gov/ccgg/trends/data.html  
   
 - to get the NOAA daily readings:

``` shell
$ curl -q https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_daily_mlo.txt > co2_daily_mlo.txt
```

 - to get the NOAA global co2 trend data:

``` shell
$ curl -q ftp://aftp.cmdl.noaa.gov/products/trends/co2/co2_trend_gl.txt > co2_trend_gl.txt
```

## 2025-02-07  

 - Whole-atmosphere monthly mean COz concentration based on GOSAT observations  
   - https://www.gosat.nies.go.jp/assets  
   - Recent data: https://www.gosat.nies.go.jp/en/recent-global-co2.html  
   - most recent data source download link available on that webpage  

 - `gosatghg.sh` is a `zsh` script to retrieve and display the latest
   CO2 and CH4 data from the GOSAT project  
   
## 2025-08-14  
 - set up on Codeberg  
 
 
