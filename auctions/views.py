from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404, redirect
from .models import Listing, Watchlist, User, Listing, Bid, Comment, Category
from .forms import ListingForm, BidForm, CommentForm



def index(request):
    active_listings = Listing.objects.filter(status='active')
    categories = Category.objects.all()
    return render(request, 'auctions/index.html', {
        'listings': active_listings,
        'categories': categories 
    })


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

@login_required
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


def listing_detail(request, listing_id):
    # Fetch the listing with the given ID or return a 404 error if not found
    listing = get_object_or_404(Listing, pk=listing_id)
    
    # Check if the listing is on the user's watchlist
    on_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists() if request.user.is_authenticated else False

    comments = Comment.objects.filter(listing=listing)
    comment_form = CommentForm(request.POST or None)

    current_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
    
    # Initialize the bid form
    bid_form = BidForm(request.POST or None)
    
    # Initialize a variable for displaying messages to the user
    message = None

    if request.method == 'POST':
        # Bid submissions
        if 'place_bid' in request.POST:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                bid_amount = bid_form.cleaned_data['bid_amount']
                
                # Ensure that the bid is higher than the starting bid
                if bid_amount < listing.starting_bid:
                    bid_form.add_error(None, f'Your bid must be higher than the starting bid of ${listing.starting_bid:.2f}.')
                    message = f'Your bid must be higher than the starting bid of ${listing.starting_bid:.2f}.'
                
                # Ensure that the bid is higher than the current highest bid
                elif current_bid is not None and bid_amount <= current_bid.amount:
                    bid_form.add_error(None, f'Your bid must be higher than the current highest bid of ${current_bid.amount:.2f}.')
                    message = f'Your bid must be higher than the current highest bid of ${current_bid.amount:.2f}.'
                
                # If the bid is valid, save it
                else:
                    bid = Bid(listing=listing, user=request.user, amount=bid_amount)
                    bid.save()
                    message = "Your bid was successful!"
                    current_bid = bid  # Update current bid to the new highest
            else:
                # Invalid form submission
                message = "Invalid bid amount. Please enter a valid number."

        # Toggle the watchlist status
        if 'toggle_watchlist' in request.POST:
            if on_watchlist:
                Watchlist.objects.filter(user=request.user, listing=listing).delete()
                on_watchlist = False
            else:
                Watchlist.objects.create(user=request.user, listing=listing)
                on_watchlist = True
        
        # Closing the auction
        if 'close_auction' in request.POST and request.user == listing.owner:
            if listing.status == 'active':
                listing.status = 'closed'
                listing.save()
                message = "Auction has been closed."
            else:
                message = "Auction is not active and cannot be closed."

        # Commenting
        if 'comment_submit' in request.POST and comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.listing = listing
            new_comment.user = request.user
            new_comment.save()

    return render(request, 'auctions/listing_detail.html', {
        'listing': listing,
        'on_watchlist': on_watchlist,
        'comment_form': comment_form,
        'comments': comments,
        'current_bid': current_bid,
        'bid_form': bid_form if listing.status == 'active' else None,
        'message': message,
    })




def watchlist_view(request):
    if not request.user.is_authenticated:
        # Redirect to login or show an error
        return redirect('login')
    
    # Get all watchlist items for the logged-in user
    watchlist_items = Watchlist.objects.filter(user=request.user).select_related('listing')

    return render(request, 'auctions/watchlist.html', {'watchlist_items': watchlist_items})


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'auctions/category_list.html', {'categories': categories})


def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = Listing.objects.filter(category=category, status='active')
    return render(request, 'auctions/category_detail.html', {'category': category, 'listings': listings})


def watchlist_count(request):
    count = 0
    if request.user.is_authenticated:
        count = Watchlist.objects.filter(user=request.user).count()
    return {'watchlist_count': count}
