from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from django.views import View
from django.utils import timezone
from .models import Cart, Payment, Order
from .forms import CheckoutForm
from accounts.models import Address

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
class CartView(LoginRequiredMixin, View):
    template_name = "orders/cart.html"
    
    def get(self, request, *args, **kwargs):
        context = {
            'is_not_empty': False,
        }
        cart_queryset = Cart.objects.filter(user=request.user, ordered=False)
        if cart_queryset.exists():
            cart = cart_queryset[0]
            context['cart'] = cart
            if not cart.is_empty():
                context['is_not_empty'] = True
        return render(request, self.template_name, context)

class CheckoutView(LoginRequiredMixin, View):
    template_name = "orders/checkout.html"
    
    def get(self, request, *args, **kwargs):
        # check if cart exists and is not empty
        cart_queryset = Cart.objects.filter(user=request.user, ordered=False)
        if cart_queryset.exists():
            cart = cart_queryset[0]
            if cart.is_empty():
                messages.warning(request, "Your shopping cart is empty.")
                return redirect('products:item-list')
        else:
            messages.warning(request, "Your shopping cart is empty.")
            return redirect('products:item-list')
        
        form = CheckoutForm()
        order_queryset = Order.objects.filter(user=request.user, ordered=False)
        if order_queryset.exists():
            order = order_queryset[0]
            address = order.address
            form = CheckoutForm(instance=address)
        context = {
            'form': form,
            'cart': cart,
        }
        return render(request, self.template_name, context)
        
    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST)
        cart = Cart.objects.get(user=request.user, ordered=False)
        if form.is_valid():
            # update default shipping address for this user
            save_ship = form.cleaned_data.get('save_ship')
            if save_ship:
                address_queryset = Address.objects.filter(user=request.user, save_ship=True)
                if address_queryset.exists():
                    previous_address = address_queryset[0]
                    previous_address.save_ship = False
                    previous_address.save()
            address = Address(
                        user        = request.user,
                        first_name  = form.cleaned_data.get('first_name'),
                        last_name   = form.cleaned_data.get('last_name'),
                        email       = form.cleaned_data.get('email'),
                        address     = form.cleaned_data.get('address'),
                        address2    = form.cleaned_data.get('address2'),
                        city        = form.cleaned_data.get('city'),
                        state       = form.cleaned_data.get('state'),
                        country     = form.cleaned_data.get('country'),
                        zip         = form.cleaned_data.get('zip'),
                        save_ship   = save_ship,
                    )
            address.save()
            # get + update or create order, don't forget to save order
            order_queryset = Order.objects.filter(user=request.user, ordered=False)
            if order_queryset.exists():
                order = order_queryset[0]
                if not order.address.save_bill:
                    order.address.delete()
                order.address = address
            else:    
                order   = Order(
                            user        = request.user,
                            cart        = cart,
                            address     = address,
                        )
            order.save()
            # payment_option  = form.cleaned_data.get('payment_option')
            return redirect("orders:payment")
            
        context = {
            'form': form
        }
        return render(request, self.template_name, context)
        
class PaymentView(LoginRequiredMixin, View):
    template_name = "orders/payment.html"
    
    def get(self, request, *args, **kwargs):
        # check if cart exists and is not empty
        cart_queryset = Cart.objects.filter(user=request.user, ordered=False)
        if cart_queryset.exists():
            cart = cart_queryset[0]
            if cart.is_empty():
                messages.warning(request, "Your shopping cart is empty.")
                return redirect('products:item-list')
        else:
            messages.warning(request, "Your shopping cart is empty.")
            return redirect('products:item-list')
        # check if order exists
        order_queryset = Order.objects.filter(user=request.user, ordered=False)
        if not order_queryset.exists():
            messages.warning(request, "You need to fill the information before checkout.")
            return redirect('orders:checkout')
        context = {
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'cart': cart,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        order   = Order.objects.get(user=request.user, ordered=False)
        cart    = order.cart
        token   = request.POST.get('stripeToken')
        print(request.POST)
        try:
            charge  = stripe.Charge.create(
                      amount    = int(cart.get_total_price() * 100), #cents
                      currency  = "usd",
                      source    = token,
                    #   source="tok_visa",
                    )
            payment = Payment(
                    user        = request.user,
                    charge_id   = charge['id'],
                    amount      = cart.get_total_price(),
                    ordered_date= timezone.now(),
                )
            payment.save()    
            order.payment = payment
            order.ordered = True
            order.save()
            cart.ordered = True
            cart.save()
            for order_item in cart.items.all():
                order_item.ordered = True
                order_item.save()
            
            messages.success(request, "Your order has been successfully placed.")
            return redirect('/')
            
        except stripe.error.CardError as e:
            messages.error(request, e.error.message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except stripe.error.RateLimitError as e:
            messages.error(request, e.error.message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except stripe.error.InvalidRequestError as e:
            messages.error(request, e.error.message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except stripe.error.AuthenticationError as e:
            messages.error(request, e.error.message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except stripe.error.APIConnectionError as e:
            messages.error(request, e.error.message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except stripe.error.StripeError as e:
            messages.error(request, e.error.message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Exception as e:
            messages.error(request, str(e)+"A serious error occurred. We have been notifed.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        messages.error(self.request, "Invalid data received.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))