from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Manga(models.Model):
    title = models.CharField(max_length=300)
    mangadex_id = models.CharField(max_length=150, unique=True)
    anilist_id = models.CharField(max_length=150, unique=True)
    description = models.CharField(max_length=2000)
    cover_art = models.CharField(max_length=150, unique=True)
    total_chapters = models.IntegerField()

    def __str__(self):
        return self.title


class Book(models.Model):
    title = models.CharField(max_length=300)
    book_id = models.CharField(max_length=150, unique=True)
    description = models.CharField(max_length=500)
    cover_art = models.CharField(max_length=150, unique=True)
    total_page = models.IntegerField()

    def __str__(self):
        return self.title


class Anime(models.Model):
    title = models.CharField(max_length=300)
    anilist_id = models.CharField(max_length=150, unique=True)
    description = models.CharField(max_length=2000)
    cover_art = models.CharField(max_length=150, unique=True)
    total_episodes = models.IntegerField()
    duration = models.IntegerField(null=True)

    def __str__(self):
        return self.title


class Progress(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('ANIME', 'Anime'),
        ('MANGA', 'Manga'),
        ('BOOK', 'Book'),
    ]
    STATUS_CHOICES = [
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('ON_HOLD', 'On Hold'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    media_id = models.IntegerField()
    episode_number = models.IntegerField(null=True, blank=True)
    chapter_number = models.IntegerField(null=True, blank=True)
    page_number = models.IntegerField(null=True, blank=True)
    star_rate = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return self.media_id
