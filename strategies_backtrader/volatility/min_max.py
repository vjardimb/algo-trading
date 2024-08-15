import backtrader as bt
import os
import sys


class MaxMinStrategy(bt.Strategy):
	params = (
		('period', 4),
		('max_loss', 0.05),
		('printlog', False),
	)

	def __init__(self):
		# Define indicators
		self.highest = bt.indicators.Highest(self.data.high, period=self.params.period)
		self.highest_minus_1 = bt.indicators.Highest(self.data.high, period=self.params.period - 1)
		self.lowest = bt.indicators.Lowest(self.data.low, period=self.params.period)
		self.lowest_minus_1 = bt.indicators.Lowest(self.data.low, period=self.params.period - 1)

		self.highest.plotinfo.subplot = False
		self.highest_minus_1.plotinfo.plot = False
		self.lowest.plotinfo.subplot = False
		self.lowest_minus_1.plotinfo.plot = False

		self.order = None  # To track the current order
		self.stop_loss_order = None

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
		if self.stop_loss_order:
			# Cancel existing stop-loss order if it has not been executed
			self.cancel(self.stop_loss_order)

		if not self.position:  # Check if not in the market
			# Enter long with a new stop order at the highest of the last 20 days
			# Since the order is always placed on the next bar, a different reasoning needs to be leveraged.
			# If the next period has at least one price >= the highest of the last self.params.highest_period - 1 bars,
			# one can already infer that this price will be the next bar's self.params.highest_period-periods highest.
			# That's why the best thing to do is place the stop order price at the current [self.params.highest_period - 1]-periods highest.
			self.order = self.buy(size=order_size, exectype=bt.Order.Limit, price=self.lowest_minus_1[0])
		else:
			# Close the position with a stop order at the lowest of the last 10 days.
			# Same self.params.highest_period - 1 periods is applied to the lowest
			entry_price = self.position.price
			stop_price = entry_price * (1 - self.params.max_loss)
			self.stop_loss_order = self.sell(size=self.position.size, exectype=bt.Order.Stop, price=stop_price)

			self.order = self.close(exectype=bt.Order.Limit, price=self.highest_minus_1[0])

	def stop(self):
		self.log(f'(Period {self.params.period}) Ending Value {self.broker.getvalue()}', doprint=True)


if __name__ == '__main__':
	from datetime import datetime

	DATA_CSV = "ABEV3.csv"
	PRINT_RESULTS = True
	PLOT = True
	PARAM_PERIOD = 4

	# Create a cerebro entity
	cerebro = bt.Cerebro(stdstats=False)

	# Add analyzers
	cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
	cerebro.addanalyzer(bt.analyzers.Transactions, _name="transactions")
	cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
	cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0)
	cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
	cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
	cerebro.addanalyzer(bt.analyzers.TimeDrawDown, _name='timedrawdown')

	# Datas are in a subfolder of the samples. Need to find where the script is
	# because it could have been called from anywhere
	modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
	datapath = os.path.join(modpath, '../../data/' + DATA_CSV)

	# Create a Data Feed
	data = bt.feeds.YahooFinanceCSVData(
		dataname=datapath,
		# Do not pass values before this date
		fromdate=datetime(2023, 1, 1),
		# Do not pass values before this date
		todate=datetime(2023, 12, 31),
		# Do not pass values after this date
		reverse=False)

	cerebro.adddata(data)

	# Set our desired cash start
	cerebro.broker.set_cash(10000)

	# Set the commission - 0.1% ... divide by 100 to remove the %
	cerebro.broker.setcommission(commission=0.001)

	cerebro.addobserver(bt.observers.Broker)
	cerebro.addobserver(bt.observers.Trades)
	cerebro.addobserver(bt.observers.BuySell)

	# Add the strategy
	cerebro.addstrategy(MaxMinStrategy, period=PARAM_PERIOD)

	# Add a strategy
	# strats = cerebro.optstrategy(
	# 	MaxMinStrategy,
	# 	period=range(3, 21, 1),
	# )

	# Run over everything
	results = cerebro.run()

	# Analyze results
	first_strategy = results[0]
	trade_metrics = first_strategy.analyzers.trades.get_analysis()

	if PRINT_RESULTS:
		print('Strategy Results:')
		print('\nFinal Portfolio Value: %.2f' % cerebro.broker.getvalue())
		print('SQN: %.2f' % first_strategy.analyzers.sqn.get_analysis()['sqn'])
		print('Sharpe Ratio:', first_strategy.analyzers.sharpe.get_analysis()['sharperatio'])
		print('Annual Return:', first_strategy.analyzers.returns.get_analysis()['rnorm100'])
		print('Drawdown:', first_strategy.analyzers.drawdown.get_analysis()['max']['drawdown'])
		print('Max Drawdown Duration:', first_strategy.analyzers.drawdown.get_analysis()['max']['len'])
		# print('Time Drawdown:', first_strategy.analyzers.timedrawdown.get_analysis())
		print('\nTrade Analysis:')
		print('longest profit streak:', trade_metrics['streak']['won']['longest'])
		print('longest loss streak:', trade_metrics['streak']['lost']['longest'])
		print('avg pnl:', trade_metrics['pnl']['net']['average'])
		print('\nn of closed trades:', trade_metrics['total']['closed'])
		print('n of profit trades:', trade_metrics['won']['total'])
		print('n of loss trades:', trade_metrics['lost']['total'])
		print('% of profit trades:', trade_metrics['won']['total'] / trade_metrics['total']['closed'] if trade_metrics['total']['closed'] != 0 else 0)
		print('\nn of longs:', trade_metrics['long']['total'])
		print('n of profit longs:', trade_metrics['long']['won'])
		print('n of loss longs:', trade_metrics['long']['lost'])
		print('% of profit longs:', trade_metrics['long']['won'] / trade_metrics['long']['total'] if trade_metrics['long']['total'] != 0 else 0)
		print('\nn of shorts:', trade_metrics['short']['total'])
		print('n of profit shorts:', trade_metrics['short']['won'])
		print('n of loss shorts:', trade_metrics['short']['lost'])
		print('% of profit shorts:', trade_metrics['short']['won'] / trade_metrics['short']['total'] if trade_metrics['short']['total'] != 0 else 0)
		print('\ntotal period positioned:', trade_metrics['len']['total'])
		print('average trade duration:', trade_metrics['len']['average'])
		print('max trade duration:', trade_metrics['len']['max'])
		print('min trade duration:', trade_metrics['len']['min'])

	# Plot the result
	if PLOT:
		cerebro.plot(style='candlestick')
