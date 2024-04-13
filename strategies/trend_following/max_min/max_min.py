from backtesting import Backtest, Strategy
from backtesting.test import SMA, GOOG

from helpers.indicators import highest, lowest, atr


class MaxMin(Strategy):
	"""
	Entry Criteria:
	- Buy Signal: A new high is made when today's highest price is greater than the highest price of the previous 20 days.

	Exit Criteria:
	- The position is exited if a new low is set, meaning today's lowest price is less than the lowest price of the previous 10 days.
	- 2*ATR is used as a stop-loss.

	Indicators Used:
	- Highest: Tracks the highest high of the last 20 days to determine buy entry points.
	- Lowest: Monitors the lowest low of the last 10 days to set exit points for the trade.
	- ATR (Average True Range): Utilized to calculate the stop-loss level at 2x ATR below the entry price,
	providing a buffer based on market volatility.

	Additional Strategy Details:
	- This strategy enters a trade upon breaking a 20-day high and exits either on a 10-day low, aiming to capitalize on sustained trends.
	"""

	highest_length = 20
	lowest_length = 10
	sma_length = 20
	atr_length = 20

	def init(self):
		# Calculate the highest of the last X days and lowest of the last Y days
		self.highest = self.I(highest, self.data.High, self.highest_length)
		self.lowest = self.I(lowest, self.data.Low, self.lowest_length)
		self.atr = self.I(atr, self.data.High, self.data.Low, self.data.Close, self.atr_length)

	def next(self):
		if not self.position:
			if self.data.High[-1] == self.highest[-1]:
				# Calculate stop loss and take profit levels
				stop_loss = max(self.data.Close[-1] - 2 * self.atr, self.lowest)

				# Place the buy order
				self.buy(sl=stop_loss)
		else:
			# Check if we need to update the take profit level (if new lows are found)
			if self.lowest[-1] == self.data.Low[-1]:
				self.position.close()


if __name__ == '__main__':
	from helpers.functions import get_ohlc_data
	import warnings

	warnings.filterwarnings('ignore')

	# Define the ticker symbol and the time period you're interested in
	# ticker_ = "^RUI"
	ticker_ = "AAPL"  # Example: Apple Inc.
	# ticker_ = "GOOG"  # Example: Apple Inc.
	# ticker_ = "^BVSP"  # Example: Apple Inc.

	end_date_ = '2022-02-15'  # Start date for the data
	start_date_ = '2011-01-05'  # Start date for the data

	interval_ = '1d'  # ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

	ohlc_data = get_ohlc_data(
		ticker_,
		start_date_,
		end_date_,
		interval_
	)

	# Setup and run the backtest
	bt = Backtest(ohlc_data, MaxMin, cash=10_000, margin=1, commission=.00)

	# Execute the backtest
	results = bt.run()

	# Print the results
	print(results)

	# Optionally, plot the results
	bt.plot()
