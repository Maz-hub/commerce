from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .forms import ListingForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Listing
from django.shortcuts import render, get_object_or_404
from .models import Listing, Watchlist
from .forms import BidForm

from .models import User


def index(request):
    active_listings = Listing.objects.filter(status='active')
    return render(request, 'auctions/index.html', {'listings': active_listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

# @login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            return redirect('index')
    else:
        form = ListingForm()
    return render(request, 'auctions/create_listing.html', {'form': form})


# check if the listing is currently on the user's watchlist and provide an option to toggle this status. If the 'toggle_watchlist' POST request is sent, it either creates or deletes a Watchlist entry.
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    on_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists() if request.user.is_authenticated else False
    bid_form = BidForm(request.POST or None)

    if request.method == 'POST' and 'place_bid' in request.POST:
        if bid_form.is_valid():
            bid_amount = bid_form.cleaned_data['bid_amount']
            if bid_amount > listing.starting_bid and (not listing.bids.exists() or bid_amount > listing.bids.latest('amount').amount):
                bid = Bid(listing=listing, user=request.user, amount=bid_amount)
                bid.save()
            else:
                bid_form.add_error(None, 'Your bid must be higher than the current bid.')

    return render(request, 'auctions/listing_detail.html', {
        'listing': listing,
        'on_watchlist': on_watchlist,
        'bid_form': bid_form
    })