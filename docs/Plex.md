# Plex Movie Collections

## 1 <em> IMDB Top 250 List </em> Table

### Depedency

#### Parameter

**PlexToken**: Required, Type as Date; 

**IP address**: Required, Type as Text

#### Tables 


<em>Date</em> Table

<em>Year</em> Table

<em>LastRefreshed</em> Table

### Steps
1. Download the IMDB Top 250 from [Kaggle](https://www.kaggle.com/datasets/mustafacicek/imdb-top-250-lists-1996-2020?resource=download "Top 250 List");
1. Extract ZIP file into a folder, e.g. <em>c:\Plex</em>;
1. Import <em>imdbTop250.csv</em> into Power BI

### Power Query Scripts
```css
let
    Source = Csv.Document(File.Contents("C:\Plex\imdbTop250.csv"),[Delimiter=",", Columns=16, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Ranking", Int64.Type}, {"IMDByear", Int64.Type}, {"IMDBlink", type text}, {"Title", type text}, {"Date", Int64.Type}, {"RunTime", Int64.Type}, {"Genre", type text}, {"Rating", type number}, {"Score", Int64.Type}, {"Votes", Int64.Type}, {"Gross", type number}, {"Director", type text}, {"Cast1", type text}, {"Cast2", type text}, {"Cast3", type text}, {"Cast4", type text}}),
    #"Inserted Text Between Delimiters" = Table.AddColumn(#"Changed Type", "IMDB", each Text.BetweenDelimiters([IMDBlink], "/", "/", 1, 0), type text),
    #"Added Custom" = Table.AddColumn(#"Inserted Text Between Delimiters", "RankingGroup", each if [Ranking] < 50 then 1 else if [Ranking] <100 then 2 else if [Ranking] < 150 then 3 else if [Ranking] < 200 then 4 else 5),
    #"Inserted Merged Column" = Table.AddColumn(#"Added Custom", "IMDB_URL", each Text.Combine({"https://www.imdb.com", [IMDBlink]}), type text),
    #"Changed Type1" = Table.TransformColumnTypes(#"Inserted Merged Column",{{"RankingGroup", Int64.Type}})
in
    #"Changed Type1"
```

# Reference
### Power Query Reference
#### 1. [Fuzzy Matching](https://learn.microsoft.com/en-us/power-query/fuzzy-matching)
### Plex API
#### 1. [Get All Movies](https://www.plexopedia.com/plex-media-server/api/library/movies/)
`GET http://[IP address]:32400/library/sections/[Movies Library ID]/all?X-Plex-Token=[PlexToken]`

