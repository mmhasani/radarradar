Python
1
import requests
2
 
3
BOT_TOKEN = "8888012466:AAEzxacUUvfa2I5ny7LMzicZChZZQ_lQkWoا"
4
CHAT_ID = "8325305534"
5
 
6
message = "✅ Trading Radar Test"
7
 
8
url = f"https://api.telegram.org/bot{8888012466:AAEzxacUUvfa2I5ny7LMzicZChZZQ_lQkWo}/sendMessage"
9
 
10
requests.post(
11
url,
12
data={
13
"chat_id": 8325305534,
14
"text": message
15
}
16
)
17
 
18
print("Message Sent")
