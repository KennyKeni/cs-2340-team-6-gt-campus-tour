from django import forms
from .models import Location

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = [
            'name',
            'description',
            'historical_info',
            'latitude',
            'longitude',
            'address',
            'category',
            'photo',
            'image_url',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'historical_info': forms.Textarea(attrs={'rows': 3}),
        }
