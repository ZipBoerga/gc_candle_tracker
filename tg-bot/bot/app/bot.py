import logging
import os
from functools import wraps
from http import HTTPStatus
from typing import Optional

import aiohttp
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler

from secrets import TELEGRAM_BOT_TOKEN, ADMIN_ID


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


BACKEND_HOST = os.environ['BACKEND_HOST']
session: Optional[aiohttp.ClientSession] = None


async def create_session(application: Application):
    global session
    session = aiohttp.ClientSession()


async def close_session(application: Application):
    global session
    if session:
        await session.close()


def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != ADMIN_ID:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return await func(update, context, *args, **kwargs)

    return wrapped


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    request_body = {
        'user_id': user_id,
        'chat_id': chat_id
    }
    async with session.post(f'http://{BACKEND_HOST}/api/user', json=request_body) as response:
        logger.info(response.status)
        if response.status == 201:
            success_json = await response.json()
            logger.info(success_json)
            await update.message.reply_text(f'Hearing from the user {user_id}! We have written your data to db.')
        elif response.status == 409:
            error_json = await response.json()
            logger.info(error_json)
            await update.message.reply_text('You have been already enrolled!')
        else:
            error_message = await response.text()
            logger.info(error_message)


@restricted
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Here we\'ll have our great candles tracking bot')


def main() -> None:
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(create_session)
        .post_shutdown(close_session)
        .build()
    )
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    print('The bot is initialized and running!')

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
