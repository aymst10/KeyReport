from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models import Category, Product
from support.models import SupportTicket, ServiceRequest
import random
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up sample data for IT Store application'

    def handle(self, *args, **options):
        self.stdout.write('Setting up sample data...')
        
        # Create sample categories
        categories = self.create_categories()
        
        # Create sample products
        products = self.create_products(categories)
        
        # Create sample users
        users = self.create_users()
        
        # Create sample support tickets
        self.create_support_tickets(users, products)
        
        # Create sample service requests
        self.create_service_requests(users)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up sample data!')
        )

    def create_categories(self):
        """Create sample product categories."""
        categories_data = [
            {
                'name': 'Security Cameras',
                'slug': 'security-cameras',
                'description': 'Professional security camera systems for home and business use.'
            },
            {
                'name': 'Scanners',
                'slug': 'scanners',
                'description': 'High-quality document and photo scanners for various applications.'
            },
            {
                'name': 'Network Equipment',
                'slug': 'network-equipment',
                'description': 'Routers, switches, and networking accessories.'
            },
            {
                'name': 'Computer Accessories',
                'slug': 'computer-accessories',
                'description': 'Essential computer peripherals and accessories.'
            },
            {
                'name': 'Software',
                'slug': 'software',
                'description': 'Professional software solutions for business and personal use.'
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        return categories

    def create_products(self, categories):
        """Create sample products."""
        products_data = [
            {
                'name': 'HD Security Camera System',
                'slug': 'hd-security-camera-system',
                'category': categories[0],  # Security Cameras
                'description': 'Professional 4K security camera system with night vision and motion detection.',
                'short_description': '4K security camera system with night vision',
                'price': Decimal('299.99'),
                'sale_price': Decimal('249.99'),
                'sku': 'SEC-001',
                'stock_quantity': 25,
                'brand': 'SecureTech',
                'model': 'ST-4K-8CH',
                'condition': 'new',
                'warranty_months': 24,
                'is_featured': True
            },
            {
                'name': 'Document Scanner Pro',
                'slug': 'document-scanner-pro',
                'category': categories[1],  # Scanners
                'description': 'High-speed document scanner with automatic document feeder.',
                'short_description': 'High-speed document scanner with ADF',
                'price': Decimal('199.99'),
                'sku': 'SCAN-001',
                'stock_quantity': 15,
                'brand': 'ScanMaster',
                'model': 'SM-ADF-2000',
                'condition': 'new',
                'warranty_months': 12
            },
            {
                'name': 'Wireless Router',
                'slug': 'wireless-router',
                'category': categories[2],  # Network Equipment
                'description': 'Dual-band wireless router with advanced security features.',
                'short_description': 'Dual-band wireless router with security',
                'price': Decimal('89.99'),
                'sku': 'NET-001',
                'stock_quantity': 30,
                'brand': 'NetGear',
                'model': 'NG-WR3000',
                'condition': 'new',
                'warranty_months': 12
            },
            {
                'name': 'USB-C Hub',
                'slug': 'usb-c-hub',
                'category': categories[3],  # Computer Accessories
                'description': 'Multi-port USB-C hub with HDMI, USB, and SD card reader.',
                'short_description': 'Multi-port USB-C hub with HDMI',
                'price': Decimal('49.99'),
                'sku': 'ACC-001',
                'stock_quantity': 50,
                'brand': 'TechHub',
                'model': 'TH-USB-C-7',
                'condition': 'new',
                'warranty_months': 12
            },
            {
                'name': 'Antivirus Software Suite',
                'slug': 'antivirus-software-suite',
                'category': categories[4],  # Software
                'description': 'Comprehensive antivirus and internet security software.',
                'short_description': 'Comprehensive antivirus and security software',
                'price': Decimal('79.99'),
                'sale_price': Decimal('59.99'),
                'sku': 'SW-001',
                'stock_quantity': 100,
                'brand': 'SecureSoft',
                'model': 'SS-AV-2024',
                'condition': 'new',
                'warranty_months': 12,
                'is_featured': True
            }
        ]
        
        products = []
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            products.append(product)
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        return products

    def create_users(self):
        """Create sample users."""
        users_data = [
            {
                'email': 'admin@itstore.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True
            },
            {
                'email': 'staff@itstore.com',
                'first_name': 'Staff',
                'last_name': 'Member',
                'user_type': 'staff',
                'is_staff': True,
                'is_verified': True
            },
            {
                'email': 'customer1@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'user_type': 'customer',
                'is_verified': True
            },
            {
                'email': 'customer2@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'user_type': 'customer',
                'is_verified': True
            }
        ]
        
        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults=user_data
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {user.email}')
            users.append(user)
        
        return users

    def create_support_tickets(self, users, products):
        """Create sample support tickets."""
        ticket_data = [
            {
                'customer': users[2],  # customer1
                'title': 'Camera installation help needed',
                'description': 'I need assistance installing the security camera system I purchased.',
                'ticket_type': 'technical',
                'priority': 'medium',
                'related_product': products[0]
            },
            {
                'customer': users[3],  # customer2
                'title': 'Scanner driver issues',
                'description': 'Having trouble installing the scanner drivers on Windows 11.',
                'ticket_type': 'technical',
                'priority': 'high',
                'related_product': products[1]
            }
        ]
        
        for ticket_info in ticket_data:
            ticket, created = SupportTicket.objects.get_or_create(
                title=ticket_info['title'],
                customer=ticket_info['customer'],
                defaults={
                    'ticket_number': f"TKT-{ticket_info['customer'].id}-{random.randint(1000, 9999)}",
                    'description': ticket_info['description'],
                    'ticket_type': ticket_info['ticket_type'],
                    'priority': ticket_info['priority'],
                    'related_product': ticket_info['related_product']
                }
            )
            if created:
                self.stdout.write(f'Created ticket: {ticket.title}')

    def create_service_requests(self, users):
        """Create sample service requests."""
        service_data = [
            {
                'customer': users[2],  # customer1
                'title': 'Security camera installation',
                'description': 'Need professional installation of security camera system at my home.',
                'service_type': 'installation',
                'service_address': '123 Main Street',
                'service_city': 'Anytown',
                'service_state': 'CA',
                'service_zip_code': '90210'
            },
            {
                'customer': users[3],  # customer2
                'title': 'Network setup consultation',
                'description': 'Looking for advice on setting up a home office network.',
                'service_type': 'consultation',
                'service_address': '456 Oak Avenue',
                'service_city': 'Somewhere',
                'service_state': 'NY',
                'service_zip_code': '10001'
            }
        ]
        
        for service_info in service_data:
            service, created = ServiceRequest.objects.get_or_create(
                title=service_info['title'],
                customer=service_info['customer'],
                defaults={
                    'request_number': f"SRV-{service_info['customer'].id}-{random.randint(1000, 9999)}",
                    'description': service_info['description'],
                    'service_type': service_info['service_type'],
                    'service_address': service_info['service_address'],
                    'service_city': service_info['service_city'],
                    'service_state': service_info['service_state'],
                    'service_zip_code': service_info['service_zip_code']
                }
            )
            if created:
                self.stdout.write(f'Created service request: {service.title}')
