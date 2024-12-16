from django.contrib import admin
from django import forms
from .models import Customer, Product, Order, OrderItem, ShippingAddress, Size, ProductImage

# Custom form for Product model to conditionally display gender field
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show gender field only if the category is 'Clothes' or 'Shoes'
        if self.instance and self.instance.category in ['clothes', 'shoes']:
            self.fields['gender'].required = True
        else:
            self.fields['gender'].required = False

# Inline admin for ProductImage model
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty forms to display
    fields = ('image',)

# Product admin
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm  # Use the custom form
    list_display = ('name', 'price', 'category', 'stock_quantity', 'is_in_stock')
    list_filter = ('category',)
    search_fields = ('name', 'category')
    fieldsets = (
        (None, {
            'fields': ('name', 'price', 'digital', 'image', 'category', 'stock_quantity', 'description', 'delivery_returns', 'gender')
        }),
        ('Material and Size', {
            'fields': ('material', 'sizes')  # Sizes as a Many-to-Many field
        }),
    )
    inlines = [ProductImageInline]  # Add inline for multiple images

    # Method to show 'In Stock' as a boolean checkmark
    def is_in_stock(self, obj):
        return obj.stock_quantity > 0
    is_in_stock.boolean = True
    is_in_stock.short_description = 'In Stock'

# Customer Admin to ensure user association
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'user')  # Display the associated user
    search_fields = ('name', 'email', 'user__username')

    # Ensure customer is created when User is created
    def save_model(self, request, obj, form, change):
        if not obj.user:
            user = request.user  # Can be modified based on the user creation logic
            obj.user = user
        super().save_model(request, obj, form, change)

# Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'date_ordered', 'complete', 'transaction_id')
    search_fields = ('customer__name', 'transaction_id')
    list_filter = ('complete',)

    def save_model(self, request, obj, form, change):
        if obj.complete:
            # Update stock when order is completed
            for item in obj.orderitem_set.all():
                item.update_stock()
        super().save_model(request, obj, form, change)

# OrderItem Admin
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity', 'get_total')
    search_fields = ('product__name', 'order__id')

# ShippingAddress Admin
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order', 'address', 'city', 'state', 'zipcode')
    search_fields = ('customer__name', 'order__id', 'city', 'state')

# Size Admin
class SizeAdmin(admin.ModelAdmin):
    list_display = ('size_label', 'category')

# Register models
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(Size, SizeAdmin)
