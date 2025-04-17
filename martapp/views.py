from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from .forms import RegisterUserForm, LoginUserForm, CreateProductForm, CreateReviewForm, ChangeUsernameForm, ChangePasswordForm, ReviewForm, RatingForm, StockUpdateForm, CartQuantityForm
from .models import CustomUser, Products, ProductReviews, ProductsBought, Purchase, CartItem 
from functools import wraps
import random
from django.http import HttpResponse
from django.contrib.auth.hashers import check_password
import base64
from django.contrib.auth.forms import PasswordChangeForm

# Decorators
def only_bought(view_func):
    def wrapper(request, product_id, *args, **kwargs):
        if Purchase.objects.filter(user=request.user, product__id=product_id).exists():
            return view_func(request, product_id, *args, **kwargs)
        
        product = get_object_or_404(Products, id=product_id)
        messages.error(request, "You must buy this product before leaving a review or rating.")
        return redirect('view-product', product_id=product.id)   
    return wrapper


# ** Register User ** #
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


# ** Login User ** #
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


# ** Logout User ** #
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


# ** Sell Product ** #
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


# ** Search Products ** #
@login_required
def search_view(request):
    query = request.GET.get('q') 
    results = []

    if query:
        results = Products.objects.filter(
            is_listed=True
        ).filter(
            product_name__icontains=query
        ) | Products.objects.filter(
            is_listed=True
        ).filter(
            product_type__icontains=query
        ) | Products.objects.filter(
            is_listed=True
        ).filter(
            seller_name__username__icontains=query
        )

    return render(request, 'search_results.html', {'query': query, 'results': results})


# ** Product Recommendations ** #
@login_required
def recommendation_view(request):
    display = list(Products.objects.filter(is_listed=True).order_by('-customer_rating')[:6])
    random.shuffle(display)
    return render(request, 'dashboard.html', {'display': display})


# ** View Product Details ** #
@login_required
def view_product_view(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    return render(request, 'product.html', {'product': product})


# Buy Product 
@login_required
def buy_product_view(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    if request.user == product.seller_name:
        messages.error(request, "You cannot buy your own product!")
        return redirect('view-product', product_id=product.id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))  
       
        if quantity > product.stock:
            messages.error(request, "Not enough stock available!")
            return redirect('buy-product', product_id=product.id)

        ProductsBought.objects.create(
            product=product,
            buyer=request.user,
            seller=product.seller_name,
            price=product.price * quantity  
        )

        product.stock -= quantity
        product.save()

        messages.success(request, f"Purchase successful! You bought {quantity} {product.product_name}(s).")
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
@login_required
@only_bought
def submit_review_view(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Your review has been submitted.")
            return redirect('view-product', product_id=product_id)

    return render(request, 'martapp/submit_review_rating.html', {
        'form': form,
        'product': product,
        'action_type': 'review'
    })

@login_required
@only_bought
def submit_rating_view(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    form = RatingForm()

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.product = product
            rating.save()
            messages.success(request, "Your rating has been submitted.")
            return redirect('view-product', product_id=product_id)

    return render(request, 'martapp/submit_review_rating.html', {
        'form': form,
        'product': product,
        'action_type': 'rating'
    })


# Dashboard View
@login_required
def dashboard_view(request):

    recommended_products = Products.objects.filter(is_listed=True).order_by('?')[:6]

    for product in recommended_products:
        if product.product_image:
            with open(product.product_image.path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')        
        else:
            product.image_data = ""

    return render(request, 'dashboard.html', {
        'recommended_products': recommended_products
    })

# Profile View
@login_required
def profile_view(request):
    user = request.user  


    products_bought = ProductsBought.objects.filter(buyer=user)
    products_sold = ProductsBought.objects.filter(seller=user)

    
    context = {
        'profile': user,
        'products_bought': products_bought,
        'products_sold': products_sold,
    }

    return render(request, 'profile.html', context)


# Seller Inventory View
@login_required
def seller_inventory_view(request):
    seller = request.user  
    products = Products.objects.filter(seller_name=seller) 

    if request.method == 'POST':
        product_id = request.POST.get('product_id')  # 
        product = get_object_or_404(Products, id=product_id, seller_name=seller)  

        if 'delete_product' in request.POST:
            product.delete()
            return redirect('seller_inventory')  

        elif 'list_product' in request.POST:
            product.is_listed = True
            product.save()

        elif 'unlist_product' in request.POST:
            product.is_listed = False
            product.save()

        elif 'add_stock' in request.POST:
            add_stock = int(request.POST.get('add_stock', 0))
            if add_stock > 0:
                product.stock += add_stock
                product.save()

        elif 'remove_stock' in request.POST:
            remove_stock = int(request.POST.get('remove_stock', 0))
            if remove_stock > 0 and product.stock >= remove_stock:
                product.stock -= remove_stock
                product.save()

    return render(request, 'seller_inventory.html', {'products': products})


# Purchase Success Page 
@login_required
def purchase_success_view(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    return render(request, 'purchase_success.html', {'product': product})

@login_required
def change_username_view(request):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            new_username = form.cleaned_data['username']
            request.user.username = new_username  
            request.user.save()
            messages.success(request, "Your username has been updated successfully.")
            return redirect('profile')  
    else:
        form = ChangeUsernameForm(instance=request.user)

    return render(request, 'change_username.html', {'form': form})


# ** Change Password View ** #
@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()  # Save the new password
            update_session_auth_hash(request, form.user)  # Prevent session logout
            messages.success(request, "Your password has been updated successfully.")
            return redirect('profile')  # Redirect to profile page after changing password
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})

# Success Page View
@login_required
def success_page_view(request, product_id=None):
    product = None
    if product_id:
        product = get_object_or_404(Products, id=product_id)
    return render(request, 'success_page.html', {'product': product})

#add-t0-cart view
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Product added to cart.")
    return redirect('view-product', product_id=product.id)

#view-cart
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = 0
    for item in cart_items:
        total_price += item.quantity * item.product.price

    if request.method == 'POST':
        for item in cart_items:
            form = CartQuantityForm(request.POST, instance=item, prefix=str(item.id))
            if form.is_valid():
                updated_quantity = form.cleaned_data['quantity']
                if updated_quantity > item.product.stock:
                    messages.error(request, f"Cannot buy more than available stock for {item.product.name}.")
                else:
                    item.quantity = updated_quantity
                    item.save()
        return redirect('view-cart')

    forms_dict = {item.id: CartQuantityForm(instance=item, prefix=str(item.id)) for item in cart_items}

    return render(request, 'buy_cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'forms_dict': forms_dict,
    })

#removefromcart
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('view-cart')

#buy-cart
@login_required
def buy_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f"Insufficient stock for {item.product.name}")
            return redirect('view-cart')

    for item in cart_items:
        product = item.product
        product.stock -= item.quantity
        product.save()

    
        BoughtProduct.objects.create(
            user=request.user,
            product=product,
            quantity=item.quantity,
            bought_at=timezone.now()
        )

    cart_items.delete()
    messages.success(request, "Purchase completed successfully!")
    return redirect('dashboard') 