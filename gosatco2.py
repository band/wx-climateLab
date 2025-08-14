#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# URL of the webpage to scrape
url = 'https://www.gosat.nies.go.jp/en/recent-global-co2.html'

# Send a GET request to the webpage
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Define the text you want to search for within href attributes
search_text = '../assets/'

# Filter function to find <a> tags with specific text in href
def href_contains_text(tag):
    return tag.name == 'a' and search_text in tag.get('href', '')

# Use find_all with the filter function
a_tags = soup.find_all(href_contains_text)

print(len(a_tags))
# Extract and print the text from each <a> tag that matches the filter
for tag in a_tags:
    print(f"\n{tag}")

