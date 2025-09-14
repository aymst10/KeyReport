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

from .models import Category, Product, Order, OrderItem, Cart, CartItem, Payment, Wishlist, ProductReview
from .forms import ProductForm, CategoryForm, ProductReviewForm, PaymentMethodForm, CardPaymentForm, BankTransferForm, PayPalForm, PaymentConfirmationForm
from .admin_views import admin_dashboard
from .payment_gateway import PaymentService


def contact_demo(request):
    """Demo page showing contact interactions"""
    return render(request, 'store/contact_demo.html')


def home(request):
    """Home page view."""
    from django.db.models import Avg, Count
    
    # Get featured products with ratings
    featured_products = Product.objects.filter(
        is_featured=True, 
        is_active=True
    ).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating', '-created_at')[:6]
    
    # Get top-rated products
    top_rated_products = Product.objects.filter(
        is_active=True
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(
        avg_rating__gte=4.0
    ).order_by('-avg_rating', '-review_count')[:4]
    
    # Get user-specific recommendations if logged in
    user_recommendations = []
    if request.user.is_authenticated:
        # Get products from categories the user has purchased
        user_orders = Order.objects.filter(customer=request.user)
        purchased_categories = set()
        for order in user_orders:
            for item in order.items.all():
                purchased_categories.add(item.product.category)
        
        if purchased_categories:
            user_recommendations = Product.objects.filter(
                category__in=purchased_categories,
                is_active=True
            ).annotate(
                avg_rating=Avg('reviews__rating')
            ).filter(
                avg_rating__gte=3.5
            ).exclude(
                id__in=[item.product.id for order in user_orders for item in order.items.all()]
            ).order_by('-avg_rating')[:4]
    
    categories = Category.objects.filter(is_active=True)[:8]
    
    context = {
        'featured_products': featured_products,
        'top_rated_products': top_rated_products,
        'user_recommendations': user_recommendations,
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
    
    # Get recommended and related products using the new methods
    recommended_products = product.get_recommended_products(limit=4)
    related_products = product.get_related_products(limit=4)
    customers_also_bought = product.get_customers_also_bought(limit=4)
    
    # Get approved reviews
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')[:10]
    
    # Check if user has already reviewed this product
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = product.reviews.get(user=request.user)
        except ProductReview.DoesNotExist:
            pass
    
    # Review form
    review_form = None
    if request.user.is_authenticated and not user_review:
        review_form = ProductReviewForm()
    
    # Prepare rating distribution for template
    rating_distribution = product.rating_distribution
    rating_distribution_list = []
    for rating in range(5, 0, -1):  # 5 to 1
        rating_distribution_list.append({
            'rating': rating,
            'count': rating_distribution.get(rating, 0)
        })
    
    context = {
        'product': product,
        'recommended_products': recommended_products,
        'related_products': related_products,
        'customers_also_bought': customers_also_bought,
        'reviews': reviews,
        'user_review': user_review,
        'review_form': review_form,
        'rating_distribution_list': rating_distribution_list,
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
def payment_method_selection(request, order_id=None):
    """Payment method selection view."""
    # Si pas d'order_id, utiliser le panier actuel
    if order_id:
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        if order.status != 'pending':
            messages.error(request, 'Cette commande ne peut pas être payée.')
            return redirect('store:order_detail', order_id=order.id)
        
        cart_items = order.items.all()
        cart_total = order.total_amount
    else:
        # Utiliser le panier actuel
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()
        cart_total = cart.total_price
        order = None
    
    if not cart_items.exists():
        messages.error(request, 'Votre panier est vide.')
        return redirect('store:cart')
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            
            # Si pas de commande, créer une commande depuis le panier
            if not order:
                # Générer un numéro de commande unique
                import uuid
                order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
                
                order = Order.objects.create(
                    order_number=order_number,
                    customer=request.user,
                    status='pending',
                    subtotal=cart_total,
                    total_amount=cart_total,
                    shipping_address="À définir",
                    shipping_city="À définir",
                    shipping_state="À définir",
                    shipping_zip_code="00000",
                    shipping_country="Maroc"
                )
                
                # Créer les OrderItems
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product.current_price,
                        total_price=cart_item.quantity * cart_item.product.current_price,
                        product_name=cart_item.product.name,
                        product_sku=cart_item.product.sku or "N/A"
                    )
                
                # Vider le panier
                cart.items.all().delete()
            
            return redirect('store:payment_process', order_id=order.id, payment_method=payment_method)
    else:
        form = PaymentMethodForm()
    
    context = {
        'order': order,
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'store/payment_method_selection.html', context)


@login_required
def payment_process(request, order_id, payment_method):
    """Payment processing view."""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status != 'pending':
        messages.error(request, 'This order cannot be paid for.')
        return redirect('store:order_detail', order_id=order.id)
    
    # Get payment method details
    payment_methods = PaymentService.get_payment_methods()
    method_details = payment_methods.get(payment_method)
    
    if not method_details:
        messages.error(request, 'Invalid payment method.')
        return redirect('store:payment_method_selection_order', order_id=order.id)
    
    # Initialize forms based on payment method
    card_form = None
    bank_form = None
    paypal_form = None
    confirmation_form = PaymentConfirmationForm()
    
    if payment_method in ['credit_card', 'debit_card', 'visa', 'mastercard', 'stripe', 'apple_pay', 'google_pay']:
        card_form = CardPaymentForm()
    elif payment_method in ['bank_transfer', 'cih_bank', 'attijariwafa', 'bmce']:
        bank_form = BankTransferForm()
    elif payment_method == 'paypal':
        paypal_form = PayPalForm()
    
    if request.method == 'POST':
        # Process the payment
        if payment_method == 'cash':
            # Cash on delivery - no additional form needed
            confirmation_form = PaymentConfirmationForm(request.POST)
            if confirmation_form.is_valid():
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='pending'
                )
                
                # Process payment
                result = PaymentService.process_payment(payment)
                
                if result['success']:
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, result['message'])
                    return redirect('store:payment_success', payment_id=payment.id)
                else:
                    messages.error(request, result['message'])
        
        elif payment_method in ['credit_card', 'debit_card', 'visa', 'mastercard', 'stripe', 'apple_pay', 'google_pay']:
            card_form = CardPaymentForm(request.POST)
            confirmation_form = PaymentConfirmationForm(request.POST)
            
            if card_form.is_valid() and confirmation_form.is_valid():
                # Extract month and year from expiry_date (MM/AA format)
                expiry_date = card_form.cleaned_data['expiry_date']
                expiry_month = expiry_date[:2]
                expiry_year = '20' + expiry_date[3:]
                
                # Prepare card details with separate month and year
                card_details = card_form.cleaned_data.copy()
                card_details['expiry_month'] = expiry_month
                card_details['expiry_year'] = expiry_year
                
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='processing',
                    card_last_four=card_form.cleaned_data['card_number'][-4:],
                    card_brand=payment_method
                )
                
                # Process payment
                result = PaymentService.process_payment(
                    payment, 
                    payment_method_id=f"pm_{payment.id}",
                    card_details=card_details
                )
                
                if result['success']:
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, result['message'])
                    return redirect('store:payment_success', payment_id=payment.id)
                else:
                    messages.error(request, result['message'])
        
        elif payment_method in ['bank_transfer', 'cih_bank', 'attijariwafa', 'bmce']:
            bank_form = BankTransferForm(request.POST)
            confirmation_form = PaymentConfirmationForm(request.POST)
            
            if bank_form.is_valid() and confirmation_form.is_valid():
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='processing'
                )
                
                # Process payment
                result = PaymentService.process_payment(
                    payment,
                    bank_details=bank_form.cleaned_data
                )
                
                if result['success']:
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, result['message'])
                    return redirect('store:payment_success', payment_id=payment.id)
                else:
                    messages.error(request, result['message'])
        
        elif payment_method == 'paypal':
            paypal_form = PayPalForm(request.POST)
            confirmation_form = PaymentConfirmationForm(request.POST)
            
            if paypal_form.is_valid() and confirmation_form.is_valid():
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='processing'
                )
                
                # Process payment
                result = PaymentService.process_payment(
                    payment,
                    paypal_email=paypal_form.cleaned_data['paypal_email']
                )
                
                if result['success']:
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, result['message'])
                    return redirect('store:payment_success', payment_id=payment.id)
                else:
                    messages.error(request, result['message'])
    
    context = {
        'order': order,
        'payment_method': payment_method,
        'method_details': method_details,
        'card_form': card_form,
        'bank_form': bank_form,
        'paypal_form': paypal_form,
        'confirmation_form': confirmation_form,
    }
    return render(request, 'store/payment_process.html', context)


