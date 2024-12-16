from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart
from .models import Product, ProductImage
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.forms import UserCreationForm
from .models import Order, Customer
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    return render(request, 'store/home.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('store')  # Redirect to home or dashboard after login
    else:
        form = AuthenticationForm()

    return render(request, 'store/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = UserCreationForm()

    return render(request, 'store/register.html', {'form': form})

def profile(request):
    # Get the Customer instance for the current user
    customer = Customer.objects.get(user=request.user)
    
    # Filter orders based on the Customer instance
    orders = Order.objects.filter(customer=customer)
    
    return render(request, 'store/profile.html', {'orders': orders})

def logout_view(request):
    logout(request)
    return redirect('login')

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Keep the user logged in after password change
            return redirect('profile')  # Redirect back to profile page
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'store/change_password.html', {'form': form})

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        user.profile.phone_number = request.POST.get('phone_number', '')
        user.profile.address.street = request.POST.get('street', '')
        user.profile.address.city = request.POST.get('city', '')
        user.profile.address.postal_code = request.POST.get('postal_code', '')
        user.profile.address.country = request.POST.get('country', '')
        user.save()
        user.profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')  # Replace 'profile' with the name of your profile page URL.
    return render(request, 'profile.html')

def store(request):
    if request.user.is_authenticated:
        # Ensure a Customer is created if it doesn't exist
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # Create empty cart for non-logged-in user
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        for i in cart:
            try:
                cartItems += cart[i]['quantity']
                product = Product.objects.get(id=i)
                total = product.price * cart[i]['quantity']  # Multiplying price by quantity
                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']

                item = {
                    'id': product.id,
                    'product': {'id': product.id, 'name': product.name, 'price': product.price, 'imageURL': product.imageURL},
                    'quantity': cart[i]['quantity'],
                    'digital': product.digital,
                    'get_total': total,  # Showing total for each item
                }
                items.append(item)

                if product.digital == False:
                    order['shipping'] = True
            except:
                pass

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def product_detail(request, product_id):
    # Fetch the product based on its ID
    product = get_object_or_404(Product, id=product_id)
    
    # Fetch the images related to the product and convert the QuerySet to a list
    images = list(product.images.all())

    # Default to the first image if no image is specified in the query
    current_image_id = request.GET.get('image')
    
    if current_image_id:
        try:
            current_image = next(image for image in images if image.id == int(current_image_id))
        except StopIteration:
            current_image = images[0]  # fallback to the first image
    else:
        current_image = images[0]  # fallback to the first image

    # Determine the previous and next image by finding their indices in the list
    current_image_index = images.index(current_image)
    previous_image = images[current_image_index - 1] if current_image_index > 0 else None
    next_image = images[current_image_index + 1] if current_image_index < len(images) - 1 else None

    # Initialize cartItems
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        cartItems = sum(cart[item]['quantity'] for item in cart)

    # Render the product detail template with the product, current_image, previous_image, next_image, and cartItems context
    return render(request, 'store/product.html', {
        'product': product,
        'current_image': current_image,
        'previous_image': previous_image,
        'next_image': next_image,
        'cartItems': cartItems,
    })


def cart(request):
    if request.user.is_authenticated:
        # Ensure a Customer is created if it doesn't exist
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # Create empty cart for non-logged-in user
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

        for i in cart:
            try:
                cartItems += cart[i]['quantity']
                product = Product.objects.get(id=i)
                total = product.price * cart[i]['quantity']  # Multiplying price by quantity
                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']

                item = {
                    'id': product.id,
                    'product': {'id': product.id, 'name': product.name, 'price': product.price, 'imageURL': product.imageURL},
                    'quantity': cart[i]['quantity'],
                    'digital': product.digital,
                    'get_total': total,  # Showing total for each item
                }
                items.append(item)

                if product.digital == False:
                    order['shipping'] = True
            except:
                pass

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        # Ensure a Customer is created if it doesn't exist
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # Create empty cart for non-logged-in user
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def updateitem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer, created = Customer.objects.get_or_create(user=request.user)
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
    else:
        print('User is not logged in')

    return JsonResponse('Payment submitted..', safe=False)

