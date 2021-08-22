from dominos import api
import telegram

from dominos.api import DominosNGClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ( Updater, 
    CommandHandler, 
    MessageHandler, 
    ConversationHandler, 
    Filters, 
    CallbackQueryHandler
)



telegram_bot_token = "1999242546:AAGVFTQy19ouCD1eFTtd4V4IYqmf6fL2Q7A"


client = DominosNGClient()

updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher



def start(update, context):
    '''
    This function receives the user's details and sends a welcome message
    '''
    chat_id = update.effective_chat.id
    username = update["message"]["chat"]["username"]
    first_name = update["message"]["chat"]["first_name"]
    last_name = update["message"]["chat"]["last_name"]

    """
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    print(longitude, latitude)
    """
    msg = f"Hello {first_name},\nWelcome to the unofficial bot for Domino's Pizza Nigeria. My name is John and i'll be your botler"
    context.bot.send_message(chat_id=chat_id, text=msg)

def location(update, context):

    chat_id = update.effective_chat.id
    location = update.message.location
    stores = client.findNearbyStoresFromLocation(location.latitude, location.longitude)

    

    for store in stores:

        if store['IsDeliveryStore']=="true":

            keyboard = [
                InlineKeyboardButton("Delivery", callback_data=f"Delivery_{store['StoreID']}"),
                InlineKeyboardButton("Carryout", callback_data=f"Carryout_{store['StoreID']}")
            ]

        keyboard = [
                InlineKeyboardButton("Carryout", callback_data=f"Carryout_{store['StoreID']}")
        ]

        reply_markup = InlineKeyboardMarkup([keyboard])

        msg = f"{store['StoreName']}\n{store['StreetName']}, {store['City']}\n{store['Phone']}\n\nService Hours: \n\nDelivery: \n{store['ServiceHoursDescription']['Delivery']}\n\nCarryout: \n{store['ServiceHoursDescription']['Carryout']}"
        context.bot.send_message(chat_id=chat_id, text = msg, reply_markup=reply_markup)

def button(update, context):
    chat_id = update.effective_chat.id
    query = update.callback_query

    query.answer()
    
    # This will define which button the user tapped on (from what you assigned to "callback_data". As I assigned them "1" and "2"):
    choice = query.data

    if "Delivery" in choice or "Carryout" in choice:
        choice = choice.split('_')
        order_type = choice[0]
        store_id = choice[1]

        context.bot.send_message(chat_id=chat_id, text = f"{order_type} {store_id}")

    


def find_stores(update, context):
    pass
    




dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.location, location))
dispatcher.add_handler(CommandHandler("find_stores", find_stores))
dispatcher.add_handler(CallbackQueryHandler(button))

updater.start_polling()