from django.core.management.base import BaseCommand
from store.models import Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Update product prices with realistic Moroccan market prices'

    def handle(self, *args, **options):
        self.stdout.write('Updating product prices for Moroccan market...')
        
        # Define realistic prices for Moroccan market (in MAD)
        price_updates = {
            'dashboard-widget-suite': {
                'price': Decimal('899.00'),
                'sale_price': Decimal('749.00'),
                'description': 'Complete suite of interactive dashboard widgets for real-time data visualization and monitoring.'
            },
            'advanced-chart-component': {
                'price': Decimal('449.00'),
                'sale_price': Decimal('399.00'),
                'description': 'Advanced charting library with multiple visualization types including bar, line, pie, and scatter plots.'
            },
            'business-intelligence-platform': {
                'price': Decimal('1899.00'),
                'sale_price': Decimal('1599.00'),
                'description': 'Complete BI platform with advanced analytics, reporting, and data discovery capabilities.'
            },
            'data-processing-engine': {
                'price': Decimal('1199.00'),
                'sale_price': Decimal('999.00'),
                'description': 'High-performance data processing engine for ETL operations and real-time analytics.'
            },
            'automated-report-generator': {
                'price': Decimal('599.00'),
                'sale_price': Decimal('499.00'),
                'description': 'Automated report generation system with customizable templates and scheduling.'
            },
            'predictive-analytics-suite': {
                'price': Decimal('1399.00'),
                'sale_price': Decimal('1199.00'),
                'description': 'Machine learning suite with predictive modeling and forecasting capabilities.'
            }
        }
        
        updated_count = 0
        for slug, price_data in price_updates.items():
            try:
                product = Product.objects.get(slug=slug)
                old_price = product.price
                old_sale_price = product.sale_price
                
                product.price = price_data['price']
                product.sale_price = price_data['sale_price']
                if 'description' in price_data:
                    product.description = price_data['description']
                
                product.save()
                
                self.stdout.write(
                    f'Updated {product.name}: '
                    f'Price: {old_price} → {product.price} MAD, '
                    f'Sale: {old_sale_price} → {product.sale_price} MAD'
                )
                updated_count += 1
                
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Product with slug "{slug}" not found')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} products with realistic Moroccan prices!')
        )
        
        # Display pricing summary
        self.stdout.write('\n📊 New Pricing Summary (MAD):')
        self.stdout.write('=' * 50)
        
        for slug, price_data in price_updates.items():
            product = Product.objects.get(slug=slug)
            discount = ((product.price - product.sale_price) / product.price * 100) if product.sale_price else 0
            self.stdout.write(
                f'• {product.name}: {product.price} MAD '
                f'{"(" + str(int(discount)) + "% off)" if discount > 0 else ""}'
            )
        
        self.stdout.write('\n💡 Price ranges by category:')
        self.stdout.write('• Data Visualization: 399-899 MAD')
        self.stdout.write('• Business Intelligence: 1599-1899 MAD')
        self.stdout.write('• Data Processing: 999-1199 MAD')
        self.stdout.write('• Reporting Tools: 499-599 MAD')
        self.stdout.write('• Predictive Analytics: 1199-1399 MAD')

