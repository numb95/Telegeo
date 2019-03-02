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
db_info = []
def start(bot, update):
    bot.send_message(text=welcome_message, chat_id=update.message.chat_id)
    db_info.append( update.message.from_user['id'])


def times(bot, update):
    type_keyboard = [[InlineKeyboardButton("تصادف", callback_data='تصادف'),
                     InlineKeyboardButton("مشکل جاده", callback_data='مشکل جاده'),
                      InlineKeyboardButton("ترافیک", callback_data='ترافیک'),
                      InlineKeyboardButton("پلیس", callback_data='پلیس')
                      ]]
    type_reply_markup = InlineKeyboardMarkup(type_keyboard)
    update.message.reply_text(type_message, reply_markup=type_reply_markup)
    db_info.append(update.message.text)
def button(bot, update):
    query = update.callback_query
    db_info.append(query.data)
    bot.edit_message_text(text="%s گزینهٔ انتخابی شما"  % query.data,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id)  
    query = update.callback_query
    bot.send_message(text="حالا موقعیت مکانی‌ت رو هم برام بفرست",
        chat_id=query.message.chat_id)
def get_loc(bot, update):
    global db_info
    sender_data = update.message.from_user
    user_id = sender_data['id']
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    db_info.append(latitude)
    db_info.append(longitude)
    try:
        username = sender_data['username']
    except:
        username = sender_data['id']
    db_info.append(username)
    if sender_data['first_name'] or sender_data['last_name'] is None:
        db_info.append("Unknown name")
    else:
        user_name = sender_data['first_name'] + ' ' + sender_data['last_name']
        db_info.append(user_name)
    print(db_info)
#    [28357375, 'db_info.append(user_name)', 'ترفیک', 34.854012, 52.607471, 'Amirhossein_Goodarzi', 'Unknown name'
    store_db(db_info[0], db_info[6], db_info[5], db_info[3], db_info[4], db_info[2],db_info[1])
    bot.send_message(chat_id=update.message.chat_id, text=get_loc_message)
    db_info = []
#    [28357375, 28357375, '1397/12/07', 'مشکل جاده', 34.854012, 52.607471]

def make_table_db():
    connection = sqlite3.connect('database.sqlite3')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE datas
                    (id INTEGER, name TEXT DEFAULT 'undefined', username TEXT DEFAULT 'undefiend', lat REAL, long REAL, typo TEXT, date TEXT)
                    ''')
    connection.commit()
    connection.close()

def store_db(user_id, user_name, username, latitude, longitude,typo, date):
    connection = sqlite3.connect('database.sqlite3')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO datas VALUES (?,?,?,?,?,?,?)",(user_id, user_name, username, latitude, longitude,typo, date))
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

