import sqlite3
from datetime import datetime

# ==========================================
# STEP 3: DATABASE SETUP & CONNECTION
# ==========================================
def init_database():
    """Initializes the SQLite database and creates necessary tables."""
    conn = sqlite3.connect('library_system.db')
    cursor = conn.cursor()
    
    # Table for storing books
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            status TEXT DEFAULT 'Available'
        )
    ''')
    
    # Table for tracking issue and return transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            borrower_name TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# ==========================================
# STEP 1: BOOK MANAGEMENT MODULES
# ==========================================
def add_book():
    """Allows admin/user to add a new book to the library."""
    print("\n--- Add New Book ---")
    title = input("Enter book title: ").strip()
    author = input("Enter author name: ").strip()
    
    if not title or not author:
        print("Error: Title and Author cannot be empty!")
        return

    conn = sqlite3.connect('library_system.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, status) VALUES (?, ?, 'Available')", (title, author))
    conn.commit()
    conn.close()
    print(f"Success! '{title}' has been added to the library.")

def view_books():
    """Displays all books currently registered in the library system."""
    conn = sqlite3.connect('library_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()

    print("\n--- Library Book Inventory ---")
    if not books:
        print("No books found in the system.")
        return

    print(f"{'ID':<5} | {'Title':<25} | {'Author':<20} | {'Status':<10}")
    print("-" * 68)
    for book in books:
        print(f"{book[0]:<5} | {book[1]:<25} | {book[2]:<20} | {book[3]:<10}")

def search_books():
    """Allows searching books by title or author."""
    keyword = input("\nEnter book title or author keyword to search: ").strip()
    
    conn = sqlite3.connect('library_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", ('%' + keyword + '%', '%' + keyword + '%'))
    books = cursor.fetchall()
    conn.close()

    print(f"\n--- Search Results for '{keyword}' ---")
    if not books:
        print("No matching books found.")
        return

    print(f"{'ID':<5} | {'Title':<25} | {'Author':<20} | {'Status':<10}")
    print("-" * 68)
    for book in books:
        print(f"{book[0]:<5} | {book[1]:<25} | {book[2]:<20} | {book[3]:<10}")

# ==========================================
# STEP 2: ISSUE & RETURN FUNCTIONALITY
# ==========================================
def issue_book():
    """Issues an available book to a borrower."""
    view_books()
    try:
        book_id = int(input("\nEnter Book ID to issue: "))
    except ValueError:
        print("Invalid input. Please enter a numeric Book ID.")
        return

    conn = sqlite3.connect('library_system.db')
    cursor = conn.cursor()
    
    # Check if book exists and is available
    cursor.execute("SELECT status, title FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    
    if not book:
        print("Error: Book ID not found.")
        conn.close()
        return
    
    if book[0] == 'Issued':
        print(f"Sorry, '{book[1]}' is already issued out!")
        conn.close()
        return

    borrower = input("Enter borrower's name: ").strip()
    if not borrower:
        print("Borrower name cannot be empty.")
        conn.close()
        return

    issue_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Update book status and record transaction
    cursor.execute("UPDATE books SET status = 'Issued' WHERE id = ?", (book_id,))
    cursor.execute("INSERT INTO transactions (book_id, borrower_name, issue_date) VALUES (?, ?, ?)", 
                   (book_id, borrower, issue_date))
    
    conn.commit()
    conn.close()
    print(f"Success! '{book[1]}' has been issued to {borrower}.")

def return_book():
    """Handles the return process of an issued book."""
    conn = sqlite3.connect('library_system.db')
    cursor = conn.cursor()
    
    # Show currently issued books
    cursor.execute("SELECT b.id, b.title, t.borrower_name, t.issue_date FROM books b JOIN transactions t ON b.id = t.book_id WHERE b.status = 'Issued' AND t.return_date IS NULL")
    issued_books = cursor.fetchall()
    
    if not issued_books:
        print("\nNo books are currently issued out.")
        conn.close()
        return

    print("\n--- Currently Issued Books ---")
    print(f"{'ID':<5} | {'Title':<25} | {'Borrower':<15} | {'Issue Date':<16}")
    print("-" * 68)
    for item in issued_books:
        print(f"{item[0]:<5} | {item[1]:<25} | {item[2]:<15} | {item[3]:<16}")

    try:
        book_id = int(input("\nEnter Book ID to return: "))
    except ValueError:
        print("Invalid input.")
        conn.close()
        return

    return_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Update book status to Available and update transaction record
    cursor.execute("UPDATE books SET status = 'Available' WHERE id = ?", (book_id,))
    cursor.execute("UPDATE transactions SET return_date = ? WHERE book_id = ? AND return_date IS NULL", 
                   (return_date, book_id))
    
    conn.commit()
    conn.close()
    print("Success! Book has been returned and marked as Available.")

# ==========================================
# STEP 4: GENERATE REPORTS
# ==========================================
def generate_reports():
    """Generates a summary report of library statistics and transaction logs."""
    conn = sqlite3.connect('library_system.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM books WHERE status = 'Available'")
    available_books = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM books WHERE status = 'Issued'")
    issued_books = cursor.fetchone()[0]
    
    print("\n========================================")
    print("        LIBRARY MANAGEMENT REPORT       ")
    print("========================================")
    print(f" Total Books in Library : {total_books}")
    print(f" Available for Issue    : {available_books}")
    print(f" Currently Issued Out   : {issued_books}")
    print("----------------------------------------")
    
    # Transaction History Log
    cursor.execute('''
        SELECT t.id, b.title, t.borrower_name, t.issue_date, 
               CASE WHEN t.return_date IS NULL THEN 'Not Returned' ELSE t.return_date END 
        FROM transactions t JOIN books b ON t.book_id = b.id
    ''')
    logs = cursor.fetchall()
    
    print("\n--- Complete Transaction History ---")
    if not logs:
        print("No transactions recorded yet.")
    else:
        print(f"{'Tx ID':<6} | {'Book Title':<20} | {'Borrower':<12} | {'Issue Date':<16} | {'Return Status':<15}")
        print("-" * 75)
        for log in logs:
            print(f"{log[0]:<6} | {log[1]:<20} | {log[2]:<12} | {log[3]:<16} | {log[4]:<15}")
    print("========================================\n")
    conn.close()

# ==========================================
# STEP 5: MAIN MENU & SYSTEM VALIDATION LOOP
# ==========================================
def main():
    init_database()
    while True:
        print("\n=== LIBRARY MANAGEMENT SYSTEM ===")
        print("1. Add New Book")
        print("2. View All Books")
        print("3. Search Books")
        print("4. Issue Book")
        print("5. Return Book")
        print("6. Generate Reports")
        print("7. Exit")
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == '1':
            add_book()
        elif choice == '2':
            view_books()
        elif choice == '3':
            search_books()
        elif choice == '4':
            issue_book()
        elif choice == '5':
            return_book()
        elif choice == '6':
            generate_reports()
        elif choice == '7':
            print("\nExiting system. Goodbye!")
            break
        else:
            print("Invalid option! Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()