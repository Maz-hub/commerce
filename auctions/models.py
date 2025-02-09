from django.contrib.auth.models import AbstractUser
from django.db import models

# add additional models to this file to represent details about auction listings, bids, comments, and auction categories. 
# Remember that each time you change anything in auctions/models.py, you’ll need to first run python manage.py makemigrations and then python manage.py migrate to migrate those changes to your database.

# Models: Your application should have at least three models in addition to the User model: one for auction listings, one for bids, and one for comments made on auction listings. It’s up to you to decide what fields each model should have, and what the types of those fields should be. You may have additional models if you would like.

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


class Listing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    status = models.CharField(choices=LISTING_STATUS, default='active', max_length=10)



class Bid(models.Model):
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    content = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)



