from django.urls import path
from .views import (
    ItemListView,
    ItemDetailView,
    add_to_cart,
    remove_single_from_cart,
    remove_from_cart,
)

app_name='products'
urlpatterns = [
    path('', ItemListView.as_view(), name='item-list'),
    path('products/<slug>/', ItemDetailView.as_view(), name='item-detail'),
    path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
    path('remove-single-from-cart/<slug>', remove_single_from_cart, name='remove-single-from-cart'),
    path('remove-from-cart/<slug>', remove_from_cart, name='remove-from-cart'),
    ]