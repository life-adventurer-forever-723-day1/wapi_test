import requests

BOT_TOKEN = "7803185537:AAFP7SK0-41jDXUj_F8cmpyda8QcVABk-hE"  # Replace with actual token

def send_message(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, json=payload)
    return response.json()
