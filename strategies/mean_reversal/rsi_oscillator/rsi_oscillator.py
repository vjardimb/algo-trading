from backtesting import Strategy
from backtesting.lib import crossover
from helpers.indicators import rsi
from helpers.functions import get_ohlc_data


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
	import datetime

	# Define the ticker symbol and the time period you're interested in
	ticker_ = 'AAPL'  # Example: Apple Inc.

	train_data_range_ = datetime.timedelta(days=200)
	test_data_range_ = datetime.timedelta(days=200)

	train_end_date_ = datetime.datetime.today()  # End date for the data
	test_end_date_ = datetime.datetime.today()  # End date for the data

	train_start_date_ = train_end_date_ - train_data_range_  # Start date for the data
	test_start_date_ = test_end_date_ - test_data_range_  # Start date for the data

	interval_ = '1d'  # ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

	opt_data_info = {
		'ticker': ticker_,
		'start_date': train_start_date_,
		'end_date': train_end_date_,
		'interval': interval_,
	}

	opt_data = get_ohlc_data(
		opt_data_info['ticker'],
		opt_data_info['start_date'],
		opt_data_info['end_date'],
		opt_data_info['interval']
	)

	bt = Backtest(opt_data, RsiOscillator, cash=10_000, commission=.002)

	# stats = bt.run()
	stats = bt.optimize(
		rsi_len=[14, 20, 25],
		upper_bound=70,
		lower_bound=30,
		maximize='Sharpe Ratio'
	)

	print(stats)

	# bt.plot(show_legend=False)
