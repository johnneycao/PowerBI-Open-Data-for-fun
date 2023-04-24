---
title: Movie collections analysis
author: Johnney Cao
date updated: 2023-4-13
keyword: [IMDB, Plex API, parameter, web connector, Python, pandas, bs4, custom function, Image URL, Web URL, html color, table reference, conditional format]
---

# Analysis of Movie Collections from IMDB Top 250 and Plex - WIP

----------

[PBI Download Link](../_Asset%20Library/Source_Files/Movies.pbit)

----------

## Parameters

- **StarDate**: Required, Type as `Date`
- **X-Plex-Token**: Required, Type as `Text`
- **PlexServer**: Required, Type as `Text`

----------

## Custom Functions

### *1. Load Movie Content* Function

NOTE: it returns result from [Library Section](https://www.plexopedia.com/plex-media-server/api/library/movies/) List not Movie Metadata

#### Parameter

- **X-Plex-Token**: Required, token key to access Plex Server endpoints or XML
- **LibraryURL**: Required, Format like `[PLEX_URL]/library/sections/{key}/all?X-Plex-Token=[PLEX_TOKEN]` (can be copied from **Plex Libraries** Table below)

#### Steps

1. Retrieve library detail from **LibraryURL** Parameter
1. Expand **Video** into columns, and expand Video.Media and Video.Collection information

#### Power Query Sample Script
```css
let
    Source = (LibraryURL as any) => let
    Source = Xml.Tables(Web.Contents(LibraryURL)),
    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Attribute:size", Int64.Type}, {"Attribute:allowSync", Int64.Type}, {"Attribute:title1", type text}}),
    #"Removed Other Columns" = Table.SelectColumns(#"Changed Type",{"Video", "Attribute:librarySectionTitle"}),
    #"Reordered Columns" = Table.ReorderColumns(#"Removed Other Columns",{"Attribute:librarySectionTitle", "Video"}),
    #"Expanded Video" = Table.ExpandTableColumn(#"Reordered Columns", "Video", {"Media", "Attribute:key", "Attribute:studio", "Attribute:type", "Attribute:title", "Attribute:contentRating", "Attribute:summary", "Attribute:audienceRating", "Attribute:year", "Attribute:tagline", "Attribute:duration", "Attribute:originallyAvailableAt", "Attribute:addedAt", "Attribute:updatedAt", "Collection", "Attribute:viewCount", "Attribute:chapterSource", "Attribute:titleSort", "Attribute:originalTitle"}, {"Video.Media", "Video.Attribute:key", "Video.Attribute:studio", "Video.Attribute:type", "Video.Attribute:title", "Video.Attribute:contentRating", "Video.Attribute:summary", "Video.Attribute:audienceRating", "Video.Attribute:year", "Video.Attribute:tagline", "Video.Attribute:duration", "Video.Attribute:originallyAvailableAt", "Video.Attribute:addedAt", "Video.Attribute:updatedAt", "Video.Collection", "Video.Attribute:viewCount", "Video.Attribute:chapterSource", "Video.Attribute:titleSort", "Video.Attribute:originalTitle"}),
    #"Expanded Video.Media" = Table.ExpandTableColumn(#"Expanded Video", "Video.Media", {"Attribute:duration", "Attribute:bitrate", "Attribute:aspectRatio", "Attribute:audioChannels", "Attribute:audioCodec", "Attribute:videoCodec", "Attribute:videoResolution", "Attribute:videoFrameRate", "Attribute:audioProfile", "Attribute:videoProfile"}, {"Video.Media.Attribute:duration", "Video.Media.Attribute:bitrate", "Video.Media.Attribute:aspectRatio", "Video.Media.Attribute:audioChannels", "Video.Media.Attribute:audioCodec", "Video.Media.Attribute:videoCodec", "Video.Media.Attribute:videoResolution", "Video.Media.Attribute:videoFrameRate", "Video.Media.Attribute:audioProfile", "Video.Media.Attribute:videoProfile"}),
    #"Expanded Video.Collection" = Table.ExpandTableColumn(#"Expanded Video.Media", "Video.Collection", {"Attribute:tag"}, {"Video.Collection.Attribute:tag"}),
    #"Renamed Columns" = Table.RenameColumns(#"Expanded Video.Collection",{{"Attribute:librarySectionTitle", "Library"}, {"Video.Media.Attribute:duration", "Duration"}, {"Video.Media.Attribute:videoResolution", "Resolution"}, {"Video.Media.Attribute:videoFrameRate", "FrameRate"}, {"Video.Media.Attribute:audioProfile", "AudioProfile"}, {"Video.Media.Attribute:videoProfile", "VideoProfile"}, {"Video.Attribute:key", "key"}, {"Video.Attribute:studio", "Studio"}, {"Video.Attribute:type", "Type"}, {"Video.Attribute:title", "Title"}, {"Video.Attribute:contentRating", "ContentRating"}, {"Video.Attribute:summary", "Summary"}, {"Video.Attribute:audienceRating", "AudienceRating"}, {"Video.Attribute:year", "Year"}, {"Video.Attribute:tagline", "Tagline"}, {"Video.Attribute:duration", "IMDBduration"}, {"Video.Attribute:originallyAvailableAt", "OriginallyAvailableAt"}, {"Video.Collection.Attribute:tag", "Collection"}, {"Video.Attribute:titleSort", "TitleSort"}, {"Video.Attribute:originalTitle", "OriginalTitle"}, {"Video.Media.Attribute:bitrate", "Bitrate"}, {"Video.Media.Attribute:aspectRatio", "AspectRatio"}, {"Video.Media.Attribute:audioChannels", "AudioChannels"}, {"Video.Media.Attribute:audioCodec", "AudioCodec"}, {"Video.Media.Attribute:videoCodec", "VideoCodec"}, {"Video.Attribute:viewCount", "ViewCount"}}),
    #"Removed Columns" = Table.RemoveColumns(#"Renamed Columns",{"Video.Attribute:addedAt", "Video.Attribute:updatedAt", "Video.Attribute:chapterSource"}),
    #"Changed Type1" = Table.TransformColumnTypes(#"Removed Columns",{{"Library", type text}, {"Duration", Int64.Type}, {"Resolution", type text}, {"FrameRate", type text}, {"AudioProfile", type text}, {"VideoProfile", type text}, {"key", type text}, {"Studio", type text}, {"Type", type text}, {"Title", type text}, {"ContentRating", type text}, {"Summary", type text}, {"AudienceRating", type number}, {"Year", Int64.Type}, {"Tagline", type text}, {"IMDBduration", Int64.Type}, {"OriginallyAvailableAt", type date}, {"Collection", type text}, {"ViewCount", Int64.Type}, {"TitleSort", type text}, {"OriginalTitle", type text}})
in
    #"Changed Type1"
in
    Source
```

----------

## Data Tables

### 1 Basic Tables

#### Tables 

- **Date** Table

- **Year** Table

- **LastRefreshed** Table

### 2 *IMDB Top 250 List* Current Table

#### Data Sources
 [https://www.imdb.com/chart/top](https://www.imdb.com/chart/top)

*This data scraped from IMDB, and historical data can be found [here](https://www.imdb.com/user/ur48187336/lists).*

#### Steps
1. Use python code below to pull data from [IMDB Top 250 Site](https://www.imdb.com/chart/top);
    ```python
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
    
    # Send a GET request to the URL
    url = "https://www.imdb.com/chart/top"
    response = requests.get(url)
    
    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table with the data
    table = soup.find("tbody", class_="lister-list")
    
    # Create a list to store the data
    data = []
    
    # Loop through each row in the table
    for tr in table.find_all("tr"):
    
        # Find the title and original title
        title = tr.find("td", class_="titleColumn").a.get_text()
        
        # Find the Rank
        rank = tr.find("td", class_="titleColumn").get_text().split(".")[0]
    
        # Find the IMDB ID
        imdb_id = tr.find("td", class_="posterColumn").a["href"].split("/")[2]
        
        # Find the year
        year = tr.find("span", class_="secondaryInfo").get_text().strip("()")
        
        # Find the rating
        rating = tr.find("strong").get_text()
        
        # Find the image URL
        image_url = tr.find("td", class_="posterColumn").img["src"]
    
        # Add the data to the list
        data.append([rank, title, imdb_id, year, rating, image_url])
    
    # Convert the list to a pandas dataframe
    df = pd.DataFrame(data, columns=["Rank", "Title", "IMDB ID", "Year", "Rating", "Image URL"])
    
    # Return the dataframe as a table
    df
    
    ```
1. Change **Rank** and **Year** to *Whole Number* and **Rating** to *Decimal Number*;
1. Insert a merged column for **Year** and **Original Title**;
1. Add **IMDB URL** and setup Data category (Ribbon bar -> Format -> Data catagory = *Web URL*);
1. Setup Data category for **Image URL**  (Ribbon bar -> Format -> Data catagory = *Image URL*).

#### Power Query Sample Script
```css
let
    Source = Python.Execute("import requests#(lf)from bs4 import BeautifulSoup#(lf)import pandas as pd#(lf)#(lf)# Send a GET request to the URL#(lf)url = ""https://www.imdb.com/chart/top""#(lf)response = requests.get(url)#(lf)#(lf)# Use BeautifulSoup to parse the HTML#(lf)soup = BeautifulSoup(response.text, 'html.parser')#(lf)#(lf)# Find the table with the data#(lf)table = soup.find(""tbody"", class_=""lister-list"")#(lf)#(lf)# Create a list to store the data#(lf)data = []#(lf)#(lf)# Loop through each row in the table#(lf)for tr in table.find_all(""tr""):#(lf)#(lf)    # Find the title and original title#(lf)    title = tr.find(""td"", class_=""titleColumn"").a.get_text()#(lf)    #(lf)    # Find the Rank#(lf)    rank = tr.find(""td"", class_=""titleColumn"").get_text().split(""."")[0]#(lf)#(lf)    # Find the IMDB ID#(lf)    imdb_id = tr.find(""td"", class_=""posterColumn"").a[""href""].split(""/"")[2]#(lf)    #(lf)    # Find the year#(lf)    year = tr.find(""span"", class_=""secondaryInfo"").get_text().strip(""()"")#(lf)    #(lf)    # Find the rating#(lf)    rating = tr.find(""strong"").get_text()#(lf)    #(lf)    # Find the image URL#(lf)    image_url = tr.find(""td"", class_=""posterColumn"").img[""src""]#(lf)#(lf)    # Add the data to the list#(lf)    data.append([rank, title, imdb_id, year, rating, image_url])#(lf)#(lf)# Convert the list to a pandas dataframe#(lf)df = pd.DataFrame(data, columns=[""Rank"", ""Original Title"", ""IMDB ID"", ""Year"", ""Rating"", ""Image URL""])#(lf)#(lf)# Return the dataframe as a table#(lf)df"),
    df1 = Source{[Name="df"]}[Value],
    #"Changed Type" = Table.TransformColumnTypes(df1,{{"Year", Int64.Type}, {"Rating", type number}, {"Rank", Int64.Type}}),
    #"Inserted IMDB_URL" = Table.AddColumn(#"Changed Type", "IMDB URL", each Text.Combine({"https://www.imdb.com/title/", [IMDB ID]}), type text),
    #"Inserted Year_TItle" = Table.AddColumn(#"Inserted IMDB_URL", "Year Title", each Text.Combine({Text.From([Year], "en-US"), " / ", [Original Title]}), type text)
in
    #"Inserted Year_TItle"
```

### 3 *IMDB Top 250 Lists* - Historical Table (1996 to last year)

#### Data Sources
 [pollmaster's List](https://www.imdb.com/user/ur48187336/lists)

##### Steps
1. Run the Python Script to load the data
    1. From Pollmaster's list, find all the lists which start with **IMDb Top 250** and generate the URLs list
    1. Loop through URLs list and Run the *extract_movie_details* function to extract movie details
    ```python
    import pandas as pd
    import numpy as np
    import re
    import lxml
    from bs4 import BeautifulSoup
    from requests import get
    
    page = get('https://www.imdb.com/user/ur48187336/lists')
    soup = BeautifulSoup(page.content, 'lxml')
    content = soup.find(id="main")
    urls = pd.DataFrame()
    temp = pd.DataFrame()
    
    for i in range(len(content.find_all("a", class_="list-name"))):
        link = content.find_all("a", class_="list-name")[i].get('href')
        year = content.find_all("a", class_="list-name")[i].text
        inf = [year, link]
        temp = pd.DataFrame([inf], columns=['year', 'link'])
        urls = pd.concat([urls, temp], ignore_index=True)
    
    urls = urls[urls['year'].str.startswith('IMDb Top 250') == True]
    urls['year'] = urls['year'].apply(lambda x: 'IMDB_' + str(x[13:]))
    urls['link'] = urls['link'].apply(lambda x: 'https://www.imdb.com' + x)
    urls = urls.sort_values(['year']).reset_index(drop=True)
    urls['page2'] = urls['link'].apply(lambda x: x + "?page=2")
    urls['page3'] = urls['link'].apply(lambda x: x + "?page=3")
    
    # Define function to extract movie details from a single page
    def extract_movie_details(page_content):
        soup = BeautifulSoup(page_content, 'lxml')
        Frame = soup.find_all("div", class_ = "lister-item mode-detail")
        details_list = []
        for i in range(len(Frame)):
            ArticleTitle = soup.find("h1", class_ = "header").text.replace("\n","")
            FirstLine = Frame[i].find("h3", class_ = "lister-item-header")
            Ranking = FirstLine.find("span").text
            IMDBlink = FirstLine.find("a").get("href")
            Title = FirstLine.find("a").text
            Date = re.sub(r"[()]", "", FirstLine.find_all("span")[-1].text)
            RunTime = Frame[i].find("span", class_ = "runtime").text[:-4]
            Genre = Frame[i].find("span", class_ = "genre").text.rstrip().replace("\n", "")
            Rating = Frame[i].find("span", class_ = "ipl-rating-star__rating").text
            try:
                Score = Frame[i].find("span", class_ = "metascore favorable").text.rstrip()
            except:
                Score = None
            Votes = Frame[i].find_all("p", class_ = "text-muted")[-1].text.lstrip().replace('\n', '').split('|')[0][6:]
            try:
                Gross = Frame[i].find_all("p", class_ = "text-muted")[-1].text.lstrip().replace('\n', '').split('|')[1][7:]
            except:
                Gross = None
            a = Frame[i].find_all("p", class_ = "text-muted text-small")[1].text.split('|')
            Director = a[0].strip().replace('\n', ' ')
            Cast = a[1].strip().replace('\n', ' ')
            details = [ArticleTitle, Ranking, IMDBlink, Title, Date, RunTime, Genre, Rating, Score, Votes, Gross, Director, Cast]
            details_list.append(details)
        return details_list
    
    # Loop through URLs and extract movie details
    details_list = []
    for i in range(len(urls)):
        # Load page 1
        page = get(urls.loc[i, 'link'])
        details_list.extend(extract_movie_details(page.content))
        # Load page 2
        page = get(urls.loc[i, 'page2'])
        details_list.extend(extract_movie_details(page.content))
        # Load page 3
        page = get(urls.loc[i, 'page3'])
        details_list.extend(extract_movie_details(page.content))
    
    # Convert details to DataFrame
    columns=["IMDByear", "Ranking", "IMDBlink", "Title", "Date", "RunTime", "Genre", "Rating", "Score", "Votes", "Gross", "Director", "Cast"]
    details_df = pd.DataFrame(details_list, columns=columns)
    
    # Add year to details_df
    details_df['IMDByear'] = details_df['IMDByear'].apply(lambda x: 'IMDB_' + str(x[13:]))    
    ```
1. Add custom fields for **RankingGroup**, **IMDB_ID** and **IMDB_URL**

#### Power Query Sample Script
```css
let
    Source = Python.Execute("import pandas as pd#(lf)import numpy as np#(lf)import re#(lf)import lxml#(lf)from bs4 import BeautifulSoup#(lf)from requests import get#(lf)#(lf)page = get('https://www.imdb.com/user/ur48187336/lists')#(lf)soup = BeautifulSoup(page.content, 'lxml')#(lf)content = soup.find(id=""main"")#(lf)urls = pd.DataFrame()#(lf)temp = pd.DataFrame()#(lf)#(lf)for i in range(len(content.find_all(""a"", class_=""list-name""))):#(lf)    link = content.find_all(""a"", class_=""list-name"")[i].get('href')#(lf)    year = content.find_all(""a"", class_=""list-name"")[i].text#(lf)    inf = [year, link]#(lf)    temp = pd.DataFrame([inf], columns=['year', 'link'])#(lf)    urls = pd.concat([urls, temp], ignore_index=True)#(lf)#(lf)urls = urls[urls['year'].str.startswith('IMDb Top 250') == True]#(lf)urls['year'] = urls['year'].apply(lambda x: 'IMDB_' + str(x[13:]))#(lf)urls['link'] = urls['link'].apply(lambda x: 'https://www.imdb.com' + x)#(lf)urls = urls.sort_values(['year']).reset_index(drop=True)#(lf)urls['page2'] = urls['link'].apply(lambda x: x + ""?page=2"")#(lf)urls['page3'] = urls['link'].apply(lambda x: x + ""?page=3"")#(lf)#(lf)# Define function to extract movie details from a single page#(lf)def extract_movie_details(page_content):#(lf)    soup = BeautifulSoup(page_content, 'lxml')#(lf)    Frame = soup.find_all(""div"", class_ = ""lister-item mode-detail"")#(lf)    details_list = []#(lf)    for i in range(len(Frame)):#(lf)        ArticleTitle = soup.find(""h1"", class_ = ""header"").text.replace(""\n"","""")#(lf)        FirstLine = Frame[i].find(""h3"", class_ = ""lister-item-header"")#(lf)        Ranking = FirstLine.find(""span"").text#(lf)        IMDBlink = FirstLine.find(""a"").get(""href"")#(lf)        Title = FirstLine.find(""a"").text#(lf)        Date = re.sub(r""[()]"", """", FirstLine.find_all(""span"")[-1].text)#(lf)        RunTime = Frame[i].find(""span"", class_ = ""runtime"").text[:-4]#(lf)        Genre = Frame[i].find(""span"", class_ = ""genre"").text.rstrip().replace(""\n"", """")#(lf)        Rating = Frame[i].find(""span"", class_ = ""ipl-rating-star__rating"").text#(lf)        try:#(lf)            Score = Frame[i].find(""span"", class_ = ""metascore favorable"").text.rstrip()#(lf)        except:#(lf)            Score = None#(lf)        Votes = Frame[i].find_all(""p"", class_ = ""text-muted"")[-1].text.lstrip().replace('\n', '').split('|')[0][6:]#(lf)        try:#(lf)            Gross = Frame[i].find_all(""p"", class_ = ""text-muted"")[-1].text.lstrip().replace('\n', '').split('|')[1][7:]#(lf)        except:#(lf)            Gross = None#(lf)        a = Frame[i].find_all(""p"", class_ = ""text-muted text-small"")[1].text.split('|')#(lf)        Director = a[0].strip().replace('\n', ' ')#(lf)        Cast = a[1].strip().replace('\n', ' ')#(lf)        details = [ArticleTitle, Ranking, IMDBlink, Title, Date, RunTime, Genre, Rating, Score, Votes, Gross, Director, Cast]#(lf)        details_list.append(details)#(lf)    return details_list#(lf)#(lf)# Loop through URLs and extract movie details#(lf)details_list = []#(lf)for i in range(len(urls)):#(lf)    # Load page 1#(lf)    page = get(urls.loc[i, 'link'])#(lf)    details_list.extend(extract_movie_details(page.content))#(lf)    # Load page 2#(lf)    page = get(urls.loc[i, 'page2'])#(lf)    details_list.extend(extract_movie_details(page.content))#(lf)    # Load page 3#(lf)    page = get(urls.loc[i, 'page3'])#(lf)    details_list.extend(extract_movie_details(page.content))#(lf)#(lf)# Convert details to DataFrame#(lf)columns=[""IMDByear"", ""Ranking"", ""IMDBlink"", ""Title"", ""Date"", ""RunTime"", ""Genre"", ""Rating"", ""Score"", ""Votes"", ""Gross"", ""Director"", ""Cast""]#(lf)details_df = pd.DataFrame(details_list, columns=columns)#(lf)#(lf)# Add year to details_df#(lf)details_df['IMDByear'] = details_df['IMDByear'].apply(lambda x: 'imdb_' + str(x[13:]))"),
    details_df = Source{[Name="details_df"]}[Value],
    #"Changed Type" = Table.TransformColumnTypes(details_df,{{"IMDByear", type text}, {"Ranking", Int64.Type}, {"IMDBlink", type text}, {"Title", type text}, {"Date", type text}, {"RunTime", Int64.Type}, {"Genre", type text}, {"Rating", type number}, {"Score", Int64.Type}, {"Votes", Int64.Type}, {"Gross", type text}, {"Director", type text}, {"Cast", type text}}),
    #"Added RankingGroup" = Table.AddColumn(#"Changed Type", "RankingGroup", each if [Ranking] < 50 then 1 else if [Ranking] <100 then 2 else if [Ranking] < 150 then 3 else if [Ranking] < 200 then 4 else 5),
    #"Changed RankingGroup Type" = Table.TransformColumnTypes(#"Added RankingGroup",{{"RankingGroup", Int64.Type}}),
    #"Add IMDB_ID" = Table.AddColumn(#"Changed RankingGroup Type", "IMDB_ID", each Text.BetweenDelimiters([IMDBlink], "/", "/", 1, 0), type text),
    Add_IMDB_URL = Table.AddColumn(#"Add IMDB_ID", "IMDB_URL", each Text.Combine({"https://www.imdb.com", [IMDBlink]}), type text),
    #"Sorted Rows" = Table.Sort(Add_IMDB_URL,{{"IMDByear", Order.Descending}})
in
    #"Sorted Rows"
```

### 4 *Oscar Hightlights List* - Table

#### Data Sources
 [pollmaster's List](https://www.imdb.com/user/ur48187336/lists)

##### Steps
1. Run the Python Script to load the data
    1. From Pollmaster's list, find all the lists which start with **Oscar Highlights** and generate the URLs list
    1. Loop through URLs list and Run the *extract_movie_details* function to extract movie details
    ```python
    import pandas as pd
    import numpy as np
    import re
    import lxml
    from bs4 import BeautifulSoup
    from requests import get
    
    page = get('https://www.imdb.com/user/ur48187336/lists')
    soup = BeautifulSoup(page.content, 'lxml')
    content = soup.find(id="main")
    urls = pd.DataFrame()
    temp = pd.DataFrame()
    
    for i in range(len(content.find_all("a", class_="list-name"))):
        link = content.find_all("a", class_="list-name")[i].get('href')
        year = content.find_all("a", class_="list-name")[i].text
        inf = [year, link]
        temp = pd.DataFrame([inf], columns=['year', 'link'])
        urls = pd.concat([urls, temp], ignore_index=True)
    
    urls = urls[urls['year'].str.startswith('Oscar Highlights') == True]
    urls['year'] = urls['year'].apply(lambda x: str(x[16:]))
    urls['link'] = urls['link'].apply(lambda x: 'https://www.imdb.com' + x)
    urls = urls.sort_values(['year']).reset_index(drop=True)
    urls['page2'] = urls['link'].apply(lambda x: x + "?page=2")
    urls['page3'] = urls['link'].apply(lambda x: x + "?page=3")
    
    # Define function to extract movie details from a single page
    def extract_movie_details(page_content):
        soup = BeautifulSoup(page_content, 'lxml')
        Frame = soup.find_all("div", class_ = "lister-item mode-detail")
        details_list = []
        for i in range(len(Frame)):
            ArticleTitle = soup.find("h1", class_ = "header").text.replace("\n","")
            FirstLine = Frame[i].find("h3", class_ = "lister-item-header")
            Ranking = FirstLine.find("span").text
            IMDBlink = FirstLine.find("a").get("href")
            Title = FirstLine.find("a").text
            Date = re.sub(r"[()]", "", FirstLine.find_all("span")[-1].text)
            RunTime = Frame[i].find("span", class_ = "runtime").text[:-4]
            Genre = Frame[i].find("span", class_ = "genre").text.rstrip().replace("\n", "")
            Rating = Frame[i].find("span", class_ = "ipl-rating-star__rating").text
            try:
                Score = Frame[i].find("span", class_ = "metascore favorable").text.rstrip()
            except:
                Score = None
            Votes = Frame[i].find_all("p", class_ = "text-muted")[-1].text.lstrip().replace('\n', '').split('|')[0][6:]
            try:
                Gross = Frame[i].find_all("p", class_ = "text-muted")[-1].text.lstrip().replace('\n', '').split('|')[1][7:]
            except:
                Gross = None
            a = Frame[i].find_all("p", class_ = "text-muted text-small")[1].text.split('|')
            Director = a[0].strip().replace('\n', ' ')
            Cast = a[1].strip().replace('\n', ' ')
            details = [ArticleTitle, Ranking, IMDBlink, Title, Date, RunTime, Genre, Rating, Score, Votes, Gross, Director, Cast]
            details_list.append(details)
        return details_list
    
    # Loop through URLs and extract movie details
    details_list = []
    for i in range(len(urls)):
        # Load page 1
        page = get(urls.loc[i, 'link'])
        details_list.extend(extract_movie_details(page.content))
        # Load page 2
        page = get(urls.loc[i, 'page2'])
        details_list.extend(extract_movie_details(page.content))
        # Load page 3
        page = get(urls.loc[i, 'page3'])
        details_list.extend(extract_movie_details(page.content))
    
    # Convert details to DataFrame
    columns=["HighlightYear", "Ranking", "IMDBlink", "Title", "Date", "RunTime", "Genre", "Rating", "Score", "Votes", "Gross", "Director", "Cast"]
    details_df = pd.DataFrame(details_list, columns=columns)
    
    # Add year to details_df
    details_df['HighlightYear'] = details_df['HighlightYear'].apply(lambda x: str(x[16:]))
    ```
1. Add custom fields for **IMDB_ID** and **IMDB_URL**

#### Power Query Sample Script
```css
let
    Source = Python.Execute("import pandas as pd#(lf)import numpy as np#(lf)import re#(lf)import lxml#(lf)from bs4 import BeautifulSoup#(lf)from requests import get#(lf)#(lf)page = get('https://www.imdb.com/user/ur48187336/lists')#(lf)soup = BeautifulSoup(page.content, 'lxml')#(lf)content = soup.find(id=""main"")#(lf)urls = pd.DataFrame()#(lf)temp = pd.DataFrame()#(lf)#(lf)for i in range(len(content.find_all(""a"", class_=""list-name""))):#(lf)    link = content.find_all(""a"", class_=""list-name"")[i].get('href')#(lf)    year = content.find_all(""a"", class_=""list-name"")[i].text#(lf)    inf = [year, link]#(lf)    temp = pd.DataFrame([inf], columns=['year', 'link'])#(lf)    urls = pd.concat([urls, temp], ignore_index=True)#(lf)#(lf)urls = urls[urls['year'].str.startswith('IMDb Top 250') == True]#(lf)urls['year'] = urls['year'].apply(lambda x: 'IMDB_' + str(x[13:]))#(lf)urls['link'] = urls['link'].apply(lambda x: 'https://www.imdb.com' + x)#(lf)urls = urls.sort_values(['year']).reset_index(drop=True)#(lf)urls['page2'] = urls['link'].apply(lambda x: x + ""?page=2"")#(lf)urls['page3'] = urls['link'].apply(lambda x: x + ""?page=3"")#(lf)#(lf)# Define function to extract movie details from a single page#(lf)def extract_movie_details(page_content):#(lf)    soup = BeautifulSoup(page_content, 'lxml')#(lf)    Frame = soup.find_all(""div"", class_ = ""lister-item mode-detail"")#(lf)    details_list = []#(lf)    for i in range(len(Frame)):#(lf)        ArticleTitle = soup.find(""h1"", class_ = ""header"").text.replace(""\n"","""")#(lf)        FirstLine = Frame[i].find(""h3"", class_ = ""lister-item-header"")#(lf)        Ranking = FirstLine.find(""span"").text#(lf)        IMDBlink = FirstLine.find(""a"").get(""href"")#(lf)        Title = FirstLine.find(""a"").text#(lf)        Date = re.sub(r""[()]"", """", FirstLine.find_all(""span"")[-1].text)#(lf)        RunTime = Frame[i].find(""span"", class_ = ""runtime"").text[:-4]#(lf)        Genre = Frame[i].find(""span"", class_ = ""genre"").text.rstrip().replace(""\n"", """")#(lf)        Rating = Frame[i].find(""span"", class_ = ""ipl-rating-star__rating"").text#(lf)        try:#(lf)            Score = Frame[i].find(""span"", class_ = ""metascore favorable"").text.rstrip()#(lf)        except:#(lf)            Score = None#(lf)        Votes = Frame[i].find_all(""p"", class_ = ""text-muted"")[-1].text.lstrip().replace('\n', '').split('|')[0][6:]#(lf)        try:#(lf)            Gross = Frame[i].find_all(""p"", class_ = ""text-muted"")[-1].text.lstrip().replace('\n', '').split('|')[1][7:]#(lf)        except:#(lf)            Gross = None#(lf)        a = Frame[i].find_all(""p"", class_ = ""text-muted text-small"")[1].text.split('|')#(lf)        Director = a[0].strip().replace('\n', ' ')#(lf)        Cast = a[1].strip().replace('\n', ' ')#(lf)        details = [ArticleTitle, Ranking, IMDBlink, Title, Date, RunTime, Genre, Rating, Score, Votes, Gross, Director, Cast]#(lf)        details_list.append(details)#(lf)    return details_list#(lf)#(lf)# Loop through URLs and extract movie details#(lf)details_list = []#(lf)for i in range(len(urls)):#(lf)    # Load page 1#(lf)    page = get(urls.loc[i, 'link'])#(lf)    details_list.extend(extract_movie_details(page.content))#(lf)    # Load page 2#(lf)    page = get(urls.loc[i, 'page2'])#(lf)    details_list.extend(extract_movie_details(page.content))#(lf)    # Load page 3#(lf)    page = get(urls.loc[i, 'page3'])#(lf)    details_list.extend(extract_movie_details(page.content))#(lf)#(lf)# Convert details to DataFrame#(lf)columns=[""IMDByear"", ""Ranking"", ""IMDBlink"", ""Title"", ""Date"", ""RunTime"", ""Genre"", ""Rating"", ""Score"", ""Votes"", ""Gross"", ""Director"", ""Cast""]#(lf)details_df = pd.DataFrame(details_list, columns=columns)#(lf)#(lf)# Add year to details_df#(lf)details_df['IMDByear'] = details_df['IMDByear'].apply(lambda x: 'imdb_' + str(x[13:]))"),
    details_df = Source{[Name="details_df"]}[Value],
    #"Changed Type" = Table.TransformColumnTypes(details_df,{{"IMDByear", type text}, {"Ranking", Int64.Type}, {"IMDBlink", type text}, {"Title", type text}, {"Date", type text}, {"RunTime", Int64.Type}, {"Genre", type text}, {"Rating", type number}, {"Score", Int64.Type}, {"Votes", Int64.Type}, {"Gross", type text}, {"Director", type text}, {"Cast", type text}}),
    #"Added RankingGroup" = Table.AddColumn(#"Changed Type", "RankingGroup", each if [Ranking] < 50 then 1 else if [Ranking] <100 then 2 else if [Ranking] < 150 then 3 else if [Ranking] < 200 then 4 else 5),
    #"Changed RankingGroup Type" = Table.TransformColumnTypes(#"Added RankingGroup",{{"RankingGroup", Int64.Type}}),
    #"Add IMDB_ID" = Table.AddColumn(#"Changed RankingGroup Type", "IMDB_ID", each Text.BetweenDelimiters([IMDBlink], "/", "/", 1, 0), type text),
    Add_IMDB_URL = Table.AddColumn(#"Add IMDB_ID", "IMDB_URL", each Text.Combine({"https://www.imdb.com", [IMDBlink]}), type text),
    #"Sorted Rows" = Table.Sort(Add_IMDB_URL,{{"IMDByear", Order.Descending}})
in
    #"Sorted Rows"
```

### 5 *Plex Libraries* Table

##### Parameter

- **X-Plex-Token**: [Finding an authentication token / X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) 

- **PlexServer**: Plex Server IP Address with Port Number e.g., `http://your_ip_address:32400` or `https://your_ip_address:32400`

#### Steps
1. Combine IP and X-Plex-Token into a Plex Libraries List URL, and retrive all libraries ('**Directory**');
    >Xml.Tables(Web.Contents(Text.Combine({PlexServer,"/library/sections?X-Plex-Token=",#"X-Plex-Token"})))
1. Drill down *Directory* into a table;
1. Expand *Location* to Folder Path;
1. Combine IP and X-Plex-Token into Plex Content Library URL;
    >Uri.Combine(Text.Combine({IP,":32400/"}) as text, Text.Combine({"library/sections/",Text.From([#"Attribute:key"]),"/all?X-Plex-Token=",#"X-Plex-Token"}) as text)
1. Split Location into columns and Parse as SMB format

#### Power Query Sample Script
```css
let
    Source = Xml.Tables(Web.Contents(Text.Combine({PlexServer,"/library/sections?X-Plex-Token=",#"X-Plex-Token"}))),
    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Attribute:size", Int64.Type}, {"Attribute:allowSync", Int64.Type}, {"Attribute:title1", type text}}),
    Directory = #"Changed Type"{0}[Directory],
    #"Removed Other Columns" = Table.SelectColumns(Directory,{"Location", "Attribute:art", "Attribute:composite", "Attribute:key", "Attribute:type", "Attribute:title", "Attribute:agent", "Attribute:scanner", "Attribute:language", "Attribute:hidden"}),
    #"Expanded Location" = Table.ExpandTableColumn(#"Removed Other Columns", "Location", {"Attribute:path"}, {"Location.Attribute:path"}),
    #"Added Custom" = Table.AddColumn(#"Expanded Location", "URL", each Uri.Combine(
    Text.Combine({IP,":32400/"}) as text,
    Text.Combine({"library/sections/",Text.From([#"Attribute:key"]),"/all?X-Plex-Token=",#"X-Plex-Token"}) as text)
as text),
    #"Reordered Columns" = Table.ReorderColumns(#"Added Custom",{"Attribute:art", "Attribute:key", "Attribute:type", "Attribute:title", "Attribute:agent", "Attribute:scanner", "Attribute:language", "Attribute:hidden", "Location.Attribute:path", "URL"}),
    #"Split Column by Delimiter" = Table.SplitColumn(#"Reordered Columns", "Location.Attribute:path", Splitter.SplitTextByDelimiter("/", QuoteStyle.Csv), {"Location.Attribute:path.1", "Location.Attribute:path.2", "Location.Attribute:path.3", "Location.Attribute:path.4", "Location.Attribute:path.5", "Location.Attribute:path.6"}),
    #"Added Folder Column" = Table.AddColumn(#"Split Column by Delimiter", "Folder", each Text.From("\\") & IP & Text.From("\") & Text.Combine({[#"Location.Attribute:path.4"],[#"Location.Attribute:path.5"],[#"Location.Attribute:path.6"]},"\")),
    #"Removed Columns" = Table.RemoveColumns(#"Added Folder Column",{"Location.Attribute:path.1", "Location.Attribute:path.2", "Location.Attribute:path.3", "Location.Attribute:path.4", "Location.Attribute:path.5", "Location.Attribute:path.6", "Attribute:art"}),
    #"Renamed Columns" = Table.RenameColumns(#"Removed Columns",{{"Attribute:key", "Key"}, {"Attribute:type", "Type"}, {"Attribute:title", "Library"}, {"Attribute:agent", "Agent"}, {"Attribute:scanner", "Scanner"}, {"Attribute:language", "Language"}, {"Attribute:hidden", "Hidden"}})
in
    #"Renamed Columns"
```

### 4 *Plex Movies Content* Table

#### Dependency

- **Plex Libraries** Table

- **Load Movie Content** Custom Function

#### Steps
1. Reference from **Plex Libraries** Table above;
1. Filter **Type** = '*movie*' and **Scanner** = '*Plex Movie*';
1. Invoke **Load Movie Content** Function from Library *URL* field;
1. Add **Runtime** column and calculate base on *Duration* field, and format result into HH:MM:SS format by removing *Date* and *AM*;

    >Text.From(#datetime(1970, 1, 1, 0, 0, 0) + #duration(0, 0, 0, [Duration]/1000))
1. Combine IP, Item Key and X-Plex-Token into **MetadatURL**;

    >Table.AddColumn(#"Trimmed Text", "MetadataURL", each Text.Combine({"http://",IP,":32400", [key], "?X-Plex-Token=",#"X-Plex-Token"}), type text)

----------

## Relationship

----------

## Reports

----------

## Reference

### Power Query Reference
- [Learn more about Power Query functions](https://docs.microsoft.com/powerquery-m/understanding-power-query-m-functions)
- [Fuzzy Matching](https://learn.microsoft.com/en-us/power-query/fuzzy-matching)


### Plex API
- [Finding an authentication token / X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
- [Plex Media Server API Documentation](https://www.plexopedia.com/plex-media-server/api/)
- [Plex Media Server URL Command](https://support.plex.tv/articles/201638786-plex-media-server-url-commands/)
 
    - List Base Server Capabilities: http://[*IP*]:32400/?X-Plex-Token=[*X-Plex-Token*]
    - List Defined Libraries: http://[*IP*]:32400/library/sections/?X-Plex-Token=[*X-Plex-Token*]
    - List Library Contents: http://[*IP*]:32400/library/sections/[*Movies Library ID*]/all?X-Plex-Token=[*X-Plex-Token*]
    - List Detail of an Item: http://[*IP*]:32400/library/metadata/[*Item Key ID*]?X-Plex-Token=[*X-Plex-Token*]