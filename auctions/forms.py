from django import forms
from .models import Listing, Category

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 5}),
            'category': forms.Select(choices=[(cat.id, cat.name) for cat in Category.objects.all()])
        }
