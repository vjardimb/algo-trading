import backtrader as bt


class MaxMinStrategy(bt.Strategy):
	params = (
		('highest_length', 20),
		('lowest_length', 10),
	)

	def __init__(self):
		# Define indicators
		self.highest = bt.indicators.Highest(self.data.high, period=self.params.highest_length)
		self.lowest = bt.indicators.Lowest(self.data.low, period=self.params.lowest_length)

		self.highest.plotinfo.subplot = False
		self.lowest.plotinfo.subplot = False

		self.order = None  # To track the current order

	def next(self):
		order_size = self.get_size(self.datas[0].close[0])

		if self.order:
			# Cancel the existing order if it has not been executed
			self.cancel(self.order)

		if not self.position:  # Check if not in the market
			# Enter long with a new stop order at the highest of the last 20 days
			self.order = self.buy(size=order_size, exectype=bt.Order.Stop, price=self.highest[0])

			print(f"order sise : {order_size}, price: {self.datas[0].close[0]}")
		else:
			# Close the position with a stop order at the lowest of the last 10 days
			self.order = self.close(size=order_size, exectype=bt.Order.Stop, price=self.lowest[0])

	def get_size(self, price):
		""" Calculate the number of shares to buy based on the current price and available cash. """
		cash = self.broker.get_cash()
		size = int(cash / price)  # Calculate maximum number of shares that can be bought
		return size*0.95


if __name__ == '__main__':
	from datetime import datetime

	# Create a cerebro entity
	cerebro = bt.Cerebro(stdstats=False)

	########################## get data #################################
	from helpers.functions import get_ohlc_data
	import warnings

	warnings.filterwarnings('ignore')

	# Define the ticker symbol and the time period you're interested in
	ticker_ = "AAPL"  # Example: Apple Inc.

	end_date_ = '2022-02-15'  # Start date for the data
	start_date_ = '2011-01-05'  # Start date for the data

	interval_ = '1d'  # ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

	ohlc_data = get_ohlc_data(
		ticker_,
		start_date_,
		end_date_,
		interval_
	)
	#######################################################################

	# Add the data feed
	data = bt.feeds.PandasData(dataname=ohlc_data)
	cerebro.adddata(data)

	# Set our desired cash start
	cerebro.broker.set_cash(10000)

	cerebro.addobserver(bt.observers.Broker)
	cerebro.addobserver(bt.observers.Trades)
	cerebro.addobserver(bt.observers.BuySell)

	# Add the strategy
	cerebro.addstrategy(MaxMinStrategy)

	# Set the commission - 0.1% ... divide by 100 to remove the %
	# cerebro.broker.setcommission(commission=0.001)

	# Run over everything
	results = cerebro.run()

	# Plot the result
	cerebro.plot(style='candlestick')
