from backtesting import Backtest, Strategy

from helpers.indicators import ema


class NineOne(Strategy):
	"""
	Entry Criteria:
	- Buy Signal: The 9-period exponential moving average (EMA) turns upward, confirmed by a candle closing above
	the previous high. The entry is executed at a tick above the high of this candle.

	Exit Criteria:
	- The 9-period EMA turns downward after an entry has been made. When this downward turn is confirmed, the exit is
	set at a tick below the low of the candle that caused the EMA to turn down. The trade is exited if the price crosses
	below this exit price.

	Indicators Used:
	- EMA (Exponential Moving Average): A 9-period EMA is used to gauge the short-term trend direction and trigger entry
	and exit points based on its turning points.
	"""
	ema_length = 9

	def init(self):
		self.ema = self.I(ema, self.data.Close, self.ema_length)
		self.entry_price = None
		self.exit_price = None
		self.low_since_entry = None

	def next(self):
		price = self.data.Close[-1]
		high = self.data.High[-1]
		low = self.data.Low[-1]

		# Condition to enter a trade
		if not self.position:
			# If the moving average has started to rise, activate the buy signal
			if (self.ema[-1] > self.ema[-2]) and (self.ema[-2] < self.ema[-3]):
				self.entry_price = high + 0.01  # Buy with a stop loss at the lowest low since entry
				self.low_since_entry = low  # Reset the entry price after buying
			# If the moving average has fallen, deactivate
			elif self.ema[-2] > self.ema[-1]:
				self.entry_price = None  # Reset the entry condition
		else:
			# Update the lowest low since entry while in position
			if low < self.low_since_entry:
				self.low_since_entry = low

		# Execute the entry
		if self.entry_price and price > self.entry_price:
			if not self.position:
				self.buy(sl=self.low_since_entry)  # Buy with a stop loss at the lowest low since entry
			self.entry_price = None  # Reset the entry price after buying

		# Condition to exit the trade
		if self.position:
			# If the moving average has started to decline, activate the exit signal
			if (self.ema[-1] < self.ema[-2]) and (self.ema[-2] > self.ema[-3]):
				self.exit_price = low + 0.01  # Set the exit price one tick below the current low
			# If the moving average has risen again, deactivate
			elif self.ema[-2] < self.ema[-1]:
				self.exit_price = None  # Reset the exit price

		# Execute the exit
		if self.exit_price and price < self.exit_price:
			if self.position:
				self.position.close()  # Exit the current position
			self.exit_price = None  # Reset the exit price after exiting


if __name__ == '__main__':
	from helpers.functions import get_ohlc_data
	import warnings

	warnings.filterwarnings('ignore')

	# Define the ticker symbol and the time period you're interested in
	# ticker_ = "^RUI"
	#ticker_ = "AAPL"  # Example: Apple Inc.
	# ticker_ = "GOOG"  # Example: Apple Inc.
	ticker_ = "^BVSP"  # Example: Apple Inc.

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
	bt = Backtest(ohlc_data, NineOne, cash=10_000_000, margin=1, commission=.00)

	# Execute the backtest
	results = bt.run()

	# Print the results
	print(results)

	# Optionally, plot the results
	bt.plot()
