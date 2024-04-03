import yfinance as yf
import pandas as pd


def get_ohlc_data(ticker, start_date, end_date, interval, auto_adjust=True):
	# Fetch the historical data
	data = yf.download(
		ticker,
		start=start_date,
		end=end_date,
		interval=interval,
		auto_adjust=auto_adjust
	)

	# remove days without negotiations
	data = data[data.High != data.Low]
	data.reset_index(inplace=True)

	# Set Datetime/Date column as df index
	if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
		datetime_column = "Datetime"
	else:
		datetime_column = "Date"

	data[datetime_column] = pd.to_datetime(data[datetime_column], format='%d.%m.%Y %H:%M:%S')
	data.set_index(datetime_column, inplace=True)
	data.index.name = None

	return data
