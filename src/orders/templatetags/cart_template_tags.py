from django import template
from orders.models import Cart

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        queryset = Cart.objects.filter(user=user, ordered=False)
        if queryset.exists():
            count = 0
            for item in queryset[0].items.all():
                count += item.quantity
            return count
    return 0