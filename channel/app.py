from telegram.ext import ApplicationBuilder, CommandHandler, filters

import constants
from channel.handlers import handle_add_pair, handle_show_pairs, handle_set_posting_interval, send_periodic_message
from utils.config_manager import load_config

# Create the Application and pass it your bot's token
application = ApplicationBuilder().token(constants.BOT_TOKEN).build()


# Set up a job to send a periodic message every hour
config = load_config()
for chat_id in config.keys():
    posting_interval: int = config[chat_id].get("posting_interval", 3600)
    application.job_queue.run_repeating(send_periodic_message, interval=posting_interval, first=0, chat_id=chat_id)

# Register the message handlers
application.add_handler(CommandHandler("addpair", filters=filters.COMMAND, callback=handle_add_pair))
application.add_handler(CommandHandler("showpairs", filters=filters.COMMAND, callback=handle_show_pairs))
application.add_handler(CommandHandler("setinterval", filters=filters.COMMAND, callback=handle_set_posting_interval))

# Start the Bot
application.run_polling()
