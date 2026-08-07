import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np

# ==========================================
# 1. قائمة الأسهم التي ترغب بمراقبتها
# ==========================================
WATCHLIST = ["MRVL", "AMD", "NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META", "QQQ", "SPY"]

# ==========================================
# 2. إعدادات التلجرام (استبدل بالتوكن والآيدي الخاصين بك)
# ==========================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8888012466:AAEzxacUUvfa2I5ny7LMzicZChZZQ_lQkWo")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8325305534")

def send_telegram_msg(message):
    """دالة إرسال التنبيه إلى التلجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, json=payload)
        if res.status_code != 200:
            print(f"فشل إرسال التلجرام: {res.text}")
    except Exception as e:
        print(f"خطأ أثناء الإرسال: {e}")

def analyze_stock(ticker_symbol):
    """دالة جلب البيانات وحساب المؤشرات السبعة"""
    try:
        # جلب بيانات 5 دقائق لآخر 5 أيام
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period="5d", interval="5m")

        if df.empty or len(df) < 30:
            return None

        # --- حساب المؤشرات ---
        # 1 & 2. EMA 9 & EMA 20
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()

        # 3. RSI (14)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # 4. MACD (12, 26, 9)
        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # 5. ATR (14)
        high_low = df['High'] - df['Low']
        high_cp = np.abs(df['High'] - df['Close'].shift())
        low_cp = np.abs(df['Low'] - df['Close'].shift())
        df['TR'] = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
        df['ATR'] = df['TR'].rolling(14).mean()

        # 6 & 7. Volume & RVOL (Relative Volume)
        df['Vol_SMA20'] = df['Volume'].rolling(20).mean()
        df['RVOL'] = df['Volume'] / df['Vol_SMA20']

        # قراءة آخر شمعة مكتملة
        last = df.iloc[-1]
        prev = df.iloc[-2]

        price = round(last['Close'], 2)
        rsi_val = round(last['RSI'], 1)
        rvol_val = round(last['RVOL'], 2)
        atr_val = round(last['ATR'], 2)

        # --- شروط الكول (CALL) ---
        call_cond = (
            (prev['EMA9'] <= prev['EMA20'] and last['EMA9'] > last['EMA20']) and  # تقاطع إيجابي للمتوسطات
            last['RSI'] > 50 and                                                   # RSI فوق 50
            last['MACD'] > last['Signal'] and                                     # MACD إيجابي
            last['RVOL'] >= 1.2                                                   # دخول سيولة (RVOL عالي)
        )

        # --- شروط البوت (PUT) ---
        put_cond = (
            (prev['EMA9'] >= prev['EMA20'] and last['EMA9'] < last['EMA20']) and  # تقاطع سلبي للمتوسطات
            last['RSI'] < 50 and                                                   # RSI تحت 50
            last['MACD'] < last['Signal'] and                                     # MACD سلبي
            last['RVOL'] >= 1.2                                                   # دخول سيولة عالي
        )

        if call_cond:
            msg = (
                f"🟢 <b>تنبيه CALL جديد!</b>\n\n"
                f"📌 <b>السهم:</b> {ticker_symbol}\n"
                f"💵 <b>السعر الحالي:</b> ${price}\n"
                f"📊 <b>RSI:</b> {rsi_val}\n"
                f"🔥 <b>RVOL:</b> {rvol_val}x\n"
                f"⚡ <b>ATR:</b> {atr_val}\n\n"
                f"🎯 <i>تطابقت شروط التقاطع والزخم والسيولة!</i>"
            )
            return msg

        elif put_cond:
            msg = (
                f"🔴 <b>تنبيه PUT جديد!</b>\n\n"
                f"📌 <b>السهم:</b> {ticker_symbol}\n"
                f"💵 <b>السعر الحالي:</b> ${price}\n"
                f"📊 <b>RSI:</b> {rsi_val}\n"
                f"🔥 <b>RVOL:</b> {rvol_val}x\n"
                f"⚡ <b>ATR:</b> {atr_val}\n\n"
                f"🎯 <i>تطابقت شروط الهبوط والزخم والسيولة!</i>"
            )
            return msg

    except Exception as e:
        print(f"خطأ في فحص السهم {ticker_symbol}: {e}")

    return None

if __name__ == "__main__":
    print("بدء فحص قائمة الأسهم...")
    for symbol in WATCHLIST:
        alert = analyze_stock(symbol)
        if alert:
            send_telegram_msg(alert)
            print(f"تم إرسال تنبيه للسهم: {symbol}")
        else:
            print(f"السهم {symbol}: لا توجد إشارة حالية.")
