import logging
import os
from functools import wraps
from typing import Optional

import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application, CommandHandler, CallbackQueryHandler, ConversationHandler

import app_text as text_consts
from secrets import TELEGRAM_BOT_TOKEN, ADMIN_ID

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BACKEND_HOST = os.environ['BACKEND_HOST']
session: Optional[aiohttp.ClientSession] = None

GET_UPDATES, SUBSCRIBE, UNSUBSCRIBE = range(3)

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
        user_id = update.effective_user.id
        if SUBSCRIPTION_CONTEXT_KEY in context.user_data:
            logger.info(
                f'The user {user_id} is '
                f'{"subscribed" if context.user_data.get(SUBSCRIPTION_CONTEXT_KEY) else "not subscribed"}')
        else:
            logger.info('We have no sub info, fetching it')
            params = {
                'user_id': user_id
            }
            async with session.get(f'http://{BACKEND_HOST}/api/user', params=params) as response:
                logger.info(response.status)

                # TODO change logic of DB subs
                if response.status == 200:
                    context.user_data[SUBSCRIPTION_CONTEXT_KEY] = True
                elif response.status == 204:
                    context.user_data[SUBSCRIPTION_CONTEXT_KEY] = False
                else:
                    error_message = await response.text()
                    logger.warning(
                        f'No subscription status was retrieved for user due to the error: {error_message}.'
                        f' Will be retried on the next user request.')

        return await func(update, context, *args, **kwargs)

    return wrapped


def _get_subscription_action_button(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardButton:
    is_user_subscribed = context.user_data.get(SUBSCRIPTION_CONTEXT_KEY)
    if is_user_subscribed is None:
        raise Exception('Subscription status must be already defined, but None is contained in context')
    logger.debug(f'The subscription status for this one: {is_user_subscribed}')
    return (
        InlineKeyboardButton(text_consts.UNSUBSCRIBE_BUTTON, callback_data=UNSUBSCRIBE)
        if is_user_subscribed
        else InlineKeyboardButton(text_consts.SUBSCRIBE_BUTTON, callback_data=SUBSCRIBE)
    )


def _get_keyboard(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    sub_button = _get_subscription_action_button(context)
    keyboard = [
        [
            InlineKeyboardButton('Request update', callback_data=GET_UPDATES),
            sub_button
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


@restricted
@subscription_check
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscription_action_button = _get_subscription_action_button(context)
    reply_markup = _get_keyboard(context)
    await update.message.reply_text('Welcome to GC Price Updates bot! Please select what you want to do.',
                                    reply_markup=reply_markup)


@restricted
@subscription_check
async def get_price_changes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    reply_markup = _get_keyboard(context)
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

    request_body = {
        'user_id': update.effective_user.id,
        'chat_id': update.effective_chat.id
    }
    async with session.post(f'http://{BACKEND_HOST}/api/user', json=request_body) as response:
        logger.info(response.status)
        if response.status == 201:
            success_json = await response.json()
            logger.info(success_json)
            context.user_data[SUBSCRIPTION_CONTEXT_KEY] = True
            # TODO replace it with the reply markup only message, otherwise it's doubled
            await context.bot.send_message(text='You are subscribed now! Daily you will be receiving price updates!',
                                           chat_id=update.effective_chat.id)
        elif response.status == 409:
            error_json = await response.json()
            logger.info(error_json)
            await context.bot.send_message(text='You are already subscribed!', chat_id=update.effective_chat.id)

        else:
            error_message = await response.text()
            logger.info(error_message)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=query.message.message_id
    )
    # await query.edit_message_text(
    #     text='Want something now? (sub call)', reply_markup=reply_markup
    # )
    reply_markup = _get_keyboard(context)
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
    application.add_handler(CallbackQueryHandler(get_price_changes, pattern=f'^{str(GET_UPDATES)}$'))
    application.add_handler(CallbackQueryHandler(subscribe, pattern=f'^{str(SUBSCRIBE)}$'))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
