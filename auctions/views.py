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

    # Initialize or fetch the current highest bid
    try:
        current_bid = listing.bids.order_by('-amount').first()
    except:
        current_bid = None

    bid_form = BidForm(request.POST or None)
    message = None

    if request.method == 'POST':
        if 'place_bid' in request.POST and bid_form.is_valid():
            bid_amount = bid_form.cleaned_data['bid_amount']
            if current_bid is None or bid_amount > current_bid.amount:
                bid = Bid(listing=listing, user=request.user, amount=bid_amount)
                bid.save()
                message = "Your bid was successful!"
                current_bid = bid  # Update current bid to the new highest
            else:
                bid_form.add_error(None, 'Your bid must be higher than the current highest bid of $%.2f.' % current_bid.amount)
                message = 'The bid must be higher than the current highest bid of $%.2f.' % current_bid.amount

    if request.method == 'POST':
        # Handle toggling the watchlist status
        if 'toggle_watchlist' in request.POST:
            if on_watchlist:
                Watchlist.objects.filter(user=request.user, listing=listing).delete()
                on_watchlist = False
            else:
                Watchlist.objects.create(user=request.user, listing=listing)
                on_watchlist = True
        
        # Handle bid submissions
        if 'place_bid' in request.POST:
            if bid_form.is_valid():
                bid_amount = bid_form.cleaned_data['bid_amount']
                # Ensure the bid is higher than the starting bid and all previous bids
                if bid_amount > listing.starting_bid and (not listing.bids.exists() or bid_amount > listing.bids.latest('amount').amount):
                    Bid.objects.create(listing=listing, user=request.user, amount=bid_amount)
                else:
                    bid_form.add_error(None, 'Your bid must be higher than the current bid.')

        # Handle closing the auction
        if 'close_auction' in request.POST and request.user == listing.owner:
            if listing.status == 'active':
                listing.status = 'closed'
                listing.save()
                message = "Auction has been closed."
            else:
                message = "Auction is not active and cannot be closed."

        # Handle commenting
        if 'comment_submit' in request.POST and comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.listing = listing
            new_comment.user = request.user
            new_comment.save()

        

    # Render the page with the current state
    return render(request, 'auctions/listing_detail.html', {
        'listing': listing,
        'on_watchlist': on_watchlist,
        'comment_form': comment_form,
        'comments': comments,
        'current_bid': current_bid,
        'bid_form': bid_form if listing.status == 'active' else None,  # Don't show bid form if auction is closed
        'message': message,  # Display messages about actions taken
  
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
