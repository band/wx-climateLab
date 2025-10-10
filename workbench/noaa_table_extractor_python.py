import requests
from bs4 import BeautifulSoup
import pandas as pd

def extract_table_from_noaa():
    """
    Extracts the HTML table from NOAA's monthly CO2 trends page.
    Returns both the raw HTML and the data as a pandas DataFrame.
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
                    print('Table found!')
                    
                    # Extract table data as a list of lists
                    table_data = []
                    rows = table.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        table_data.append(row_data)
                    
                    # Convert to pandas DataFrame
                    if len(table_data) > 1:
                        df = pd.DataFrame(table_data[1:], columns=table_data[0])
                    else:
                        df = pd.DataFrame(table_data)
                    
                    return {
                        'html': str(table),
                        'data': table_data,
                        'dataframe': df
                    }
                else:
                    print('Table not found in card-body')
            else:
                print('card-body not found in main div')
        else:
            print('main div not found')
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f'Error fetching data: {e}')
        return None


def save_to_csv(df, filename='noaa_co2_data.csv'):
    """Save the DataFrame to a CSV file."""
    df.to_csv(filename, index=False)
    print(f'Data saved to {filename}')


# Usage example
if __name__ == '__main__':
    result = extract_table_from_noaa()
    
    if result:
        print('\n--- Table HTML (first 500 chars) ---')
        print(result['html'][:500])
        
        print('\n--- Table Data (first 5 rows) ---')
        for row in result['data'][:5]:
            print(row)
        
        print('\n--- DataFrame ---')
        print(result['dataframe'])
        
        # Optionally save to CSV
        save_to_csv(result['dataframe'])
    else:
        print('Failed to extract table')