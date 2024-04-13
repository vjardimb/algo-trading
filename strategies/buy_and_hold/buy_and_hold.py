from backtesting import Strategy, Backtest

from helpers.functions import get_ohlc_data


class BuyAndHold(Strategy):
	def init(self):
		pass

	def next(self):
		if not self.position:
			self.buy()


if __name__ == '__main__':
	from helpers.functions import get_ohlc_data
	import warnings

	warnings.filterwarnings('ignore')

	# Define the ticker symbol and the time period you're interested in
	# ticker_ = "^RUI"
	# ticker_ = "AAPL"
	# ticker_ = "GOOG"
	ticker_ = "^BVSP"

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
	bt = Backtest(ohlc_data, BuyAndHold, cash=10_000_000, margin=1, commission=.00)

	# Execute the backtest
	results = bt.run()

	# Print the results
	print(results)

	# Optionally, plot the results
	bt.plot()
