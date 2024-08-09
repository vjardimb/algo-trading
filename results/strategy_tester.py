import yfinance as yf
import datetime
import pandas as pd
from backtesting import Backtest

from strategies.baseline.buy_and_hold.buy_and_hold import BuyAndHold
from strategies.trend_following.max_min.max_min import MaxMin as MaxMin
from strategies.trend_following.max_min.filtered_max_min import MaxMin as MaxMinFilt
from helpers.functions import get_ohlc_data


class StrategyTester:
	def __init__(self):
		self.strategies = []
		self._strategy_params = []
		self._optimize_strategies = []

		self.train_data = None

	def add_strategies(self, strategies):
		if not type(strategies) is list:
			raise Exception(f"Please, provide a list object, and not a {type(strategies)} object")

		# get number of previously added strategy
		prior_n_strategies = len(self.strategies)

		# initialize optimization flags as False for each provided Strtegy
		self._optimize_strategies += [False]*len(strategies)

		# check if the strategies object is a simple list of backtesting.py Strategies or a list of tuples
		# containing both the Strategy objects and the parameters to be optimized
		for i, strategy in enumerate(strategies):
			if type(strategy) is tuple:
				if not ((len(strategies) == 2) and (type(strategy[1]) is dict)):
					raise Exception(f"Please, provide a valid list object")

				# save strategy object
				self.strategies.append(strategy[0])

				# save strategy parameters
				self._strategy_params.append(strategy[1])

				# check whether the provided strategy will require optimization or not, and save it
				for param, values in strategy[1].items():
					if type(values) is list:
						if len(values) > 1:
							self._optimize_strategies[prior_n_strategies + i] = True
							break
			else:
				# save strategy object
				self.strategies.append(strategy)

				# save strategy parameters
				self._strategy_params.append({})

	def optimize(self, optimization_info):
		if not optimization_info:
			raise Exception(f"No optimization instructions were provided")
		elif [*optimization_info.keys()] != ['data_info', 'maximize'] or \
				[*optimization_info['data_info']] != ['ticker', 'start_date', 'end_date', 'interval']:
			raise Exception(f"Missing information for ohlc data retrieval."
							f"\nRequired info is (Stock Sticker, Start Data, End Date, timeframe)")

		if not(any(self._optimize_strategies)):
			print("No optimizations requested")

		data_info = optimization_info['data_info']

		opt_data = get_ohlc_data(
			data_info['ticker'],
			data_info['start_date'],
			data_info['end_date'],
			data_info['interval']
		)

		for i, strategy in enumerate(self.strategies):
			if self._optimize_strategies[i]:
				bt = Backtest(opt_data, strategy, cash=10_000)
				stats = bt.optimize(**(self._strategy_params[i] | {'maximize': optimization_info['maximize']}))

				for param in self._strategy_params[i]:
					self._strategy_params[i][param] = getattr(stats._strategy, param)

	def run_backtests(self, data_info, metrics):
		bt_data = get_ohlc_data(
			data_info['ticker'],
			data_info['start_date'],
			data_info['end_date'],
			data_info['interval']
		)

		results = pd.DataFrame(columns=metrics, index=[strat.__name__ for strat in self.strategies])

		for strategy in self.strategies:
			bt = Backtest(bt_data, strategy, cash=10_000)
			stats = bt.run()

			results.loc[strategy.__name__] = {metric: stats[metric] for metric in metrics}

		return results


if __name__ == "__main__":
	# Define the ticker symbol and the time period you're interested in
	ticker_ = 'AAPL'  # Example: Apple Inc.
	ticker_ = 'ABEV3.SA'  # Example: Apple Inc.

	# train_data_range_ = datetime.timedelta(days=500)
	test_data_range_ = datetime.timedelta(days=3000)

	test_end_date_ = '2022-02-15'  # Start date for the data
	test_start_date_ = '2011-01-05'  # Start date for the data

	# train_end_date_ = test_start_date_ - datetime.timedelta(days=1)   # End date for the data
	# train_start_date_ = train_end_date_ - train_data_range_  # Start date for the data

	interval_ = '1d'  # ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

	# opt_data_info = {
	# 		'ticker': ticker_,
	# 		'start_date': train_start_date_,
	# 		'end_date': train_end_date_,
	# 		'interval': interval_,
	# }

	test_data_info = {
		'ticker': ticker_,
		'start_date': test_start_date_,
		'end_date': test_end_date_,
		'interval': interval_,
	}

	opt_info = {
	# 	'data_info': opt_data_info,
	# 	'maximize': 'Sharpe Ratio'
	}

	backtester = StrategyTester()

	# strategies_ = [
	# 	(
	# 		RsiOscillator, {
	# 			'rsi_len': [14, 20, 25],
	# 			'upper_bound': 70,
	# 			'lower_bound': 30,
	# 		}
	# 	),
	# 	(
	# 		SmaCross, {
	# 			'n1': [10],
	# 			'n2': 40,
	# 		}
	# 	)
	# ]

	# or
	strategies_ = [
		# BuyAndHold,
		MaxMin,
		MaxMinFilt
	]

	comparison_metrics = [
		'Exposure Time [%]',
		'Equity Final [$]',
		'Equity Peak [$]',
		'Return [%]',
		'Buy & Hold Return [%]',
		'Return (Ann.) [%]',
		'Volatility (Ann.) [%]',
		'Sharpe Ratio',
		'# Trades',
		'Win Rate [%]',
		'Best Trade [%]',
		'Worst Trade [%]',
		'Avg. Trade [%]',
		'Max. Trade Duration',
		'Avg. Trade Duration',
		'Profit Factor'
	]

	backtester.add_strategies(strategies_)

	# backtester.optimize(optimization_info=opt_info)

	results = backtester.run_backtests(test_data_info, comparison_metrics)

	print(results.T)
