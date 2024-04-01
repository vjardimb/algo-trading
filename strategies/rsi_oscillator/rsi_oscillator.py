from backtesting import Strategy
from backtesting.lib import crossover
from helpers.indicators import rsi


class RsiOscillator(Strategy):
	rsi_len = 14
	upper_bound = 70
	lower_bound = 30

	def init(self):
		self.rsi = self.I(rsi, self.data.Close, self.rsi_len)

	def next(self):
		if crossover(self.rsi, self.upper_bound):
			self.position.close()
		elif crossover(self.lower_bound, self.rsi):
			self.buy()


if __name__ == "__main__":
	from backtesting.test import GOOG
	from backtesting import Backtest

	bt = Backtest(GOOG, RsiOscillator, cash=10_000, commission=.002)
	stats = bt.run()

	print(stats)
	bt.plot(show_legend=False)
