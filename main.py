import os
import logging
import time
import requests
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler
from telegram.ext.filters import Filters
from telegram.update import Update
from telegram import ParseMode


TELEGRAM_BOT_TOKEN = '5558118981:AAHQ8YmW4Ip4ifpiFFipGH4E4brC_tKNF2U'
RAPID_API_URL = 'https://tiktok-info.p.rapidapi.com/dl/'
RAPID_API_KEY = 'e0ffcd909emsh1d42846ceac4f36p1278e0jsn4a987af97a26'
RAPID_API_HOST = 'tiktok-info.p.rapidapi.com'
FILE_PATH = 'videos/video.mp4'
SOCIAL_NAME = 'tiktok'
OWNER = '@abdibrokhim'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    update.message \
        .reply_text('Welcome to TikTok Watermark remover bot\n'
                    'Try /search <tiktok link>')


def help(update: Update, context: CallbackContext):
    update.message \
        .reply_text('Try /search <tiktok link>\n'
                    f'If you have any queries contact -> {OWNER}')


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def search(update: Update, context: CallbackContext):
    args = context.args
    print("args:", args)
    logging.info('checking args length ... ')
    if len(args) == 0:
        update.message \
            .reply_text('Try /search <tiktok link>')
    else:
        search_text = ' '.join(args)
        if SOCIAL_NAME in search_text:
            print('search text:', search_text)
            url = RAPID_API_URL
            querystring = {"link": search_text}
            headers = {
                "X-RapidAPI-Key": RAPID_API_KEY,
                "X-RapidAPI-Host": RAPID_API_HOST
            }
            response = requests.request("GET", url, headers=headers, params=querystring)
            time.sleep(1)
            result = response.json()
            print('result:', result)
            link = str(result['videoLinks']['download'])
            print('link:', link)

            if len(link):
                send_link(update, context, link)
                if write_to_file(link):
                    if upload_video(update, context):
                        logging.info('success ... ')
                    else:
                        error_uploading(update, context)
                    remove_file()
                    time.sleep(1)
                else:
                    update.message \
                        .reply_text('Something went wrong')
                    remove_file()
                    time.sleep(1)
            else:
                update.message \
                    .reply_text('Media not found')
        else:
            update.message \
                .reply_text('Try /search <tiktok link>')


def send_link(update, context, link):
    update.message \
        .reply_text(text=f"<a href='{link}'>Click</a> to download",
                    parse_mode=ParseMode.HTML)
    update.message \
        .reply_text(text="Media is uploading ... ")


def error_uploading(update, context):
    update.message \
        .reply_text(text="Low internet connection")


def remove_file():
    if os.path.isfile(FILE_PATH):
        os.remove(FILE_PATH)


def upload_video(update, context):
    try:
        update.message. \
            reply_video(video=open(FILE_PATH, 'rb'), supports_streaming=True)
        time.sleep(1)
        return True
    except:
        return False


def write_to_file(url):
    try:
        response = requests.get(url, allow_redirects=True)
        open(FILE_PATH, 'wb').write(response.content)
        time.sleep(1)
        return True
    except:
        return False


def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('search', search))
    dispatcher.add_handler(MessageHandler(Filters.all, start))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
