#! python3
# 
# scraper3.py: Scrapes Letterboxd for films with highest proportion of 
# people who watched it who is a fan of it. Throws all film info into
# an unsorted csv, which is then imported into Excel and sorted there.

import requests
import csv
import time
import re
import operator
from datetime import date
from bs4 import BeautifulSoup
from unidecode import unidecode

# Sets output file name to current date and time
OUTPUT_FILE = 'fans_' + time.strftime("%m-%d-%Y") + '_' + time.strftime("%H-%M-%S") + '.csv'
IMPORT_FILE = OUTPUT_FILE[:-4] + '_import' + OUTPUT_FILE[-4:]
PAGE_COUNT = 10
PAGES = ['http://letterboxd.com/films/ajax/popular/size/small/page/',
         'http://letterboxd.com/films/ajax/by/rating/size/small/page/']

### Gathers urls of films from a page of most popular and highest rated
def get_urls(page, page_num):
    urls = []
    r = requests.get(page + str(page_num) + '/')
    soup = BeautifulSoup(r.text, 'html.parser')
    for link in soup.find("ul").find_all('a'):
        urls.append("http://letterboxd.com" + link.get('href'))
    print(str(len(urls))+' films found on '+page+str(page_num))
    r.close()
    return urls

### Gathers film info using OMDb and scrapes number of watched and fans.
### Also calculates percentage fans out of watched.
def get_info(url):

    # First scrape for film info from Letterboxd page.
    r = requests.get(url, allow_redirects=False)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Use unidecode to handle annoying unicode issues with foreign words.
    try:
        title = unidecode(soup.find("h1", itemprop = "name").text)
        year = int(soup.find(itemprop = "datePublished").text)
        directors = soup.find_all("a", itemprop = "director")
        if len(directors) > 1: # if multiple directors found
            d = []
            for director in directors:
                d.append(unidecode(director.text))
            # gets directors and concatenates them into one string
            director = ', '.join(d) 
        else:
            director = unidecode(directors[0].text)
        runtime_text = soup.find("p", "text-footer").text
        runtime = int(re.search('\d+', runtime_text).group())
        tmdb = int(soup.body['data-tmdb-id'])
    except:
        print("Error in finding film info for " + url)
        title = ""
        year = 0
        director = ""
        runtime = 0
        tmdb = 0
        
    r.close()
    
    # Special cases
    if url == "http://letterboxd.com/film/the-up-series/":
        title = "The Up Series"
        year = 1964
        director = "Michael Apted"
        runtime = 769
    if "Joel Coen" in director:
        director = "Joel Coen, Ethan Coen"

    # Next, grab number of fans and watched from Letterboxd page
    lbd_url = url.split('/')[4]
    r = requests.get("http://letterboxd.com/csi/film/" + lbd_url + "/sidebar-viewings/")
    r_soup = BeautifulSoup(r.text, 'html.parser')
    s = r_soup.find_all('a')
    r.close()

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
        fans = 0

    if watched != 0:    # covers division by zero case
        percent = fans / watched * 100
    else:
        percent = 0
    return [title, year, director, runtime, fans, watched, percent, tmdb]
    
### Writes film info to csv and returns number of films processed.
def write_to_csv():
    print('WRITING TO ' + OUTPUT_FILE)
    urls1 = []
    urls2 = []
    for i in range(1, PAGE_COUNT + 1):
        urls1 += get_urls(PAGES[0], i)
        urls2 += get_urls(PAGES[1], i)
    urls = list(set(urls1+urls2)) # collects all urls and removes duplicates
    print("Number of films:", len(urls))
    film_info = {}
    with open(OUTPUT_FILE, 'w', newline='') as outfile:
        filmout = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
        i = 0
        for url in urls:
            if i % 50 == 0:
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
    with open(OUTPUT_FILE, "w", newline='') as outfile:
        writer = csv.writer(outfile)
        # Sets column headers for csv file
        writer.writerow(['Title', 'Year', 'Director(s)', 'Runtime', 'Fans', 
                         'Watched', '% Fans out of Watched', 'TMDB ID', 'URL'])
        writer.writerows(sortedlist)

### Creates CSV file in Letterboxd import format 
### (https://letterboxd.com/about/importing-data/)
def prepare_import():
    with open(OUTPUT_FILE, newline='') as infile, open(IMPORT_FILE, 'w', newline='') as outfile:
        filmout = csv.writer(outfile, quoting=csv.QUOTE_ALL)
        filmout.writerow(["tmdbID","Title","Year","Directors"])
        filmin = csv.reader(infile, delimiter=',', quotechar='"')
        next(filmin)
        for row in filmin:
            filmout.writerow([row[7],row[0],row[1],row[2]])        

def main():
    start = time.time()
    len = write_to_csv()
    sort_csv()
    prepare_import()
    end = time.time()
    total_time = end - start
    print("Execution took %f seconds, which is %f seconds per film."
          % (total_time, total_time/len))

if __name__ == '__main__':
    main()