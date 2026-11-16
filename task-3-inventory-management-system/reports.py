from database import connect_db


def show_dashboard():
    """Calculates totals, category breakdowns, and low-stock warnings."""
    with connect_db() as conn:
        # Overall totals (COALESCE prevents None when the table is empty)
        totals = conn.execute("""
            SELECT 
                COUNT(*) AS product_count,
                COALESCE(SUM(quantity), 0) AS total_units,
                COALESCE(SUM(quantity * unit_price), 0.0) AS total_valuation
            FROM products
        """).fetchone()

        # Group stock value by category
        categories = conn.execute("""
            SELECT 
                category,
                COUNT(*) AS item_count,
                SUM(quantity) AS units,
                SUM(quantity * unit_price) AS cat_value
            FROM products
            GROUP BY category
            ORDER BY cat_value DESC
        """).fetchall()

        # Items at or below their reorder threshold
        alerts = conn.execute("""
            SELECT sku, name, quantity, reorder_level
            FROM products
            WHERE quantity <= reorder_level
            ORDER BY quantity ASC
        """).fetchall()

    print("\n==============================================")
    print("           INVENTORY SUMMARY DASHBOARD        ")
    print("==============================================")
    print(f"Unique Products : {totals['product_count']}")
    print(f"Total Units     : {totals['total_units']}")
    print(f"Total Value     : ${totals['total_valuation']:,.2f}")

    print("\n--- Category Breakdown ---")
    if not categories:
        print("  (No items recorded yet)")
    else:
        for cat in categories:
            print(
                f"  - {cat['category']}: {cat['item_count']} items | "
                f"{cat['units']} units | ${cat['cat_value']:,.2f}"
            )

    print("\n--- Restock Alerts ---")
    if not alerts:
        print("  All stock levels look good.")
    else:
        for item in alerts:
            print(
                f"  ! {item['name']} [{item['sku']}] -> "
                f"{item['quantity']} left (Reorder level: {item['reorder_level']})"
            )
    print("==============================================\n")