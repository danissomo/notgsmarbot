from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    Application,
    CommandHandler
)
from notgsmarbot.config import save_config, CONFIG
from notgsmarbot.logs import LOGGER
from pyppeteer import launch
import asyncio


class BrowserError(Exception):
    pass


async def browser_check():
    try:
        LOGGER.info("Staring browser")
        browser = await launch(
            headless=True,
            executablePath=CONFIG.browser.execurable,
            handleSIGINT=False,
            args=CONFIG.browser.args,
        )
        LOGGER.info("Browser started")
        LOGGER.info("Closing browser")
        await browser.close()
        LOGGER.info("Browser closed")
    except Exception as e:
        LOGGER.critical(str(e))
        LOGGER.critical("GOT EXCEPTION WITH BROWSER, check launch args")
        raise BrowserError()


async def print_bot_link(app: Application):
    bot_info = await app.bot.get_me()
    bot_username = bot_info.username
    LOGGER.info(f"Go to: https://t.me/{bot_username}")
    LOGGER.info(f"And send /start")


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    LOGGER.info(f"chat_id = {chat_id}")
    await update.message.reply_text(f"Your chat ID is {chat_id}")
    CONFIG.tg.god_chat_id = chat_id
    CONFIG.tg.first_launch = False
    LOGGER.info("Saving config...")
    save_config()
    LOGGER.info("Exiting...")
    context.application.stop_running()


def first_launch():
    LOGGER.info("First launch of the bot")
    if CONFIG.tg.token is None:
        LOGGER.info("Enter telegram bot token: ")
        CONFIG.tg.token = input()
    LOGGER.info("Let's obtain your chat_id")
    app = (
        ApplicationBuilder()
        .token(CONFIG.tg.token)
        .build()
    )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(print_bot_link(app))
    app.add_handler(CommandHandler("start", start))
    LOGGER.info("App started")
    app.run_polling(close_loop=False)
    LOGGER.info("App exited")
    LOGGER.info("Now browser check")

    try:
        asyncio.run(browser_check())
    except:
        exit(1)
    exit(0)
