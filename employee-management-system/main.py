from database import init_database
from employees import (
    add_department,
    list_departments,
    register_employee,
    update_employee,
    delete_employee,
    search_employees,
)
from reports import print_organization_report


def display_employees(records):
    """Prints a clean table of employee records."""
    if not records:
        print("\nNo matching employee records found.\n")
        return

    print(f"\n{'Code':<10} {'Full Name':<20} {'Department':<15} {'Role':<18} {'Salary':<11} {'Status':<10}")
    print("-" * 88)
    for emp in records:
        print(
            f"{emp['emp_code']:<10} {emp['full_name']:<20} {emp['department_name']:<15} "
            f"{emp['role']:<18} ${emp['salary']:<10,.2f} {emp['status']:<10}"
        )
    print()


def main_menu():
    init_database()

    while True:
        print("=== Employee Management System ===")
        print("1. Manage Departments (Add / View)")
        print("2. Register New Employee")
        print("3. Update Employee Record")
        print("4. Delete Employee Record")
        print("5. Search & View Employees")
        print("6. Generate Organizational Report")
        print("7. Exit")

        choice = input("\nSelect an option (1-7): ").strip()

        if choice == "1":
            print("\n--- Existing Departments ---")
            depts = list_departments()
            if not depts:
                print("None yet.")
            for d in depts:
                print(f"  [{d['id']}] {d['name']} (Manager: {d['manager_name']})")

            create = input("\nAdd a new department? (y/n): ").strip().lower()
            if create == "y":
                d_name = input("Department name: ")
                mgr = input("Department manager (optional): ")
                _, msg = add_department(d_name, mgr)
                print(f"\n{msg}\n")

        elif choice == "2":
            code = input("Employee Code (e.g. EMP-01): ")
            name = input("Full Name: ")
            email = input("Email Address: ")
            role = input("Job Role / Title: ")

            depts = list_departments()
            if depts:
                print("Available Departments:", ", ".join(f"{d['id']}:{d['name']}" for d in depts))
            dept_input = input("Department ID (press Enter to leave unassigned): ").strip()

            try:
                salary = float(input("Salary: "))
                dept_id = int(dept_input) if dept_input else None
                _, msg = register_employee(code, name, email, role, salary, dept_id)
                print(f"\n{msg}\n")
            except ValueError:
                print("\nInvalid number entered for salary or department ID.\n")

        elif choice == "3":
            code = input("Enter Employee Code to update: ")
            print("(Press Enter on any field you want to keep unchanged)")
            role = input("New Role: ")
            sal_str = input("New Salary: ").strip()
            status = input("New Status (Active / On Leave / Resigned): ")

            try:
                sal = float(sal_str) if sal_str else None
                _, msg = update_employee(code, role=role, salary=sal, status=status)
                print(f"\n{msg}\n")
            except ValueError:
                print("\nSalary must be a valid number.\n")

        elif choice == "4":
            code = input("Enter Employee Code to delete: ")
            confirm = input(f"Are you sure you want to permanently remove {code.upper()}? (y/n): ").strip().lower()
            if confirm == "y":
                _, msg = delete_employee(code)
                print(f"\n{msg}\n")
            else:
                print("\nDeletion cancelled.\n")

        elif choice == "5":
            kw = input("Search by name, code, or role (Enter for all): ")
            dept = input("Filter by department name (Enter for all): ")
            results = search_employees(kw, dept)
            display_employees(results)

        elif choice == "6":
            print_organization_report()

        elif choice == "7":
            print("Exiting Employee Management System.")
            break
        else:
            print("\nInvalid choice. Please pick between 1 and 7.\n")


if __name__ == "__main__":
    main_menu()