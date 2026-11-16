
import requests 
import openpyxl
import re 
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import time # lets us pause the script for a few seconds to avoid overloading the server
import re # Lets us use regular expressions to extract numbers from strings

BASE_URL= "https://books.toscrape.com/" #This is the page we want to scrape
SOURCE_CURRENCY= "GBP" # This is the currency of the prices on the page we are scraping


headers = {
    "user-agent": "Educational book-scraper/1.0"
}
        
Feedback=requests.get(BASE_URL, headers=headers,timeout=5)

BeautifulSoup(Feedback.content, "html.parser")
Soup = BeautifulSoup(Feedback.content, "html.parser")


#Networking and fetching the page content
def fetch(BASE_URL: str) -> requests.Response | None: ##"""Fetch the content of a URL, returning the response or None on failure."""
    try:
        Feedback = requests.get(
            BASE_URL, 
            headers=headers, 
            timeout=5
            )
        
        Feedback.raise_for_status()
        
        print("Website connection successful!")
        print("Status Code:", Feedback.status_code)
        
        return Feedback
    
    except requests.RequestException as e:
        print(f"[!] Error fetching {BASE_URL}: {e}")
        return None
    
##
if __name__ == "__main__":
    response = fetch(BASE_URL)

    if response:
        soup = BeautifulSoup(response.content, "html.parser")
        print("Website HTML downloaded successfully!")
    
#Cleaning the data on prices and converting them to float values

def clean_price(raw: str) -> float | None:
    """'Â£51.77' / '£51.77' -> 51.77 (strips currency symbols and stray characters)."""
    match = re.search(r"\d+(?:[.,]\d+)?", raw.replace(",", ""))
    return float(match.group()) if match else None

# Testing the clean_price function
if __name__ == "__main__":

    test_price = "£51.77"

    cleaned = clean_price(test_price)

    print("Original Price:", test_price)
    print("Cleaned Price:", cleaned)

def scrape_books(min_items: int = 10, max_pages: int = 50) -> list[dict]:
    """Scrape pages until at least `min_items` books are collected."""
    books: list[dict] = []
    for page in range(1, max_pages + 1):
        if len(books) >= min_items:
            break
        resp = fetch(BASE_URL.format(page))
        if resp is None:
            print(f"[!] Skipping page {page}.")
            break
        resp.encoding = "utf-8"  # avoids the 'Â£' mojibake
        soup = BeautifulSoup(resp.text, "html.parser")

        for item in soup.select("article.product_pod"):
            title = item.h3.a["title"].strip()
            price = clean_price(item.select_one("p.price_color").get_text(strip=True))
            if title and price is not None:
                books.append({"title": title, f"price_{SOURCE_CURRENCY}": price})
        print(f"[+] Page {page}: {len(books)} books collected so far")

    return books[:min_items] if min_items else books

# Testing the book scraping function
if __name__ == "__main__":

    books = scrape_books(min_items=10)

    print("\n===== SCRAPED BOOKS =====")

    for book in books:
        print(book)

    print("\nTotal books scraped:", len(books))


##getting currency conversion rates from the API-"""Get the conversion rate from `source_currency` to `target_currency`."""
def get_conversion_rate(
    source_currency: str, 
    target_currency: str
    ) -> float | None:
    
    
    url = f"https://open.er-api.com/v6/latest/{source_currency}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        return data["rates"].get(target_currency)
    
    except (requests.RequestException, KeyError) as e:
        print(f"[!] Error fetching conversion rate: {e}")
        return None
    
# Testing currency conversion rate

if __name__ == "__main__":

    rate = get_conversion_rate("GBP", "KES")

    if rate is not None:

        print("\n===== CURRENCY CONVERSION =====")

        print("Source Currency: GBP")
        print("Target Currency: KES")
        print("Exchange Rate:", rate)

    else:
        print("Unable to retrieve exchange rate.")
    
### main 
def main():
    books = scrape_books(min_items=10, max_pages=50)
    
    if not books:
        print("[!] No books were scraped.Check your internet connection and try again.")
        return
    
##Reuqesting the user to input the target currency for conversion
    
    target_currency = input(
        "Enter the target currency (e.g., KES, EUR, USD): "
        ).strip().upper()
    
    if not target_currency:
        print("[!] Please enter a currency code.")
        return
    
##Getting the exhange rate for the target currency and converting the prices of the books to the target currency
    
    conversion_rate = get_conversion_rate(
        SOURCE_CURRENCY, 
        target_currency
        )
    
    if conversion_rate is None:
        print(f"[!] Could not retrieve conversion rate for {target_currency}.")
        return
    
    print(f"\n[+] Exchange rate: 1 {SOURCE_CURRENCY} = "
          f"{conversion_rate} {target_currency}")

##Converting the prices of the books to the target currency and rounding them to 2 decimal places
    
    for book in books:
        price_in_target = book[f"price_{SOURCE_CURRENCY}"] * conversion_rate
        
        book[f"price_{target_currency}"] = round(price_in_target, 2)

## Creating a DataFrame using pandas
    
    df = pd.DataFrame(books)
  
    
## Display the DataFrame in a tabular format using tabulate
    from tabulate import tabulate
    print(tabulate(df, 
           headers='keys', 
           tablefmt='grid', 
           showindex=False
           ))

    output_file = Path("scraped_books.xlsx")
    df.to_excel(output_file, index=False)
    print(f"\n[+] Data saved to {output_file.resolve()}")
    
# Run the main program
if __name__ == "__main__":
    main()

    
                

  