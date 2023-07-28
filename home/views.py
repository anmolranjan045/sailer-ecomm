from django.shortcuts import render
from products.models import Product
from home.models import Feedback
from django.contrib import messages
from products.models import Coupon


def index(request):
    context = {'products': Product.objects.all()}
    return render(request, 'home/index.html', context)

def feedback(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        feedback_obj = Feedback.objects.create(name=name,
                                               email=email,
                                               subject=subject,
                                               message=message)
        feedback_obj.save()
        messages.success(request, 'Your feedback was submitted successfully.')
    return render(request, 'home/feedback.html')

def offers(request):
    context = {'coupons': Coupon.objects.filter(is_expired=False)}
    if not context['coupons']:
        messages.warning(request, 'There are no coupons available.')
    return render(request, 'home/offers.html', context)
