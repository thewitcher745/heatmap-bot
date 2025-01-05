from telegram.ext import ApplicationBuilder, CommandHandler, filters

import constants
from channel.handlers import handle_init, handle_add_pair, handle_remove_pair, handle_show_pairs, handle_set_posting_interval, handle_current_chart, \
    handle_set_mode, handle_set_pair_interval, initiate_periodic_charting
from channel.channel_utils import error_handler

application = ApplicationBuilder().token(constants.BOT_TOKEN).build()

# Register the error handler
application.add_error_handler(error_handler)

initiate_periodic_charting(application)

# Register the message handlers
application.add_handler(CommandHandler("init", filters=filters.COMMAND, callback=handle_init))
application.add_handler(CommandHandler("addpair", filters=filters.COMMAND, callback=handle_add_pair))
application.add_handler(CommandHandler("removepair", filters=filters.COMMAND, callback=handle_remove_pair))
application.add_handler(CommandHandler("showpairs", filters=filters.COMMAND, callback=handle_show_pairs))
application.add_handler(CommandHandler("setinterval", filters=filters.COMMAND, callback=handle_set_posting_interval))
application.add_handler(CommandHandler("currentchart", filters=filters.COMMAND, callback=handle_current_chart))
application.add_handler(CommandHandler("setmode", filters=filters.COMMAND, callback=handle_set_mode))
application.add_handler(CommandHandler("setpairinterval", filters=filters.COMMAND, callback=handle_set_pair_interval))

# Start the Bot
application.run_polling()
