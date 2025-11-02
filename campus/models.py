from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name
