from django.contrib.auth.models import AbstractUser # import the AbstractUser class
from django.db import models # import the models module
from django.conf import settings # import the settings.py file

# add additional models to this file to represent details about auction listings, bids, comments, and auction categories. 
# Remember that each time you change anything in auctions/models.py, you’ll need to first run python manage.py makemigrations and then python manage.py migrate to migrate those changes to your database.


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
LISTING_STATUS = (
    ('active', 'Active'),
    ('closed', 'Closed'),
    ('sold', 'Sold'),
)

# create a Listing model to represent details about auction listings
class Listing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    status = models.CharField(choices=LISTING_STATUS, default='active', max_length=10)


# create a Bid model to represent details about bids placed on auction listings
class Bid(models.Model):
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    created_at = models.DateTimeField(auto_now_add=True)


# create a Comment model to represent details about comments made on auction listings
class Comment(models.Model):
    content = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

# track which listings a user has added to their watchlist
# This model links a user and a listing, indicating that the user has added the listing to their watchlist.
class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.listing.title}"