@login_required
def payment_success(request, payment_id):
    """Payment success view."""
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'store/payment_success.html', context)


@login_required
def payment_failed(request, payment_id):
    """Payment failed view."""
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'store/payment_failed.html', context)


@login_required
@require_POST
def refund_payment(request, payment_id):
    """Refund a payment."""
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    if payment.status not in ['completed']:
        return JsonResponse({'success': False, 'error': 'Payment cannot be refunded'})
    
    try:
        result = PaymentService.refund_payment(payment)
        
        if result['success']:
            payment.order.status = 'refunded'
            payment.order.save()
            return JsonResponse({
                'success': True,
                'message': result['message']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['message']
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def cart_view(request):
    """Shopping cart view."""
    try:
        cart = Cart.objects.get(user=request.user)
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


@login_required
@require_POST
def toggle_wishlist(request):
    """Toggle product in user's wishlist."""
    import json
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        if not product_id:
            return JsonResponse({'success': False, 'error': 'Product ID required'})
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check if product is already in wishlist
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            # Added to wishlist
            return JsonResponse({
                'success': True,
                'added': True,
                'message': f'{product.name} added to wishlist'
            })
        else:
            # Remove from wishlist
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'added': False,
                'message': f'{product.name} removed from wishlist'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def wishlist_view(request):
    """User's wishlist view."""
    wishlist_items = Wishlist.objects.filter(user=request.user).order_by('-added_at')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'store/wishlist.html', context)


@login_required
def submit_review(request, product_id):
    """Submit a product review."""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check if user has already reviewed this product
        existing_review = ProductReview.objects.filter(
            user=request.user,
            product=product
        ).first()
        
        if existing_review:
            messages.error(request, 'You have already reviewed this product.')
            return redirect('store:product_detail', slug=product.slug)
        
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            
            # Check if user has purchased this product (for verified purchase)
            has_purchased = OrderItem.objects.filter(
                order__customer=request.user,
                product=product
            ).exists()
            review.is_verified_purchase = has_purchased
            
            review.save()
            messages.success(request, 'Thank you for your review! It has been submitted for approval.')
        else:
            messages.error(request, 'Please correct the errors in your review.')
        
        return redirect('store:product_detail', slug=product.slug)
    
    return redirect('store:product_list')


@login_required
def payment_method_selection(request, order_id=None):
    """Payment method selection view."""
    # Si pas d'order_id, utiliser le panier actuel
    if order_id:
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        if order.status != 'pending':
            messages.error(request, 'Cette commande ne peut pas être payée.')
            return redirect('store:order_detail', order_id=order.id)
        
        cart_items = order.items.all()
        cart_total = order.total_amount
    else:
        # Utiliser le panier actuel
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()
        cart_total = cart.total_price
        order = None
    
    if not cart_items.exists():
        messages.error(request, 'Votre panier est vide.')
        return redirect('store:cart')
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            
            # Si pas de commande, créer une commande depuis le panier
            if not order:
                # Générer un numéro de commande unique
                import uuid
                order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
                
                order = Order.objects.create(
                    order_number=order_number,
                    customer=request.user,
                    status='pending',
                    subtotal=cart_total,
                    total_amount=cart_total,
                    shipping_address="À définir",
                    shipping_city="À définir",
                    shipping_state="À définir",
                    shipping_zip_code="00000",
                    shipping_country="Maroc"
                )
                
                # Créer les OrderItems
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product.current_price,
                        total_price=cart_item.quantity * cart_item.product.current_price,
                        product_name=cart_item.product.name,
                        product_sku=cart_item.product.sku or "N/A"
                    )
                
                # Vider le panier
                cart.items.all().delete()
            
            return redirect('store:payment_process', order_id=order.id, payment_method=payment_method)
    else:
        form = PaymentMethodForm()
    
    context = {
        'order': order,
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'store/payment_method_selection.html', context)


