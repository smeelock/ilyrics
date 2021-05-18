from tqdm import tqdm
import concurrent.futures

from django.core.management.base import BaseCommand, CommandError
from searchApp.models import Song

class Command(BaseCommand):
    # NOTE: Extremely inefficient because checks for each combination title/artist...
    help = "Removes duplicates from database"

    def add_arguments(self, parser):
        parser.add_argument('--workers', type=int, default=5, help="number of workers")
        parser.add_argument('-f', '--force', action='store_true', help="force deletion without verification")

    def handle(self, *args, **options):
        self.stdout.write("*"*40)
        self.stdout.write("Starting remove_duplicates")
        # find duplicates
        artists = Song.objects.values_list('artist', flat=True).distinct()
        self.stdout.write(f"Database info: {Song.objects.all().count()} (total), {len(artists)} (artists)")

        with tqdm(total=len(artists), desc="Find duplicates") as pbar:
            # /!\ thread unsafe
            # TODO: make it trade safe
            def _find_duplicates(artist):
                duplicates = []
                titles = Song.objects.filter(artist=artist).values_list('title', flat=True).distinct()
                for title in titles:
                    ids = Song.objects.filter(title=title, artist=artist).values_list('id', flat=True)
                    d = Song.objects.filter(pk__in=ids[1:])
                    if d.exists():
                        duplicates += list(d)
                pbar.update(1)
                if len(duplicates) > 0:
                    self.stdout.write(f"*Found {len(duplicates)} duplicates for artist {artist}")
                    return duplicates

            with concurrent.futures.ThreadPoolExecutor(max_workers=options['workers']) as executor:
                results = list(executor.map(_find_duplicates, artists))
        
        to_delete = []
        for res in results:
            if res:
                to_delete += [r.pk for r in res] # store id of songs to delete

        # remove duplicates
        if options['force'] or (input(f"Found {len(to_delete)} duplicates, continue and remove them from database? [y/N] ").lower().strip() in ['yes', 'y', 'ok']):
            Song.objects.filter(pk__in=to_delete).delete() # bulk delete duplicates
            
            self.stdout.write(self.style.SUCCESS(f"Successfully removed {len(to_delete)} duplicates from database!"))
        else:
            self.stdout.write("Aborted")