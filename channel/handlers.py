import os.path
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from utils.config_manager import save_config, load_config
from utils.logger import logger
from data.chart import Chart
from data.utils import send_image_with_caption
from channel.channel_utils import get_image_caption, initiate_channel_config
from channel.scheduler_utils import SimultaneousScheduler, SequentialScheduler


def initiate_periodic_charting(application):
    # Set up a job to send a periodic message every hour
    config = load_config()
    for chat_id in config.keys():
        if config[chat_id]["mode"] == "simultaneous":
            posting_interval: int = config[chat_id].get("posting_interval", 14400)
            pair_list = config[chat_id]["pair_list"]

            starting_time = SimultaneousScheduler(posting_interval).starting_time

            logger.info(
                f"Started periodic chart generation for {chat_id} "
                f"mode = 'simultaneous', "
                f"period = {posting_interval}, "
                f"starting time {starting_time}")

            application.job_queue.run_repeating(send_periodic_chart,
                                                interval=posting_interval,
                                                first=starting_time,
                                                chat_id=chat_id,
                                                data={"pair_list": pair_list,
                                                      "posting_interval": posting_interval,
                                                      "starting_time": starting_time})

        elif config[chat_id]["mode"] == "sequential":
            # If mode is sequential, each pair has its own queue, with the starting point being different but with the same posting_interval.
            # The starting point is determined by the order of the pairs in the list, and the starting points are spaced by the pair_interval value.
            # All the logic for the sequential mode is contained in the scheduler_utils.py file's SequentialScheduler class.

            posting_interval: int = config[chat_id].get("posting_interval", 43200)
            pair_interval: int = config[chat_id].get("pair_interval", 3600)
            pair_list = config[chat_id]["pair_list"]

            scheduler = SequentialScheduler(posting_interval, pair_interval, pair_list)
            starting_schedule = scheduler.starting_schedule

            for starting_schedule_dict in starting_schedule:
                pair = starting_schedule_dict['pair']
                starting_time = starting_schedule_dict['starting_time']

                application.job_queue.run_repeating(send_periodic_chart,
                                                    interval=posting_interval,
                                                    first=starting_time,
                                                    chat_id=chat_id,
                                                    data={"pair": pair,
                                                          "posting_interval": posting_interval,
                                                          "pair_interval": pair_interval,
                                                          "starting_time": starting_time})

            logger.info(scheduler.compose_starting_schedule())


async def handle_set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Select the mode of the bot for a channel. The mode can be either "simultaneous" or "sequential".
    """

    chat_id = str(update.channel_post.chat.id)
    title = update.channel_post.chat.title
    message_text = update.channel_post.text

    # Log the message
    logger.info(f"Config message in chat {title}({chat_id}): {message_text}")

    # Separate the setup command and process the inputs
    parts = message_text.split(" ")
    if len(parts) < 2:
        await context.bot.send_message(chat_id=chat_id,
                                       text="❌ Invalid command format. Use /setmode <mode>, where mode is either 'simultaneous' or 'sequential'.")
        return

    mode = parts[1]

    # Load the current configuration
    config = initiate_channel_config(chat_id)
    config[chat_id]["mode"] = mode

    # Save the updated configuration
    save_config(config)

    await context.bot.send_message(chat_id=chat_id, text=f"✅ Set mode to {mode}. The bot needs to be restarted for the changes to take effect.")


async def handle_add_pair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Add a pair with a timeframe to a channel. The pair name and timeframes are set by the command. THe format is /addpair <pair name> <timeframe>
    """

    chat_id = str(update.channel_post.chat.id)
    title = update.channel_post.chat.title
    message_text = update.channel_post.text

    # Log the message
    logger.info(f"Config message in chat {title}({chat_id}): {message_text}")

    # Separate the setup command and process the inputs
    parts = message_text.split(" ")

    if len(parts) < 2:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid command format. Use /addpair <pair>")
        return

    pair = parts[1]

    config = initiate_channel_config(chat_id)

    if pair not in config[chat_id]["pair_list"]:
        config[chat_id]["pair_list"].append(pair.upper())

        # Save the updated configuration
        save_config(config)

        # Post the update of the timeframe to the channel that requested it
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Added pair {pair.upper()}")

    # If pair is already on the list, nothing should change
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ {pair.upper()} already exists on the list.")


