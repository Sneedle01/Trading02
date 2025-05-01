import ccxt
from dotenv import load_dotenv
import os

# ENV laden
load_dotenv()

api_key = os.getenv("BYBIT_API_KEY")
api_secret = os.getenv("BYBIT_API_SECRET")

if not api_key or not api_secret:
    raise ValueError("API Key oder Secret fehlt – bitte .env prüfen!")

exchange = ccxt.bybit({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'recvWindow': 10000  # Zeitabweichungstoleranz erhöhen
    }
})

try:
    balance = exchange.fetch_balance()
    usdt_balance = balance.get('total', {}).get('USDT')
    if usdt_balance is not None:
        print(f"✅ Verbindung erfolgreich – USDT Balance: {usdt_balance}")
    else:
        print("⚠️  Keine USDT-Balance gefunden oder API liefert keine Werte.")
except Exception as e:
    print("❌ Fehler bei Verbindung:", str(e))
