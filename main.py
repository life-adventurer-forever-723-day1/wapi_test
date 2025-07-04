# main.py
import time
import threading
from fastapi import FastAPI
from database import SessionLocal
from models import User
from telegram_notif import send_message   # keeps the Telegram greeting logic

app = FastAPI()
db = SessionLocal()

# Track users we’ve already greeted
seen_user_ids: set[int] = set()

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def _all_users_json() -> list[dict]:
    """Return every row from the `users` table as a list of dicts."""
    users = db.query(User).all()
    return [
        {"uid": u.uid, "name": u.name, "phone": u.phone, "chat_id": u.chat_id}
        for u in users
    ]

# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Telegram Alert API is running"}

@app.get("/users")
def get_users():
    """Pull – fetch the latest snapshot of all users in the DB."""
    return {"users": _all_users_json()}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Pull – fetch a single user by primary key."""
    user = db.query(User).filter(User.uid == user_id).first()
    if user:
        return {
            "uid": user.uid,
            "name": user.name,
            "phone": user.phone,
            "chat_id": user.chat_id,
        }
    return {"error": "User not found"}

@app.post("/push")
def push_now():
    """
    Push – **no external calls**.
    Simply returns the JSON payload that would normally be forwarded
    elsewhere, so you can inspect it in Postman / curl.
    """
    payload = _all_users_json()
    return {"status": "ok", "payload": payload}

# ─────────────────────────────────────────────────────────────
# Background poller – greets brand-new users on Telegram
# ─────────────────────────────────────────────────────────────
def _poll_new_users():
    while True:
        users = db.query(User).all()
        for user in users:
            if user.uid not in seen_user_ids:
                seen_user_ids.add(user.uid)
                print(f"✅ New user detected: {user.uid}, sending message…")
                if user.chat_id:
                    resp = send_message(user.chat_id, "Hi!")
                    print(f"Telegram response ➜ {resp}")
                else:
                    print("❌ No chat_id provided")
        time.sleep(5)

threading.Thread(target=_poll_new_users, daemon=True).start()
