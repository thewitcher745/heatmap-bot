from telegram.ext import ApplicationBuilder, CommandHandler, filters

import constants
from channel.handlers import handle_setup_command

# Create the Application and pass it your bot's token
application = ApplicationBuilder().token(constants.BOT_TOKEN).build()

# Register the message handler
application.add_handler(CommandHandler("/setuphm", filters=filters.COMMAND, callback=handle_setup_command))

# Start the Bot
application.run_polling()
