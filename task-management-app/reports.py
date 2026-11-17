from datetime import datetime
from database import get_db


def generate_performance_report(user_id):
    """Calculates task completion rates, overdue counts, and productivity score."""
    today = datetime.now().strftime("%Y-%m-%d")

    with get_db() as conn:
        rows = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()

    total = len(rows)
    if total == 0:
        return {
            "total_tasks": 0,
            "completed": 0,
            "pending": 0,
            "overdue": 0,
            "completion_rate": 0.0,
            "productivity_score": 0.0,
            "grade": "N/A",
            "by_priority": {"High": 0, "Medium": 0, "Low": 0},
        }

    completed = sum(1 for r in rows if r["status"] == "Completed")
    overdue = sum(1 for r in rows if r["status"] != "Completed" and r["due_date"] < today)
    pending = total - completed

    # Weighted score: High priority completions earn extra points; overdue tasks deduct slightly
    weights = {"High": 3, "Medium": 2, "Low": 1}
    max_points = sum(weights.get(r["priority"], 1) for r in rows)
    earned_points = sum(weights.get(r["priority"], 1) for r in rows if r["status"] == "Completed")
    penalty = overdue * 0.5

    raw_score = max(0.0, ((earned_points - penalty) / max_points) * 100) if max_points > 0 else 0.0
    productivity_score = round(min(100.0, raw_score), 1)
    completion_rate = round((completed / total) * 100, 1)

    if productivity_score >= 85:
        grade = "A (Excellent)"
    elif productivity_score >= 70:
        grade = "B (On Track)"
    elif productivity_score >= 50:
        grade = "C (Needs Focus)"
    else:
        grade = "D (Behind Schedule)"

    by_priority = {
        p: sum(1 for r in rows if r["priority"] == p) for p in ("High", "Medium", "Low")
    }

    return {
        "total_tasks": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue,
        "completion_rate": completion_rate,
        "productivity_score": productivity_score,
        "grade": grade,
        "by_priority": by_priority,
    }