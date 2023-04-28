from plexapi.server import PlexServer
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import pandas as pd

# Fill in your Plex server details.
PLEX_URL = ['Your Plex Server'] # e.g., 'http://{your_ip_address}:32400' or 'https://{your_ip_address}:32400'
PLEX_TOKEN = ['Your Plex Token'] # Find from https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
EXPORT_FILE = ['Plex_movie_details.csv'] # Output CSV file

class InsecureHttpAdapter(HTTPAdapter):
    """An adapter that disables SSL certification validation."""

    def cert_verify(self, *args, **kwargs):
        return None

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        pool_kwargs['assert_hostname'] = False
        super(InsecureHttpAdapter, self).init_poolmanager(connections, maxsize, block, **pool_kwargs)

def get_insecure_requests_session():
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

    # Add movie details to the DataFrame
#    movie_count = 0
    for movie in movie_list:
#        if movie_count >= 10:
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
