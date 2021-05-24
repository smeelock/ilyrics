from itertools import islice
from tqdm import tqdm
import concurrent.futures

from django.core.management.base import BaseCommand
from searchApp.models import Song
from . import _dataloader as dataloader
from . import _utils as utils

# ======================================
#          addSongs command
# ======================================
class Command(BaseCommand):
    help = "Add songs to index from a given dataset"

    def add_arguments(self, parser):
        # positional arguments
        available_datasets = ['kaggle', 'spotify', 'azlyrics']
        parser.add_argument('dataset', type=str, choices=available_datasets, metavar="DATASET", 
            help="which dataset to add, must be one of {}".format(' | '.join(available_datasets)))
        parser.add_argument('location', type=str, metavar="LOCATION", 
            help="location of the dataset files (.zip)")

        # optional arguments
        parser.add_argument('--batch-size', type=int, default=1000, 
            help="bulk_create batch size")
        parser.add_argument('-f', '--force', action='store_true',
            help="force deletion without verification")
        parser.add_argument('--cache', type=str, default="../data/", 
            help="directory where to unzip temporary files")

    def handle(self, *args, **options):
        # get the dataset's dataloader
        load_data = getattr(dataloader, options['dataset'])
        loaded_songs = load_data(options['location'], options['cache'])

        # existing artists/titles
        existing_artists = Song.objects.values_list('artist', flat=True).distinct()
        existing_titles = Song.objects.values_list('title', flat=True).distinct()

        # verify duplicates
        songs = []
        for song in tqdm(loaded_songs, desc="songs"):
            if (song['title'] not in existing_titles) and (song['artist'] not in existing_artists):
                new_song = Song(title=song['title'], artist=song['artist'], lyrics=song['lyrics'])
                songs.append(new_song)
        
        # add songs
        if options['force'] or (input(f"Insert {len(songs)} songs to database? [y/N] ").lower().strip() in ['yes', 'y', 'ok']):
            for batch in utils.makeBatches(songs, options['batch_size']):
                Song.objects.bulk_create(batch, options['batch_size'], ignore_conflicts=True)
                self.stdout.write(f"*Added {options['batch_size']} songs")

            self.stdout.write(self.style.SUCCESS(f"Successfully added {len(songs)} songs to index"))