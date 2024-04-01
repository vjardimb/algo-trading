# How to Use Technical Indicators

The goal of this document is to show you the way indicators are used in this project, either from imported libraries or
from custom functions locally implemented.

Whichever way is chosen, the function relating to the desired indicator must be implemented in the file "incicators.py",
and not in the module where the strategy where it will be used is located. This facilitates accessibility, organization
and taking advantage of previously written code dedicated to different strategies.

## Importing from pandas_ta

For more commonly used technical indicators, it is recommended to import the same from the pandas_ta specified in the 
project requirements. To do this, make sure that the library is being imported at the top of the script.

In this case, the indicator calculation is done by the imported function. The function to be written will only serve as a wrapper
which will enable its use in an easier way within the strategies created.

```python
import pandas_ta as ta
import pandas as pd


def sma(close, length):
    # Convert to pandas series. Necessary for error avoidance.
    close = pd.Series(close)

    # simple moving average values calculated by the imported function.
    sma_values = ta.sma(close=close, lenght=length)

    return sma_values
```

## Custom indicators

In case you want to write your own indicators, also use the "indicators.py" file to store the functions that
you will create.

This time, these functions will be responsible for the complete processing of OHLCV data.

```python
import pandas_ta as ta
import pandas as pd


def local_sma(close, length):
    # Convert to pandas series.
    close = pd.Series(close)
    
    # computing the simple moving average without using pandas-ta. 
    # Used as an example for creating other custom indicators.
    sma_values = close.rolling(length).mean()
    
    return sma_values
```

##Conventions

Function arguments must follow the following pattern:
   * open: opening price of the candle.
   * high: maximum of the candle.
   * low: minimum of the candle.
   * close: closing price of the candle.
   * volume: candle trading volume.
   * length: number of candles used in the calculation, such as that used in simple moving averages, rsi, bbands etc.

For different arguments, follow the PEP8 convention and prioritize clarity.