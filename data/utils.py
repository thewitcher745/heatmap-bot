import requests
import pandas as pd
import constants


def get_candlesticks(symbol: str, timeframe: str, limit=70) -> pd.DataFrame:
    """
    Get the candlesticks for a given symbol

    Args:
        symbol (str): The symbol to get the candlesticks for
        timeframe (str): The interval to get the candlesticks for
        limit (int): The number of candles to fetch

    Returns:
        pd.DataFrame: The candlesticks data
    """

    response = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&limit={limit}").json()

    # Convert the response to a DataFrame
    df = pd.DataFrame(response, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])

    # Convert timestamp columns to datetime
    df['time'] = pd.to_datetime(df['open_time'], unit='ms')
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)

    # Select only the time and OHLC columns
    df = df[['time', 'open', 'high', 'low', 'close']]

    # Set the "time" column as the index
    df = df.set_index('time')

    return df
