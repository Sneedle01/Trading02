import unittest
import pandas as pd
from core.strategy import StrategyRSIMACrossover


class TestStrategyRSIMACrossover(unittest.TestCase):

    def test_entry_signal_should_trigger_on_valid_conditions(self):
        close_prices = [120] * 10 + [100] * 10 + [80] * 10 + [80] * 20
        volumes = [900] * 30 + [3100] * 19 + [3400]  # Volumen > Durchschnitt

        df = pd.DataFrame({"close": close_prices, "volume": volumes})
        strategy = StrategyRSIMACrossover(df, min_rsi=35, min_ma_gap=-13.0)
        result = strategy.check_entry_signal(debug=True)

        self.assertTrue(result, "Erwartet: True – RSI, MA und Volumen-Bedingungen erfüllt.")

    def test_entry_signal_should_not_trigger_on_flat_rsi(self):
        df = pd.DataFrame({
            "close": [100] * 50,
            "volume": [1500] * 50
        })
        strategy = StrategyRSIMACrossover(df)
        result = strategy.check_entry_signal(debug=True)

        self.assertFalse(result, "Erwartet: False, RSI ist nicht unter 35.")


if __name__ == "__main__":
    unittest.main()
