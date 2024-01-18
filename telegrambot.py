from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, ConversationHandler
import json

# Load the configuration file
with open('config.json') as f:
    data = json.load(f)
# Define states for ConversationHandler
ADD, NAME, APPNAME, APPSOURCE, USERID, PASSWORD, USERKEY, ENCKEY, CLIENTCODE, PIN, TOTP, QTY = range(12)
# List of authorized users
authorized_users = [123456789, 987654321]  # Replace with actual user IDs

def start(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id not in authorized_users:
        update.message.reply_text('You are not authorized to use this bot.')
        return
    # Show available commands
    update.message.reply_text('/add /modifyQty /list')

def add(update: Update, context: CallbackContext) -> None:
    # Ask the user to provide the necessary information
    update.message.reply_text('Please provide name')
    return NAME
    # Ask the user to provide the necessary information
    update.message.reply_text('Please provide name,appname,appsource,userid,password,userkey,enckey,clientcode,pin,totp,qty')
def name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    update.message.reply_text('Please provide appname')
    return APPNAME
def appname(update: Update, context: CallbackContext) -> int:
    context.user_data['appname'] = update.message.text
    update.message.reply_text('Please provide appsource')
    return APPSOURCE

def appsource(update: Update, context: CallbackContext) -> int:
    context.user_data['appsource'] = update.message.text
    update.message.reply_text('Please provide userid')
    return USERID

def userid(update: Update, context: CallbackContext) -> int:
    context.user_data['userid'] = update.message.text
    update.message.reply_text('Please provide password')
    return PASSWORD

def password(update: Update, context: CallbackContext) -> int:
    context.user_data['password'] = update.message.text
    update.message.reply_text('Please provide userkey')
    return USERKEY

def userkey(update: Update, context: CallbackContext) -> int:
    context.user_data['userkey'] = update.message.text
    update.message.reply_text('Please provide enckey')
    return ENCKEY

def enckey(update: Update, context: CallbackContext) -> int:
    context.user_data['enckey'] = update.message.text
    update.message.reply_text('Please provide clientcode')
    return CLIENTCODE

def clientcode(update: Update, context: CallbackContext) -> int:
    context.user_data['clientcode'] = update.message.text
    update.message.reply_text('Please provide pin')
    return PIN

def pin(update: Update, context: CallbackContext) -> int:
    context.user_data['pin'] = update.message.text
    update.message.reply_text('Please provide totp')
    return TOTP

def totp(update: Update, context: CallbackContext) -> int:
    context.user_data['totp'] = update.message.text
    update.message.reply_text('Please provide qty')
    return QTY

def qty(update: Update, context: CallbackContext) -> int:
    context.user_data['qty'] = update.message.text
    # Add the data to the configuration file
    user_name = context.user_data.pop('name')
    data[user_name] = context.user_data
    with open('config.json', 'w') as f:
        json.dump(data, f)
    update.message.reply_text('Data added successfully')
    return ConversationHandler.END
def modifyQty(update: Update, context: CallbackContext) -> None:
    # Ask the user which user they want to modify
    update.message.reply_text('Which user do you want to modify?')

def list(update: Update, context: CallbackContext) -> None:
    # Show all the user data
    update.message.reply_text(str(data))

def main() -> None:
    updater = Updater("token", use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("modifyQty", modifyQty))
    dispatcher.add_handler(CommandHandler("list", list))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()