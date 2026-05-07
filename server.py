from fastapi import FastAPI
import uvicorn, os, httpx
from datetime import datetime

app = FastAPI()
API_KEY = os.getenv("TWELVE_API_KEY")
WA_NUMBER = os.getenv("WA_NUMBER")

@app.get("/")
def root():
    return {"status": "Bot Signal FFX Online 24 Jam", "time": str(datetime.now())}

@app.get("/scan")
async def scan():
    return {"status": "scanning XAUUSD BTCUSD GBPJPY"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
