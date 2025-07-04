
from fastapi import FastAPI
from database import SessionLocal
from models import User

app = FastAPI()
def _open_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _all_rows():
    with next(_open_db()) as db:
        return db.query(User).all()

@app.get("/")
def fetch_users():
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

@app.post("/")
def push_payload():
    users = _all_rows()
    return [
        {
            "name":    u.name,
            "phone":   u.phone,
            "message": "Hi",
        }
        for u in users
    ]
