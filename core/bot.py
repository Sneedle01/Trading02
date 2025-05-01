import os
import json
import pandas as pd
from dotenv import load_dotenv
from bybit_api import BybitClient
from core.strategy import StrategyRSIMACrossover


class TradingBot:
    def __init__(self, config_path: str = None):
        load_dotenv()
        config_path = config_path or os.path.join(os.path.dirname(__file__), "../config/config.json")
        with open(config_path, "r") as f:
            self.config = json.load(f)
        self.client = BybitClient()

    def fetch_candles(self, symbol: str, timeframe="1h", limit=100) -> pd.DataFrame:
        candles = self.client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        return df

    def calculate_order_size(self, symbol: str, price: float) -> float:
        balance = self.client.get_balance("USDT")
        risk_amount = balance * self.config["risk_per_trade"]
        amount = (risk_amount * self.config["leverage"]) / price
        return round(amount, 4)

    def place_order(self, symbol: str, side: str, amount: float):
        tp_percent = self.config.get("take_profit", 0.07)
        sl_percent = self.config.get("stop_loss", 0.03)
        price = self.client.fetch_ticker(symbol)["last"]

        # Menge auf gültige Step Size anpassen
        min_qty = self.client.get_market_min_qty(symbol)
        amount = self.client.adjust_to_step_size(symbol, amount)

        if amount < min_qty:
            print(f"❌ Abbruch: Berechnete Menge {amount} liegt unter Mindestmenge {min_qty} für {symbol}")
            return

        tp_price = round(price * (1 + tp_percent), 6)
        sl_price = round(price * (1 - sl_percent), 6)

        if self.config.get("paper_trading", True):
            print(f"🧾 PAPER TRADE: {side.upper()} {amount} {symbol} | TP: {tp_price} | SL: {sl_price}")
        else:
            print(f"📈 REAL ORDER: {side.upper()} {amount} {symbol} | TP: {tp_price} | SL: {sl_price}")
            self.client.create_market_order(symbol, side, amount, tp_price, sl_price)

    def run(self):
        print(f"🛠 Paper-Trading aktiv: {self.config.get('paper_trading', True)}")
        # if not self.config.get("paper_trading", True):
        # confirm = input("🚨 Paper-Trading ist deaktiviert. Echten Trade ausführen? (ja/nein): ")
        # if confirm.strip().lower() != "ja":
        #     print("❌ Abbruch.")
        #     return
        best_score = -1
        best_symbol = None
        best_df = None

        for symbol in self.config["symbols"]:
            print(f"\n🔍 Prüfe {symbol}...")
            df_raw = self.fetch_candles(symbol, timeframe=self.config.get("timeframe", "15m"))
            strategy = StrategyRSIMACrossover(df_raw, min_rsi=50, min_ma_gap=-13.0, ignore_volume=False)
            df = strategy.df
            strategy = StrategyRSIMACrossover(df, min_rsi=50, min_ma_gap=-13.0, ignore_volume=False)

            latest = df.iloc[-1]
            ma_diff = latest['ma20'] - latest['ma50']
            rsi_check = latest['rsi'] > strategy.min_rsi
            ma_check = ma_diff > strategy.min_ma_gap
            volume_check = True if strategy.ignore_volume else latest['volume'] > latest['volume_avg'] * strategy.min_volume_ratio

            score = int(rsi_check) + int(ma_check) + int(volume_check)

            print("--- DEBUG STRATEGY SIGNAL ---")
            print(latest[['rsi', 'ma20', 'ma50', 'volume', 'volume_avg']])
            print(f"Score: {score}/3 | RSI ok: {rsi_check} | MA Gap ok: {ma_check} | Volume ok: {volume_check}")

            if score > best_score:
                best_score = score
                best_symbol = symbol
                best_df = df

        if best_score == 3 and best_symbol:
            print(f"\n🚀 Beste Chancen bei {best_symbol} mit Score {best_score}/3")
            last_price = best_df.iloc[-1]["close"]
            amount = self.calculate_order_size(best_symbol, last_price)
            self.place_order(best_symbol, "buy", amount)
        else:
            print("⏳ Kein Symbol erfüllt alle Kriterien vollständig.")


if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
