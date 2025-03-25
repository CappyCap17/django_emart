from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Products, ProductReviews


class RegisterUser(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password1', 'password2']  


class LoginUser(AuthenticationForm):
    class Meta:
        fields = ['username', 'password'] 


class CreateProduct(forms.ModelForm):
    PRODUCT_TYPE = [
        ('Clothes', 'Clothes'),
        ('Electronics', 'Electronics'),
        ('Food', 'Food'),
        ('Toys', 'Toys'),
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('Tools', 'Tools'),
    ]
    product_type = forms.ChoiceField(choices=PRODUCT_TYPE, required=True) 

    class Meta:
        model = Products
        fields = ['product_name', 'proudct_Image', 'product_type', 'seller_name', 'price', 'description']


class CreateReview(forms.ModelForm):
    class Meta:
        model = ProductReviews
        fields = ['product_name', 'customer_review', 'customer_rating'] 
