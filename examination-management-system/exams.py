from database import get_db

# Lightweight query cache to speed up repeated catalog searches
_EXAM_CACHE = {}


def clear_exam_cache():
    """Clears cached exam listings whenever exam data changes."""
    _EXAM_CACHE.clear()


def fetch_exams(search="", category="", difficulty=""):
    """Returns filtered exam summaries (with caching for UI responsiveness)."""
    cache_key = (search.strip().lower(), category.strip().lower(), difficulty.strip().lower())
    if cache_key in _EXAM_CACHE:
        return _EXAM_CACHE[cache_key]

    query = """
        SELECT e.id, e.code, e.title, e.category, e.difficulty, e.duration_mins, e.description,
               COUNT(q.id) AS question_count
        FROM exams e
        LEFT JOIN questions q ON e.id = q.exam_id
        WHERE 1=1
    """
    params = []

    if search.strip():
        query += " AND (e.title LIKE ? OR e.code LIKE ? OR e.description LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term, term])

    if category.strip() and category.lower() != "all":
        query += " AND LOWER(e.category) = LOWER(?)"
        params.append(category.strip())

    if difficulty.strip() and difficulty.lower() != "all":
        query += " AND LOWER(e.difficulty) = LOWER(?)"
        params.append(difficulty.strip())

    query += " GROUP BY e.id ORDER BY e.id ASC"

    with get_db() as conn:
        rows = [dict(row) for row in conn.execute(query, params).fetchall()]

    _EXAM_CACHE[cache_key] = rows
    return rows


def get_exam_details(exam_id):
    """Fetches full exam metadata and questions (without exposing answer keys to the client)."""
    with get_db() as conn:
        exam = conn.execute("SELECT * FROM exams WHERE id = ?", (exam_id,)).fetchone()
        if not exam:
            return None

        questions = conn.execute(
            """
            SELECT id, prompt, option_a, option_b, option_c, option_d
            FROM questions
            WHERE exam_id = ?
            ORDER BY id ASC
            """,
            (exam_id,),
        ).fetchall()

    result = dict(exam)
    result["questions"] = [dict(q) for q in questions]
    return result


def grade_submission(user_id, exam_id, answers_map):
    """Grades submitted answers against stored keys and records the attempt."""
    with get_db() as conn:
        questions = conn.execute(
            "SELECT id, correct_option FROM questions WHERE exam_id = ?", (exam_id,)
        ).fetchall()

        if not questions:
            return False, "Exam not found or has no questions.", None

        score = 0
        total = len(questions)
        for q in questions:
            chosen = str(answers_map.get(str(q["id"]), "")).strip().upper()
            if chosen == q["correct_option"].upper():
                score += 1

        conn.execute(
            "INSERT INTO submissions (user_id, exam_id, score, total) VALUES (?, ?, ?, ?)",
            (user_id, exam_id, score, total),
        )

    percentage = round((score / total) * 100, 1)
    return True, "Exam graded successfully.", {"score": score, "total": total, "percentage": percentage}


def get_user_results(user_id):
    """Fetches past exam scores for the logged-in user."""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT s.id, e.code, e.title, s.score, s.total, s.submitted_at
            FROM submissions s
            JOIN exams e ON s.exam_id = e.id
            WHERE s.user_id = ?
            ORDER BY s.submitted_at DESC
            """,
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]