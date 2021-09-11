import os

from commands import *
from logging import error
from telegram.ext import (
    CommandHandler, 
    MessageHandler, 
    ConversationHandler, 
    Filters, 
    CallbackQueryHandler
)




def main():
    address_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("set_address", set_address)],
        states={
            SAVE_ADDRESS: [
                MessageHandler(
                    Filters.all, save_address
                )
            ]
        
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    order_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start_order", start_order)],
        states={
            ADDRESS_OR_LOCATION: [
                CallbackQueryHandler(address_or_location)
            ],
            FIND_STORES: [
                MessageHandler(Filters.location, location)
            ]
        
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    PORT = int(os.environ.get('PORT', 5000))




    dispatcher.add_handler(address_conv_handler)
    dispatcher.add_handler(order_conv_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(None, common_message))
    dispatcher.add_handler(CallbackQueryHandler(button))

    dispatcher.add_error_handler(error)

    #updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=os.getenv("TELEGRAM_BOT_TOKEN"))
    updater.bot.setWebhook('https://dominos-order-bot.herokuapp.com/' + os.getenv("TELEGRAM_BOT_TOKEN"))

    updater.idle()

if __name__ == '__main__':
    main()