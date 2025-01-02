import requests
import pandas as pd
import constants


def get_pair_data(symbol: str, timeframe: str, limit=70) -> pd.DataFrame:
    response = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&limit={limit}").json()
    df = pd.DataFrame(response, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['time'] = pd.to_datetime(df['open_time'], unit='ms')
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
    df = df.set_index('time')

    return df


async def send_image_with_caption(image_path, context, chat_id, caption):
    # Send the chart image to the channel
    with open(image_path, 'rb') as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)

