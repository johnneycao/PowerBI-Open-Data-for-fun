---
title: Movie collections analysis
author: Johnney Cao
date updated: 2023-2-5
keyword: [IMDB, Plex API, parameter, web connector, Python, pandas, bs4, custom function, Image URL, Web URL, html color, table reference, conditional format]
---

# Analysis of Movie Collections from IMDB Top 250 and Plex - WIP

----------

[PBI Download Link](../_Asset%20Library/Source_Files/Movies.pbit)

----------

## Parameters

- **StarDate**: Required, Type as *Date*
- **X-Plex-Token**: Required, Type as *Text*
- **IP**: Required, Type as *Text*
- **LibraryURL**: Required, Type as *Text*

----------

## Custom Function

### *1. Load Movie Content* Function

#### Parameter

- **LibraryURL**: Format like http://[*IP*]:32400/library/sections/[*Movies Library ID*]/all?X-Plex-Token=[*X-Plex-Token*] (result copied from **Plex Libraries** Table below)

#### Steps

1. Retrieve library detail from LibraryURL
1. Expand Video into columns, and expand Video.Media and Video.Collection information

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

### 2 *IMDB Top 250 List* Table

#### Data Sources
> [https://www.imdb.com/chart/top](https://www.imdb.com/chart/top)

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
1. Insert a merged column for **Year** and *Original Title**;
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

### 2 *IMDB Top 250 List* Table - Alternative

#### Data Sources
> [Kaggle Dataset](https://www.kaggle.com/datasets/mustafacicek/imdb-top-250-lists-1996-2020/download?datasetVersionNumber=3)

##### Steps
1. Download [IMDB Top 250](https://www.kaggle.com/datasets/mustafacicek/imdb-top-250-lists-1996-2020/download?datasetVersionNumber=3) from [Kaggle](https://www.kaggle.com/datasets/mustafacicek/imdb-top-250-lists-1996-2020?resource=download), and extract ZIP file into a folder, e.g. *c:\Downloads*;
1. Import *imdbTop250.csv* into Power BI
1. Promote the first line to Header
1. Add custom fields for **RankingGroup**, **IMDB_ID** and **IMDB_URL**

#### Power Query Sample Script
```css
let
    Source = Csv.Document(File.Contents("C:\Downloads\imdbTop250.csv"),[Delimiter=",", Columns=16, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Ranking", Int64.Type}, {"IMDByear", Int64.Type}, {"IMDBlink", type text}, {"Title", type text}, {"Date", Int64.Type}, {"RunTime", Int64.Type}, {"Genre", type text}, {"Rating", type number}, {"Score", Int64.Type}, {"Votes", Int64.Type}, {"Gross", type number}, {"Director", type text}, {"Cast1", type text}, {"Cast2", type text}, {"Cast3", type text}, {"Cast4", type text}}),
    #"Added RankingGroup" = Table.AddColumn(#"Changed Type", "RankingGroup", each if [Ranking] < 50 then 1 else if [Ranking] <100 then 2 else if [Ranking] < 150 then 3 else if [Ranking] < 200 then 4 else 5),
    #"Changed RankingGroup Type" = Table.TransformColumnTypes(#"Added RankingGroup",{{"RankingGroup", Int64.Type}}),
    #"Add IMDB_ID" = Table.AddColumn(#"Changed RankingGroup Type", "IMDB_ID", each Text.BetweenDelimiters([IMDBlink], "/", "/", 1, 0), type text),
    Add_IMDB_URL = Table.AddColumn(#"Add IMDB_ID", "IMDB_URL", each Text.Combine({"https://www.imdb.com", [IMDBlink]}), type text)
in
    Add_IMDB_URL
```

### 3 *Plex Libraries* Table

#### Depedency

##### Parameter

- **X-Plex-Token**: [Finding an authentication token / X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) 

- **IP**: Plex Server IP Address, e.g. '*10.10.10.2*'

#### Steps
1. Combine IP and X-Plex-Token into a Plex Libraries List URL, and retrive all libraries ('**Directory**');
    >Xml.Tables(Web.Contents(Text.Combine({"http://",IP,":32400/library/sections?X-Plex-Token=",#"X-Plex-Token"})))
1. Drill down *Directory* into a table;
1. Expand *Location* to Folder Path;
1. Combine IP and X-Plex-Token into Plex Content Library URL;
    >Uri.Combine(Text.Combine({IP,":32400/"}) as text, Text.Combine({"library/sections/",Text.From([#"Attribute:key"]),"/all?X-Plex-Token=",#"X-Plex-Token"}) as text)
1. Split Location into columns and Parse as SMB format

#### Power Query Sample Script
```css
let
    Source = Xml.Tables(Web.Contents(Text.Combine({"http://",IP,":32400/library/sections?X-Plex-Token=",#"X-Plex-Token"}))),
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