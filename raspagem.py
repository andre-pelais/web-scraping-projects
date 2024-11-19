import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define a User-Agent header to mimic a real browser request, preventing blocks from some websites
headers = {
    'User-Agent': 
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}

# Prompt the user to enter the desired product and format it for the URL
product = input('Type the product that you want: ')
product = product.replace(' ', '-')  # Replace spaces with dashes for Mercado Livre's URL format

# Construct the base URL for Mercado Livre searches
url = f'https://lista.mercadolivre.com.br/{product}'

# Initialize variables
start = 0  # Tracks the pagination index
products_list = pd.DataFrame()  # DataFrame to store the scraped product information

# Loop to scrape multiple pages of results
while True:
    # Adjust the URL based on the pagination index
    if start == 0:
        url_final = url + '_NoIndex_True'
    else:
        url_final = url + '_Desde_' + str(start) + '_NoIndex_True'
    
    # Send a GET request to the Mercado Livre URL
    r = requests.get(url_final, headers=headers)
    
    # Parse the HTML content using BeautifulSoup
    site = BeautifulSoup(r.content, 'html.parser')
    
    # Find all product descriptions and item containers
    descriptions = site.find_all('h2', class_='poly-box poly-component__title')  # Adjusted for Mercado Livre structure
    item = site.find_all('li', class_='ui-search-layout__item')
    
    # If no products are found, exit the loop
    if not descriptions:
        print('No more items found.')
        break
    
    # Extract product data for each description and item pair
    for descricao, item in zip(descriptions, item):
        # Check if the product has fractional or cent values, and calculate the price
        if item.find('span', class_='andes-money-amount__cents andes-money-amount__cents--superscript-24') is None:
            value = float(item.find('span', class_='andes-money-amount__fraction').get_text())
        elif item.find('span', class_='andes-money-amount__fraction') is None:
            value = float(item.find('span', class_='andes-money-amount__cents andes-money-amount__cents--superscript-24').get_text()) / 100
        else:
            value = (
                float(item.find('span', class_='andes-money-amount__fraction').get_text()) +
                (float(item.find('span', class_='andes-money-amount__cents andes-money-amount__cents--superscript-24').get_text()) / 100)
            )
        
        # Create a dictionary with the product information
        new_row = {
            'PRODUCTS': descricao.get_text(),  # Product name
            'VALUES (R$)': value,  # Price in Brazilian Reais
            'URL': item.find('a', class_='').get('href')  # URL to the product page
        }
        
        # Append the new data to the DataFrame
        if products_list.empty:
            products_list = pd.DataFrame([new_row])
        else:
            products_list = pd.concat([products_list, pd.DataFrame([new_row])], ignore_index=True)
    
    # Update the pagination index (Mercado Livre uses 50 results per page)
    start += 50 - 1

# Display the first few rows of the scraped data
print(products_list.head())

# Save the collected data to an Excel file
products_list.to_excel('products_list.xlsx', index=False)
