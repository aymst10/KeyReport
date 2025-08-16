from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Order, OrderItem, Cart, CartItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    
    list_display = ('name', 'slug', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    
    def product_count(self, obj):
        """Display count of products in category."""
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    
    list_display = (
        'name', 'category', 'current_price', 'stock_quantity', 
        'is_active', 'is_featured', 'condition', 'created_at'
    )
    list_filter = (
        'category', 'is_active', 'is_featured', 'condition', 
        'brand', 'created_at'
    )
    search_fields = ('name', 'sku', 'description', 'brand', 'model')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active', 'is_featured', 'stock_quantity')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description', 'short_description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'sale_price', 'sku', 'stock_quantity', 'min_stock_level')
        }),
        ('Product Details', {
            'fields': ('brand', 'model', 'condition', 'warranty_months')
        }),
        ('Images', {
            'fields': ('main_image', 'additional_images')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def current_price(self, obj):
        """Display current price with sale indicator."""
        if obj.sale_price and obj.sale_price < obj.price:
            return format_html(
                '<span style="text-decoration: line-through;">${}</span> <span style="color: red;">${}</span>',
                obj.price, obj.sale_price
            )
        return f"${obj.price}"
    current_price.short_description = 'Current Price'


class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem."""
    
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""
    
    list_display = (
        'order_number', 'customer', 'status', 'payment_status', 
        'total_amount', 'created_at'
    )
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'customer__email', 'customer__first_name', 'customer__last_name')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    list_editable = ('status', 'payment_status')
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        (None, {
            'fields': ('order_number', 'customer', 'status', 'payment_status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 'total_amount')
        }),
        ('Shipping Information', {
            'fields': (
                'shipping_address', 'shipping_city', 'shipping_state', 
                'shipping_zip_code', 'shipping_country'
            )
        }),
        ('Contact Information', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'staff_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_formset(self, request, form, formset, change):
        """Save formset and recalculate order total."""
        super().save_formset(request, form, formset, change)
        if formset.model == OrderItem:
            form.instance.calculate_total()


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart model."""
    
    list_display = ('user', 'total_items', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def total_items(self, obj):
        """Display total items in cart."""
        return obj.total_items
    total_items.short_description = 'Total Items'
    
    def total_price(self, obj):
        """Display total price of cart."""
        return f"${obj.total_price}"
    total_price.short_description = 'Total Price'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for CartItem model."""
    
    list_display = ('cart', 'product', 'quantity', 'total_price', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('cart__user__email', 'product__name')
    readonly_fields = ('added_at',)
    
    def total_price(self, obj):
        """Display total price for cart item."""
        return f"${obj.total_price}"
    total_price.short_description = 'Total Price'
