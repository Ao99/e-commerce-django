from django.conf import settings
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import reverse
from products.models import Item
from accounts.models import Address

# Create your models here.
class OrderItem(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    item        = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity    = models.IntegerField(default=1)
    ordered     = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    
    def get_total_item_price(self):
        if self.item.discount_price:
            price = self.item.discount_price
        else:
            price = self.item.price
        return self.quantity * price
    
    def get_total_item_saving(self):
        if self.item.discount_price:
            saving = self.item.price - self.item.discount_price
        else:
            saving = 0
        return self.quantity * saving

class Coupon(models.Model):
    code        = models.CharField(max_length=15)
    off_value   = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    off_percent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return self.code

class Cart(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items       = models.ManyToManyField(OrderItem)
    start_date  = models.DateTimeField(auto_now_add=True)
    ordered     = models.BooleanField(default=False)
    coupon      = models.ForeignKey(Coupon,
                             on_delete=models.SET_NULL, blank=True, null=True)
                             
    def __str__(self):
        return self.user.username + "- $" + str(self.get_total_price())
    
    def get_total_price_without_coupon(self):
        total_price = 0
        for order_item in self.items.all():
            total_price += order_item.get_total_item_price()
        return total_price
        
    
    def get_coupon_off(self):
        coupon_off= 0
        try:
            off_value = self.coupon.off_value
            coupon_off += off_value
        except:
            pass
        try:
            off_percent = self.coupon.off_percent
            coupon_off += off_percent* self.get_total_price_without_coupon()
            coupon_off = round(coupon_off, 2)
        except:
            pass
        return coupon_off 
        
    def get_total_price(self):
        return self.get_total_price_without_coupon() - self.get_coupon_off()
    
    def get_total_saving(self):
        total_saving = 0
        for order_item in self.items.all():
            total_saving += order_item.get_total_item_saving()
        total_saving += self.get_coupon_off()
        return total_saving
        
    def has_discount_item(self):
        has_discount = False
        for order_item in self.items.all():
            if order_item.item.discount_price:
                has_discount = True
                break
        return has_discount
        
    def is_empty(self):
        return self.items.count() < 1
        
class Payment(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    charge_id   = models.CharField(max_length=50)
    amount      = models.DecimalField(max_digits=100, decimal_places=2)
    ordered_date= models.DateTimeField(auto_now_add=True)
    # billing address
    address     = models.ForeignKey(Address, 
                             on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return self.charge_id

class Order(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code    = models.CharField(max_length=20, blank=True, null=False)
    cart        = models.ForeignKey(Cart,
                             on_delete=models.SET_NULL, blank=True, null=True)
    # shipping address
    address     = models.ForeignKey(Address, 
                             on_delete=models.SET_NULL, blank=True, null=True)
    payment     = models.ForeignKey(Payment, 
                             on_delete=models.SET_NULL, blank=True, null=True)
    ordered     = models.BooleanField(default=False)
    canceled    = models.BooleanField(default=False)

    def __str__(self):
        return self.ref_code
    
    def get_amount(self):
        return self.cart.get_total_price()
        
    def get_show_items_url(self):
        return reverse('accounts:show-items', kwargs={'ref_code': self.ref_code})
        
    def get_cancel_order_url(self):
        return reverse('accounts:cancel-order', kwargs={'ref_code': self.ref_code})
        
    def get_reorder_url(self):
        return reverse('accounts:reorder', kwargs={'ref_code': self.ref_code})
        