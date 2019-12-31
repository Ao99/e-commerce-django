from django.db import models
from django.shortcuts import reverse

# Create your models here.

class Category(models.Model):
    c_title = models.CharField(max_length=50)
    
    def __str__(self):
        return self.c_title
        
    def get_category_view_url(self):
        return reverse("products:category-view", kwargs={'c_title':self.c_title})

class Gender(models.Model):
    g_title = models.CharField(max_length=50)
    
    def __str__(self):
        return self.g_title
        
    def get_gender_view_url(self):
        return reverse("products:gender-view", kwargs={'g_title':self.g_title})

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    discount_price = models.DecimalField(
        blank=True, null=True, max_digits=100, decimal_places=2)
    category = models.ManyToManyField(Category)
    gender = models.ManyToManyField(Gender)
    slug = models.SlugField()
    description = models.TextField()
    photo = models.ImageField(upload_to='products')

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
    