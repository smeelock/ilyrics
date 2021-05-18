import os
from bs4 import BeautifulSoup
import requests
import urllib
import concurrent.futures

# with concurrent.futures.ThreadPoolExecutor(max_workers=13) as executor:
#     executor.map(populateDB, "0abcdefghijklmnopqrstuvwxyz")

from ..models import Song
WORKERS = 5

# tokens and auth stuff
GENIUS_ACCESS_TOKEN = os.environ['GENIUS_ACCESS_TOKEN']
agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
headers = {'User-Agent': agent, 'Authorization': "Bearer "+ GENIUS_ACCESS_TOKEN }

# use genius API to get a song
def askGenius(query, update_index=False):
    """ Returns hits after asking 'www.api.genius.com' """
    try :
        url_api = "https://api.genius.com/"
        url_search = "search?q="
        url = "{}{}{}".format(url_api, url_search, query.replace('\s', '+'))
        response = requests.get(url, headers=headers)
        
        hits = [h['result'] for h in response.json()['response']['hits']]
        if update_index:
            # check if not already in db
            used_titles = set(Song.objects.values_list('title', flat=True))
            used_artists = set(Song.objects.values_list('artist', flat=True))
            
            def _update(hit):
                title, artist = hit['title_with_featured'], hit['primary_artist']['name']
                if (title not in used_titles) or (artist not in used_artists):
                    lyrics = getLyrics(hit)
                    if lyrics:
                        s = Song(title=title, artist=artist, lyrics=lyrics)
                        s.save()
                        print(f"Adding 1 song to index: '{title}' by '{artist}'")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
                executor.map(_update, hits)
        return hits

    except Exception as e:
        print("An error occurred while asking Genius.com, ignoring... ", e)
        return None

def getLyrics(hit):
    # CAUTION: hit must have a genius url (hit['url'])
    try :
        html = BeautifulSoup(requests.get(hit['url'], headers=headers).text, 'html.parser')
        
        # find lyrics in page
        if html.find(attrs={'class': "lyrics"}):
            lyrics = html.find(attrs={'class': "lyrics"})
        elif html.find(attrs={'class': "song_body-lyrics"}):
            lyrics = html.find(attrs={'class': "song_body-lyrics"})
        elif html.find('lyrics'):
            lyrics = html.find('lyrics')
        
        assert lyrics, "Couldn't find lyrics."
        
        lyrics = lyrics.get_text().encode('utf-8', 'ignore').decode('utf-8') # decode to transform bytes to str
        return lyrics
    except Exception as e:
        print(f"An error occurred while scraping lyrics for '{hit['title']}' by '{hit['primary_artist']['name']}' \n\t Ignoring: ", e)
        return None

def getSong(song_id):
    try :
        url = f"https://api.genius.com/songs/{song_id}"
        response = requests.get(url, headers=headers)
        
        song = response.json()['response']['song']
        return song

    except Exception as e:
        print("An error occurred while asking Genius.com, ignoring... \n\t", e)
        return None