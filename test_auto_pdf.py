#!/usr/bin/env python
"""
Test automatic PDF generation for different payment methods
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_store.settings')
django.setup()

from store.models import Order, OrderItem, Payment, Product, Category
from store.pdf_utils import generate_payment_receipt_response
from django.contrib.auth import get_user_model
from datetime import datetime
import uuid

User = get_user_model()

def create_test_payment(payment_method, status='completed'):
    """Create a test payment for testing"""
    # Get or create test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'customer'
        }
    )
    
    # Get or create test category
    category, created = Category.objects.get_or_create(
        name='Test Category',
        defaults={
            'description': 'Test category for PDF generation',
            'slug': 'test-category'
        }
    )
    
    # Get or create test product
    product, created = Product.objects.get_or_create(
        sku=f'TEST-PRODUCT-{payment_method.upper()}',
        defaults={
            'name': f'Test Product for {payment_method}',
            'description': f'Test product for {payment_method} payment',
            'price': 100.00,
            'stock_quantity': 10,
            'category': category,
            'slug': f'test-product-{payment_method}'
        }
    )
    
    # Create test order
    order = Order.objects.create(
        customer=user,
        order_number=f"TEST-{payment_method.upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        status='confirmed' if status == 'completed' else 'pending_payment',
        shipping_address='Test Address, Test City',
        contact_phone='+212 6 00 00 00 00',
        contact_email='test@example.com',
        subtotal=100.00,
        tax_amount=0.00,
        shipping_cost=0.00,
        total_amount=100.00
    )
    
    # Create test order item
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        unit_price=100.00,
        total_price=100.00
    )
    
    # Create test payment
    payment = Payment.objects.create(
        order=order,
        payment_method=payment_method,
        amount=100.00,
        status=status,
        processed_at=datetime.now()
    )
    
    return payment, order

def test_auto_pdf_generation():
    """Test automatic PDF generation for all payment methods"""
    print("🧪 Testing Automatic PDF Generation")
    print("=" * 50)
    
    payment_methods = [
        ('credit_card', 'completed'),
        ('paypal', 'completed'),
        ('cash_delivery', 'pending'),
        ('bank_transfer', 'pending')
    ]
    
    for method, status in payment_methods:
        print(f"\n📄 Testing {method.upper()} payment ({status})")
        
        try:
            # Create test payment
            payment, order = create_test_payment(method, status)
            
            # Generate PDF response
            response = generate_payment_receipt_response(payment, order)
            
            # Save to file for inspection
            filename = f"test_auto_receipt_{method}_{status}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"  ✅ PDF generated successfully!")
            print(f"  📄 File: {filename}")
            print(f"  📊 Size: {len(response.content)} bytes")
            print(f"  🏷️  Content-Type: {response['Content-Type']}")
            
            # Clean up test data
            payment.delete()
            order.delete()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ All tests completed!")

if __name__ == '__main__':
    test_auto_pdf_generation()
