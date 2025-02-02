import asyncio
import datetime
import json
import os
import sys

import telegram
from telegram import Bot, WebAppInfo, Update, \
    InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegram.ext import CommandHandler, Application, MessageHandler, filters, CallbackQueryHandler

from bot_manager import BotManager, Reply
from quotes_loader import QuotesLoader

# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=53509, stdoutToServer=True, stderrToServer=True)

QUOTES_DIR="quotes"

if "insert_categories" in sys.argv:

    def remove_quotes(category):
        category['quotes'] = {}
        for subcategory in category['subcategories'].values():
            remove_quotes(subcategory)

    print("Inserting categories")
    loader = QuotesLoader(QUOTES_DIR)
    remove_quotes(loader.categories)
    categories = json.dumps(loader.categories)


    with open('miniapp-frontend/index.html') as f: index_html = f.read()

    index_html_split = index_html.split("/* insert categories */")

    patched = index_html_split[0] + "/* insert categories */\n window.categories = " + categories + ";\n/* insert categories */\n" + index_html_split[2]

    try:
        os.unlink("miniapp-frontend/index_patched.html")
    except:
        pass

    with open("miniapp-frontend/index_patched.html", "w") as text_file:
        text_file.write(patched)

    os.rename("miniapp-frontend/index_patched.html", "miniapp-frontend/index.html")

    print("All done")

    exit(0)

TOKEN = os.environ.get('TOKEN')
ENV = os.environ.get('ENV')
FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL')

bot = Bot(token=TOKEN)

bot_manager = BotManager("wisdom-quotes.db", QUOTES_DIR, ENV, FRONTEND_BASE_URL)

async def process_ticks():
    global bot_manager
    replies = bot_manager.process_tick()
    for reply in replies:
        try:
            await send_reply_with_bot(reply)
        except Exception as e:
            if type(e).__name__ == 'Forbidden' and 'bot was blocked by the user' in e.message:
                print('Deleting blocked user')
                bot_manager.user_orm.remove_user(reply['to_chat_id'])

def buttons_to_inline_keyboard(buttons):
    if buttons is None or len(buttons) == 0:
        return None
    keyboard = [
        [
            InlineKeyboardButton(button['text'], web_app=WebAppInfo(url=button['url'])) if button.get('url') is not None else
            InlineKeyboardButton(button['text'], callback_data=button['data'])
        ] for button in buttons
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

async def send_reply(message: Message, rets: list[Reply]):
    for ret in rets:
        if len(ret['message']) > 0:
            print("Sending message to " + str(ret['to_chat_id']) + " " + str(datetime.datetime.now().isoformat()))
            await message.reply_text(ret['message'], parse_mode='HTML', protect_content=ret['protect_content'], reply_markup=buttons_to_inline_keyboard(ret['buttons']))

        if len(ret['menu_commands']) > 0:
            await bot.set_my_commands(
                commands=ret['menu_commands'],
                scope=telegram.BotCommandScopeChat(
                    chat_id=message.chat.id
                )
            )

        if 'image' in ret and ret['image'] is not None:
            await message.reply_photo(photo=ret['image'])
            if ret['image'].startswith('tmp_'):
                os.remove(ret['image'])


async def send_reply_with_bot(ret: Reply):
    global bot
    if len(ret['message']) > 0:
        print("Sending message to " + str(ret['to_chat_id']) + " " + str(datetime.datetime.now().isoformat()))
        await bot.send_message(ret['to_chat_id'], ret['message'], parse_mode='HTML', protect_content=ret['protect_content'], reply_markup=buttons_to_inline_keyboard(ret['buttons']))

    if 'image' in ret and ret['image'] is not None:
        if ret['image'].endswith('.txt'):
            with open(ret['image'], "rb") as file:
                await bot.send_document(ret['to_chat_id'], document=file, filename='user_data.txt')
        else:
            await bot.send_photo(ret['to_chat_id'], photo=ret['image'])

        if ret['image'].startswith('tmp_'):
            os.remove(ret['image'])

def get_message(update: Update):
    return update.message if update.message is not None else update.callback_query.message


async def start_command(update, context):
    global bot_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = bot_manager.on_start_command(chat_id)
    await send_reply(message, [ret])

async def settings_command(update: Update, context):
    global bot_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = bot_manager.on_settings_command(chat_id)
    await send_reply(message, [ret])

async def fallback_command(update: Update, context):
    global bot_manager
    message = get_message(update)
    chat_id = message.chat.id
    ret = bot_manager.on_data_provided(chat_id, message.text)
    await send_reply(message, ret)

async def fetch_and_process_updates(app: Application):
    offset = None

    while True:
        updates = await app.bot.get_updates(offset=offset, timeout=10, allowed_updates=["message",
                                                                                        "edited_channel_post", "callback_query", "message_reaction"])  # Fetch updates from Telegram
        if len(updates) > 0:
            print('Received ' + str(len(updates)) + ' updates at ' + str(datetime.datetime.now()))
        for update in updates:
            # print(update)
            await app.process_update(update)
            offset = update.update_id + 1

        await asyncio.sleep(1)
        await process_ticks()

async def button(update: Update, ctx) -> None:
    global bot_manager
    query = update.callback_query

    await query.answer()
    message = get_message(update)
    ret = bot_manager.on_data_provided(message.chat.id, query.data)
    await send_reply(message, ret)


async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('settings', settings_command))

    app.add_handler(CallbackQueryHandler(button))

    app.add_handler(MessageHandler(filters.TEXT, fallback_command))

    await app.initialize()
    print("Bot is running...")

    await fetch_and_process_updates(app)

asyncio.run(main())
