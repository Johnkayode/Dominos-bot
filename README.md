# Domino's Pizza Order Bot

### A Telegram Bot-As-A-Service for ordering from Domino's Pizza Stores in Nigeria.

## Use
1. Click here https://t.me/dominos_orderbot
or search @dominos_orderbot on Telegram app.
2. Then click the start button or use the /start command to start the bot.


## Installation 
To begin installation git clone repo into preferred directory
```
git clone https://github.com/Johnkayode/Dominos-bot.git
```
Install required packages 
```
pip install -r requirements.txt
```
Create a .env file for your Telegram, Fauna and Google API Keys
```
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
FAUNA_TOKEN=<your-fauna-key>
GOOGLE_API_KEY=<google-api-key>
```
Edit the webhook url in the bot.py file and run the bot
```
python bot.py
```