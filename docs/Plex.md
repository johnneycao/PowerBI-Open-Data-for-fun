# Plex Movie Collections with IMDB 250

## Data Tables

### 1 Basic Tables

#### Tables 
[Basic Data](./BasicData.md)

**Date** Table

**Year** Table

**LastRefreshed** Table

### 2 <em> IMDB Top 250 List </em> Table

#### Steps
1. Download [IMDB Top 250](https://www.kaggle.com/datasets/mustafacicek/imdb-top-250-lists-1996-2020/download?datasetVersionNumber=3) from [Kaggle](https://www.kaggle.com/datasets/mustafacicek/imdb-top-250-lists-1996-2020?resource=download), and extract ZIP file into a folder, e.g. <em>c:\Plex</em>;
1. Import <em>imdbTop250.csv</em> into Power BI
1. Promote the first line to Header
1. Add custom fields for RankingGroup, IMDB_ID and IMDB_URL

#### Power Query Scripts
```css
let
    Source = Csv.Document(File.Contents("C:\Plex\imdbTop250.csv"),[Delimiter=",", Columns=16, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Ranking", Int64.Type}, {"IMDByear", Int64.Type}, {"IMDBlink", type text}, {"Title", type text}, {"Date", Int64.Type}, {"RunTime", Int64.Type}, {"Genre", type text}, {"Rating", type number}, {"Score", Int64.Type}, {"Votes", Int64.Type}, {"Gross", type number}, {"Director", type text}, {"Cast1", type text}, {"Cast2", type text}, {"Cast3", type text}, {"Cast4", type text}}),
    #"Added RankingGroup" = Table.AddColumn(#"Changed Type", "RankingGroup", each if [Ranking] < 50 then 1 else if [Ranking] <100 then 2 else if [Ranking] < 150 then 3 else if [Ranking] < 200 then 4 else 5),
    #"Changed RankingGroup Type" = Table.TransformColumnTypes(#"Added RankingGroup",{{"RankingGroup", Int64.Type}}),
    #"Add IMDB_ID" = Table.AddColumn(#"Changed RankingGroup Type", "IMDB_ID", each Text.BetweenDelimiters([IMDBlink], "/", "/", 1, 0), type text),
    Add_IMDB_URL = Table.AddColumn(#"Add IMDB_ID", "IMDB_URL", each Text.Combine({"https://www.imdb.com", [IMDBlink]}), type text)
in
    Add_IMDB_URL
```

### 3 <em> Plex Library </em> Tables

#### Depedency

##### Parameter

**PlexToken**: Required, Type as <em>Date</em>; 

**IP address**: Required, Type as <em>Text</em>

## Relationship

## Reports

## Reference

### Power Query Reference
1. [Fuzzy Matching](https://learn.microsoft.com/en-us/power-query/fuzzy-matching)

### Plex API
1. [Get All Movies](https://www.plexopedia.com/plex-media-server/api/library/movies/)

    GET http://[<em>IP address</em>]:32400/library/sections/[Movies Library ID]/all?X-Plex-Token=[<em>PlexToken</em>]
1. 