import os
import pytz

from datetime import datetime
from dominos.api import DominosNGClient
from dotenv import load_dotenv

from faunadb.client import FaunaClient
from faunadb import query as q

from telegram import ( 
    ReplyKeyboardMarkup, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    ReplyKeyboardRemove,
    replymarkup
)

from telegram.ext import ( Updater,  
    ConversationHandler, 
)

from utils import geocode



load_dotenv()



fauna_client = FaunaClient(secret=os.getenv("FAUNA_TOKEN"), domain="db.us.fauna.com")
client = DominosNGClient()

updater = Updater(token=os.getenv("TELEGRAM_BOT_TOKEN"), use_context=True)
dispatcher = updater.dispatcher



CONFIRM_ADDRESS, SAVE_ADDRESS, ADDRESS_OR_LOCATION, FIND_STORES = range(4)




# Main Functions


def start(update, context):
    '''
    This function receives and saves the user's details and sends a welcome message
    '''

    chat_id = update.effective_chat.id
    name = update.message.chat.first_name or update.message.chat.username

    try:
        user = fauna_client.query(q.get(q.match(q.index("id"), chat_id)))
    except:
        user = fauna_client.query(q.create(q.collection("users"), {
            "data": {
                "id": chat_id,
                "name": name,
                "address": "",
                "latitude": "",
                "longitude": "",
                "date": datetime.now(pytz.UTC)
            }
        }))

    context.user_data["user_id"] = user["ref"].id()

    msg = f"Hello {name},\nWelcome to the unofficial bot for Domino's Pizza Nigeria.\n"\
    "My name is John and i'll be your botler\n\n"\
    "/set_address To set your address\n"\
    "/start_order To start order\n"\
    "/cart To view your cart items\n"\
    "/update_address To update address details\n"\
    "/recent_orders To get your recent orders"

    context.bot.send_message(chat_id=chat_id, text=msg)

def set_address(update, context):
    '''
    This function is used to request the user's address
    '''

    chat_id = update.effective_chat.id

    name = update.message.chat.first_name or update.message.chat.username

    try:
        user = fauna_client.query(q.get(q.match(q.index("id"), chat_id)))
    except:
        user = fauna_client.query(q.create(q.collection("users"), {
            "data": {
                "id": chat_id,
                "name": name,
                "address": "",
                "latitude": "",
                "longitude": "",
                "date": datetime.now(pytz.UTC)
            }
        }))

    context.user_data["user_id"] = user["ref"].id()

    msg = "Type your address in this format: [Street number], [Street name], [City]\n"\
    "E.g 49, Kunle Street, Lagos"

    context.bot.send_message(chat_id=chat_id, text=msg)

    return CONFIRM_ADDRESS

def confirm_address(update, context):
    '''
    This function receives the user's address and checks with Google API.
    Then asks user to confirm the address
    '''

    chat_id = update.effective_chat.id
    address = update.message.text


    try:

        # Check address with Google API
        address = geocode(address)

        if address:

            # Asks user to confirm

            msg = f"{address['address']}\n\nIs this your address. (YES/NO)?"
            context.user_data['address'] = address['address']
            context.user_data['latitude'] = address['latitude']
            context.user_data['longitude'] = address['longitude']

            reply_keyboard = [['YES','NO']]
            markup = ReplyKeyboardMarkup(reply_keyboard)
            context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=markup)

            return SAVE_ADDRESS
            
        
        else:

            context.bot.send_message(chat_id=chat_id, text="Address Not Found. Try setting another address.")
            return ConversationHandler.END


    except:
        context.bot.send_message(chat_id=chat_id, text="Address Not Found. Try setting another address")
        return ConversationHandler.END

