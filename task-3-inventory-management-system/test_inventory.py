import os
import unittest
import database
from inventory import add_new_product, adjust_stock, find_products


class TestInventorySystem(unittest.TestCase):
    """Tests core inventory rules to verify data accuracy."""

    def setUp(self):
        # Point the app to a temporary database so we don't touch real data
        database.DB_FILE = "temp_test_inventory.db"
        database.setup_database()

    def tearDown(self):
        # Clean up the temporary database after each test
        if os.path.exists("temp_test_inventory.db"):
            os.remove("temp_test_inventory.db")

    def test_duplicate_sku_blocked(self):
        added, _ = add_new_product("MON-01", "24-inch Monitor", "Displays", 8, 3, 180.0)
        self.assertTrue(added)

        # Adding the same SKU again (even lowercase) should fail
        duplicate, _ = add_new_product("mon-01", "Other Monitor", "Displays", 5, 2, 150.0)
        self.assertFalse(duplicate)

    def test_stock_adjustments_and_overdraft_protection(self):
        add_new_product("CAB-05", "USB-C Cable", "Accessories", 10, 4, 12.5)

        # Deducting 4 units should leave 6
        ok, _ = adjust_stock("CAB-05", -4)
        self.assertTrue(ok)

        # Trying to deduct 10 more when only 6 remain should be rejected
        blocked, _ = adjust_stock("CAB-05", -10)
        self.assertFalse(blocked)

        # Verify the database still shows 6 units
        item = find_products(search_term="CAB-05")[0]
        self.assertEqual(item["quantity"], 6)

    def test_low_stock_filter(self):
        add_new_product("PRN-01", "Laser Printer", "Office", 2, 5, 299.0)
        add_new_product("PAP-01", "A4 Paper Box", "Office", 20, 5, 35.0)

        low_items = find_products(only_low_stock=True)
        self.assertEqual(len(low_items), 1)
        self.assertEqual(low_items[0]["sku"], "PRN-01")


if __name__ == "__main__":
    unittest.main()