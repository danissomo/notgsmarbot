import requests
from bs4 import BeautifulSoup
from logs import LOGGER
import aiohttp

TOKEN = "your_access_token"  # Токен, полученный при регистрации аккаунта Telegra.ph
TELEGRAPH_API = "https://api.telegra.ph/createPage"

def obtain_token()->str:
    '''
    ### Returns field access_token from json:
    ```json
    {
        "ok": true,
        "result": {
            "short_name": "MyBot",
            "author_name": "",
            "author_url": "",
            "access_token": "your_access_token",
            "auth_url": "https://telegra.ph/auth/your_auth_key"
        }
    }
    ```
    '''
    response = requests.post("https://api.telegra.ph/createAccount", json={"short_name": "MyBot"})
    data = response.json()
    return data['result']['access_token']

def html_to_telegraph(html: str):
    """Конвертирует HTML в JSON-структуру, совместимую с Telegra.ph."""
    soup = BeautifulSoup(html, "html.parser")
    
    def parse_element(element):
        """Преобразует HTML-элементы в формат Telegra.ph."""
        tag = element.name
        if not tag:
            return element.string  # Если текст — просто вернуть строку
        children = [parse_element(child) for child in element.children]
        return {"tag": tag, "children": children}

    return [parse_element(soup)]

async def create_telegraph_page(title, author_name, content_html):
    """Асинхронно создает страницу в Telegra.ph с HTML-контентом."""
    content_json = html_to_telegraph(content_html)
    
    data = {
        "access_token": TOKEN,
        "title": title,
        "author_name": author_name,
        "content": content_json,
        "return_content": True
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(TELEGRAPH_API, json=data) as response:
            result = await response.json()
    
    if result["ok"]:
        print(f"Статья опубликована: {result['result']['url']}")
        return result['result']['url']
    else:
        print("Ошибка:", result)
        return None
