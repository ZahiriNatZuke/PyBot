from pyshorteners.exceptions import ShorteningErrorException, BadAPIResponseException
from telegram import Update, ParseMode
from telegram import ChatAction
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters
)
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import qrcode
import os
import pyshorteners
import random
import logging
import html
import json
import traceback
import time

INPUT_TEXT = 0
INPUT_URL = 1


# /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        text='Hello, welcome, what do you want to do?',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Generate QR', callback_data='qr')],
            [InlineKeyboardButton(text='Shorten URL', callback_data='short_url')],
            [InlineKeyboardButton(text='Throw a Coin', callback_data='throw_coin')]
        ])
    )


# /about
def about(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        text='Link to developer\'s GitHub profile.',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='GitHub Dev', url='https://github.com/ZahiriNatZuke')]
        ])
    )


# /throw_coin
def throw_coin(update: Update, context: CallbackContext):
    msg = '⚫️ Heads' if random.randint(1, 2) == 1 else '⚪️ Tails'
    update.message.reply_text(text=msg)


# /qr
def qr_callback_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer(text='QR')
    query.edit_message_text(text='Send me the text to generate the QR code.')
    return INPUT_TEXT


# /short_url
def short_url_callback_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer('Short URL')
    query.edit_message_text(text='Send me a link to shorten it.')
    return INPUT_URL


# /throw_coin callback
def throw_coin_callback_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer('Throw Coin')
    query.edit_message_text(text='Good Luck.')

    msg = '⚫️ Heads' if random.randint(1, 2) == 1 else '⚪️ Tails'
    update.callback_query.message.reply_text(text=msg)
    return ConversationHandler.END


def generate_qr(text: str, filename: str) -> str:
    img = qrcode.make(text)
    filename = filename + ' [pyBot].png'
    img.save(filename)
    return filename


def send_qr(filename: str, chat):
    chat.send_action(action=ChatAction.UPLOAD_PHOTO, timeout=300)
    chat.send_photo(photo=open(filename, 'rb'))
    os.unlink(filename)


def input_text_handler(update: Update, context: CallbackContext):
    text = update.message.text
    ts = time.time()
    filename = generate_qr(text=text, filename=str(ts))
    chat = update.message.chat
    send_qr(filename, chat)
    return ConversationHandler.END


def input_url_handler(update: Update, context: CallbackContext):
    url = update.message.text
    chat = update.message.chat

    s = pyshorteners.Shortener(api_key=os.environ['CUTTLY_API_KEY'])
    try:
        short_url = s.cuttly.short(url)
        chat.send_action(action=ChatAction.TYPING, timeout=300)
        chat.send_message(text=short_url)
    except ShorteningErrorException:
        chat.send_message(
            text='<i>There was an error on trying to short the url:</i> <b>Invalid URL format</b>',
            parse_mode=ParseMode.HTML
        )
    except BadAPIResponseException:
        chat.send_message(
            text='<i>There was an error on trying to short the url:</i> <b>Invalid URL format</b>',
            parse_mode=ParseMode.HTML
        )

    return ConversationHandler.END


# [Logger]
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=update.callback_query.message.chat.id, text=message, parse_mode=ParseMode.HTML)


if __name__ == '__main__':
    updater: Updater = Updater(token=os.environ['TELEGRAM_BOT_TOKEN'], use_context=True)
    dp = updater.dispatcher

    # add handler
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('about', about))
    dp.add_handler(CommandHandler('throw_coin', throw_coin))

    dp.add_handler(ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern='qr', callback=qr_callback_handler),
            CallbackQueryHandler(pattern='short_url', callback=short_url_callback_handler),
            CallbackQueryHandler(pattern='throw_coin', callback=throw_coin_callback_handler)
        ],
        states={
            INPUT_TEXT: [MessageHandler(Filters.text, input_text_handler)],
            INPUT_URL: [MessageHandler(Filters.text, input_url_handler)],
        },
        fallbacks=[]
    ))

    # add error handler as logger
    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()