@login_required
def payment_process(request, order_id, payment_method):
    """Payment processing view."""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status != 'pending':
        messages.error(request, 'This order cannot be paid for.')
        return redirect('store:order_detail', order_id=order.id)
    
    # Get payment method details
    payment_methods = PaymentService.get_payment_methods()
    method_details = payment_methods.get(payment_method)
    
    if not method_details:
        messages.error(request, 'Invalid payment method.')
        return redirect('store:payment_method_selection_order', order_id=order.id)
    
    # Initialize forms based on payment method
    card_form = None
    bank_form = None
    paypal_form = None
    confirmation_form = PaymentConfirmationForm()
    
    if payment_method in ['credit_card', 'debit_card', 'visa', 'mastercard', 'stripe', 'apple_pay', 'google_pay']:
        card_form = CardPaymentForm()
    elif payment_method in ['bank_transfer', 'cih_bank', 'attijariwafa', 'bmce']:
        bank_form = BankTransferForm()
    elif payment_method == 'paypal':
        paypal_form = PayPalForm()
    
    if request.method == 'POST':
        # Process the payment
        if payment_method == 'cash':
            # Cash on delivery - no additional form needed
            confirmation_form = PaymentConfirmationForm(request.POST)
            if confirmation_form.is_valid():
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='pending'
                )
                
                # Process payment
                result = PaymentService.process_payment(payment)
                
                if result['success']:
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, result['message'])
                    return redirect('store:payment_success', payment_id=payment.id)
                else:
                    messages.error(request, result['message'])
        
        elif payment_method in ['credit_card', 'debit_card', 'visa', 'mastercard', 'stripe', 'apple_pay', 'google_pay']:
            card_form = CardPaymentForm(request.POST)
            confirmation_form = PaymentConfirmationForm(request.POST)
            
            if card_form.is_valid() and confirmation_form.is_valid():
                # Extract month and year from expiry_date (MM/AA format)
                expiry_date = card_form.cleaned_data['expiry_date']
                expiry_month = expiry_date[:2]
                expiry_year = '20' + expiry_date[3:]
                
                # Prepare card details with separate month and year
                card_details = card_form.cleaned_data.copy()
                card_details['expiry_month'] = expiry_month
                card_details['expiry_year'] = expiry_year
                
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='processing',
                    card_last_four=card_form.cleaned_data['card_number'][-4:],
                    card_brand=payment_method
                )
                
                # Process payment
                result = PaymentService.process_payment(
                    payment, 
                    payment_method_id=f"pm_{payment.id}",
                    card_details=card_details
                )
                
                if result['success']:
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, result['message'])
                    return redirect('store:payment_success', payment_id=payment.id)
                else:
                    messages.error(request, result['message'])
        
        elif payment_method in ['bank_transfer', 'cih_bank', 'attijariwafa', 'bmce']:
            bank_form = BankTransferForm(request.POST)
            confirmation_form = PaymentConfirmationForm(request.POST)
            
            if bank_form.is_valid() and confirmation_form.is_valid():
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='processing'
                )
                
                # Process payment
                result = PaymentService.process_payment(
                    payment,
                    bank_details=bank_form.cleaned_data
                )
                
                if result['success']:
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, result['message'])
                    return redirect('store:payment_success', payment_id=payment.id)
                else:
                    messages.error(request, result['message'])
        
        elif payment_method == 'paypal':
            paypal_form = PayPalForm(request.POST)
            confirmation_form = PaymentConfirmationForm(request.POST)
            
            if paypal_form.is_valid() and confirmation_form.is_valid():
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='processing'
                )
                
                # Process payment
                result = PaymentService.process_payment(
                    payment,
                    paypal_email=paypal_form.cleaned_data['paypal_email']
                )
                
                if result['success']:
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, result['message'])
                    return redirect('store:payment_success', payment_id=payment.id)
                else:
                    messages.error(request, result['message'])
    
    context = {
        'order': order,
        'payment_method': payment_method,
        'method_details': method_details,
        'card_form': card_form,
        'bank_form': bank_form,
        'paypal_form': paypal_form,
        'confirmation_form': confirmation_form,
    }
    return render(request, 'store/payment_process.html', context)


