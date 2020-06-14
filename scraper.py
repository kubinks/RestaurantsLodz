from bs4 import BeautifulSoup
import requests
import pandas as pd
from tqdm import tqdm

def get_soup(url):
    return BeautifulSoup(requests.get(url).content, 'lxml')

def get_restaurants(url, i=0, pages=0):
    soup = get_soup(url)
    
    # takes the number of total pages to report
    
    if i == 0:
        pages = int(soup.findAll('a', {'class': 'pageNum taLnk'})[-1].text.strip())

    # looks for a container with all the needed data
    
    for item in soup.findAll('div', {'class': '_1llCuDZj'}):
        
        # scrapes name, link, number of reviews, cooking and rating
        
        restaurant = item.find('a', {'class': '_15_ydu6b'})
        name = restaurant.text
        link = base + restaurant['href']
        name = name.split('.')[1].strip()
        
        # scrapes number of reviews, if none, saves 0
        
        try:
            reviews = item.find('span', {'class': 'w726Ki5B'}).text
            reviews = int(reviews.encode('ascii', 'ignore').decode('utf-8').split(' ')[0])
        except:
            reviews = 0
            
        # if a restaurant does not have specified type of cooking, we receive
        # information about its prices but we just omit it
            
        try:
            cooking = item.find('div', {'class': 'MIajtJFg _1cBs8huC _3d9EnJpt'}).span.text
            if '$' in cooking:
                cooking = ''
        except:
            cooking = ''
            
        # we look for rating and decode it with dictionary
            
        try:
            rating = item.find('span', {'class': '_141TBKA-'})
            rating = rating.span['class'][1]
            rating = rankReplace[rating]
        except:
            rating = ''
            
        # after extracting the data we append it to our list
            
        data_restaurants.append((name, cooking, rating, reviews, link))
        
        if DEBUG:
            print('Name: ', name)
            print('Cooking: ', cooking)
            print('Link: ', link)
            print('Rating: ', rating)
            print('Reviews: ', reviews)
            print()
    
    # we look for the next page, if it is not present we just save list to csv
    
    try:
        i += 1
        print(f'{i}/{pages}')
        nextPageUrl = soup.find('a', {'class': 'nav next rndBtn ui_button primary taLnk'})['href']
        nextPageUrl = base + nextPageUrl
        
        if DEBUG:
            print('Next page: ', nextPageUrl)
            
        get_restaurants(nextPageUrl, i, pages)
                    
    except:
        df = pd.DataFrame(data_restaurants, columns=['Name', 'Cooking', 'Rating', 'Reviews', 'Link'])
        df.to_csv('restaurants.csv', index=False, encoding='utf-8', sep='|')
        
    
def get_reviews(url, i=0, pages=0, name=''):
    soup = get_soup(url)
    
    # takes the number of total pages of reviews and the restaurants name
    
    if i == 0:
        try:
            pages = soup.find('a', {'class': 'pageNum last cx_brand_refresh_phase2'}).text
        except:
            pages = 1
        name = url.split('Reviews')[1][:-5]
        
    # scrapes reviews one by one, etracting rating and review text itself
    
    for item in soup.findAll('div', {'class': 'prw_rup prw_reviews_review_resp'}):
        number = item.find('div', {'class': 'reviewSelector'})['data-reviewid']
        rating = item.find('div', {'class': 'ui_column is-9'}).span['class'][1].split('_')[1]
        rating = int(rating)/10
        review = item.find('div', {'class': 'entry'}).p.text
        
        # if review is too long, we need to send Ajax post to receive whole text
        
        if 'Więcej' in review:
            headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
                    'Accept': 'text/html, */*',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'referer': f'{url}'
            }
            s = requests.Session()
            url2 = base + f'/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer=&contextChoice=DETAIL&reviews={number}'
            content = s.post(url2, headers=headers)
            try:
                soup2 = BeautifulSoup(content.content, 'lxml')
                review = soup2.find('div', {'class': 'entry'}).p.text
            except:
                review = content.text.split('<p class="partial_entry">')[1].split('</p>')[0]
        
        # appends each review to the list
        
        data_reviews.append((rating, review))
       
        if DEBUG:
            print('Rating: ', rating)
            print('Review: ', review)
            print()
            
    # we look for the next page, if it is not present we just save list to csv
            
    try:
        i += 1
        print(f'{i}/{pages}')
        nextPageUrl = soup.find('a', {'class': 'nav next ui_button primary cx_brand_refresh_phase2'})['href']
        nextPageUrl = base + nextPageUrl
        
        if DEBUG:
            print('Next page: ', nextPageUrl)
            
        get_reviews(nextPageUrl, i, pages, name)
                    
    except:
        df = pd.DataFrame(data_reviews, columns=['Rating', 'Review'])
        df.to_csv(f'reviews{name}.csv', index=False, encoding='utf-8', sep='|')

# set scraped website, debug state and ranks dictionary          
DEBUG = False
base = 'https://pl.tripadvisor.com'
url = base + '/Restaurants-g274837-Lodz_Lodz_Province_Central_Poland.html'
rankReplace = {'_2vB__cbb': 5.0,
        '_1RZqMyqR': 4.5,
        '_1-HtLqs3': 4.0,
        '_2n4wJlqY': 3.5,
        '_3RqovlMp': 3.0,
        '_2Icfy9b1': 2.5,
        '_36WMQ-A0': 2.0,
        '_2SkXD1ea': 1.5,
        '_1CSEqEVi': 1.0}
data_restaurants = []

# scrape restaurants
get_restaurants(url)

# read csv with restaurants and scrape reviews of each one
df = pd.read_csv('restaurants.csv', sep='|')

for url in tqdm(df.Link):
    data_reviews = []
    get_reviews(url)


