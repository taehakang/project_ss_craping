## Samsung Italy Product Price Scraper

This project crawls the Samsung Italy website to extract product information, including prices and stock status, and saves it into a CSV file. It excludes smartphones and handles product variants like different TV sizes.

## Execution Guide

We provide two scripts for different purposes:

1.  **Main Execution (`main.py`)**: **Final Data Collection**
    *   **Role**: Iterates through the entire Samsung Italy website (excluding smartphones) to collect all product information.
    *   **Action**: Visits all categories, extracts product links, fetches detailed data (Model Code, TaxPrice, ListPrice, SalePrice, InStock, etc.) from each product page, and saves it to `samsung_it_products.csv`.
    *   **Usage**: Run this when you need the final, complete product price list.

2.  **Test Execution (`test_scraper.py`)**: **Logic Verification**
    *   **Role**: Quickly checks a few sampled URLs (e.g., TV, Refrigerator) instead of crawling the whole site.
    *   **Action**: Prints the extracted product details to the console to verify logic. It does **not** generate a CSV file.
    *   **Usage**: Run this to verify if the scraper is working correctly or if the website structure has changed (takes ~1 min).

## File Structure

- [main.py](file:///e:/Downloads/antigravity/project_ss_craping/main.py): The main entry point for the full scraping process.
- [test_scraper.py](file:///e:/Downloads/antigravity/project_ss_craping/test_scraper.py): A lightweight script to test the extraction logic on sample products.
- [scraper_utils.py](file:///e:/Downloads/antigravity/project_ss_craping/scraper_utils.py): Core utility functions for fetching categories (Tablets, TVs, Appliances, etc.), harvesting links, and extracting product details from HTML/JSON.
- [arc/](file:///e:/Downloads/antigravity/project_ss_craping/arc/): A directory containing temporary analysis scripts, HTML source samples, and discarded tools used during development.

## Installation & Usage

1.  **Install dependencies**:
    ```bash
    pip install requests beautifulsoup4
    ```

2.  **Run full scrape**:
    ```bash
    python main.py
    ```

3.  **Run test**:
    ```bash
    python test_scraper.py
    ```

## Data Fields (CSV)
The generated `samsung_it_products.csv` contains:
- **Timestamp**: Time of scraping.
- **Name**: Product display name.
- **ModelCode**: Unique identifier for the product model.
- **TaxPrice**: Base price from taxPrice field.
- **ListPrice**: Original price displayed on the site.
- **SalePrice**: Discounted promotion price.
- **InStock**: Availability status (True/False).
- **Url**: Direct link to the product page.