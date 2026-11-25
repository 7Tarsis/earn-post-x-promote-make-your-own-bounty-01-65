import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "tasks.db"

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )

def create_task(title: str):
    with _conn() as conn:
        cur = conn.execute("INSERT INTO tasks(title, done) VALUES (?, 0)", (title,))
        task_id = cur.lastrowid
        row = conn.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

def list_tasks():
    with _conn() as conn:
        rows = conn.execute("SELECT id, title, done FROM tasks ORDER BY id ASC").fetchall()
    return [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]

def get_task(task_id: int):
    with _conn() as conn:
        row = conn.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        return None
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

def update_task(task_id: int, title: str | None = None, done: bool | None = None):
    current = get_task(task_id)
    if current is None:
        return None
    next_title = title if title is not None else current["title"]
    next_done = int(done) if done is not None else int(current["done"])
    with _conn() as conn:
        conn.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (next_title, next_done, task_id))
    return get_task(task_id)

def delete_task(task_id: int):
    if get_task(task_id) is None:
        return False
    with _conn() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return True

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload, code=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/tasks":
            self._send_json(list_tasks())
            return
        self._send_json({"error": "not found"}, code=404)

if __name__ == "__main__":
    init_db()
    server = HTTPServer(("127.0.0.1", 8080), Handler)
    server.serve_forever()
