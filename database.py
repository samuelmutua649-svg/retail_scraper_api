import sqlite3
import re
import os

# Resolves retail_data.db path relative to this file's directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retail_data.db")

def init_db():
    """Initializes SQLite database tables and enables WAL mode."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable Write-Ahead Logging for concurrent database operations
    cursor.execute("PRAGMA journal_mode=WAL;")

    # Master products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            store TEXT NOT NULL,
            product_url TEXT UNIQUE
        )
    """)

    # Price history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price REAL NOT NULL,
            scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    conn.commit()
    conn.close()

def clean_price(price_raw):
    """
    Strips non-digit characters, isolates the primary price block,
    and filters out corrupted outlier values (> KSh 1,000,000).
    """
    if not price_raw:
        return 0

    # Extract the first numerical block while ignoring commas and discounts
    match = re.search(r'\d+', str(price_raw).replace(',', ''))
    if match:
        val = int(match.group(0))
        # Cap unreasonable or corrupted values
        if val > 1000000:
            return 0
        return val
    return 0

def save_product(title, price_raw, store, product_url):
    """
    Inserts or updates a product record and appends a clean price entry to price_history.
    """
    init_db()
    
    cleaned_price = clean_price(price_raw)
    
    # Skip saving if price cleaning resulted in an invalid/zero reading
    if cleaned_price <= 0:
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Upsert: Insert product or keep existing record URL
        cursor.execute("""
            INSERT INTO products (title, store, product_url)
            VALUES (?, ?, ?)
            ON CONFLICT(product_url) DO UPDATE SET title=excluded.title
        """, (title, store, product_url))

        # Fetch product ID
        cursor.execute("SELECT id FROM products WHERE product_url = ?", (product_url,))
        product_row = cursor.fetchone()

        if product_row:
            product_id = product_row[0]
            # Log clean price entry in history
            cursor.execute("""
                INSERT INTO price_history (product_id, price)
                VALUES (?, ?)
            """, (product_id, cleaned_price))

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    init_db()
    print(f"✅ Database initialized successfully at: {DB_PATH}")