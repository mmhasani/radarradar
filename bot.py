import requests

BOT_TOKEN = "8888012466:AAEzxacUUvfa2I5ny7LMzicZChZZQ_lQkWo"
CHAT_ID = "8325305534"

symbol = "AMD"

url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

data = requests.get(url).json()

price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]

message = "TEST 777"

telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

response = requests.post(
    telegram_url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(response.text)
