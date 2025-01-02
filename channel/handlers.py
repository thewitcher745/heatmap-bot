import os.path
from telegram import Update
from telegram.ext import ContextTypes

from channel.channel_utils import get_image_caption
from utils.config_manager import save_config, load_config
from utils.logger import logger
from data.chart import Chart
from data.utils import send_image_with_caption


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

    # if len(parts) < 3:
    #     await context.bot.send_message(chat_id=chat_id, text="❌ Invalid command format. Use /addpair <pair> <timeframe>")
    #     return
    #
    # pair = parts[1]
    # timeframe = parts[2]
    #
    # # Load the current configuration
    # config = load_config()
    #
    # if chat_id not in config:
    #     config[chat_id] = {
    #         "posting_interval": 3600
    #     }
    #     config[chat_id]["pair_info"] = []
    # config[chat_id]["pair_info"].append({'pair': pair, 'timeframe': timeframe})

    if len(parts) < 2:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid command format. Use /addpair <pair>")
        return

    pair = parts[1]
    # timeframe = parts[2]

    # Load the current configuration
    config = load_config()

    if chat_id not in config:
        config[chat_id] = {
            "posting_interval": 3600
        }
        config[chat_id]["pair_info"] = []
    config[chat_id]["pair_info"].append({'pair': pair})

    # Save the updated configuration
    save_config(config)

    # Post the update of the timeframe to the channel that requested it
    await context.bot.send_message(chat_id=chat_id, text=f"✅ Added pair {pair}")


async def handle_show_pairs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the list of pairs in a channel.
    """

    chat_id = str(update.channel_post.chat.id)

    # message = "⚙️ Current pair and timeframe list:\n"
    message = "⚙️ Current pair list:\n"
    config = load_config()

    try:
        for pair_info_item in config[chat_id]["pair_info"]:
            # message += f"🔹 {pair_info_item['pair']} - {pair_info_item['timeframe']}\n"
            message += f"🔹 {pair_info_item['pair']}\n"
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
    config = load_config()

    if chat_id not in config:
        config[chat_id] = {
            "posting_interval": 3600
        }
        config[chat_id]["pair_info"] = []
    config[chat_id]["posting_interval"] = int(interval)

    # Save the updated configuration
    save_config(config)

    await context.bot.send_message(chat_id=chat_id,
                                   text=f"✅ Set posting interval to {interval} seconds. The bot needs to be restarted for the changes to take effect.")


async def send_periodic_chart(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(context.job.chat_id)

    config = load_config()
    pair_list = [pair_info_item["pair"].replace("USDT", "").replace("USD", "") for pair_info_item in config[chat_id]["pair_info"]]

    # Initialize the Chart class and download the chart
    chart = Chart(pair_list)
    chart.download_chart()

    for pair in pair_list:
        caption = get_image_caption(pair)

        output_path = os.path.join(chart.download_dir, f'heatmap_{pair}.png')

        await send_image_with_caption(output_path, context, chat_id, caption)


async def handle_current_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Generate and send the current chart to the channel.
    """

    # Set the posting interval of the channel
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

    output_path = os.path.join(chart.download_dir, f'heatmap_{pair}.png')

    await send_image_with_caption(output_path, context, chat_id, caption)
