import requests
from lxml import html
import xml.etree.ElementTree as ET
from datetime import datetime
import urllib.parse

# --- НАСТРОЙКИ ---
URL = "https://it-digit.ru/publications/1s-upravlenie-torgovley-8/"
OUTPUT_FILE = "feed.xml"
CHANNEL_TITLE = "1С:Управление торговлей 8 | ЦИФРА"
CHANNEL_LINK = URL
CHANNEL_DESC = "Статьи по направлениям 1С:УТ"
SITE_BASE_URL = "https://it-digit.ru" 

def main():
    print("Скачиваем страницу...")
    # Обязательно передаем User-Agent, иначе сайт может заблокировать запрос
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(URL, headers=headers)
    response.raise_for_status() # Проверка на ошибки (404, 500 и т.д.)
    
    print("Парсим данные...")
    tree = html.fromstring(response.content)
    
    # Создаем структуру RSS
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = CHANNEL_TITLE
    ET.SubElement(channel, "link").text = CHANNEL_LINK
    ET.SubElement(channel, "description").text = CHANNEL_DESC
    
    # Ищем блоки со статьями (используем XPath из нашего опыта)
    # Находим все div внутри publications-wrap
    articles = tree.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " publications-wrap ")]/div')
    
    print(f"Найдено статей: {len(articles)}")
    
    for article in articles:
        # Извлекаем данные
        title_elements = article.xpath('./div[1]/div/a//text()')
        title = "".join(title_elements).strip()
        
        link_elements = article.xpath('./div[1]/div/a/@href')
        link = link_elements[0] if link_elements else ""
        
        # Делаем ссылку абсолютной, если она относительная
        if link.startswith('/'):
            link = SITE_BASE_URL + link
            
        desc_elements = article.xpath('./div[1]/div/p//text()')
        description = "".join(desc_elements).strip()
        
        img_elements = article.xpath('./div[2]/img/@src')
        image_url = img_elements[0] if img_elements else ""
        if image_url.startswith('/'):
             image_url = SITE_BASE_URL + image_url
             
        # Если картинки нет, можно пропустить этот шаг, но мы добавим пустую строку
        if image_url:
            description += f'<br/><img src="{image_url}" />'

        # Генерируем текущую дату для RSS (так как на сайте ее может не быть в чистом виде)
        pub_date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0300")

        # Если есть заголовок и ссылка, добавляем в ленту
        if title and link:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = title
            ET.SubElement(item, "link").text = link
            ET.SubElement(item, "description").text = description
            ET.SubElement(item, "pubDate").text = pub_date
            
            # Уникальный идентификатор
            ET.SubElement(item, "guid", isPermaLink="true").text = link

    # Сохраняем в файл с правильным форматированием
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ", level=0)
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    
    print(f"Готово! Файл {OUTPUT_FILE} успешно создан.")

if __name__ == "__main__":
    main()