from telegram import Update
from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, ConversationHandler, \
    MessageHandler, Filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import qrcode
import os
import pyshorteners

INPUT_TEXT = 0
INPUT_URL = 1


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        text='Hello, welcome, what do you want to do?',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Generate QR', callback_data='qr')],
            [InlineKeyboardButton(text='Shorten URL', callback_data='short_url')]
        ])
    )


def about(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        text='Link to developer\'s GitHub profile.',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='GitHub Dev', url='https://github.com/ZahiriNatZuke')]
        ])
    )


def qr_callback_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Send me the text to generate the QR code.')
    return INPUT_TEXT


def short_url_callback_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Send me a link to shorten it.')
    return INPUT_URL


def generate_qr(text: str) -> str:
    img = qrcode.make(text)
    filename = text + '_pyBot.png'
    img.save(filename)
    return filename


def send_qr(filename: str, chat):
    chat.send_action(action=ChatAction.UPLOAD_PHOTO, timeout=None)
    chat.send_photo(photo=open(filename, 'rb'))
    os.unlink(filename)


def input_text_handler(update: Update, context: CallbackContext):
    text = update.message.text
    filename = generate_qr(text)
    chat = update.message.chat
    send_qr(filename, chat)
    return ConversationHandler.END


def input_url_handler(update: Update, context: CallbackContext):
    url = update.message.text

    s = pyshorteners.Shortener()
    short_url = s.chilpit.short(url)

    chat = update.message.chat
    chat.send_action(action=ChatAction.TYPING, timeout=None)
    chat.send_message(text=short_url)
    return ConversationHandler.END


if __name__ == '__main__':
    updater: Updater = Updater(token=os.environ['TELEGRAM_BOT_TOKEN'], use_context=True)
    dp = updater.dispatcher

    # add handler
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('about', about))

    dp.add_handler(ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern='qr', callback=qr_callback_handler),
            CallbackQueryHandler(pattern='short_url', callback=short_url_callback_handler)
        ],
        states={
            INPUT_TEXT: [MessageHandler(Filters.text, input_text_handler)],
            INPUT_URL: [MessageHandler(Filters.text, input_url_handler)]
        },
        fallbacks=[]
    ))

    updater.start_polling()
    updater.idle()
