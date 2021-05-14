from django.db import models

class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    lyrics = models.TextField()

    def __str__(self):
        return self.title

# class Artist(models.Model):
#     # TODO:
