import os
import pytz

from datetime import datetime

from requests.api import options
from dominos.api import DominosNGClient
from dotenv import load_dotenv

from faunadb.client import FaunaClient
from faunadb import query as q

from telegram import ( 
    ReplyKeyboardMarkup, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    ReplyKeyboardRemove,
)

from telegram.ext import ( 
    Updater,  
    ConversationHandler, 
)

from utils import geocode



load_dotenv()



fauna_client = FaunaClient(secret=os.getenv("FAUNA_TOKEN"), domain="db.us.fauna.com")
client = DominosNGClient()

updater = Updater(token=os.getenv("TELEGRAM_BOT_TOKEN"), use_context=True)
dispatcher = updater.dispatcher




CONFIRM_ADDRESS, SAVE_ADDRESS, ADDRESS_OR_LOCATION, FIND_STORES, MENU, SUBMENU, ADD_TO_CART = range(7)




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
    '''
    This function starts the order converstaion
    '''
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
    '''
    This function receives the user's location choice and returns the nearby stores
    '''

    chat_id = update.callback_query.message.chat.id
    if update.callback_query.data.lower() == "saved address":
        user = fauna_client.query(q.get(q.match(q.index("id"), chat_id)))

        if user['data']['address']:

            stores = client.findNearbyStoresFromLocation(user['data']['latitude'], user['data']['longitude'])
            
            context.user_data['latitude'] = user['data']['latitude']
            context.user_data['longitude'] = user['data']['longitude']

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
            return MENU


            
        else:
            msg = "You don't have any saved address\n/set_address To save your address"
            context.bot.send_message(chat_id=chat_id, text=msg)
            return ConversationHandler.END
       
    elif update.callback_query.data.lower() == "current location":

        msg = "Send your current location\n\n"\
        "Don't know how to send location? Check here: https://telegram.org/blog/live-locations"
        context.bot.send_message(chat_id=chat_id, text=msg)
        return FIND_STORES

    else:

        context.bot.send_message(chat_id=chat_id, text="Unrecognized Reply\n\n/start_order To start order")
        return ConversationHandler.END

def location(update, context):
    '''
    This function receives the user's current location and returns nearby stores
    '''

    chat_id = update.effective_chat.id
    location = update.message.location
    context.user_data['latitude'] = location.latitude
    context.user_data['longitude'] = location.longitude
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
    return MENU

def menu(update, context):
    '''
    This function returns the store menu
    '''
    chat_id = update.effective_chat.id
    query = update.callback_query

    

    query.answer()
    
    # This will define which button the user tapped on (from what you assigned to "callback_data"):
    choice = query.data

    if "Delivery" in choice or "Carryout" in choice:
        choice = choice.split('_')
        order_type = choice[0]
        store_id = choice[1]
        context.user_data['order_type'] = order_type
        context.user_data['store_id'] = store_id

        menu = client.storemenu(store_id)

        
        productTypes = []
        for key, product in menu['Products'].items():
            productTypes.append(product.get('ProductType').upper())

    
        productTypes = list(set(productTypes))
        
        for category in productTypes:
            msg = f"{category.upper()}"
            keyboard = [
                InlineKeyboardButton("See Products", callback_data=f"CATEGORY_{category}"),
            ]

            reply_markup = InlineKeyboardMarkup([keyboard])
            url = f'images/{category.lower()}.png'
            if category.lower() == "papotas":
                url = "images/sides.png"
            context.bot.send_photo(chat_id=chat_id, photo=open(url, 'rb'), caption=msg, reply_markup=reply_markup)
            
        return SUBMENU
        
def sub_menu(update, context):
    '''
    This function returns a menu for a given category
    '''
    chat_id = update.callback_query.message.chat.id
    choice = update.callback_query.data.split('_')
    if choice[0] == 'CATEGORY':
        category = choice[1]
        store_id = context.user_data['store_id']
        menu = client.storemenu(store_id)
        
        
        
        for key, item in menu['Products'].items():
            if item.get('ProductType').upper() == category:
                
                for variant in item.get('Variants'):
                    product = menu['Variants'][variant]
                    name = product['Name']
                    price = product['Price']
        
                    keyboard = [
                        InlineKeyboardButton("Add To Cart", callback_data=f"{product['ProductCode']}")
                    ]

                    msg = f"{name}\nNGN {price}"
                    url = f"https://cache.dominos.com/olo/6_64_5/assets/build/market/NG/_en/images/img/products/larges/{product['ProductCode']}.jpg"
                    reply_markup = InlineKeyboardMarkup([keyboard])
                    context.bot.send_photo(chat_id=chat_id, photo=url, caption=msg, reply_markup=reply_markup)
        return ADD_TO_CART

