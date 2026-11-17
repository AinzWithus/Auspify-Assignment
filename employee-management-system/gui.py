import tkinter as tk
from tkinter import ttk, messagebox
from database import init_database, get_db
from employees import (
    add_department,
    list_departments,
    register_employee,
    update_employee,
    delete_employee,
    search_employees,
)


class EmployeeManagementGUI:
    """Desktop GUI for managing employees, departments, and reports."""

    def __init__(self, root):
        self.root = root
        self.root.title("Auspify - Employee Management System")
        self.root.geometry("950x620")
        self.root.configure(bg="#f4f6f9")

        # Initialize SQLite tables and indexes
        init_database()

        # Header banner
        header = tk.Frame(self.root, bg="#1e3a8a", height=55)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Employee Management & Organizational Portal",
            font=("Segoe UI", 15, "bold"),
            bg="#1e3a8a",
            fg="white",
        ).pack(pady=12)

        # Tabbed interface for clean screen separation
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self.emp_tab = tk.Frame(self.notebook, bg="#f4f6f9")
        self.dept_tab = tk.Frame(self.notebook, bg="#f4f6f9")
        self.report_tab = tk.Frame(self.notebook, bg="#f4f6f9")

        self.notebook.add(self.emp_tab, text="  Employees Directory  ")
        self.notebook.add(self.dept_tab, text="  Departments  ")
        self.notebook.add(self.report_tab, text="  Organizational Reports  ")

        self.build_employee_screen()
        self.build_department_screen()
        self.build_report_screen()

        # Load initial data into all screens
        self.refresh_all()

    # ---------------------------------------------------------
    # SCREEN 1: EMPLOYEE REGISTRATION, SEARCH, UPDATE & DELETE
    # ---------------------------------------------------------
    def build_employee_screen(self):
        # Left panel: Registration / Edit Form
        form_frame = tk.LabelFrame(
            self.emp_tab, text="Employee Details", font=("Segoe UI", 10, "bold"), bg="white", padx=12, pady=10
        )
        form_frame.pack(side="left", fill="y", padx=(0, 10), pady=5)

        fields = [
            ("Employee Code:", "code"),
            ("Full Name:", "name"),
            ("Email Address:", "email"),
            ("Role / Title:", "role"),
            ("Monthly Salary ($):", "salary"),
        ]
        self.emp_entries = {}

        for label_text, key in fields:
            tk.Label(form_frame, text=label_text, bg="white", anchor="w").pack(fill="x", pady=(6, 0))
            entry = tk.Entry(form_frame, width=28)
            entry.pack(fill="x", pady=(2, 4))
            self.emp_entries[key] = entry

        # Department dropdown
        tk.Label(form_frame, text="Department:", bg="white", anchor="w").pack(fill="x", pady=(6, 0))
        self.dept_combo = ttk.Combobox(form_frame, state="readonly", width=25)
        self.dept_combo.pack(fill="x", pady=(2, 4))

        # Status dropdown (used when updating)
        tk.Label(form_frame, text="Employment Status:", bg="white", anchor="w").pack(fill="x", pady=(6, 0))
        self.status_combo = ttk.Combobox(
            form_frame, values=["Active", "On Leave", "Resigned"], state="readonly", width=25
        )
        self.status_combo.set("Active")
        self.status_combo.pack(fill="x", pady=(2, 12))

        # Action Buttons
        btn_style = {"width": 24, "pady": 4, "font": ("Segoe UI", 9, "bold")}
        tk.Button(
            form_frame, text="Register New Employee", bg="#16a34a", fg="white", command=self.handle_register, **btn_style
        ).pack(pady=3)
        tk.Button(
            form_frame, text="Update Selected Employee", bg="#2563eb", fg="white", command=self.handle_update, **btn_style
        ).pack(pady=3)
        tk.Button(
            form_frame, text="Delete Selected Employee", bg="#dc2626", fg="white", command=self.handle_delete, **btn_style
        ).pack(pady=3)
        tk.Button(
            form_frame, text="Clear Form", bg="#6b7280", fg="white", command=self.clear_emp_form, **btn_style
        ).pack(pady=3)

        # Right panel: Search Bar + Table
        right_frame = tk.Frame(self.emp_tab, bg="#f4f6f9")
        right_frame.pack(side="right", fill="both", expand=True, pady=5)

        search_bar = tk.Frame(right_frame, bg="#f4f6f9")
        search_bar.pack(fill="x", pady=(0, 8))

        tk.Label(search_bar, text="Search:", bg="#f4f6f9", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_employee_table())
        tk.Entry(search_bar, textvariable=self.search_var, width=30).pack(side="left", padx=8)

        tk.Button(search_bar, text="Refresh", command=self.refresh_all).pack(side="right")

        # Employee Data Table
        columns = ("code", "name", "email", "dept", "role", "salary", "status")
        self.emp_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=18)

        headers = {
            "code": ("Code", 75),
            "name": ("Full Name", 130),
            "email": ("Email", 145),
            "dept": ("Department", 100),
            "role": ("Role", 110),
            "salary": ("Salary", 85),
            "status": ("Status", 75),
        }
        for col, (heading, width) in headers.items():
            self.emp_tree.heading(col, text=heading)
            self.emp_tree.column(col, width=width, anchor="w")

        self.emp_tree.pack(fill="both", expand=True)
        self.emp_tree.bind("<<TreeviewSelect>>", self.on_employee_select)

    # ---------------------------------------------------------
    # SCREEN 2: DEPARTMENT MANAGEMENT
    # ---------------------------------------------------------
    def build_department_screen(self):
        top_box = tk.LabelFrame(
            self.dept_tab, text="Add New Department", font=("Segoe UI", 10, "bold"), bg="white", padx=12, pady=10
        )
        top_box.pack(fill="x", padx=10, pady=10)

        tk.Label(top_box, text="Department Name:", bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.dept_name_entry = tk.Entry(top_box, width=25)
        self.dept_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top_box, text="Manager / Lead:", bg="white").grid(row=0, column=2, padx=5, pady=5)
        self.dept_mgr_entry = tk.Entry(top_box, width=25)
        self.dept_mgr_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(
            top_box,
            text="Create Department",
            bg="#1e3a8a",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=self.handle_add_department,
        ).grid(row=0, column=4, padx=12, pady=5)

        # Departments Table
        self.dept_tree = ttk.Treeview(self.dept_tab, columns=("id", "name", "manager"), show="headings", height=15)
        self.dept_tree.heading("id", text="ID")
        self.dept_tree.heading("name", text="Department Name")
        self.dept_tree.heading("manager", text="Department Manager")
        self.dept_tree.column("id", width=60)
        self.dept_tree.column("name", width=250)
        self.dept_tree.column("manager", width=250)
        self.dept_tree.pack(fill="both", expand=True, padx=10, pady=5)

    # ---------------------------------------------------------
    # SCREEN 3: ORGANIZATIONAL & PAYROLL REPORTS
    # ---------------------------------------------------------
    def build_report_screen(self):
        self.summary_label = tk.Label(
            self.report_tab,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#1e293b",
            justify="left",
            padx=15,
            pady=15,
            relief="groove",
        )
        self.summary_label.pack(fill="x", padx=10, pady=10)

        self.report_tree = ttk.Treeview(
            self.report_tab, columns=("dept", "manager", "headcount", "payroll"), show="headings", height=14
        )
        self.report_tree.heading("dept", text="Department")
        self.report_tree.heading("manager", text="Department Lead")
        self.report_tree.heading("headcount", text="Staff Count")
        self.report_tree.heading("payroll", text="Total Monthly Payroll")
        self.report_tree.pack(fill="both", expand=True, padx=10, pady=5)

    # ---------------------------------------------------------
    # EVENT HANDLERS & DATA SYNC
    # ---------------------------------------------------------
    def get_selected_dept_id(self):
        choice = self.dept_combo.get()
        if not choice or choice == "Unassigned":
            return None
        # Format in dropdown is "1 - Engineering"
        return int(choice.split(" - ")[0])

    def handle_register(self):
        try:
            salary = float(self.emp_entries["salary"].get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid numeric salary.")
            return

        ok, msg = register_employee(
            emp_code=self.emp_entries["code"].get(),
            full_name=self.emp_entries["name"].get(),
            email=self.emp_entries["email"].get(),
            role=self.emp_entries["role"].get(),
            salary=salary,
            department_id=self.get_selected_dept_id(),
        )
        if ok:
            messagebox.showinfo("Success", msg)
            self.clear_emp_form()
            self.refresh_all()
        else:
            messagebox.showerror("Error", msg)

    def handle_update(self):
        code = self.emp_entries["code"].get().strip()
        if not code:
            messagebox.showwarning("Missing Code", "Select an employee from the table or enter their code first.")
            return

        sal_text = self.emp_entries["salary"].get().strip()
        try:
            salary = float(sal_text) if sal_text else None
        except ValueError:
            messagebox.showerror("Invalid Input", "Salary must be a valid number.")
            return

        ok, msg = update_employee(
            emp_code=code,
            role=self.emp_entries["role"].get(),
            salary=salary,
            department_id=self.get_selected_dept_id(),
            status=self.status_combo.get(),
        )
        if ok:
            messagebox.showinfo("Updated", msg)
            self.refresh_all()
        else:
            messagebox.showerror("Error", msg)

    def handle_delete(self):
        code = self.emp_entries["code"].get().strip()
        if not code:
            messagebox.showwarning("Missing Code", "Select an employee from the table first.")
            return

        if messagebox.askyesno("Confirm Delete", f"Permanently delete employee {code.upper()}?"):
            ok, msg = delete_employee(code)
            if ok:
                messagebox.showinfo("Deleted", msg)
                self.clear_emp_form()
                self.refresh_all()
            else:
                messagebox.showerror("Error", msg)

    def handle_add_department(self):
        ok, msg = add_department(self.dept_name_entry.get(), self.dept_mgr_entry.get())
        if ok:
            messagebox.showinfo("Success", msg)
            self.dept_name_entry.delete(0, tk.END)
            self.dept_mgr_entry.delete(0, tk.END)
            self.refresh_all()
        else:
            messagebox.showerror("Error", msg)

    def on_employee_select(self, _event):
        selected = self.emp_tree.selection()
        if not selected:
            return
        values = self.emp_tree.item(selected[0], "values")
        # Populate the left-side form so the user can easily edit or delete
        self.emp_entries["code"].delete(0, tk.END)
        self.emp_entries["code"].insert(0, values[0])

        self.emp_entries["name"].delete(0, tk.END)
        self.emp_entries["name"].insert(0, values[1])

        self.emp_entries["email"].delete(0, tk.END)
        self.emp_entries["email"].insert(0, values[2])

        self.emp_entries["role"].delete(0, tk.END)
        self.emp_entries["role"].insert(0, values[4])

        clean_salary = str(values[5]).replace("$", "").replace(",", "")
        self.emp_entries["salary"].delete(0, tk.END)
        self.emp_entries["salary"].insert(0, clean_salary)

        self.status_combo.set(values[6])

    def clear_emp_form(self):
        for entry in self.emp_entries.values():
            entry.delete(0, tk.END)
        self.dept_combo.set("Unassigned")
        self.status_combo.set("Active")

    def refresh_employee_table(self):
        for row in self.emp_tree.get_children():
            self.emp_tree.delete(row)

        records = search_employees(keyword=self.search_var.get())
        for emp in records:
            self.emp_tree.insert(
                "",
                "end",
                values=(
                    emp["emp_code"],
                    emp["full_name"],
                    emp["email"],
                    emp["department_name"],
                    emp["role"],
                    f"${emp['salary']:,.2f}",
                    emp["status"],
                ),
            )

    def refresh_all(self):
        # 1. Refresh departments table & dropdown
        depts = list_departments()
        for row in self.dept_tree.get_children():
            self.dept_tree.delete(row)

        dropdown_options = ["Unassigned"]
        for d in depts:
            self.dept_tree.insert("", "end", values=(d["id"], d["name"], d["manager_name"]))
            dropdown_options.append(f"{d['id']} - {d['name']}")

        self.dept_combo["values"] = dropdown_options
        if not self.dept_combo.get():
            self.dept_combo.set("Unassigned")

        # 2. Refresh employee directory
        self.refresh_employee_table()

        # 3. Refresh organizational report metrics
        with get_db() as conn:
            overview = conn.execute("""
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) AS active,
                    COALESCE(SUM(salary), 0.0) AS payroll,
                    COALESCE(AVG(salary), 0.0) AS avg_sal
                FROM employees
            """).fetchone()

            breakdown = conn.execute("""
                SELECT
                    COALESCE(d.name, 'Unassigned') AS dept_name,
                    COALESCE(d.manager_name, 'N/A') AS manager,
                    COUNT(e.id) AS headcount,
                    COALESCE(SUM(e.salary), 0.0) AS dept_payroll
                FROM departments d
                LEFT JOIN employees e ON d.id = e.department_id
                GROUP BY d.id
                ORDER BY headcount DESC
            """).fetchall()

        self.summary_label.config(
            text=(
                f"Total Staff: {overview['total']} ({overview['active'] or 0} Active)    |    "
                f"Total Monthly Payroll: ${overview['payroll']:,.2f}    |    "
                f"Average Salary: ${overview['avg_sal']:,.2f}"
            )
        )

        for row in self.report_tree.get_children():
            self.report_tree.delete(row)
        for item in breakdown:
            self.report_tree.insert(
                "",
                "end",
                values=(item["dept_name"], item["manager"], item["headcount"], f"${item['dept_payroll']:,.2f}"),
            )


if __name__ == "__main__":
    app_root = tk.Tk()
    EmployeeManagementGUI(app_root)
    app_root.mainloop()