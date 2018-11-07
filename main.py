from telegram.ext import Updater,CommandHandler, MessageHandler, Filters 
import logging
import os

welcome_message = "سلام به بات اینجا چه خبره خوش اومدی. قبل از هر کاری لوکیشنت رو برام بفرست تا ببینم اطرافت چی داری"

def start(bot, update):
    '''
    
    '''
    bot.send_message(chat_id=update.message.chat_id, text=welcome_message)

def get_loc(bot, update):

    map_url = 'https://www.google.com/maps/@{0},{1},15z'
    bot.send_message(chat_id=update.message.chat_id, text=map_url.format(update.message.location.latitude, update.message.location.longitude))


def main():

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
