from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from django.views import View
from django.utils import timezone
from .models import Cart, Coupon, Payment, Order
from .forms import CheckoutForm, PaymentForm, CouponForm
from accounts.models import Address

import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

# Create your views here.
class CartView(LoginRequiredMixin, View):
    template_name = "orders/cart.html"
    
    def get(self, request, *args, **kwargs):
        context = {
            'is_not_empty': False,
        }
        try:
            cart = Cart.objects.get(user=request.user, ordered=False)
            context['cart'] = cart
            if not cart.is_empty():
                context['is_not_empty'] = True
        except ObjectDoesNotExist:
            pass
        return render(request, self.template_name, context)

class CheckoutView(LoginRequiredMixin, View):
    template_name = "orders/checkout.html"
    
    def get(self, request, *args, **kwargs):
        # check if cart exists and is not empty    
        try:
            cart = Cart.objects.get(user=request.user, ordered=False)
            if cart.is_empty():
                messages.warning(request, "Your shopping cart is empty.")
                return redirect('products:item-list')
        except ObjectDoesNotExist:
            messages.warning(request, "Your shopping cart is empty.")
            return redirect('products:item-list')
        # check if order exists
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            address = order.address
            form = CheckoutForm(instance=address)
        except ObjectDoesNotExist:
            pass
        
        form = CheckoutForm()
       
        try:
            default_ship = Address.objects.get(user=request.user, save_ship=True)
        except ObjectDoesNotExist:
            default_ship = None
        
        couponform = CouponForm()
        
        context = {
            'default_ship': default_ship,
            'form': form,
            'couponform': couponform,
            'cart': cart,
            'display_coupon': True,
        }
        return render(request, self.template_name, context)
        
    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST)
        cart = Cart.objects.get(user=request.user, ordered=False)
        use_default_ship = request.POST.get('use_default_ship')
        if not use_default_ship and not form.is_valid():
            pass
        else:
            if use_default_ship:
                address = Address.objects.get(user=request.user, save_ship=True)
            elif form.is_valid():
                # update default shipping address for this user
                save_ship = form.cleaned_data.get('save_ship')
                if save_ship:
                    try:
                        previous_saved = Address.objects.get(user=request.user, save_ship=True)
                        previous_saved.save_ship = False
                        previous_saved.save()
                    except ObjectDoesNotExist:
                        pass
                        
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
            try:
                order = Order.objects.get(user=request.user, ordered=False)
                order.address = address
            except ObjectDoesNotExist:
                order = Order(
                        user        = request.user,
                        cart        = cart,
                        address     = address,
                        ref_code    = create_ref_code(),
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
        try:
            cart = Cart.objects.get(user=request.user, ordered=False)
            if cart.is_empty():
                messages.warning(request, "Your shopping cart is empty.")
                return redirect('products:item-list')
        except ObjectDoesNotExist:
            messages.warning(request, "Your shopping cart is empty.")
            return redirect('products:item-list')
        # check if order exists
        try:
            order = Order.objects.get(user=request.user, ordered=False)
        except ObjectDoesNotExist:
            messages.warning(request, "You need to fill checkout information before payment.")
            return redirect('orders:checkout')
            
        form = PaymentForm()
        
        try:
            default_bill = Address.objects.get(user=request.user, save_bill=True)
        except ObjectDoesNotExist:
            default_bill = None
            
        context = {
            'default_bill': default_bill,
            'form': form,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'cart': cart,
            'display_coupon': False,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = PaymentForm(request.POST)
        order   = Order.objects.get(user=request.user, ordered=False)
        cart    = order.cart
        token   = request.POST.get('stripeToken')
        use_same_address = request.POST.get('use_same_address')
        use_default_bill = request.POST.get('use_default_bill')
        
        if not use_same_address and not use_default_bill and not form.is_valid():
            pass
        else:
            if use_same_address:
                address = order.address
            elif use_default_bill:
                address = Address.objects.get(user=request.user, save_bill=True)
            elif form.is_valid():
                # update default billing address for this user
                save_bill = form.cleaned_data.get('save_bill')
                if save_bill:
                    try:
                        previous_saved = Address.objects.get(user=request.user, save_bill=True)
                        previous_saved.save_bill = False
                        previous_saved.save()
                    except ObjectDoesNotExist:
                        pass
                        
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
                            save_bill   = save_bill,
                        )
                address.save()    
        try:
            charge  = stripe.Charge.create(
                      amount    = int(cart.get_total_price() * 100), #cents
                      currency  = "cad",
                      source    = token,
                    )
            payment = Payment(
                    user        = request.user,
                    charge_id   = charge['id'],
                    amount      = cart.get_total_price(),
                    ordered_date= timezone.now(),
                    address     = address,
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
        context = {
            'form': form
        }
        return render(request, self.template_name, context)
        
class AddCouponView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # check if cart exists and is not empty
        if request.method == 'POST':
            form = CouponForm(request.POST or None)
            if form.is_valid():
                try:
                    cart = Cart.objects.get(user=request.user, ordered=False)
                    if cart.is_empty():
                        messages.warning(request, "Your shopping cart is empty.")
                        return redirect('products:item-list')
                    else:
                        code = form.cleaned_data.get('code')
                        try:
                            coupon = Coupon.objects.get(code=code)
                            cart.coupon = coupon
                            cart.save()
                            messages.success(request, "Successfully added coupon.")
                            # return redirect('orders:checkout')
                        except ObjectDoesNotExist:
                            messages.warning(request, "This coupon does not exist.")
                            # return redirect('orders:checkout')
                except ObjectDoesNotExist:
                    messages.warning(request, "Your shopping cart is empty.")
                    # return redirect('products:item-list')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))