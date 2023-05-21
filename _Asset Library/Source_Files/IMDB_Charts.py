import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape the data from a given URL and list name
def scrape_data(url, list_name):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find("tbody", class_="lister-list")
    data = []

    for tr in table.find_all("tr"):
        title = tr.find("td", class_="titleColumn").a.get_text()
        rank = tr.find("td", class_="titleColumn").get_text().split(".")[0]
        imdb_id = tr.find("td", class_="posterColumn").a["href"].split("/")[2]
        year = tr.find("span", class_="secondaryInfo").get_text().strip("()")
        try:
            rating = tr.find("strong").get_text()
        except AttributeError:
            rating = None
        image_url = tr.find("td", class_="posterColumn").img["src"]

        # Fetch additional attributes
        attributes = tr.find_all("span")
        rank_attribute = None
        imdb_rating_attribute = None
        user_votes_attribute = None
        num_votes_attribute = None
        user_rating_attribute = None

        for attribute in attributes:
            attribute_name = attribute.get("name")
            if attribute_name == "rk":
                rank_attribute = attribute.get("data-value")
            elif attribute_name == "ir":
                imdb_rating_attribute = attribute.get("data-value")
            elif attribute_name == "us":
                user_votes_attribute = attribute.get("data-value")
            elif attribute_name == "nv":
                num_votes_attribute = attribute.get("data-value")
            elif attribute_name == "ur":
                user_rating_attribute = attribute.get("data-value")

        data.append([rank,title,imdb_id,year,rating,image_url,list_name,rank_attribute,imdb_rating_attribute,user_votes_attribute,num_votes_attribute,user_rating_attribute])

    return data

# Main code
data = []

# Scrape data from IMDB Top 250
data.extend(scrape_data("https://www.imdb.com/chart/top", "IMDB Top 250"))

# Scrape data from Most Popular
data.extend(scrape_data("https://www.imdb.com/chart/moviemeter/", "Most Popular"))

# Scrape data from Most Top Rated English Movies
data.extend(scrape_data("https://www.imdb.com/chart/top-english-movies", "Most Top Rated English Movies"))

# Convert the list to a pandas dataframe
df = pd.DataFrame(data, columns=[
    "Rank","Title","IMDB ID","Year","Rating","Image URL","List Name","Rank Attribute","IMDB Rating Attribute","User Votes Attribute","Number of Votes Attribute","User Rating Attribute"])
