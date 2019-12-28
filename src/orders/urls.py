from django.urls import path
from .views import (
    CartView,
    CheckoutView,
    PaymentView
)

app_name='orders'
urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/', PaymentView.as_view(), name='payment'),
    ]