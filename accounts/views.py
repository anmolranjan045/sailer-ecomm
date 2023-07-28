from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from accounts.models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from base.emails import send_forget_password_mail
from accounts.models import Profile, Cart, CartItems
from products.models import Product, SizeVariant, Coupon
from django.conf import settings
import razorpay
import uuid

def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user_obj = User.objects.filter(username = username)
        
        if not user_obj.exists():
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)
        
        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'Your account is not verified.')
            return HttpResponseRedirect(request.path_info)
        
        user_obj = authenticate(username=username, password=password)
        
        if user_obj:
            login(request, user_obj)
            return redirect('/')
        
        messages.warning(request, 'Invalid credentials.')
    
    return render(request, 'accounts/login.html')




def register_page(request):
    if request.method == "POST":
        user_name = request.POST.get('user_name')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user_obj = User.objects.filter(username = user_name)
        if user_obj.exists():
            messages.warning(request, 'Username is already taken.')
            return HttpResponseRedirect(request.path_info)
        
        user_obj = User.objects.filter(email = email)
        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)
        
        print(email)
        
        user_obj = User.objects.create(first_name = first_name,
                                       last_name = last_name,
                                       email = email,
                                       username = user_name)
        user_obj.set_password(password)
        user_obj.save()
        
        messages.success(request, 'An email has been sent to your mail.')
        
    return render(request, 'accounts/register.html')



def activate_email(request, email_token):
    try:
        user = Profile.objects.get(email_token = email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Invalid Email Token')
    

@login_required
def logout_user(request):
    messages.success(request, "You were logged out!!")
    logout(request)
    return redirect('/')


def email_password(request, token):
    try:
        profile_obj = Profile.objects.get(forget_password_token=token)
        context = {'user_id': profile_obj.user.id}
        print(context)
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            verify = request.POST.get('verify')
            user_id = request.POST.get('user_id')
            print(user_id)
            if user_id is None:
                messages.warning(request, 'User ID not found.')
                return redirect(f'/accounts/email-password/{token}/')
            
            if new_password != verify:
                messages.warning(request, 'New Passwords not matching.')
                return redirect(f'/accounts/email-password/{token}/')
            
            user_obj = User.objects.get(id=user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('/accounts/login/')
    except Exception as e:
        print(e)
    return render(request, 'accounts/email-password.html', context)



def forgot_password(request):
    try:
        if request.method == "POST":
            username = request.POST.get('username')
            user_obj = User.objects.get(username=username)
            
            if not user_obj:
                messages.warning(request, 'Username does not exsist.')
                return HttpResponseRedirect(request.path_info)
            
            profile_obj = Profile.objects.get(user=user_obj)
            profile_obj.forget_password_token = str(uuid.uuid4())
            profile_obj.save()
            send_forget_password_mail(user_obj.email, user_obj.username, profile_obj.forget_password_token)
            messages.success(request, 'Please check your inbox and follow the instructions to reset your password.')
            return HttpResponseRedirect(request.path_info)
    
    except Exception as e:
        print(e)
    return render(request, 'accounts/forgot_password.html')



@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        verify = request.POST.get('verify')
        user_obj = User.objects.get(username=request.user)

        if not check_password(old_password, user_obj.password):
            messages.warning(request, 'Incorrect old password.')
            return HttpResponseRedirect(request.path_info)
        
        if check_password(new_password, user_obj.password):
            messages.warning(request, 'New Password same as the Old Password.')
            return HttpResponseRedirect(request.path_info)
        
        if new_password != verify:
            messages.warning(request, 'New Passwords not matching.')
            return HttpResponseRedirect(request.path_info)
        
        user_obj.set_password(new_password)
        user_obj.save()
        messages.success(request, 'Password changed successfully.')
        return HttpResponseRedirect(request.path_info)
    return render(request, 'accounts/change_password.html')



@login_required
def add_to_cart(request, uid):   
    variant = request.GET.get('variant')
    product = Product.objects.get(uid=uid)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user = user, is_paid = False)
    
    cart_item = CartItems.objects.create(cart=cart, product=product)
    
    if variant:
        variant = request.GET.get('variant')
        size_variant = SizeVariant.objects.get(size_name=variant)
        cart_item.size_variant = size_variant
        cart_item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



@login_required
def remove_cart(request, cart_item_uid):
    try:
        cart_item = CartItems.objects.get(uid = cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        


@login_required
def cart(request):
    cart_obj = None
    try:
        cart_obj = Cart.objects.get(is_paid=False, user=request.user)
        
    except Exception as e:
        print(e)
        
    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__icontains=coupon)
        
        if not coupon_obj.exists():
            messages.warning(request, 'Invalid Coupon')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart_obj.coupon:
            messages.warning(request, 'Coupon already exsits.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart_obj.get_cart_total() < coupon_obj[0].minimum_amount:
            messages.warning(request, f'Amount should be greater than {coupon_obj[0].minimum_amount}.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if coupon_obj[0].is_expired:
            messages.warning(request, 'Coupon is expired.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        cart_obj.coupon = coupon_obj[0]
        cart_obj.save()
        messages.success(request, 'Coupon applied.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    if cart_obj and cart_obj.get_cart_total():
        client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
        payment = client.order.create({'amount': cart_obj.get_cart_total()*100, 'currency': 'INR', 'payment_capture': 1})
        cart_obj.razor_pay_order_id = payment['id']
        cart_obj.save()
    else:
        payment = None
    context = {'cart': cart_obj, 'payment': payment}
    return render(request, 'accounts/cart.html', context)



@login_required
def remove_coupon(request, cart_uid):
    cart = Cart.objects.get(uid=cart_uid)
    cart.coupon = None
    cart.save()
    messages.success(request, 'Coupon Removed.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



@login_required
def success(request):
    order_id = request.GET.get('order_id')
    cart = Cart.objects.get(razor_pay_order_id = order_id)
    cart.is_paid = True
    cart.save()
    return HttpResponse('Payment Success')
