import requests
import csv
import urllib
import time
import re
from selenium import webdriver
from datetime import date

# Sets output file name to current date and time
OUTPUT_FILE = 'fans_' + time.strftime("%m-%d-%Y") + '_' + time.strftime("%H-%M-%S") + '.csv'

### Gathers urls of films from first 5 pages of most popular
def get_urls1(page):
	urls = []
	driver = webdriver.PhantomJS()
	driver.get('http://letterboxd.com/films/popular/page/' + str(page) + '/') 
	time.sleep(3)
	elements = driver.find_elements_by_class_name('frame')
	for element in elements:
		urls.append(element.get_attribute("href"))
	driver.close()
	print(len(urls), 'films found from popular on page', page)
	print(urls[0:3])
	return urls

### Gathers urls of films from first 5 pages of highest rated
def get_urls2(page):
	urls = []
	driver = webdriver.PhantomJS()
	driver.get('http://letterboxd.com/films/by/rating/page/' + str(page) + '/') 
	time.sleep(3)
	elements = driver.find_elements_by_class_name('frame')
	for element in elements:
		urls.append(element.get_attribute("href"))
	driver.close()
	print(len(urls), 'films found by rating on page', page)
	print(urls[0:3])
	return urls

### Reads title, year, # watched, and # fans from url.
### Also calculates percentage fans out of watched.
def get_info(url):
	driver = webdriver.PhantomJS()
	driver.get(url) 
	time.sleep(2)
	try:
		title = driver.find_element_by_class_name('film-title').text
		year = int(driver.find_element_by_xpath(
			'//*[@id="featured-film-header"]/p/small/a').text)
		watched_text = driver.find_element_by_xpath(
			'//*[@id="film-page-wrapper"]/div[2]/aside/section[3]/p/a[1]').text
		dummy = re.findall('\d+', watched_text.replace(',', ''))
		watched = int(dummy[0])
	except:
		print("Error in finding info for " + url)
		title, year, watched = '', 0, 0
	
	# separate case for finding fans on page, 
	# because it will raise an error if there are none
	try:
		fans_text = driver.find_element_by_xpath(
			'//*[@id="film-page-wrapper"]/div[2]/aside/section[3]/p/a[2]').text
		dummy = re.findall('\d+', fans_text.replace(',', ''))
		fans = int(dummy[0])
	except:
		print("Error in finding fans for " + url)
		fans = 0
		
	driver.close()
	if watched != 0: 	# covers division by zero case
		percent = fans / watched
	else:
		percent = 0
	print(url, title.encode('utf-8'), year, fans, watched, percent)
	return [title, year, fans, watched, percent]
	
print('WRITING TO ' + OUTPUT_FILE)
urls1 = []
urls2 = []
for page in range(1, 6):
	urls1 += get_urls1(page)
for page in range(1, 6):
	urls2 += get_urls2(page)
urls = list(set(urls1+urls2))	# collects all urls and removes duplicates
print("Number of films:", len(urls))
film_info = {}
with open(OUTPUT_FILE, 'w', newline='') as outfile:
	filmout = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
	# Sets column headers for csv file
	filmout.writerow(['URL', 'Title', 'Year', 'Fans', 'Watched', '% Fans out of Watched'])
	for url in urls:
		info = get_info(url)
		# Writes to csv if percent fans out of watched is at least 1%,
		# or if # watched is 0 (which is checked manually)
		if info[4] >= 0.01 or info[3] == 0:
			filmout.writerow([url] + info)