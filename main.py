from fastapi import FastAPI
from database import SessionLocal
from models import User
from telegram_notif import send_message
import time
import threading

app = FastAPI()
db = SessionLocal()

# Set to track which user IDs we've already messaged
seen_user_ids = set()

@app.get("/")
def root():
    return {"message": "Telegram Alert API is running"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.query(User).filter(User.uid == user_id).first()
    if user:
        return {
            "uid": user.uid,
            "name": user.name,
            "phone": user.phone,
            "chat_id": user.chat_id,
        }
    return {"error": "User not found"}

def poll_new_users():
    while True:
        users = db.query(User).all()
        for user in users:
            if user.uid not in seen_user_ids:
                seen_user_ids.add(user.uid)
                print(f"✅ New user detected: {user.uid}, sending message…")
                if user.chat_id:
                    response = send_message(user.chat_id, "Hi!")
                    print(f"Telegram Response: {response}")
                else:
                    print("❌ No chat_id provided")
        time.sleep(5)

threading.Thread(target=poll_new_users, daemon=True).start()
