from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import json
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

AUTHORIZED_USERS = ['523608787']  # List of authorized Telegram user IDs as strings

def load_config():
    with open('config.json') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)

def update_qty(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text('You are not authorized to perform this action.')
        return

    try:
        new_qty = context.args[0]
        config = load_config()
        config['priyanka']['qty'] = new_qty
        save_config(config)
        update.message.reply_text(f'Qty updated to {new_qty}.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /qty <new_qty>')

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('qty', update_qty))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
