import requests
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8059019021:AAEkw9yMFWBfS0xdADV3F9p9xEICHneviTs")

def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print("❌ Failed to send message:", response.text)
    return response.json()
