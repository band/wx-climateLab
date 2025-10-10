#!/usr/bin/env python3

# setup logging
import logging, os
log_level = os.environ.get('LOGLEVEL', 'WARNING').upper()

logging.basicConfig(
    level=getattr(logging, log_level, 'WARNING'),
    format="%(asctime)s - %(name)s - %(levelname)s: %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger('noaa_table_data')

import requests
from bs4 import BeautifulSoup
import pandas as pd

def extract_table_from_noaa_webpage():
    """
    Extracts the Recent Daily Average Mauna Loa HTML table from NOAA's monthly CO2 trends page.
    Returns both the raw HTML and the most recent available data (date and value)
    """
    url = 'https://gml.noaa.gov/ccgg/trends/monthly.html'
    
    try:
        # Fetch the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the div with id="main"
        main_div = soup.find('div', id='main')
        if main_div:
            # Find the element with class "colored_box" inside main
            tablebox_div = main_div.find(class_='colored_box')
            if tablebox_div:
                # Find the table in the colored_box
                table = tablebox_div.find('table')
                if table:
                    logger.info('Table found!')
                    # Extract table data as a list of lists
                    table_data = [[cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])] for row in table.find_all('tr')]
                    data_row = next((row for row in table_data if len(row) >= 2 and 'Unavailable' not in row[1]), None)
                    logger.debug(f"data_row: {data_row}")

                    return {
                        'html': str(table),
                        'data': table_data,
                        'value': data_row,
                        'date': tablebox_div.find('span').get_text(strip=True)
                    }
                else:
                    logger.error('Table not found in card-body')
            else:
                logger.error('card-body not found in main div')
        else:
            logger.error('main div not found')
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f'Error fetching data: {e}')
        return None


def save_to_csv(df, filename='noaa_co2_data.csv'):
    """Save the DataFrame to a CSV file."""
    df.to_csv(filename, index=False)
    print(f'Data saved to {filename}')

def main():
    result = extract_table_from_noaa_webpage()
    
    if result:
        logger.debug('\n--- Table HTML (first 500 chars) ---')
        logger.debug(result['html'][:500])
        
        print('\n--- Latest Data ---')
        print(result['value'])
        print(result['date'])
    else:
        logger.error('Failed to extract table')
    
if __name__ == '__main__':
    exit(main())
