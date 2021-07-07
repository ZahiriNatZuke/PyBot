from telegram import Update
from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, ConversationHandler, \
    MessageHandler, Filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import qrcode
import os

INPUT_TEXT = 0


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        text='Hello, welcome, what do you want to do?\n\n Use /qr to generate a QR code.',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Generate QR', callback_data='qr')],
            [InlineKeyboardButton(text='GitHub Dev', url='https://github.com/ZahiriNatZuke')]
        ])
    )


def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hello {update.effective_user.full_name}')


def qr_command_handler(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Send me the text to generate the QR code.')
    return INPUT_TEXT


def qr_callback_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Send me the text to generate the QR code.')
    return INPUT_TEXT


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


if __name__ == '__main__':
    updater: Updater = Updater(token='1784910419:AAEUtuB6YEH8jRsJkBYtwD6uUtZlJXl020w', use_context=True)
    dp = updater.dispatcher

    # add handler
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('hello', hello))

    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('qr', qr_command_handler),
            CallbackQueryHandler(pattern='qr', callback=qr_callback_handler)
        ],
        states={
            INPUT_TEXT: [MessageHandler(Filters.text, input_text_handler)]
        },
        fallbacks=[]
    ))

    updater.start_polling()
    updater.idle()
