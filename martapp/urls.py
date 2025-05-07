from django.urls import path
from .views import (
    RegisterUserView,
    LoginView,
    logout_view,
    sell_product_view,
    search_view, 
    recommendation_view,
    view_product_view,
    buy_product_view,
    DashboardView,
    # submit_view,
    profile_view,
    change_username_view,
    change_password_view,
    profile_view,
    purchase_success_view,
    submit_rating_view,
    submit_review_view,
    success_page_view,
    seller_inventory_view,
    view_cart,
    remove_from_cart,
    add_to_cart,
    view_cart,
    buy_cart,
    checkout_success_view,
    checkout_view,
    confirm_purchase_view

)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('sell/', sell_product_view, name='sell_product'),
    path('search/', search_view, name='search'), 
    path('profile/', profile_view, name='profile'),
    path('recommendations/', recommendation_view, name='recommendations'),
    path('product/<int:product_id>/', view_product_view, name='view-product'),
    path('buy/<int:product_id>/', buy_product_view, name='buy_product'),
    path('product/<int:product_id>/submit/review/', submit_review_view, name='submit-review'),
    path('product/<int:product_id>/submit/rating/', submit_rating_view, name='submit-rating'),
    path('purchase/success/<int:product_id>/', success_page_view, name='success_page'),
    path('seller-inventory/', seller_inventory_view, name='seller_inventory'),
    path('change-username/', change_username_view, name='change_username'),
    path('change-password/', change_password_view, name='change_password'),
    path('cart/', view_cart, name='view-cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove-from-cart'),
    path('cart/buy/', buy_cart, name='buy-cart'),
    path('checkout/<int:product_id>/', checkout_view, name='checkout'),
    path('checkout/success/', checkout_success_view, name='checkout_success'),
    path('confirm/<int:product_id>/', confirm_purchase_view, name='confirm_purchase'),


]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)