from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from .forms import RegisterUserForm, LoginUserForm, CreateProductForm, CreateReviewForm, ChangeUsernameForm, ChangePasswordForm, ReviewForm, RatingForm
from .models import CustomUser, Products, ProductReviews, ProductsBought, Products, Purchase
from functools import wraps
import random
from django.http import HttpResponse
from django.contrib.auth.hashers import check_password
import base64
from django.conf import settings


# Decorators
def only_bought(view_func):
    def wrapper(request, product_id, *args, **kwargs):
        if Purchase.objects.filter(user=request.user, product__id=product_id).exists():
            return view_func(request, product_id, *args, **kwargs)
        
        product = get_object_or_404(Products, id=product_id)
        messages.error(request, "You must buy this product before leaving a review or rating.")
        return redirect('view-product', product_id=product.id)   
    return wrapper

# Register User
@method_decorator(csrf_protect, name='dispatch')
class RegisterUserView(View):
    def get(self, request):
        form = RegisterUserForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Successfully registered and logged in!")  
            return redirect('dashboard')  
        else:
            print(form.errors)
            messages.error(request, "Unsuccessful registration. Please correct the errors below.")
        return render(request, 'register.html', {'form': form})

# Login User
@method_decorator(csrf_protect, name='dispatch')
class LoginView(View):
    def get(self, request):
        form = LoginUserForm()
        return render(request, "login.html", {'form': form})

    def post(self, request):
        form = LoginUserForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid login credentials.")
        return render(request, "login.html", {'form': form})

# Logout User
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

# Sell Product
@login_required
def sell_product_view(request):
    if request.method == 'POST':
        form = CreateProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller_name = request.user  
            product.save()
            return redirect('dashboard')
        else:
            print("Form is NOT valid:")
            print(form.errors)
    else:
        form = CreateProductForm(initial={'seller_name': request.user.id})

    return render(request, 'sell_product.html', {'form': form})

#Search Products
@login_required
def search_view(request):
    query = request.GET.get('q') 
    results = []

    if query:
        results = Products.objects.filter(
            product_name__icontains=query
        ) | Products.objects.filter(
            product_type__icontains=query
        ) | Products.objects.filter(
            seller_name__username__icontains=query
        )

    return render(request, 'search_results.html', {'query': query, 'results': results})


#Product Recommendations
@login_required
def recommendation_view(request):
    display = list(Products.objects.order_by('-customer_rating')[:6])
    random.shuffle(display)
    return render(request, 'dashboard.html', {'display': display})

#View Product Details
@login_required
def view_product_view(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    return render(request, 'product.html', {'product': product})

#dashboard/search/ buy product
@login_required
def buy_product_view(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    if request.method == 'POST':
        if request.user == product.seller_name:
            messages.error(request, "You cannot buy your own product!")
            return redirect('view-product', product_id=product.id)

        ProductsBought.objects.create(
            product=product,
            buyer=request.user,
            seller=product.seller_name,
            price=product.price
        )
        messages.success(request, "Purchase successful!")
        return redirect('success_page', product_id=product.id)

    if product.product_image:
        with product.product_image.open('rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    else:
        encoded_image = ''  

    return render(request, 'buy_product.html', {
        'product': product,
        'product_image_base64': encoded_image 
    })

#Submit Review and Rating
# @login_required
# @only_bought
# def submit_review_rating_view(request, product_id, action_type):
#     product = get_object_or_404(Products, id=product_id)
    
#     if request.method == 'POST':
#         form = CreateReviewForm(request.POST)
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.user = request.user
#             review.product = product
            
         
#             if action_type == 'rating':
#                 review.review = ''  
#             elif action_type == 'review':
#                 review.rating = None  
                
#             review.save()
#             messages.success(request, f"{action_type.capitalize()} submitted successfully!")
#             return redirect('view-product', product_id=product.id)
#         else:
#             messages.error(request, f"Invalid {action_type} submission. Please correct the errors.")
#     else:
#         form = CreateReviewForm()

#     return render(request, 'submit_review_rating.html', {'form': form, 'product': product})


#dashboard view
@login_required
def dashboard_view(request):
   
    recommended_products = Products.objects.order_by('?')[:6]

    
    for product in recommended_products:
        if product.product_image:
            with open(product.product_image.path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')        
        else:
            product.image_data = ""

    return render(request, 'dashboard.html', {
        'recommended_products': recommended_products
    })



# def submit_view(request):
#     if request.method == 'POST':
#         # handle form submission
#         return HttpResponse("Form submitted successfully!")
#     return HttpResponse("This page only handles POST requests.")


#dashboard/profile
@login_required
def profile_view(request):
    return render(request, "profile.html")

#dashboard/profile/changeusername
@login_required
def change_username_view(request):
    if request.method == 'POST':
        form  = ChangeUsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('Profile')
    else:
        form = ChangeUsernameForm(instance = request.user)
    return render(request, 'change_username.html', {'form': form})

#change password
@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            current = form.cleaned_data.get('current_password')
            new = form.cleaned_data.get('new_password')
            if not check_password(current, user.password):
                messages.error(request, "Current password is incorrect")
            else:
                user.set_password(new)
                user.save()  
                update_session_auth_hash(request, user)  
                messages.success(request, "Password successfully changed.")
                return redirect('profile')
    else:
        form = CustomPasswordChangeForm()
    
    return render(request, 'change_password_custom.html', {'form': form})

#buy-product success
@login_required
def purchase_success_view(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    return render(request, 'purchase_success.html', {'product': product})



@login_required
@only_bought
def submit_review_view(request, product_id):
    form = ReviewForm()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product_id = product_id
            review.save()
            messages.success(request, "Your review has been submitted.")
            return redirect('view-product', product_id=product_id)
    return render(request, 'martapp/submit_review.html', {'form': form, 'product_id': product_id})

@login_required
@only_bought
def submit_rating_view(request, product_id):
    form = RatingForm()
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.product_id = product_id
            rating.save()
            messages.success(request, "Your rating has been submitted.")
            return redirect('view-product', product_id=product_id)
    return render(request, 'martapp/submit_rating.html', {'form': form, 'product_id': product_id})

def success_page_view(request, product_id=None):
    product = None
    if product_id:
        product = get_object_or_404(Products, id=product_id)
    return render(request, 'success_page.html', {'product': product})