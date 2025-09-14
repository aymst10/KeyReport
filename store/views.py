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
from users.models import CustomUser

# Import professional payment views
from .professional_payment_views import (
    professional_payment,
    process_professional_payment,
    payment_success_professional,
    payment_failed_professional
)
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
    products = Product.objects.filter(category=category, is_active=True).order_by('-created_at')
    
    # Temporarily disable pagination for debugging
    # paginator = Paginator(products, 12)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': products,
        'page_obj': products,  # Use products directly for debugging
    }
    return render(request, 'store/category_detail.html', context)



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



def remove_cart_item(request, item_id):
    """Remove item from cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('store:cart')



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



def order_list(request):
    """List user's orders."""
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'store/order_list.html', context)



def order_detail(request, pk):
    """Order detail view."""
    order = get_object_or_404(Order, pk=pk, customer=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'store/order_detail.html', context)



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



def wishlist_view(request):
    """User's wishlist view."""
    wishlist_items = Wishlist.objects.filter(user=request.user).order_by('-added_at')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'store/wishlist.html', context)



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
            
            # Redirection selon le mode de paiement
            if payment_method in ['wafacash', 'cashplus', 'barid_bank']:
                return redirect('store:payment_details', order_id=order.id, payment_method=payment_method)
            elif payment_method == 'cash_on_delivery':
                return redirect('store:cash_payment_receipt', order_id=order.id)
            else:
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



def payment_success(request, payment_id):
    """Payment success view."""
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'store/payment_success.html', context)



def payment_failed(request, payment_id):
    """Payment failed view."""
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'store/payment_failed.html', context)



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


def contact(request):
    """Contact page view"""
    # Get company contact information
    company_contact = CustomUser.objects.filter(
        email='contact@keyreport.ma'
        ).first()
        
    # If company contact doesn't exist, create default info
    if not company_contact:
        contact_info = {
            'email': 'contact@keyreport.ma',
            'phone': '+212 5XX XXX XXX',
            'address': '123 Avenue Mohammed V, Casablanca 20000, Morocco',
            'company': 'KeyReport IT Solutions'
        }
    else:
        contact_info = {
            'email': company_contact.email,
            'phone': company_contact.phone or '+212 5XX XXX XXX',
            'address': company_contact.address or '123 Avenue Mohammed V, Casablanca 20000, Morocco',
            'company': company_contact.company or 'KeyReport IT Solutions'
        }
    
    context = {
        'contact_info': contact_info
    }
    
    return render(request, 'store/contact.html', context)

def payment_details(request, order_id, payment_method):
    """Payment details page for mobile payment services (WafaCash, CashPlus, Barid Bank)."""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status != 'pending':
        messages.error(request, 'Cette commande ne peut pas être payée.')
        return redirect('store:order_detail', order_id=order.id)
    
    # Définir les numéros de compte selon le service
    payment_accounts = {
        'wafacash': {
            'name': 'WafaCash',
            'account_number': '0651234567',
            'account_name': 'Key Reports Analytics',
            'instructions': [
                '1. Ouvrez l\'application WafaCash sur votre téléphone',
                '2. Sélectionnez "Envoyer de l\'argent"',
                '3. Entrez le numéro de compte ci-dessus',
                '4. Entrez le montant exact à payer',
                '5. Ajoutez le numéro de commande dans les détails',
                '6. Confirmez le paiement'
            ]
        },
        'cashplus': {
            'name': 'CashPlus',
            'account_number': '0701234567',
            'account_name': 'Key Reports Analytics',
            'instructions': [
                '1. Ouvrez l\'application CashPlus',
                '2. Cliquez sur "Paiement"',
                '3. Entrez le numéro de compte ci-dessus',
                '4. Entrez le montant exact à payer',
                '5. Mentionnez votre numéro de commande',
                '6. Effectuez le paiement'
            ]
        },
        'barid_bank': {
            'name': 'Barid Bank',
            'account_number': '001234567890',
            'account_name': 'Key Reports Analytics',
            'instructions': [
                '1. Connectez-vous à votre compte Barid Bank',
                '2. Allez dans "Virements"',
                '3. Entrez le numéro de compte ci-dessus',
                '4. Entrez le montant exact à payer',
                '5. Ajoutez votre numéro de commande en référence',
                '6. Validez le virement'
            ]
        }
    }
    
    account_info = payment_accounts.get(payment_method)
    if not account_info:
        messages.error(request, 'Méthode de paiement non valide.')
        return redirect('store:payment_method_selection_order', order_id=order.id)
    
    # Créer un paiement en attente
    payment, created = Payment.objects.get_or_create(
        order=order,
        payment_method=payment_method,
        defaults={
            'amount': order.total_amount,
            'status': 'pending'
        }
    )
    
    context = {
        'order': order,
        'payment': payment,
        'account_info': account_info,
        'payment_method': payment_method,
    }
    return render(request, 'store/payment_details.html', context)


def cash_payment_receipt(request, order_id):
    """Cash payment receipt page with order code for delivery."""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status != 'pending':
        messages.error(request, 'Cette commande ne peut pas être payée.')
        return redirect('store:order_detail', order_id=order.id)
    
    # Créer un paiement en attente pour le paiement à la livraison
    payment, created = Payment.objects.get_or_create(
        order=order,
        payment_method='cash_on_delivery',
        defaults={
            'amount': order.total_amount,
            'status': 'pending'
        }
    )
    
    # Générer un code de commande unique pour la livraison
    if not hasattr(order, 'delivery_code'):
        import random
        order.delivery_code = f"DEL-{random.randint(100000, 999999)}"
        order.save()
    
    context = {
        'order': order,
        'payment': payment,
        'delivery_code': order.delivery_code,
    }
    return render(request, 'store/cash_payment_receipt.html', context)


def categories(request):
    """Categories page view."""
    categories = Category.objects.filter(is_active=True).prefetch_related('products')
    context = {
        'categories': categories,
    }
    return render(request, 'store/categories.html', context)
