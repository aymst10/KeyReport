from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random
from decimal import Decimal

from store.models import Product, Order, OrderItem, Wishlist, Payment
from users.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Add sample orders and wishlist items for staff, admin, and client users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--orders-per-user',
            type=int,
            default=3,
            help='Number of orders to create per user (default: 3)'
        )
        parser.add_argument(
            '--wishlist-items-per-user',
            type=int,
            default=5,
            help='Number of wishlist items to create per user (default: 5)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to add sample orders and wishlist items...'))
        
        # Get all users
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return
        
        # Get all products
        products = Product.objects.filter(is_active=True)
        if not products.exists():
            self.stdout.write(self.style.ERROR('No active products found. Please add products first.'))
            return
        
        orders_per_user = options['orders_per_user']
        wishlist_items_per_user = options['wishlist_items_per_user']
        
        # Create orders for each user
        self.create_orders_for_users(users, products, orders_per_user)
        
        # Create wishlist items for each user
        self.create_wishlist_items_for_users(users, products, wishlist_items_per_user)
        
        self.stdout.write(self.style.SUCCESS('Successfully added sample orders and wishlist items!'))

    def create_orders_for_users(self, users, products, orders_per_user):
        """Create sample orders for all users"""
        self.stdout.write('Creating sample orders...')
        
        order_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        payment_methods = ['credit_card', 'bank_transfer', 'paypal', 'cash_on_delivery']
        
        for user in users:
            # Create orders for this user
            for i in range(orders_per_user):
                # Random date within the last 6 months
                days_ago = random.randint(1, 180)
                order_date = timezone.now() - timedelta(days=days_ago)
                
                # Create order
                order = Order.objects.create(
                    order_number=f"ORD-{random.randint(100000, 999999)}",
                    customer=user,
                    status=random.choice(order_statuses),
                    subtotal=Decimal('0.00'),
                    total_amount=Decimal('0.00'),
                    shipping_address=f"{random.choice(['123', '456', '789'])} {random.choice(['Main St', 'Oak Ave', 'Pine Rd'])}",
                    shipping_city=random.choice(['Casablanca', 'Rabat', 'Marrakech', 'Fez', 'Tangier']),
                    shipping_state=random.choice(['Casablanca-Settat', 'Rabat-Salé-Kénitra', 'Marrakech-Safi', 'Fès-Meknès', 'Tanger-Tétouan-Al Hoceïma']),
                    shipping_zip_code=f"{random.randint(10000, 99999)}",
                    shipping_country='Morocco',
                    contact_phone=f"+212-{random.randint(600000000, 699999999)}",
                    contact_email=user.email,
                    customer_notes=f"Sample order #{i+1} for {user.email}",
                    created_at=order_date,
                    updated_at=order_date
                )
                
                # Add random products to order
                num_items = random.randint(1, 4)
                selected_products = random.sample(list(products), min(num_items, len(products)))
                
                total_amount = Decimal('0.00')
                for product in selected_products:
                    quantity = random.randint(1, 3)
                    price = product.sale_price if product.sale_price else product.price
                    item_total = price * quantity
                    total_amount += item_total
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=price,
                        total_price=item_total,
                        product_name=product.name,
                        product_sku=product.sku
                    )
                
                # Update order totals
                order.subtotal = total_amount
                order.total_amount = total_amount
                order.save()
                
                # Create payment for the order (if not cancelled)
                if order.status != 'cancelled':
                    payment_status = 'completed' if order.status in ['shipped', 'delivered'] else 'pending'
                    Payment.objects.create(
                        order=order,
                        amount=total_amount,
                        payment_method=random.choice(payment_methods),
                        status=payment_status,
                        transaction_id=f"TXN-{order.id}-{random.randint(1000, 9999)}",
                        created_at=order_date
                    )
                
                self.stdout.write(f'  Created order {order.id} for {user.email} with {len(selected_products)} items')
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(users) * orders_per_user} orders'))

    def create_wishlist_items_for_users(self, users, products, wishlist_items_per_user):
        """Create sample wishlist items for all users"""
        self.stdout.write('Creating sample wishlist items...')
        
        for user in users:
            # Get products not already in user's wishlist
            existing_wishlist_products = Wishlist.objects.filter(user=user).values_list('product_id', flat=True)
            available_products = products.exclude(id__in=existing_wishlist_products)
            
            if not available_products.exists():
                self.stdout.write(f'  No available products for {user.email} wishlist')
                continue
            
            # Select random products for wishlist
            num_items = min(wishlist_items_per_user, len(available_products))
            selected_products = random.sample(list(available_products), num_items)
            
            for product in selected_products:
                # Random date within the last 3 months
                days_ago = random.randint(1, 90)
                added_date = timezone.now() - timedelta(days=days_ago)
                
                Wishlist.objects.create(
                    user=user,
                    product=product,
                    added_at=added_date
                )
            
            self.stdout.write(f'  Added {len(selected_products)} items to {user.email} wishlist')
        
        self.stdout.write(self.style.SUCCESS(f'Created wishlist items for {len(users)} users'))

    def get_user_type(self, user):
        """Determine user type based on custom user model"""
        return user.user_type
