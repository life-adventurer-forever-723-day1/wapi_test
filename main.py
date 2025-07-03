from fastapi import FastAPI
from models import Base, User
from database import SessionLocal, engine
import json
import time
import threading
from telegram_notif import send_telegram_message
import os

app = FastAPI()
Base.metadata.create_all(bind=engine)

NOTIFIED_FILE = "notified.json"

def load_notified_uids():
    if not os.path.exists(NOTIFIED_FILE):
        return []
    with open(NOTIFIED_FILE, "r") as f:
        return json.load(f)

def save_notified_uids(uids):
    with open(NOTIFIED_FILE, "w") as f:
        json.dump(uids, f)

def poll_db():
    db = SessionLocal()
    notified_uids = set(load_notified_uids())

    while True:
        users = db.query(User).all()

        for user in users:
            if user.uid not in notified_uids:
                print(f"✅ New user detected: {user.uid}, sending message…")

                with open("storage.json", "w") as f:
                    json.dump({
                        "uid": user.uid,
                        "name": user.name,
                        "phone": user.phone,
                        "chat_id": user.chat_id
                    }, f, indent=2)

                send_telegram_message(user.chat_id, "Hi")

                notified_uids.add(user.uid)
                save_notified_uids(list(notified_uids))

        time.sleep(5)

# Start polling in background
threading.Thread(target=poll_db, daemon=True).start()
