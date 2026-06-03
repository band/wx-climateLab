#!/usr/bin/env python3

import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

import requests
from bs4 import BeautifulSoup

def scrape_print(url):
    if 'co2' in url:
        ghg = 'CO2'
    elif 'ch4' in url:
        ghg = 'CH4'
        
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    prelims = soup.find_all("div", class_="preliminary")

    print(f"Latest {prelims[0].find('dd').text.strip()} monthly {ghg} mean value: {prelims[0].find('div', class_='values').text.strip()} | trend value: {prelims[1].find('div', class_='values').text.strip()}")
    print(f"{ghg} growth in the past one year: {prelims[2].find('dd').text.strip()} : {prelims[2].find('div', class_='values').text.strip()}\n")

def main():
    urlco2 = 'https://www.gosat.nies.go.jp/en/recent-global-co2.html'
    urlch4 = 'https://www.gosat.nies.go.jp/en/recent-global-ch4.html'
    try:
        scrape_print(urlco2)
        scrape_print(urlch4)
    except Exception as e:
        logging.error(f"Error: {e}")


if __name__ == "__main__":
    exit(main())
