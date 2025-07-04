# main.py
import os
import asyncio
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
from database import SessionLocal
from models import User     # ← already present
# ──────────────────────────────────────────────────────────────────────────────
# WhatsApp Cloud-API credentials (set these on Render / Railway)
WA_TOKEN         = os.getenv("WA_TOKEN")              # long-lived or system-user
WA_PHONE_NUMBER  = os.getenv("WA_PHONE_NUMBER_ID")    # numeric ID, *not* E.164!
if not (WA_TOKEN and WA_PHONE_NUMBER):
    raise RuntimeError("▶️  WA_TOKEN and WA_PHONE_NUMBER_ID must be env-vars")
# ──────────────────────────────────────────────────────────────────────────────
def send_whatsapp_message(to: str, body: str) -> dict:
    """
    POST text to WhatsApp Cloud-API.
    Docs: /{PHONE_NUMBER_ID}/messages endpoint :contentReference[oaicite:0]{index=0}
    """
    url = f"https://graph.facebook.com/v19.0/{WA_PHONE_NUMBER}/messages"
    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type":  "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to":   to,                     # must include country code, no “+”
        "type": "text",
        "text": {"body": body},
    }
    r = requests.post(url, json=payload, headers=headers, timeout=10)
    try:
        r.raise_for_status()
    except requests.HTTPError as exc:
        raise HTTPException(status_code=exc.response.status_code,
                            detail=exc.response.text) from exc
    return r.json()
# ──────────────────────────────────────────────────────────────────────────────
app = FastAPI()
db  = SessionLocal()
seen: set[int] = set()                # for the background poller
class Msg(BaseModel):
    """Schema for POST /send"""
    phone: constr(strip_whitespace=True, min_length=7, max_length=20)
    body:  constr(strip_whitespace=True, min_length=1, max_length=4096)
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/")
def list_users():
    """Pull – return every row in `users` as JSON."""
    users = db.query(User).all()
    return [
        {"uid": u.uid, "name": u.name, "phone": u.phone, "chat_id": u.chat_id}
        for u in users
    ]
@app.post("/send")
def send(msg: Msg):
    """Push – forward JSON to WhatsApp Cloud-API and relay its response."""
    wa_resp = send_whatsapp_message(msg.phone, msg.body)
    return {"status": "ok", "whatsapp": wa_resp}
# ──────────────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def _startup():
    """Optional: greet brand-new DB rows automatically."""
    asyncio.create_task(_poll_for_new_users())
async def _poll_for_new_users():
    while True:
        try:
            for u in db.query(User).all():
                if u.uid not in seen:
                    seen.add(u.uid)
                    send_whatsapp_message(u.phone, f"👋 Hey {u.name}, welcome!")
        except Exception as e:
            print("poller-error:", e)
        await asyncio.sleep(5)
