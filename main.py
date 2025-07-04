# main.py
from fastapi import FastAPI
from database import SessionLocal
from models import User

app = FastAPI()

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def _open_db():
    """Context-manager – always closes the session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _all_rows():
    """Return list[User] – every row in the users table."""
    with next(_open_db()) as db:
        return db.query(User).all()

# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────
@app.get("/")
def fetch_users():
    """
    GET  /  ➜  full snapshot of the users table.
    Example response:
    [
      { "uid": 1, "name": "Alice", "phone": "919876543210", "chat_id": null },
      ...
    ]
    """
    users = _all_rows()
    return [
        {
            "uid":   u.uid,
            "name":  u.name,
            "phone": u.phone,
            "chat_id": u.chat_id,
        }
        for u in users
    ]

@app.post("/push")
def push_payload():
    """
    POST /push  ➜  minimal payload for each user:
    { "name": <user.name>, "phone": <user.phone>, "message": "Hi" }
    No request body required.
    """
    users = _all_rows()
    return [
        {
            "name":    u.name,
            "phone":   u.phone,
            "message": "Hi",
        }
        for u in users
    ]
