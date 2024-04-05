from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG  # Using Google's stock data as an example
import numpy as np

from helpers.indicators import bbands


class RandomStrategy(Strategy):
	def init(self):
		pass

	def next(self):
		print(np.shape(self.bbands))
		action = np.random.choice(["buy", "sell", "hold"])

		if action == "buy" and not self.position:
			self.buy()
		elif action == "sell" and self.position:
			self.position.close()


if __name__ == '__main__':
	# Setup and run the backtest
	bt = Backtest(GOOG, RandomStrategy, cash=10_000, commission=.002)

	# Execute the backtest
	results = bt.run()

	# Print the results
	print(results)

	# Optionally, plot the results
	# bt.plot()