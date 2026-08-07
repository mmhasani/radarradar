import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np

# إعدادات التلجرام
TELEGRAM_TOKEN = os.getenv("8888012466:AAEzxacUUvfa2I5ny7LMzicZChZZQ_lQkWo")
TELEGRAM_CHAT_ID = os.getenv("8325305534")

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, json=payload)

# قائمة الأسهم
symbols = ["AMD", "NVDA", "TSLA"] 

for symbol in symbols:
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="5d", interval="5m")
    
    # حساب المؤشرات مبسط
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # شرط بسيط للتجربة
    if prev['EMA9'] <= prev['EMA20'] and last['EMA9'] > last['EMA20']:
        send_telegram_msg(f"<b>إشارة شراء (CALL) على {symbol}</b>\nالسعر: {round(last['Close'], 2)}")
