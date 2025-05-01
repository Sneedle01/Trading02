import time

from core.bot import TradingBot

if __name__ == "__main__":
    bot = TradingBot()
    interval = bot.config.get("check_interval_minutes", 5)

    while True:
        bot.run()
        print(f"⏳ Warte {interval} Minuten bis zur nächsten Prüfung...\n")
        time.sleep(interval * 60)
