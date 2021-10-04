# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию.
# Добавить в решение со сбором вакансий(продуктов) функцию,
# которая будет добавлять только новые вакансии/продукты в вашу базу.

import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import re
import json
import pymongo
from pymongo import MongoClient

def exists_in_db(s):
    for doc in vacancy_db.find({'link': s}):
        return True

client = MongoClient('127.0.0.1', 27017)

db = client['Vacancies']
vacancy_db = db.vacancy_db

url = 'https://hh.ru/search/vacancy'

search_text = input("Вакансия: ")

params = {'clusters': 'true',
          'ored_clusters': 'true',
          'enable_snippets': 'true',
          'st': 'searchVacancy',
          'text': search_text,
          'area': '113'
          }

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 YaBrowser/21.8.3.614 Yowser/2.5 Safari/537.36'}

vacancy_number = 1
page = 0

while True:
    response = requests.get(url, params=params, headers=headers)
    soup = bs(response.text, 'html.parser')

    vacancy_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})

    button_next = soup.find('a', text='дальше')

    vacancies = []

    for vacancy in vacancy_list:
        vacancy_data = {}

        vacancy_name_info = vacancy.find('a', attrs={'class': 'bloko-link'})

        vacancy_name = vacancy_name_info.text

        vacancy_link = vacancy_name_info['href']

        vacancy_employer = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
        if not vacancy_employer:
            vacancy_employer = None
        else:
            vacancy_employer = vacancy_employer.text

        vacancy_city = vacancy.find('span', attrs={'class': 'vacancy-serp-item__meta-info'}).text

        salary = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
        if not salary:
            salary_min = None
            salary_max = None
            salary_currency = None
        else:
            salary = salary.getText() \
                .replace(u'\xa0', u'')

            salary = re.split(r'\s|<|>', salary)

            if salary[0] == 'до':
                salary_min = None
                if salary[1].isdigit() and salary[2].isdigit():
                    salary_max = int("".join([salary[1], salary[2]]))
                    salary_currency = salary[3]
                else:
                    salary_max = int(salary[1])
                    salary_currency = salary[2]
            elif salary[0] == 'от':
                if salary[1].isdigit() and salary[2].isdigit():
                    salary_min = int("".join([salary[1], salary[2]]))
                    salary_currency = salary[3]
                else:
                    salary_min = int(salary[1])
                    salary_currency = salary[2]
                salary_max = None
            else:
                if salary[0].isdigit() and salary[1].isdigit():
                    salary_min = int("".join([salary[0], salary[1]]))
                    if salary[3].isdigit() and salary[4].isdigit():
                        salary_max = int("".join([salary[3], salary[4]]))
                        salary_currency = salary[5]
                    else:
                        salary_max = int(salary[3])
                        salary_currency = salary[4]
                else:
                    salary_min = int(salary[0])
                    if salary[2].isdigit() and salary[3].isdigit():
                        salary_max = int("".join([salary[2], salary[3]]))
                        salary_currency = salary[4]
                    else:
                        salary_max = int(salary[2])
                        salary_currency = salary[3]

        vacancy_data['vacancy_number'] = vacancy_number
        vacancy_data['name'] = vacancy_name
        vacancy_data['link'] = vacancy_link
        vacancy_data['employer'] = vacancy_employer
        vacancy_data['city'] = vacancy_city
        vacancy_data['salary_min'] = salary_min
        vacancy_data['salary_max'] = salary_max
        vacancy_data['salary_currency'] = salary_currency
        vacancy_data['site'] = url

        vacancy_number += 1
        #vacancies.append(vacancy_data)

        if exists_in_db(vacancy_data['link']) is True:
            continue
        else:
            vacancy_db.insert_one(vacancy_data)

    if not button_next or not response.ok:
        break

    page += 1
    params = {'clusters': 'true',
              'ored_clusters': 'true',
              'enable_snippets': 'true',
              'st': 'searchVacancy',
              'text': search_text,
              'area': '113',
              'page': page}

# with open('vacancies.json', 'w') as json_file:
#     json.dump(vacancies, json_file)

# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
# (необходимо анализировать оба поля зарплаты - минимальнную и максимульную).
# Для тех, кто выполнил задание с Росконтролем - напишите запрос для поиска продуктов с рейтингом не ниже введенного
# или качеством не ниже введенного (то есть цифра вводится одна, а запрос проверяет оба поля)

from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['Vacancies']
vacancy_db = db.vacancy_db

salary_info = int(input('Введите желаемую зарплату: '))

cur_USD = 72.5
cur_EUR = 84

for doc in vacancy_db.find({'$or': [{'salary_currency': 'руб.'},
                                    {'salary_currency': 'USD'},
                                    {'salary_currency': 'EUR'},
                                    ]
                            },
                           ):
    if doc['salary_currency'] == 'руб.':
        if doc['salary_min'] is not None and doc['salary_min'] > salary_info or doc['salary_max'] is not None and doc['salary_max'] > salary_info:
            pprint(doc)
    elif doc['salary_currency'] == 'USD':
        if doc['salary_min'] is not None and (doc['salary_min']) * cur_USD > salary_info or doc['salary_max'] is not None and (doc['salary_max']) * cur_USD > salary_info:
            pprint(doc)
    elif doc['salary_currency'] == 'EUR':
        if doc['salary_min'] is not None and (doc['salary_min']) * cur_EUR > salary_info or doc['salary_max'] is not None and (doc['salary_max']) * cur_EUR > salary_info:
            pprint(doc)
    else:
        continue
