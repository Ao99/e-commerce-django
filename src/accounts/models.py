from django.db import models
from django.conf import settings
from django_countries.fields import CountryField

# Create your models here.
class Address(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    first_name  = models.CharField(max_length = 50)
    last_name   = models.CharField(max_length = 50)
    email       = models.EmailField(blank = True, null = True, max_length = 50)
    address     = models.CharField(max_length = 100)
    address2    = models.CharField(blank = True, null = True, max_length = 50)
    city        = models.CharField(max_length = 50)
    state       = models.CharField(blank = True, null = True, max_length = 50)
    country     = CountryField()
    zip         = models.CharField(max_length = 50)
    save_ship   = models.BooleanField(default=False)
    save_bill   = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username + '-' + self.address