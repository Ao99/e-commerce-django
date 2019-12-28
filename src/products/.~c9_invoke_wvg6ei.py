from django.db import models
from django.shortcuts import reverse

# Create your models here.

CATEGORY_CHOICES = (
    ('S', 'Shirts'),
    ('ST', 'Sweater'),
    ('SW', 'Sport wears'),
    ('OW', 'Outwears'),
    ('JN', 'Jeans'),
    ('P', 'Pants'),
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)

class Item(models.Model):
    title           = models.CharField(max_length=100)
    price           = models.FloatField()
    discount_price  = models.FloatField(blank=True, null=True)
    category        = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label           = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug            = models.SlugField()
    description     = models.TextField()
    photo           = models.ImageField(upload_to='products')
    
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return reverse('products:item-detail', kwargs={'slug': self.slug})
    
    def get_add_to_cart_url(self):
        return reverse('products:add-to-cart', kwargs={'slug': self.slug})
        
    def get_remove_from_cart_url(self):
        return reverse('products:remove-from-cart', kwargs={'slug': self.slug})