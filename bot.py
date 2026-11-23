import os
import time
import requests
import pandas as pd

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOLS = {
    "BTCUSDT": "BITCOIN",
    "PAXGUSDT": "GOLD"
}

def send_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    }, timeout=15)

def analyze(symbol, name):
    url = "https://api.binance.com/api/v3/klines"
    data = requests.get(url, params={
        "symbol": symbol,
        "interval": "5m",
        "limit": 100
    }, timeout=15).json()

    df = pd.DataFrame(data)
    close = df[4].astype(float)

    ema9 = close.ewm(span=9).mean()
    ema21 = close.ewm(span=21).mean()

    price = close.iloc[-1]

    if ema9.iloc[-2] <= ema21.iloc[-2] and ema9.iloc[-1] > ema21.iloc[-1]:
        signal = "BUY"
    elif ema9.iloc[-2] >= ema21.iloc[-2] and ema9.iloc[-1] < ema21.iloc[-1]:
        signal = "SELL"
    else:
        return

    sl = price * (0.995 if signal == "BUY" else 1.005)
    tp1 = price * (1.005 if signal == "BUY" else 0.995)
    tp2 = price * (1.010 if signal == "BUY" else 0.990)
    tp3 = price * (1.015 if signal == "BUY" else 0.985)

    send_message(
        f"{name}\n"
        f"Signal: {signal}\n"
        f"Entry: {price:.4f}\n"
        f"SL: {sl:.4f}\n"
        f"TP1: {tp1:.4f}\n"
        f"TP2: {tp2:.4f}\n"
        f"TP3: {tp3:.4f}\n"
        f"Timeframe: 5m"
    )

def main():
    while True:
        for symbol, name in SYMBOLS.items():
            try:
                analyze(symbol, name)
            except Exception as e:
                print(name, e)
        time.sleep(300)

if __name__ == "__main__":
    main()
