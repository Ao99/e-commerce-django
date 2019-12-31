from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django_countries.fields import CountryField
# from orders.models import Order

# Create your models here.
class Address(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    first_name  = models.CharField(max_length = 50, null = False)
    last_name   = models.CharField(max_length = 50, null = False)
    email       = models.EmailField(max_length = 50, null = False)
    address     = models.CharField(max_length = 100, null = False)
    address2    = models.CharField(blank = True, null = False, max_length = 50)
    city        = models.CharField(max_length = 50, null = False)
    state       = models.CharField(blank = True, null = False, max_length = 50)
    country     = CountryField()
    zip         = models.CharField(max_length = 50, null = False)

    def __str__(self):
        return self.user.username + '-' + self.address
        
class UserProfile(models.Model):
    user                = models.OneToOneField(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE)
    stripe_customer_id  = models.CharField(max_length=50, blank=True, null=True)
    default_ship        = models.ForeignKey(Address, related_name='default_ship',
                             on_delete=models.SET_NULL, blank=True, null=True)
    default_bill        = models.ForeignKey(Address, related_name='default_bill',
                             on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return self.user.username
        
def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)

post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)