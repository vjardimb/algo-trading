from backtesting import Strategy
from backtesting.lib import crossover
import pandas_ta as ta
import sys
import os

# Append the path of the root directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))))

from helpers.indicators import supertrend, dema

class Supertrend(Strategy):
	"""
	Entry Criteria:
	- Buy Signal: Price closes above the Dema indicator and Supertrend shows bullish trend.
	- Sell Signal: Supertrend shows bearish trend.

	Exit Criteria:
	- A trade is exited if it exceeds price is below Supertrend.

	Indicators Used:
	- DEMA (200-day).
	- Supertrend (12-day, 3-multiplier) for trend direction.
	"""
		
	# for later optimization
	supertrend_length = 12
	supertrend_mult = 3

	dema_length = 200

	def init(self):
		# Precompute the moving averages
		self.supertrend = self.I(supertrend, self.data.High, self.data.Low, self.data.Close, self.supertrend_length, self.supertrend_mult, overlay=True)
		self.dema = self.I(dema, self.data.High, self.data.Low, self.dema_length)

	def next(self):
		if (self.data.Close > self.dema and
			crossover(self.supertrend[1], 0)):
			self.buy(sl=self.supertrend[0])

		if (crossover(0, self.supertrend[1]) or
	  		crossover(self.supertrend[0], self.data.Low)):
			self.position.close()

		if len(self.trades) > 0:
			self.trades[-1].sl = self.supertrend[0]


if __name__ == "__main__":
	from backtesting.test import GOOG
	from backtesting import Backtest

	bt = Backtest(GOOG, Supertrend, cash=10_000, commission=.002)
	stats = bt.run()

	print(stats)
	bt.plot(show_legend=False)
