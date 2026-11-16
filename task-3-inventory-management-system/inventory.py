import sqlite3
from database import connect_db

#sku - Stock Keeping Unit.
def add_new_product(sku, name, category, quantity, reorder_level, unit_price):
    """Registers a new item in the catalog. Returns (success_bool, message)."""
    # Clean up user input so 'abc-1' and ' ABC-1 ' don't create duplicate SKUs
    clean_sku = sku.strip().upper()
    clean_name = name.strip()
    clean_category = category.strip()

    if not clean_sku or not clean_name:
        return False, "SKU and product name cannot be empty."

    if quantity < 0 or unit_price < 0:
        return False, "Quantity and price must be zero or higher."

    try:
        with connect_db() as conn:
            conn.execute(
                """
                INSERT INTO products (sku, name, category, quantity, reorder_level, unit_price)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (clean_sku, clean_name, clean_category, quantity, reorder_level, unit_price),
            )
        return True, f"Saved '{clean_name}' (SKU: {clean_sku})."
    except sqlite3.IntegrityError:
        # Triggers if the UNIQUE constraint on SKU fails
        return False, f"SKU '{clean_sku}' is already in the system."


def adjust_stock(sku, change):
    """
    Updates stock levels for an existing product.
    Pass a positive number for new deliveries, or a negative number for sales/usage.
    """
    clean_sku = sku.strip().upper()

    with connect_db() as conn:
        row = conn.execute(
            "SELECT name, quantity FROM products WHERE sku = ?",
            (clean_sku,)
        ).fetchone()

        if row is None:
            return False, f"No product found with SKU '{clean_sku}'."

        updated_qty = row["quantity"] + change

        # Prevent stock from dropping below zero
        if updated_qty < 0:
            return False, (
                f"Not enough stock for {row['name']}. "
                f"Available: {row['quantity']}, Tried to remove: {abs(change)}."
            )

        conn.execute(
            "UPDATE products SET quantity = ? WHERE sku = ?",
            (updated_qty, clean_sku)
        )
        return True, f"{row['name']} updated: {row['quantity']} -> {updated_qty} units."


def find_products(search_term="", category_filter="", only_low_stock=False):
    """Searches products by name/SKU and optionally filters by category or low stock."""
    # Start with a base query and append filters dynamically
    sql = "SELECT * FROM products WHERE 1=1"
    values = []

    if search_term.strip():
        sql += " AND (name LIKE ? OR sku LIKE ?)"
        pattern = f"%{search_term.strip()}%"
        values.extend([pattern, pattern])

    if category_filter.strip():
        sql += " AND LOWER(category) = LOWER(?)"
        values.append(category_filter.strip())

    if only_low_stock:
        sql += " AND quantity <= reorder_level"

    sql += " ORDER BY name ASC"

    with connect_db() as conn:
        return conn.execute(sql, values).fetchall()
    