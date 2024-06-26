from backtesting import Strategy
from backtesting.lib import crossover
from helpers.indicators import sma


class SmaCross(Strategy):
	"""
	Entry Criteria:
	- Buy Signal: The short SMA goes above the long SMA
	- Sell Signal: The short SMA goes below the long SMA
	Exit Criteria:
	- Entry criteria is no longer active, i.e. SMAs crossed.

	Indicators Used:
	- SMA (Simple Moving Average): Used twice, one short and one long, to determine the price trend.
	"""
	# Define the two MA lags as *class variables*
	# for later optimization
	n1 = 10
	n2 = 20

	def init(self):
		# Precompute the two moving averages
		self.sma1 = self.I(sma, self.data.Close, self.n1)
		self.sma2 = self.I(sma, self.data.Close, self.n2)

	def next(self):
		# If sma1 crosses above sma2, close any existing
		# short trades, and buy the asset
		if crossover(self.sma1, self.sma2):
			self.position.close()
			self.buy()

		# Else, if sma1 crosses below sma2, close any existing
		# long trades, and sell the asset
		elif crossover(self.sma2, self.sma1):
			self.position.close()
			self.sell()


if __name__ == "__main__":
	from backtesting.test import GOOG
	from backtesting import Backtest

	bt = Backtest(GOOG, SmaCross, cash=10_000, commission=.002)
	stats = bt.run()

	print(stats)
	bt.plot(show_legend=False)