def save_address(update, context):
    '''
    If the user's address is confirmed, it is saved to the DB
    '''

    chat_id = update.effective_chat.id
    choice = update.message.text


    address = context.user_data['address']
    latitude = context.user_data['latitude']
    longitude = context.user_data['longitude']

    if choice.lower() == 'yes':

        # Updates user's address to DB
        fauna_client.query(q.update(q.ref(
            q.collection("users"), context.user_data["user_id"]), 
            {
                "data": {
                    "address": address, 
                    "latitude": latitude, 
                    "longitude": longitude
                }
            }
        ))

        msg = "Your address has been saved."
            
    elif choice.lower() == 'no':
        msg = "Your address wasn't found, try another address keyword"
    else:
        msg = "Unrecognized reply. Try YES or NO"

    context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def start_order(update, context):
    chat_id = update.effective_chat.id
    msg = "Do you want to use your saved address or current location ?"
    reply_keyboard = [
        [
            InlineKeyboardButton(
                text="Saved Address",
                callback_data="Saved Address"
            ),
            InlineKeyboardButton(
                text="Current Location",
                callback_data="Current Location"
            )
        ]
    ]
    markup = InlineKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=markup)

    return ADDRESS_OR_LOCATION

def address_or_location(update, context):

    chat_id = update.callback_query.message.chat.id
    if update.callback_query.data.lower() == "saved address":
        user = fauna_client.query(q.get(q.match(q.index("id"), chat_id)))

        if user['data']['address']:
            stores = client.findNearbyStoresFromLocation(user['data']['latitude'], user['data']['longitude'])

            for store in stores:

                keyboard = [
                            InlineKeyboardButton("Carryout", callback_data=f"Carryout_{store['StoreID']}")
                ]

                if store['IsDeliveryStore']=="true":

                    keyboard = [
                        InlineKeyboardButton("Delivery", callback_data=f"Delivery_{store['StoreID']}"),
                        InlineKeyboardButton("Carryout", callback_data=f"Carryout_{store['StoreID']}")
                    ]

                

                reply_markup = InlineKeyboardMarkup([keyboard])

                msg = f"{store['StoreName']}\n{store['StreetName']}, {store['City']}\n{store['Phone']}"\
                f"\n\nService Hours: \n\nDelivery: \n{store['ServiceHoursDescription']['Delivery']}"\
                f"\n\nCarryout: \n{store['ServiceHoursDescription']['Carryout']}"
                context.bot.send_message(chat_id=chat_id, text = msg, reply_markup=reply_markup)
        
        else:
            msg = "You don't have any saved address\n/set_address To save your address"
            context.bot.send_message(chat_id=chat_id, text=msg)
       
    elif update.callback_query.data.lower() == "current location":

        msg = "Send your current location\n\n"
        "Don't know how to send location? Check here: https://telegram.org/blog/live-locations"
        context.bot.send_message(chat_id=chat_id, text=msg)
        return FIND_STORES

    else:

        context.bot.send_message(chat_id=chat_id, text="Unrecognized Reply\n\n/start_order To start order")

def location(update, context):

    chat_id = update.effective_chat.id
    location = update.message.location
    stores = client.findNearbyStoresFromLocation(location.latitude, location.longitude)

    

    for store in stores:

        keyboard = [
                InlineKeyboardButton("Carryout", callback_data=f"Carryout_{store['StoreID']}")
        ]

        if store['IsDeliveryStore']=="true":

            keyboard = [
                InlineKeyboardButton("Delivery", callback_data=f"Delivery_{store['StoreID']}"),
                InlineKeyboardButton("Carryout", callback_data=f"Carryout_{store['StoreID']}")
            ]


        reply_markup = InlineKeyboardMarkup([keyboard])

        msg = f"{store['StoreName']}\n{store['StreetName']}, {store['City']}\n{store['Phone']}"\
        f"\n\nService Hours: \n\nDelivery: \n{store['ServiceHoursDescription']['Delivery']}"\
        f"\n\nCarryout: \n{store['ServiceHoursDescription']['Carryout']}"
        context.bot.send_message(chat_id=chat_id, text = msg, reply_markup=reply_markup)

def button(update, context):
    chat_id = update.effective_chat.id
    query = update.callback_query

    query.answer()
    
    # This will define which button the user tapped on (from what you assigned to "callback_data"):
    choice = query.data

    if "Delivery" in choice or "Carryout" in choice:
        choice = choice.split('_')
        order_type = choice[0]
        store_id = choice[1]

        menu = client.storemenu(store_id)
        context.bot.send_message(chat_id=chat_id, text = "Seen")


# Control


def cancel(update, context) -> int: 
    update.message.reply_text(
        'Cancelled.',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def common_message(update, context):
    pass






