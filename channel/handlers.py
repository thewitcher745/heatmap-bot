from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from utils.config_manager import save_config, load_config
from utils.logger import logger


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
    if len(parts) < 3:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid command format. Use /addpair <pair> <timeframe>")
        return

    pair = parts[1]
    timeframe = parts[2]

    # Load the current configuration
    config = load_config()

    if chat_id not in config:
        config[chat_id]["pair_info"] = []
    config[chat_id]["pair_info"].append({'pair': pair, 'timeframe': timeframe})

    # Save the updated configuration
    save_config(config)

    # Post the update of the timeframe to the channel that requested it
    await context.bot.send_message(chat_id=chat_id, text=f"✅ Added pair {pair} with timeframe {timeframe}")


async def handle_show_pairs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the list of pairs in a channel.
    """

    chat_id = str(update.channel_post.chat.id)

    message = "⚙️ Current pair and timeframe list:\n"
    config = load_config()

    for pair_info_item in config[chat_id]["pair_info"]:
        message += f"🔹 {pair_info_item['pair']} - {pair_info_item['timeframe']}\n"

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

    config[chat_id]["posting_interval"] = int(interval)

    # Save the updated configuration
    save_config(config)

    await context.bot.send_message(chat_id=chat_id,
                             text=f"✅ Set posting interval to {interval} seconds. The bot needs to be restarted for the changes to take effect.")


async def send_periodic_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(context.job.chat_id)

    # Get the current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create the message with the current time
    message = f"🕒 Current time: {current_time}"

    # Send the message to the chat
    await context.bot.send_message(chat_id=chat_id, text=message)
