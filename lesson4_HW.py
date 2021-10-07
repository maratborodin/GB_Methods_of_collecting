import requests
from pprint import pprint
from lxml import html
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['News']
mail_news = db.mail_news

url = 'https://news.mail.ru/'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}

response = requests.get(url, headers=headers)

dom = html.fromstring(response.text)

items = dom.xpath('//td[@class="daynews__main"]/div | //div[@class="daynews__item"] | //ul[@data-module]/li')

for item in items:

    news = {}
    title = item.xpath('.//span[@class="photo__captions"]//span[1]/text() | .//a/text()')[0].replace('\xa0', ' ')
    link = item.xpath('.//a/@href')[0]
    response_link = requests.get(link, headers=headers)
    dom_news = html.fromstring(response_link.text)
    source = dom_news.xpath('//span[@class="note"]//span[@class="link__text"]/text()')[0]
    date = dom_news.xpath('//span[@class="note"]/span[@datetime]/@datetime')[0]

    news['title'] = title
    news['link'] = link
    news['date'] = date
    news['source'] = source

    try:
        mail_news.update_one({'link': news['link']}, {'$set': news}, upsert=True)
    except Exception:
        pprint(f'Ошибка загрузки')