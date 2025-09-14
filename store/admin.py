from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Product, ProductImage, Order, OrderItem, Cart, CartItem, Payment, Wishlist, ProductReview


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


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin configuration for ProductImage model."""
    
    list_display = ('product', 'image_type', 'sort_order', 'is_active', 'image_preview', 'created_at')
    list_filter = ('image_type', 'is_active', 'created_at')
    search_fields = ('product__name', 'alt_text', 'caption')
    list_editable = ('sort_order', 'is_active')
    ordering = ('product', 'sort_order', 'created_at')
    
    def image_preview(self, obj):
        """Display image preview in admin."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Preview'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    
    list_display = (
        'name', 'category', 'current_price', 'stock_quantity', 
        'average_rating_display', 'total_reviews_display', 'is_active', 'is_featured', 'condition', 'created_at'
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
                '<span style="text-decoration: line-through;">{} MAD</span> <span style="color: red;">{} MAD</span>',
                obj.price, obj.sale_price
            )
        return f"{obj.price} MAD"
    current_price.short_description = 'Current Price'
    
    def average_rating_display(self, obj):
        """Display average rating with stars."""
        rating = obj.average_rating
        if rating > 0:
            stars = '★' * int(rating) + '☆' * (5 - int(rating))
            return format_html(
                '<span style="color: #ffc107;">{}</span> <span style="font-size: 0.8em;">({})</span>',
                stars, rating
            )
        return format_html('<span style="color: #ccc;">☆☆☆☆☆</span>')
    average_rating_display.short_description = 'Rating'
    
    def total_reviews_display(self, obj):
        """Display total reviews count with link."""
        count = obj.total_reviews
        if count > 0:
            url = reverse('admin:store_productreview_changelist') + f'?product__id__exact={obj.id}'
            return format_html('<a href="{}">{} reviews</a>', url, count)
        return '0 reviews'
    total_reviews_display.short_description = 'Reviews'


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
        return f"{obj.total_price} MAD"
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
        return f"{obj.total_price} MAD"
    total_price.short_description = 'Total Price'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model."""
    
    list_display = (
        'order', 'payment_method', 'amount', 'status', 
        'transaction_id', 'created_at'
    )
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('order__order_number', 'transaction_id', 'order__customer__email')
    readonly_fields = ('created_at', 'processed_at')
    list_editable = ('status',)
    
    fieldsets = (
        (None, {
            'fields': ('order', 'payment_method', 'amount', 'status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'processor_response')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin configuration for Wishlist model."""
    
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at', 'product__category')
    search_fields = ('user__email', 'product__name')
    readonly_fields = ('added_at',)
    list_select_related = ('user', 'product')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Admin configuration for ProductReview model."""
    
    list_display = (
        'product', 'user', 'rating_display', 'title', 
        'is_approved', 'is_verified_purchase', 'created_at'
    )
    list_filter = (
        'rating', 'is_approved', 'is_verified_purchase', 
        'product__category', 'created_at'
    )
    search_fields = ('product__name', 'user__email', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_approved',)
    
    fieldsets = (
        (None, {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        ('Status', {
            'fields': ('is_approved', 'is_verified_purchase')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_display(self, obj):
        """Display rating with stars."""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color: #ffc107;">{}</span> <span style="font-size: 0.8em;">({}/5)</span>',
            stars, obj.rating
        )
    rating_display.short_description = 'Rating'
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        """Approve selected reviews."""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews were approved.')
    approve_reviews.short_description = 'Approve selected reviews'
    
    def disapprove_reviews(self, request, queryset):
        """Disapprove selected reviews."""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews were disapproved.')
    disapprove_reviews.short_description = 'Disapprove selected reviews'
