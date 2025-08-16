from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
import time

from .models import Category, Product, Order, OrderItem, Cart, CartItem
from .forms import ProductForm, CategoryForm


def home(request):
    """Home page view."""
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:6]
    categories = Category.objects.filter(is_active=True)[:8]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    """Product listing view with filtering and search."""
    products = Product.objects.filter(is_active=True)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(model__icontains=query)
        )
    
    # Category filtering
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Price filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(current_price__gte=min_price)
    if max_price:
        products = products.filter(current_price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        products = products.order_by('current_price')
    elif sort_by == 'price_high':
        products = products.order_by('-current_price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'query': query,
        'category_slug': category_slug,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    """Product detail view."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


def category_detail(request, slug):
    """Category detail view."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
    }
    return render(request, 'store/category_detail.html', context)


@login_required
def add_to_cart(request, product_id):
    """Add product to cart."""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than 0.')
            return redirect('store:product_detail', slug=product.slug)
        
        if not product.is_in_stock:
            messages.error(request, 'Product is out of stock.')
            return redirect('store:product_detail', slug=product.slug)
        
        if quantity > product.stock_quantity:
            messages.error(request, f'Only {product.stock_quantity} items available in stock.')
            return redirect('store:product_detail', slug=product.slug)
        
        # Get or create cart for user
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if product already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart.')
        return redirect('store:cart')
    
    return redirect('store:product_list')


@login_required
def cart_view(request):
    """Shopping cart view."""
    try:
        cart = request.user.cart
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html', context)


@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity."""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
        elif quantity > cart_item.product.stock_quantity:
            messages.error(request, f'Only {cart_item.product.stock_quantity} items available in stock.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully.')
        
        return redirect('store:cart')
    
    return redirect('store:cart')


@login_required
def remove_cart_item(request, item_id):
    """Remove item from cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('store:cart')


@login_required
def checkout(request):
    """Checkout view."""
    try:
        cart = request.user.cart
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('store:cart')
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('store:cart')
    
    # Check stock availability
    for item in cart_items:
        if not item.product.is_in_stock:
            messages.error(request, f'{item.product.name} is out of stock.')
            return redirect('store:cart')
        if item.quantity > item.product.stock_quantity:
            messages.error(request, f'Only {item.product.stock_quantity} {item.product.name} available in stock.')
            return redirect('store:cart')
    
    if request.method == 'POST':
        # Process checkout
        # This is a simplified version - in a real app you'd integrate with payment gateway
        try:
            # Create order
            order = Order.objects.create(
                customer=request.user,
                order_number=f"ORD-{request.user.id}-{int(time.time())}",
                subtotal=cart.total_price,
                total_amount=cart.total_price,
                shipping_address=request.POST.get('shipping_address'),
                shipping_city=request.POST.get('shipping_city'),
                shipping_state=request.POST.get('shipping_state'),
                shipping_zip_code=request.POST.get('shipping_zip_code'),
                shipping_country=request.POST.get('shipping_country'),
                contact_phone=request.POST.get('contact_phone'),
                contact_email=request.POST.get('contact_email'),
                customer_notes=request.POST.get('customer_notes', ''),
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.current_price,
                    product_name=cart_item.product.name,
                    product_sku=cart_item.product.sku,
                )
                
                # Reduce stock
                cart_item.product.reduce_stock(cart_item.quantity)
            
            # Clear cart
            cart.delete()
            
            messages.success(request, f'Order {order.order_number} created successfully!')
            return redirect('store:order_detail', pk=order.pk)
            
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def order_list(request):
    """User's order list."""
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'store/order_list.html', context)


@login_required
def order_detail(request, pk):
    """Order detail view."""
    order = get_object_or_404(Order, pk=pk, customer=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'store/order_detail.html', context)


# Admin views for staff members
class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff access."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff_member()


@method_decorator(login_required, name='dispatch')
class ProductCreateView(StaffRequiredMixin, CreateView):
    """Create new product view."""
    
    model = Product
    form_class = ProductForm
    template_name = 'store/product_form.html'
    success_url = reverse_lazy('store:product_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ProductUpdateView(StaffRequiredMixin, UpdateView):
    """Update product view."""
    
    model = Product
    form_class = ProductForm
    template_name = 'store/product_form.html'
    success_url = reverse_lazy('store:product_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ProductDeleteView(StaffRequiredMixin, DeleteView):
    """Delete product view."""
    
    model = Product
    template_name = 'store/product_confirm_delete.html'
    success_url = reverse_lazy('store:product_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Product deleted successfully!')
        return super().delete(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class CategoryCreateView(StaffRequiredMixin, CreateView):
    """Create new category view."""
    
    model = Category
    form_class = CategoryForm
    template_name = 'store/category_form.html'
    success_url = reverse_lazy('store:product_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    """Update category view."""
    
    model = Category
    form_class = CategoryForm
    template_name = 'store/category_form.html'
    success_url = reverse_lazy('store:product_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    """Delete category view."""
    
    model = Category
    template_name = 'store/category_confirm_delete.html'
    success_url = reverse_lazy('store:product_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)
