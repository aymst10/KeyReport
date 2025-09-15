from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

User = get_user_model()


class Category(models.Model):
    """Product category model."""
    
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Category Name'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Category Slug'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name=_('Category Image'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:category_detail', kwargs={'slug': self.slug})


class ProductImage(models.Model):
    """Model for multiple product images."""
    
    IMAGE_TYPE_CHOICES = [
        ('main', _('Main Image')),
        ('front', _('Front View')),
        ('back', _('Back View')),
        ('side', _('Side View')),
        ('top', _('Top View')),
        ('bottom', _('Bottom View')),
        ('detail', _('Detail View')),
        ('reference', _('Reference/Serial')),
        ('package', _('Package')),
        ('accessories', _('Accessories')),
    ]
    
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images', verbose_name=_('Product'))
    image = models.ImageField(upload_to='products/gallery/', verbose_name=_('Image'))
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES, default='detail', verbose_name=_('Image Type'))
    alt_text = models.CharField(max_length=200, blank=True, verbose_name=_('Alt Text'))
    caption = models.CharField(max_length=300, blank=True, verbose_name=_('Caption'))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('Sort Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.get_image_type_display()}"


class Product(models.Model):
    """Product model for IT materials."""
    
    CONDITION_CHOICES = [
        ('new', _('New')),
        ('refurbished', _('Refurbished')),
        ('used', _('Used')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_('Product Name'))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_('Product Slug'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name=_('Category'))
    description = models.TextField(verbose_name=_('Description'))
    short_description = models.CharField(max_length=300, blank=True, verbose_name=_('Short Description'))
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Sale Price'))
    
    # Inventory
    sku = models.CharField(max_length=50, unique=True, verbose_name=_('SKU'))
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name=_('Stock Quantity'))
    min_stock_level = models.PositiveIntegerField(default=5, verbose_name=_('Minimum Stock Level'))
    
    # Product details
    brand = models.CharField(max_length=100, blank=True, verbose_name=_('Brand'))
    model = models.CharField(max_length=100, blank=True, verbose_name=_('Model'))
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new', verbose_name=_('Condition'))
    warranty_months = models.PositiveIntegerField(default=12, verbose_name=_('Warranty (Months)'))
    
    # Images
    main_image = models.ImageField(upload_to='products/', verbose_name=_('Main Image'))
    additional_images = models.JSONField(default=list, blank=True, verbose_name=_('Additional Images'))
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Featured Product'))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['stock_quantity']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Generate slug automatically if empty."""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:product_detail', kwargs={'slug': self.slug})
    
    @property
    def current_price(self):
        """Return the current price (sale price if available, otherwise regular price)."""
        return self.sale_price if self.sale_price else self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale."""
        if self.sale_price and self.price > self.sale_price:
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0
    
    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        """Check if product stock is low."""
        return self.stock_quantity <= self.min_stock_level
    
    def get_gallery_images(self):
        """Get all active gallery images for this product, prioritizing realistic images."""
        # Prioriser les images réalistes, puis les autres
        realistic_images = self.images.filter(image_type='realistic', is_active=True).order_by('created_at')
        other_images = self.images.filter(is_active=True).exclude(image_type='realistic').order_by('sort_order', 'created_at')
        
        # Combiner en mettant les images réalistes en premier
        from django.db.models import QuerySet
        combined = QuerySet(model=self.images.model)
        combined._result_cache = list(realistic_images) + list(other_images)
        return combined
    
    def get_main_gallery_image(self):
        """Get the main gallery image or fallback to main_image."""
        main_gallery = self.images.filter(image_type='main', is_active=True).first()
        return main_gallery.image if main_gallery else self.main_image
    
    def reduce_stock(self, quantity):
        """Reduce stock quantity."""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
            return True
        return False
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews."""
        from django.db.models import Avg
        avg_rating = self.reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        return round(avg_rating, 1) if avg_rating else 0
    
    @property
    def total_reviews(self):
        """Get total number of approved reviews."""
        return self.reviews.filter(is_approved=True).count()
    
    @property
    def rating_distribution(self):
        """Get rating distribution for the product."""
        from django.db.models import Count
        distribution = {}
        for rating in range(1, 6):
            count = self.reviews.filter(is_approved=True, rating=rating).count()
            distribution[rating] = count
        return distribution
    
    def get_recommended_products(self, limit=4):
        """Get recommended products based on category and ratings."""
        from django.db.models import Q, Avg
        
        # Get products from the same category with good ratings
        recommended = Product.objects.filter(
            category=self.category,
            is_active=True
        ).exclude(id=self.id).annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(
            avg_rating__gte=3.0  # Only recommend products with 3+ star average
        ).order_by('-avg_rating', '-created_at')[:limit]
        
        # If not enough products in same category, add popular products
        if recommended.count() < limit:
            popular_products = Product.objects.filter(
                is_active=True,
                is_featured=True
            ).exclude(
                Q(id=self.id) | Q(id__in=[p.id for p in recommended])
            ).annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating', '-created_at')[:limit - recommended.count()]
            
            recommended = list(recommended) + list(popular_products)
        
        return recommended[:limit]
    
    def get_related_products(self, limit=4):
        """Get related products based on category and brand."""
        related = Product.objects.filter(
            is_active=True
        ).exclude(id=self.id)
        
        # First try same category and brand
        if self.brand:
            same_brand = related.filter(
                category=self.category,
                brand=self.brand
            )[:limit]
            if same_brand.exists():
                return same_brand
        
        # Then try same category
        same_category = related.filter(category=self.category)[:limit]
        if same_category.exists():
            return same_category
        
        # Finally, return featured products
        return related.filter(is_featured=True)[:limit]
    
    def get_customers_also_bought(self, limit=4):
        """Get products that customers who bought this also bought."""
        from django.db.models import Count, Avg
        
        # Get products that were bought together with this product
        # This is a simplified version - in a real app you'd analyze order patterns
        also_bought = Product.objects.filter(
            is_active=True
        ).exclude(id=self.id).annotate(
            purchase_count=Count('orderitem'),
            avg_rating=Avg('reviews__rating')
        ).filter(
            purchase_count__gt=0
        ).order_by('-purchase_count', '-avg_rating')[:limit]
        
        return also_bought


