from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils import timezone


class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    category_image = models.ImageField(upload_to='categories')
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.category_name
    




class ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    
    def __str__(self):
        return self.color_name




class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    
    def __str__(self):
        return self.size_name
 


class Seller(BaseModel):
    seller_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pin_code = models.BigIntegerField()
    email_id = models.EmailField()
    
    def __str__(self):
        return self.seller_name

 
 
    
class Product(BaseModel):
    product_name = models.CharField(max_length=100)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='seller')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.IntegerField()
    product_description = models.TextField()
    slug = models.SlugField(unique=True, null=True, blank=True)
    color_variant = models.ManyToManyField(ColorVariant, blank=True)
    size_variant = models.ManyToManyField(SizeVariant, blank=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.product_name
    
    def get_product_price_be_size(self, size):
        return self.price + SizeVariant.objects.get(size_name = size).price
    
    def get_product_price_be_color(self, size):
        return self.price + SizeVariant.objects.get(size_name = size).price
   
   
   
   
    
class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product')





class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    coupon_image = models.ImageField(upload_to='coupons')
    expiry_date = models.DateTimeField(blank=True, null=True)
    discount_price = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)
    
    def __str__(self):
        return f"{self.coupon_code}, {self.is_expired}"
    
    def save(self, *args, **kwargs):
        if self.expiry_date:
            if self.expiry_date and timezone.now() >= self.expiry_date:
                self.is_expired = True
            else:
                self.is_expired = False
        super().save(*args, **kwargs)
    
    
    
    
class ProductReview(BaseModel):
    RATING_CHOICES = (
        ('1', '⭐'),
        ('2', '⭐⭐'),
        ('3', '⭐⭐⭐'),
        ('4', '⭐⭐⭐⭐'),
        ('5', '⭐⭐⭐⭐⭐'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=40)
    rating = models.CharField(max_length=1, choices=RATING_CHOICES)
    message_review = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.name