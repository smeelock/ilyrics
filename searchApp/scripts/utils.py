# ======================================
#                Useful
# ======================================

import os
import zipfile
from itertools import islice
from tqdm import tqdm

from ..models import Song
        
WORKERS = 5

def unzip(zip_file, target_dir):
    with zipfile.ZipFile(zip_file, 'r') as f:
        f.extractall(target_dir)
    print(f"Unzipped {os.path.basename(zip_file)} into {target_dir}.")

def removeDuplicates():
    """ Removes duplicates. Extremely inefficient because checks for each combination title/artist..."""
    # find duplicates
    artists = Song.objects.values_list('artist', flat=True).distinct()
    print(f"Database info: {Song.objects.all().count()} (total), {len(artists)} (artists)")
    def _find_duplicates(artist):
        duplicates = []
        titles = Song.objects.filter(artist=artist).values_list('title', flat=True).distinct()
        for title in titles:
            ids = Song.objects.filter(title=title, artist=artist).values_list('id', flat=True)
            d = Song.objects.filter(pk__in=ids[1:])
            if d.exists():
                duplicates += list(d)
        if len(duplicates) > 0:
            print(f"*Found {len(duplicates)} duplicates for artist {artist}")
            return duplicates

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        results = list(executor.map(_find_duplicates, artists))
    
    to_delete = []
    for res in results:
        if res:
            to_delete += [r.pk for r in res] # store id of songs to delete

    # remove duplicates
    if input(f"Found {len(to_delete)} duplicates, continue and remove them from database? [y/N] ").lower().strip() in ['yes', 'y', 'ok']:
        Song.objects.filter(pk__in=to_delete).delete() # bulk delete duplicates
        # def _delete_duplicates(d):
        #     d.delete() # remove duplicates and only keep first one
        #     print(f"*Removed {len(d)} duplicates")
        
        # with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        #     executor.map(_delete_duplicates, to_delete)

        print(f"DONE! Removed {len(to_delete)} duplicates from database!")
    else:
        print("Aborted")

def addSongs(iterator, batch_size=100):
    # def _add_one_song(song):
    #     new_song = Song(title=song['title'], artist=song['artist'], lyrics=song['lyrics'])
    #     new_song.save()
    #     print(f"*Added {song['title']} by {song['artist']}")

    # with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
    #     executor.map(_add_one_song, iterator)
    # print(f"Added {len(iterator)} songs to index.")
    songs = []
    for song in tqdm(iterator, desc="songs"):
        new_song = Song(title=song['title'], artist=song['artist'], lyrics=song['lyrics'])
        songs.append(new_song)
    while True:
        batch = list(islice(songs, batch_size))
        if not batch:
            break
        Song.objects.bulk_create(batch, batch_size)
        print(f"*Added {batch_size} songs to index")