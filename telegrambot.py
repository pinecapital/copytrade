from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, CallbackContext,
                          ConversationHandler, MessageHandler, Filters)
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the TOKEN from environment variables
TOKEN = os.getenv("TOKEN")
AUTHORIZED_USERS = ['523608787']  # List of authorized Telegram user IDs as strings

SELECT_USER, GET_QTY = range(2)  # Define conversation states
LIST_USERS, ADD_USER = range(4, 6)

def load_config():
    with open('config.json') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Update Qty", callback_data='update_qty')],
        [InlineKeyboardButton("List Users", callback_data='list_users')],
        [InlineKeyboardButton("Add New User", callback_data='add_user')],
        # Add other buttons here as needed
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome to the bot. Choose an option:', reply_markup=reply_markup)
def list_users(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_list = load_config().keys()
    user_list_message = "List of users:\n" + "\n".join(user_list)
    query.edit_message_text(text=user_list_message)

def add_user(update: Update, context: CallbackContext):
    update.callback_query.edit_message_text('Please send the new user\'s name.')
    return ADD_USER
def receive_new_user(update: Update, context: CallbackContext):
    new_user_name = update.message.text.strip()
    if new_user_name:
        # Add the new user to config with default values
        config = load_config()
        if new_user_name in config:
            update.message.reply_text(f'User {new_user_name} already exists.')
        else:
            config[new_user_name] = {"qty": "0"}  # Add new user with default qty of 0
            save_config(config)
            update.message.reply_text(f'User {new_user_name} added with default quantity of 0.')
    else:
        update.message.reply_text('The name cannot be empty. Please try again.')

    return ConversationHandler.END
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = str(query.from_user.id)

    # Check if user is authorized
    if user_id not in AUTHORIZED_USERS:
        query.edit_message_text(text='You are not authorized to perform this action.')
        return ConversationHandler.END

    if query.data == 'update_qty':
        # Load the current config to display qty with user buttons
        current_config = load_config()
        # Ask which user to update
        keyboard = [[InlineKeyboardButton(f"{user} (Current Qty: {current_config[user]['qty']})", callback_data=user)]
                    for user in current_config.keys()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text='Select a user to update qty:', reply_markup=reply_markup)
        return SELECT_USER

def select_user(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data['selected_user'] = query.data  # Store the selected user
    query.edit_message_text(text='Enter the new quantity:')
    return GET_QTY

def get_qty(update: Update, context: CallbackContext):
    qty = update.message.text
    selected_user = context.user_data.get('selected_user')

    if not qty.isdigit():
        update.message.reply_text('Please enter a valid number for quantity.')
        return GET_QTY

    config = load_config()
    config[selected_user]['qty'] = qty
    save_config(config)
    update.message.reply_text(f'Qty for {selected_user} updated to {qty}.')

    return ConversationHandler.END

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Use /start to update quantity.')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Define conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            SELECT_USER: [CallbackQueryHandler(select_user)],
            GET_QTY: [MessageHandler(Filters.text & ~Filters.command, get_qty)],
            LIST_USERS: [CallbackQueryHandler(list_users)],
            ADD_USER: [MessageHandler(Filters.text & ~Filters.command, receive_new_user)],
        },
        fallbacks=[CommandHandler('help', help_command)],
        conversation_timeout=300  # Timeout for conversation in seconds (optional)
    )

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(conv_handler)  # Handle the conversation

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
