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
)

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('sell/', sell_product_view, name='sell-product'),
    path('search/', search_view, name='search-results'), 
    path('recommendations/', recommendation_view, name='recommendations'),
    path('product/<int:product_id>/', view_product_view, name='view-product'),
    path('product/<int:product_id>/buy/', buy_product_view, name='buy-product'),
    path('product/<int:product_id>/review/', submit_review_rating_view, name='submit-review'),
]
