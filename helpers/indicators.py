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
    rsi_values = ta.rsi(close=close, length=length)

    return rsi_values


def ema(close):
    # Convert to pandas series. Necessary for error avoidance.
    close = pd.Series(close)

    # relative strength index values calculated by the imported function.
    ema_values = ta.ema(close=close)

    return ema_values


def bbands(close, length=20, std=2.0):
    # Convert to pandas series. Necessary for error avoidance.
    close = pd.Series(close)

    # Lower, mid and upper, respectively, being calculated by the imported bbands function.
    bband_values = ta.bbands(close=close, length=length, std=std)

    return bband_values.iloc[:, :3]


def highest(price, length):
    # Convert to pandas series. Necessary for error avoidance.
    price = pd.Series(price)

    return price.rolling(length).max()


def lowest(price, length):
    # Convert to pandas series. Necessary for error avoidance.
    price = pd.Series(price)

    return price.rolling(length).min()


def atr(high, low, close, length):
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)

    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)

    return true_range.rolling(length).mean()


