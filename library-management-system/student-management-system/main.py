import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# --- APPLICATION CLASS ---
class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("850x550")
        self.root.configure(bg="#0f172a")

        # Variables
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.course_var = tk.StringVar()
        self.selected_db_id = None

        # Title Header
        title = tk.Label(
            self.root, 
            text="Student Management System", 
            font=("Helvetica", 20, "bold"), 
            bg="#1e293b", 
            fg="#f8fafc", 
            pady=12
        )
        title.pack(fill=tk.X)

        # Main Layout Container
        main_frame = tk.Frame(self.root, bg="#0f172a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Form Frame
        form_frame = tk.LabelFrame(
            main_frame, 
            text=" Student Details ", 
            font=("Helvetica", 12, "bold"), 
            bg="#1e293b", 
            fg="#38bdf8", 
            padx=15, 
            pady=15
        )
        form_frame.place(x=10, y=10, width=320, height=430)

        # Form Inputs
        tk.Label(form_frame, text="Student ID:", bg="#1e293b", fg="#f8fafc", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", pady=8)
        tk.Entry(form_frame, textvariable=self.id_var, font=("Helvetica", 10), width=22).grid(row=0, column=1, pady=8)

        tk.Label(form_frame, text="Full Name:", bg="#1e293b", fg="#f8fafc", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=8)
        tk.Entry(form_frame, textvariable=self.name_var, font=("Helvetica", 10), width=22).grid(row=1, column=1, pady=8)

        tk.Label(form_frame, text="Email Address:", bg="#1e293b", fg="#f8fafc", font=("Helvetica", 10)).grid(row=2, column=0, sticky="w", pady=8)
        tk.Entry(form_frame, textvariable=self.email_var, font=("Helvetica", 10), width=22).grid(row=2, column=1, pady=8)

        tk.Label(form_frame, text="Course:", bg="#1e293b", fg="#f8fafc", font=("Helvetica", 10)).grid(row=3, column=0, sticky="w", pady=8)
        tk.Entry(form_frame, textvariable=self.course_var, font=("Helvetica", 10), width=22).grid(row=3, column=1, pady=8)

        # Action Buttons Frame
        btn_frame = tk.Frame(form_frame, bg="#1e293b")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=25)

        tk.Button(btn_frame, text="Add Record", command=self.add_student, bg="#10b981", fg="white", font=("Helvetica", 10, "bold"), width=12).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Update Details", command=self.update_student, bg="#0284c7", fg="white", font=("Helvetica", 10, "bold"), width=12).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="Delete Record", command=self.delete_student, bg="#ef4444", fg="white", font=("Helvetica", 10, "bold"), width=12).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Clear Form", command=self.clear_form, bg="#64748b", fg="white", font=("Helvetica", 10, "bold"), width=12).grid(row=1, column=1, padx=5, pady=5)

        # Right Data View Frame (Table)
        display_frame = tk.Frame(main_frame, bg="#1e293b")
        display_frame.place(x=350, y=10, width=460, height=430)

        # Treeview Scrollbar
        scroll_y = tk.Scrollbar(display_frame, orient=tk.VERTICAL)
        
        self.student_table = ttk.Treeview(
            display_frame, 
            columns=("db_id", "student_id", "name", "email", "course"), 
            yscrollcommand=scroll_y.set
        )
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_y.config(command=self.student_table.yview)

        # Configure Table Columns
        self.student_table.heading("student_id", text="Student ID")
        self.student_table.heading("name", text="Name")
        self.student_table.heading("email", text="Email")
        self.student_table.heading("course", text="Course")
        
        self.student_table["show"] = "headings"
        self.student_table.column("student_id", width=80)
        self.student_table.column("name", width=120)
        self.student_table.column("email", width=140)
        self.student_table.column("course", width=100)

        self.student_table.pack(fill=tk.BOTH, expand=True)
        self.student_table.bind("<ButtonRelease-1>", self.get_selected_row)

        # Load Existing Records
        self.fetch_all_records()

    # --- CRUD FUNCTIONS ---

    # 1. CREATE / ADD RECORD
    def add_student(self):
        if not self.id_var.get() or not self.name_var.get() or not self.email_var.get() or not self.course_var.get():
            messagebox.showerror("Validation Error", "All fields are required!")
            return

        try:
            conn = sqlite3.connect("students.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO students (student_id, name, email, course) VALUES (?, ?, ?, ?)",
                (self.id_var.get(), self.name_var.get(), self.email_var.get(), self.course_var.get())
            )
            conn.commit()
            conn.close()
            self.fetch_all_records()
            self.clear_form()
            messagebox.showinfo("Success", "Student record added successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Database Error", "Student ID already exists!")

    # 2. READ / DISPLAY RECORDS
    def fetch_all_records(self):
        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, student_id, name, email, course FROM students")
        rows = cursor.fetchall()
        
        self.student_table.delete(*self.student_table.get_children())
        for row in rows:
            self.student_table.insert("", tk.END, values=row)
        
        conn.close()

    # SELECT ROW FROM TABLE
    def get_selected_row(self, event):
        cursor_row = self.student_table.focus()
        content = self.student_table.item(cursor_row)
        row = content["values"]
        
        if row:
            self.selected_db_id = row[0]
            self.id_var.set(row[1])
            self.name_var.set(row[2])
            self.email_var.set(row[3])
            self.course_var.set(row[4])

    # 3. UPDATE RECORD
    def update_student(self):
        if not self.selected_db_id:
            messagebox.showwarning("Selection Error", "Please select a record from the table to update.")
            return

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET student_id=?, name=?, email=?, course=? WHERE id=?",
            (self.id_var.get(), self.name_var.get(), self.email_var.get(), self.course_var.get(), self.selected_db_id)
        )
        conn.commit()
        conn.close()
        self.fetch_all_records()
        self.clear_form()
        messagebox.showinfo("Success", "Student details updated successfully!")

    # 4. DELETE RECORD
    def delete_student(self):
        if not self.selected_db_id:
            messagebox.showwarning("Selection Error", "Please select a record from the table to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
        if confirm:
            conn = sqlite3.connect("students.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id=?", (self.selected_db_id,))
            conn.commit()
            conn.close()
            self.fetch_all_records()
            self.clear_form()
            messagebox.showinfo("Success", "Student record deleted successfully!")

    # RESET FORM
    def clear_form(self):
        self.selected_db_id = None
        self.id_var.set("")
        self.name_var.set("")
        self.email_var.set("")
        self.course_var.set("")

# --- RUN APPLICATION ---
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = StudentManagementApp(root)
    root.mainloop()