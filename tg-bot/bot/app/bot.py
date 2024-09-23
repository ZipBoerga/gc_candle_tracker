import logging
import os
from functools import wraps
from http import HTTPStatus
from typing import Optional

import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application, CommandHandler, CallbackQueryHandler, ConversationHandler

from secrets import TELEGRAM_BOT_TOKEN, ADMIN_ID

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BACKEND_HOST = os.environ['BACKEND_HOST']
session: Optional[aiohttp.ClientSession] = None

REQUEST_UPDATE, SUBSCRIBE, UNSUBSCRIBE = range(3)

SUBSCRIPTION_CONTEXT_KEY = 'is_subscribed'


async def create_session(application: Application):
    global session
    session = aiohttp.ClientSession()


async def close_session(application: Application):
    global session
    if session:
        await session.close()


def restricted(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != ADMIN_ID:
            logger.info("Unauthorized access denied for {}.".format(user_id))
            return
        return await func(update, context, *args, **kwargs)

    return wrapped


def subscription_check(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if SUBSCRIPTION_CONTEXT_KEY in context.user_data:
            logger.info('We have subscription')
        else:
            logger.info('We have no sub info, need to fetch it!')
        return await func(update, context, *args, **kwargs)
    return wrapped


@restricted
@subscription_check
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton('Request update', callback_data=REQUEST_UPDATE),
            InlineKeyboardButton('Subscribe to timed updates', callback_data=SUBSCRIBE)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to GC Price Updates bot! Please select what you want to do.',
                                    reply_markup=reply_markup)
    # user_id = update.effective_user.id
    # chat_id = update.effective_chat.id
    #
    # request_body = {
    #     'user_id': user_id,
    #     'chat_id': chat_id
    # }
    # async with session.post(f'http://{BACKEND_HOST}/api/user', json=request_body) as response:
    #     logger.info(response.status)
    #     if response.status == 201:
    #         success_json = await response.json()
    #         logger.info(success_json)
    #         await update.message.reply_text(f'Hearing from the user {user_id}! We have written your data to db.')
    #     elif response.status == 409:
    #         error_json = await response.json()
    #         logger.info(error_json)
    #         await update.message.reply_text('You have been already enrolled!')
    #     else:
    #         error_message = await response.text()
    #         logger.info(error_message)


@restricted
@subscription_check
async def get_price_changes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton('Request update', callback_data=REQUEST_UPDATE),
            InlineKeyboardButton('Subscribe to timed updates', callback_data=SUBSCRIBE)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=query.message.message_id
    )
    await context.bot.send_message(text='Here are some changes', chat_id=update.effective_chat.id)
    # await query.edit_message_text(
    #     text='Want something now? (updates call)', reply_markup=reply_markup
    # )
    await context.bot.send_message(text='Want something now? (updates call)', reply_markup=reply_markup,
                                   chat_id=update.effective_chat.id)


@restricted
@subscription_check
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton('Request update', callback_data=REQUEST_UPDATE),
            InlineKeyboardButton('Unsubscribe! (You are acc not subscribed, it\'s a test', callback_data=SUBSCRIBE)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=query.message.message_id
    )
    await context.bot.send_message(text='Subscribed? I doubt it.', chat_id=update.effective_chat.id)
    # await query.edit_message_text(
    #     text='Want something now? (sub call)', reply_markup=reply_markup
    # )
    await context.bot.send_message(text='Want something now? (sub call)', reply_markup=reply_markup,
                                   chat_id=update.effective_chat.id)


def main() -> None:
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(create_session)
        .post_shutdown(close_session)
        .build()
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(get_price_changes, pattern=f'^{str(REQUEST_UPDATE)}$'))
    application.add_handler(CallbackQueryHandler(subscribe, pattern=f'^{str(SUBSCRIBE)}$'))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
