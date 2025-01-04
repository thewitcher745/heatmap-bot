from datetime import datetime, timezone, timedelta

import constants
from utils.config_manager import load_config, save_config
from utils.logger import logger


def get_seconds_until_next_interval(interval):
    """
    Calculate the number of seconds until the next interval.

    Args:
        interval (int): The interval in seconds.

    Returns:
        float: The number of seconds until the next interval.
    """

    now = datetime.now(timezone.utc)
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    seconds_until_next_interval = interval - (seconds_since_midnight % interval)

    # +delay to make sure the candles are formed
    return seconds_until_next_interval + constants.CHART_DELAY_SECONDS


# Error handler function
async def error_handler(update, context):
    logger.error(f"Update {update} caused error {context.error}")


def get_image_caption(pair, posting_interval: int = None):
    # Convert the seconds of posting_interval to hours
    interval_in_hours = int(posting_interval / 3600)

    if posting_interval:
        caption = f"""
⚡️ #{pair} Liquidation Heatmap ⚡️

{interval_in_hours} Hourly Update 🔔

The color range is between Purple to Yellow!

Yellow Represents Higher Number of Liquidation Levels.

https://t.me/cryptoliquidationheatmap"""
    else:
        caption = f"""
⚡️ #{pair} Liquidation Heatmap ⚡️

Latest Update 🔔

The color range is between Purple to Yellow!

Yellow Represents Higher Number of Liquidation Levels.

https://t.me/cryptoliquidationheatmap"""

    return caption


def initiate_channel_config(chat_id: str):
    """
    Initialize the configuration for a channel, if no config exists.

    Args:
        chat_id (str): The ID of the channel.
    """

    config = load_config()

    if chat_id not in config:
        config[chat_id] = {
            "posting_interval": 14400,  # 4 hours by default
            "mode": "simultaneous",
            "pair_list": []
        }

        save_config(config)
        logger.info(f"Initialized configuration for channel {chat_id}")

    else:
        logger.info(f"Configuration for channel {chat_id} already exists")

    return config
