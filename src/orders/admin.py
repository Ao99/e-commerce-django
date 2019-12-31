from django.contrib import admin
from .models import OrderItem, Cart, Coupon, Payment, Order

# Register your models here.


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'ordered']


class CartAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'ordered', 'start_date']


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'amount', 'address', 'ordered_date']


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'user',
        'cart',
        'address', 
        'payment',
        'ordered',
        'canceled',
    ]
    list_display_links = [
        '__str__',
        'user',
        'cart',
        'address', 
        'payment',
        'ordered',
        'canceled',
    ]
    list_filter = [
        'user',
        'ordered',
        'canceled',
    ]
    search_fields = [
        'user__username',
        'ref_code',
    ]


admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Coupon)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
