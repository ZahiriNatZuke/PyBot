from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

INPUT_TEXT = 0


def start(update: Update, context: CallbackContext) -> None:
    btn1 = InlineKeyboardButton(text='GitHub Dev', url='https://github.com/ZahiriNatZuke')
    btn2 = InlineKeyboardButton(text='Twitter Dev', url='https://twitter.com/ZahiriNatZuke')
    btn3 = InlineKeyboardButton(text='LinkedIn Dev', url='https://www.linkedin.com/in/yohan-gonz%C3%A1lez-almaguer/')
    update.message.reply_text(
        text='Social links.',
        reply_markup=InlineKeyboardMarkup([
            [btn1],
            [btn2],
            [btn3]
        ])
    )


if __name__ == '__main__':
    updater: Updater = Updater(token='1784910419:AAEUtuB6YEH8jRsJkBYtwD6uUtZlJXl020w', use_context=True)
    dp = updater.dispatcher

    # add handler
    dp.add_handler(CommandHandler('start', start))

    updater.start_polling()
    updater.idle()
