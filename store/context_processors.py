import json

def cart_total(request):
    cart = request.COOKIES.get('cart', '{}')  # Get cart from cookies
    try:
        cart = json.loads(cart)  # Convert JSON string to dictionary
    except json.JSONDecodeError:
        cart = {}

    total_items = sum(item['quantity'] for item in cart.values())
    return {'cartItems': total_items}
