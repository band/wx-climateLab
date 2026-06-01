#!/usr/bin/env python3

import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

import requests
from bs4 import BeautifulSoup

# URL of the webpage to scrape
url = 'https://www.gosat.nies.go.jp/en/recent-global-co2.html'

def main():
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

if __name__ == "__main__":
    exit(main())
