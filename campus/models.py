from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Location(models.Model):
    """
    Represents a campus location or point of interest.
    Admins can add, edit, or remove these to keep campus information accurate.
    """

    name = models.CharField(
        max_length=120,
        unique=True,
        help_text="Displayed name of the campus location.",
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        help_text="URL-friendly identifier auto-generated from the name.",
    )
    description = models.TextField(
        help_text="High-level overview that appears in campus tour content.",
    )
    historical_info = models.TextField(
        blank=True,
        null=True,
        help_text="Optional historical context or fun facts for visitors.",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Latitude in decimal degrees (positive for north).",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Longitude in decimal degrees (negative for west).",
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        help_text="Street address or building details shown in the tour.",
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Category used for filtering (e.g., Dining, Academic).",
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        help_text="Link to an external photo if one is hosted elsewhere.",
    )
    photo = models.ImageField(
        upload_to='locations/photos/',
        blank=True,
        null=True,
        help_text="Upload location photo.",
    )

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        """
        Automatically generate a slug from the name if not provided.
        Example: 'Tech Tower' → 'tech-tower'
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Bookmark(models.Model):
    """
    Represents a user's bookmarked campus location.
    Allows visitors to save locations for quick access.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        help_text="The user who bookmarked this location.",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        help_text="The location that was bookmarked.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this bookmark was created.",
    )

    class Meta:
        unique_together = ['user', 'location']
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user.username} → {self.location.name}"


class TourBookmark(models.Model):
    """
    Represents a user's bookmarked tour.
    Allows visitors to save tours for quick access.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tour_bookmarks',
        help_text="The user who bookmarked this tour.",
    )
    tour = models.ForeignKey(
        'Tour',
        on_delete=models.CASCADE,
        related_name='bookmarks',
        help_text="The tour that was bookmarked.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this bookmark was created.",
    )

    class Meta:
        unique_together = ['user', 'tour']
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user.username} → {self.tour.name}"


class Tour(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    route_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Cached route segments from Google Directions API"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.name


class TourStop(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='stops')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = [['tour', 'location']]

    def __str__(self) -> str:
        return f"{self.tour.name} - {self.location.name} (#{self.order})"


class Rating(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings',
        help_text="The user who submitted this rating.",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='ratings',
        help_text="The location being rated.",
    )
    score = models.PositiveIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rating score from 1 to 5 stars.",
    )
    comment = models.TextField(
        blank=True,
        help_text="Optional feedback comment from the user.",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        help_text="Admin review status of this feedback.",
    )
    admin_response = models.TextField(
        blank=True,
        help_text="Admin response to user feedback.",
    )
    responded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_responses',
        help_text="Admin who responded to this feedback.",
    )
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the admin responded.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this rating was submitted.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this rating was last updated.",
    )

    class Meta:
        unique_together = ['user', 'location']
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user.username} rated {self.location.name}: {self.score}/5"


class SharedTour(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tours_shared')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tours_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tour', 'shared_with')
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.shared_by.username} shared {self.tour.name} with {self.shared_with.username}"
