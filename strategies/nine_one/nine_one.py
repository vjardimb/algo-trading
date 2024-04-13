from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG  # Usando dados de exemplo do Google

from helpers.indicators import ema


class NineOne(Strategy):
	def init(self):
		# Inicializa a média móvel de 9 períodos
		self.sma9 = self.I(ema, self.data.Close, 9)
		self.entry_price = None
		self.exit_price = None
		self.low_since_entry = None

	def next(self):
		price = self.data.Close[-1]
		high = self.data.High[-1]
		low = self.data.Low[-1]

		# Condição para entrar na operação
		if not self.position:
			# Se a média móvel passou a subir, ativa sinal de compra
			if (self.sma9[-1] > self.sma9[-2]) and (self.sma9[-2] < self.sma9[-3]):
				self.entry_price = high + 0.01  # Preço de compra um tick acima da máxima atual
				self.low_since_entry = low  # Atualiza a menor baixa desde a entrada
			# Se a media caiu, desativa
			elif self.sma9[-2] > self.sma9[-1]:
				self.entry_price = None  # Reset na condição de entrada
		else:
			# Atualiza a menor baixa desde a entrada enquanto está em posição
			if low < self.low_since_entry:
				self.low_since_entry = low

		# Executar a entrada
		# print(self.entry_price, price)
		if self.entry_price and price > self.entry_price:
			if not self.position:
				self.buy(sl=self.low_since_entry)  # Compra com stop loss na menor baixa desde a entrada
			self.entry_price = None  # Reset no preço de entrada após comprar

		# Condição para sair da operação
		if self.position:
			# Se a média móvel passou a descer, ativa sinal de saida
			if (self.sma9[-1] < self.sma9[-2]) and (self.sma9[-2] > self.sma9[-3]):
				self.exit_price = low + 0.01  # Preço de compra um tick acima da máxima atual
			# Se a media voltou a subir, desativa
			elif self.sma9[-2] < self.sma9[-1]:
				self.exit_price = None  # Reset na condição de entrada


		# Executar a saida
		# print(self.entry_price, price)
		if self.exit_price and price < self.exit_price:
			if self.position:
				self.position.close()  # Compra com stop loss na menor baixa desde a entrada
			self.exit_price = None  # Reset no preço de entrada após comprar


if __name__ == '__main__':
	from helpers.functions import get_ohlc_data
	import warnings

	warnings.filterwarnings('ignore')

	# Define the ticker symbol and the time period you're interested in
	# ticker_ = "^RUI"
	ticker_ = "AAPL"  # Example: Apple Inc.
	# ticker_ = "GOOG"  # Example: Apple Inc.
	ticker_ = "^BVSP"  # Example: Apple Inc.

	end_date_ = '2021-01-05'  # End date for the data
	start_date_ = '2011-01-05'  # Start date for the data

	interval_ = '1d'  # ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

	ohlc_data = get_ohlc_data(
		ticker_,
		start_date_,
		end_date_,
		interval_
	)

	# Setup and run the backtest
	bt = Backtest(ohlc_data, NineOne, cash=10_000_000, margin=1, commission=.00)

	# Execute the backtest
	results = bt.run()

	# Print the results
	print(results)

	# Optionally, plot the results
	bt.plot()
