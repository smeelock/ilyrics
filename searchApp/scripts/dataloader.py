# ======================================
#              Data Loader
# ======================================
# used to load data from downloaded datasets in order to update the index

import os
import pandas as pd

from . import utils
DATA_DIR = "../data"


def kaggle_dataset(zipfile):
    """ Load kaggle dataset and return an iterator over all songs """
    target_dir = f"{DATA_DIR}/kaggle/"
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
    # data = data.drop_duplicates(subset=['artist', 'lyrics'], keep='first')
    return data.to_dict(orient='records')
    return data.to_dict(orient='records')

