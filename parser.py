import requests
import csv
from lxml import html
from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv('BASE_URL')

'''
Method to get the page number from URL
@param url (The url containing the paramter 'page')
'''
def get_page_number_from_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return int(query_params.get('page', [1])[0])


'''
Method to get the url for the scraping
@param url (The url which you want to scrape)
'''
def get_scrapeops_url(url):
    try:
        payload = {'api_key': os.getenv('API_KEY'), 'url': url}
        proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
        return proxy_url
    except:
        print("Error while using ScarpeOps API")

'''
Method to scrape product_names frm the page
'''
def get_product_names_from_page(tree):
    products = tree.xpath('//div[contains(@class, "project-info-wrapper")]//h3')
    return [product.text_content().strip() for product in products]

'''
Method to scrape next_page_url
'''
def get_next_page_url(tree):
    """Returns the URL for the next page, or None if there isn't one."""
    next_buttons = tree.xpath('//li[@class="pagination-next "]/a')
    return next_buttons[0].get('href') if next_buttons else None

def main():
    terms = ["manufacturing"]
    for term in terms:
        OUTPUT_FILE = term+'.csv'
        product_names = []
        url = BASE_URL + term
        while url:
            response = requests.get(get_scrapeops_url(url))  # Use the current URL
            tree = html.fromstring(response.content)
            product_names.extend(get_product_names_from_page(tree))
            next_page_url = get_next_page_url(tree)
            if next_page_url:
                url = "https://slashdot.org" + next_page_url
            else:
                url = None  # Break the loop if there's no next page

        with open(OUTPUT_FILE, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Product Name'])
            for name in product_names:
                writer.writerow([name])
        print(f"Scraped {len(product_names)} product names and saved them to {OUTPUT_FILE}.")


if __name__ == '__main__':
    main()
