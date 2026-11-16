from database import setup_database
from inventory import add_new_product, adjust_stock, find_products
from reports import show_dashboard


def print_table(rows):
    """Formats product rows into a readable terminal table."""
    if not rows:
        print("\nNo matching items found.\n")
        return

    print(f"\n{'SKU':<12} {'Product Name':<22} {'Category':<15} {'Stock':<7} {'Price':<10}")
    print("-" * 70)
    for r in rows:
        print(
            f"{r['sku']:<12} {r['name']:<22} {r['category']:<15} "
            f"{r['quantity']:<7} ${r['unit_price']:<9.2f}"
        )
    print()


def run_app():
    # Ensure the SQLite table is ready before showing the menu
    setup_database()

    while True:
        print("=== Inventory Management Menu ===")
        print("1. Add a new product")
        print("2. Update stock (restock or sale)")
        print("3. Search and filter inventory")
        print("4. View inventory report & dashboard")
        print("5. Quit")

        choice = input("\nChoose an option (1-5): ").strip()

        if choice == "1":
            sku = input("Enter SKU (e.g. LAP-01): ")
            name = input("Enter product name: ")
            category = input("Enter category: ")
            try:
                qty = int(input("Starting quantity: "))
                reorder = int(input("Low-stock alert threshold: "))
                price = float(input("Unit price: "))
                _, message = add_new_product(sku, name, category, qty, reorder, price)
                print(f"\n{message}\n")
            except ValueError:
                print("\nInvalid input: quantity and price must be numbers.\n")

        elif choice == "2":
            sku = input("Enter product SKU: ")
            try:
                amount = int(input("Quantity change (e.g. 10 to add, -3 to deduct): "))
                _, message = adjust_stock(sku, amount)
                print(f"\n{message}\n")
            except ValueError:
                print("\nPlease enter a valid whole number.\n")

        elif choice == "3":
            term = input("Search by name or SKU (press Enter to skip): ")
            cat = input("Filter by category (press Enter to skip): ")
            low_only = input("Show low-stock items only? (y/n): ").strip().lower() == "y"

            matches = find_products(term, cat, low_only)
            print_table(matches)

        elif choice == "4":
            show_dashboard()

        elif choice == "5":
            print("Closing inventory system. Goodbye!")
            break
        else:
            print("\nInvalid option. Please pick a number between 1 and 5.\n")


if __name__ == "__main__":
    run_app()
    