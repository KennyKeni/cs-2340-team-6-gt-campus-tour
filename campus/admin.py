from django.contrib import admin
from django.utils.html import format_html

from django.utils import timezone
from .models import Location, Bookmark, Tour, TourStop, Rating


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


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'location__name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_official', 'created_at')
    list_editable = ('is_official',)
    search_fields = ('name', 'description', 'user__username')
    list_filter = ('is_official', 'created_at')


@admin.register(TourStop)
class TourStopAdmin(admin.ModelAdmin):
    list_display = ('tour', 'location', 'order')
    list_filter = ('tour',)
    search_fields = ('tour__name', 'location__name')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'score_display', 'status', 'created_at', 'has_response')
    list_filter = ('status', 'score', 'location', 'created_at')
    search_fields = ('user__username', 'location__name', 'comment', 'admin_response')
    readonly_fields = ('user', 'location', 'score', 'comment', 'created_at', 'updated_at', 'responded_by', 'responded_at')
    ordering = ('-created_at',)
    list_editable = ('status',)

    fieldsets = (
        ('User Feedback', {
            'fields': ('user', 'location', 'score', 'comment', 'created_at', 'updated_at'),
        }),
        ('Admin Response', {
            'fields': ('status', 'admin_response', 'responded_by', 'responded_at'),
        }),
    )

    def score_display(self, obj):
        stars = '★' * obj.score + '☆' * (5 - obj.score)
        return format_html('<span style="color: #f59e0b;">{}</span>', stars)
    score_display.short_description = 'Rating'

    def has_response(self, obj):
        if obj.admin_response:
            return format_html('<span style="color: green;">Yes</span>')
        return format_html('<span style="color: gray;">No</span>')
    has_response.short_description = 'Responded'

    def save_model(self, request, obj, form, change):
        if 'admin_response' in form.changed_data and obj.admin_response:
            obj.responded_by = request.user
            obj.responded_at = timezone.now()
        super().save_model(request, obj, form, change)
