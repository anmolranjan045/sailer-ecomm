from django.shortcuts import render
from products.models import Product, ProductReview

def get_products(request, slug):
    context = {}
    try:
        product_obj = Product.objects.get(slug=slug)
        try:
            review = ProductReview.objects.filter(product=product_obj)
            context['reviews'] = review
        except Exception as e:
            print(e)
        context['product'] = product_obj
        context['count'] = request.user.profile.get_cart_count()
        
        if request.GET.get('size'):
            size = request.GET.get('size')
            price = product_obj.get_product_price_be_size(size)
            context['selected_size'] = size
            context['updated_price'] = price
        
        if request.method == 'POST':
            rating = request.POST['rating']
            message_review = request.POST['message_review']

            review = ProductReview.objects.create(product=product_obj, 
                                                  name=request.user.username, 
                                                  rating=rating, 
                                                  message_review=message_review)
            review.save()

        return render(request, 'products/products.html', context=context)

    except Exception as e:
        print(e)
    