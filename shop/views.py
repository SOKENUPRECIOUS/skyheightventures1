from django.shortcuts import render, redirect
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from accounts.models import Profile
# Create your views here.
def index(request):
    products = Product.objects.all()[:8]
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'pages/index.html', context)

def shop(request):
    search_query = request.GET.get('search', '') 
    products = Product.objects.all
    if search_query:
        products = Product.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
    else:
        products = Product.objects.all()
    
    categories = Category.objects.all()
    paginator = Paginator(products, 6) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj, 
        'categories': categories,
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'shop/shop.html', context)
def product_detail(request, slug):
    product = Product.objects.get (slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:3]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product-detail.html', context)


def contact(request):
    return render(request, 'pages/contact.html')

def login(request):
    return render(request, 'auth/login.html')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, item_created=  CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
   cart, create = Cart.objects.get_or_create(user=request.user)
   items = cart.items.all()
   total = sum([ item.subtotal()  for item in items])
   context = {
       'items': items,
       'total': total,
   }
   return render(request, 'shop/shop-cart.html', context)


@login_required
def remove_from_cart(request, item_id):
    get_object_or_404(CartItem, id=item_id).delete()
    return redirect('view_cart')

@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.quantity +=1
    item.save()
    return redirect('view_cart')


@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('view_cart')

@login_required
def checkout(request):
    try:
        cart, create = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        total = sum([item.subtotal() for item in items])
    except Cart.DoesNotExist:
        return redirect('view_cart')
    
    if request.method == "POST":
        address1 = request.POST['address1']
        address2 = request.POST['address2']
        phone = request.POST['phone']
        city = request.POST['city']
        state = request.POST['state']
        zipcode = request.POST['zipcode']
        country = request.POST['country']

        # update profile with shipping information
        profile = Profile.objects.update_or_create(
            user=request.user,
            defaults={
                'address1': address1,
                'address2': address2,
                'phone': phone,
                'city': city,
                'state': state,
                'zipcode': zipcode,
                'country': country,
            }
        )
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.save()

        # create an order and order items
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
        )
        for item in items:
            OrderItem.objects.create(
            order=order, 
            product=item.product, 
            quantity=item.quantity,
            price=item.product.price,
            )

        # clear cart 
        cart.items.all().delete()
        return redirect('order_completed', order_id=order.id)

    context = {
        'items': items,
        'total': total,
        'cart': cart,
    }
    return render(request, 'shop/checkout.html', context)

@login_required
def order_completed(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'shop/order-completed.html', {'order': order})

