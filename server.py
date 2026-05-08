from fastapi import FastAPI
import requests, time, os
from datetime import datetime
import pytz

app = FastAPI()

# === SETTING BOT CRYPTO BINANCE ===
PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]  # ← 3 koin lu
TIMEFRAME = "15min"  # M15 biar gak kebanyakan sinyal. Ganti "5min" kalo mau agresif
TP1_PERCENT = 1.5    # TP1 = 1.5% dari entry. BTC $80k = $1200 = 18jt lot 1 BTC
SL_PERCENT = 0.7     # SL = 0.7%. RR 1:2.14 
MIN_SCORE = 3        # Minimal skor setup 3 baru kirim WA

# === API KEY LU ===
TWELVE_API = "0aa470b9363a4dcdb91b79fe20c67453"
WAHA_URL = "https://gate.whapi.cloud"
WAHA_TOKEN = "R4bWD3lxpKwND6kJrsVSPDZ0w1H5jT7l"
WAHA_TO = "6281333903800@s.whatsapp.net"

def send_wa(msg):
    url = f"{WAHA_URL}/messages/text"
    headers = {"Authorization": f"Bearer {WAHA_TOKEN}", "Content-Type": "application/json"}
    data = {"to": WAHA_TO, "body": msg}
    try: requests.post(url, headers=headers, json=data, timeout=10)
    except: pass

def get_price(symbol):
    try:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_API}"
        r = requests.get(url, timeout=10).json()
        return float(r['price'])
    except: return None

def get_candles(symbol):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={TIMEFRAME}&outputsize=50&apikey={TWELVE_API}"
        r = requests.get(url, timeout=10).json()
        return r['values'][::-1]  # dibalik biar urut lama→baru
    except: return []

def analyze_crypto(symbol):
    candles = get_candles(symbol)
    if len(candles) < 30: return None
    
    closes = [float(c['close']) for c in candles]
    highs = [float(c['high']) for c in candles]
    lows = [float(c['low']) for c in candles]
    
    price = closes[-1]
    ma20 = sum(closes[-20:]) / 20
    ma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else ma20
    
    # Setup LONG: Breakout + di atas MA20 + MA20 > MA50
    score = 0
    if price > max(highs[-10:-1]): score += 2  # Breakout high 10 candle
    if price > ma20: score += 1
    if ma20 > ma50: score += 1
    
    if score >= MIN_SCORE:
        sl = price * (1 - SL_PERCENT/100)
        tp1 = price * (1 + TP1_PERCENT/100)
        return {
            "type": "LONG", "price": price, "sl": sl, "tp1": tp1, 
            "score": score, "pair": symbol.replace("USDT", "/USDT")
        }
    
    # Setup SHORT: Breakdown + di bawah MA20 
    score = 0
    if price < min(lows[-10:-1]): score += 2  # Breakdown low 10 candle  
    if price < ma20: score += 1
    if ma20 < ma50: score += 1
    
    if score >= MIN_SCORE:
        sl = price * (1 + SL_PERCENT/100)
        tp1 = price * (1 - TP1_PERCENT/100)
        return {
            "type": "SHORT", "price": price, "sl": sl, "tp1": tp1,
            "score": score, "pair": symbol.replace("USDT", "/USDT")
        }
    return None

def scan_all():
    jakarta = pytz.timezone('Asia/Jakarta')
    now = datetime.now(jakarta).strftime("%H:%M WIB")
    
    for pair in PAIRS:
        signal = analyze_crypto(pair)
        if signal:
            msg = f"🚀 {signal['type']} {signal['pair']}\n"
            msg += f"Entry: ${signal['price']:.2f}\n"
            msg += f"SL: ${signal['sl']:.2f}\n" 
            msg += f"TP1: ${signal['tp1']:.2f}\n"
            msg += f"Score: {signal['score']}/4 | {now}\n"
            msg += f"OP manual di Binance ya bro 🔥"
            send_wa(msg)
            time.sleep(2)
    return {"status": "scan done", "pairs": PAIRS}

@app.get("/")
def home(): return {"status": "Bot Signal Crypto Binance Online 24 Jam", "pairs": PAIRS}

@app.get("/scan") 
def scan(): return scan_all()

if __name__ == "__main__":
    import uvicorn
    send_wa("✅ Bot Signal Crypto BTC/ETH/SOL Online bro. Siap cari setup A+")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
