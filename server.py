from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import json
import secrets
import sqlite3

ROOT = Path(__file__).parent
DB_PATH = ROOT / "linkpulse.db"


def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def initialize():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS links (
            code TEXT PRIMARY KEY,
            destination TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER NOT NULL DEFAULT 0
        )""")


class LinkPulseHandler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/links":
            with connect() as db:
                links = [dict(row) for row in db.execute(
                    "SELECT code, destination, created_at, clicks FROM links ORDER BY created_at DESC"
                )]
            return self.send_json(200, links)
        if path == "/":
            return self.serve_file("index.html", "text/html; charset=utf-8")
        if path.startswith("/assets/"):
            name = Path(path).name
            content_type = "text/css; charset=utf-8" if name.endswith(".css") else "text/javascript; charset=utf-8"
            return self.serve_file(name, content_type)
        code = path.strip("/")
        with connect() as db:
            row = db.execute("SELECT destination FROM links WHERE code = ?", (code,)).fetchone()
            if row:
                db.execute("UPDATE links SET clicks = clicks + 1 WHERE code = ?", (code,))
                self.send_response(302)
                self.send_header("Location", row["destination"])
                self.end_headers()
                return
        self.send_error(404, "Short link not found")

    def do_POST(self):
        if urlparse(self.path).path != "/api/links":
            return self.send_error(404)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(size))
            destination = str(data.get("url", "")).strip()
        except (ValueError, json.JSONDecodeError):
            return self.send_json(400, {"error": "Send a valid URL."})
        parsed = urlparse(destination)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return self.send_json(400, {"error": "Enter a complete URL starting with http:// or https://."})
        code = secrets.token_urlsafe(5).replace("-", "").replace("_", "")[:7]
        with connect() as db:
            while db.execute("SELECT 1 FROM links WHERE code = ?", (code,)).fetchone():
                code = secrets.token_urlsafe(5).replace("-", "").replace("_", "")[:7]
            db.execute("INSERT INTO links (code, destination) VALUES (?, ?)", (code, destination))
        return self.send_json(201, {"code": code, "destination": destination})

    def serve_file(self, name, content_type):
        file_path = ROOT / name
        if not file_path.is_file():
            return self.send_error(404)
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    initialize()
    print("LinkPulse running at http://localhost:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), LinkPulseHandler).serve_forever()
