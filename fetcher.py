# ==============================================================================
#                 TEST SCRIPT: Using a Single Global Tag
# ==============================================================================
# This script is a special test to verify the API's behavior.
# It uses the SINGLE tag 'strobify10-20' for ALL countries.
# We will inspect the logs to see which countries succeed and which fail.
# ==============================================================================

import os
import json
from paapi.api import API

# --- Configuration Section ---

AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")

# --- TEST CONFIGURATION: Using a single tag for all API calls ---
# We are testing the hypothesis that 'strobify10-20' works everywhere.
LOCALES_CONFIG = {
    'us': {'tag': 'strobify10-20',   'node': '1292116011'},
    'ca': {'tag': 'strobify10-20',   'node': '1232593011'},
    'uk': {'tag': 'strobify10-20',   'node': '430505031'},   # Using US tag for UK
    'de': {'tag': 'strobify10-20',   'node': '430168031'},   # Using US tag for DE
    'fr': {'tag': 'strobify10-20',   'node': '430343031'},   # Using US tag for FR
    'it': {'tag': 'strobify10-20',   'node': '430103031'},   # Using US tag for IT
    'es': {'tag': 'strobify10-20',   'node': '937915031'},   # Using US tag for ES
    'nl': {'tag': 'strobify10-20',   'node': '16366535031'}, # Using US tag for NL
    'pl': {'tag': 'strobify10-20',   'node': None},          # Using US tag for PL
    'se': {'tag': 'strobify10-20',   'node': None},          # Using US tag for SE
}

SEARCH_KEYWORD = "nvme ssd"

def parse_capacity_from_title(title):
    title_lower = title.lower().replace(" ", "")
    if "8tb" in title_lower: return 8000
    if "4tb" in title_lower: return 4000
    if "2tb" in title_lower: return 2000
    if "1tb" in title_lower: return 1000
    if "512gb" in title_lower or "500gb" in title_lower: return 500
    return 0

def generate_ssd_json():
    all_ssd_data = {}

    for locale, config in LOCALES_CONFIG.items():
        print(f"--- Testing data fetch for locale: {locale.upper()} ---")
        try:
            api = API(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, config['tag'], locale.upper())
            products = api.search_items(
                keywords=SEARCH_KEYWORD,
                browse_node_id=config['node'],
                resources=["ItemInfo.Title", "Offers.Listings.Price", "DetailPageURL", "Images.Primary.Large"],
                item_count=10
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
                        "image": image_url, "title": title, "capacity_gb": capacity_gb,
                        "price": price, "currency": currency, "price_per_tb": round(price_per_tb, 2), "link": url
                    })
                print(f"  [SUCCESS] Found {len(locale_ssds)} products for {locale.upper()}.")
            else:
                 print(f"  [EMPTY] No products found for {locale.upper()}.")

            all_ssd_data[locale] = locale_ssds

        except Exception as e:
            # This is the most important part. We expect errors for Europe.
            print(f"  [ERROR] The API call failed for {locale.upper()}. Reason: {e}")
            all_ssd_data[locale] = []
            continue

    with open('ssd_prices.json', 'w', encoding='utf-8') as f:
        json.dump(all_ssd_data, f, indent=2, ensure_ascii=False)

    print("\n✅ Test finished. ssd_prices.json created.")

if __name__ == "__main__":
    generate_ssd_json()