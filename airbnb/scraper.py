from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options 
import time, os
import pandas as pd
from parsel import Selector
from entries import search_city, save_path






chrome_options = Options()

chrome_options.add_argument(f'user-agent=Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36')

chrome_options.add_argument('--headless')
chrome_options.add_argument('window-size=1920x1080')
driver = webdriver.Chrome(options=chrome_options)

print('getting airbnb home page')

driver.get('https://fr.airbnb.com')
time.sleep(10)

city = '//*[@id="bigsearch-query-detached-query-input"]'
search = '_1mzhry13'

city_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, city)))
city_element.click()
time.sleep(3)

print('Searching for your location')
city_element.send_keys(search_city)
time.sleep(3)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, search))).click()
time.sleep(5)

next_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '._za9j7e')))

places = []

print('Start collecting data!')

i = 1
while next_page:
	url = driver.current_url
	sel = Selector(driver.page_source)
	containers = sel.css('._1e541ba5')
	for container in containers:
		link = 'https://fr.airbnb.com' + containers[0].css('._8s3ctt a::attr(href)').get()
		title = container.css('._5kaapu span::text').get()
		location = container.css('._1tanv1h div::text').get().replace(' ⋅ ', '/')
		features = '/ '.join([a for a in container.css('._3c0zz1 span::text').getall() if a != ' · '])
		price = container.css('._ls0e43 span::text').getall()[2]
		if container.css('._1hxyyw3 span::attr(aria-label)').get():
			evaluation = container.css('._1hxyyw3 span::attr(aria-label)').get().split(';')[0]
			comments = container.css('._1hxyyw3 span::attr(aria-label)').get().split(';')[1]
			places.append((title, location, features, price, evaluation, comments, link))
		else:
			evaluation = 'NA'
			comments= 'NA'
			places.append((title, location, features, price, evaluation, comments, link))
	
	print(f'finished page {i}')

	next_page.click()
	time.sleep(5)
	next_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '._za9j7e')))
	new_url = driver.current_url
	if url == new_url:
		break
	else:
		url = new_url
		i += 1


print('Finish! Storing in csv file')

if save_path != '':
	pd.DataFrame(places, columns=['title', 'location', 'features', 'price', 'evaluation', 'comments', 'link']).to_csv(save_path)
else:
	save_path = os.path.join(os.getcwd(), 'data.csv')
	pd.DataFrame(places, columns=['title', 'location', 'features', 'price', 'evaluation', 'comments', 'link']).to_csv(save_path)


driver.quit()

print('Data saved!')

