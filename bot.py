# crypto_pulse/bot.py
import time
import numpy as np
from config import Config
from exchange import ExchangeInterface
from strategy import ExtendedStrategy

class CryptoPulseBot:
    def __init__(self):
        self.config = Config()
        self.exchange = ExchangeInterface(
            exchange_name=self.config.get("exchange", "binance")
        )
        self.symbol = self.config.get("trade_pair", "BTC/USDT")
        # Use the extended strategy instead of the basic one
        self.strategy = ExtendedStrategy()
        self.order_volume = self.config.get("order_volume", 0.001)
        self.sleep_time = self.config.get("sleep_time", 10)

    def fetch_historical_prices(self, limit=50):
        # Attempt to fetch real historical data using the public API
        prices = self.exchange.get_historical_prices(self.symbol, interval='1h', limit=limit)
        if prices is None:
            print("Using simulated price data as fallback.")
            prices = np.linspace(30000, 35000, limit).tolist()
        return prices

    def run(self):
        print("CryptoPulseBot started.")
        while True:
            prices = self.fetch_historical_prices()
            # Fetch order book data as well
            orderbook = self.exchange.get_orderbook(self.symbol, limit=5)
            signal, details = self.strategy.generate_signal(prices, orderbook=orderbook)
            print(f"Current trading signal: {signal}")
            print("Indicator details:", details)
            if signal == "buy":
                self.exchange.place_order(self.symbol, "buy", self.order_volume)
            elif signal == "sell":
                self.exchange.place_order(self.symbol, "sell", self.order_volume)
            time.sleep(self.sleep_time)

if __name__ == "__main__":
    bot = CryptoPulseBot()
    bot.run()
