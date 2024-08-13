import backtrader as bt
import os
import sys
from datetime import date

DEBUG_DATE = '2014-02-06'


class NineOne(bt.Strategy):
    params = (
        ('ema_length', 9),
        ('max_order_duration', 1)
    )

    def __init__(self):
        self.ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.ema_length)
        self.order = None  # To track the current order
        self.stop_loss_order = None

    def log(self, txt, dt=None):
        """ Logging function for this strategy """
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def get_size(self, price):
        """ Calculate the number of shares to buy based on the current price and available cash. """
        cash = self.broker.get_cash()
        size = int(0.95 * cash / price)  # Calculate maximum number of shares that can be bought
        return size

    def next(self):
        if self.datas[0].datetime.date(0) == date.fromisoformat(DEBUG_DATE):
            debug_aux = None

        close = self.data.close[0]
        open = self.data.open[0]
        high = self.data.high[0]
        low = self.data.low[0]

        order_size = self.get_size(self.datas[0].close[0])

        # Cancel the existing order if conditions are not favorable anymore
        if self.order and self.order.alive() and not self.order.status == self.order.Completed:
            if (self.order.isbuy() and self.ema[0] < self.ema[-1]) or \
                    (self.order.issell() and self.ema[0] > self.ema[-1]):
                self.cancel(self.order)
                self.log('Order canceled due to EMA direction change')
                self.order = None
                return  # Prevent further execution until the next tick

            elif len(self) - self.order_age >= self.params.max_order_duration:
                self.cancel(self.order)
                self.log('Order canceled due to time expiration')
                self.order = None
                return  # Prevent further execution until the next tick

        if self.position and not self.stop_loss_order:
            self.stop_loss_order = self.close(price=low, exectype=bt.Order.Stop)

        # Condition to enter a trade
        if not self.position:
            if (self.ema[0] > self.ema[-1] and self.ema[-1] < self.ema[-2] and self.ema[-2] < self.ema[-3]) and (self.ema[0] < close):
                if not self.order:
                    self.log(f'Buy signal at {high}')
                    self.order = self.buy(size=order_size, price=high, exectype=bt.Order.Stop)
                    self.order_age = len(self)
        else:
            # Condition to exit the trade
            if (close < self.ema[0]) and self.ema[0] < self.ema[-1]:
                if not self.order:
                    self.log(f'Sell signal at {low}')
                    self.order = self.close(price=low, exectype=bt.Order.Stop)
                    self.order_age = len(self)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}, Comm {order.executed.comm}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}, Comm {order.executed.comm}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None  # No pending orders


if __name__ == '__main__':
    from datetime import datetime

    DATA_CSV = "AAPL.csv"

    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)

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
    cerebro.broker.set_cash(10000)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.001)

    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.BuySell)

    # Add the strategy
    cerebro.addstrategy(NineOne)

    # Add a strategy
    # strats = cerebro.optstrategy(
    # 	MaxMinStrategy,
    # 	period=range(3, 21, 1),
    # )

    # Run over everything
    results = cerebro.run()

    # Plot the result
    cerebro.plot(style='candlestick')