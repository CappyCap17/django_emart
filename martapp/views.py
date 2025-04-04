from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from .forms import RegisterUserForm, LoginUserForm, CreateProductForm, CreateReviewForm
from .models import CustomUser, Products, ProductReviews, ProductsBought
from functools import wraps
import random
from django.http import HttpResponse


# Decorators
def only_bought(view_func):
    @wraps(view_func)
    def wrapper(request, product_id, *args, **kwargs):
        product = get_object_or_404(Products, id=product_id)
        has_bought = ProductsBought.objects.filter(buyer=request.user, product=product).exists()
        if not has_bought:
            messages.error(request, "You need to buy the product to access this feature!")
            return redirect('view-product', product_id=product.id)
        return view_func(request, product_id, *args, **kwargs)
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
        form = CreateProductForm()
        form.fields.pop('seller_name')  
    return render(request, 'sell_product.html', {'form': form})

#Search Products
@login_required
def search_view(request):
    query = request.GET.get('query', '')
    results = Products.objects.filter(product_name__icontains=query)
    paginator = Paginator(results, 6)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    return render(request, 'search_results.html', {'products': products, 'query': query})

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

# Buy Product
@login_required
def buy_product_view(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    if request.method == 'POST':
        if request.user == product.seller_name:
            messages.error(request, "You cannot buy your own product!")
            return redirect('view-product', product_id=product.id)
        purchase = ProductsBought.objects.create(
            product=product,
            buyer=request.user,
            seller=product.seller_name,
            price=product.price
        )
        purchase.save()
        messages.success(request, "Purchase successful!")
        return redirect('success_page')
    return render(request, 'buy_product.html', {'product': product})

#Submit Review and Rating
@login_required
@only_bought
def submit_review_rating_view(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    if request.method == 'POST':
        form = CreateReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Review submitted successfully!")
            return redirect('view-product', product_id=product.id)
        else:
            messages.error(request, "Invalid review submission. Please correct the errors below.")
    else:
        form = CreateReviewForm()
    return render(request, 'submit_review.html', {'form': form, 'product': product})

from .models import Products  # Or whatever your Product model is

@login_required
def dashboard_view(request):
    # Fetch 6 random recommended products
    recommended_products = Products.objects.order_by('?')[:6]

    # Convert binary image data to base64 for embedding
    for product in recommended_products:
        if product.image:
            import base64
            product.image_data = base64.b64encode(product.image).decode('utf-8')
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

@login_required
def profile_view(request):
    return render(request, "profile.html")

@login_required
def change_username_view(request):
    return render(request, 'change_username.html')