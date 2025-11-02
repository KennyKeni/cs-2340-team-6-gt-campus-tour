from django.contrib import admin

from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'latitude', 'longitude')
    search_fields = ('name', 'category', 'description')
    prepopulated_fields = {'slug': ('name',)}
