from django.contrib import admin
from django.utils.html import format_html

from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'thumbnail', 'latitude', 'longitude')
    list_editable = ('category',)
    list_filter = ('category',)
    search_fields = ('name', 'category', 'description', 'historical_info')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('thumbnail',)
    fieldsets = (
        ('Basic details', {
            'fields': ('name', 'slug', 'category', 'description', 'historical_info'),
        }),
        ('Location data', {
            'fields': ('latitude', 'longitude', 'address'),
        }),
        ('Media', {
            'fields': ('thumbnail', 'photo', 'image_url'),
        }),
    )

    def thumbnail(self, obj):
        """
        Render a small preview of the uploaded photo or fallback to the external image URL.
        """
        source = obj.photo.url if obj.photo else obj.image_url
        if source:
            return format_html(
                '<img src="{}" alt="{} photo" style="max-height: 60px; border-radius: 4px;" />',
                source,
                obj.name,
            )
        return 'No photo'

    thumbnail.short_description = 'Photo'
