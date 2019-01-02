from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import logging
import os
import sqlite3
from pathlib import Path
from xlsxwriter.workbook import Workbook

time_date = ""
welcome_message = "سلام. برای اینکه بفهمیم این اتفاق در چه روزی افتاده لازمه که بهمون تاریخ رو بگی. حتی اگه امروز این اتفاق افتاده باشه تاریخ امروز رو وارد کن. تاریخ رو هم به فرمت مثال زیر برامون بفرست: 1397/08/29"
location_message = "حالا برای اینکه بدونیم چه اتفاقی افتاده لوکیشنت رو برامون به کمک دکمه زیر بفرست"
type_message=" در ضمن نوع مشکلت رو هم مشخص کن"
get_loc_message = "با سپاس از شما، اطلاعات شما دریافت شد"

def start(bot, update):
    bot.send_message(text=welcome_message, chat_id=update.message.chat_id)


def times(bot, update):
    type_keyboard = [[InlineKeyboardButton("تصادف", callback_data='تصادف'),
                     InlineKeyboardButton("مشکل جاده", callback_data='مشکل جاده'),
                      InlineKeyboardButton("ترافیک", callback_data='ترفیک'),
                      InlineKeyboardButton("پلیس", callback_data='پلیس')
                      ]]
    type_reply_markup = InlineKeyboardMarkup(type_keyboard)
    update.message.reply_text(type_message, reply_markup=type_reply_markup)


def button(bot, update):
    query = update.callback_query
    bot.edit_message_text(text="%s گزینهٔ انتخابی شما"  % query.data,
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
    serv = 0
    geo = 0
    try:
        username = sender_data['username']
    except:
        username = sender_data['id']
    if sender_data['first_name'] or sender_data['last_name'] is None:
        user_name = 'undefiend'
    else:
        user_name = sender_data['first_name'] + ' ' + sender_data['last_name']
    store_db(user_id, user_name, username, latitude, longitude, geo,admin_id, date, serv)
    bot.send_message(chat_id=update.message.chat_id, text=get_loc_message)

def make_table_db():
    connection = sqlite3.connect('database.sqlite3')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE datas
                    (id INTEGER, name TEXT DEFAULT 'undefined', username TEXT DEFAULT 'undefiend', lat REAL, long REAL, geo REAL DEFAULT 0, is_admin INTEGER DEFAULT 0, date TEXT, serv TEXT DEFAULT 0)
                    ''')
    connection.commit()
    connection.close()

def store_db(user_id, user_name, username, latitude, longitude, geo, admin_id, date, serv):
    connection = sqlite3.connect('database.sqlite3')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO datas VALUES (?,?,?,?,?,?,?,?,?)",(user_id, user_name, username, latitude, longitude, geo, admin_id, date, serv))
    connection.commit()
    connection.close()



def get_db(bot, update):
    workbook = Workbook('database.xlsx')
    worksheet = workbook.add_worksheet()
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    c.execute("select * from datas")
    mysel = c.execute("select * from datas")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, value)
    workbook.close()
    bot.send_document(chat_id=update.message.chat_id, document=open('database.xlsx', 'rb'))
    bot.send_document(chat_id=update.message.chat_id, document=open('database.sqlite3', 'rb'))


def main():
    if Path("./database.sqlite3").is_file():
        pass
    else:
        make_table_db()

    token = os.getenv('BOT_TOKEN')
    updater = Updater(token=token)

    logging.basicConfig(format='%(asctime)s - %(name)s %(levelname)s - %(message)s', level=logging.INFO)
    print (time_date)
    start_handler = CommandHandler('start', start)
    times_handler = MessageHandler(Filters.text, times)
    getdb_handler = CommandHandler('get_db', get_db)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(times_handler)
    updater.dispatcher.add_handler(getdb_handler)

    print(time_date)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    get_loc_handler = MessageHandler(Filters.location, get_loc)
    updater.dispatcher.add_handler(get_loc_handler)
    updater.start_polling()


if __name__ == '__main__':
    main()

