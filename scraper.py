# import json
# import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
from tqdm import tqdm

def get_soup(url):
    return BeautifulSoup(requests.get(url).content, 'lxml')

def get_restaurants(url, i=0, pages=0):
    soup = get_soup(url)
    if i == 0:
        pages = int(soup.findAll('a', {'class': 'pageNum taLnk'})[-1].text.strip())

    for item in soup.findAll('div', {'class': '_1llCuDZj'}):
        restaurant = item.find('a', {'class': '_15_ydu6b'})
        name = restaurant.text
        link = base + restaurant['href']
        name = name.split('.')[1].strip()
        try:
            reviews = item.find('span', {'class': 'w726Ki5B'}).text
            reviews = int(reviews.encode('ascii', 'ignore').decode('utf-8').split(' ')[0])
        except:
            reviews = 0
        try:
            cooking = item.find('div', {'class': 'MIajtJFg _1cBs8huC _3d9EnJpt'}).span.text
            if '$' in cooking:
                cooking = ''
        except:
            cooking = ''
        try:
            rating = item.find('span', {'class': '_141TBKA-'})
            rating = rating.span['class'][1]
            rating = rankReplace[rating]
        except:
            rating = ''
            
        data_restaurants.append((name, cooking, rating, reviews, link))
        
        if DEBUG:
            print('Name: ', name)
            print('Cooking: ', cooking)
            print('Link: ', link)
            print('Rating: ', rating)
            print('Reviews: ', reviews)
            print()
    
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
        df.to_csv('restaurants.csv', index=False, encoding='utf-8')
        
    
def get_reviews(url, i=0, pages=0, name=''):
    soup = get_soup(url)
    if i == 0:
        pages = soup.find('a', {'class': 'pageNum last cx_brand_refresh_phase2'}).text
        name = url.split('Reviews')[1][:-5]
    
    for item in soup.findAll('div', {'class': 'prw_rup prw_reviews_review_resp'}):
        number = item.find('div', {'class': 'reviewSelector'})['data-reviewid']
        rating = item.find('div', {'class': 'ui_column is-9'}).span['class'][1].split('_')[1]
        rating = int(rating)/10
        review = item.find('div', {'class': 'entry'}).p.text
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
        
        data_reviews.append((rating, review))
       
        if DEBUG:
            print('Rating: ', rating)
            print('Review: ', review)
            print()
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
        df.to_csv(f'reviews{name}.csv', index=False, encoding='utf-8')
           
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
data_reviews = []
get_restaurants(url)
df = pd.read_csv('restaurants.csv')
for url in tqdm(df.Link):
    get_reviews(url)


