import sys
import json
import asyncio
import logging
from fake_useragent import UserAgent
from playwright.async_api import async_playwright
from database import save_product

logging.basicConfig(level=logging.ERROR)
ua = UserAgent()

async def scrape_jumia(page, query):
    target_url = f"https://www.jumia.co.ke/catalog/?q={query.replace(' ', '+')}"
    scraped = []
    
    try:
        # 1. Set realistic User-Agent to bypass headless bot detection
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        })

        await page.goto(target_url, wait_until="domcontentloaded", timeout=25000)
        print(f"DEBUG PAGE TITLE: {await page.title()}", file=sys.stderr)

        # 2. Update selector wait to include flexible product card wrappers
        await page.wait_for_selector("article.prd, article.c-prd, div.-paxs article", timeout=10000)
        
        # 3. Query all product cards using current Jumia selectors
        products = await page.query_selector_all("article.prd, article.c-prd, div.-paxs article")

        for item in products[:10]:
            try:
                # Target name, price, and anchor elements
                title_elem = await item.query_selector(".name, h3.name, .info .name")
                price_elem = await item.query_selector(".prc, .info .prc")
                link_elem = await item.query_selector("a.core, a[href]")

                if title_elem and price_elem and link_elem:
                    title = (await title_elem.inner_text()).strip()
                    
                    # Direct inner_text extraction for cleaner price parsing
                    price_text = await price_elem.inner_text()
                    price_raw = price_text.split("\n")[0].strip() if price_text else ""

                    link = await link_elem.get_attribute("href")
                    if link and not link.startswith("http"):
                        link = f"https://www.jumia.co.ke{link}"

                    if title and price_raw:
                        save_product(title, price_raw, "Jumia", link)
                        scraped.append({
                            "title": title, 
                            "price": price_raw, 
                            "store": "Jumia", 
                            "link": link
                        })
            except Exception as e:
                continue

    except Exception as e:
        print(f"Jumia scrape error: {e}", file=sys.stderr)

    return scraped

async def scrape_kilimall(page, query):
    target_url = f"https://www.kilimall.co.ke/new/goods/search?q={query.replace(' ', '%20')}"
    scraped = []
    try:
        # Navigate and wait for DOM load
        await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        
        # Scroll down to trigger image and list lazy-loading
        await page.evaluate("window.scrollTo(0, 500)")
        await asyncio.sleep(2)  # Give SPA time to render items

        # Query all potential card elements
        products = await page.query_selector_all(".goods-item, div[class*='goods-item']")

        for item in products[:10]:
            try:
                title_elem = await item.query_selector(".goods-title, div[class*='title']")
                price_elem = await item.query_selector(".goods-price, div[class*='price']")
                link_elem = await item.query_selector("a")

                if title_elem and price_elem:
                    title = (await title_elem.inner_text()).strip()
                    price_raw = (await price_elem.inner_text()).strip()
                    
                    link = target_url
                    if link_elem:
                        href = await link_elem.get_attribute("href")
                        if href:
                            link = href if href.startswith("http") else f"https://www.kilimall.co.ke{href}"

                    # Clean price & persist to SQLite
                    save_product(title, price_raw, "Kilimall", link)
                    scraped.append({"title": title, "price": price_raw, "store": "Kilimall", "link": link})
            except Exception:
                continue
    except Exception as e:
        print(f"Kilimall error: {e}", file=sys.stderr)

    return scraped
async def main():
    search_query = sys.argv[1] if len(sys.argv) > 1 else "laptop"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu",
                "--window-size=1280,800"
            ]
        )                                  
        context = await browser.new_context(
            user_agent=ua.random, 
            viewport={"width": 1280, "height": 800},
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
            })
        
        # Open two tabs for concurrent scraping
        page_jumia = await context.new_page()
        page_kilimall = await context.new_page()

        # Hide navigator.webdriver flag
        await page_jumia.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        await page_kilimall.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        jumia_results, kilimall_results = await asyncio.gather(
            scrape_jumia(page_jumia, search_query),
            scrape_kilimall(page_kilimall, search_query)
        )

        await browser.close()

    total_scraped = jumia_results + kilimall_results
    print(json.dumps(total_scraped))
    sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())