# main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from database import SessionLocal, engine
from models import Base, User
from telegram_notif import send_telegram_message
import asyncio

app = FastAPI()
Base.metadata.create_all(bind=engine)

seen_users = set()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(poll_for_new_users())

@app.get("/")
def read_root():
    return {"message": "API is working"}

@app.get("/users")
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return JSONResponse(content=[{
        "uid": user.uid,
        "name": user.name,
        "phone": user.phone,
        "chat_id": user.chat_id
    } for user in users])

async def poll_for_new_users():
    while True:
        try:
            db = SessionLocal()
            db.expire_all()  # Force fresh data
            users = db.query(User).all()
            for user in users:
                if user.uid not in seen_users:
                    print(f"✅ New user detected: {user.uid}, sending message…")
                    send_telegram_message(user.chat_id, "Hi from Render API")
                    seen_users.add(user.uid)
            db.close()
        except Exception as e:
            print("Polling error:", str(e))
        await asyncio.sleep(5)
