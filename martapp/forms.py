from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Products, ProductReviews, Review, Rating 
from django.contrib.auth import get_user_model

User = get_user_model()


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
        widgets = {
            'seller_name': forms.HiddenInput(),  
        }



class CreateReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReviews
        fields = ['customer_review', 'customer_rating'] 
        widgets = {
            'customer_review': forms.Textarea(attrs={'placeholder': 'Optional review text here...'}),
        }

    customer_review = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'Write a review (optional)...'}))

class ChangeUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

class ChangePasswordForm(forms.ModelForm):
    current_password = forms.CharField(
        widget = forms.PasswordInput(attrs={'placeholder':'Current password'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder':'Conform New password'})
    )
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        if new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match")

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_text']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating_value']