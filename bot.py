import os

from commands import *
from logger import error
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
            CONFIRM_ADDRESS: [
                MessageHandler(
                    Filters.all, confirm_address
                )
            ],
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
                MessageHandler(Filters.location, location),
            ],
            MENU: [
                CallbackQueryHandler(menu)
            ],
            SUBMENU: [
                CallbackQueryHandler(sub_menu)
            ],
            ADD_TO_CART:[
                CallbackQueryHandler(add_to_cart)
            ]
        
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    PORT = int(os.environ.get('PORT', '8443'))




    dispatcher.add_handler(address_conv_handler)
    dispatcher.add_handler(order_conv_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(None, common_message))
    

    #dispatcher.add_error_handler(error)

    updater.start_polling()



    '''
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=os.getenv("TELEGRAM_BOT_TOKEN"),
                          webhook_url='https://dominos-order-bot.herokuapp.com/' + os.getenv("TELEGRAM_BOT_TOKEN")
                        )
    '''
    updater.idle()


if __name__ == '__main__':
    main()