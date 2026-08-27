import asyncio
from database import init_db
from scraper import scrape_jumia
import logging

# Configure logging to track background tasks and errors

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("tracker.log"),
        logging.StreamHandler()
    ]
)

INTERVAL = 60 * 60  # 1 hour in seconds

async def periodic_scrape():
    print("initializing database...")
    init_db()
    print ("🤖 Starting tracker process...")
    while True:
        try:
            logging.info("Starting a new scraping cycle...")
            await scrape_jumia()
            logging.info("Scraping cycle completed successfully.")
        except Exception as e:
            logging.error(f"Error during scraping: {e}")
            logging.info("sleeping for the next cycle despite the error...")


        await asyncio.sleep(INTERVAL)

def main():
    try:
        asyncio.run(periodic_scrape())
    except KeyboardInterrupt:
        print("\n🛑 Tracker process stopped manually.")

if __name__ == "__main__":
    main()  