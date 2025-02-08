from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
    Bot,
    LinkPreviewOptions,
    InlineQueryResultPhoto,
    InlineQueryResultCachedPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    InlineQueryHandler,
    ChosenInlineResultHandler,
    MessageHandler,
    filters,
)
from telegram.constants import InlineQueryResultLimit
from uuid import uuid4
from notgsmarbot.config import load_config, CONFIG, parse_pkg_meta
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
from pkg_resources import resource_filename

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
        : 30
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
            thumbnail_height=100,
            thumbnail_width=2
        )
        RQ_CACHE[article.id] = device["url"]
        results.append(article)

    if len(results) == 0:
        article = InlineQueryResultArticle(
            id=str(uuid4()),
            title="Not found",
            input_message_content=InputTextMessageContent("Not found")
        )
        RQ_CACHE[article.id] = None
        results.append(article)

    await update.inline_query.answer(results, cache_time=1, auto_pagination=True)
    LOGGER.info("Ответ на inline-запрос отправлен")


async def render_html(html: str = None, get_html_task: asyncio.Task = None):
    """Рендер HTML в изображение."""
    global BROWSER
    if BROWSER is None:
        BROWSER = await launch(
            headless=True,
            executablePath=CONFIG.browser.executable,
            handleSIGINT=False,
            args=CONFIG.browser.args + [f'--user-agent={UserAgent().chrome}'],
            defaultViewport=CONFIG.browser.viewport.to_dict(),
        )

    page: Page = await BROWSER.newPage()
    if html is None:
        await get_html_task
        html = get_html_task.result()
    await page.setContent(html)
    await page.waitForFunction(
        '''() => {
            xp = '#margin > div.kc-container.dark.blue.heading > div > header > div > div.device-main-image.front > figure > a > img'
            const img = document.querySelector(xp);
            return img && img.complete && img.naturalWidth > 0;
        }'''
    )
    img_data = await page.screenshot({"type": "png", "fullPage": True, "quality": 80})
    asyncio.create_task(page.close())
    return img_data


async def chosen_inline_result(update: Update, context):
    """Обработка выбора inline-результата."""
    result = update.chosen_inline_result
    user = result.from_user.username
    LOGGER.debug(f"result: {result}")
    url = RQ_CACHE.pop(result.result_id)
    if url is None:
        return
    LOGGER.info(f"User {user} selected: {url}")
    page_html_task = asyncio.create_task(get_specs_card_async(url))
    page_img = await render_html(get_html_task=page_html_task)
    bot: Bot = context.bot
    bot_send = bot.send_photo(
        chat_id=CONFIG.tg.god_chat_id, photo=page_img, caption=f'@{user} : {url}')
    photo_change = bot.edit_message_media(
        media=InputMediaPhoto(page_img), inline_message_id=result.inline_message_id
    )
    await bot_send
    await photo_change


async def bot_send_greeting(update: Update, context):
    bot: Bot = context.bot
    chat_id = update.message.chat.id
    greeting_path = resource_filename('notgsmarbot', 'files/greeting_ru.txt')
    with open(greeting_path, 'r', encoding='utf-8') as f:
        greeting_text = f.read()
    await bot.send_message(
        chat_id=chat_id,
        text=greeting_text,
        parse_mode="markdown",
        link_preview_options=LinkPreviewOptions(
            show_above_text=True,
            url=parse_pkg_meta("notgsmarbot")["Home-page"]
        )
    )


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
    app.add_handler(MessageHandler(filters.ALL, bot_send_greeting))
    app.post_shutdown = post_shutdown
    LOGGER.info("Приложение запущено")
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
