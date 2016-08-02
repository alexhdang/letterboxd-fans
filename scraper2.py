#! python3
# 
# scraper2.py: Scrapes Letterboxd for films with highest proportion of 
# people who watched it who is a fan of it. Throws all film info into
# an unsorted csv, which is then imported into Excel and sorted there.

import requests
import csv
import urllib
import time
import re
import json
from selenium import webdriver
from datetime import date
from bs4 import BeautifulSoup

# Sets output file name to current date and time
OUTPUT_FILE = 'fans_' + time.strftime("%m-%d-%Y") + '_' + time.strftime("%H-%M-%S") + '.csv'

### Gathers urls of films from first 5 pages of most popular
def get_urls1(page):
	urls = []
	driver = webdriver.PhantomJS()
	driver.get('http://letterboxd.com/films/popular/page/' + str(page) + '/') 
	#time.sleep(2)
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
	#time.sleep(2)
	elements = driver.find_elements_by_class_name('frame')
	for element in elements:
		urls.append(element.get_attribute("href"))
	driver.close()
	print(len(urls), 'films found by rating on page', page)
	print(urls[0:3])
	return urls

### Gathers film info using OMDb and scrapes number of watched and fans.
### Also calculates percentage fans out of watched.
def get_info(url):

	# First scrape for IMDb id and grab film info using json request of OMDb.
	r = requests.get(url)
	r_soup = BeautifulSoup(r.text, 'html.parser')
	s = r_soup.find("p", "text-link").find('a')['href']
	filmid = s.split('/')[4]
	
	r = requests.get('http://www.omdbapi.com/?i=' + filmid).json()
	try:
		title = r['Title']
		year = r['Year']
		if r['Runtime'] == 'N/A':
			runtime = ''
		else:
			runtime = r['Runtime'][:-4]
		director = r['Director'].split(', ') # Extract up to two directors
		director = ', '.join(director[:2])
	except:
		print("Error in finding info for " + url)
		title, year, runtime, director = "", "", "", ""
		
	# Special cases
	if url == "http://letterboxd.com/film/the-up-series/":
		title = "The Up Series"
		year = "1964"
		director = "Michael Apted"
		runtime = "769"
	if url == "http://letterboxd.com/film/flcl/":
		director = "Kazuya Tsurumaki"
	if url == "http://letterboxd.com/film/scenes-from-a-marriage/":
		director = "Ingmar Bergman"
	if url == "http://letterboxd.com/film/berlin-alexanderplatz/":
		director = "Rainer Werner Fassbinder"
	if url == "http://letterboxd.com/film/the-decalogue/":
		title = "The Decalogue"
		year = "1989"
		director = "Krzysztof Kieslowski"
		runtime = "572"
	if url == "http://letterboxd.com/film/kill-bill-the-whole-bloody-affair/":
		title = "Kill Bill: The Whole Bloody Affair"
		year = "2009"
		director = "Quentin Tarantino"
		runtime = "243"
		
	# Next, grab number of fans and watched from Letterboxd page
	driver = webdriver.PhantomJS()
	driver.get(url) 
	#time.sleep(1.5)
	try:
		watched_text = driver.find_element_by_xpath(
			'//*[@id="film-page-wrapper"]/div[2]/aside/section[3]/p/a[1]').text
		dummy = re.findall('\d+', watched_text.replace(',', ''))
		watched = int(dummy[0])
	except:
		print("Error in finding number of watched for " + url)
		watched = 0
	
	# separate case for finding fans on page, 
	# because it will raise an error if there are none
	try:
		fans_text = driver.find_element_by_xpath(
			'//*[@id="film-page-wrapper"]/div[2]/aside/section[3]/p/a[2]').text
		dummy = re.findall('\d+', fans_text.replace(',', ''))
		fans = int(dummy[0])
	except:
		print("Error in finding number of fans for " + url)
		fans = 0
	driver.close()
	
	if watched != 0: 	# covers division by zero case
		percent = fans / watched * 100
	else:
		percent = 0
	#print(url, title, fans, watched, percent)
	return [title, year, director, runtime, fans, watched, percent]
	
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
	filmout.writerow(['Title', 'Year', 'Director(s)', 'Runtime',
						'Fans', 'Watched', '% Fans out of Watched', 'URL'])
	i = 0
	for url in urls:
		if i % 20 == 0:
			print(str(i) + " films processed.")
		info = get_info(url)
		# Writes to csv if percent fans out of watched is at least 1%,
		# or if # watched is 0 (which is checked manually)
		if info[6] >= 1.0 or info[5] == 0:
			filmout.writerow(info + [url])
		i += 1