from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/<int:product_id>/change/<str:reverse_method>", views.change_watchlist, name="change_watchlist"),
    path("<int:product_id>", views.product, name="product"),
    path("category/<str:cats>/", views.category, name="category"),
    path("categories", views.categories, name="categories"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
