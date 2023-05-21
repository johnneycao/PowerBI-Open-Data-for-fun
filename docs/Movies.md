---
title: Movie collections analysis
author: Johnney Cao
date updated: 2023-5-21
keyword: [IMDB, IMDB Top 250, Plex API, parameter, web connector, Python, pandas, bs4, custom function, Image URL, Web URL, table reference, conditional format, csv, Matrix table, dashboard, DAX, tooltips card]
---

# Analysis of Movie Collections from IMDB Top 250 and Plex

----------

[PBI Download Link](../_Asset%20Library/Source_Files/Movies.pbit)

----------

## Parameters


|Parameter  |Description  |Data Type  |Reference  |
|:--------|:--------|:--------|:--------|
|**StarDate**  | Start Date for the report| Required, Type as `Date`  |    |
|**X-Plex-Token**  |token key to access Plex Server endpoints or XML|Required, Type as `Text`  |[Finding an authentication token / X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)  | 
|**PlexServer**  |Plex Server IP Address with Port Number e.g., `http://your_ip_address:32400` or `https://your_ip_address:32400`|Required, Type as `Text`  |    |

----------

## Data Tables

### 1. Basic Tables

#### Tables 

- **Date** Table

- **Year** Table

- **LastRefreshed** Table

### 2. Plex Tables

There are different options to load the movie contents from Plex Server:

