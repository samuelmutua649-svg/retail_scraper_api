import logging
import sqlite3
from database import init_db, save_product, get_connection

# Configure logging to display direct output in the terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def run_database_tests():
    logging.info("=== Starting Database Logic Verification ===")
    
    # 1. Initialize Tables
    init_db()
    
    # Define mock test data
    test_url = "https://www.jumia.co.ke/hp-elitebook-840-g3-laptop-1"
    test_title = "HP EliteBook 840 G3 - 8GB RAM - 256GB SSD"
    
    # 2. Test Case 1: Insert New Product
    logging.info("\n--- Test 1: Insert New Product ---")
    status = save_product(test_url, test_title, "KSh 28,500")
    assert status == "NEW", f"Expected 'NEW', got {status}"
    
    # 3. Test Case 2: Scrape Same Product with Unchanged Price
    logging.info("\n--- Test 2: Scrape Unchanged Price ---")
    status = save_product(test_url, test_title, "KSh 28,500")
    assert status == "UNCHANGED", f"Expected 'UNCHANGED', got {status}"
    
    # 4. Test Case 3: Detect Price Drop
    logging.info("\n--- Test 3: Detect Price Drop ---")
    status = save_product(test_url, test_title, "KSh 24,000")
    assert status == "PRICE_CHANGED", f"Expected 'PRICE_CHANGED', got {status}"

    # 5. Test Case 4: Verify Database State via Direct Query
    logging.info("\n--- Test 4: Verify Database Records ---")
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Query Products Table
        cursor.execute("SELECT id, title, current_price FROM products WHERE url = ?", (test_url,))
        product = cursor.fetchone()
        logging.info(f"Products Table Record: {product}")
        assert product[2] == 24000.0, f"Expected 24000.0, got {product[2]}"
        
        product_id = product[0]
        
        # Query Price History Table
        cursor.execute(
            "SELECT price, recorded_at FROM price_history WHERE product_id = ? ORDER BY id ASC", 
            (product_id,)
        )
        history = cursor.fetchall()
        logging.info(f"Price History Records for Product ID {product_id}:")
        for row in history:
            logging.info(f"  - Price: KSh {row[0]} | Recorded At: {row[1]}")
            
        # Assert History Integrity: Should contain exactly 2 entries (initial 28500.0 and updated 24000.0)
        assert len(history) == 2, f"Expected 2 history records, found {len(history)}"

    logging.info("\n=== All Database Tests Passed Successfully! ===")

if __name__ == "__main__":
    run_database_tests()