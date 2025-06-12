import os
import json
from python_amazon_paapi import AmazonAPI  # Official package import
# --- Configuration Section ---
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")

# ... (rest of your config remains the same) ...

def generate_ssd_json():
    all_ssd_data = {}

    for locale, config in LOCALES_CONFIG.items():
        print(f"--- Testing data fetch for locale: {locale.upper()} ---")
        try:
            # Initialize AmazonAPI with the correct parameters
            api = AmazonAPI(
                AMAZON_ACCESS_KEY,
                AMAZON_SECRET_KEY,
                config['tag'],
                locale.upper()
            )
            
            # Search for products (slightly different syntax)
            products = api.search_items(
                keywords=SEARCH_KEYWORD,
                browse_node_id=config['node'],
                item_count=10
            )

            locale_ssds = []
            if products and hasattr(products, 'items'):
                for product in products.items:
                    if not product.offers: continue
                    title = product.item_info.title.display_value
                    capacity_gb = parse_capacity_from_title(title)
                    if capacity_gb == 0: continue
                    price = product.offers.listings[0].price.amount
                    currency = product.offers.listings[0].price.currency
                    url = product.detail_page_url
                    image_url = product.images.primary.large.url if product.images.primary else ""
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
            print(f"  [ERROR] The API call failed for {locale.upper()}. Reason: {e}")
            all_ssd_data[locale] = []
            continue

    with open('ssd_prices.json', 'w', encoding='utf-8') as f:
        json.dump(all_ssd_data, f, indent=2, ensure_ascii=False)

    print("\n✅ Test finished. ssd_prices.json created.")

if __name__ == "__main__":
    generate_ssd_json()
