from database import get_db


def print_organization_report():
    """Generates headcount, payroll, and department-level breakdown reports."""
    with get_db() as conn:
        overview = conn.execute("""
            SELECT 
                COUNT(*) AS total_staff,
                SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) AS active_staff,
                COALESCE(SUM(salary), 0.0) AS total_payroll,
                COALESCE(AVG(salary), 0.0) AS avg_salary
            FROM employees
        """).fetchone()

        dept_breakdown = conn.execute("""
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

    print("\n====================================================")
    print("            EMPLOYEE & ORGANIZATIONAL REPORT          ")
    print("====================================================")
    print(f"Total Employees   : {overview['total_staff']} ({overview['active_staff'] or 0} Active)")
    print(f"Monthly Payroll   : ${overview['total_payroll']:,.2f}")
    print(f"Average Salary    : ${overview['avg_salary']:,.2f}")

    print("\n--- Department Summary ---")
    if not dept_breakdown:
        print("  No departments set up yet.")
    else:
        for dept in dept_breakdown:
            print(
                f"  * {dept['dept_name']} (Lead: {dept['manager']}) -> "
                f"{dept['headcount']} staff | Payroll: ${dept['dept_payroll']:,.2f}"
            )
    print("====================================================\n")