class Order(models.Model):
    """Order model for customer purchases."""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, verbose_name=_('Order Number'))
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_('Customer'))
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Order Status'))
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name=_('Payment Status'))
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Subtotal'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Tax Amount'))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Shipping Cost'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Amount'))
    
    # Shipping information
    shipping_address = models.TextField(verbose_name=_('Shipping Address'))
    shipping_city = models.CharField(max_length=100, verbose_name=_('Shipping City'))
    shipping_state = models.CharField(max_length=100, verbose_name=_('Shipping State'))
    shipping_zip_code = models.CharField(max_length=20, verbose_name=_('Shipping ZIP Code'))
    shipping_country = models.CharField(max_length=100, verbose_name=_('Shipping Country'))
    
    # Contact information
    contact_phone = models.CharField(max_length=20, verbose_name=_('Contact Phone'))
    contact_email = models.EmailField(verbose_name=_('Contact Email'))
    
    # Notes
    customer_notes = models.TextField(blank=True, verbose_name=_('Customer Notes'))
    staff_notes = models.TextField(blank=True, verbose_name=_('Staff Notes'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Paid At'))
    shipped_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Shipped At'))
    delivered_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Delivered At'))
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer.email}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:order_detail', kwargs={'pk': self.pk})
    
    def calculate_total(self):
        """Calculate total amount including tax and shipping."""
        total = self.subtotal + self.tax_amount + self.shipping_cost
        self.total_amount = total
        self.save()
        return total
    
    def get_status_display_class(self):
        """Get Bootstrap class for status display."""
        status_classes = {
            'pending': 'warning',
            'confirmed': 'info',
            'processing': 'primary',
            'shipped': 'info',
            'delivered': 'success',
            'cancelled': 'danger',
            'refunded': 'secondary',
        }
        return status_classes.get(self.status, 'secondary')


class OrderItem(models.Model):
    """Individual items within an order."""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_('Order'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'))
    
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Unit Price'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Price'))
    
    # Product snapshot at time of order
    product_name = models.CharField(max_length=200, verbose_name=_('Product Name'))
    product_sku = models.CharField(max_length=50, verbose_name=_('Product SKU'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} in Order {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        """Calculate total price before saving."""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Cart(models.Model):
    """Shopping cart for users."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart', verbose_name=_('User'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Shopping Cart')
        verbose_name_plural = _('Shopping Carts')
    
    def __str__(self):
        return f"Cart for {self.user.email}"
    
    @property
    def total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Calculate total price of all items in cart."""
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Individual items in shopping cart."""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name=_('Cart'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantity'))
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.cart}"
    
    @property
    def total_price(self):
        """Calculate total price for this item."""
        return self.quantity * self.product.current_price


class Payment(models.Model):
    """Payment model for order transactions."""
    
    PAYMENT_METHOD_CHOICES = [
        # Cartes bancaires
        ('credit_card', _('Credit Card')),
        ('debit_card', _('Debit Card')),
        ('visa', _('Visa')),
        ('mastercard', _('Mastercard')),
        
        # Paiements numériques
        ('paypal', _('PayPal')),
        ('apple_pay', _('Apple Pay')),
        ('google_pay', _('Google Pay')),
        
        # Paiement à la livraison
        ('cash_delivery', _('Cash on Delivery')),
        
        # Services de paiement marocains
        ('wafacash', _('WafaCash')),
        ('cashplus', _('CashPlus')),
        ('baridbanque', _('Barid Bank')),
        
        # Virements bancaires
        ('bank_transfer', _('Bank Transfer')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name=_('Order'))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name=_('Payment Method'))
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name=_('Transaction ID'))
    
    # Card details (for card payments) - should be encrypted in production
    card_last_four = models.CharField(max_length=4, blank=True, verbose_name=_('Card Last 4 Digits'))
    card_brand = models.CharField(max_length=20, blank=True, verbose_name=_('Card Brand'))
    
    # Payment processor details
    processor_response = models.JSONField(default=dict, blank=True, verbose_name=_('Processor Response'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Processed At'))
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.id} - {self.order.order_number} - {self.get_payment_method_display()}"
    
    def get_status_display_class(self):
        """Get Bootstrap class for status display."""
        status_classes = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger',
            'refunded': 'secondary',
        }
        return status_classes.get(self.status, 'secondary')


class Wishlist(models.Model):
    """Wishlist model for users to save favorite products."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist', verbose_name=_('User'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'))
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Added At'))
    
    class Meta:
        verbose_name = _('Wishlist Item')
        verbose_name_plural = _('Wishlist Items')
        unique_together = ['user', 'product']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"


class ProductReview(models.Model):
    """Product review and rating model."""
    
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('Product'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('User'))
    
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, verbose_name=_('Rating'))
    title = models.CharField(max_length=200, verbose_name=_('Review Title'))
    comment = models.TextField(verbose_name=_('Review Comment'))
    
    # Review status
    is_approved = models.BooleanField(default=True, verbose_name=_('Approved'))
    is_verified_purchase = models.BooleanField(default=False, verbose_name=_('Verified Purchase'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Product Review')
        verbose_name_plural = _('Product Reviews')
        unique_together = ['product', 'user']  # One review per user per product
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name} - {self.rating} stars"
    
    @property
    def rating_display(self):
        """Return rating as stars display."""
        return '★' * self.rating + '☆' * (5 - self.rating)