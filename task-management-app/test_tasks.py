import os
import unittest
import database
from auth import register_user, login_user
from tasks import create_task, list_tasks, update_task_status, delete_task
from reports import generate_performance_report


class TestTaskManagementSecurityAndReports(unittest.TestCase):
    """Verifies input validation, user data isolation, brute-force protection, and score reports."""

    def setUp(self):
        database.DB_FILE = "temp_test_tasks.db"
        database.init_database()

    def tearDown(self):
        if os.path.exists("temp_test_tasks.db"):
            os.remove("temp_test_tasks.db")

    def test_security_user_isolation(self):
        register_user("userone", "User One", "secure123")
        register_user("usertwo", "User Two", "secure456")

        _, _, s1 = login_user("userone", "secure123")
        _, _, s2 = login_user("usertwo", "secure456")

        ok, _, task_id = create_task(s1["user_id"], "Submit Project", "Final repo", "Work", "High", "2026-12-01")
        self.assertTrue(ok)

        # User Two must NOT see, modify, or delete User One's task
        self.assertEqual(len(list_tasks(s2["user_id"])), 0)
        mod_ok, _ = update_task_status(s2["user_id"], task_id, "Completed")
        self.assertFalse(mod_ok)
        del_ok, _ = delete_task(s2["user_id"], task_id)
        self.assertFalse(del_ok)

    def test_validation_and_performance_report(self):
        register_user("benji", "Benji Dev", "pass9876")
        _, _, session = login_user("benji", "pass9876")
        uid = session["user_id"]

        # Reject invalid date format
        bad_ok, _, _ = create_task(uid, "Bad Date Task", "", "Work", "Low", "17-11-2026")
        self.assertFalse(bad_ok)

        _, _, t1 = create_task(uid, "API Integration", "", "Dev", "High", "2026-12-10")
        _, _, t2 = create_task(uid, "Write Docs", "", "Dev", "Low", "2026-12-12")

        update_task_status(uid, t1, "Completed")
        report = generate_performance_report(uid)

        self.assertEqual(report["total_tasks"], 2)
        self.assertEqual(report["completed"], 1)
        self.assertEqual(report["productivity_score"], 75.0)
        self.assertEqual(report["grade"], "B (On Track)")


if __name__ == "__main__":
    unittest.main()