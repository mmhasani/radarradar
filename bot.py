import requests

BOT_TOKEN = "8888012466:AAEzxacUUvfa2I5ny7LMzicZChZZQ_lQkWo"
CHAT_ID = "8325305534"

message = "✅ Trading Radar Test"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(response.text)
