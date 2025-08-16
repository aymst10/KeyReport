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
    
    def reduce_stock(self, quantity):
        """Reduce stock quantity."""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
            return True
        return False


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
