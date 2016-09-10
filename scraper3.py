#! python3
# 
# scraper3.py: Scrapes Letterboxd for films with highest proportion of 
# people who watched it who is a fan of it. Throws all film info into
# an unsorted csv, which is then imported into Excel and sorted there.

# http://letterboxd.com/films/ajax/by/rating/size/small/page/1/
# http://letterboxd.com/csi/film/the-godfather/sidebar-viewings/

import requests
import csv
import urllib
import time
import re
import operator
from datetime import date
from bs4 import BeautifulSoup
from unidecode import unidecode

# Sets output file name to current date and time
OUTPUT_FILE = 'fans_' + time.strftime("%m-%d-%Y") + '_' + time.strftime("%H-%M-%S") + '.csv'
PAGE_COUNT = 5

### Gathers urls of films from first 5 pages of most popular and highest rated
def get_urls(page, page_num):
    urls = []
    r = requests.get(page + str(page_num) + '/')
    soup = BeautifulSoup(r.text, 'html.parser')
    for link in soup.find("ul").find_all('a'):
        urls.append("http://letterboxd.com" + link.get('href'))
    print(str(len(urls))+' films found on '+page+str(page_num))
    print(urls[0:3])
    return urls

### Gathers film info using OMDb and scrapes number of watched and fans.
### Also calculates percentage fans out of watched.
def get_info(url):

    # First scrape for film info from Letterboxd page.
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Use unidecode to handle annoying unicode issues with foreign words.
    title = unidecode(soup.find("h1", itemprop = "name").text)
    year = soup.find(itemprop = "datePublished").text
    director = unidecode(soup.find("span", itemprop = "name").text)
    runtime_text = soup.find("p", "text-footer").text
    runtime = int(re.search('\d+', runtime_text).group())

    # Next, grab number of fans and watched from Letterboxd page
    lbd_url = url.split('/')[4]
    r = urllib.request.urlopen("http://letterboxd.com/csi/film/" + lbd_url + "/sidebar-viewings/")
    r_soup = BeautifulSoup(r, 'html.parser')
    s = r_soup.find_all('a')

    try:
        watched_text = s[0].text
        dummy = re.findall('\d+', watched_text.replace(',', ''))
        watched = int(dummy[0])
    except:
        print("Error in finding number of watched for " + url)
        watched = 0

    # separate case for finding fans on page, 
    # because it will raise an error if there are none
    try:
        fans_text = s[1].text
        dummy = re.findall('\d+', fans_text.replace(',', ''))
        fans = int(dummy[0])
    except:
        #print("Error in finding number of fans for " + url)
        fans = 0

    if watched != 0:    # covers division by zero case
        percent = fans / watched * 100
    else:
        percent = 0
    #print(url, title, fans, watched, percent)
    return [title, year, director, 
            runtime, fans, watched, percent]
    
### Writes film info to csv and returns number of films processed.
def write_to_csv():
    print('WRITING TO ' + OUTPUT_FILE)
    urls1 = []
    urls2 = []
    pages = ['http://letterboxd.com/films/ajax/popular/size/small/page/',
             'http://letterboxd.com/films/ajax/by/rating/size/small/page/']
    for i in range(1, PAGE_COUNT + 1):
        urls1 += get_urls(pages[0], i)
        urls2 += get_urls(pages[1], i)
    urls = list(set(urls1+urls2)) # collects all urls and removes duplicates
    print("Number of films:", len(urls))
    film_info = {}
    with open(OUTPUT_FILE, 'w', newline='') as outfile:
        filmout = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
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
    return len(urls)

### Sorts csv by percentage of fans out of total watched.
def sort_csv():
    data = csv.reader(open(OUTPUT_FILE), delimiter=',')
    sortedlist = sorted(data, key=operator.itemgetter(6), reverse=True)
    #print(sortedlist[0:5])
    with open(OUTPUT_FILE, "w", newline='') as outfile:
        writer = csv.writer(outfile)
        # Sets column headers for csv file
        writer.writerow(['Title', 'Year', 'Director(s)', 'Runtime',
                         'Fans', 'Watched', '% Fans out of Watched', 'URL'])
        writer.writerows(sortedlist)

def main():
    start = time.time()
    len = write_to_csv()
    sort_csv()
    end = time.time()
    total_time = end - start
    print("Execution took %f seconds, which is %f seconds per film."
          % (total_time, total_time/len))

if __name__ == '__main__':
    main()