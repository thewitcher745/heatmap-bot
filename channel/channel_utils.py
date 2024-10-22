from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from utils.logger import logger
import constants


# Function to handle incoming messages
def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.channel_post.chat.id
    title = update.channel_post.chat.title
    message_text = update.channel_post.text

    # Log the message
    logger.info(f"Message in chat {title}({chat_id}): {message_text}")


# Create the Application and pass it your bot's token
application = ApplicationBuilder().token(constants.BOT_TOKEN).build()

# Register the message handler
application.add_handler(MessageHandler(filters.COMMAND, handle_message))

# Start the Bot
application.run_polling()
