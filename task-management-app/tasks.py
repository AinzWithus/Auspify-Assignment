from datetime import datetime
from database import get_db

VALID_PRIORITIES = {"Low", "Medium", "High"}
VALID_STATUSES = {"Pending", "In Progress", "Completed"}


def _validate_date(date_str):
    """Ensures due_date follows YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def create_task(user_id, title, description, category, priority, due_date):
    """Validates inputs and creates a new task owned by user_id."""
    clean_title = title.strip()
    if not clean_title:
        return False, "Task title cannot be empty.", None

    clean_priority = priority.strip().title() if priority else "Medium"
    if clean_priority not in VALID_PRIORITIES:
        return False, f"Priority must be one of: {', '.join(VALID_PRIORITIES)}.", None

    if not due_date or not _validate_date(due_date):
        return False, "Due date must be in YYYY-MM-DD format.", None

    clean_category = category.strip() or "General"

    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO tasks (user_id, title, description, category, priority, due_date, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending')
            """,
            (user_id, clean_title, description.strip(), clean_category, clean_priority, due_date.strip()),
        )
        task_id = cur.lastrowid

    return True, "Task added.", task_id


def list_tasks(user_id, status_filter="All", priority_filter="All", search=""):
    """Lists tasks belonging strictly to the authenticated user."""
    today = datetime.now().strftime("%Y-%m-%d")
    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [user_id]

    if status_filter and status_filter != "All":
        if status_filter == "Overdue":
            query += " AND status != 'Completed' AND due_date < ?"
            params.append(today)
        else:
            query += " AND status = ?"
            params.append(status_filter)

    if priority_filter and priority_filter != "All":
        query += " AND priority = ?"
        params.append(priority_filter)

    if search.strip():
        query += " AND (title LIKE ? OR description LIKE ? OR category LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term, term])

    query += " ORDER BY CASE WHEN status = 'Completed' THEN 1 ELSE 0 END, due_date ASC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()

    results = []
    for r in rows:
        item = dict(r)
        item["is_overdue"] = item["status"] != "Completed" and item["due_date"] < today
        results.append(item)
    return results


def update_task_status(user_id, task_id, new_status):
    """Updates task status only if the task belongs to user_id."""
    if new_status not in VALID_STATUSES:
        return False, "Invalid status value."

    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if new_status == "Completed" else None

    with get_db() as conn:
        cur = conn.execute(
            """
            UPDATE tasks
            SET status = ?, completed_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (new_status, completed_at, task_id, user_id),
        )
        if cur.rowcount == 0:
            return False, "Task not found or access denied."

    return True, f"Task marked as {new_status}."


def delete_task(user_id, task_id):
    """Deletes a task only if owned by user_id."""
    with get_db() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        if cur.rowcount == 0:
            return False, "Task not found or access denied."
    return True, "Task deleted."