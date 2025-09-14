from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models import Category, Product
from support.models import SupportTicket, ServiceRequest
import random
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up sample data for Key Reports Analytics application'

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
        """Create sample analytics component categories."""
        categories_data = [
            {
                'name': 'Data Visualization',
                'slug': 'data-visualization',
                'description': 'Interactive charts, graphs, and dashboard components for data presentation.'
            },
            {
                'name': 'Business Intelligence',
                'slug': 'business-intelligence',
                'description': 'Advanced BI tools and analytics platforms for business insights.'
            },
            {
                'name': 'Data Processing',
                'slug': 'data-processing',
                'description': 'ETL tools, data connectors, and processing engines.'
            },
            {
                'name': 'Reporting Tools',
                'slug': 'reporting-tools',
                'description': 'Automated reporting and document generation solutions.'
            },
            {
                'name': 'Predictive Analytics',
                'slug': 'predictive-analytics',
                'description': 'Machine learning and predictive modeling components.'
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
        """Create sample analytics components."""
        products_data = [
            {
                'name': 'Dashboard Widget Suite',
                'slug': 'dashboard-widget-suite',
                'category': categories[0],  # Data Visualization
                'description': 'Complete suite of interactive dashboard widgets for real-time data visualization and monitoring.',
                'short_description': 'Interactive dashboard widgets for real-time analytics',
                'price': Decimal('5999.90'),
                'sale_price': Decimal('4999.90'),
                'sku': 'DASH-001',
                'stock_quantity': 50,
                'brand': 'AnalyticsPro',
                'model': 'DW-Suite-2024',
                'condition': 'new',
                'warranty_months': 12,
                'is_featured': True
            },
            {
                'name': 'Advanced Chart Component',
                'slug': 'advanced-chart-component',
                'category': categories[0],  # Data Visualization
                'description': 'Advanced charting library with multiple visualization types including bar, line, pie, and scatter plots.',
                'short_description': 'Advanced charting library with multiple visualization types',
                'price': Decimal('2999.90'),
                'sku': 'CHART-001',
                'stock_quantity': 75,
                'brand': 'ChartMaster',
                'model': 'CM-Adv-2024',
                'condition': 'new',
                'warranty_months': 12
            },
            {
                'name': 'Business Intelligence Platform',
                'slug': 'business-intelligence-platform',
                'category': categories[1],  # Business Intelligence
                'description': 'Complete BI platform with advanced analytics, reporting, and data discovery capabilities.',
                'short_description': 'Complete BI platform with advanced analytics',
                'price': Decimal('12999.90'),
                'sale_price': Decimal('9999.90'),
                'sku': 'BI-001',
                'stock_quantity': 25,
                'brand': 'BIAnalytics',
                'model': 'BI-Enterprise-2024',
                'condition': 'new',
                'warranty_months': 24,
                'is_featured': True
            },
            {
                'name': 'Data Processing Engine',
                'slug': 'data-processing-engine',
                'category': categories[2],  # Data Processing
                'description': 'High-performance data processing engine for ETL operations and real-time analytics.',
                'short_description': 'High-performance data processing engine for ETL',
                'price': Decimal('7999.90'),
                'sku': 'DPE-001',
                'stock_quantity': 40,
                'brand': 'DataFlow',
                'model': 'DF-Engine-Pro',
                'condition': 'new',
                'warranty_months': 12
            },
            {
                'name': 'Automated Report Generator',
                'slug': 'automated-report-generator',
                'category': categories[3],  # Reporting Tools
                'description': 'Automated report generation system with customizable templates and scheduling.',
                'short_description': 'Automated report generation with customizable templates',
                'price': Decimal('3999.90'),
                'sku': 'ARG-001',
                'stock_quantity': 60,
                'brand': 'ReportPro',
                'model': 'RP-Auto-2024',
                'condition': 'new',
                'warranty_months': 12
            },
            {
                'name': 'Predictive Analytics Suite',
                'slug': 'predictive-analytics-suite',
                'category': categories[4],  # Predictive Analytics
                'description': 'Machine learning suite with predictive modeling and forecasting capabilities.',
                'short_description': 'Machine learning suite with predictive modeling',
                'price': Decimal('8999.90'),
                'sale_price': Decimal('7499.90'),
                'sku': 'PA-001',
                'stock_quantity': 30,
                'brand': 'PredictML',
                'model': 'PM-Suite-2024',
                'condition': 'new',
                'warranty_months': 18,
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
                'email': 'admin@keyreportsanalytics.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True
            },
            {
                'email': 'staff@keyreportsanalytics.com',
                'first_name': 'Staff',
                'last_name': 'Member',
                'user_type': 'staff',
                'is_staff': True,
                'is_verified': True
            },
            {
                'email': 'customer1@keyreportsanalytics.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'user_type': 'customer',
                'is_verified': True
            },
            {
                'email': 'customer2@keyreportsanalytics.com',
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
                'title': 'Dashboard widget configuration help needed',
                'description': 'I need assistance configuring the dashboard widgets for my analytics platform.',
                'ticket_type': 'technical',
                'priority': 'medium',
                'related_product': products[0]
            },
            {
                'customer': users[3],  # customer2
                'title': 'Chart component integration issues',
                'description': 'Having trouble integrating the advanced chart component into my existing system.',
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
        from datetime import date, time
        
        service_data = [
            {
                'customer': users[2],  # customer1
                'title': 'Analytics platform setup',
                'description': 'Need professional setup and configuration of analytics platform for my business.',
                'service_type': 'installation',
                'service_address': '123 Main Street',
                'service_city': 'Anytown',
                'service_state': 'CA',
                'service_zip_code': '90210',
                'preferred_date': date(2024, 12, 15),
                'preferred_time': time(10, 0)  # 10:00 AM
            },
            {
                'customer': users[3],  # customer2
                'title': 'Data analytics consultation',
                'description': 'Looking for advice on implementing data analytics solutions for my business.',
                'service_type': 'consultation',
                'service_address': '456 Oak Avenue',
                'service_city': 'Somewhere',
                'service_state': 'NY',
                'service_zip_code': '10001',
                'preferred_date': date(2024, 12, 20),
                'preferred_time': time(14, 0)  # 2:00 PM
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
                    'service_zip_code': service_info['service_zip_code'],
                    'preferred_date': service_info['preferred_date'],
                    'preferred_time': service_info['preferred_time']
                }
            )
            if created:
                self.stdout.write(f'Created service request: {service.title}')
