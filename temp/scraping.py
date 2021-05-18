import os
import json
import requests
from bs4 import BeautifulSoup

agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
headers = {'User-Agent': agent}

class AZLyrics:
    def __init__(self):
        self.base_url = "https://www.azlyrics.com"

    def populateDatabase(self):
        def _getArtists(letter):
            res = requests.get(f"{self.base_url}/{letter}.html", headers=headers)
            soup = BeautifulSoup(res.content, 'html.parser')
            artists = soup.find('div', attrs={'class': 'container main-page'}).findAll('a')
            return {a.text.strip(): f"{self.base_url}/{a.get('href')}" for a in artists}

        def _getSongs(artist_url):
            res = requests.get(artist_url, headers=headers)
            soup = BeautifulSoup(res.content, 'html.parser')
            songs = soup.findAll('div', attrs={'class': 'listalbum-item'})
            return {s.find('a').text.strip(): f"{self.base_url}/{s.find('a').get('href')}" for s in songs}

        def _getLyrics(songs_url):
            res = requests.get(song_url, headers=headers)
            soup = BeautifulSoup(res.content, 'html.parser')
            lyrics = soup.find('div', attrs={"class": None, "id": None})
            return lyrics.getText()
        
        all_artists = {}
        for letter in "abcdefghijklmnopqrstuvwxyz":
            all_artists = {**all_artists, **_getArtists(letter)}
        all_artists = {**all_artists, **_getArtists('19')}

        pk = 0
        with open('azlyrics_songs.txt', 'a') as songfile:
            for artist, artist_url in all_artists.items():
                for song, song_url in _getSongs(artist_url).items():
                    s = {
                        'model': "searchApp.Song",
                        'pk': pk,
                        'fields': {
                            'title': song,
                            'artist': artist,
                            'lyrics': _getLyrics(song_url),
                            }
                        }
                    json.dump(s, songfile)
                    songfile.write("\n")
                    
                    pk += 1
                    print(f"{pk} songs added so far !")

class Lyrics:
    def __init__(self):
        self.base_url = "https://www.lyrics.com"
    
    def populateDatabase(self):
        def _getArtists(letter):
            res = requests.get(f"{self.base_url}/artists/{letter.upper()}/99999", headers=headers)
            soup = BeautifulSoup(res.content, 'html.parser')
            artists = soup.find('div', attrs={'id': 'content-body'}).findAll('strong')
            all_artists = {}
            for artist in artists:
                a = artist.find('a')
                if a:
                    all_artists = {**all_artists, **{a.text.strip(): f"{self.base_url}/{a.get('href')}"}}
            return all_artists

        def _getSongs(artist_url):
            res = requests.get(artist_url, headers=headers)
            soup = BeautifulSoup(res.content, 'html.parser')
            songs = soup.find('div', attrs={'id': 'content-body'}).findAll('strong')
            all_songs = {}
            for song in songs:
                s = song.find('a')
                if s:
                    all_songs = {**all_songs, **{ s.text.strip(): f"{self.base_url}/{s.get('href')}" }}
            return all_songs

        def _getLyrics(song_url):
            res = requests.get(song_url, headers=headers)
            soup = BeautifulSoup(res.content, 'html.parser')
            lyrics = soup.find('pre', attrs={'id': 'lyric-body-text'})
            if lyrics:
                return lyrics.getText()
            return ""
        
        # populateDatabase
        pk = 0
        with open('lyrics_songs.txt', 'a') as songfile:
            for letter in "0abcdefghijklmnopqrstuvwxyz":
                artists = _getArtists(letter)
                for artist, artist_url in artists.items():
                    songs = _getSongs(artist_url)
                    for song, song_url in songs.items():
                        s = {
                            'model': "searchApp.Song",
                            'pk': pk,
                            'fields': {
                                'title': song,
                                'artist': artist,
                                'lyrics': _getLyrics(song_url),
                            }
                        }
                        json.dump(s, songfile)
                        songfile.write("\n")

                        pk += 1
                        print(f"{pk} songs added so far !")