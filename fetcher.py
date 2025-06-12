import os
import json
from paapi5_python_sdk.api_helper import ApiHelper
from paapi5_python_sdk.configuration import Configuration
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.search_items_resource import SearchItemsResource
from paapi5_python_sdk.search_items_request import SearchItemsRequest
from paapi5_python_sdk.sort_by import SortBy

# Amazon API credentials from environment variables
AWS_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")

# Affiliate tag for all locales
PARTNER_TAG = "strobify10-20"

# Supported locales with domain, region, search index, and category
LOCALE_CONFIGS = {
    "US": {"host": "webservices.amazon.com", "region": "US", "search_index": "InternalHardDrives"},
    "CA": {"host": "webservices.amazon.ca", "region": "CA", "search_index": "InternalHardDrives"},
    "UK": {"host": "webservices.amazon.co.uk", "region": "GB", "search_index": "Computers"},
    "DE": {"host": "webservices.amazon.de", "region": "DE", "search_index": "Computer"},
    "FR": {"host": "webservices.amazon.fr", "region": "FR", "search_index": "Informatique"},
    "IT": {"host": "webservices.amazon.it", "region": "IT", "search_index": "Informatica"},
    "ES": {"host": "webservices.amazon.es", "region": "ES", "search_index": "Informática"},
    "NL": {"host": "webservices.amazon.nl", "region": "NL", "search_index": "Computers"},
    "PL": {"host": "webservices.amazon.pl", "region": "PL", "search_index": "Komputery"},
    "SE": {"host": "webservices.amazon.se", "region": "SE", "search_index": "Datorer"},
}

# Keywords to search for SSDs
SEARCH_KEYWORDS = "solid state drive"

# Output JSON structure
products = []

def fetch_ssd_data(locale):
    config = LOCALE_CONFIGS[locale]
    
    configuration = Configuration(
        access_key=AWS_ACCESS_KEY,
        secret_key=AWS_SECRET_KEY,
        host=config["host"],
        region=config["region"]
    )

    api = DefaultApi(ApiHelper(configuration))

    # Set up request
    search_items_request = SearchItemsRequest(
        partner_tag=PARTNER_TAG,
        partner_type="Associates",
        keywords=SEARCH_KEYWORDS,
        search_index=config["search_index"],
        item_count=10,
        sort_by=SortBy.BEST_SELLER,  # Sort by Most Popular / Best Seller
        resources=[
            SearchItemsResource.ITEMINFO_TITLE,
            SearchItemsResource.OFFERS_LISTINGS_PRICE,
            SearchItemsResource.IMAGES_PRIMARY_LARGE,
            SearchItemsResource.OFFERS_LISTINGS_URL,
        ]
    )

    try:
        response = api.search_items(search_items_request)
        if response.search_result:
            for item in response.search_result.items:
                title = item.item_info.title.display_value if item.item_info.title else "N/A"
                price = item.offers.listings[0].price.amount if item.offers.listings and item.offers.listings[0].price else None
                currency = item.offers.listings[0].price.currency if item.offers.listings and item.offers.listings[0].price else ""
                image = item.images.primary.large.url if item.images and item.images.primary and item.images.primary.large else ""
                url = item.offers.listings[0].url if item.offers.listings and item.offers.listings[0].url else ""

                # Try to extract capacity from title (basic logic)
                capacity = "N/A"
                for word in title.split():
                    if "TB" in word or "GB" in word:
                        capacity = word
                        break

                # Calculate price per TB if possible
                price_per_tb = "N/A"
                if price and "TB" in capacity:
                    try:
                        cap_value = float(capacity.replace("TB", "").replace(" ", ""))
                        price_per_tb = round(float(price) / cap_value, 2)
                    except:
                        price_per_tb = "N/A"
                elif price and "GB" in capacity:
                    try:
                        cap_value = float(capacity.replace("GB", "").replace(" ", "")) / 1000
                        price_per_tb = round(float(price) / cap_value, 2)
                    except:
                        price_per_tb = "N/A"

                products.append({
                    "locale": locale,
                    "title": title,
                    "capacity": capacity,
                    "price": price,
                    "currency": currency,
                    "price_per_tb": price_per_tb,
                    "image": image,
                    "url": url
                })
    except Exception as e:
        print(f"Error fetching data for {locale}: {e}")


def main():
    for locale in LOCALE_CONFIGS.keys():
        print(f"Fetching SSD data for locale: {locale}")
        fetch_ssd_data(locale)

    # Write results to JSON file
    with open("ssd_prices.json", "w") as f:
        json.dump(products, f, indent=2)

if __name__ == "__main__":
    main()
