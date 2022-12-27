# Plex Movie Collections

## Datasources

### IMDB Top 250 Lists (1996-2021)
<ol>
    <li> Download the IMDB Top 250 from [Kaggle](https://www.kaggle.com/datasets/mustafacicek/imdb-top-250-lists-1996-2020?resource=download "Top 250 List");
    <li> Extract ZIP file into a folder;
</ol>

### Plex API
`GET http://[IP address]:32400/library/sections/[Movies Library ID]/all?X-Plex-Token=[PlexToken]`
#### [Get All Movies](https://www.plexopedia.com/plex-media-server/api/library/movies/)