async def handle_remove_pair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Remove a pair from the channel. The pair name is set by the command. The format is /removepair <pair name>
    """

    chat_id = str(update.channel_post.chat.id)
    title = update.channel_post.chat.title
    message_text = update.channel_post.text

    # Log the message
    logger.info(f"Config message in chat {title}({chat_id}): {message_text}")

    # Separate the setup command and process the inputs
    parts = message_text.split(" ")

    if len(parts) < 2:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid command format. Use /removepair <pair>")
        return

    pair = parts[1]

    config = initiate_channel_config(chat_id)
    if pair in config[chat_id]["pair_list"]:
        config[chat_id]["pair_list"].remove(pair.upper())

        # Save the updated configuration
        save_config(config)

        # Post the update of the pair removal to the channel that requested it
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Removed pair {pair.upper()}")

    # If the pair doesn't exist in the list, nothing would change.
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"✅ {pair.upper()} doesn't exist in the channel pair list. Nothing changed.")


async def handle_show_pairs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the list of pairs in a channel.
    """

    chat_id = str(update.channel_post.chat.id)

    # message = "⚙️ Current pair and timeframe list:\n"
    message = "⚙️ Current pair list:\n"
    config = load_config()

    try:
        for pair in config[chat_id]["pair_list"]:
            message += f"🔹 {pair}\n"
    except:
        message = "❌ No data yet."

    await context.bot.send_message(chat_id=chat_id, text=message)


async def handle_set_posting_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Set the posting interval of the channel
    chat_id = str(update.channel_post.chat.id)
    title = update.channel_post.chat.title
    message_text = update.channel_post.text

    # Log the message
    logger.info(f"Interval config message in chat {title}({chat_id}): {message_text}")

    # Separate the setup command and process the inputs
    parts = message_text.split(" ")
    if len(parts) < 2:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid command format. Use /setinterval <interval>, where interval is in seconds.")
        return

    interval = parts[1]

    # Load the current configuration
    config = initiate_channel_config(chat_id)
    config[chat_id]["posting_interval"] = int(interval)

    # Save the updated configuration
    save_config(config)

    await context.bot.send_message(chat_id=chat_id,
                                   text=f"✅ Set posting interval to {interval} seconds. "
                                        f"The bot needs to be restarted for the changes to take effect.")


async def handle_set_pair_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Set the pair interval of the channel, which is the time between the pairs being posted. This parameter is ignored if mode == 'simultaneous'
    chat_id = str(update.channel_post.chat.id)
    title = update.channel_post.chat.title
    message_text = update.channel_post.text

    # Log the message
    logger.info(f"Interval config message in chat {title}({chat_id}): {message_text}")

    # Separate the setup command and process the inputs
    parts = message_text.split(" ")
    if len(parts) < 2:
        await context.bot.send_message(chat_id=chat_id,
                                       text="❌ Invalid command format. Use /setpairinterval <interval>, where interval is in seconds.")
        return

    interval = parts[1]

    # Load the current configuration
    config = initiate_channel_config(chat_id)
    config[chat_id]["pair_interval"] = int(interval)

    # Save the updated configuration
    save_config(config)

    await context.bot.send_message(chat_id=chat_id,
                                   text=f"✅ Set pair interval to {interval} seconds. The bot needs to be restarted for the changes to take effect.")


async def send_periodic_chart(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(context.job.chat_id)
    posting_interval = int(context.job.data["posting_interval"])

    config = load_config()

    if config[chat_id]["mode"] == "simultaneous":
        pair_list = [pair.replace("USDT", "").replace("USD", "") for pair in config[chat_id]["pair_list"]]

        # Initialize the Chart class and download the chart
        chart = Chart(pair_list)
        chart.download_chart()

        for pair in pair_list:
            caption = get_image_caption(pair, channel_link=config[chat_id]['channel_link'], posting_interval=posting_interval)

            output_path = os.path.join(chart.download_dir, f'heatmap_{pair}.png')

            await send_image_with_caption(output_path, context, chat_id, caption)

    elif config[chat_id]["mode"] == "sequential":
        # The pair is passed from the job queue through the context.job.data property as a dict.
        pair = context.job.data["pair"].replace("USDT", "").replace("USD", "")

        # Initialize the Chart class and download the chart
        chart = Chart(pair)
        chart.download_chart()

        caption = get_image_caption(pair, channel_link=config[chat_id]['channel_link'], posting_interval=posting_interval)

        output_path = os.path.join(chart.download_dir, f'heatmap_{pair}.png')

        await send_image_with_caption(output_path, context, chat_id, caption)


async def handle_current_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Generate and send the current chart to the channel.
    """

    chat_id = str(update.channel_post.chat.id)
    title = update.channel_post.chat.title
    message_text = update.channel_post.text

    # Log the message
    logger.info(f"Current chart request message in chat {title}({chat_id}): {message_text}")

    # Separate the setup command and process the inputs
    parts = message_text.split(" ")
    if len(parts) < 2:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid command format. Use /currentchart <symbol>, where interval is in seconds.")
        return

    pair = parts[1]

    # Initialize the Chart class and download the chart
    pair = pair.replace("USDT", "").replace("USD", "")

    await context.bot.send_message(chat_id=chat_id, text=f"⏳ Generating {pair} chart, please wait...")

    chart = Chart(pair)
    chart.download_chart()

    caption = get_image_caption(pair)
    config = load_config()
    caption = get_image_caption(pair, channel_link=config[chat_id]['channel_link'])

    output_path = os.path.join(chart.download_dir, f'heatmap_{pair}.png')

    await send_image_with_caption(output_path, context, chat_id, caption)
