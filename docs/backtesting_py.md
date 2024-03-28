# Backtesting.py

The backtesting.py library is a Python package designed for backtesting trading strategies with minimal effort. It 
stands out for its simplicity, flexibility, and powerful features, making it an excellent choice for traders and 
researchers who wish to test their strategies against historical data. Below is a summary of its key capabilities 
followed by an example code snippet.

## Key Capabilities of backtesting.py
- Ease of Use: The library is designed to be intuitive, allowing users to quickly set up and run backtests without extensive setup.
- Strategy Definition: Users can define trading strategies by simply extending the Strategy class and implementing their logic in the init and next methods.
- Comprehensive Data Support: It supports backtesting on any financial instrument's historical data that can be represented in a tabular format, including stocks, forex, crypto, etc.
- Built-in Indicators and Statistics: The library comes with numerous built-in technical indicators and statistics calculations, facilitating comprehensive strategy analysis.
- Performance Visualization: Provides detailed visualization tools to analyze the performance of strategies, including equity curves, drawdowns, and even per-trade information.
- Optimization Framework: Offers an optimization API to fine-tune strategy parameters, helping to find the most profitable settings.

## Strategy Implementation
This example demonstrates how to backtest a simple moving average crossover strategy using backtesting.py. 
The strategy buys the asset when the short moving average crosses above the long moving average and sells when the 
opposite crossover occurs.

1. Import Necessary Components
Begin by importing the `Strategy` class from `backtesting.py`, along with any other necessary components such as 
indicators or the data you intend to use for backtesting.

```python
from backtesting import Strategy
from backtesting.lib import crossover

# example function return the moving average
from indicators import SMA
```

2. Define Your Strategy Class
Your strategy class should inherit from Strategy. Within the class, you will define two main methods: init() and next().

```python
class MyStrategy(Strategy):
    # Your strategy definition goes here
```

3. Initialize Strategy Components in init()
The init() method is called when your strategy is instantiated. It's used for initializing indicators, signals, and any 
other necessary setup. Use the self.I() method to declare indicators, ensuring they're dynamically updated.


```python
def init(self):
        # Define a simple moving average (SMA) indicator
        self.sma = self.I(SMA, self.data.Close, period=15)
```

4. Define Trading Logic in next()
The next() method is called for each bar of the data. This is where you implement the trading logic, making decisions 
based on the current and historical data points. Use self.buy() or self.sell() to execute trades.
```python
def next(self):
    # If the close price crosses above the SMA, buy
    if self.data.Close[-1] > self.sma[-1]:
        self.buy()
    # If the close price crosses below the SMA, sell
    elif self.data.Close[-1] < self.sma[-1]:
        self.sell()
```

## Nuances and Best Practices
- Using self.I() for Indicators: Always use self.I() to define indicators in the init() method. This ensures indicators 
are properly updated and aligned with the data.

- Accessing Data: Use self.data to access current and historical data. For example, self.data.Close[-1] refers to the 
latest close price. The data object provides access to open, high, low, close prices (OHLC), and volume.

- Order Management: The methods self.buy() and self.sell() place buy and sell orders, respectively. You can specify the 
amount, price, and other order parameters. By default, orders are executed at the next available price.

- Exclusive Orders: By setting exclusive_orders=True in the Backtest class, you ensure that only one position 
(long or short) can be open at a time, which is a common scenario in strategy testing.

- Handling State and Memory: You can define custom attributes in your strategy class to keep track of state or to store 
calculations for use in the next() method.