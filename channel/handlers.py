from telegram import Update
from telegram.ext import ContextTypes

from utils.logger import logger


async def handle_setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle incoming messages in all the channels the bot is in. This will be used as a handler function so the input args are fixed and not set by
    the code/developer.
    """

    chat_id = update.channel_post.chat.id
    title = update.channel_post.chat.title
    message_text = update.channel_post.text

    # Log the message
    logger.info(f"Message in chat {title}({chat_id}): {message_text}")
