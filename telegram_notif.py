import requests

BOT_TOKEN = "7803185537:AAFP7SK0-41jDXUj_F8cmpyda8QcVABk-hE"  # 🔁 Replace with your bot token

def send_telegram_message(chat_id: str, message: str):
    if not chat_id:
        print("❌ chat_id not available.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print(f"✅ Message sent to chat_id {chat_id}")
    else:
        print(f"❌ Failed to send message: {response.text}")
