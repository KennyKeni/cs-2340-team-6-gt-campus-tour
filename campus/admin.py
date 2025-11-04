from django.contrib import admin

from .models import Bookmark, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'has_photo', 'latitude', 'longitude')
    search_fields = ('name', 'category', 'description', 'historical_info')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Location Data', {
            'fields': ('latitude', 'longitude', 'address')
        }),
        ('Historical & Media', {
            'fields': ('historical_info', 'photo')
        }),
    )

    def has_photo(self, obj):
        return bool(obj.photo)
    has_photo.boolean = True
    has_photo.short_description = 'Has Photo'


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'location__name')
