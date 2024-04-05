from backtesting import Strategy
from backtesting import Backtest
from backtesting.lib import crossover
from backtesting.test import GOOG
import datetime

from helpers.indicators import sma, rsi, bbands


class BBandRsi(Strategy):
	# indicator parameters
	rsi_length = 2           # candles
	sma_length = 200         # candles
	bbands_length = 20       # candles
	bbands_std = 2.5         # standard deviations

	# strategy parameters
	order_time_max = 5       # maximum duration of an active order [days]
	trade_time_max = 10      # maximum duration of a trade [days]
	rsi_upper_limit = 50     # RSI upper limit for keeping a long [%]
	rsi_lower_limit = 50     # RSI lower limit for keeping a short (preferably 100 - rsi_upper_limit) [%]
	order_size = 0.99        # Fraction of cash to use on new order [%]
	stoploss_factor = 50     # Fraction of the order limit to set the stop loss [%]
	buy_limit_offset = 0     # Distance btw the candle close and the buy order limit [% of close]
	sell_limit_offset = 0    # Distance btw the candle close and the sell order limit [% of close]

	# list of datetime of the current order initialization
	orders_datetime = []

	def init(self):
		self.sma = self.I(sma, self.data.Close, self.sma_length)
		self.rsi = self.I(rsi, self.data.Close, self.rsi_length)
		self.bbands = self.I(bbands, self.data.Close, self.bbands_length, self.bbands_std)

	def next(self):
		lower_band = self.bbands[0]
		upper_band = self.bbands[2]

		# buying conditions
		buy_sma_cross = crossover(self.data.High, self.sma)
		buy_bband_cross = crossover(lower_band, self.data.Close)

		buy_signal = buy_sma_cross and buy_bband_cross

		# selling conditions
		sell_sma_cross = crossover(self.data.High, self.sma)
		sell_bband_cross = crossover(self.data.Close, upper_band)

		sell_signal = sell_sma_cross and sell_bband_cross

		# if an order surpasses max days active, cancel it.
		for _ in range(0, len(self.orders)):
			if self.data.index[-1] - self.orders_datetime[0] > datetime.timedelta(days=self.order_time_max):
				self.orders[0].cancel()
				self.orders_datetime.pop(0)

		if len(self.trades) > 0:
			# if a trade remains open for more than the defined maximum, close it.
			if self.data.index[-1] - self.trades[-1].entry_time >= datetime.timedelta(days=self.trade_time_max):
				self.trades[-1].close()

			# if a long has an rsi level above the defined limit, close it
			if self.trades[-1].is_long and self.rsi >= self.rsi_upper_limit:
				self.trades[-1].close()

			# if a shot has an rsi level below the defined limit, close it
			elif self.trades[-1].is_short and self.rsi <= self.rsi_lower_limit:
				self.trades[-1].close()

		# only set new buy or sell orders if there aren't any open trades
		if not len(self.trades):

			# if the high price is above the sma and the close price is below the lower bband, buy
			if buy_signal:
				buy_limit = self.data.Close * (1 - self.buy_limit_offset / 100)
				stop_loss = buy_limit * (1 - self.stoploss_factor / 100)

				# Cancel all previous orders
				for _ in range(0, len(self.orders)):
					self.orders[0].cancel()
					self.orders_datetime.pop(0)

				# set buy order and stop loss
				self.buy(
					limit=buy_limit,
					sl=stop_loss,
					size=self.order_size
				)
				self.orders_datetime.append(self.data.index[-1])

			elif sell_signal:
				sell_limit = self.data.Close * (1 - self.buy_limit_offset / 100)
				stop_loss = sell_limit * (1 + self.stoploss_factor / 100)

				# Cancel previous orders
				for _ in range(0, len(self.orders)):
					self.orders[0].cancel()
					self.orders_datetime.pop(0)

				# Add new replacement order
				self.sell(
					limit=sell_limit,
					sl=stop_loss,
					size=self.order_size
				)
				self.orders_datetime.append(self.data.index[-1])


if __name__ == '__main__':
	# Setup and run the backtest
	bt = Backtest(GOOG, BBandRsi, cash=10_000, commission=.002)

	# Execute the backtest
	results = bt.run()

	# Print the results
	print(results)

	# Optionally, plot the results
	# bt.plot()
