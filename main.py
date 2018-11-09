from telegram.ext import Updater,CommandHandler, MessageHandler, Filters 
import logging
import os
import sqlite3
from pathlib import Path

welcome_message = "سلام به بات اینجا چه خبره خوش اومدی. قبل از هر کاری لوکیشنت رو برام بفرست تا ببینم اطرافت چی داری"
get_loc_message = "با سپاس از شما، اطلاعات شما دریافت شد"

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=welcome_message)

def get_loc(bot, update):
    sender_data = update.message.from_user
    user_id = sender_data['id']
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    admin_id = 0 
    try:
        username = sender_data['username']
    except:
        username = sender_data['id']
    if sender_data['first_name'] or sender_data['last_name'] is None:
        user_name = 'undefiend'
    else:
        user_name = sender_data['first_name'] + ' ' + sender_data['last_name']
    store_db(user_id, user_name, username, latitude, longitude, admin_id) 
    bot.send_message(chat_id=update.message.chat_id, text=get_loc_message)
#   for future release
#    bot.send_message(chat_id=update.message.chat_id, text=map_url.format(update.message.location.latitude, update.message.location.longitude))

def make_table_db():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE datas
                    (id INTEGER, name TEXT DEFAULT 'undefined', username TEXT DEFAULT 'undefiend', lat REAL, long REAL, is_admin INTEGER DEFAULT 0)
                    ''')
    connection.commit()
    connection.close()

def store_db(user_id, user_name, username, latitude, longitude, admin_id):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO datas VALUES (?,?,?,?,?,?)",(user_id, user_name, username, latitude, longitude, admin_id))
    connection.commit()
    connection.close

def main():
    if Path("./database.db").is_file():
        pass
    else:
        make_table_db()

    token = os.getenv('BOT_TOKEN')
    updater = Updater(token=token)

    logging.basicConfig(format='%(asctime)s - %(name)s %(levelname)s - %(message)s', level=logging.INFO)

    start_handler = CommandHandler('start', start)
    updater.dispatcher.add_handler(start_handler)

    get_loc_handler = MessageHandler(Filters.location, get_loc)
    updater.dispatcher.add_handler(get_loc_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
