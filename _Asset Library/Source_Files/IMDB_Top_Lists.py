from bs4 import BeautifulSoup
from requests import get
import pandas as pd
import re

page = get('https://www.imdb.com/user/ur48187336/lists')
soup = BeautifulSoup(page.content, 'html.parser')  # Changed parser to 'html.parser'
content = soup.find(id="main")
urls = pd.DataFrame()
temp = pd.DataFrame()

for i in range(len(content.find_all("a", class_="list-name"))):
    link = content.find_all("a", class_="list-name")[i].get('href')
    list_name = content.find_all("a", class_="list-name")[i].text
    inf = [list_name, link]
    temp = pd.DataFrame([inf], columns=['list_name', 'link'])
    urls = pd.concat([urls, temp], ignore_index=True)

imdb_urls = urls[urls['list_name'].str.startswith('IMDb Top 250')]
oscar_urls = urls[urls['list_name'].str.startswith('Oscar Highlights')]

def process_urls(urls, list_prefix):
    new_urls = urls.copy()
    new_urls['year'] = new_urls['list_name'].apply(lambda x: list_prefix + str(x[len(list_prefix):]))  # Fixed indexing
    new_urls['link'] = new_urls['link'].apply(lambda x: 'https://www.imdb.com' + x)
    new_urls = new_urls.sort_values(['year']).reset_index(drop=True)
    new_urls['page2'] = new_urls['link'].apply(lambda x: x + "?page=2")
    new_urls['page3'] = new_urls['link'].apply(lambda x: x + "?page=3")
    return new_urls

imdb_urls = process_urls(imdb_urls, 'IMDb Top 250')
oscar_urls = process_urls(oscar_urls, 'Oscar Highlights')

all_urls = pd.concat([imdb_urls, oscar_urls], ignore_index=True)

# Define function to extract movie details from a single page
def extract_movie_details(page_content, ListYear):
    soup = BeautifulSoup(page_content, 'html.parser')
    Frame = soup.find_all("div", class_="lister-item mode-detail")
    details_list = []
    
    for i in range(len(Frame)):
        ArticleTitle = soup.find("h1", class_="header").text.replace("\n", "")
        FirstLine = Frame[i].find("h3", class_="lister-item-header")
        Ranking = int(FirstLine.find("span").text.replace('.', ''))
        IMDBlink = "https://www.imdb.com" + FirstLine.find("a").get("href")
        Title = FirstLine.find("a").text
        Date = re.sub(r"[()]", "", FirstLine.find_all("span")[-1].text)
        
        try:
            Certificate = Frame[i].find("span", class_="certificate").text
        except:
            Certificate = None
            
        RunTime = Frame[i].find("span", class_="runtime").text[:-4]
        Genre = Frame[i].find("span", class_="genre").text.rstrip().replace("\n", "")
        Rating = Frame[i].find("span", class_="ipl-rating-star__rating").text
        
        try:
            Score = Frame[i].find("span", class_="metascore").text.rstrip()
        except:
            Score = None
            
        Votes = Frame[i].find_all("span", attrs={"name": "nv"})[0].text
        
        try:
            Gross = Frame[i].find_all("span", attrs={"name": "nv"})[1].text
        except:
            Gross = None
            
        a = Frame[i].find_all("p", class_="text-muted text-small")[1].text.split('|')
        Director = a[0].strip().replace('\n', ' ').replace('Director: ', '').replace('Directors: ', '')
        Cast = a[1].strip().replace('\n', ' ').replace('Star: ', '').replace('Stars: ', '')

        ImageLink = Frame[i].find("img", class_="loadlate")["src"]
        
        details = [ArticleTitle, ListYear, Ranking, IMDBlink, Title, Date, Certificate, RunTime, Genre, Rating, Score, Votes, Gross, Director, Cast, ImageLink]
        details_list.append(details)
        
    return details_list

# Loop through URLs and extract movie details
details_list = []
for i in range(len(all_urls)):
    list_name = all_urls.loc[i, 'list_name']
    ListYear = list_name.replace('IMDb Top 250 ', '').replace('Oscar Highlights ', '')
    # Load page 1
    page = get(all_urls.loc[i, 'link'])
    details_list.extend(extract_movie_details(page.content, ListYear))
    
    # Load page 2
    page = get(all_urls.loc[i, 'page2'])
    details_list.extend(extract_movie_details(page.content, ListYear))
    
    # Load page 3
    page = get(all_urls.loc[i, 'page3'])
    details_list.extend(extract_movie_details(page.content, ListYear))

# Convert details to DataFrame
columns=["List Name", "List Year", "Ranking", "IMDB URL", "Title", "Year", "Certificate", "RunTime", "Genre", "Rating", "Score", "Votes", "Gross", "Director", "Cast", "Image URL"]
details_df = pd.DataFrame(details_list, columns=columns)