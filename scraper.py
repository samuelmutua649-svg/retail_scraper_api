import sys
import json
from bs4 import BeautifulSoup
from curl_cffi import requests

def scrape_jumia_http(query):
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

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.select("article.prd")

            for prod in products:
                name_el = prod.select_one(".name")
                price_el = prod.select_one(".prc")

                if name_el and price_el:
                    scraped.append({
                        "title": name_el.get_text(strip=True),
                        "price": price_el.get_text(strip=True)
                    })
    except Exception as e:
        print(f"Error fetching Jumia: {e}", file=sys.stderr)

    return scraped

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "laptop"
    results = scrape_jumia_http(query)
    print(json.dumps(results))