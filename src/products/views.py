from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import(
    ListView,
    DetailView
)
from .models import Item, Category, Gender
from .forms import AddToCartForm
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


# class ItemListView(ListView):
#     queryset = Item.objects.get_queryset().order_by('slug')
#     paginate_by = 4

class ItemListView(View):
    template_name = "products/item_list.html"
    category_list = Category.objects.all()
    gender_list = Gender.objects.all()
    
    def get(self, request, *args, **kwargs):
        c_title = "all"
        g_title = "all"
        try:
            c_title = kwargs['c_title']
            queryset = Item.objects.get_queryset().filter(category__c_title=c_title).order_by('slug')
        except:
            queryset = Item.objects.get_queryset().order_by('slug')
        try:
            g_title = kwargs['g_title']
            queryset = queryset.filter(gender__g_title=g_title).order_by('slug')
        except:
            pass
                
        paginator = Paginator(queryset, 4)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        context = {
            'page': page,
            'paginator': paginator,
            'page_obj': page_obj,
            'category_list': self.category_list,
            'gender_list': self.gender_list,
            'c_title': c_title,
            'g_title': g_title,
        }
        return render(request, self.template_name,context)
    

class ItemDetailView(ItemObjectMixin, DetailView):

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        queryset = []
        for cat in self.get_object().category.all():
            queryset += Item.objects.filter(
                category__c_title=cat).exclude(
                slug=self.get_object().slug)
        queryset = list(dict.fromkeys(queryset))
        context['object_list'] = queryset
        form = AddToCartForm()
        context['form'] = form
        return context


@login_required
def add_to_cart(request, slug):
    quantity = request.POST.get("quantity")
    if not quantity:
        quantity = 1
    quantity = int(quantity)
    if quantity > 0:
        item = get_object_or_404(Item, slug=slug)
        # check if the user has an cart
        try:
            cart = Cart.objects.get(user=request.user, ordered=False)
        except ObjectDoesNotExist:
            cart = Cart.objects.create(
                user=request.user
            )
        # check if the orderitem is in the cart
        try:
            order_item = cart.items.get(item__slug=slug)
            order_item.quantity += quantity
            order_item.save()
            messages.success(request, f"Updated the quantity for {item}.")
        except ObjectDoesNotExist:
            order_item, created = OrderItem.objects.get_or_create(
                item=item,
                user=request.user,
                quantity=quantity,
                ordered=False,
            )
            cart.items.add(order_item)
            messages.success(request, f"{item} has been added to your cart.")
    else:
        messages.error(request, "Please input a positive number.")
    previous_page = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if "login" in previous_page.url:
        return redirect('products:item-list')
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def remove_single_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # check if the user has an cart
    try:
        cart = Cart.objects.get(user=request.user, ordered=False)
        # check if the orderitem is in the cart
        try:
            order_item = cart.items.get(item__slug=slug)
            order_item.quantity -= 1
            if order_item.quantity > 0:
                order_item.save()
                messages.success(request, f"Updated the quantity for {item}.")
            else:
                order_item.delete()
                messages.success(
                    request, f"{item} has been removed from your cart.")
        except ObjectDoesNotExist:
            messages.warning(
                request, f"You do not have any {item} in your cart.")
    except ObjectDoesNotExist:
        messages.error(request, f"You do not have any {item} in your cart.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # check if the user has an cart
    try:
        cart = Cart.objects.get(user=request.user, ordered=False)
        # check if the orderitem is in the Cart
        try:
            order_item = cart.items.get(item__slug=slug)
            order_item.delete()
            messages.success(
                request, f"{item} has been removed from your cart.")
        except ObjectDoesNotExist:
            messages.warning(
                request, f"You do not have any {item} in your cart.")
    except ObjectDoesNotExist:
        messages.error(request, f"You do not have any {item} in your cart.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
