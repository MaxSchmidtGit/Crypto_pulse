# crypto_pulse/strategy.py
import numpy as np

class ExtendedStrategy:
    def __init__(self,
                 rsi_period=14, rsi_overbought=70, rsi_oversold=30,
                 macd_fast=12, macd_slow=26, macd_signal=9):
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal

    def compute_rsi(self, prices):
        prices = np.array(prices)
        deltas = np.diff(prices)
        seed = deltas[:self.rsi_period]
        up = seed[seed >= 0].sum() / self.rsi_period
        down = -seed[seed < 0].sum() / self.rsi_period
        rs = up / down if down != 0 else 0
        rsi = np.zeros_like(prices)
        rsi[:self.rsi_period] = 50  # Initial default value
        for i in range(self.rsi_period, len(prices)):
            delta = deltas[i - 1]
            upval = max(delta, 0)
            downval = -min(delta, 0)
            up = (up * (self.rsi_period - 1) + upval) / self.rsi_period
            down = (down * (self.rsi_period - 1) + downval) / self.rsi_period
            rs = up / down if down != 0 else 0
            rsi[i] = 100 - (100 / (1 + rs))
        return rsi

    def compute_ema(self, prices, period):
        prices = np.array(prices)
        ema = np.zeros_like(prices)
        multiplier = 2 / (period + 1)
        ema[0] = prices[0]
        for i in range(1, len(prices)):
            ema[i] = (prices[i] - ema[i-1]) * multiplier + ema[i-1]
        return ema

    def compute_macd(self, prices):
        ema_fast = self.compute_ema(prices, self.macd_fast)
        ema_slow = self.compute_ema(prices, self.macd_slow)
        macd_line = ema_fast - ema_slow
        signal_line = self.compute_ema(macd_line, self.macd_signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def compute_fibonacci_levels(self, prices):
        # Calculate Fibonacci retracement levels based on high and low prices
        high = max(prices)
        low = min(prices)
        diff = high - low
        levels = {
            "0.0%": high,
            "23.6%": high - 0.236 * diff,
            "38.2%": high - 0.382 * diff,
            "50.0%": high - 0.5 * diff,
            "61.8%": high - 0.618 * diff,
            "78.6%": high - 0.786 * diff,
            "100.0%": low
        }
        return levels

    def compute_orderbook_indicator(self, orderbook):
        """
        Calculate a simple orderbook indicator.
        Expects a dictionary with "bids" and "asks" (list of [price, volume] pairs).
        A positive value indicates buying pressure, negative indicates selling pressure.
        """
        bids = orderbook.get("bids", [])
        asks = orderbook.get("asks", [])
        total_bid = sum(bid[1] for bid in bids)
        total_ask = sum(ask[1] for ask in asks)
        if total_bid + total_ask == 0:
            return 0
        return (total_bid - total_ask) / (total_bid + total_ask)

    def compute_bollinger_bands(self, prices, period=20, num_std=2):
        prices = np.array(prices)
        if len(prices) < period:
            period = len(prices)
        sma = np.convolve(prices, np.ones(period)/period, mode='valid')
        std = np.array([np.std(prices[i-period:i]) for i in range(period, len(prices)+1)])
        upper = sma + num_std * std
        lower = sma - num_std * std
        # Return the most recent values
        return sma[-1], upper[-1], lower[-1]

    def risk_management(self, current_price, atr, risk_multiplier=1.5, reward_multiplier=2):
        # Calculate stop-loss and take-profit levels based on current price and ATR
        stop_loss = current_price - risk_multiplier * atr
        take_profit = current_price + reward_multiplier * atr
        return stop_loss, take_profit

    def generate_signal(self, prices, orderbook=None):
        """
        Combines multiple indicators:
          - RSI for overbought/oversold conditions
          - MACD as a trend indicator
          - Bollinger Bands to assess volatility
          - Fibonacci levels to identify key support/resistance zones
          - Orderbook data (if available) for additional buying/selling pressure

        Each indicator casts a vote (1 for buy, -1 for sell, 0 for hold), which are weighted to form an overall signal.
        Also calculates dynamic risk management parameters (stop-loss and take-profit levels) based on an ATR proxy.
        """
        # RSI calculation and vote
        rsi = self.compute_rsi(prices)
        current_rsi = rsi[-1]
        if current_rsi < self.rsi_oversold:
            rsi_vote = 1
        elif current_rsi > self.rsi_overbought:
            rsi_vote = -1
        else:
            rsi_vote = 0

        # MACD calculation and vote
        macd_line, signal_line, histogram = self.compute_macd(prices)
        macd_vote = 1 if histogram[-1] > 0 else -1

        # Orderbook vote (if orderbook data is provided)
        if orderbook:
            orderbook_pressure = self.compute_orderbook_indicator(orderbook)
            if orderbook_pressure > 0.1:
                orderbook_vote = 1
            elif orderbook_pressure < -0.1:
                orderbook_vote = -1
            else:
                orderbook_vote = 0
        else:
            orderbook_vote = 0
            orderbook_pressure = None

        # Bollinger Bands calculation and vote
        sma, upper, lower = self.compute_bollinger_bands(prices)
        current_price = prices[-1]
        if current_price < lower:
            bollinger_vote = 1
        elif current_price > upper:
            bollinger_vote = -1
        else:
            bollinger_vote = 0

        # Weighted signals
        weights = {"rsi": 0.3, "macd": 0.3, "orderbook": 0.2, "bollinger": 0.2}
        weighted_score = (rsi_vote * weights["rsi"] +
                          macd_vote * weights["macd"] +
                          orderbook_vote * weights["orderbook"] +
                          bollinger_vote * weights["bollinger"])

        overall_signal = "hold"
        if weighted_score > 0.3:
            overall_signal = "buy"
        elif weighted_score < -0.3:
            overall_signal = "sell"

        # Dynamic risk management using an ATR proxy (Average True Range)
        atr = (max(prices[-14:]) - min(prices[-14:])) / 14
        stop_loss, take_profit = self.risk_management(current_price, atr)

        return overall_signal, {
            "weighted_score": weighted_score,
            "rsi": current_rsi,
            "macd_histogram": histogram[-1],
            "orderbook_pressure": orderbook_pressure,
            "bollinger": {"sma": sma, "upper": upper, "lower": lower},
            "atr": atr,
            "risk_management": {"stop_loss": stop_loss, "take_profit": take_profit},
            "fibonacci_levels": self.compute_fibonacci_levels(prices)
        }

    def backtest(self, prices):
        """
        A simple backtesting function that calculates a signal for each time point,
        starting from an index determined by the longest indicator window.
        """
        min_index = max(self.rsi_period, self.macd_slow, 20)
        signals = []
        for i in range(min_index, len(prices)):
            signal, _ = self.generate_signal(prices[:i+1])
            signals.append(signal)
        return signals
