import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from database import init_database
from auth import register_user, login_user, get_session, logout_user
from exams import fetch_exams, get_exam_details, grade_submission, get_user_results

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ExamAPIHandler(BaseHTTPRequestHandler):
    """Handles REST API endpoints and serves the web frontend."""

    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def _current_user(self):
        auth_header = self.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()
        return get_session(token), token

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Serve the main frontend screen
        if path == "/" or path == "/index.html":
            index_path = os.path.join(BASE_DIR, "index.html")
            with open(index_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        # REST API: List / Search / Filter Exams
        if path == "/api/exams":
            params = parse_qs(parsed.query)
            search = params.get("search", [""])[0]
            category = params.get("category", [""])[0]
            difficulty = params.get("difficulty", [""])[0]
            exams = fetch_exams(search=search, category=category, difficulty=difficulty)
            self._send_json(200, {"exams": exams})
            return

        # REST API: Single Exam Details + Questions
        if path.startswith("/api/exams/"):
            user, _ = self._current_user()
            if not user:
                self._send_json(401, {"error": "Please log in to start an exam."})
                return

            try:
                exam_id = int(path.split("/")[-1])
            except ValueError:
                self._send_json(400, {"error": "Invalid exam ID."})
                return

            details = get_exam_details(exam_id)
            if not details:
                self._send_json(404, {"error": "Exam not found."})
                return
            self._send_json(200, details)
            return

        # REST API: User's Past Results
        if path == "/api/results":
            user, _ = self._current_user()
            if not user:
                self._send_json(401, {"error": "Authentication required."})
                return
            self._send_json(200, {"results": get_user_results(user["user_id"])})
            return

        self._send_json(404, {"error": "Endpoint not found."})

    def do_POST(self):
        path = urlparse(self.path).path
        data = self._read_json_body()

        if path == "/api/register":
            ok, msg = register_user(
                data.get("username", ""), data.get("full_name", ""), data.get("password", "")
            )
            self._send_json(201 if ok else 400, {"message": msg})
            return

        if path == "/api/login":
            ok, msg, session = login_user(data.get("username", ""), data.get("password", ""))
            if ok:
                self._send_json(200, {"message": msg, "session": session})
            else:
                self._send_json(401, {"error": msg})
            return

        if path == "/api/logout":
            _, token = self._current_user()
            logout_user(token)
            self._send_json(200, {"message": "Logged out."})
            return

        if path == "/api/submit":
            user, _ = self._current_user()
            if not user:
                self._send_json(401, {"error": "Please log in before submitting."})
                return

            ok, msg, result = grade_submission(
                user["user_id"], data.get("exam_id"), data.get("answers", {})
            )
            self._send_json(200 if ok else 400, {"message": msg, "result": result})
            return

        self._send_json(404, {"error": "Endpoint not found."})

    def log_message(self, format, *args):
        # Keep terminal output clean
        return


def run_server(port=8000):
    init_database()
    server = ThreadingHTTPServer(("127.0.0.1", port), ExamAPIHandler)
    print(f"Online Examination System running at http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    run_server()