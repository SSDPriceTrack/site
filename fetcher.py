import os
import json
from amazon_paapi import AmazonAPI, models

# --- Configuration ---
# These will be pulled from your GitHub Secrets
AMAZON_ACCESS_KEY = os.environ.get("AKPAB3SVQ11749716070")
AMAZON_SECRET_KEY = os.environ.get("g2Qx2Bxv0g3XtuUUSVay+t1llrXngqeJgEEtc8fR")

# --- YOUR PERSONALIZED LOCALES AND TRACKING IDs ---
# IMPORTANT: Double-check these tracking IDs in your Amazon Associates account!
# Go to "Manage Your Tracking IDs" to confirm them.
LOCALES = {
    'us': 'strobify10',   # United States
    'ca': 'strobify10',   # Canada (Often shares the US ID if linked, but verify!)
    'uk': 'strobify10',   # United Kingdom
    'de': 'strobify10',   # Germany
    'fr': 'strobify10',   # France (Often grouped with DE, verify)
    'it': 'strobify10',   # Italy (Often grouped with DE, verify)
    'es': 'strobify10',   # Spain (Often grouped with DE, verify)
    'nl': 'strobify10',   # Netherlands (Often grouped with DE, verify)
    'pl': 'strobify10',   # Poland (Often grouped with DE, verify)
    'se': 'strobify10',   # Sweden (Often grouped with DE, verify)
}
# Note: Amazon Europe often groups countries under one tag (like -22). Please verify!
# --- NEW: We now use a single, generic search term ---
SEARCH_KEYWORD = "nvme ssd"

# Helper function for parsing capacity. This function is now MORE important
# because titles will be varied. You may need to improve it over time.
def parse_capacity_from_title(title):
    title_lower = title.lower().replace(" ", "")
    if "8tb" in title_lower: return 8000
    if "4tb" in title_lower: return 4000
    if "2tb" in title_lower: return 2000
    if "1tb" in title_lower: return 1000
    if "512gb" in title_lower or "500gb" in title_lower: return 500
    return 0

# --- Main Script Logic ---
def generate_ssd_json():
    all_ssd_data = {}
    search_resources = [
        models.SearchItemsResource.ITEM_INFO_TITLE,
        models.SearchItemsResource.IMAGES_PRIMARY_LARGE,
        models.SearchItemsResource.OFFERS_LISTINGS_PRICE,
        models.SearchItemsResource.DETAIL_PAGE_URL,
    ]

    for locale, config in LOCALES_CONFIG.items():
        print(f"--- Fetching data for locale: {locale.upper()} ---")
        try:
            api = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, config['tag'], locale)
            locale_ssds = []
            
            # --- NEW: The search request now includes the BrowseNodeId ---
            search_request = models.SearchItemsRequest(
                keywords=SEARCH_KEYWORD,
                resources=search_resources,
                browse_node_id=config['node'] if config['node'] else None,
                item_count=10, # API max is 10 per page
                # You can experiment with sorting. 'Relevance' is a good start.
                # Other options: models.SortBy.PRICE_LOW_TO_HIGH, models.SortBy.FEATURED
                sort_by=models.SortBy.RELEVANCE 
            )
            response = api.search_items(search_request)

            if response.search_result and response.search_result.items:
                for product in response.search_result.items:
                    if not (product.offers and product.offers.listings and product.offers.listings[0].price):
                        continue

                    title = product.item_info.title.display_value
                    capacity_gb = parse_capacity_from_title(title)
                    
                    if capacity_gb == 0: continue # Skip if we can't determine capacity

                    price = product.offers.listings[0].price.amount
                    currency = product.offers.listings[0].price.currency
                    url = product.detail_page_url
                    image_url = product.images.primary.large.url if product.images and product.images.primary else ""
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
        
        except Exception as e:
            print(f"  [ERROR] Could not fetch data for {locale.upper()}: {e}")
            all_ssd_data[locale] = []
            continue
        
        all_ssd_data[locale] = locale_ssds

    # Write the combined data to a single JSON file
    with open('ssd_prices.json', 'w', encoding='utf-8') as f:
        json.dump(all_ssd_data, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Successfully created ssd_prices.json")

if __name__ == "__main__":
    generate_ssd_json()