@login_required
def payment_success(request, payment_id):
    """Payment success view."""
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'store/payment_success.html', context)


@login_required
def payment_failed(request, payment_id):
    """Payment failed view."""
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'store/payment_failed.html', context)


@login_required
@require_POST
def refund_payment(request, payment_id):
    """Refund a payment."""
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    if payment.status not in ['completed']:
        return JsonResponse({'success': False, 'error': 'Payment cannot be refunded'})
    
    try:
        result = PaymentService.refund_payment(payment)
        
        if result['success']:
            payment.order.status = 'refunded'
            payment.order.save()
            return JsonResponse({
                'success': True,
                'message': result['message']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['message']
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


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


@login_required
def checkout(request):
    """Checkout page with payment options."""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items:
            messages.warning(request, 'Your cart is empty.')
            return redirect('store:cart')
            
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:cart')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def process_payment(request):
    """Process payment for the order."""
    if request.method != 'POST':
        return redirect('store:checkout')
    
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items:
            messages.error(request, 'Your cart is empty.')
            return redirect('store:cart')
        
        # Get payment details from form
        payment_method = request.POST.get('payment_method')
        shipping_address = request.POST.get('shipping_address')
        shipping_city = request.POST.get('shipping_city')
        shipping_state = request.POST.get('shipping_state')
        shipping_zip = request.POST.get('shipping_zip')
        contact_phone = request.POST.get('contact_phone')
        contact_email = request.POST.get('contact_email')
        
        # Validate required fields
        if not all([payment_method, shipping_address, shipping_city, shipping_state, shipping_zip, contact_phone, contact_email]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('store:checkout')
        
        # Calculate totals
        subtotal = cart.total_price
        tax_amount = 0  # You can implement tax calculation here
        shipping_cost = 0  # Free shipping for now
        total_amount = subtotal + tax_amount + shipping_cost
        
        # Create order
        import uuid
        order = Order.objects.create(
            order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            customer=request.user,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_cost=shipping_cost,
            total_amount=total_amount,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_state=shipping_state,
            shipping_zip_code=shipping_zip,
            shipping_country='Morocco',  # Updated for Morocco
            contact_phone=contact_phone,
            contact_email=contact_email,
            status='pending'  # Changed to pending until payment is processed
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.current_price,
                total_price=cart_item.total_price,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku
            )
            
            # Reduce stock
            cart_item.product.reduce_stock(cart_item.quantity)
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, f'Order {order.order_number} created successfully! Please complete your payment.')
        return redirect('store:payment_method_selection_order', order_id=order.id)
        
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('store:cart')
    except Exception as e:
        messages.error(request, f'Payment processing failed: {str(e)}')
        return redirect('store:checkout')


@login_required 
def order_list(request):
    """List user's orders."""
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


@login_required
@require_POST
def toggle_wishlist(request):
    """Toggle product in user's wishlist."""
    import json
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        if not product_id:
            return JsonResponse({'success': False, 'error': 'Product ID required'})
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check if product is already in wishlist
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            # Added to wishlist
            return JsonResponse({
                'success': True,
                'added': True,
                'message': f'{product.name} added to wishlist'
            })
        else:
            # Remove from wishlist
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'added': False,
                'message': f'{product.name} removed from wishlist'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def wishlist_view(request):
    """User's wishlist view."""
    wishlist_items = Wishlist.objects.filter(user=request.user).order_by('-added_at')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'store/wishlist.html', context)


@login_required
def submit_review(request, product_id):
    """Submit a product review."""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check if user has already reviewed this product
        existing_review = ProductReview.objects.filter(
            user=request.user,
            product=product
        ).first()
        
        if existing_review:
            messages.error(request, 'You have already reviewed this product.')
            return redirect('store:product_detail', slug=product.slug)
        
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            
            # Check if user has purchased this product (for verified purchase)
            has_purchased = OrderItem.objects.filter(
                order__customer=request.user,
                product=product
            ).exists()
            review.is_verified_purchase = has_purchased
            
            review.save()
            messages.success(request, 'Thank you for your review! It has been submitted for approval.')
        else:
            messages.error(request, 'Please correct the errors in your review.')
        
        return redirect('store:product_detail', slug=product.slug)
    
    return redirect('store:product_list')


@login_required
def payment_method_selection(request, order_id=None):
    """Payment method selection view."""
    # Si pas d'order_id, utiliser le panier actuel
    if order_id:
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        if order.status != 'pending':
            messages.error(request, 'Cette commande ne peut pas être payée.')
            return redirect('store:order_detail', order_id=order.id)
        
        cart_items = order.items.all()
        cart_total = order.total_amount
    else:
        # Utiliser le panier actuel
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()
        cart_total = cart.total_price
        order = None
    
    if not cart_items.exists():
        messages.error(request, 'Votre panier est vide.')
        return redirect('store:cart')
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            
            # Si pas de commande, créer une commande depuis le panier
            if not order:
                # Générer un numéro de commande unique
                import uuid
                order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
                
                order = Order.objects.create(
                    order_number=order_number,
                    customer=request.user,
                    status='pending',
                    subtotal=cart_total,
                    total_amount=cart_total,
                    shipping_address="À définir",
                    shipping_city="À définir",
                    shipping_state="À définir",
                    shipping_zip_code="00000",
                    shipping_country="Maroc"
                )
                
                # Créer les OrderItems
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product.current_price,
                        total_price=cart_item.quantity * cart_item.product.current_price,
                        product_name=cart_item.product.name,
                        product_sku=cart_item.product.sku or "N/A"
                    )
                
                # Vider le panier
                cart.items.all().delete()
            
            return redirect('store:payment_process', order_id=order.id, payment_method=payment_method)
    else:
        form = PaymentMethodForm()
    
    context = {
        'order': order,
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'store/payment_method_selection.html', context)


