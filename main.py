from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import logging
import os
import sqlite3
from pathlib import Path
welcome_message = "سلام. برای اینکه بدونیم چه اتفاقی افتاده لازمه که به ما بگی دقیقاً کی این اتفاق افتاد اگر همین الان بود روی دکمه همین الان و اگه یه روز دیگه بود دکمه مرتبطش رو انتخا کن"
location_message = "حالا برای اینکه بدونیم چه اتفاقی افتاده لوکیشنت رو برامون به کمک دکمه زیر بفرست"
type_message=" در ضمن نوع مشکلت رو هم مشخص کن"
get_loc_message = "با سپاس از شما، اطلاعات شما دریافت شد"

def start(bot, update):
    #print(update)
    keyboard = [[InlineKeyboardButton("همین الان", callback_data='همین الان', request_location=True),
                InlineKeyboardButton("یه روز دیگه", callback_data='یه روز دیگه')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(welcome_message, reply_markup=reply_markup)
    type_keyboard = [[InlineKeyboardButton("تصادف", callback_data='تصادف'),
                     InlineKeyboardButton("مشکل جاده", callback_data='مشکل جاده')]]
    type_reply_markup = InlineKeyboardMarkup(type_keyboard)
    update.message.reply_text(type_message, reply_markup=type_reply_markup)


def button(bot, update):
    #print(update)
    query = update.callback_query
    bot.edit_message_text(text="%s گزینهٔ انتخابی شما" % query.data,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id)
    query = update.callback_query
    bot.send_message(text="حالا موقعیت مکانی‌ت رو هم برام بفرست",
        chat_id=query.message.chat_id)





def get_loc(bot, update):


    sender_data = update.message.from_user
    user_id = sender_data['id']
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    admin_id = 0
    date = update.message.date
    try:
        username = sender_data['username']
    except:
        username = sender_data['id']
    if sender_data['first_name'] or sender_data['last_name'] is None:
        user_name = 'undefiend'
    else:
        user_name = sender_data['first_name'] + ' ' + sender_data['last_name']
    store_db(user_id, user_name, username, latitude, longitude, admin_id, date, type)
    bot.send_message(chat_id=update.message.chat_id, text=get_loc_message)

def make_table_db():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE datas
                    (id INTEGER, name TEXT DEFAULT 'undefined', username TEXT DEFAULT 'undefiend', lat REAL, long REAL, is_admin INTEGER DEFAULT 0, date TEXT, type TEXT)
                    ''')
    connection.commit()
    connection.close()

def store_db(user_id, user_name, username, latitude, longitude, admin_id, date, type):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO datas VALUES (?,?,?,?,?,?,?,?)",(user_id, user_name, username, latitude, longitude, admin_id, date, type))
    connection.commit()
    connection.close()

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
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    get_loc_handler = MessageHandler(Filters.location, get_loc)
    updater.dispatcher.add_handler(get_loc_handler)
    updater.start_polling()


if __name__ == '__main__':
    main()

