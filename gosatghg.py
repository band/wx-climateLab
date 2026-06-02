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
        
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # find the soup elements to scrape
    prelims = soup.find_all("div", class_="preliminary")

    logging.info(f"prelims[0]: {prelims[0]}\n")

    for pre in prelims:
        print(f"pre: {pre}\n")
        print(pre.find('dt').text.strip())
        print(f"date: {pre.find('dd').text.strip()}")
        print(f"value: {pre.find('div', class_='values').text.strip()}")
        print("___________")

    print(f"Latest {prelims[0].find('dd').text.strip()} monthly {ghg} mean value: {prelims[0].find('div', class_='values').text.strip()} | trend value: {prelims[1].find('div', class_='values').text.strip()}")
    print(f"{ghg} growth in the past one year: {prelims[2].find('dd').text.strip()} : {prelims[2].find('div', class_='values').text.strip()}")

def main():

    # URL of the webpage to scrape
    urlco2 = 'https://www.gosat.nies.go.jp/en/recent-global-co2.html'
    urlch4 = 'https://www.gosat.nies.go.jp/en/recent-global-ch4.html'

    scrape_print(urlco2)
    scrape_print(urlch4)


if __name__ == "__main__":
    exit(main())
