import sys
import json
import logging
from bs4 import BeautifulSoup
from curl_cffi import requests

# Silence debug logs so they don't pollute stdout JSON
logging.basicConfig(level=logging.ERROR)

def scrape_jumia(query):
    url = f"https://www.jumia.co.ke/catalog/?q={query.replace(' ', '+')}"
    scraped = []

    try:
        # Impersonate Chrome 120 TLS fingerprint
        response = requests.get(
            url,
            impersonate="chrome120",
            headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            timeout=15
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        page_title = soup.title.string.strip() if soup.title and soup.title.string else "No Title Found"
        
        print(f"[DEBUG] HTTP STATUS: {response.status_code}", file=sys.stderr)
        print(f"[DEBUG] RESPONSE LENGTH: {len(response.text)}", file=sys.stderr)
        print(f"[DEBUG] PAGE TITLE: {page_title}", file=sys.stderr)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.select("article.prd")

            for prod in products:
                name_el = prod.select_one(".name")
                price_el = prod.select_one(".prc")

                if name_el and price_el:
                    scraped.append({
                        "title": name_el.get_text(strip=True),
                        "price": price_el.get_text(strip=True),
                        "source": "Jumia"
                    })
        else:
            print(f"[SCRAPER ERROR]: Jumia returned HTTP status {response.status_code}", file=sys.stderr)

    except Exception as e:
        print(f"[SCRAPER ERROR]: Jumia scrape failed: {e}", file=sys.stderr)

    return scraped


def scrape_kilimall(query):
    url = f"https://www.kilimall.co.ke/new/goods-list?q={query.replace(' ', '+')}"
    scraped = []

    try:
        response = requests.get(
            url,
            impersonate="chrome120",
            headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            timeout=15
        )

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract Kilimall catalog elements
            products = soup.select(".goods-item, .product-item")

            for prod in products:
                name_el = prod.select_one(".goods-title, .product-title, .title")
                price_el = prod.select_one(".goods-price, .product-price, .price")

                if name_el and price_el:
                    scraped.append({
                        "title": name_el.get_text(strip=True),
                        "price": price_el.get_text(strip=True),
                        "source": "Kilimall"
                    })
        else:
            print(f"[SCRAPER ERROR]: Kilimall returned HTTP status {response.status_code}", file=sys.stderr)

    except Exception as e:
        print(f"[SCRAPER ERROR]: Kilimall scrape failed: {e}", file=sys.stderr)

    return scraped


def main():
    # Read search query passed from Fastify spawn argument
    search_query = sys.argv[1] if len(sys.argv) > 1 else "laptop"

    # Synchronous sequential execution
    jumia_results = scrape_jumia(search_query)
    kilimall_results = scrape_kilimall(search_query)

    total_scraped = jumia_results + kilimall_results

    # Output JSON string directly to stdout for Fastify
    print(json.dumps(total_scraped))
    sys.stdout.flush()


if __name__ == "__main__":
    main()