from django.db import models
from django.shortcuts import reverse
from multiselectfield import MultiSelectField

# Create your models here.

CATEGORY_CHOICES = [
    ('Shirts', 'Shirts'),
    ('Sweaters', 'Sweaters'),
    ('Sport wears', 'Sport wears'),
    ('Outwears', 'Outwears'),
    ('Jeans', 'Jeans'),
    ('Pants', 'Pants'),
]

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('K', 'Kids'),
    ('U', 'Unisex'),
]

class Item(models.Model):
    title           = models.CharField(max_length=100)
    price           = models.DecimalField(max_digits=100, decimal_places=2)
    discount_price  = models.DecimalField(blank=True, null=True, max_digits=100, decimal_places=2)
    category        = MultiSelectField(choices=CATEGORY_CHOICES)
    gender          = models.CharField(choices=GENDER_CHOICES, max_length=1)
    slug            = models.SlugField()
    description     = models.TextField()
    photo           = models.ImageField(upload_to='products')
    
    def __str__(self):
        return self.title
    
    def get_category(self):
        return self.category.attname
        
    def get_absolute_url(self):
        return reverse('products:item-detail', kwargs={'slug': self.slug})
    
    def get_add_to_cart_url(self):
        return reverse('products:add-to-cart', kwargs={'slug': self.slug})
        
    def get_remove_single_from_cart_url(self):
        return reverse('products:remove-single-from-cart', kwargs={'slug': self.slug})
        
    def get_remove_from_cart_url(self):
        return reverse('products:remove-from-cart', kwargs={'slug': self.slug})