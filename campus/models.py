from django.contrib.auth.models import User
from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True)
    historical_info = models.TextField(blank=True)
    photo = models.ImageField(upload_to='locations/', blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'location')
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user.username} bookmarked {self.location.name}"
