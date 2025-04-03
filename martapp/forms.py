from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Products, ProductReviews


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


class LoginUserForm(AuthenticationForm):
      class Meta:
          fields = ['username', 'password']


class CreateProductForm(forms.ModelForm):
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
        fields = ['product_name', 'product_image', 'product_type', 'seller_name', 'price', 'description']


class CreateReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReviews
        fields = ['customer_review', 'customer_rating'] 
        widgets = {
            'customer_review': forms.Textarea(attrs={'placeholder': 'Optional review text here...'}),
        }

    customer_review = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'Write a review (optional)...'}))
