from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
    Bot,
    InlineQueryResultPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    InlineQueryHandler,
    ChosenInlineResultHandler,
    ContextTypes,
    Application,
)
from telegram.constants import InlineQueryResultLimit
from uuid import uuid4
from notgsmarbot.config import load_config, CONFIG
from notgsmarbot.kimovil_api import (
    URL_TO_ANTUTU,
    get_device_by_querry_async,
    get_specs_card_async,
)
from notgsmarbot.logs import LOGGER
from pyppeteer import launch
from pyppeteer.page import Page
import asyncio
import random
import time
import os
from fake_useragent import UserAgent
from notgsmarbot.firstlaunch import first_launch

RSP_LOAD_MOCK = InputTextMessageContent(
    "Поиск..",
)
RQ_CACHE = {}
BROWSER = None


async def inline_query_handler(update: Update, context):
    """Обработка inline-запросов."""
    query = update.inline_query.query
    LOGGER.info(f"GOT RQ: {query}")
    if not query or len(query) < 3:
        return

    devices = (await get_device_by_querry_async(query))[
        : InlineQueryResultLimit.MAX_ID_LENGTH
    ]
    results = []

    for device in devices:
        keyboard = [
            [InlineKeyboardButton(
                "Источник", url=URL_TO_ANTUTU(device["url"]))]
        ]
        article = InlineQueryResultArticle(
            id=str(uuid4()),
            title=device["full_name"],
            description=device["specs"],
            input_message_content=RSP_LOAD_MOCK,
            thumbnail_url="https://cdn-files.kimovil.com" + device["img"],
            reply_markup=InlineKeyboardMarkup(keyboard),
            url=device["url"],
            hide_url=True,
        )
        RQ_CACHE[article.id] = device["url"]
        results.append(article)

    await update.inline_query.answer(results, cache_time=1, auto_pagination=True)
    LOGGER.info("Ответ на inline-запрос отправлен")
    import time

    s = time.time_ns()
    LOGGER.debug(f"Start time {s}")


async def render_html(html: str):
    """Рендер HTML в изображение."""
    global BROWSER
    if BROWSER is None:
        BROWSER = await launch(
            headless=True,
            executablePath=CONFIG.browser.execurable,
            handleSIGINT=False,
            args=CONFIG.browser.args,
        )

    page: Page = await BROWSER.newPage()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(page.setUserAgent(UserAgent().chrome))
        tg.create_task(page.setViewport(CONFIG.browser.viewport.to_dict()))
        tg.create_task(page.setContent(html))
    await page.waitForSelector("body")
    await page.waitForFunction(
        """() => {
        return performance.getEntriesByType('resource')
            .every(entry => entry.responseEnd && (performance.now() - entry.responseEnd) > 300);
        }"""
    )
    img_data = await page.screenshot({"type": "jpeg", "fullPage": True})
    await asyncio.create_task(page.close())
    return img_data


async def chosen_inline_result(update: Update, context):
    """Обработка выбора inline-результата."""
    result = update.chosen_inline_result
    user = result.from_user.username
    LOGGER.debug(f"result: {result}")
    url = RQ_CACHE.pop(result.result_id)
    LOGGER.info(f"User {user} selected: {url}")
    page_html = await get_specs_card_async(url)
    page_img = await render_html(page_html)
    bot: Bot = context.bot
    bot_send = bot.send_photo(
        chat_id=CONFIG.tg.god_chat_id, photo=page_img, caption=f'@{user} : {url}')
    photo_change = bot.edit_message_media(
        media=InputMediaPhoto(page_img), inline_message_id=result.inline_message_id
    )
    await bot_send
    await photo_change


async def post_shutdown(app):
    LOGGER.info("Exiting...")
    if BROWSER is not None:
        LOGGER.info("Closing browser...")
        await BROWSER.close()
        LOGGER.info("Closed")


def main():
    load_config()
    random.seed(time.time())
    if CONFIG.tg.token is None or CONFIG.tg.god_chat_id is None:
        first_launch()
    app = (
        ApplicationBuilder()
        .token(CONFIG.tg.token)
        .build()
    )
    app.add_handler(InlineQueryHandler(inline_query_handler))
    app.add_handler(ChosenInlineResultHandler(chosen_inline_result))
    app.post_shutdown = post_shutdown
    LOGGER.info("Приложение запущено")
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
