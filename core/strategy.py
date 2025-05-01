import pandas as pd
from ta.momentum import RSIIndicator


class StrategyRSIMACrossover:
    def __init__(self, df: pd.DataFrame, min_rsi: float = 50, min_ma_gap: float = 0.0, min_volume_ratio: float = 0.9, ignore_volume: bool = False):
        self.df = df.copy()
        self.min_rsi = min_rsi
        self.min_ma_gap = min_ma_gap
        self.min_volume_ratio = min_volume_ratio
        self.ignore_volume = ignore_volume

        if len(self.df) < 50:
            raise ValueError("Nicht genug Daten: mindestens 50 Zeilen erforderlich für MA50.")

        self._apply_indicators()

    def _apply_indicators(self):
        self.df['rsi'] = RSIIndicator(close=self.df['close']).rsi()
        self.df['ma20'] = self.df['close'].rolling(window=20).mean()
        self.df['ma50'] = self.df['close'].rolling(window=50).mean()
        self.df['volume_avg'] = self.df['volume'].rolling(window=20).mean()

    def check_entry_signal(self, debug: bool = False) -> bool:
        latest = self.df.iloc[-1]

        ma_diff = latest['ma20'] - latest['ma50']
        rsi_check = latest['rsi'] > self.min_rsi
        ma_check = ma_diff > self.min_ma_gap
        volume_check = latest['volume'] > latest['volume_avg'] * self.min_volume_ratio if not self.ignore_volume else True

        if debug:
            print("--- DEBUG STRATEGY SIGNAL ---")
            print(latest[['rsi', 'ma20', 'ma50', 'volume', 'volume_avg']])
            print(f"RSI ok: {rsi_check} | MA Gap ok: {ma_check} | Volume ok: {volume_check}")
            print(f"RSI={latest['rsi']:.2f}, MA Gap={ma_diff:.2f}, Vol={latest['volume']} > {latest['volume_avg'] * self.min_volume_ratio:.2f}")

        if pd.isna(ma_diff) or pd.isna(latest['rsi']) or pd.isna(latest['volume_avg']):
            return False

        return rsi_check and ma_check and volume_check
