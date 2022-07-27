from random import choices
import re
from sre_parse import CATEGORIES
from django import forms
from attr import fields
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.forms import ModelForm, NumberInput, TextInput
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.forms import HiddenInput
from .models import *

choices = Category.objects.all().values_list('name', 'name')

choice_list = []

for item in choices:
    choice_list.append(item)

class CreateProdcutForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'title', 'price', 'description', 'pictures',]

        widgets = {
            'category': forms.Select(choices=choice_list),
        }

class CommentForm(ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={
        'class': "comment-input",
        'rows': '1',
        'cols': '40'
    }))
    class Meta:
        model = Comment
        fields = ['comment',]

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount',]

        widgets = {
            'amount': NumberInput(attrs={
            'class': "bid-input",
            })
        }


def index(request):
    products = Product.objects.all()
    latest_products = products.order_by('-id')

    return render(request, "auctions/index.html", {
        "products": Product.objects.all(),
        "latest_products": latest_products,
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


@login_required
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
def create(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            form = CreateProdcutForm(request.POST, request.FILES)
            for field in form:
                print(field.value())
            if form.is_valid():
                product = form.save(commit=False)
                product.seller = User.objects.get(pk=request.user.id)
                product.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "auctions/create.html", {
                    "form": form,
                    "message": "Not Posted"
                })
    return render(request, "auctions/create.html", {
        "form": CreateProdcutForm(),
    })

@login_required
def product(request, product_id):
    product = Product.objects.get(pk=product_id)
    comments = product.comments.all()
    new_comment = None
    bids = product.bids.all()
    current_bid = product.current_bid
    bid_msg = ""
    new_bid = None

    if request.user in product.watchers.all():
        product.is_watched = True
    else:
        product.is_watched = False
    if not request.user.is_authenticated:
        return render(request, "auctions/login.html")
    else:
        if request.method == "POST":
                form = CommentForm(request.POST)
                bid_form = BidForm(request.POST)
                if form.is_valid():
                    form.instance.user = request.user
                    form.instance.product = product
                    new_comment = form.save(commit=False)
                    new_comment.product = product
                    new_comment.save()
                    return HttpResponseRedirect(reverse("product", args={product.id,}))
                if bid_form.is_valid():
                    bid_form.instance.user = request.user
                    bid_form.product = product
                    new_bid = bid_form.save(commit=False)
                    if new_bid.amount <= current_bid:
                        bid_msg = "New Bids must be higher than the current bid!"
                    else:
                        current_bid = int(new_bid.amount)
                        print(f"Current Bid: {current_bid}")
                        new_bid.product = product
                        product.current_bid = current_bid
                        new_bid.save()
                        product.save()
                        return HttpResponseRedirect(reverse("product", args={product.id,}))
        else:
            form = CommentForm()
            bid_form = BidForm()
    return render(request, "auctions/product.html", {
        "product": product,
        "comments": comments,
        "bids": bids,
        "current_bid": current_bid,
        "bid_form": bid_form,
        "bid_msg": bid_msg,
        "form": form,
    })

def categories(request):
    categories = Category.objects.all()
    weapons_products = Product.objects.filter(category="Weapons")
    armor_products = Product.objects.filter(category="Armor")
    shields_products = Product.objects.filter(category="Shields")
    talismans_products = Product.objects.filter(category="Talismans")

    return render(request, "auctions/category.html", {
        "weapons_products": weapons_products,
        "armor_products": armor_products,
        "shields_products": shields_products,
        "talismans_products": talismans_products,
        "categories": categories,
    })

def category(request, cats):
    category_products = Product.objects.filter(category=cats)
    return render(request, "auctions/categories.html", {
        "cats": cats,
        "category_products": Product.objects.filter(category=cats),
    })

@login_required
def watchlist(request):
    products = request.user.watched_products.all()
    categories = Category.objects.all()

    for product in products:
        if request.user in product.watchers.all():
            product.is_watched = True
        else:
            product.is_watched = False

    return render(request, "auctions/watchlist.html", {
        "products": products,
        "categories": categories,
    })

@login_required
def change_watchlist(request, product_id, reverse_method):
    product = Product.objects.get(pk=product_id)
    if request.user in product.watchers.all():
        product.watchers.remove(request.user)
    else:
        product.watchers.add(request.user)
    return HttpResponseRedirect(reverse("product", args={product.id,}))

