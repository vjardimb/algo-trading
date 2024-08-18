import backtrader as bt
import os
import sys
from datetime import date, datetime

DEBUG_DATE = '2023-02-09'


class BBandRsi(bt.Strategy):
	params = (
		('rsi_length', 2),
		('sma_length', 200),
		('bbands_length', 20),
		('bbands_stddev', 2.5),
		('order_time_max', 5),
		('trade_time_max', 10),
		('rsi_upper_limit', 70),
		('rsi_lower_limit', 30),
		('order_size_fraction', 0.99),
		('stoploss_factor', 0.05),
		('buy_limit_offset', 0.0),
		('sell_limit_offset', 0),
		('do_logging', True),
	)

	def __init__(self):
		# Indicators
		self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_length)
		self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_length)
		self.bbands = bt.indicators.BollingerBands(self.data.close, period=self.params.bbands_length,
												   devfactor=self.params.bbands_stddev)
		self.active_order = None
		self.entry_date = None
		self.order_creation = None

	def log(self, txt, dt=None, skiplines=0, log=None):
		""" Logging function for this strategy """
		dt = dt or self.datas[0].datetime.date(0)

		# if not log:
		# 	log = self.params.do_logging

		if log or self.params.do_logging:
			print(skiplines*'\n' + f'{dt.isoformat()} {txt}')
		else:
			return

	def get_size(self, price):
		""" Calculate the number of shares to buy based on the current price and available cash. """

		cash = self.broker.get_cash()

		if cash < price:
			raise Exception('Cash not sufficient!')

		size = int(0.55 * cash / price)  # Calculate maximum number of shares that can be bought

		return size

	def next(self):
		if self.datas[0].datetime.date(0) == date.fromisoformat(DEBUG_DATE):
			debug_aux = None

		if self.active_order:
			if len(self) - self.order_creation >= self.params.order_time_max:
				self.cancel(self.active_order)
				self.active_order = None
		else:
			if not self.position:
				if all(self.data.low[-1 * i] > self.sma[-1 * i] for i in range(0, 6)):
					if self.data.close[0] < self.bbands.bot[0]:
						order_size = self.get_size(self.datas[0].close[0])
						price = self.data.low[0]*(1 - self.params.buy_limit_offset)

						self.active_order = self.buy(size=order_size, price=price, exectype=bt.Order.Limit)
						self.log(f'BUY SIGNAL AT {price}', skiplines=1)

						self.order_creation = len(self)
			else:
				# Exit conditions
				if len(self) - self.entry_date >= self.params.trade_time_max:
					self.close()
				elif self.rsi[0] > self.params.rsi_upper_limit:
					self.close()

	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			return

		if order.status in [order.Completed]:
			if order.isbuy():
				self.log(
					f'BUY EXECUTED, Price: {round(order.executed.price, 2)}, Cost: {round(order.executed.value, 2)}, Comm {round(order.executed.comm, 2)}')

				self.entry_date = len(self)
				self.order_creation = None
				self.active_order = None
			elif order.issell():
				self.log(
					f'SELL EXECUTED, Price: {round(order.executed.price, 2)}, Cost: {round(order.executed.value, 2)}, Comm {round(order.executed.comm, 2)}')
				self.entry_date = None

		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log('Order Canceled/Margin/Rejected')

			if order.isbuy():
				self.order_creation = None

	def notify_trade(self, trade):
		if not trade.isclosed:
			return

		self.log('OPERATION PROFIT, GROSS: %.2f, NET: %.2f' %
				 (trade.pnl, trade.pnlcomm))

	def stop(self):
		if self.position:
			self.close()

		self.log(f'(bbands_stddev {self.params.bbands_stddev}, rsi_upper_limit {self.params.rsi_upper_limit}) Ending Value {round(self.broker.getvalue(), 2)}', skiplines=1, log=True)


if __name__ == '__main__':
	DATA_CSV = "BTC.csv"
	PRINT_RESULTS = True
	PLOT = False
	DO_LOGGING = True

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
		fromdate=datetime(2014, 1, 1),
		# Do not pass values before this date
		todate=datetime(2023, 12, 31),
		# Do not pass values after this date
		reverse=False)

	cerebro.adddata(data)

	# Set our desired cash start
	cerebro.broker.set_cash(100_000)

	# Set the commission - 0.1% ... divide by 100 to remove the %
	cerebro.broker.setcommission(commission=0.001)

	cerebro.addobserver(bt.observers.Broker)
	cerebro.addobserver(bt.observers.Trades)
	cerebro.addobserver(bt.observers.BuySell)

	# Add the strategy
	cerebro.addstrategy(BBandRsi, do_logging=DO_LOGGING)

	# Add a strategy
	# strats = cerebro.optstrategy(
	# 	BBandRsi,
	# 	bbands_stddev=[1.5, 1.75, 2.0, 2.25, 2.50, 2.75],
	# 	rsi_upper_limit=range(50, 81, 10),
	# 	do_logging=False
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
		print('% of profit trades:',
			  round(100 * trade_metrics['won']['total'] / trade_metrics['total']['closed'], 2) if trade_metrics['total'][
																					  'closed'] != 0 else 0, "%")
		print('\nn of longs:', trade_metrics['long']['total'])
		print('n of profit longs:', trade_metrics['long']['won'])
		print('n of loss longs:', trade_metrics['long']['lost'])
		print('% of profit longs:',
			  round(100 * trade_metrics['long']['won'] / trade_metrics['long']['total'], 2) if trade_metrics['long'][
																				   'total'] != 0 else 0, "%")
		print('\nn of shorts:', trade_metrics['short']['total'])
		print('n of profit shorts:', trade_metrics['short']['won'])
		print('n of loss shorts:', trade_metrics['short']['lost'])
		print('% of profit shorts:',
			  round(100 * trade_metrics['short']['won'] / trade_metrics['short']['total'], 2) if trade_metrics['short'][
																					 'total'] != 0 else 0, "%")
		print('\ntotal period positioned:', trade_metrics['len']['total'])
		print('average trade duration:', trade_metrics['len']['average'])
		print('max trade duration:', trade_metrics['len']['max'])
		print('min trade duration:', trade_metrics['len']['min'])

	# Plot the result
	if PLOT:
		cerebro.plot(style='candlestick')
