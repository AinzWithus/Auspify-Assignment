import os
import unittest
import database
from auth import register_user, login_user, get_session
from exams import fetch_exams, get_exam_details, grade_submission, get_user_results, clear_exam_cache


class TestOnlineExamSystem(unittest.TestCase):
    """Tests user authentication, exam search/filtering, and automatic grading."""

    def setUp(self):
        database.DB_FILE = "temp_test_exams.db"
        clear_exam_cache()
        database.init_database()

    def tearDown(self):
        if os.path.exists("temp_test_exams.db"):
            os.remove("temp_test_exams.db")

    def test_auth_registration_and_login(self):
        ok, _ = register_user("benji", "Benji Student", "pass1234")
        self.assertTrue(ok)

        logged_in, _, session = login_user("benji", "pass1234")
        self.assertTrue(logged_in)
        self.assertIsNotNone(get_session(session["token"]))

        bad_login, _, _ = login_user("benji", "wrongpass")
        self.assertFalse(bad_login)

    def test_search_filter_and_grading(self):
        register_user("alice", "Alice Kato", "secret99")
        _, _, session = login_user("alice", "secret99")

        # Filter by category
        db_exams = fetch_exams(category="Databases")
        self.assertEqual(len(db_exams), 1)
        self.assertEqual(db_exams[0]["code"], "DB-201")

        # Load exam details & submit answers
        details = get_exam_details(db_exams[0]["id"])
        q_ids = [q["id"] for q in details["questions"]]
        answers = {str(q_ids[0]): "B", str(q_ids[1]): "B", str(q_ids[2]): "C"}

        graded, _, result = grade_submission(session["user_id"], details["id"], answers)
        self.assertTrue(graded)
        self.assertEqual(result["score"], 3)
        self.assertEqual(result["percentage"], 100.0)

        history = get_user_results(session["user_id"])
        self.assertEqual(len(history), 1)


if __name__ == "__main__":
    unittest.main()