@login_required
def payment_process(request, order_id, payment_method):
    """Payment processing view."""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status != 'pending':
        messages.error(request, 'This order cannot be paid for.')
        return redirect('store:order_detail', order_id=order.id)
    
    # Get payment method details
    payment_methods = PaymentService.get_payment_methods()
    method_details = payment_methods.get(payment_method)
    
    if not method_details:
        messages.error(request, 'Invalid payment method.')
        return redirect('store:payment_method_selection_order', order_id=order.id)
    
    # Initialize forms based on payment method
    card_form = None
    bank_form = None
    paypal_form = None
    confirmation_form = PaymentConfirmationForm()
    
    if payment_method in ['credit_card', 'debit_card', 'visa', 'mastercard', 'stripe', 'apple_pay', 'google_pay']:
        card_form = CardPaymentForm()
    elif payment_method in ['bank_transfer', 'cih_bank', 'attijariwafa', 'bmce']:
        bank_form = BankTransferForm()
    elif payment_method == 'paypal':
        paypal_form = PayPalForm()
    
    if request.method == 'POST':
        # Process the payment
        if payment_method == 'cash':
            # Cash on delivery - no additional form needed
            confirmation_form = PaymentConfirmationForm(request.POST)
            if confirmation_form.is_valid():
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='pending'
                )
                
                # Process payment
                result = PaymentService.process_payment(payment)
                
                if result['success']:
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, result['message'])
                    return redirect('store:payment_success', payment_id=payment.id)
                else:
                    messages.error(request, result['message'])
        
        elif payment_method in ['credit_card', 'debit_card', 'visa', 'mastercard', 'stripe', 'apple_pay', 'google_pay']:
            card_form = CardPaymentForm(request.POST)
            confirmation_form = PaymentConfirmationForm(request.POST)
            
            if card_form.is_valid() and confirmation_form.is_valid():
                # Extract month and year from expiry_date (MM/AA format)
                expiry_date = card_form.cleaned_data['expiry_date']
                expiry_month = expiry_date[:2]
                expiry_year = '20' + expiry_date[3:]
                
                # Prepare card details with separate month and year
                card_details = card_form.cleaned_data.copy()
                card_details['expiry_month'] = expiry_month
                card_details['expiry_year'] = expiry_year
                
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='processing',
                    card_last_four=card_form.cleaned_data['card_number'][-4:],
                    card_brand=payment_method
                )
                
                # Process payment
                result = PaymentService.process_payment(
                    payment, 
                    payment_method_id=f"pm_{payment.id}",
                    card_details=card_details
                )
                
                if result['success']:
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, result['message'])
                    return redirect('store:payment_success', payment_id=payment.id)
                else:
                    messages.error(request, result['message'])
        
        elif payment_method in ['bank_transfer', 'cih_bank', 'attijariwafa', 'bmce']:
            bank_form = BankTransferForm(request.POST)
            confirmation_form = PaymentConfirmationForm(request.POST)
            
            if bank_form.is_valid() and confirmation_form.is_valid():
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='processing'
                )
                
                # Process payment
                result = PaymentService.process_payment(
                    payment,
                    bank_details=bank_form.cleaned_data
                )
                
                if result['success']:
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, result['message'])
                    return redirect('store:payment_success', payment_id=payment.id)
                else:
                    messages.error(request, result['message'])
        
        elif payment_method == 'paypal':
            paypal_form = PayPalForm(request.POST)
            confirmation_form = PaymentConfirmationForm(request.POST)
            
            if paypal_form.is_valid() and confirmation_form.is_valid():
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='processing'
                )
                
                # Process payment
                result = PaymentService.process_payment(
                    payment,
                    paypal_email=paypal_form.cleaned_data['paypal_email']
                )
                
                if result['success']:
                    order.status = 'confirmed'
                    order.save()
                    messages.success(request, result['message'])
                    return redirect('store:payment_success', payment_id=payment.id)
                else:
                    messages.error(request, result['message'])
    
    context = {
        'order': order,
        'payment_method': payment_method,
        'method_details': method_details,
        'card_form': card_form,
        'bank_form': bank_form,
        'paypal_form': paypal_form,
        'confirmation_form': confirmation_form,
    }
    return render(request, 'store/payment_process.html', context)


