from tqdm import tqdm
from ..models import Song

def removeDuplicates():
    """ Removes duplicates. Extremely inefficient because checks for each combination title/artist..."""
    artists = Song.objects.values_list('artist', flat=True).distinct()

    to_delete = []
    for artist in tqdm(artists, desc="Find duplicates"):
        titles = Song.objects.filter(artist=artist).values_list('title', flat=True).distinct()
        for title in titles:
            duplicates = Song.objects.filter(title=title, artist=artist).values_list('id', flat=True)
            deletes = Song.objects.filter(pk__in=duplicates[1:])
            to_delete.append(deletes)

            # to_delete.delete() # remove duplicates and only keep first one
    if input(f"Found {len(to_delete)} duplicates, continue and remove them from database? [y/N] ").lower().strip() in ['yes', 'y', 'ok']:
        for d in tqdm(to_delete, desc="Remove duplicates"):
            d.delete() # remove duplicates and only keep first one
        print(f"Removed {len(to_delete)} duplicates from database!")
    else:
        print("Aborted.")