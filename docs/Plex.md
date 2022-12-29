# Plex Movie Collections join with IMDB 250

----------

## Parameters

1. **StarDate**: Required, Type as <em>Date</em>
1. **X-Plex-Token**: Required, Type as <em>Text</em>
1. **IP**: Required, Type as <em>Text</em>
1. **LibraryURL**: Required, Type as <em>Text</em>

----------

## Custom Function

### <em> 1. Load Movie Content</em> Function

#### Parameter

**LibraryURL**: Format like http://[<em>IP</em>]:32400/library/sections/[<em>Movies Library ID</em>]/all?X-Plex-Token=[<em>X-Plex-Token</em>] (can be copied from **Plex Libraries** Table below)

#### Steps

1. Retrieve library detail from LibraryURL
1. Expand Video into columns, and expand Video.Media and Video.Collection information

#### Power Query Sample Scripts
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
[Basic Data](./BasicData.md)

**Date** Table

**Year** Table

**LastRefreshed** Table

### 2 <em> IMDB Top 250 List </em> Table

#### Steps
1. Download [IMDB Top 250](https://www.kaggle.com/datasets/mustafacicek/imdb-top-250-lists-1996-2020/download?datasetVersionNumber=3) from [Kaggle](https://www.kaggle.com/datasets/mustafacicek/imdb-top-250-lists-1996-2020?resource=download), and extract ZIP file into a folder, e.g. <em>c:\Plex</em>;
1. Import <em>imdbTop250.csv</em> into Power BI
1. Promote the first line to Header
1. Add custom fields for **RankingGroup**, **IMDB_ID** and **IMDB_URL**

#### Power Query Sample Scripts
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

### 3 <em> Plex Libraries </em> Table

#### Depedency

##### Parameter

**X-Plex-Token**: [Finding an authentication token / X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) 

**IP**: Plex Server IP Address, e.g. '<em>10.10.10.2</em>'

#### Steps
1. Combine IP and X-Plex-Token into a Plex Libraries List URL, and retrive all libraries ('**Directory**');
    `Xml.Tables(Web.Contents(Text.Combine({"http://",IP,":32400/library/sections?X-Plex-Token=",#"X-Plex-Token"})))`
1. Drill down <em>Directory</em> into a table;
1. Expand <em>Location</em> to Folder Path;
1. Combine IP and X-Plex-Token into Plex Content Library URL;
    `Uri.Combine(Text.Combine({IP,":32400/"}) as text, Text.Combine({"library/sections/",Text.From([#"Attribute:key"]),"/all?X-Plex-Token=",#"X-Plex-Token"}) as text)`
1. Split Location into columns and Parse as SMB format

#### Power Query Sample Scripts
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

### 4 <em> Plex Movies Content</em> Table

#### Dependency

**Plex Libraries** Table

**Load Movie Content** Custom Function

#### Steps
1. Reference from **Plex Libraries** Table above;
1. Filter **Type** = '<em>movie</em>' and **Scanner** = '<em>Plex Movie</em>';
1. Invoke **Load Movie Content** Function from Library <em>URL</em> field;
1. Add **Runtime** column and calculate base on <em>Duration</em> field, and format result into HH:MM:SS format by removing <em>Date</em> and <em>AM</em>;

    `Text.From(#datetime(1970, 1, 1, 0, 0, 0) + #duration(0, 0, 0, [Duration]/1000))`
1. Combine IP, Item Key and X-Plex-Token into **MetadatURL**;

    `Table.AddColumn(#"Trimmed Text", "MetadataURL", each Text.Combine({"http://",IP,":32400", [key], "?X-Plex-Token=",#"X-Plex-Token"}), type text)`

----------

## Relationship

----------

## Reports

----------

## Reference

### Power Query Reference
1. [Fuzzy Matching](https://learn.microsoft.com/en-us/power-query/fuzzy-matching)

### Plex API
1. [Finding an authentication token / X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
1. [Plex Media Server API Documentation](https://www.plexopedia.com/plex-media-server/api/)
1. [Plex Media Server URL Command](https://support.plex.tv/articles/201638786-plex-media-server-url-commands/)
 
    - List Base Server Capabilities: http://[<em>IP</em>]:32400/?X-Plex-Token=[<em>X-Plex-Token</em>]
    - List Defined Libraries: http://[<em>IP</em>]:32400/library/sections/?X-Plex-Token=[<em>X-Plex-Token</em>]
    - List Library Contents: http://[<em>IP</em>]:32400/library/sections/[<em>Movies Library ID</em>]/all?X-Plex-Token=[<em>X-Plex-Token</em>]
    - List Detail of an Item: http://[<em>IP</em>]:32400/library/metadata/[<em>Item Key ID</em>]?X-Plex-Token=[<em>X-Plex-Token</em>]