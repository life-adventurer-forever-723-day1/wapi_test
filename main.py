from fastapi import FastAPI
from database import SessionLocal, engine
from models import Base, User
from telegram_notif import send_telegram_message
import asyncio

app = FastAPI()

seen_users = set()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(poll_for_new_users())

@app.get("/")
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return [{"uid": u.uid, "name": u.name, "phone": u.phone, "chat_id": u.chat_id} for u in users]

async def poll_for_new_users():
    while True:
        try:
            db = SessionLocal()
            users = db.query(User).all()
            for user in users:
                if user.uid not in seen_users:
                    print(f"✅ New user detected: {user.uid}, sending message…")
                    response = send_telegram_message(user.chat_id, "Hi")
                    print(response)
                    seen_users.add(user.uid)
            db.close()
        except Exception as e:
            print("Polling error:", str(e))
        await asyncio.sleep(5)
