from backtesting import Strategy, Backtest
import warnings

from helpers.functions import get_ohlc_data
from helpers.indicators import highest, lowest, atr


class MinMax(Strategy):
	"""
	Entry Criteria:
	- Buy Signal: Buy order placed on the lowest low of the last 2 candles
	Exit Criteria:
	- Price goes below the highest high of the last 2 days
	"""
	# Define the two MA lags as *class variables*
	# for later optimization
	lowest_length = 2
	highest_length = 2
	atr_length = 20

	def init(self):
		# Precompute the two moving averages
		self.highest = self.I(highest, self.data.High, self.highest_length)
		self.lowest = self.I(lowest, self.data.Low, self.lowest_length)
		self.atr = self.I(atr, self.data.High, self.data.Low, self.data.Close, self.atr_length)

	def next(self):
		if not self.position:
			if self.data.Low[-1] == self.lowest[-1]:
				stop_loss = self.data.Close[-1] - 2 * self.atr

				# Place the buy order
				self.buy(sl=stop_loss)
		else:
			# Check if we need to update the take profit level (if new lows are found)
			if self.data.High == self.highest[-1]:
				self.position.close()


if __name__ == "__main__":
	warnings.filterwarnings('ignore')

	# Define the ticker symbol and the time period you're interested in
	# ticker_ = "^RUI"
	ticker_ = "AAPL"  # Example: Apple Inc.
	# ticker_ = "GOOG"  # Example: Apple Inc.
	# ticker_ = "^BVSP"  # Example: Apple Inc.
	ticker_ = "ABEV3.SA"  # Example: Apple Inc.

	end_date_ = '2022-02-15'  # end date for the data
	start_date_ = '2011-01-05'  # Start date for the data

	interval_ = '1d'  # ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

	ohlc_data = get_ohlc_data(
		ticker_,
		start_date_,
		end_date_,
		interval_
	)

	bt = Backtest(ohlc_data, MinMax, cash=10_000, commission=.00, trade_on_close=True)
	stats = bt.run()

	print(stats)
	bt.plot(show_legend=False)
