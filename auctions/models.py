from django.contrib.auth.models import AbstractUser 
from django.db import models
from django.conf import settings

# Custom User model (inherits from AbstractUser)
class User(AbstractUser):
    pass

# Model for categories
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Choices for the status of a listing
LISTING_STATUS = (
    ('active', 'Active'),
    ('closed', 'Closed'),
    ('sold', 'Sold'),
)

# Model for auction listings
class Listing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    status = models.CharField(choices=LISTING_STATUS, default='active', max_length=10)


# Model for bids placed on listings
class Bid(models.Model):
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    created_at = models.DateTimeField(auto_now_add=True)


# Model for comments made on listings
class Comment(models.Model):
    content = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

# Model for tracking which listings a user has added to their watchlist
class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.listing.title}"

