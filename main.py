from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import sqlite3, csv, os, logging
from pathlib import Path
from xlsxwriter.workbook import Workbook
import uuid
time_date = ""
welcome_message = "سلام. برای اینکه بفهمیم این اتفاق در چه روزی افتاده لازمه که بهمون تاریخ رو بگی. حتی اگه امروز این اتفاق افتاده باشه تاریخ امروز رو وارد کن. تاریخ رو هم به فرمت مثال زیر برامون بفرست: 1397/08/29"
location_message = "حالا برای اینکه بدونیم چه اتفاقی افتاده لوکیشنت رو برامون به کمک دکمه زیر بفرست"
type_message=" در ضمن نوع مشکلت رو هم مشخص کن"
get_loc_message = "با سپاس از شما، اطلاعات شما دریافت شد"
error_message= "در حال حاضر صف ارسال داده پر است. لطفا ۲۰ ثانیه دیگر مجدداً ربات را بسته و دوباره اجرا کنید."
db_info = [0,0,0,0,0,0,0]
identity = 0

def gpid():
    return str(uuid.uuid4())

def start(bot, update):
    bot.send_message(text=welcome_message, chat_id=update.message.chat_id)
    db_info[0]=update.message.from_user['id']
    global identity
    identity = str(uuid.uuid4())
    db_info[6] = identity
    print (db_info)
    print ("identitiy is ", identity)

def times(bot, update):
    type_keyboard = [[InlineKeyboardButton("تصادف", callback_data='تصادف'),
                     InlineKeyboardButton("مشکل جاده", callback_data='مشکل جاده'),
                      InlineKeyboardButton("ترافیک", callback_data='ترافیک'),
                      InlineKeyboardButton("پلیس", callback_data='پلیس')
                      ]]
    type_reply_markup = InlineKeyboardMarkup(type_keyboard)
    update.message.reply_text(type_message, reply_markup=type_reply_markup)
    db_info[5]=update.message.text
    print (db_info)
def button(bot, update):
    query = update.callback_query
    db_info[4]=query.data
    bot.edit_message_text(text="%s گزینهٔ انتخابی شما"  % query.data,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id)  
    print ("identitiy is ", identity)
    query = update.callback_query
    bot.send_message(text="حالا موقعیت مکانی‌ت رو هم برام بفرست",
        chat_id=query.message.chat_id)
def get_loc(bot, update):
    global db_info
    sender_data = update.message.from_user
    user_id = sender_data['id']
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    db_info[2]=latitude
    db_info[3]=longitude
    print (db_info)
    try:
        username = sender_data['username']
    except:
        username = sender_data['id']
    db_info[1]=username
    # if sender_data['first_name'] or sender_data['last_name'] is None:
    #     db_info.insert(1,"Unknown name")
    # else:
    #     user_name = sender_data['first_name'] + ' ' + sender_data['last_name']
    #     db_info.insert(1,user_name)
    print ("identitiy is ", identity)
    print(db_info)
#    [28357375, 'db_info.append(user_name)', 'ترفیک', 34.854012, 52.607471, 'Amirhossein_Goodarzi', 'Unknown name'
    if db_info[6] == identity:
        store_db(db_info[0], db_info[1], db_info[2], db_info[3], db_info[4], db_info[5],db_info[6])
        print ("identitiy is ", identity)
    else: 
        bot.send_message(chat_id=update.message.chat_id, text=error_message)
    bot.send_message(chat_id=update.message.chat_id, text=get_loc_message)
#    [28357375, 28357375, '1397/12/07', 'مشکل جاده', 34.854012, 52.607471]

def make_table_db():
    connection = sqlite3.connect('database.sqlite3')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE datas
                    (id INTEGER, username TEXT DEFAULT 'undefiend', lat REAL, long REAL, typo TEXT, date TEXT, identifier TEXT)
                    ''')
    connection.commit()
    connection.close()

def store_db(user_id, username, latitude, longitude,typo, date, identifier):
    connection = sqlite3.connect('database.sqlite3')
    cursor = connection.cursor()
    with connection:
        cursor.execute("INSERT INTO datas VALUES (?,?,?,?,?,?,?)",(user_id, username, latitude, longitude, typo, date, identifier))
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
    inpsql3 = sqlite3.connect('database.sqlite3')
    sql3_cursor = inpsql3.cursor()
    sql3_cursor.execute('SELECT * FROM datas')
    with open('database.csv','w') as out_csv_file:
        csv_out = csv.writer(out_csv_file)
    # write header                        
        csv_out.writerow([d[0] for d in sql3_cursor.description])
    # write data                          
        for result in sql3_cursor:
            csv_out.writerow(result)
    inpsql3.close() 
    bot.send_document(chat_id=update.message.chat_id, document=open('database.xlsx', 'rb'))
    bot.send_document(chat_id=update.message.chat_id, document=open('database.sqlite3', 'rb'))
    bot.send_document(chat_id=update.message.chat_id, document=open('database.csv', 'rb'))

def rm(bot, update):
    os.remove("database.csv")
    os.remove("database.sqlite3")
    os.remove("database.xlsx")
    bot.send_document(chat_id=update.message.chat_id, text="All deleted.")

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
    rm_handler = CommandHandler('rm', rm)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(times_handler)
    updater.dispatcher.add_handler(getdb_handler)
    updater.dispatcher.add_handler(rm_handler)

    print(time_date)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    get_loc_handler = MessageHandler(Filters.location, get_loc)
    updater.dispatcher.add_handler(get_loc_handler)
    updater.start_polling()


if __name__ == '__main__':
    main()

