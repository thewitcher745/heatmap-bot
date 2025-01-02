from datetime import datetime, timezone

from channel.handlers import send_periodic_chart
from utils.config_manager import load_config
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

    # +30 to make sure the candles are formed, I guess?
    return seconds_until_next_interval + 30


# Error handler function
async def error_handler(update, context):
    logger.error(f"Update {update} caused error {context.error}")


def initiate_periodic_charting(application):
    # Set up a job to send a periodic message every hour
    config = load_config()
    for chat_id in config.keys():
        logger.info(f"Started periodic chart generation for {chat_id}")
        posting_interval: int = config[chat_id].get("posting_interval", 3600)
        first_interval = get_seconds_until_next_interval(posting_interval)
        application.job_queue.run_repeating(send_periodic_chart, interval=posting_interval, first=first_interval, chat_id=chat_id)
