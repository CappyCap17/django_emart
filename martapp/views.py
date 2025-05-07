from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from .forms import RegisterUserForm, LoginUserForm, CreateProductForm, CreateReviewForm, ChangeUsernameForm, ChangePasswordForm, ReviewForm, RatingForm, StockUpdateForm, CartQuantityForm, CheckoutForm
from .models import CustomUser, Products, ProductReviews, ProductsBought, Purchase, CartItem 
from functools import wraps
import random
from django.http import HttpResponse
from django.contrib.auth.hashers import check_password
import base64
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin


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

                request.session['username'] = username
                request.session['login_time'] = str(user.last_login)

                response = redirect("dashboard")
                response.set_cookie('last_login_user', username, max_age=3600)  # 1 hour expiry

                messages.success(request, "Login successful!")

                print(f"[AUTH] User authenticated: {request.user.is_authenticated} | Username: {request.user.username}")

                return response
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid login credentials.")

        return render(request, "login.html", {'form': form})


# ** Logout User ** #
@login_required
def logout_view(request):
    logout(request)  # Destroys session
    response = redirect('login')
    response.delete_cookie('last_login_user')  # Remove custom cookie
    messages.success(request, "You have been logged out.")
    return response



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
        return redirect('dashboard')

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
import base64
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from martapp.models import Products  # Ensure this is imported

# Dashboard View
class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        username = request.session.get('username')  
        last_login_user = request.COOKIES.get('last_login_user') 

        recommended_products = Products.objects.filter(is_listed=True).order_by('?')[:6]

        print(f"[DEBUG] Username: {username}, Last Login Cookie: {last_login_user}")
        print(f"[DEBUG] Recommended Product IDs: {[p.id for p in recommended_products]}")

        for product in recommended_products:
            if product.product_image:
                try:
                    with open(product.product_image.path, 'rb') as image_file:
                        product.image_data = base64.b64encode(image_file.read()).decode('utf-8')
                
                    print(f"[DEBUG] Loaded image for product ID {product.id} from: {product.product_image.path}")
                except Exception as e:
                    print(f"[ERROR] Failed to load image for product ID {product.id}: {e}")
                    product.image_data = ""
            else:
                print(f"[DEBUG] No image for product ID {product.id}")
                product.image_data = ""

        context = {
            'username': username,
            'last_user_cookie': last_login_user,
            'recommended_products': recommended_products
        }
        return render(request, 'dashboard.html', context)


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

    messages.success(request, f"'{product.product_name}' has been added to your cart.")
    return redirect('buy_product', product_id=product.id)

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
def remove_from_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    cart_item = get_object_or_404(CartItem, user=request.user, product=product)
    cart_item.delete()
    return redirect('view-cart')

#buy-cart
@login_required
def buy_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f"Insufficient stock for {item.product.product_name}")
            return redirect('view-cart')

    for item in cart_items:
        product = item.product
        product.stock -= item.quantity
        product.save()

    
        ProductsBought.objects.create(
            buyer=request.user,
            product=product,
            quantity=item.quantity,
            price=item.product.price,
            date_purchased= timezone.now(),
            seller=item.product.seller_name,
        )

    cart_items.delete()
    messages.success(request, "Purchase completed successfully!")
    return redirect('dashboard') 

#cart view
class CartView(LoginRequiredMixin, View):

    def get(self, request):
    
        cart_items = CartItems.objects.filter(user=request.user)

        
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        return render(request, 'buy_cart.html', {
            'cart_items': cart_items,
            'total_price': total_price
        })

    def post(self, request):
        
        action = request.GET.get('action')
        product_id = request.GET.get('product_id')

        if not action or not product_id:
            return redirect('buy_cart')

        product = get_object_or_404(Product, id=product_id)

        if action == 'add':
            cart_item, created = CartItems.objects.get_or_create(user=request.user, product=product)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            messages.success(request, f"'{product.product_name}' has been added to your cart.")
            return redirect('buy_cart')

        elif action == 'remove':
            CartItems.objects.filter(user=request.user, product=product).delete()
            messages.info(request, f"{product.product_name} removed from cart.")

        elif action == 'buy':
            if product.stock > 0:
                product.stock -= 1
                product.save()
                PurchaseHistory.objects.create(user=request.user, product=product)
                CartItems.objects.filter(user=request.user, product=product).delete()
                messages.success(request, f"You bought {product.name} successfully!")
            else:
                messages.error(request, f"{product.product_name} is out of stock.")

        return redirect('buy_cart')




#checkout 
@login_required
def checkout_view(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        if quantity > product.stock:
            messages.error(request, "Not enough stock.")
            return redirect('buy_product', product_id=product_id)

        if product.product_image:
            with product.product_image.open('rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        else:
            encoded_image = ''
            
        total_price = product.price * quantity

        return render(request, 'checkout.html', {
            'product': product,
            'product_image_base64': encoded_image,
            'quantity': quantity,
            'total_price': total_price  
        })

    return redirect('buy_product', product_id=product_id)



@login_required
def confirm_purchase_view(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        if quantity > product.stock:
            messages.error(request, "Not enough stock available!")
            return redirect('buy_product', product_id=product.id)

        ProductsBought.objects.create(
            product=product,
            buyer=request.user,
            seller=product.seller_name,
            price=product.price * quantity
        )

        product.stock -= quantity
        product.save()

        messages.success(request, "Purchase successful!")
        return render(request, 'purchase_success.html', {
            'product': product,
            'quantity': quantity
        })

    return redirect('dashboard')
    
@login_required
def checkout_success_view(request):
    info = request.session.get('checkout_info', {})
    return render(request, 'martapp/checkout_success.html', {'info': info})