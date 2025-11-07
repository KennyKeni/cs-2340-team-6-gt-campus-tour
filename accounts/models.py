from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='United States')
    affiliation = models.CharField(max_length=100, blank=True, default='')
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"
