from itertools import product
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=20, default="Weapons")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    price = models.IntegerField(blank=False, default=0)
    pictures = models.ImageField(upload_to="images/", null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="live_products")
    category = models.CharField(max_length=20, default="Weapons")
    current_bid = models.IntegerField(blank=False, null=True, default=1)
    watchers = models.ManyToManyField(User, blank=True, related_name="watched_products")

    def __str__(self):
        return f"Product: '{self.title}' ({self.id}) | {self.price} ETH | {self.description} | {self.category}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="active_bid")
    amount = models.IntegerField(blank=False, default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"@{self.user} bidding {self.amount}ETH on {self.product}"

class Comment(models.Model):
    comment = models.TextField(blank=False, max_length=300)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"@{self.user} - {self.comment} on the product {self.product} {self.date}"
