#! C:\Users\Asus\Desktop\prog\algo-trading\venv\Scripts\python.exe

import sys
import os

# Construct the path to the root directory
root_path = os.path.abspath(
	os.path.join(os.path.dirname(__file__), '..', '..')
)

# Append the path to sys.path only if it is not already included
if root_path not in sys.path:
	sys.path.append(root_path)

from backtesting import Strategy
from backtesting import Backtest
from backtesting.lib import crossover
from backtesting.test import GOOG
import datetime

from helpers.indicators import sma, rsi, bbands


class BBandRsi(Strategy):
	"""
	Entry Criteria:
	- Buy Signal: Price closes below the lower Bollinger Band after at least 6 consecutive days where the daily low is
	above the 200-day SMA.
	- Sell Signal: Price closes above the upper Bollinger Band after at least 6 consecutive days where the daily high is
	below the 200-day SMA.

	Exit Criteria:
	- A trade is exited if it exceeds 10 days in duration or if RSI crosses above 70 (for longs) or drops below
	30 (for shorts), suggesting a potential reversal or overextended move.

	Indicators Used:
	- SMA (200-day) for trend direction.
	- RSI (2-day) to identify overbought or oversold conditions.
	- Bollinger Bands (20-day, 2.5 standard deviations) to determine volatility and trading bounds.
	"""
	# indicator parameters
	rsi_length = 2           # candles
	sma_length = 200         # candles
	bbands_length = 20       # candles
	bbands_std = 2.5         # standard deviations

	# strategy parameters
	order_time_max = 5       # maximum duration of an active order [days]
	trade_time_max = 10      # maximum duration of a trade [days]
	rsi_upper_limit = 70     # RSI upper limit for keeping a long [%]
	rsi_lower_limit = 30     # RSI lower limit for keeping a short (preferably 100 - rsi_upper_limit) [%]
	order_size = 99          # Fraction of cash to use on new order [%]
	stoploss_factor = 5     # Fraction of the order limit to set the stop loss [%]
	buy_limit_offset = 0     # Distance btw the candle close and the buy order limit [% of close]
	sell_limit_offset = 0    # Distance btw the candle close and the sell order limit [% of close]

	# list of datetime of the current order initialization
	orders_datetime = []

	def init(self):
		self.sma = self.I(sma, self.data.Close, self.sma_length)
		self.rsi = self.I(rsi, self.data.Close, self.rsi_length)
		self.bbands = self.I(bbands, self.data.Close, self.bbands_length, self.bbands_std)
		self.consecutive_days_above_sma = 0  # Counter for days low is above SMA
		self.consecutive_days_below_sma = 0  # Counter for days high is below SMA

	def next(self):
		lower_band = self.bbands[0]
		upper_band = self.bbands[2]

		# Update the counter for days low is above the SMA
		if self.data.Low[-1] > self.sma:
			self.consecutive_days_above_sma += 1
		else:
			self.consecutive_days_above_sma = 0

		# Update the counter for days high is below the SMA
		if self.data.High[-1] < self.sma:
			self.consecutive_days_below_sma += 1
		else:
			self.consecutive_days_below_sma = 0

		# Define buying and selling conditions
		buy_signal = self.consecutive_days_above_sma >= 6 and lower_band > self.data.Close[-1]
		sell_signal = self.consecutive_days_below_sma >= 6 and self.data.Close[-1] > upper_band

		# if an order surpasses max days active, cancel it.
		for _ in range(0, len(self.orders)):
			if self.data.index[-1] - self.orders_datetime[0] > datetime.timedelta(days=self.order_time_max):
				self.orders[0].cancel()
				self.orders_datetime.pop(0)

		if len(self.trades) > 0:
			# if a trade remains open for more than the defined maximum, close it.
			if self.data.index[-1] - self.trades[-1].entry_time >= datetime.timedelta(days=self.trade_time_max):
				self.trades[-1].close()

			# if a long has an rsi level above the defined limit, close it
			if self.trades[-1].is_long and self.rsi >= self.rsi_upper_limit:
				self.trades[-1].close()

			# if a shot has an rsi level below the defined limit, close it
			elif self.trades[-1].is_short and self.rsi <= self.rsi_lower_limit:
				self.trades[-1].close()

		# only set new buy or sell orders if there aren't any open trades
		if not len(self.trades):

			# if the high price is above the sma and the close price is below the lower bband, buy
			if buy_signal:
				buy_limit = self.data.Close[-1] * (1 - self.buy_limit_offset / 100)
				stop_loss = buy_limit * (1 - self.stoploss_factor / 100)
				order_size = self.order_size / 100

				# Cancel all previous orders
				for _ in range(0, len(self.orders)):
					self.orders[0].cancel()
					self.orders_datetime.pop(0)

				# set buy order and stop loss
				self.buy(
					limit=buy_limit,
					sl=stop_loss,
					size=order_size
				)
				self.orders_datetime.append(self.data.index[-1])

			elif sell_signal:
				sell_limit = self.data.Close[-1] * (1 - self.buy_limit_offset / 100)
				stop_loss = sell_limit * (1 + self.stoploss_factor / 100)
				order_size = self.order_size / 100

				# Cancel previous orders
				for _ in range(0, len(self.orders)):
					self.orders[0].cancel()
					self.orders_datetime.pop(0)

				# Add new replacement order
				self.sell(
					limit=sell_limit,
					sl=stop_loss,
					size=order_size
				)
				self.orders_datetime.append(self.data.index[-1])


if __name__ == '__main__':
	from helpers.functions import get_ohlc_data
	import warnings

	warnings.filterwarnings('ignore')

	# Define the ticker symbol and the time period you're interested in
	ticker_ = "^RUI"
	# ticker_ = "AAPL"  # Example: Apple Inc.
	# ticker_ = "GOOG"  # Example: Apple Inc.
	# ticker_ = "^BVSP"  # Example: Apple Inc.

	end_date_ = '2021-01-05'  # End date for the data
	start_date_ = '2011-01-05'  # Start date for the data

	interval_ = '1d'  # ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

	ohlc_data = get_ohlc_data(
		ticker_,
		start_date_,
		end_date_,
		interval_
	)

	# Setup and run the backtest
	bt = Backtest(ohlc_data, BBandRsi, cash=10_000, margin=1, commission=.00)

	# Execute the backtest
	results = bt.run()

	# Print the results
	print(results)

	# Optionally, plot the results
	bt.plot()
