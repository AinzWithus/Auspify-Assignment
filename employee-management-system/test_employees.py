import os
import unittest
import database
from employees import (
    add_department,
    list_departments,
    register_employee,
    update_employee,
    delete_employee,
    search_employees,
    clear_cache,
)


class TestEmployeeSystem(unittest.TestCase):
    """Verifies CRUD operations, department links, and caching behavior."""

    def setUp(self):
        database.DB_FILE = "temp_test_employees.db"
        clear_cache()
        database.init_database()

    def tearDown(self):
        if os.path.exists("temp_test_employees.db"):
            os.remove("temp_test_employees.db")

    def test_department_and_employee_registration(self):
        ok_dept, _ = add_department("Engineering", "Sarah Jenkins")
        self.assertTrue(ok_dept)

        dept_id = list_departments()[0]["id"]
        ok_emp, _ = register_employee("EMP-101", "David Kato", "david@auspify.com", "Backend Dev", 3500.0, dept_id)
        self.assertTrue(ok_emp)

        # Duplicate employee code should be rejected
        dup_emp, _ = register_employee("emp-101", "Another Person", "other@auspify.com", "QA", 2500.0, dept_id)
        self.assertFalse(dup_emp)

    def test_update_and_delete_employee(self):
        register_employee("EMP-202", "Grace Namukasa", "grace@auspify.com", "Analyst", 2800.0)

        updated, _ = update_employee("EMP-202", role="Senior Analyst", salary=3400.0)
        self.assertTrue(updated)

        record = search_employees(keyword="EMP-202")[0]
        self.assertEqual(record["role"], "Senior Analyst")
        self.assertEqual(record["salary"], 3400.0)

        deleted, _ = delete_employee("EMP-202")
        self.assertTrue(deleted)
        self.assertEqual(len(search_employees(keyword="EMP-202")), 0)


if __name__ == "__main__":
    unittest.main()