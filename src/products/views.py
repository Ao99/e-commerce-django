from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import(
    ListView,
    DetailView
)
from .models import Item
from orders.models import OrderItem, Cart

# Create your views here.
class ItemObjectMixin(object):
    model = Item
    lookup = 'slug'

    def get_object(self):
        lookup = self.kwargs.get(self.lookup)
        obj = None
        if lookup is not None:
            obj = get_object_or_404(self.model, slug=lookup)
        return obj
        
class ItemListView(ListView):
    queryset = Item.objects.all()
    paginate_by = 4
    paginator = Paginator(queryset,paginate_by)
    
class ItemDetailView(ItemObjectMixin, DetailView):
    queryset = Item.objects.all()
    paginate_by = 4
    paginator = Paginator(queryset,paginate_by)
    
    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context['object_list'] = Item.objects.exclude(slug=self.get_object().slug)
        return context

@login_required    
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    # check if the user has an cart
    queryset = Cart.objects.filter(user=request.user, ordered=False)
    if queryset.exists():
        cart = queryset[0]
        # check if the orderitem is in the cart
        if cart.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.success(request, f"Updated the quantity for {item}.")
        else:
            cart.items.add(order_item)
            messages.success(request, f"{item} has been added to your cart.")
    else:
        cart = Cart.objects.create(
            user=request.user
        )
        cart.items.add(order_item)
        messages.success(request, f"{item} has been added to your cart.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required    
def remove_single_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # check if the user has an cart
    queryset = Cart.objects.filter(user=request.user, ordered=False)
    if queryset.exists():
        cart = queryset[0]
        # check if the orderitem is in the cart
        if cart.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.success(request, f"Updated the quantity for {item}.")
            else:
                order_item.delete()
                messages.success(request, f"{item} has been removed from your cart.")
        else:
            messages.warning(request, f"You do not have any {item} in your cart.")
    else:
        messages.error(request, f"You do not have any {item} in your cart.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
@login_required    
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # check if the user has an cart
    queryset = Cart.objects.filter(user=request.user, ordered=False)
    if queryset.exists():
        cart = queryset[0]
        # check if the orderitem is in the Cart
        if cart.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.delete()
            messages.success(request, f"{item} has been removed from your cart.")
        else:
            messages.warning(request, f"You do not have any {item} in your cart.")
    else:
        messages.error(request, f"You do not have any {item} in your cart.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))