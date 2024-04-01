import pandas as pd
import pandas_ta as ta
import numpy as np


def local_sma(close, length):
    # Convert to pandas series.
    close = pd.Series(close)

    # computing the simple moving average without using pandas-ta.
    # Used as an example for creating other custom indicators.
    sma_values = close.rolling(length).mean()

    return sma_values


def sma(close, length):
    # Convert to pandas series. Necessary for error avoidance.
    close = pd.Series(close)

    # simple moving average values calculated by the imported function.
    sma_values = ta.sma(close=close, length=length)

    return sma_values


def rsi(close, length):
    # Convert to pandas series. Necessary for error avoidance.
    close = pd.Series(close)

    # relative strength index values calculated by the imported function.
    rsi_values = ta.rsi(close=close, lenght=length)

    return rsi_values
