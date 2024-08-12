import backtrader as bt
import os
import sys
from pathlib import Path


class MaxMinStrategy(bt.Strategy):
	params = (
		('highest_length', 20),
		('lowest_length', 10),
		('printlog', False),
	)

	def __init__(self):
		# Define indicators
		self.highest = bt.indicators.Highest(self.data.high, period=self.params.highest_length)
		self.lowest = bt.indicators.Lowest(self.data.low, period=self.params.lowest_length)

		self.highest.plotinfo.subplot = False
		self.lowest.plotinfo.subplot = False

		self.order = None  # To track the current order

	def get_size(self, price):
		""" Calculate the number of shares to buy based on the current price and available cash. """
		cash = self.broker.get_cash()
		size = int(0.95 * cash / price)  # Calculate maximum number of shares that can be bought
		return size

	def log(self, txt, dt=None, doprint=False):
		""" Logging function fot this strategy """
		if self.params.printlog or doprint:
			dt = dt or self.datas[0].datetime.date(0)
			print('%s, %s' % (dt.isoformat(), txt))

	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			# Buy/Sell order submitted/accepted to/by broker - Nothing to do
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enough cash
		if order.status in [order.Completed]:
			if order.isbuy():
				self.log(
					'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
					(order.executed.price,
					 order.executed.value,
					 order.executed.comm))

				self.buyprice = order.executed.price
				self.buycomm = order.executed.comm
			else:  # Sell
				self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
						 (order.executed.price,
						  order.executed.value,
						  order.executed.comm))

		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log('Order Canceled/Margin/Rejected')

	def notify_trade(self, trade):
		if not trade.isclosed:
			return

		self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
				 (trade.pnl, trade.pnlcomm))

	def next(self):
		order_size = self.get_size(self.datas[0].close[0])

		if self.order:
			# Cancel the existing order if it has not been executed
			self.cancel(self.order)

		if not self.position:  # Check if not in the market
			# Enter long with a new stop order at the highest of the last 20 days
			self.order = self.buy(size=order_size, exectype=bt.Order.Stop, price=self.highest[0])
		else:
			# Close the position with a stop order at the lowest of the last 10 days
			self.order = self.close(exectype=bt.Order.Stop, price=self.lowest[0])

	def stop(self):
		self.log(f'(highest len {self.params.highest_length}, lowest length {self.params.lowest_length}) Ending Value {self.broker.getvalue()}', doprint=True)


if __name__ == '__main__':
	from datetime import datetime

	DATA_CSV = "AAPL.csv"

	# Create a cerebro entity
	cerebro = bt.Cerebro(stdstats=False)

	# Datas are in a subfolder of the samples. Need to find where the script is
	# because it could have been called from anywhere
	modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
	datapath = os.path.join(modpath, '../data/' + DATA_CSV)

	# Create a Data Feed
	data = bt.feeds.YahooFinanceCSVData(
		dataname=datapath,
		# Do not pass values before this date
		fromdate=datetime(2014, 1, 1),
		# Do not pass values before this date
		todate=datetime(2023, 12, 31),
		# Do not pass values after this date
		reverse=False)

	cerebro.adddata(data)

	# Set our desired cash start
	cerebro.broker.set_cash(10000)

	# Set the commission
	cerebro.broker.setcommission(commission=0.0)

	cerebro.addobserver(bt.observers.Broker)
	cerebro.addobserver(bt.observers.Trades)
	cerebro.addobserver(bt.observers.BuySell)

	# Add the strategy
	cerebro.addstrategy(MaxMinStrategy)

	# Add a strategy
	# strats = cerebro.optstrategy(
	#	MaxMinStrategy,
	#	lowest_length=range(10, 90, 10),
	#	highest_length=range(10, 90, 10)
	#)

	# Set the commission - 0.1% ... divide by 100 to remove the %
	# cerebro.broker.setcommission(commission=0.001)

	# Run over everything
	results = cerebro.run()

	# Plot the result
	cerebro.plot(style='candlestick')
