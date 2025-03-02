# crypto_pulse/exchange.py
import requests


class ExchangeInterface:
    def __init__(self, exchange_name="binance"):
        self.exchange_name = exchange_name

    def get_ticker(self, symbol):
        # Use public Binance API; no API key required
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.replace('/', '')}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error fetching ticker data.")
            return None

    def place_order(self, symbol, side, quantity, order_type="market"):
        # Placeholder: Simulated order since no authentication is provided
        print(f"{order_type.capitalize()} {side.capitalize()} order for {quantity} {symbol} (simulated) executed.")
        return {"status": "simulated order", "symbol": symbol, "side": side, "quantity": quantity}

    def get_historical_prices(self, symbol, interval='1h', limit=50):
        """
        Fetch historical price data using Binance's public Klines API.
        The endpoint returns candlestick data; we extract the closing prices.
        """
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol.replace('/', '')}&interval={interval}&limit={limit}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            closing_prices = [float(kline[4]) for kline in data]
            return closing_prices
        else:
            print("Error fetching historical price data.")
            return None

    def get_orderbook(self, symbol, limit=5):
        """
        Fetch order book data using Binance's public depth API.
        Returns a dictionary with 'bids' and 'asks' lists,
        where each entry is a [price, quantity] pair.
        """
        url = f"https://api.binance.com/api/v3/depth?symbol={symbol.replace('/', '')}&limit={limit}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            orderbook = {
                "bids": [[float(price), float(qty)] for price, qty in data.get("bids", [])],
                "asks": [[float(price), float(qty)] for price, qty in data.get("asks", [])]
            }
            return orderbook
        else:
            print("Error fetching order book data.")
            return None