1. Load data from Plex Server using **official** [Plex API](https://www.plexopedia.com/plex-media-server/api/) directly, which can be run from any Web browser, sample as below: 

    > Library List: [http(s)://your_ip_address:32400]/library/sections?X-Plex-Token=[X-Plex-Token]
    
    > Library Section List: [http(s)://your_ip_address:32400]/library/sections/{key}/all?X-Plex-Token=[X-Plex-Token]
    
    > Movie MetaData: [http(s)://your_ip_address:32400]/library/metadata/{ratingKey}?X-Plex-Token=[X-Plex-Token]

1. Load data using Python [PlexAPI](https://pypi.org/project/PlexAPI/) [Project GitHub](https://github.com/pkkid/python-plexapi), which is **unofficial** Python bindings for the Plex API; 

1. Run the Python job using [PlexAPI](https://pypi.org/project/PlexAPI/) above and export result in csv file, and import as datasource in Power BI.

Here below is the Pros / Cons for each options:

|Option  |Description  |Pros  |Cons  |
|:-------:|:--------|:--------|:--------|
|Option 1    |Use Plex API directly  |- Direct access: Bypasses the need for any third-party libraries or tools. <br/>- Real-time data: Fetches the most up-to-date data directly from the server.  |- More complex setup: Requires manual handling of HTTP requests and parsing API responses.<br/> - Some metadata, e.g. IMDB_ID, Audio, Video, Subtitles are stored in Movie Metadata not in Library Section, need a seperate custom function to fetch data from each item|
|Option 2    |Use Python PlexAPI library in python script  |- Easier implementation: The library simplifies interactions with the Plex API.<br/>- Better error handling: The library is more likely to handle errors and edge cases gracefully.<br/>- Community support: Updates to the library will accommodate changes in the Plex API.  |- Dependency on external library: Need to ensure the library stays up-to-date and compatible with system.<br/>- Slower execution: Using a library cause slightly slower compared to direct API calls, depending on its implementation.  |
|Option 3    |Use Python PlexAPI, export in CSV file and import in Power BI  |- Separation of concerns: Data extraction and processing are separated, making it easier to manage and troubleshoot.<br/>- CSV compatibility: CSV files can be easily used by various tools and platforms, providing flexibility in data analysis and visualization.  |- Not real-time: The data will only be as recent as the last time you exported the CSV file.<br/>- Additional steps: Exporting to a CSV file and importing into Power BI adds extra overhead to workflow.<br/>- Potential storage issues: Depending on the size of the dataset, you may face storage limitations or performance issues when dealing with large CSV files.  |

Consider about the volumn of Plex Library as well as the required columns, I am using Option 3 as primary datasource in the sample, but keep the Queries for Option 1 and Option 2 (set limit to 20 records) in the PBIX for reference.

#### 2.1. Option 1 - *Plex Libraries* Table

##### Parameter

- **X-Plex-Token** 
- **PlexServer**

##### Steps
1. Combine IP and X-Plex-Token into a Plex Libraries List URL, and retrive all libraries ('**Directory**');
    > = Xml.Tables(Web.Contents(Text.Combine({PlexServer,"/library/sections?X-Plex-Token=",#"X-Plex-Token"})))
1. Drill down **Directory** into a table;
1. Expand **Location** to Folder Path;
1. Combine IP and X-Plex-Token into Plex Content Library URL;
    > = Uri.Combine(Text.Combine({IP,":32400/"}) as text, Text.Combine({"library/sections/",Text.From([#"Attribute:key"]),"/all?X-Plex-Token=",#"X-Plex-Token"}) as text)
1. Split Location into columns and Parse as SMB File Folder format

##### Power Query Sample Script
```css
    let
        Source = Xml.Tables(Web.Contents(Text.Combine({PlexServer,"/library/sections?X-Plex-Token=",#"X-Plex-Token"}))),
        #"Changed Type" = Table.TransformColumnTypes(Source,{{"Attribute:size", Int64.Type}, {"Attribute:allowSync", Int64.Type}, {"Attribute:title1", type text}}),
        Directory = #"Changed Type"{0}[Directory],
        #"Removed Other Columns" = Table.SelectColumns(Directory,{"Location", "Attribute:art", "Attribute:composite", "Attribute:key", "Attribute:type", "Attribute:title", "Attribute:agent", "Attribute:scanner", "Attribute:language", "Attribute:hidden"}),
        #"Expanded Location" = Table.ExpandTableColumn(#"Removed Other Columns", "Location", {"Attribute:path"}, {"Location.Attribute:path"}),
        #"Added Custom" = Table.AddColumn(#"Expanded Location", "URL", each Uri.Combine(
        PlexServer,
        Text.Combine({"/library/sections/",Text.From([#"Attribute:key"]),"/all?X-Plex-Token=",#"X-Plex-Token"}) as text)
    as text),
        #"Reordered Columns" = Table.ReorderColumns(#"Added Custom",{"Attribute:art", "Attribute:key", "Attribute:type", "Attribute:title", "Attribute:agent", "Attribute:scanner", "Attribute:language", "Attribute:hidden", "Location.Attribute:path", "URL"}),
        #"Split Column by Delimiter" = Table.SplitColumn(#"Reordered Columns", "Location.Attribute:path", Splitter.SplitTextByDelimiter("/", QuoteStyle.Csv), {"Location.Attribute:path.1", "Location.Attribute:path.2", "Location.Attribute:path.3", "Location.Attribute:path.4", "Location.Attribute:path.5", "Location.Attribute:path.6"}),
        #"Inserted Folder Name" = Table.AddColumn(#"Split Column by Delimiter", "Folder", each Text.Combine({Text.BetweenDelimiters(PlexServer, "http://", ":32400"), "\", [#"Location.Attribute:path.4"], "\", [#"Location.Attribute:path.5"]}), type text),
        #"Clean Up Columns" = Table.RemoveColumns(#"Inserted Folder Name",{"Location.Attribute:path.1", "Location.Attribute:path.2", "Location.Attribute:path.3", "Location.Attribute:path.4", "Location.Attribute:path.5", "Location.Attribute:path.6", "Attribute:art"}),
        #"Renamed Columns" = Table.RenameColumns(#"Clean Up Columns",{{"Attribute:key", "Key"}, {"Attribute:type", "Type"}, {"Attribute:title", "Library"}, {"Attribute:agent", "Agent"}, {"Attribute:scanner", "Scanner"}, {"Attribute:language", "Language"}, {"Attribute:hidden", "Hidden"}})
    in
        #"Renamed Columns"
```

#### 2.1. Option 1 - *Load Movie Contents* Function

*NOTE: it only returns result from [Library Section](https://www.plexopedia.com/plex-media-server/api/library/movies/) not Movie Metadata, therefore no information about **Audio**, **Video**, **Subtitles**, **IMDB_ID**, **TMDB_ID** or **TVDB_ID**.*

###### Parameter

- **X-Plex-Token**; 
- **LibraryURL**: Required, Format like `[PlexServer]/library/sections/{key}/all?X-Plex-Token=[X-Plex-Token]` (can be copied from **Plex Libraries** Table above)

###### Steps

1. Retrieve library detail from **LibraryURL** Parameter;
1. Expand **Video** into columns, and expand Video.Media and Video.Collection information.

##### Power Query Sample Script
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

#### 2.1. Option 1 - *Plex Movies - API* Raw Data Table

##### Dependency

- **Plex Libraries** Table;
- **Load Movie Content** Custom Function.

##### Steps
1. Reference from **Plex Libraries** Table above;
1. Filter **Type** = '*movie*' and **Scanner** = '*Plex Movie*';
1. Invoke **Load Movie Content** Function from Library *URL* field;
1. Add **Runtime** column and calculate base on *Duration* field, and format result into HH:MM:SS format by removing *Date* and *AM*;

    > = Text.From(#datetime(1970, 1, 1, 0, 0, 0) + #duration(0, 0, 0, [Duration]/1000))
1. Combine PlexServer, Item Key and X-Plex-Token into **MetadatURL**.

    > = Text.Combine({PlexServer, [key], "?X-Plex-Token=",#"X-Plex-Token"});
1. Mark the table not "include in report refresh".

##### Power Query Sample Script
```css
    let
        Source = #"Plex Library",
        #"Filtered Rows" = Table.SelectRows(Source, each ([Type] = "movie") and ([Scanner] = "Plex Movie")),
        #"Removed Duplicates" = Table.Distinct(#"Filtered Rows", {"URL"}),
        #"Invoked Custom Function" = Table.AddColumn(#"Removed Duplicates", "Contents", each LoadMovieContents([URL])),
        #"Expanded Contents" = Table.ExpandTableColumn(#"Invoked Custom Function", "Contents", {"Duration", "Bitrate", "AspectRatio", "AudioChannels", "AudioCodec", "VideoCodec", "Resolution", "FrameRate", "AudioProfile", "VideoProfile", "key", "Studio", "Title", "ContentRating", "Summary", "AudienceRating", "Year", "Tagline", "IMDBduration", "OriginallyAvailableAt", "Collection", "ViewCount", "TitleSort", "OriginalTitle"}, {"Duration", "Bitrate", "AspectRatio", "AudioChannels", "AudioCodec", "VideoCodec", "Resolution", "FrameRate", "AudioProfile", "VideoProfile", "key", "Studio", "Title", "ContentRating", "Summary", "AudienceRating", "Year", "Tagline", "IMDBduration", "OriginallyAvailableAt", "Collection", "ViewCount", "TitleSort", "OriginalTitle"}),
        #"Removed Header Columns" = Table.RemoveColumns(#"Expanded Contents",{"Agent", "Scanner", "Language", "Hidden", "URL", "Folder"}),
        #"Added Runtime" = Table.AddColumn(#"Removed Header Columns", "Runtime", each Text.From(#datetime(1970, 1, 1, 0, 0, 0) + #duration(0, 0, 0, [Duration]/1000))),
        #"Replaced Errors" = Table.ReplaceErrorValues(#"Added Runtime", {{"Runtime", ""}}),
        #"Replaced Value" = Table.ReplaceValue(#"Replaced Errors","1/1/1970 12","1/1/1970 0",Replacer.ReplaceText,{"Runtime"}),
        #"Remove Date from Runtime" = Table.ReplaceValue(#"Replaced Value","1/1/1970 ","",Replacer.ReplaceText,{"Runtime"}),
        #"Remove AM from Runtime" = Table.ReplaceValue(#"Remove Date from Runtime"," AM","",Replacer.ReplaceText,{"Runtime"}),
        #"Trimmed Text" = Table.TransformColumns(#"Remove AM from Runtime",{{"Runtime", Text.Trim, type text}}),
        #"Added Conditional Column" = Table.AddColumn(#"Trimmed Text", "Original Title", each if [OriginalTitle] = null then [Title] else [OriginalTitle]),
        #"Inserted Year TItle" = Table.AddColumn(#"Added Conditional Column", "Year Title", each Text.Combine({Text.From([Year], "en-US"), " | ", [Original Title]}), type text),
        #"Inserted Metadata URL" = Table.AddColumn(#"Inserted Year TItle", "MetadataURL", each Text.Combine({PlexServer, [key], "?X-Plex-Token=",#"X-Plex-Token"}), type text),
        #"Changed Type" = Table.TransformColumnTypes(#"Inserted Metadata URL",{{"AspectRatio", Currency.Type}, {"AudioChannels", Int64.Type}, {"AudienceRating", Currency.Type}, {"Year", Int64.Type}, {"OriginallyAvailableAt", type date}, {"ViewCount", Int64.Type}, {"Duration", Int64.Type}, {"Bitrate", Int64.Type}})
    in
        #"Changed Type"
```

#### 2.2. Option 2 - *Plex Movies - Python* Raw Data Table

##### Paramter
- **X-Plex-Token** 
- **PlexServer**

##### Dependency
- pandas
    > pip install pandas

- plexapi
    > pip install plexapi

##### Steps
1. Get Data from Python Script below;
1. Replace the Variables using Parameters and phase it to a Python Script;
1. Add **Resolution** column from **Video**;
1. Add **IMDB_URL** column using **IMDB_ID**;
1. Change **PlexMetadata_ID**, **IMDB_ID**, **TMDB_ID**, **TVDB_ID** to `text`;
1. Mark the table not "include in report refresh".

##### Python Sample Code
```python
    from plexapi.server import PlexServer
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util import Retry
    import pandas as pd
    
    # Fill in your Plex server details.
    PLEX_URL = ['Your Plex Server'] # e.g., 'http://{your_ip_address}:32400' or 'https://{your_ip_address}:32400'
    PLEX_TOKEN = ['Your Plex Token'] 
        
    class InsecureHttpAdapter(HTTPAdapter):
        """An adapter that disables SSL certification validation."""
        
        def cert_verify(self, *args, **kwargs):
            return None
    
        def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
            pool_kwargs['assert_hostname'] = False
            super(InsecureHttpAdapter, self).init_poolmanager(connections, maxsize, block, **pool_kwargs)
    
    
    def get_insecure_requests_session():
        # Check if using HTTPS in PlexServer, and bypass SSL cerfification certification
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        adapter = InsecureHttpAdapter(max_retries=retry)
        session.mount('https://', adapter)
        return session
            
    def main():
        # Connect to Plex server.
        session = None
        if PLEX_URL.lower().startswith("https"):
            session = get_insecure_requests_session()
        
        plex = PlexServer(PLEX_URL, PLEX_TOKEN, session=session)
        
        # Fetch all movies from the library and filter based on type and scanner.
        all_sections = plex.library.sections()
        movie_sections = [section for section in all_sections if section.type == 'movie' and section.scanner == 'Plex Movie']
        movie_list = [movie for section in movie_sections for movie in section.all()]
    
        # Prepare DataFrame columns
        columns = ["PlexMetadata ID", "Movie GUID", "Title", "Sort Title", "Original Title", "Library", "Genres", "Content Rating", "Collection", "Studio", "Director", "Cast", "Summary", "Country", "Thumb Link", "IMDB ID", "TMDB ID", "TVDB ID", "View Count", "Audience Rate", "Release Date", "Year", "Added Date", "IMDB Duration (mins)", "Duration (mins)", "File", "Aspect Ratio", "Frame Rate","Container", "Video Codec", "Audio Codec", "Audio Channels", "Audio", "Video", "Subtitles"]
        
        # Create an empty DataFrame with these columns
        df = pd.DataFrame(columns=columns, dtype=object)
    
        # Add movie details to the DataFrame, unmark the 4 comments below to load all the movies. 
    #    movie_count = 0
        for movie in movie_list:
    #        if movie_count >= 20:
    #            break
            row = print_movie_details(movie)
            df.loc[len(df)] = pd.Series(row, index=df.columns)
    #        movie_count += 1
    
        return df
    
    def print_movie_details(movie):
    
        # Extract IMDB, TMDB, and TVDB IDs from movie info.
        ids = {'imdb': None, 'tmdb': None, 'tvdb': None}
        for guid_obj in movie.guids:
            guid_str = str(guid_obj.id).lower()
            for key in ids.keys():
                if f'{key}://' in guid_str:
                    ids[key] = guid_str.split(f'{key}://')[-1]
    
        media = movie.media[0] if movie.media else None           
        part = media.parts[0] if media.parts else None
        
        # Prepare movie details in tab-separated format.
        row = [
            str(movie.ratingKey),
            str(movie.guid),
            str(movie.title),
            str(movie.titleSort) if movie.titleSort else movie.title,
            str(movie.originalTitle) if movie.originalTitle else movie.title,
            str(movie.librarySectionTitle),
            ', '.join(str(genre.tag) for genre in movie.genres),
            movie.contentRating or '',
            ', '.join(str(col.tag) for col in movie.collections) if movie.collections else '',
            movie.studio or '',
            ', '.join(str(director.tag) for director in movie.directors),
            ', '.join(str(role.tag) for role in movie.roles),
            (movie.summary.replace('\n', ' ').replace('\r', '').replace('\t', ' ')[:150] + "...") if movie.summary else '',
            ', '.join(str(country.tag) for country in movie.countries),
            str(movie.thumb) if movie.thumb else '',
            ids['imdb'] or '',
            ids['tmdb'] or '',
            ids['tvdb'] or '',
            str(movie.viewCount) if movie.viewCount else '0',
            str(movie.audienceRating) if movie.audienceRating else '',
            str(movie.originallyAvailableAt) if movie.originallyAvailableAt else '',
            str(movie.year) if movie.year else '',
            str(movie.addedAt) if movie.addedAt else '',
            str(round(movie.duration / 60000)) if movie.duration else '',
            str(round(media.duration / 60000)) if media and media.duration else '',
            f"{part.file}" if media and part and part.file else '',
            f"{media.aspectRatio}" if media and media.aspectRatio else '',
            f"{media.videoFrameRate}" if media and media.videoFrameRate else '',
            f"{media.container}" if media and media.container else '',
            f"{media.videoCodec}" if media and media.videoCodec else '',
            f"{media.audioCodec}" if media and media.audioCodec else '',
            f"{media.audioChannels}" if media and media.audioChannels else '',
            ', '.join([f"{str(stream.displayTitle)}" for part in movie.media[0].parts for stream in part.streams if stream.streamType == 2]) if movie.media and movie.media[0].parts else '',
            ', '.join([f"{str(stream.displayTitle)}" for part in movie.media[0].parts for stream in part.streams if stream.streamType == 1]) if movie.media and movie.media[0].parts else '',
            ', '.join([f"{str(stream.displayTitle)}" for part in movie.media[0].parts for stream in part.streams if stream.streamType == 3]) if movie.media and movie.media[0].parts else ''
        ]
        
        # Return the movie details as a list
        return row
    
    if __name__ == "__main__":
        result_df = main()
    
    result_df
```

#### 2.3. Option 3 - *Plex Movies - CSV* Raw Data Table

##### Paramter
- **X-Plex-Token** 
- **PlexServer**
- **Plex_CSV** - the export file from in Python code, which will be used when import into Power BI.

##### Dependency
- pandas
    > pip install pandas

- plexapi
    > pip install plexapi

##### Steps
1. Update the 3 Variables (PLEX_URL, PLEX_TOKEN, EXPORT_FILE) in sample script and run the Python Script locally to export the file in CSV format;
1. Import the CSV file into Power BI;
1. Add **Resolution** column from **Video**;
1. Add **IMDB_URL** column using **IMDB_ID**;
1. Change **PlexMetadata_ID**, **IMDB_ID**, **TMDB_ID**, **TVDB_ID** to `text`;
1. Mark the table not "include in report refresh".

##### Python Sample Code

[Python Download Link](../_Asset%20Library/Source_Files/Plex_Movies.py)

##### Power Query Sample Script
```css
let
    Source = Csv.Document(File.Contents(Plex_CSV),[Delimiter=",", Columns=36, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Inserted Resolution" = Table.AddColumn(#"Promoted Headers", "Resolution", each Text.BeforeDelimiter(Text.Upper([Video]), " "), type text),
    #"Inserted IMDB_URL" = Table.AddColumn(#"Inserted Resolution", "IMDB_URL", each if [IMDB ID] <> null and [IMDB ID] <> "" then Text.Combine({"https://www.imdb.com/title/", [IMDB ID]}) else ""),
    #"Changed Type" = Table.TransformColumnTypes(#"Inserted IMDB_URL",{{"PlexMetadata ID", type text}, {"Title", type text}, {"Original Title", type text}, {"Library", type text}, {"Genres", type text}, {"Content Rating", type text}, {"Collection", type text}, {"Studio", type text}, {"Director", type text}, {"Cast", type text}, {"Summary", type text}, {"Country", type text}, {"IMDB ID", type text}, {"TMDB ID", type text}, {"TVDB ID", type text}, {"Audience Rate", type number}, {"Release Date", type datetime}, {"Year", Int64.Type}, {"Duration (mins)", Int64.Type}, {"Aspect Ratio", type number}, {"Frame Rate", type text}, {"Container", type text}, {"Video Codec", type text}, {"Audio Codec", type text}, {"Audio Channels", Int64.Type}, {"Audio", type text}, {"Video", type text}, {"Subtitles", type text}, {"Resolution", type text}, {"IMDB_URL", type text}, {"Added Date", type datetime}, {"IMDB Duration (mins)", Int64.Type}})
in
    #"Changed Type"
```

#### 2.4. *Plex Movies* Master Table
*Note: Add the table to minimum impact to the databoard, and easily switch between different Raw Data Table options.*

##### Dependency

- **Plex Moives** Raw Table;

##### Steps
1. Reference from one of the 3 **Plex Movies** Raw Data Tables above;
1. Remove Duplicats from PlexMetadata Id.

##### Power Query Sample Script
```css
let
    Source = #"Plex Movies - CSV",
    #"Removed Duplicates PlexMetadata ID" = Table.Distinct(Source, {"PlexMetadata ID"})
in
    #"Removed Duplicates PlexMetadata ID"
```

#### 2.5. *Plex IMDB* Master Table
Note: Simiar to *Plex Movies* Master Table, used to 1:many with IMDB Data Table

##### Dependency

- **Plex Libraries** Raw Table;

##### Steps
1. Reference from one of the 3 **Plex Movies** Raw Data Tables above;
1. Clean up the item which doesnot have IMDB_ID;
1. Keep only IMDB related colummn;
1. Remove Duplicats from PlexMetadata Id;
1. Add column for **In Most Popular**;
    > In Most Popular = IF(COUNTROWS(FILTER('IMDB Charts', 'IMDB Charts'[List Name] = "Most Popular" && 'IMDB Charts'[IMDB ID] = 'Plex IMDB Master'[IMDB ID])) > 0,"TRUE","FALSE")
1. Add column for **In Oscar Highlight**;
    >In Oscar Highlight = IF(COUNTROWS(FILTER('IMDB Top Lists', LEFT('IMDB Top Lists'[List Name], 5) = "Oscar" && 'IMDB Top Lists'[IMDB ID] = 'Plex IMDB Master'[IMDB ID])) > 0,"TRUE","FALSE")
1. Add column for **In Top 250**;
    > In T250 = IF(OR(COUNTROWS(FILTER('IMDB Charts', 'IMDB Charts'[List Name] = "IMDB Top 250" &&  'IMDB Charts'[IMDB ID] = 'Plex IMDB Master'[IMDB ID])) > 0,COUNTROWS(FILTER('IMDB Top Lists', LEFT('IMDB Top Lists'[List Name], 4) = "IMDB" && 'IMDB Top Lists'[IMDB ID] = 'Plex IMDB Master'[IMDB ID])) > 0),"TRUE","FALSE")
1. Add column for T250 Best Ranking
    > T250 Best Ranking = 
VAR CurrentRank =
    CALCULATE(
        MIN('IMDB Charts'[Rank]),
        FILTER(
            ALL('IMDB Charts'),
            'IMDB Charts'[List Name] = "IMDB Top 250" && 'IMDB Charts'[IMDB ID] = EARLIER([IMDB ID])
        ),
        NOT(ISBLANK('IMDB Charts'[Rank]))
    )
VAR HistoryRank =
    CALCULATE(
        MIN('IMDB Top Lists'[Ranking]),
        FILTER(
            ALL('IMDB Top Lists'),
            LEFT('IMDB Top Lists'[List Name], 4) = "IMDB" && 'IMDB Top Lists'[IMDB ID] = EARLIER([IMDB ID])
        ),
        NOT(ISBLANK('IMDB Top Lists'[Ranking]))
    )
RETURN
    SWITCH(TRUE(),ISBLANK(CurrentRank) && ISBLANK(HistoryRank), BLANK(), ISBLANK(CurrentRank), HistoryRank, ISBLANK(HistoryRank), CurrentRank, MIN(CurrentRank, HistoryRank))
1. Add column for T250 Current Ranking
    > T250 Current Ranking = CALCULATE(
        MIN('IMDB Charts'[Rank]),
        FILTER(
            ALL('IMDB Charts'),
            'IMDB Charts'[List Name] = "IMDB Top 250" && 'IMDB Charts'[IMDB ID] = EARLIER([IMDB ID])
        ),
        NOT(ISBLANK('IMDB Charts'[Rank]))
    )

##### Power Query Sample Script
```css
let
    Source = #"Plex Movies - CSV",
    #"Remove Empty IMDB ID" = Table.SelectRows(Source, each [IMDB ID] <> null and [IMDB ID] <> ""),
    #"Removed Other Columns" = Table.SelectColumns(#"Remove Empty IMDB ID",{"Title", "Original Title", "Genres", "Content Rating", "Collection", "Studio", "Director", "Cast", "Summary", "Country", "IMDB ID", "TMDB ID", "TVDB ID", "Audience Rate", "Release Date", "Year", "IMDB Duration (mins)", "Duration (mins)", "IMDB_URL"}),
    #"Filtered Rows" = Table.SelectRows(#"Removed Other Columns", each [IMDB ID] <> null and [IMDB ID] <> ""),
    #"Removed Duplicates" = Table.Distinct(#"Filtered Rows", {"IMDB ID"})
in
    #"Removed Duplicates"
```

#### 2.6 *Plex Movie* Casts, Genres, Country, Audio, Video and SubTitles Tables
*Note: Extended tables for filtering*

##### Dependency

- **Plex Moives** Master Table;

##### Steps
1. Reference from one of the **Plex Libraries** Master Data Table above;
1. Keep PlexMetadata ID, Title, IMDB_ID, and extented columns only (e.g. **Casts**, **Genres**, **Country**, **Audio**, **Video** and **SubTitles** Tables)
1. Split the extended column by Delimiter into Rows
1. Trim and clean the Text

##### Power Query Sample Script
*Note: Use Cast as an example, rest are similar*

```css
let
    Source = #"Plex Movies - CSV",
    #"Removed Other Columns" = Table.SelectColumns(Source,{"PlexMetadata ID", "Title", "Cast", "IMDB ID"}),
    #"Split Cast Column by Delimiter" = Table.ExpandListColumn(Table.TransformColumns(#"Removed Other Columns", {{"Cast", Splitter.SplitTextByDelimiter(",", QuoteStyle.Csv), let itemType = (type nullable text) meta [Serialized.Text = true] in type {itemType}}}), "Cast"),
    #"Trimmed Text" = Table.TransformColumns(#"Split Cast Column by Delimiter",{{"Cast", Text.Trim, type text}}),
    #"Cleaned Text" = Table.TransformColumns(#"Trimmed Text",{{"Cast", Text.Clean, type text}}),
    #"Filtered Empty Cast" = Table.SelectRows(#"Cleaned Text", each [Cast] <> null and [Cast] <> "")
in
    #"Filtered Empty Cast"
```

### 3 *IMDB* Tables

#### 3.1 *IMDB Charts*  Tables
IMDB Top 250 Movies (Most recent), Top Rated English Movies (250) and Most Popular Movies (100)

##### Data Sources
 - [Most Popular Movies](https://www.imdb.com/chart/moviemeter)
 - [IMDB Top 250 Movies](https://www.imdb.com/chart/top)
 - [Top Rated English Movies](https://www.imdb.com/chart/top-english-movies) 

##### Steps
1. Use python code below to pull data from data source lists above;
1. Change **Rank** and **Year** to *Whole Number* and **Rating** to *Decimal Number*;
1. Add **IMDB URL** and setup Data category (Ribbon bar -> Format -> Data catagory = *Web URL*);
1. Setup Data category for **Image URL**  (Ribbon bar -> Format -> Data catagory = *Image URL*);
1. Add columns for **IMDB 250 Best Ranking** and **In Plex**.

    Note: **IMDB 250 Best Ranking**: Find minimum value from both **IMDB Charts** (current IMDB Top 250) and **IMDB Tops Lists** (Historic IMDB Top 250) tables, and use the smaller value.

    > IMDB 250 Best Ranking = 
        VAR CurrentRank =
            CALCULATE(
                MIN('IMDB Charts'[Rank]),
                FILTER(
                    ALL('IMDB Charts'),
                    'IMDB Charts'[List Name] = "IMDB Top 250" && 'IMDB Charts'[IMDB ID] = EARLIER([IMDB ID])
                ),
                NOT(ISBLANK('IMDB Charts'[Rank]))
            )
        VAR HistoryRank =
            CALCULATE(
                MIN('IMDB Top Lists'[Ranking]),
                FILTER(
                    ALL('IMDB Top Lists'),
                    LEFT('IMDB Top Lists'[List Name], 4) = "IMDB" && 'IMDB Top Lists'[IMDB ID] = EARLIER([IMDB ID])
                ),
                NOT(ISBLANK('IMDB Top Lists'[Ranking]))
            )
        RETURN
            SWITCH(TRUE(),ISBLANK(CurrentRank) && ISBLANK(HistoryRank), BLANK(), ISBLANK(CurrentRank), HistoryRank, ISBLANK(HistoryRank), CurrentRank, MIN(CurrentRank, HistoryRank))


    > In Plex = IF(COUNTROWS(FILTER('Plex IMDB Master', 'Plex IMDB Master'[IMDB ID]=EARLIER([IMDB ID])))>0,TRUE,FALSE)


##### Python Sample Code

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
    try:
        rating = tr.find("strong").get_text()
    except:
        rating = None
    
    # Find the image URL
    image_url = tr.find("td", class_="posterColumn").img["src"]

    # Add the data to the list
    data.append([rank, title, imdb_id, year, rating, image_url])

# Convert the list to a pandas dataframe
df = pd.DataFrame(data, columns=["Rank", "Title", "IMDB ID", "Year", "Rating", "Image URL"])
```

##### Power Query Sample Script
```css
let
    Source = Python.Execute("import requests#(lf)from bs4 import BeautifulSoup#(lf)import pandas as pd#(lf)#(lf)# Function to scrape the data from a given URL and list name#(lf)def scrape_data(url, list_name):#(lf)    response = requests.get(url)#(lf)    soup = BeautifulSoup(response.text, 'html.parser')#(lf)    table = soup.find(""tbody"", class_=""lister-list"")#(lf)    data = []#(lf)#(lf)    for tr in table.find_all(""tr""):#(lf)        title = tr.find(""td"", class_=""titleColumn"").a.get_text()#(lf)        rank = tr.find(""td"", class_=""titleColumn"").get_text().split(""."")[0]#(lf)        imdb_id = tr.find(""td"", class_=""posterColumn"").a[""href""].split(""/"")[2]#(lf)        year = tr.find(""span"", class_=""secondaryInfo"").get_text().strip(""()"")#(lf)        try:#(lf)            rating = tr.find(""strong"").get_text()#(lf)        except AttributeError:#(lf)            rating = None#(lf)        image_url = tr.find(""td"", class_=""posterColumn"").img[""src""]#(lf)#(lf)        # Fetch additional attributes#(lf)        attributes = tr.find_all(""span"")#(lf)        rank_attribute = None#(lf)        imdb_rating_attribute = None#(lf)        user_votes_attribute = None#(lf)        num_votes_attribute = None#(lf)        user_rating_attribute = None#(lf)#(lf)        for attribute in attributes:#(lf)            attribute_name = attribute.get(""name"")#(lf)            if attribute_name == ""rk"":#(lf)                rank_attribute = attribute.get(""data-value"")#(lf)            elif attribute_name == ""ir"":#(lf)                imdb_rating_attribute = attribute.get(""data-value"")#(lf)            elif attribute_name == ""us"":#(lf)                user_votes_attribute = attribute.get(""data-value"")#(lf)            elif attribute_name == ""nv"":#(lf)                num_votes_attribute = attribute.get(""data-value"")#(lf)            elif attribute_name == ""ur"":#(lf)                user_rating_attribute = attribute.get(""data-value"")#(lf)#(lf)        data.append([#(lf)            rank,#(lf)            title,#(lf)            imdb_id,#(lf)            year,#(lf)            rating,#(lf)            image_url,#(lf)            list_name,#(lf)            rank_attribute,#(lf)            imdb_rating_attribute,#(lf)            user_votes_attribute,#(lf)            num_votes_attribute,#(lf)            user_rating_attribute#(lf)        ])#(lf)#(lf)    return data#(lf)#(lf)# Main code#(lf)data = []#(lf)#(lf)# Scrape data from IMDB Top 250#(lf)data.extend(scrape_data(""https://www.imdb.com/chart/top"", ""IMDB Top 250""))#(lf)#(lf)# Scrape data from Most Popular#(lf)data.extend(scrape_data(""https://www.imdb.com/chart/moviemeter/"", ""Most Popular""))#(lf)#(lf)# Scrape data from Most Top Rated English Movies#(lf)data.extend(scrape_data(""https://www.imdb.com/chart/top-english-movies"", ""Most Top Rated English Movies""))#(lf)#(lf)# Convert the list to a pandas dataframe#(lf)df = pd.DataFrame(data, columns=[#(lf)    ""Rank"",#(lf)    ""Title"",#(lf)    ""IMDB ID"",#(lf)    ""Year"",#(lf)    ""Rating"",#(lf)    ""Image URL"",#(lf)    ""List Name"",#(lf)    ""Rank Attribute"",#(lf)    ""IMDB Rating Attribute"",#(lf)    ""User Votes Attribute"",#(lf)    ""Number of Votes Attribute"",#(lf)    ""User Rating Attribute""#(lf)])#(lf)"),
    df1 = Source{[Name="df"]}[Value],
    #"Changed Type" = Table.TransformColumnTypes(df1,{{"Year", Int64.Type}, {"Rating", type number}, {"Rank", Int64.Type}, {"Title", type text}, {"IMDB ID", type text}, {"Image URL", type text}, {"List Name", type text}, {"Rank Attribute", Int64.Type}, {"IMDB Rating Attribute", type number}, {"User Votes Attribute", Int64.Type}, {"Number of Votes Attribute", Int64.Type}, {"User Rating Attribute", type number}}),
    #"Replaced Errors" = Table.ReplaceErrorValues(#"Changed Type", {{"Rank", null}}),
    #"Inserted IMDB_URL" = Table.AddColumn(#"Replaced Errors", "IMDB URL", each Text.Combine({"https://www.imdb.com/title/", [IMDB ID]}), type text)
in
    #"Inserted IMDB_URL"
```

#### 3.2 *IMDB Top Lists* Table 
Top 250 Historical Table (1996 to last year) and Oscar Highlight (2019 till now).

*Note: Since it needs to load multiple lists and process each individually, the data retrieval process is expected to take more than 5 minutes to complete.*

##### Data Sources
- [pollmaster's List](https://www.imdb.com/user/ur48187336/lists)

##### Steps
1. Run the Python Script to load the data;
    1. From Pollmaster's list, find all the lists which start with **IMDb Top 250** or **Oscar Highlights**, and generate the URLs list;
    1. Loop through URLs list and Run the *extract_movie_details* function to extract movie details;
1. Clean up the year column;
1. Add custom fields for **RankingGroup** and **IMDB_ID**;
1. Add columns for **IMDB 250 Best Ranking** and **In Plex**.

##### Python Sample COde
    
```python
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
```

##### Power Query Sample Script
```css
let
    Source = Python.Execute("from bs4 import BeautifulSoup#(lf)from requests import get#(lf)import pandas as pd#(lf)import re#(lf)#(lf)page = get('https://www.imdb.com/user/ur48187336/lists')#(lf)soup = BeautifulSoup(page.content, 'html.parser')  # Changed parser to 'html.parser'#(lf)content = soup.find(id=""main"")#(lf)urls = pd.DataFrame()#(lf)temp = pd.DataFrame()#(lf)#(lf)for i in range(len(content.find_all(""a"", class_=""list-name""))):#(lf)    link = content.find_all(""a"", class_=""list-name"")[i].get('href')#(lf)    list_name = content.find_all(""a"", class_=""list-name"")[i].text#(lf)    inf = [list_name, link]#(lf)    temp = pd.DataFrame([inf], columns=['list_name', 'link'])#(lf)    urls = pd.concat([urls, temp], ignore_index=True)#(lf)#(lf)imdb_urls = urls[urls['list_name'].str.startswith('IMDb Top 250')]#(lf)oscar_urls = urls[urls['list_name'].str.startswith('Oscar Highlights')]#(lf)#(lf)def process_urls(urls, list_prefix):#(lf)    new_urls = urls.copy()#(lf)    new_urls['year'] = new_urls['list_name'].apply(lambda x: list_prefix + str(x[len(list_prefix):]))  # Fixed indexing#(lf)    new_urls['link'] = new_urls['link'].apply(lambda x: 'https://www.imdb.com' + x)#(lf)    new_urls = new_urls.sort_values(['year']).reset_index(drop=True)#(lf)    new_urls['page2'] = new_urls['link'].apply(lambda x: x + ""?page=2"")#(lf)    new_urls['page3'] = new_urls['link'].apply(lambda x: x + ""?page=3"")#(lf)    return new_urls#(lf)#(lf)imdb_urls = process_urls(imdb_urls, 'IMDb Top 250')#(lf)oscar_urls = process_urls(oscar_urls, 'Oscar Highlights')#(lf)#(lf)all_urls = pd.concat([imdb_urls, oscar_urls], ignore_index=True)#(lf)#(lf)# Define function to extract movie details from a single page#(lf)def extract_movie_details(page_content, ListYear):#(lf)    soup = BeautifulSoup(page_content, 'html.parser')#(lf)    Frame = soup.find_all(""div"", class_=""lister-item mode-detail"")#(lf)    details_list = []#(lf)    #(lf)    for i in range(len(Frame)):#(lf)        ArticleTitle = soup.find(""h1"", class_=""header"").text.replace(""\n"", """")#(lf)        FirstLine = Frame[i].find(""h3"", class_=""lister-item-header"")#(lf)        Ranking = int(FirstLine.find(""span"").text.replace('.', ''))#(lf)        IMDBlink = ""https://www.imdb.com"" + FirstLine.find(""a"").get(""href"")#(lf)        Title = FirstLine.find(""a"").text#(lf)        Date = re.sub(r""[()]"", """", FirstLine.find_all(""span"")[-1].text)#(lf)        #(lf)        try:#(lf)            Certificate = Frame[i].find(""span"", class_=""certificate"").text#(lf)        except:#(lf)            Certificate = None#(lf)            #(lf)        RunTime = Frame[i].find(""span"", class_=""runtime"").text[:-4]#(lf)        Genre = Frame[i].find(""span"", class_=""genre"").text.rstrip().replace(""\n"", """")#(lf)        Rating = Frame[i].find(""span"", class_=""ipl-rating-star__rating"").text#(lf)        #(lf)        try:#(lf)            Score = Frame[i].find(""span"", class_=""metascore"").text.rstrip()#(lf)        except:#(lf)            Score = None#(lf)            #(lf)        Votes = Frame[i].find_all(""span"", attrs={""name"": ""nv""})[0].text#(lf)        #(lf)        try:#(lf)            Gross = Frame[i].find_all(""span"", attrs={""name"": ""nv""})[1].text#(lf)        except:#(lf)            Gross = None#(lf)            #(lf)        a = Frame[i].find_all(""p"", class_=""text-muted text-small"")[1].text.split('|')#(lf)        Director = a[0].strip().replace('\n', ' ').replace('Director: ', '').replace('Directors: ', '')#(lf)        Cast = a[1].strip().replace('\n', ' ').replace('Star: ', '').replace('Stars: ', '')#(lf)#(lf)        ImageLink = Frame[i].find(""img"", class_=""loadlate"")[""src""]#(lf)        #(lf)        details = [ArticleTitle, ListYear, Ranking, IMDBlink, Title, Date, Certificate, RunTime, Genre, Rating, Score, Votes, Gross, Director, Cast, ImageLink]#(lf)        details_list.append(details)#(lf)        #(lf)    return details_list#(lf)#(lf)# Loop through URLs and extract movie details#(lf)details_list = []#(lf)for i in range(len(all_urls)):#(lf)    list_name = all_urls.loc[i, 'list_name']#(lf)    ListYear = list_name.replace('IMDb Top 250 ', '').replace('Oscar Highlights ', '')#(lf)    # Load page 1#(lf)    page = get(all_urls.loc[i, 'link'])#(lf)    details_list.extend(extract_movie_details(page.content, ListYear))#(lf)    #(lf)    # Load page 2#(lf)    page = get(all_urls.loc[i, 'page2'])#(lf)    details_list.extend(extract_movie_details(page.content, ListYear))#(lf)    #(lf)    # Load page 3#(lf)    page = get(all_urls.loc[i, 'page3'])#(lf)    details_list.extend(extract_movie_details(page.content, ListYear))#(lf)#(lf)# Convert details to DataFrame#(lf)columns=[""List Name"", ""List Year"", ""Ranking"", ""IMDB URL"", ""Title"", ""Year"", ""Certificate"", ""RunTime"", ""Genre"", ""Rating"", ""Score"", ""Votes"", ""Gross"", ""Director"", ""Cast"", ""Image URL""]#(lf)details_df = pd.DataFrame(details_list, columns=columns)"),
    details_df = Source{[Name="details_df"]}[Value],
    #"Replaced Value" = Table.ReplaceValue(details_df," TV Movie","",Replacer.ReplaceText,{"Year"}),
    #"Clean Up Year column" = Table.TransformColumns(#"Replaced Value", {{"Year", each Text.End(_, 4), type text}}),
    #"Changed Type" = Table.TransformColumnTypes(#"Clean Up Year column",{{"List Name", type text}, {"List Year", Int64.Type}, {"Ranking", Int64.Type}, {"IMDB URL", type text}, {"Title", type text}, {"Year", Int64.Type}, {"Certificate", type text}, {"RunTime", Int64.Type}, {"Genre", type text}, {"Rating", type number}, {"Score", Int64.Type}, {"Votes", Int64.Type}, {"Gross", type text}, {"Director", type text}, {"Cast", type text} }),
    #"Added RankingGroup" = Table.AddColumn(#"Changed Type", "Ranking Group", each if [Ranking] < 50 then 1 else if [Ranking] <100 then 2 else if [Ranking] < 150 then 3 else if [Ranking] < 200 then 4 else 5),
    #"Changed RankingGroup Type" = Table.TransformColumnTypes(#"Added RankingGroup",{{"Ranking Group", Int64.Type}}),
    #"Add IMDB ID" = Table.AddColumn(#"Changed RankingGroup Type", "IMDB ID", each Text.BetweenDelimiters([IMDB URL], "/", "/", 3, 0), type text),
    #"Added List Category" = Table.AddColumn(#"Add IMDB ID", "Category", each Text.Reverse(Text.Middle(Text.Reverse([List Name]), 5)), type text)
in
    #"Added List Category"
```

----------

## Relationship
### Dependency Map
![Screenshot](../_Asset%20Library/Movies_Dependencies.png)
Tables | Relationship
---- | -----
**Plex Movies Genres** / **Plex Movies** |Many to 1
**Plex Movies Cast** / **Plex Movies** |Many to 1
**Plex Movies Country** / **Plex Movies** |Many to 1
**Plex Movies Video** / **Plex Movies** |Many to 1
**Plex Movies Audio** / **Plex Movies** |Many to 1
**Plex Movies SubTitles** / **Plex Movies** |Many to 1
**Plex Movies - CSV** / **Plex Movies** |1 to 1
**Plex Movies** / **Plex IMDB Master** | Many to 1
**Plex Movies Master** / **IMDB Master** |1 to 1
**IMDB Top Lists** / **IMDB Master** | Many to 1
**IMDB Charts** / **IMDB Master** | Many to 1

----------

## Dashboard & Reports

### 1. **Movie Collections** Page

![Screenshot](../_Asset%20Library/Movies_Dashboard.png)

- Cards - Total Movies, Collections, Studio, Library, IMDB Matched, TMDB Matched, TVDB Matched, Viewed, IMDB Top 250, Oscar Highlight, Genres, Country
- Donut Chart - by Resolution, IMDB Top 250 Coverage
- Funnel - by container, by Audio Channels, Video Codec, Audio Codec
- Map - by Country
- Stacked Column Chart - by Year and Rating Group

### 2. **Plex Movie Library** Page

![Screenshot](../_Asset%20Library/Plex_Movie_Library.png)

- Decomposition tree - by Collection and Studio
- Sankey - Audio Channels vs Audio Codec, Resolution vs Frame Rate
- Table - Plex Movies

### 3. **IMDB Pop List** Page

![Screenshot](../_Asset%20Library/IMDB_Top_List.png)

- Stacked Colum Chart - In Plex or not
- Matrix table - IMDB Top 250 / MOst Top 250 Rated English Movies
- Table - Most Popular

### 4. **IMDB Top 250 Heatmap** Page

![Screenshot](../_Asset%20Library/IMDB_Top250_Heatmap.png)

- Matrix table - IMDB Top 250 Historic Data by Year

### 5. **IMDB Top 250 Trends** Page

![Screenshot](../_Asset%20Library/IMDB_Top250_Trend.gif)

- Matrix table - IMDB Top 250 Historic Data by Released Year

### 6. *Plex Collection Card* tooltips Page
![Screenshot](../_Asset%20Library/Plex_Collection_Card.png)

### 7. *Plex Collection Card* tooltips Page
![Screenshot](../_Asset%20Library/Plex_Movie_Card.png)
----------

## Reference

----------

### Power Query Reference
- [Learn more about Power Query functions](https://docs.microsoft.com/powerquery-m/understanding-power-query-m-functions)

### Plex API
- [Finding an authentication token / X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
- [Plex Media Server API Documentation](https://www.plexopedia.com/plex-media-server/api/)
- [Plex Media Server URL Command](https://support.plex.tv/articles/201638786-plex-media-server-url-commands/)
 
    - List Base Server Capabilities: [PlexServer]/?X-Plex-Token=[*X-Plex-Token*]
    - List Defined Libraries: [PlexServer]/library/sections/?X-Plex-Token=[*X-Plex-Token*]
    - List Library Contents: [PlexServer]/library/sections/{*Movies Library Key*}/all?X-Plex-Token=[*X-Plex-Token*]
    - List Detail of an Item: [PlexServer]/library/metadata/{*Item ratingKey*}?X-Plex-Token=[*X-Plex-Token*]