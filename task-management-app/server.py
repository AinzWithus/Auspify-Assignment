import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from database import init_database
from auth import register_user, login_user, get_session, logout_user
from tasks import create_task, list_tasks, update_task_status, delete_task
from reports import generate_performance_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TaskAppHandler(BaseHTTPRequestHandler):
    """REST API handler with security headers and token-based authorization."""

    def _set_security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cache-Control", "no-store")

    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self._set_security_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _require_auth(self):
        token = self.headers.get("Authorization", "").replace("Bearer ", "").strip()
        user = get_session(token)
        return user, token

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            with open(os.path.join(BASE_DIR, "index.html"), "rb") as f:
                html = f.read()
            self.send_response(200)
            self._set_security_headers()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        user, _ = self._require_auth()
        if not user:
            self._send_json(401, {"error": "Unauthorized. Please log in."})
            return

        if path == "/api/tasks":
            qs = parse_qs(parsed.query)
            tasks = list_tasks(
                user_id=user["user_id"],
                status_filter=qs.get("status", ["All"])[0],
                priority_filter=qs.get("priority", ["All"])[0],
                search=qs.get("search", [""])[0],
            )
            self._send_json(200, {"tasks": tasks})
            return

        if path == "/api/report":
            report = generate_performance_report(user["user_id"])
            self._send_json(200, {"report": report})
            return

        self._send_json(404, {"error": "Not found."})

    def do_POST(self):
        path = urlparse(self.path).path
        data = self._read_json()

        if path == "/api/register":
            ok, msg = register_user(data.get("username", ""), data.get("full_name", ""), data.get("password", ""))
            self._send_json(201 if ok else 400, {"message": msg})
            return

        if path == "/api/login":
            ok, msg, session = login_user(data.get("username", ""), data.get("password", ""))
            if ok:
                self._send_json(200, {"message": msg, "session": session})
            else:
                self._send_json(401, {"error": msg})
            return

        user, token = self._require_auth()
        if not user:
            self._send_json(401, {"error": "Unauthorized."})
            return

        if path == "/api/logout":
            logout_user(token)
            self._send_json(200, {"message": "Logged out."})
            return

        if path == "/api/tasks":
            ok, msg, task_id = create_task(
                user_id=user["user_id"],
                title=data.get("title", ""),
                description=data.get("description", ""),
                category=data.get("category", "General"),
                priority=data.get("priority", "Medium"),
                due_date=data.get("due_date", ""),
            )
            self._send_json(201 if ok else 400, {"message": msg, "task_id": task_id})
            return

        if path == "/api/tasks/status":
            ok, msg = update_task_status(user["user_id"], data.get("task_id"), data.get("status", ""))
            self._send_json(200 if ok else 400, {"message": msg})
            return

        if path == "/api/tasks/delete":
            ok, msg = delete_task(user["user_id"], data.get("task_id"))
            self._send_json(200 if ok else 400, {"message": msg})
            return

        self._send_json(404, {"error": "Not found."})

    def log_message(self, format, *args):
        return


def run_server(port=8080):
    init_database()
    server = ThreadingHTTPServer(("127.0.0.1", port), TaskAppHandler)
    print(f"Task & Deadline Management App running at http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    run_server()