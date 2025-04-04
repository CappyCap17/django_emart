from django.urls import path
from .views import (
    RegisterUserView,
    LoginView,
    logout_view,
    sell_product_view,
    search_view,  # Ensure this matches the function name in views.py
    recommendation_view,
    view_product_view,
    buy_product_view,
    submit_review_rating_view,
    dashboard_view,
    # submit_view,
    profile_view,
    change_username_view,
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
    path('product/<int:product_id>/buy/', buy_product_view, name='buy-product'),
    path('product/<int:product_id>/review/', submit_review_rating_view, name='submit-review'),
    # path('submit/', submit_view, name='submit'),
    path('change-username/', change_username_view, name='change_username'),
    path('change-password/', auth_views.PasswordChangeView.as_view(template_name='change_password.html'), name='change_password'),


]
