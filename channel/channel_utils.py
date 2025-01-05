from datetime import datetime, timezone, timedelta

import constants
from utils.config_manager import load_config, save_config
from utils.logger import logger


# Error handler function
async def error_handler(update, context):
    logger.error(f"Update {update} caused error {context.error}")


def get_image_caption(pair, channel_link, posting_interval: int = None):
    if posting_interval:
        # Convert the seconds of posting_interval to hours
        interval_in_hours = int(posting_interval / 3600)

        caption = f"""
⚡️ #{pair} Liquidation Heatmap ⚡️

{interval_in_hours} Hourly Update 🔔

The color range is between Purple to Yellow!

Yellow Represents Higher Number of Liquidation Levels.

"""
    else:
        caption = f"""
⚡️ #{pair} Liquidation Heatmap ⚡️

Latest Update 🔔

The color range is between Purple to Yellow!

Yellow Represents Higher Number of Liquidation Levels.

"""

    if channel_link:
        caption += channel_link

    return caption
