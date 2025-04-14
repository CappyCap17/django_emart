from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class CustomUser(AbstractUser):

    def __str__(self):
        return f"{self.username} {self.email}"


class Products(models.Model):
    PRODUCT_TYPE = [
        ('Clothes', 'Clothes'),
        ('Electronics', 'Electronics'),
        ('Food', 'Food'),
        ('Toys', 'Toys'),
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('Tools', 'Tools'),
    ]

    product_name = models.CharField(max_length=30)
    seller_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=30, choices=PRODUCT_TYPE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length=1048)
    product_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    stock = models.PositiveIntegerField(default= 0)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product_name} - {self.seller_name} - {self.product_type} - ₹{self.price} - Stock: {self.stock}"

class ProductReviews(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product_name = models.ForeignKey('Products', on_delete=models.CASCADE, related_name='product_reviews')
    customer_review = models.TextField(max_length=500)
    customer_rating = models.IntegerField(choices=RATING_CHOICES, default=0)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Rating: {self.customer_rating} - {self.customer_review[:30]}..."

class ProductsBought(models.Model):
    product = models.ForeignKey('Products', on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sold_products', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_purchased = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.username} bought {self.product.product_name} for ₹{self.price}"

class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    rating_value = models.IntegerField()  # 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)
