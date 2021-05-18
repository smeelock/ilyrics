from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Song
from .documents import SongDocument
from .scripts import genius, utils

def index(request):
    return render(request, 'searchApp/index.html', {})

def search(request):
    try :
        queryterms = request.GET['q']
        assert queryterms

        # ask genius and update index
        _ = genius.askGenius(queryterms, update_index=True)
    
        # ask indexed songs
        query = "*" + "* *".join(queryterms.split()) + "*"
        top = SongDocument.search().query('multi_match', query=query, fields=['title', 'artist', 'lyrics'], type="cross_fields").execute()
        songs = SongDocument.search().query('multi_match', query=query, fields=['title', 'artist'], type="cross_fields").execute()
        lyrics = SongDocument.search().query('multi_match', query=query, fields=['lyrics']).highlight('lyrics', fragment_size=30).execute()

        # print(lyrics[0].meta.highlight.lyrics)
        context = {
            'query': queryterms,
            'top_result': top[0] if top else None,
            'song_results': songs,
            'lyric_results': lyrics,
        }
        return render(request, 'searchApp/search.html', context)

    except Exception as e:
        print("An error occurred, redirecting to index... \n\t", e)
        return redirect('/') 

def song(request, songid):
    try: 
        song = Song.objects.get(pk=songid)
        assert song, "Invalid songid"
        metadata = { 'title': song.title, 'artist': song.artist, 'lyrics': song.lyrics }
        hits = genius.askGenius(f"{song.title} {song.artist}", update_index=False)

        if hits is not None and len(hits) > 0:
            best = genius.getSong(hits[0]['id'])
            if best:
                metadata['cover'] = best['song_art_image_url']
                metadata['album'] = best['album']['name'] if best['album'] else ""
                metadata['url'] = best['url']
                metadata['media'] = best['media']


        context = {
            'song': metadata,
        }
        return render(request, 'searchApp/song.html', context)
    
    except Exception as e:
        print("An error occurred, redirecting to search results... \n\t", e)
        # return to previous page if http_refere is set, else redirect to homepage
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", '/'))

    # return HttpResponseRedirect(reverse('song', kwargs=context))