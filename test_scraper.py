from scraper_utils import get_category_urls, get_product_links_from_category, extract_product_details
import random
import time

def test_random_samples():
    print("Starting Randomized Scraper Test...")
    categories = get_category_urls()
    
    results = []
    for cat_name, cat_url in categories.items():
        print(f"\nCategory: {cat_name} ({cat_url})")
        
        # 1. Fetch product links
        product_links = get_product_links_from_category(cat_url)
        if not product_links:
            print(f"  No products found in {cat_name}.")
            continue
            
        # 2. Pick one random product
        sample_prod = random.choice(product_links)
        pdp_url = sample_prod['url']
        display_name = sample_prod['name']
        
        print(f"  Random Sample: {display_name} ({pdp_url})")
        
        # 3. Extract details
        try:
            variants = extract_product_details(pdp_url, display_name)
            if not variants:
                print("    Failed to extract details.")
                continue
                
            for v in variants:
                print(f"    - Model: {v['ModelCode']}")
                print(f"      Tax: {v['TaxPrice']} | List: {v['ListPrice']} | Sale: {v['SalePrice']}")
                print(f"      Stock: {v['InStock']}")
                results.append(v)
        except Exception as e:
            print(f"    Error during extraction: {e}")
            
    # Add a specific model mentioned by user to verify RRP null logic
    user_model_url = "https://www.samsung.com/it/computers/galaxy-book/galaxy-book4-pro-14-inch-ultra-7-16gb-512gb-np940xha-kg3it/"
    print(f"\nVerifying User's Specific Case: {user_model_url}")
    v_user = extract_product_details(user_model_url, "Galaxy Book4 Pro")
    for v in v_user:
        print(f"    - Model: {v['ModelCode']}")
        print(f"      Tax: '{v['TaxPrice']}' | List: '{v['ListPrice']}' | Sale: '{v['SalePrice']}'")
        print(f"      Stock: {v['InStock']}")

    print(f"\nRandomized test finished. Total {len(results)} items verified across {len(categories)} categories.")

if __name__ == "__main__":
    test_random_samples()
