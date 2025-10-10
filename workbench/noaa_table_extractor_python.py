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
            # Find the element with class "card-body" inside main
            card_body = main_div.find(class_='card-body')
            if card_body:
                # Find the table inside card-body
                table = card_body.find('table')
                if table:
                    logger.info('Table found!')
                    # Extract table data as a list of lists
                    table_data = []
                    rows = table.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        table_data.append(row_data)
                    
                    return {
                        'html': str(table),
                        'data': table_data,
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
        
        print('\n--- Table Data (first 5 rows) ---')
        table_rows=result['data'][:5]
        data_row = next((row for row in table_rows if len(row) >= 2 and 'Unavailable' not in row[1]), None)
        print(data_row)
    else:
        logger.error('Failed to extract table')
    
if __name__ == '__main__':
    exit(main())
