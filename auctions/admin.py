from django.contrib import admin
from .models import *

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "price", "seller", "pictures")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("comment", "user", "product", "date")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount", "product")

admin.site.register(User)
admin.site.register(Product, ProductAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category)
admin.site.register(Bid, BidAdmin)
