import random
from parsel import Selector
import stealth_requests as requests
from stealth_requests import AsyncStealthSession
import asyncio
import inspect
from fake_useragent import UserAgent
import copy
import re
from lxml import html
import jinja2
from notgsmarbot.logs import LOGGER
from pkg_resources import resource_filename


def URL_TO_ANTUTU(dev): return f"https://www.kimovil.com/ru/{dev}/antutu"


SEARCH_DEV_URL = "https://www.kimovil.com/_json/autocomplete_devicemodels_joined.json"
ANTUTU_SCORE_XPATH = (
    '//*[@id="margin"]/div[2]/div[2]/div[1]/div/div/article/div/p[1]/b/text()'
)


def _parse_vers(devices):
    new_set = []
    for i, dev in enumerate(devices):
        if dev["type"] == 2:
            continue  # skips tv
        if "vers" not in dev.keys():
            cp = copy.copy(dev)
            cp["specs"] = "Default"
            new_set.append(cp)
            continue
        vers: str = dev["vers"]
        variants_mixed = vers.split("#")
        added_code_names = set()
        for v in variants_mixed:
            desc, url = v.split("=")
            sub_var = desc.split("·")[-1]
            if sub_var in added_code_names:
                continue
            added_code_names.add(sub_var)
            cp = copy.copy(dev)
            cp["url"] = url
            cp["specs"] = desc
            new_set.append(cp)
    return new_set


def get_device_by_querry(qerry: str):
    payload = {"name": qerry}
    kimovil_url = SEARCH_DEV_URL
    ua = UserAgent()
    headers = {"User-Agent": str(ua.chrome)}
    resp = requests.get(kimovil_url, params=payload, headers=headers)
    try:
        resp_json = resp.json()
    except:
        LOGGER.error("Json fucked up")
        return []
    try:
        return _parse_vers(resp_json["results"])
    except TypeError as e:
        LOGGER.error(inspect.currentframe().f_code.co_name)
        LOGGER.error(e)
        LOGGER.error(f"resp_json type {type(resp_json)}")
        return []


async def get_device_by_querry_async(qerry: str):
    payload = {"name": qerry}
    kimovil_url = SEARCH_DEV_URL
    ua = UserAgent()
    headers = {"User-Agent": str(ua.chrome)}
    async with AsyncStealthSession() as session:
        resp = await session.get(kimovil_url, params=payload, headers=headers)
    try:
        resp_json = resp.json()
    except:
        LOGGER.error("Json fucked up")
        return []
    try:
        return _parse_vers(resp_json["results"])
    except TypeError as e:
        LOGGER.error(inspect.currentframe().f_code.co_name)
        LOGGER.error(e)
        LOGGER.error(f"resp_json type {type(resp_json)}")
        return []


async def get_antutu_async(url: str):
    url = URL_TO_ANTUTU(url)

    async def get_async():
        return requests.get(url)

    cor = asyncio.create_task(get_async())
    await cor
    resp = cor.result()
    selector = Selector(str(resp.content))
    score = selector.xpath(ANTUTU_SCORE_XPATH).get()
    LOGGER.debug(url, score)
    return score


def get_antutu_sync(url: str):
    url = URL_TO_ANTUTU(url)
    resp = requests.get(url)
    selector = Selector(str(resp.content))
    score = selector.xpath(ANTUTU_SCORE_XPATH).get()
    return score


def URL_TO_SPECS(dev): return f"https://www.kimovil.com/en/where-to-buy-{dev}"


SPECS_HEADER_XPATH = '//*[@id="margin"]/div[1]/header'
SPECS_CARD_XPATH = '//*[@id="margin"]/div[3]/div/div[1]'
with open(resource_filename("notgsmarbot", "files/show.jinja")) as file_:
    JINJA_TEMPLATE = jinja2.Template(file_.read())


def _replace_protocol_relative_urls(html):
    # Регулярное выражение для нахождения всех ссылок, начинающихся с //
    pattern = r'(?<!:)(?<=["\'\s])//([^"\',\s]+)'
    # Замена всех найденных ссылок на https://
    result = re.sub(pattern, r"https://\1", html)
    return result


def get_specs_card(url):
    url = URL_TO_SPECS(url)
    LOGGER.debug(url)
    resp = requests.get(url)
    header_html = resp.xpath(SPECS_HEADER_XPATH).pop()
    header = html.tostring(header_html, encoding="unicode")
    header = _replace_protocol_relative_urls(header)
    footer = html.tostring(resp.xpath(
        SPECS_CARD_XPATH).pop(), encoding="unicode")
    page_html = JINJA_TEMPLATE.render(blue_header=header, footer=footer)
    return page_html


async def get_specs_card_async(url):
    url = URL_TO_SPECS(url)
    async with AsyncStealthSession() as session:
        for i in range(10):
            try:
                ua = UserAgent()
                session_cor = session.get(
                    url, headers={"User-Agent": str(ua.chrome)})
                session_task = asyncio.create_task(session_cor)
                await session_task
                resp = session_task.result()
                header_html = resp.xpath(SPECS_HEADER_XPATH).pop()
                LOGGER.debug(f"OK {url}")
                break
            except IndexError:
                LOGGER.warning(f"Cloudflare blocked rq {url}")
                await asyncio.sleep(random.random())

    header = html.tostring(header_html, encoding="unicode")
    header = _replace_protocol_relative_urls(header)
    footer = html.tostring(resp.xpath(
        SPECS_CARD_XPATH).pop(), encoding="unicode")
    page_html = JINJA_TEMPLATE.render(blue_header=header, footer=footer)
    return page_html
