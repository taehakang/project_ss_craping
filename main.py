import csv
import time
import datetime
import os
from scraper_utils import get_category_urls, get_product_links_from_category, extract_product_details

def main():
    print("Starting Samsung Italy Product Scraper...")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_file = "samsung_it_products.csv"
    
    # 1. Get Category URLs (excluding smartphones)
    print("Fetching categories...")
    categories = get_category_urls()
    print(f"Found {len(categories)} categories (smartphones excluded).")
    
    all_variants = []
    visited_pdp_urls = set()
    
    # Check existing data to avoid redownloading? No, user wants a fresh scrape.
    
    for cat_name, cat_url in categories.items():
        print(f"\nProcessing Category: {cat_name} ({cat_url})")
        
        # 2. Get Product Links from Category
        product_links = get_product_links_from_category(cat_url)
        print(f"  Found {len(product_links)} products in category.")
        
        for p in product_links:
            pdp_url = p['url']
            display_name = p['name']
            
            if pdp_url in visited_pdp_urls:
                continue
            
            print(f"  Scraping: {display_name} ...")
            variants = extract_product_details(pdp_url, display_name)
            
            for v in variants:
                print(f"  - Model: {v['ModelCode']}")
                print(f"    Name: {v['Name']}")
                print(f"    Tax: {v['TaxPrice']} | List: {v['ListPrice']} | Sale: {v['SalePrice']}")
                print(f"    Stock: {v['InStock']}")
                # Add timestamp
                v['Timestamp'] = timestamp
                all_variants.append(v)
                visited_pdp_urls.add(v['Url'])
            
            # Rate limiting / Polite crawling
            time.sleep(1)

    # 3. Save to CSV
    if all_variants:
        # Column Order: Timestamp, Name, ModelCode, TaxPrice, ListPrice, SalePrice, InStock, Url
        csv_headers = ["Timestamp", "Name", "ModelCode", "TaxPrice", "ListPrice", "SalePrice", "InStock", "Url"]
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers)
            writer.writeheader()
            for row in all_variants:
                writer.writerow({k: row.get(k, "") for k in csv_headers})
        
        print(f"\nScraping complete. {len(all_variants)} items saved to {output_file}.")
    else:
        print("\nNo products collected.")

if __name__ == "__main__":
    main()
