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


|Parameter  |Description  |Data Type  |Reference  |
|:--------|:--------|:--------|:--------|
|**StarDate**  | Start Date for the report| Required, Type as `Date`  |    |
|**X-Plex-Token**  |token key to access Plex Server endpoints or XML|Required, Type as `Text`  |[Finding an authentication token / X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)  | 
|**PlexServer**  |Plex Server IP Address with Port Number e.g., `http://your_ip_address:32400` or `https://your_ip_address:32400`|Required, Type as `Text`  |    |
|

----------

## Data Tables

### 1 Basic Tables

#### Tables 

- **Date** Table

- **Year** Table

- **LastRefreshed** Table

### 2 Plex Tables

There are couple of options to load the movie contents from Plex Server:

1. Load data from Plex Server using **official** [Plex API](https://www.plexopedia.com/plex-media-server/api/) directly, the API commands can be run from any Web browser, sample as below: 

    > Library List: [PlexServer]/library/sections?X-Plex-Token=[X-Plex-Token]
    
    > Library Section List: [PlexServer]/library/sections/{key}/all?X-Plex-Token=[X-Plex-Token]
    
    > Movie MetaData: [PlexServer]/library/metadata/{ratingKey}?X-Plex-Token=[X-Plex-Token]

1. Load data using Python [PlexAPI](https://pypi.org/project/PlexAPI/) [Project GitHu](https://github.com/pkkid/python-plexapi), which is **unofficial** Python bindings for the Plex API; 

1. Run the Python job using [PlexAPI](https://pypi.org/project/PlexAPI/) above and export result in csv file, then use it as datasource in Power BI.

Here below is the Pros / Cons for each options:

|Option  |Description  |Pros  |Cons  |
|:-------:|:--------|:--------|:--------|
|Option 1    |Load data from Plex Server using Plex API directly  |- Direct access: Bypasses the need for any third-party libraries or tools. <br/>- Real-time data: Fetches the most up-to-date data directly from the server.  |- More complex setup: Requires manual handling of HTTP requests and parsing API responses.<br/> - Some metadata, e.g. IMDB_ID, Audio, Video, Subtitles are stored in Movie Metadata not in Library Section, need a seperate custom function to fetch data from each item|
|Option 2    |Load data using Python PlexAPI library in python script  |- Easier implementation: The library simplifies interactions with the Plex API.<br/>- Better error handling: The library is more likely to handle errors and edge cases gracefully.<br/>- Community support: Updates to the library will accommodate changes in the Plex API.  |- Dependency on external library: Need to ensure the library stays up-to-date and compatible with system.<br/>- Slower execution: Using a library cause slightly slower compared to direct API calls, depending on its implementation.  |
|Option 3    |Use Python PlexAPI and export result in csv file, then use it as data source in Power BI  |- Separation of concerns: Data extraction and processing are separated, making it easier to manage and troubleshoot.<br/>- CSV compatibility: CSV files can be easily used by various tools and platforms, providing flexibility in data analysis and visualization.  |- Not real-time: The data will only be as recent as the last time you exported the CSV file.<br/>- Additional steps: Exporting to a CSV file and importing into Power BI adds extra overhead to workflow.<br/>- Potential storage issues: Depending on the size of the dataset, you may face storage limitations or performance issues when dealing with large CSV files.  |
|

Consider about the volumn of Plex Library as well as the required columns, I am using Option 3 as primary datasource in the sample, but keep the Queries for Option 1 and Option 2 (set limit to 20 records) in the PBIX for reference.

#### 2.1.1 Option 1 - *Plex Libraries* Table

##### Parameter

- **X-Plex-Token** 
- **PlexServer**

##### Steps
1. Combine IP and X-Plex-Token into a Plex Libraries List URL, and retrive all libraries ('**Directory**');
    >Xml.Tables(Web.Contents(Text.Combine({PlexServer,"/library/sections?X-Plex-Token=",#"X-Plex-Token"})))
1. Drill down *Directory* into a table;
1. Expand *Location* to Folder Path;
1. Combine IP and X-Plex-Token into Plex Content Library URL;
    >Uri.Combine(Text.Combine({IP,":32400/"}) as text, Text.Combine({"library/sections/",Text.From([#"Attribute:key"]),"/all?X-Plex-Token=",#"X-Plex-Token"}) as text)
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

#### 2.1.2 Option 1 - Custom Function - *Load Movie Contents*

NOTE: it only returns result from [Library Section](https://www.plexopedia.com/plex-media-server/api/library/movies/) not Movie Metadata, therefore no detail about **Audio**, **Video**, **Subtitles**, **IMDB_ID**, **TMDB_ID** or **TVDB_ID** information.

###### Parameter

- **X-Plex-Token**; 
- **LibraryURL**: Required, Format like `[PLEX_URL]/library/sections/{key}/all?X-Plex-Token=[PLEX_TOKEN]` (can be copied from **Plex Libraries** Table above)

###### Steps

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

#### 2.1.3 Option 1 - *Plex Movies - API* Table

##### Dependency

- **Plex Libraries** Table;
- **Load Movie Content** Custom Function

##### Steps
1. Reference from **Plex Libraries** Table above;
1. Filter **Type** = '*movie*' and **Scanner** = '*Plex Movie*';
1. Invoke **Load Movie Content** Function from Library *URL* field;
1. Add **Runtime** column and calculate base on *Duration* field, and format result into HH:MM:SS format by removing *Date* and *AM*;

    >Text.From(#datetime(1970, 1, 1, 0, 0, 0) + #duration(0, 0, 0, [Duration]/1000))
1. Combine PlexServer, Item Key and X-Plex-Token into **MetadatURL**;

    >= Text.Combine({PlexServer, [key], "?X-Plex-Token=",#"X-Plex-Token"})

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
#### 2.2 Option 2 - *Plex Movies - Python* Table

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
1. Change **PlexMetadata_ID**, **IMDB_ID**, **TMDB_ID**, **TVDB_ID** to `text`.

##### Python Code
    ```python
    from plexapi.server import PlexServer
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util import Retry
    import pandas as pd
    
    # Fill in your Plex server details.
    PLEX_URL = [PlexServer] # e.g., 'http://192.168.0.1:32400' or 'https://192.168.0.1:32400'
    PLEX_TOKEN = [X-Plex-Token]
    
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
        columns = ["PlexMetadata ID", "Title", "Sort Title", "Original Title", "Library", "Genres", "Content Rating", "Collection", "Studio", "Director", "Cast", "Summary", "Country", "IMDB ID", "TMDB ID", "TVDB ID", "View Count", "Audience Rate", "Release Date", "Year", "Added Date", "IMDB Duration (mins)", "Duration (mins)", "Aspect Ratio", "Frame Rate","Container", "Video Codec", "Audio Codec", "Audio Channels", "Audio", "Video", "Subtitles"]
        
        # Create an empty DataFrame with these columns
        df = pd.DataFrame(columns=columns, dtype=object)
    
        # Add movie details to the DataFrame, currently only return the first 10 records from library
        movie_count = 0
        for movie in movie_list:
            if movie_count >= 10:
                break
            row = print_movie_details(movie)
            df.loc[len(df)] = pd.Series(row, index=df.columns)
            movie_count += 1
    
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
        
        # Prepare movie details in tab-separated format.
        row = [
            str(movie.ratingKey),
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

#### 2.3 Option 3 - *Plex Movies - CSV* Table

##### Paramter
- **X-Plex-Token** 
- **PlexServer**

##### Dependency
- pandas
    > pip install pandas

- plexapi
    > pip install plexapi

##### Steps
1. Update the 3 Variable below and run the Python Script locally to export the file as csv format;
1. Import the csv file into Power BI;
1. Add **Resolution** column from **Video**;
1. Add **IMDB_URL** column using **IMDB_ID**;
1. Change **PlexMetadata_ID**, **IMDB_ID**, **TMDB_ID**, **TVDB_ID** to `text`.

##### Python Code
    ```python
    from plexapi.server import PlexServer
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util import Retry
    import pandas as pd
    
    # Fill in your Plex server details.
    PLEX_URL = [PlexServer] # e.g., 'http://192.168.0.1:32400' or 'https://192.168.0.1:32400'
    PLEX_TOKEN = [X-Plex-Token]
    EXPORT_FILE = [Filename.csv] #e.g., 'Plex_movie_details.csv'
    
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
        columns = ["PlexMetadata ID", "Title", "Sort Title", "Original Title", "Library", "Genres", "Content Rating", "Collection", "Studio", "Director", "Cast", "Summary", "Country", "IMDB ID", "TMDB ID", "TVDB ID", "View Count", "Audience Rate", "Release Date", "Year", "Added Date", "IMDB Duration (mins)", "Duration (mins)", "Aspect Ratio", "Frame Rate","Container", "Video Codec", "Audio Codec", "Audio Channels", "Audio", "Video", "Subtitles"]
        
        # Create an empty DataFrame with these columns
        df = pd.DataFrame(columns=columns, dtype=object)
    
        # Add movie details to the DataFrame, currently only return the first 10 records from library
        movie_count = 0
        for movie in movie_list:
            if movie_count >= 10:
                break
            row = print_movie_details(movie)
            df.loc[len(df)] = pd.Series(row, index=df.columns)
            movie_count += 1
    
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
        
        # Prepare movie details in tab-separated format.
        row = [
            str(movie.ratingKey),
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
        result_df.to_csv(EXPORT_FILE, index=False, encoding='utf-8')
    
    ```

### *IMDB Top 250 List* Current Table

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

##### Python Code

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


----------

## Relationship

----------

## Reports

----------

## Reference


----------

### Power Query Reference
- [Learn more about Power Query functions](https://docs.microsoft.com/powerquery-m/understanding-power-query-m-functions)
- [Fuzzy Matching](https://learn.microsoft.com/en-us/power-query/fuzzy-matching)


### Plex API
- [Finding an authentication token / X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
- [Plex Media Server API Documentation](https://www.plexopedia.com/plex-media-server/api/)
- [Plex Media Server URL Command](https://support.plex.tv/articles/201638786-plex-media-server-url-commands/)
 
    - List Base Server Capabilities: [PlexServer]/?X-Plex-Token=[*X-Plex-Token*]
    - List Defined Libraries: [PlexServer]/library/sections/?X-Plex-Token=[*X-Plex-Token*]
    - List Library Contents: [PlexServer]/library/sections/{*Movies Library Key*}/all?X-Plex-Token=[*X-Plex-Token*]
    - List Detail of an Item: [PlexServer]/library/metadata/{*Item ratingKey*}?X-Plex-Token=[*X-Plex-Token*]