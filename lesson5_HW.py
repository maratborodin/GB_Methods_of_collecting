from selenium import webdriver
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import time

client = MongoClient('127.0.0.1', 27017)
db = client['mvideo_db']
mvideo_hits = db.mvideo_hits

chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.mvideo.ru')
wait = WebDriverWait(driver, 20)

# time.sleep(5)
#
# alert = driver.switch_to.alert
# alert.dismiss()

pop_up = wait.until(EC.presence_of_element_located((By.XPATH, '//mvid-icon[contains(@class, "modal-layout__close ng-tns-c72-1 ng-star-inserted")]')))
pop_up.click()
time.sleep(4)

driver.execute_script("window.scrollTo(0, 1500);")
time.sleep(4)

try:
    hits = driver.find_element_by_xpath(
        "//mvid-shelf-group/*//span[contains(text(), 'В тренде')]"
    )
except exceptions.NoSuchElementException:
    print('Хиты продаж не найдены')

while True:
    try:
        button = driver.find_elements(By.XPATH, '//mvid-shelf-group/*//button[contains(@class, "btn forward")]/mvid-icon[@type = "chevron_right"]')
        button[1].click()
        time.sleep(3)
    except exceptions.ElementNotInteractableException:
        break

items = driver.find_elements(By.XPATH, "//mvid-shelf-group//mvid-product-cards-group//div[@class='title']")

items_list = []
for item in items:
    item_info = {}
    item_link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
    item_title = item.find_element(By.TAG_NAME, "a").text
    item_info['Title'] = item_title
    item_info['Link'] = item_link

    items_list.append(item_info)

    try:
        mvideo_hits.insert_one(item_info)
        mvideo_hits.create_index('Link', unique=True)
    except dke:
        continue

driver.quit()