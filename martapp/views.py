from django.shortcuts import render, redirect, error_code_on_404
from django.contrib.auth import AuthenticationForm, AuthenticateUser, authenticate, login
from .forms import RegisterUser, LoginUser, CreateProduct, CreateReview
from .models import CustomUser, Products, ProductReviews
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

def RegisterUserView(request):
    if request.method == 'POST':
        forms = RegisterUser(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            messages.success(request,"Successfully registered and logged user in!")
            return redirect("templates/dashboard.html")
        else:
            messages.error(request,"Unsuccessfull, user not registered")
    else:
        forms = RegisterUser()
    return render(request, "register.html", {'form':form})

def Loginview(request):
    if request.method == 'POST':
        forms = LoginUser(data=request.POST)
        if form.isvalid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username==username, password==password)

            if user is not None:
                login(request, user)
                messages.success(request,"login successful!")
                return redirect("templates/dashboard.html")
            else:
                messages.error(request,"Login unsuccessful, Invalid username or password")
        else:
            messages.error(request,"Invalid login credentials")
    else:
        forms = LoginUser()
    return render(request, "login.html",{'form':form})

@login_required
def SellProductView(request):
    if request.method == 'POST':
        forms = CreateProduct(data = request.POST)
        if form.is_invalid():
            product = form.save(commit = False)
            product.seller_name = request.user
            product.save()

            messages.success(request, "Product listed successfully!")
            return redirect("dashboard")
        else:
            messages.error(request, "Product not listed")
    else:
        form = CreateProduct()
    return render(request, 'sell_product.html', {'form': form})
        

