# algo-trading
Repo dedicate for the development of algorithmic trading strategies and proper backtest on real stock price data.

The goal is to also test machine learning techniques, such as reinforcement learning, on trading tasks.

## Getting started

1. Open the command line and move to the folder where you want to have the project in.

```bash
cd <folder/path>
```

2. Clone the repo into the folder you chose.

```bash
git clone https://github.com/vjardimb/algo-trading.git
```

3. Create a virtual environment.

```bash
python -m venv <venvname>
```

In case you already have a virtual environment, just activate it.

On Windows, run:
```bash
<venvname>\Scripts\activate
```
On Unix or MacOS, run:
```bash
source <venvname>/bin/activate
```

4. Upgrade pip and install the project dependencies.

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. To test if things are working, you can try running the sma_cross module, which backtests the SmaCross strategy on 
OHLC daily data for Google Inc.

```bash
python strategies\sma_cross.py
```