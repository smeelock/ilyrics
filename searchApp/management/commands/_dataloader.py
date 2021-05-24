# ======================================
#              Data Loader
# ======================================
# load data from downloaded datasets in order to update the index

import os
import pandas as pd

from . import _utils as utils

def kaggle(zipfile, cache):
    """ Load kaggle dataset and return an iterator over all songs """
    target_dir = f"{cache}/kaggle/"
    utils.unzip(zipfile, target_dir)
    
    # read data
    artist_filename = os.path.join(target_dir, "artists-data.csv")
    lyrics_filename = os.path.join(target_dir, "lyrics-data.csv")
    artists = pd.read_csv(artist_filename, usecols=['Artist', 'Link'])
    lyrics = pd.read_csv(lyrics_filename, usecols=['ALink', 'SName', 'Lyric'])
    data = lyrics.merge(artists, left_on='ALink', right_on='Link', how='inner')
    data = data.dropna(axis=0, how='any')
    data['title+artist'] = data['SName'] + data['Artist']
    data = data.drop_duplicates('title+artist', keep='first')

    # format data
    data = data.rename(columns={'SName': 'title', 'Lyric': 'lyrics', 'Artist': 'artist'})[
        ['title', 'artist', 'lyrics']]
    data = data.drop_duplicates(subset=['artist', 'lyrics'], keep='first')
    return data.to_dict(orient='records')

def spotify(zipfile, cache):
    """ Load spotify_billboard dataset and return an iterator over all songs """
    target_dir = f"{cache}/spotify_billboard/"
    utils.unzip(zipfile, target_dir)

    # read data
    filename = os.path.join(target_dir, 
        f"{os.path.splitext(os.path.basename(zipfile))[0]}/billboard_2000_2018_spotify_lyrics.csv")
    data = pd.read_csv(filename, usecols=['title', 'main_artist', 'lyrics'])
    data = data.dropna(axis=0, how='any')
    
    # format data
    data = data.rename(columns={'main_artist': 'artist'})
    return data.to_dict(orient='records')

def azlyrics(zipfile, cache):
    """ Load manually scraped lyrics from azlyrics.com """
    target_dir = f"{cache}/azlyrics/"
    utils.unzip(zipfile, target_dir)

    # read data
    data = pd.DataFrame(columns=['title', 'artist', 'lyrics'])
    for json_file in os.listdir(target_dir):
        records = []
        with open(json_file, 'r') as f:
            for r in f:
                records.append(r['fields'])
        data = pd.concat([data, pd.DataFrame(records)])
    data = data.dropna(axis=0, how='any')

    # format data 
    return data.to_dict(orient='records')

