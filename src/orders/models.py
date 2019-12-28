from django.conf import settings
from django.db import models
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

class Cart(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items       = models.ManyToManyField(OrderItem)
    start_date  = models.DateTimeField(auto_now_add=True)
    ordered     = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + "- $" + str(self.get_total_price())
    
    def get_total_price(self):
        total_price = 0
        for order_item in self.items.all():
            total_price += order_item.get_total_item_price()
        return total_price
    
    def get_total_saving(self):
        total_saving = 0
        for order_item in self.items.all():
            total_saving += order_item.get_total_item_saving()
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
    address     = models.ForeignKey('accounts.Address', 
                             on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return self.user.username + self.charge_id

class Order(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    cart        = models.ForeignKey('Cart',
                             on_delete=models.SET_NULL, blank=True, null=True)
    # shipping address
    address     = models.ForeignKey('accounts.Address', 
                             on_delete=models.SET_NULL, blank=True, null=True)
    payment     = models.ForeignKey('Payment', 
                             on_delete=models.SET_NULL, blank=True, null=True)
    ordered     = models.BooleanField(default=False)
    
    def __str__(self):
        charge_id = '-proceeding'
        if self.ordered:
            charge_id = "-paid-" + self.payment.charge_id
        return self.user.username + charge_id