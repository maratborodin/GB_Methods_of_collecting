import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://hh.ru/search/vacancy?fromSearchLine=true&st=searchVacancy&text=Python&from=suggest_post&area=1&search_field=description&search_field=company_name&search_field=name',
        'https://hh.ru/search/vacancy?fromSearchLine=true&st=searchVacancy&text=Python&from=suggest_post&area=2&search_field=description&search_field=company_name&search_field=name']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@data-qa="pager-next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath('//h1[@data-qa="vacancy-title"]/text()').get()
        salary = response.xpath('//p[contains(@class,"vacancy-salary")]/span/text()').getall()
        employer = response.xpath('//a[@data-qa="vacancy-company-name"]/span/text()').getall()
        city = response.xpath('//p[@data-qa="vacancy-view-location"]/text()').get()
        link = response.url
        item = JobparserItem(name=name, salary=salary, employer=employer, city=city, link=link)
        yield item