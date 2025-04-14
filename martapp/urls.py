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
    dashboard_view,
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
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('sell/', sell_product_view, name='sell_product'),
    path('search/', search_view, name='search'), 
    path('profile/', profile_view, name='profile'),
    path('recommendations/', recommendation_view, name='recommendations'),
    path('product/<int:product_id>/', view_product_view, name='view-product'),
   path('buy/<int:product_id>/', buy_product_view, name='buy-product'),
    path('product/<int:product_id>/submit/review/', submit_review_view, name='submit-review'),
path('product/<int:product_id>/submit/rating/', submit_rating_view, name='submit-rating'),
    path('purchase/success/<int:product_id>/', success_page_view, name='success_page'),
    path('seller-inventory/', seller_inventory_view, name='seller_inventory'),
    
    # path('submit/', submit_view, name='submit'),
    path('change-username/', change_username_view, name='change_username'),
    path('change-password/', change_password_view, name='change_password'),


]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)