# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.

import requests
from json import dumps
from pprint import pprint
import json
username = 'maratborodin'

url = 'https://api.github.com'

request = requests.get(url + '/users/' + username + '/repos')
#j_data = request.json()

with open('lesson1_HW_ex1.json', 'w') as f:
  json.dump(request.json(), f)

for i in request.json():
    print(i['name'])

# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

import requests
from json import dumps
from pprint import pprint
import json

id_page = '2209124'
token = ''

url = 'https://api.vk.com/method/users.get?user_ids=' + id_page + '&fields=bdate&access_token=' + token + '&v=5.131'

response = requests.get(url)
j_data = response.json()

#pprint(j_data)

with open('lesson1_HW_ex2.json', 'w') as f:
    json.dump(j_data, f)


