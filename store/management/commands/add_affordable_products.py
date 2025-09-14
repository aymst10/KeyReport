from django.core.management.base import BaseCommand
from store.models import Category, Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Add affordable products for the Moroccan market'

    def handle(self, *args, **options):
        self.stdout.write('Adding affordable products for Moroccan market...')
        
        # Get existing categories
        try:
            data_viz_category = Category.objects.get(slug='data-visualization')
            bi_category = Category.objects.get(slug='business-intelligence')
            reporting_category = Category.objects.get(slug='reporting-tools')
        except Category.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Required categories not found. Please run setup_sample_data first.')
            )
            return
        
        # Define affordable products for Moroccan market
        affordable_products = [
            {
                'name': 'Basic Chart Widget',
                'slug': 'basic-chart-widget',
                'category': data_viz_category,
                'description': 'Simple and easy-to-use chart widget for basic data visualization needs. Perfect for small businesses and startups.',
                'short_description': 'Simple chart widget for basic data visualization',
                'price': Decimal('199.00'),
                'sale_price': Decimal('149.00'),
                'sku': 'CHART-BASIC-001',
                'stock_quantity': 100,
                'brand': 'ChartMaster',
                'model': 'CM-Basic-2024',
                'condition': 'new',
                'warranty_months': 6,
                'is_featured': False
            },
            {
                'name': 'Simple Dashboard Template',
                'slug': 'simple-dashboard-template',
                'category': data_viz_category,
                'description': 'Ready-to-use dashboard template with common widgets and responsive design. Ideal for quick deployment.',
                'short_description': 'Ready-to-use dashboard template with common widgets',
                'price': Decimal('299.00'),
                'sale_price': Decimal('249.00'),
                'sku': 'DASH-TEMPLATE-001',
                'stock_quantity': 75,
                'brand': 'AnalyticsPro',
                'model': 'AP-Template-2024',
                'condition': 'new',
                'warranty_months': 6,
                'is_featured': False
            },
            {
                'name': 'Excel Report Converter',
                'slug': 'excel-report-converter',
                'category': reporting_category,
                'description': 'Convert Excel files to professional PDF reports with customizable templates. Perfect for small offices.',
                'short_description': 'Convert Excel to professional PDF reports',
                'price': Decimal('99.00'),
                'sale_price': Decimal('79.00'),
                'sku': 'REP-EXCEL-001',
                'stock_quantity': 150,
                'brand': 'ReportPro',
                'model': 'RP-Excel-2024',
                'condition': 'new',
                'warranty_months': 6,
                'is_featured': False
            },
            {
                'name': 'Data Table Component',
                'slug': 'data-table-component',
                'category': data_viz_category,
                'description': 'Responsive data table component with sorting, filtering, and pagination. Essential for data display.',
                'short_description': 'Responsive data table with sorting and filtering',
                'price': Decimal('149.00'),
                'sale_price': Decimal('119.00'),
                'sku': 'TABLE-001',
                'stock_quantity': 120,
                'brand': 'DataTable',
                'model': 'DT-Component-2024',
                'condition': 'new',
                'warranty_months': 6,
                'is_featured': False
            },
            {
                'name': 'Simple Analytics Tracker',
                'slug': 'simple-analytics-tracker',
                'category': bi_category,
                'description': 'Basic analytics tracking for websites and applications. Track key metrics without complexity.',
                'short_description': 'Basic analytics tracking for websites and apps',
                'price': Decimal('199.00'),
                'sale_price': Decimal('159.00'),
                'sku': 'ANALYTICS-BASIC-001',
                'stock_quantity': 80,
                'brand': 'BIAnalytics',
                'model': 'BI-Basic-2024',
                'condition': 'new',
                'warranty_months': 6,
                'is_featured': False
            },
            {
                'name': 'CSV Data Processor',
                'slug': 'csv-data-processor',
                'category': reporting_category,
                'description': 'Simple CSV data processing tool with basic cleaning and formatting capabilities.',
                'short_description': 'Simple CSV data processing and cleaning tool',
                'price': Decimal('79.00'),
                'sale_price': Decimal('59.00'),
                'sku': 'CSV-PROC-001',
                'stock_quantity': 200,
                'brand': 'DataFlow',
                'model': 'DF-CSV-2024',
                'condition': 'new',
                'warranty_months': 6,
                'is_featured': False
            }
        ]
        
        created_count = 0
        for prod_data in affordable_products:
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            
            if created:
                self.stdout.write(
                    f'Created: {product.name} - {product.price} MAD '
                    f'({"Sale: " + str(product.sale_price) + " MAD" if product.sale_price else "No sale"})'
                )
                created_count += 1
            else:
                self.stdout.write(
                    f'Updated: {product.name} - {product.price} MAD '
                    f'({"Sale: " + str(product.sale_price) + " MAD" if product.sale_price else "No sale"})'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {len(affordable_products)} affordable products!')
        )
        
        # Display complete pricing summary
        self.stdout.write('\n💰 Complete Pricing Structure (MAD):')
        self.stdout.write('=' * 60)
        
        # Entry Level (Under 200 MAD)
        self.stdout.write('\n🟢 Entry Level (Under 200 MAD):')
        entry_products = Product.objects.filter(price__lt=200).order_by('price')
        for product in entry_products:
            discount = ((product.price - product.sale_price) / product.price * 100) if product.sale_price else 0
            self.stdout.write(
                f'  • {product.name}: {product.price} MAD '
                f'{"(" + str(int(discount)) + "% off)" if discount > 0 else ""}'
            )
        
        # Mid Level (200-500 MAD)
        self.stdout.write('\n🟡 Mid Level (200-500 MAD):')
        mid_products = Product.objects.filter(price__gte=200, price__lt=500).order_by('price')
        for product in mid_products:
            discount = ((product.price - product.sale_price) / product.price * 100) if product.sale_price else 0
            self.stdout.write(
                f'  • {product.name}: {product.price} MAD '
                f'{"(" + str(int(discount)) + "% off)" if discount > 0 else ""}'
            )
        
        # Professional Level (500+ MAD)
        self.stdout.write('\n🔴 Professional Level (500+ MAD):')
        pro_products = Product.objects.filter(price__gte=500).order_by('price')
        for product in pro_products:
            discount = ((product.price - product.sale_price) / product.price * 100) if product.sale_price else 0
            self.stdout.write(
                f'  • {product.name}: {product.price} MAD '
                f'{"(" + str(int(discount)) + "% off)" if discount > 0 else ""}'
            )
        
        self.stdout.write('\n🎯 Market Positioning:')
        self.stdout.write('• Entry Level: 59-199 MAD (Startups, Small Businesses)')
        self.stdout.write('• Mid Level: 199-499 MAD (Growing Companies)')
        self.stdout.write('• Professional: 499-1899 MAD (Enterprises)')

