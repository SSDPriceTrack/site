# ==============================================================================
#                 SSD Price Tracker - Data Fetching Script
# ==============================================================================
# This script connects to the Amazon API to find SSD prices across multiple
# countries and saves the data to a JSON file for the website to use.
# ==============================================================================

import os
import json
from paapi.api import API  # The library for connecting to Amazon's API

# --- Configuration Section ---

# These keys are securely loaded from your GitHub Repository Secrets.
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")

# Ensure that keys are loaded properly
if not AMAZON_ACCESS_KEY or not AMAZON_SECRET_KEY:
    raise ValueError("Amazon Access Key and Secret Key must be set in environment variables")

# Shared tracking tag for all countries (e.g., strobify10-20)
TRACKING_TAG = 'strobify10-20'

# Category ID for SSD (This is the same for all locales)
SSD_BROWSE_NODE_ID = '1292116011'  # You can adjust this for specific locales if needed

# Locale configurations
LOCALES = [
    'us', 'ca', 'uk', 'de', 'fr', 'it', 'es', 'nl', 'pl', 'se'
]

# General keyword to search for within the specified category.
SEARCH_KEYWORD = "nvme ssd"

def parse_capacity_from_title(title):
    """Helper function to find the storage capacity from a product title."""
    title_lower = title.lower().replace(" ", "")
    if "8tb" in title_lower: return 8000
    if "4tb" in title_lower: return 4000
    if "2tb" in title_lower: return 2000
    if "1tb" in title_lower: return 1000
    if "512gb" in title_lower or "500gb" in title_lower: return 500
    return 0

def fetch_ssd_data_for_locale(locale):
    """Fetches SSD data from Amazon API for a specific locale."""
    try:
        # Initialize the API for the current country with the shared tracking tag
        api = API(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, TRACKING_TAG, locale.upper())

        # Search for items
        products = api.search_items(
            keywords=SEARCH_KEYWORD,
            browse_node_id=SSD_BROWSE_NODE_ID,
            resources=[
                "ItemInfo.Title", "Images.Primary.Large",
                "Offers.Listings.Price", "DetailPageURL"
            ],
            item_count=10,
            sort_by="Relevance"
        )

        locale_ssds = []
        if products and products.get('SearchResult') and products['SearchResult'].get('Items'):
            for product in products['SearchResult']['Items']:
                if not product.get('Offers'): continue

                title = product['ItemInfo']['Title']['DisplayValue']
                capacity_gb = parse_capacity_from_title(title)
                if capacity_gb == 0: continue

                price = product['Offers']['Listings'][0]['Price']['Amount']
                currency = product['Offers']['Listings'][0]['Price']['Currency']
                url = product['DetailPageURL']
                image_url = product.get('Images', {}).get('Primary', {}).get('Large', {}).get('URL', "")
                price_per_tb = (price / capacity_gb) * 1024

                locale_ssds.append({
                    "image": image_url,
                    "title": title,
                    "capacity_gb": capacity_gb,
                    "price": price,
                    "currency": currency,
                    "price_per_tb": round(price_per_tb, 2),
                    "link": url,
                })
                print(f"  [OK] Found: {title[:50]}... @ {price} {currency}")

        return locale_ssds

    except Exception as e:
        print(f"  [ERROR] Could not fetch data for {locale.upper()}: {e}")
        return []

def generate_ssd_json():
    """Main function to loop through countries, fetch data, and write the JSON file."""
    all_ssd_data = {}

    # Loop through each country and fetch SSD data using the shared tracking tag
    for locale in LOCALES:
        print(f"--- Fetching data for locale: {locale.upper()} ---")
        locale_ssds = fetch_ssd_data_for_locale(locale)
        all_ssd_data[locale] = locale_ssds

    # Write all data to the final JSON file
    output_file = 'ssd_prices.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_ssd_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Successfully created {output_file}")

if __name__ == "__main__":
    generate_ssd_json()
