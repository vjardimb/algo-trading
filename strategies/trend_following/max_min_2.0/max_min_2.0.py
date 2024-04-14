from backtesting import Backtest, Strategy
from backtesting.test import SMA, GOOG
import sys
import os

# Append the path of the root directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))))

from helpers.indicators import highest, lowest, atr


class MaxMin(Strategy):
	"""
	Entry Criteria:
	- Buy Signal: A new high is made when today's highest price is greater than the highest price of the previous 20 days. - Tendência
	- Buy Signal: A new low is made when today's lowest price is lower than the lowest price of the previous 2 days. - Consolidado

	Exit Criteria:
	- The position is exited if a new low is set, meaning today's lowest price is less than the lowest price of the previous 10 days.

	Indicators Used:
	- Highest: Tracks the highest high of the last 20 days to determine buy entry points.
	- Lowest: Monitors the lowest low of the last 10 days to set exit points for the trade.
	- ATR (Average True Range): Utilized to calculate the stop-loss level at 2x ATR below the entry price,
	providing a buffer based on market volatility.

	Strategy Parameters:
	- Highest Length: 20 days. Determines how long the highest price should be considered for setting a new entry.
	- Lowest Length: 10 days. Determines how long the lowest price is considered for triggering an exit.
	- ATR Length: 20 days. Used to compute the Average True Range, influencing the stop-loss distance.

	Additional Strategy Details:
	- This strategy enters a trade upon breaking a 20-day high and exits either on a 10-day low, aiming to capitalize on sustained trends.
	- The stop-loss is dynamically adjusted based on market volatility, providing a flexible risk management approach that adapts to changing market conditions.
	"""

	min_highest_length = 2
	min_lowest_length = 2
	med_highest_length = 20
	med_lowest_length = 10
	max_highest_length = 30
	max_lowest_length = 30
	atr_length = 20

	def init(self):
		# Calculate the highest of the last X days and lowest of the last Y days
		self.highest_min = self.I(highest, self.data.High, self.min_highest_length)
		self.highest_med = self.I(highest, self.data.High, self.med_highest_length)
		self.highest_max = self.I(highest, self.data.High, self.max_highest_length)
		self.lowest_min = self.I(lowest, self.data.Low, self.min_lowest_length)
		self.lowest_med = self.I(lowest, self.data.Low, self.med_lowest_length)
		self.lowest_max = self.I(lowest, self.data.Low, self.max_lowest_length)
		self.atr = self.I(atr, self.data.High, self.data.Low, self.data.Close, self.atr_length)

	def next(self):
		if self.highest_max == self.highest_med or self.lowest_max == self.lowest_med: # tendencia
			if not self.position:
				if (self.data.High[-1] > self.highest_med[-2]) or (self.data.High[-1] == self.highest_med[-1]):
					# Calculate stop loss and take profit levels
					stop_loss = max(self.data.Close[-1] - 2 * self.atr, self.lowest_med)

					# Place the buy order
					self.buy(sl=stop_loss)
			else:
				# Check if we need to update the take profit level (if new lows are found)
				if (self.lowest_med[-2] > self.data.Low[-1]) or (self.lowest_med[-1] == self.data.Low[-1]):
					self.position.close()

		else:
			if not self.position:
				if (self.data.Low[-1] < self.lowest_min[-2]) or (self.data.Low[-1] == self.lowest_min[-1]):
					
					take_profit = self.highest_min[-1]

					if take_profit == self.data.Close[-1]:
						take_profit += 1

					self.buy(tp=take_profit)
			else:
				self.trades[-1].tp = self.highest_min[-1]

if __name__ == '__main__':
	from helpers.functions import get_ohlc_data
	import warnings

	warnings.filterwarnings('ignore')

	# Define the ticker symbol and the time period you're interested in
	# ticker_ = "SPY"
	# ticker_ = "AAPL"  # Example: Apple Inc.
	# ticker_ = "GOOG"  # Example: Apple Inc.
	ticker_ = "^BVSP"  # Example: Apple Inc.

	end_date_ = '2024-02-15'  # Start date for the data
	start_date_ = '2011-01-05'  # Start date for the data

	interval_ = '1d'  # ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

	ohlc_data = get_ohlc_data(
		ticker_,
		start_date_,
		end_date_,
		interval_
	)

	# Setup and run the backtest
	bt = Backtest(ohlc_data, MaxMin, cash=1_000_000, margin=1, commission=.00, trade_on_close=True)

	# results = bt.optimize(max_highest_length = list(range(20,300)),
	# 		 max_lowest_length = list(range(20,300)),
	# 		 maximize='Return [%]',
	# 		 constraint= lambda x: x.max_highest_length == x.max_lowest_length)

	# Execute the backtest
	results = bt.run()

	# Print the results
	print(results)

	# Optionally, plot the results
	bt.plot()
