from django import forms
from .models import Listing, Category
from django.core.exceptions import ValidationError

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 5}),
            'image_url': forms.URLInput(attrs={'placeholder': 'http://example.com/image.jpg'}),
        }


    def __init__(self, *args, **kwargs):
        super(ListingForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()  # Dynamically load the choices
        self.fields['category'].widget = forms.Select()

class BidForm(forms.Form):
    bid_amount = forms.DecimalField(decimal_places=2, max_digits=12, label="Your Bid")

    def __init__(self, *args, **kwargs):
        self.listing = kwargs.pop('listing', None)
        super().__init__(*args, **kwargs)

    def clean_bid_amount(self):
        amount = self.cleaned_data['bid_amount']
        if amount <= 0:
            raise ValidationError('The bid must be greater than zero.')
        if self.listing and amount <= self.listing.starting_bid:
            raise ValidationError(f'The bid must be higher than the starting bid of ${self.listing.starting_bid}.')
        if self.listing and self.listing.bids.exists():
            highest_bid = self.listing.bids.latest('amount').amount
            if amount <= highest_bid:
                raise ValidationError(f'The bid must be higher than the current highest bid of ${highest_bid}.')
        return amount