@login_required
def payment_success(request, payment_id):
    """Payment success view."""
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'store/payment_success.html', context)


@login_required
def payment_failed(request, payment_id):
    """Payment failed view."""
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'store/payment_failed.html', context)


@login_required
@require_POST
def refund_payment(request, payment_id):
    """Refund a payment."""
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    if payment.status not in ['completed']:
        return JsonResponse({'success': False, 'error': 'Payment cannot be refunded'})
    
    try:
        result = PaymentService.refund_payment(payment)
        
        if result['success']:
            payment.order.status = 'refunded'
            payment.order.save()
            return JsonResponse({
                'success': True,
                'message': result['message']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['message']
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



def process_checkout(request):
    """Process checkout form submission."""
    if request.method == 'POST':
        # Get form data
        contact_name = request.POST.get('contact_name', '')
        contact_email = request.POST.get('contact_email', '')
        contact_phone = request.POST.get('contact_phone', '')
        shipping_address = request.POST.get('shipping_address', '')
        shipping_city = request.POST.get('shipping_city', '')
        shipping_state = request.POST.get('shipping_state', '')
        shipping_zip = request.POST.get('shipping_zip', '')
        payment_method = request.POST.get('payment_method', '')
        
        # Validate required fields
        if not all([contact_name, contact_email, contact_phone, shipping_address, shipping_city, shipping_state, payment_method]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return redirect('store:checkout')
        
        # Store order data in session
        order_data = {
            'customerName': contact_name,
            'customerEmail': contact_email,
            'customerPhone': contact_phone,
            'paymentMethod': payment_method,
            'subtotal': '159.00',
            'shipping': 'Gratuit',
            'taxes': '0.00',
            'total': '159.00',
            'deliveryAddress': f"{shipping_address}, {shipping_city}",
            'deliveryRegion': shipping_state,
            'deliveryTime': '1-2 jours ouvrables',
            'items': [
                {
                    'name': 'Carte Graphique NVIDIA RTX 4060',
                    'sku': 'RTX4060-8GB',
                    'quantity': 1,
                    'price': '159.00',
                    'total': '159.00'
                }
            ]
        }
        
        request.session['order_data'] = order_data
        
        # Redirect to payment confirmation first
        return redirect('store:payment_confirmation')
    
    return redirect('store:checkout')


def payment_confirmation(request):
    """Payment confirmation view."""
    # Get order data from session or request parameters
    order_data = request.session.get('order_data', {})
    
    # If no order data in session, create sample data for demo
    if not order_data:
        order_data = {
            'customerName': 'Yassine Mousta',
            'customerEmail': 'yassinomousta2004@gmail.com',
            'customerPhone': '+212 6 04 12 12 83',
            'paymentMethod': 'CIH Bank',
            'subtotal': '159.00',
            'shipping': 'Gratuit',
            'taxes': '0.00',
            'total': '159.00',
            'deliveryAddress': 'Mazola rue 6, Casablanca',
            'deliveryRegion': 'Casablanca-Settat',
            'deliveryTime': '1-2 jours ouvrables',
            'items': [
                {
                    'name': 'Carte Graphique NVIDIA RTX 4060',
                    'sku': 'RTX4060-8GB',
                    'quantity': 1,
                    'price': '159.00',
                    'total': '159.00'
                }
            ]
        }
    
    context = {
        'order_data': order_data,
    }
    return render(request, 'store/payment_confirmation.html', context)


def payment_receipt(request):
    """Payment receipt view."""
    # Get order data from session or request parameters
    order_data = request.session.get('order_data', {})
    
    # If no order data in session, create sample data for demo
    if not order_data:
        order_data = {
            'customerName': 'Yassine Mousta',
            'customerEmail': 'yassinomousta2004@gmail.com',
            'customerPhone': '+212 6 04 12 12 83',
            'paymentMethod': 'CIH Bank',
            'subtotal': '159.00',
            'shipping': 'Gratuit',
            'taxes': '0.00',
            'total': '159.00',
            'deliveryAddress': 'Mazola rue 6, Casablanca',
            'deliveryRegion': 'Casablanca-Settat',
            'deliveryTime': '1-2 jours ouvrables',
            'items': [
                {
                    'name': 'Carte Graphique NVIDIA RTX 4060',
                    'sku': 'RTX4060-8GB',
                    'quantity': 1,
                    'price': '159.00',
                    'total': '159.00'
                }
            ]
        }
    
    context = {
        'order_data': order_data,
    }
    return render(request, 'store/payment_receipt.html', context)
