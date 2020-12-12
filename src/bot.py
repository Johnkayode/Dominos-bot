import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters 
from scraper import get_stores

telegram_bot_token = "1438440634:AAHbTaoFmzHIwAynqS3NPBXMaiAG-fmausM"

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
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    msg = f"Hello {first_name},\nWelcome to the unofficial bot for Domino's Pizza Nigeria. My name is John and i'll be your botler"
    context.bot.send_message(chat_id=chat_id, text=msg)



def find_stores(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text='Searching for nearby stores..')
    get_stores(context=context, chat_id=chat_id)
    

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("find_stores", find_stores))


updater.start_polling()