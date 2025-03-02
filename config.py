# crypto_pulse/config.py
import json

class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.data = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Configuration file not found, using default values.")
            return {
                "exchange": "binance",
                "trade_pair": "BTC/USDT",
                "strategy": "extended",
                "order_volume": 0.001,
                "sleep_time": 10
            }

    def get(self, key, default=None):
        return self.data.get(key, default)
