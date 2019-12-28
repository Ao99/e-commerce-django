from django.contrib import admin
from django.contrib import admin
from .models import OrderItem, Cart, Payment, Order

# Register your models here.
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(Payment)
admin.site.register(Order)
