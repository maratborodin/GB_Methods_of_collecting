from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from Instaparser.spiders.instagram import InstaSpider
from Instaparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    #query = input('')
    process.crawl(InstaSpider, query='r.proeschel')

    process.start()