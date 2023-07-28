from django.urls import path
from accounts.views import *

urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('activate/<email_token>/', activate_email, name='activate_email'),
    path('logout/', logout_user, name="logout"),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('change-password/', change_password, name='change_password'),
    path('email-password/<token>/', email_password, name='email_password'),
    # path('invoice/', invoice, name="invoice"),
    path('add-to-cart/<uid>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart, name='cart'),
    path('remove-cart/<cart_item_uid>/', remove_cart, name="remove_cart"),
    path('remove-coupon/<cart_uid>/', remove_coupon, name="remove_coupon"),
    path('success/', success, name='success'),
]