def add_to_cart(update, context):
    '''
    This function adds an item to the cart or increases its quantity
    '''
    chat_id = update.callback_query.message.chat.id
    product_code = update.callback_query.data
    store_id = context.user_data['store_id']
    order_type = context.user_data['order_type'] or 'Carryout'
    
    try:
        context.user_data['id']
    except:
        context.user_data['id'] = 0

    store = client.getStoreDetails(store_id)
    streetName = store['StreetName']
    city = store['City']

    try:
        latitude = context.user_data['latitude']
        longitude = context.user_data['longitude']
    except:
        user = fauna_client.query(q.get(q.match(q.index("id"), chat_id)))
        latitude = user['data']['latitude']
        longitude = user['data']['longitude']

    '''
    options = {
        "D": {
            "1/1": "1"
        },
        "C": {
            "1/1": "1"
        },
        "I": {
            "1/1": "1"
        },
        "M": {
            "1/1": "1"
        },
        "N": {
            "1/1": "1"
        },
        "X": {
            "1/1": "1"
        }
    }
    '''
    options = {}


    try:
        cart = fauna_client.query(q.get(q.match(q.index("customer_id"), chat_id)))
    except:
        cart = fauna_client.query(q.create(q.collection("cart"), {
            "data": {
                "customer_id": chat_id,
                "products": [],
                "store_id": store_id,
                "order_id" : "",
                "order_type": order_type,
                "date": datetime.now(pytz.UTC)
            }
        }))

    ref = cart['ref'].id()

    cart = cart['data']['products']
    new_product = {
            "Code": product_code,
            "Qty": 1,
            "ID": 1,
            "isNew": True,
            "Options": options
        }

    # Checks if product is already in cart
    for product in cart:
        if product['Code'] == new_product['Code']:
            product['Qty'] += 1
            break
    else:
        context.user_data['id'] += 1
        new_product["ID"] = context.user_data['id']
        cart.append(new_product)

    

    orderID = context.user_data.get('orderID',"")

    try:
        order_id = client.addToCart(
                    store_id=store_id, 
                    store_city=city, 
                    store_street=streetName, 
                    latitude=latitude, 
                    longitude=longitude, 
                    products=cart,
                    orderID=orderID,
                    order_type=order_type,
                )

        context.user_data['orderID'] = order_id

        fauna_client.query(q.update(q.ref(
                q.collection("cart"), ref), 
                {
                    "data": {
                        "products": cart, 
                        "order_id": order_id
                    }
                }
        ))

        msg =  f'Product Added\n\nSee Your Cart /cart'
    except:
        msg = "Something went wrong, try again later."

    context.bot.send_message(chat_id=chat_id, text = msg)

def view_cart(update, context):
    '''
    View Cart Items
    '''

    chat_id = update.callback_query.message.chat.id
    try:
        cart = fauna_client.query(q.get(q.match(q.index("customer_id"), chat_id)))
        orderID = cart['data']['order_id']
        store_id = cart['data']['store_id']
        order_type = cart['data']['order_type']
        products = cart['data']['products']

        store = client.getStoreDetails(store_id)
        streetName = store['StreetName']
        city = store['City']

        try:
            latitude = context.user_data['latitude']
            longitude = context.user_data['longitude']
        except:
            user = fauna_client.query(q.get(q.match(q.index("id"), chat_id)))
            latitude = user['data']['latitude']
            longitude = user['data']['longitude']

        cart_summary = client.PriceOrder(
                        store_id=store_id, 
                        store_city=city, 
                        store_street=streetName, 
                        latitude=latitude, 
                        longitude=longitude, 
                        products=products,
                        orderID=orderID,
                        order_type=order_type,
                    )

        order_id = f"Order ID: {cart_summary['Order']['OrderID']}\n"
    
        for product in cart_summary['Order']['Products']:
            cart_item = f"{product['id']}. {product['Name']}\nDescription: {product['descriptions'][0]['value']}"\
                f"Qty: {product['Qty']}\nAmount: NGN {product['Amount']}"
            keyboard = [
                        InlineKeyboardButton("Remove from Cart", callback_data=f"{product['Code']}")
                    ]
            reply_markup = InlineKeyboardMarkup([keyboard])
            context.bot.send_message(chat_id=chat_id, text=cart_item, reply_markup=reply_markup)

        msg = f"Amount: NGN {cart_summary['Order']['Amounts']['Menu']}\nTax: NGN {cart_summary['Order']['Amounts']['Tax']}\n"\
            f"Discount: NGN {cart_summary['Order']['Amounts']['Discount']}\n\n"\
            f"Total: NGN {cart_summary['Order']['Amounts']['Payment']}"

        keyboard = [
                    InlineKeyboardButton("Checkout", callback_data=f"Checkout_{cart_summary['Order']['OrderID']}")
                ]
        reply_markup = InlineKeyboardMarkup([keyboard])
        context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=reply_markup)

    except:
        msg = "Your Cart is empty\n\n/start_order To start order"
        context.bot.send_message(chat_id=chat_id, text=msg)


# Control
def cancel(update, context) -> int: 
    update.message.reply_text(
        'Cancelled.',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def common_message(update, context):
    pass





