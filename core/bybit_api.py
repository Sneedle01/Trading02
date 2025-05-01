import math
import os
from dotenv import load_dotenv
import ccxt
from typing import Optional


class BybitClient:
    def __init__(self):
        load_dotenv()
        self.exchange = ccxt.bybit({
            "apiKey": os.getenv("BYBIT_API_KEY", ""),
            "secret": os.getenv("BYBIT_API_SECRET", ""),
            "enableRateLimit": True,
            "options": {
                "defaultType": "future"  # wichtig: standardmäßig Futures
            }
        })

    def get_market_min_qty(self, symbol: str) -> float:
        market = self.exchange.market(symbol)
        return market.get("limits", {}).get("amount", {}).get("min", 0)

    def adjust_to_step_size(self, symbol: str, amount: float) -> float:
        market = self.exchange.market(symbol)
        step = market.get("limits", {}).get("amount", {}).get("min", 0.001)
        precision = market.get("precision", {}).get("amount", 6)
        return math.floor(amount / step) * step

    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100):
        return self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def fetch_ticker(self, symbol: str):
        return self.exchange.fetch_ticker(symbol)

    def get_balance(self, asset: str = "USDT") -> float:
        balance = self.exchange.fetch_balance()
        return balance["total"].get(asset, 0.0)

    def create_market_order(
            self,
            symbol: str,
            side: str,
            amount: float,
            tp: Optional[float] = None,
            sl: Optional[float] = None
    ):
        market = self.exchange.market(symbol)

        # 1. Market Order ausführen
        market_order = self.exchange.create_order(
            symbol=market['id'],
            type="market",
            side=side,
            amount=amount,
            params={
                "category": "linear"
            }
        )

        # 2. TP/SL als separate reduceOnly Orders
        opposite = "sell" if side == "buy" else "buy"

        try:
            if tp is not None:
                self.exchange.create_order(
                    symbol=market['id'],
                    type="limit",
                    side=opposite,
                    amount=amount,
                    price=tp,
                    params={
                        "reduceOnly": True,
                        "category": "linear",
                        "timeInForce": "GoodTillCancel"
                    }
                )
            if sl is not None:
                self.exchange.create_order(
                    symbol=market['id'],
                    type="stop_market",
                    side=opposite,
                    amount=amount,
                    params={
                        "triggerPrice": sl,
                        "reduceOnly": True,
                        "category": "linear"
                    }
                )
        except Exception as e:
            print(f"⚠️ Warnung: TP/SL konnten nicht gesetzt werden: {e}")

        return market_order
