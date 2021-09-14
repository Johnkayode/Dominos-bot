# Domino's Pizza Order Bot

### A Telegram Bot-As-A-Service for ordering from Domino's Pizza Stores in Nigeria.

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
Run the bot
```
python bot.py
```