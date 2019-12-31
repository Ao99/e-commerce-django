from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Address
from orders.models import Order

# Create your views here.
@login_required
def cancel_order(request, ref_code):
    order = get_object_or_404(Order, ref_code=ref_code)
    order.canceled = True
    order.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
@login_required
def reorder(request, ref_code):
    order = get_object_or_404(Order, ref_code=ref_code)
    order.canceled = False
    order.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
class ProfileView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"
    
    def get(self, request, *args, **kwargs):
        userprofile = request.user.userprofile
        try:
            ref_code = kwargs['ref_code']
        except:
            ref_code = None
        try:
            default_ship = userprofile.default_ship
        except ObjectDoesNotExist:
            default_ship = None
        try:
            default_bill = userprofile.default_bill
        except ObjectDoesNotExist:
            default_bill = None
        order_list = Order.objects.filter(user=request.user).order_by('-id')
            
        context = {
            'default_ship': default_ship,
            'default_bill': default_bill,
            'order_list': order_list,
            'ref_code': ref_code,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))