from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.name or "Unnamed Customer"

    def save(self, *args, **kwargs):
        # Automatically populate name and email if user exists
        if self.user:
            self.name = self.user.username
            self.email = self.user.email
        super().save(*args, **kwargs)

class Size(models.Model):
    CATEGORY_CHOICES = (
        ('clothes', 'Clothes'),
        ('shoes', 'Shoes'),
    )
    size_label = models.CharField(max_length=10)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.size_label} ({self.category})"

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('clothes', 'Clothes'),
        ('shoes', 'Shoes'),
        ('books', 'Books'),
        ('watches', 'Watches'),
    )
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    name = models.CharField(max_length=200)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    stock_quantity = models.IntegerField(default=0)
    description = models.TextField()
    delivery_returns = models.TextField(default="No return policy specified.")
    material = models.CharField(max_length=200, blank=True, null=True)
    sizes = models.ManyToManyField(Size, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/placeholder.png'

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.name}"

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    sizes = product.sizes.filter(category=product.category) if product.category in ['clothes', 'shoes'] else product.sizes.all()
    context = {
        'product': product,
        'sizes': sizes,
        'is_in_stock': product.is_in_stock,
        'gender': product.gender,
        'images': product.images.all(),
    }
    return render(request, 'store/product.html', context)

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    )
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='payment_instance')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.FloatField()
    payment_status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f"Payment for Order {self.order.id} via {self.payment_method}"

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    payment = models.OneToOneField(Payment, null=True, blank=True, on_delete=models.SET_NULL, related_name='order_instance')

    def __str__(self):
        return f"Order {self.id}"

    @property
    def shipping(self):
        return any(not item.product.digital for item in self.orderitem_set.all())

    @property
    def get_cart_total(self):
        return sum(item.get_total for item in self.orderitem_set.all())

    @property
    def get_cart_items(self):
        return sum(item.quantity for item in self.orderitem_set.all())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.complete:
            for item in self.orderitem_set.all():
                item.update_stock()

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        return self.product.price * self.quantity

    def update_stock(self):
        if self.product.stock_quantity >= self.quantity:
            self.product.stock_quantity -= self.quantity
            self.product.save()

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address}, {self.city}"

