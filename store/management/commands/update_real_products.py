from django.core.management.base import BaseCommand
from store.models import Category, Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Update products with real IT component names and brands'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Updating products with real IT components and brands...')
        
        # Get existing categories
        try:
            data_viz_category = Category.objects.get(slug='data-visualization')
            bi_category = Category.objects.get(slug='business-intelligence')
            reporting_category = Category.objects.get(slug='reporting-tools')
            data_processing_category = Category.objects.get(slug='data-processing')
            predictive_category = Category.objects.get(slug='predictive-analytics')
        except Category.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Required categories not found. Please run setup_sample_data first.')
            )
            return
        
        # Clear existing products
        Product.objects.all().delete()
        self.stdout.write('🗑️  Cleared existing products')
        
        # Define real IT components with actual brands
        real_products = [
            # Data Visualization Components
            {
                'name': 'Samsung 4K Monitor 32" U32J590U',
                'slug': 'samsung-4k-monitor-32-u32j590u',
                'category': data_viz_category,
                'description': 'Samsung 32-inch 4K UHD monitor with excellent color accuracy and wide viewing angles. Perfect for data visualization and professional work.',
                'short_description': 'Samsung 32" 4K UHD monitor for professional data visualization',
                'price': Decimal('1899.00'),
                'sale_price': Decimal('1599.00'),
                'sku': 'SAM-U32J590U-001',
                'stock_quantity': 25,
                'brand': 'Samsung',
                'model': 'U32J590U',
                'condition': 'new',
                'warranty_months': 24,
                'is_featured': True
            },
            {
                'name': 'LG UltraWide 29" 29WP60G-B',
                'slug': 'lg-ultrawide-29-29wp60g-b',
                'category': data_viz_category,
                'description': 'LG UltraWide 29-inch monitor with 21:9 aspect ratio, perfect for multitasking and data analysis workflows.',
                'short_description': 'LG UltraWide 29" monitor for enhanced productivity',
                'price': Decimal('1299.00'),
                'sale_price': Decimal('1099.00'),
                'sku': 'LG-29WP60G-001',
                'stock_quantity': 40,
                'brand': 'LG',
                'model': '29WP60G-B',
                'condition': 'new',
                'warranty_months': 24,
                'is_featured': False
            },
            {
                'name': 'Dell P2422H 24" Business Monitor',
                'slug': 'dell-p2422h-24-business-monitor',
                'category': data_viz_category,
                'description': 'Dell 24-inch business monitor with IPS panel, excellent for office environments and data visualization tasks.',
                'short_description': 'Dell 24" business monitor with IPS panel',
                'price': Decimal('899.00'),
                'sale_price': Decimal('749.00'),
                'sku': 'DELL-P2422H-001',
                'stock_quantity': 60,
                'brand': 'Dell',
                'model': 'P2422H',
                'condition': 'new',
                'warranty_months': 36,
                'is_featured': False
            },
            
            # Business Intelligence Components
            {
                'name': 'Intel Core i7-12700K Processor',
                'slug': 'intel-core-i7-12700k-processor',
                'category': bi_category,
                'description': 'Intel 12th Gen Core i7-12700K processor with 12 cores, perfect for data processing and business intelligence applications.',
                'short_description': 'Intel Core i7-12700K 12-core processor for BI workloads',
                'price': Decimal('2499.00'),
                'sale_price': Decimal('2199.00'),
                'sku': 'INTEL-I7-12700K-001',
                'stock_quantity': 15,
                'brand': 'Intel',
                'model': 'Core i7-12700K',
                'condition': 'new',
                'warranty_months': 36,
                'is_featured': True
            },
            {
                'name': 'AMD Ryzen 9 5900X Processor',
                'slug': 'amd-ryzen-9-5900x-processor',
                'category': bi_category,
                'description': 'AMD Ryzen 9 5900X 12-core processor with excellent multi-threading performance for data analytics and BI processing.',
                'short_description': 'AMD Ryzen 9 5900X 12-core processor for analytics',
                'price': Decimal('2299.00'),
                'sale_price': Decimal('1999.00'),
                'sku': 'AMD-R9-5900X-001',
                'stock_quantity': 20,
                'brand': 'AMD',
                'model': 'Ryzen 9 5900X',
                'condition': 'new',
                'warranty_months': 36,
                'is_featured': False
            },
            
            # Data Processing Components
            {
                'name': 'Samsung 980 PRO 1TB NVMe SSD',
                'slug': 'samsung-980-pro-1tb-nvme-ssd',
                'category': data_processing_category,
                'description': 'Samsung 980 PRO 1TB NVMe SSD with PCIe 4.0 interface, perfect for high-speed data processing and storage.',
                'short_description': 'Samsung 980 PRO 1TB NVMe SSD for high-speed storage',
                'price': Decimal('899.00'),
                'sale_price': Decimal('749.00'),
                'sku': 'SAM-980PRO-1TB-001',
                'stock_quantity': 50,
                'brand': 'Samsung',
                'model': '980 PRO 1TB',
                'condition': 'new',
                'warranty_months': 60,
                'is_featured': True
            },
            {
                'name': 'Western Digital Black SN850 2TB NVMe SSD',
                'slug': 'wd-black-sn850-2tb-nvme-ssd',
                'category': data_processing_category,
                'description': 'WD Black SN850 2TB NVMe SSD with PCIe 4.0, excellent for data processing and large dataset storage.',
                'short_description': 'WD Black SN850 2TB NVMe SSD for data processing',
                'price': Decimal('1299.00'),
                'sale_price': Decimal('1099.00'),
                'sku': 'WD-SN850-2TB-001',
                'stock_quantity': 30,
                'brand': 'Western Digital',
                'model': 'SN850 2TB',
                'condition': 'new',
                'warranty_months': 60,
                'is_featured': False
            },
            
            # Reporting Tools Components
            {
                'name': 'HP LaserJet Pro M404dn Printer',
                'slug': 'hp-laserjet-pro-m404dn-printer',
                'category': reporting_category,
                'description': 'HP LaserJet Pro M404dn monochrome laser printer with duplex printing, perfect for business reports and documentation.',
                'short_description': 'HP LaserJet Pro M404dn monochrome laser printer',
                'price': Decimal('599.00'),
                'sale_price': Decimal('499.00'),
                'sku': 'HP-M404DN-001',
                'stock_quantity': 35,
                'brand': 'HP',
                'model': 'LaserJet Pro M404dn',
                'condition': 'new',
                'warranty_months': 12,
                'is_featured': False
            },
            {
                'name': 'Canon PIXMA G6020 All-in-One Printer',
                'slug': 'canon-pixma-g6020-all-in-one-printer',
                'category': reporting_category,
                'description': 'Canon PIXMA G6020 wireless all-in-one printer with high-capacity ink tanks, ideal for office reporting and documentation.',
                'short_description': 'Canon PIXMA G6020 wireless all-in-one printer',
                'price': Decimal('799.00'),
                'sale_price': Decimal('649.00'),
                'sku': 'CANON-G6020-001',
                'stock_quantity': 25,
                'brand': 'Canon',
                'model': 'PIXMA G6020',
                'condition': 'new',
                'warranty_months': 12,
                'is_featured': False
            },
            
            # Predictive Analytics Components
            {
                'name': 'NVIDIA GeForce RTX 4070 Graphics Card',
                'slug': 'nvidia-geforce-rtx-4070-graphics-card',
                'category': predictive_category,
                'description': 'NVIDIA GeForce RTX 4070 graphics card with AI acceleration, perfect for machine learning and predictive analytics workloads.',
                'short_description': 'NVIDIA RTX 4070 graphics card for AI and ML workloads',
                'price': Decimal('3299.00'),
                'sale_price': Decimal('2899.00'),
                'sku': 'NVIDIA-RTX4070-001',
                'stock_quantity': 10,
                'brand': 'NVIDIA',
                'model': 'GeForce RTX 4070',
                'condition': 'new',
                'warranty_months': 36,
                'is_featured': True
            },
            {
                'name': 'AMD Radeon RX 7800 XT Graphics Card',
                'slug': 'amd-radeon-rx-7800-xt-graphics-card',
                'category': predictive_category,
                'description': 'AMD Radeon RX 7800 XT graphics card with excellent compute performance for data science and predictive analytics.',
                'short_description': 'AMD RX 7800 XT graphics card for data science',
                'price': Decimal('2799.00'),
                'sale_price': Decimal('2399.00'),
                'sku': 'AMD-RX7800XT-001',
                'stock_quantity': 12,
                'brand': 'AMD',
                'model': 'Radeon RX 7800 XT',
                'condition': 'new',
                'warranty_months': 36,
                'is_featured': False
            },
            
            # Additional Components
            {
                'name': 'Corsair Vengeance LPX 32GB DDR4 RAM',
                'slug': 'corsair-vengeance-lpx-32gb-ddr4-ram',
                'category': data_processing_category,
                'description': 'Corsair Vengeance LPX 32GB DDR4-3200 memory kit, perfect for data processing and multitasking applications.',
                'short_description': 'Corsair Vengeance LPX 32GB DDR4-3200 memory kit',
                'price': Decimal('699.00'),
                'sale_price': Decimal('599.00'),
                'sku': 'CORSAIR-LPX-32GB-001',
                'stock_quantity': 45,
                'brand': 'Corsair',
                'model': 'Vengeance LPX 32GB',
                'condition': 'new',
                'warranty_months': 60,
                'is_featured': False
            },
            {
                'name': 'ASUS ROG Strix B550-F Gaming Motherboard',
                'slug': 'asus-rog-strix-b550-f-gaming-motherboard',
                'category': bi_category,
                'description': 'ASUS ROG Strix B550-F Gaming motherboard with excellent connectivity and performance for business intelligence systems.',
                'short_description': 'ASUS ROG Strix B550-F Gaming motherboard',
                'price': Decimal('899.00'),
                'sale_price': Decimal('749.00'),
                'sku': 'ASUS-B550F-001',
                'stock_quantity': 20,
                'brand': 'ASUS',
                'model': 'ROG Strix B550-F',
                'condition': 'new',
                'warranty_months': 36,
                'is_featured': False
            },
            {
                'name': 'MSI MAG B550 Tomahawk Motherboard',
                'slug': 'msi-mag-b550-tomahawk-motherboard',
                'category': bi_category,
                'description': 'MSI MAG B550 Tomahawk motherboard with robust build quality and excellent performance for data processing systems.',
                'short_description': 'MSI MAG B550 Tomahawk motherboard',
                'price': Decimal('799.00'),
                'sale_price': Decimal('649.00'),
                'sku': 'MSI-B550-TOM-001',
                'stock_quantity': 25,
                'brand': 'MSI',
                'model': 'MAG B550 Tomahawk',
                'condition': 'new',
                'warranty_months': 36,
                'is_featured': False
            },
            {
                'name': 'Seagate BarraCuda 4TB HDD',
                'slug': 'seagate-barracuda-4tb-hdd',
                'category': data_processing_category,
                'description': 'Seagate BarraCuda 4TB internal hard drive with 7200 RPM, perfect for bulk data storage and backup solutions.',
                'short_description': 'Seagate BarraCuda 4TB 7200 RPM internal hard drive',
                'price': Decimal('399.00'),
                'sale_price': Decimal('329.00'),
                'sku': 'SEAGATE-4TB-001',
                'stock_quantity': 60,
                'brand': 'Seagate',
                'model': 'BarraCuda 4TB',
                'condition': 'new',
                'warranty_months': 24,
                'is_featured': False
            },
            {
                'name': 'Logitech MX Master 3S Wireless Mouse',
                'slug': 'logitech-mx-master-3s-wireless-mouse',
                'category': data_viz_category,
                'description': 'Logitech MX Master 3S wireless mouse with precision tracking and ergonomic design, perfect for data visualization work.',
                'short_description': 'Logitech MX Master 3S wireless precision mouse',
                'price': Decimal('299.00'),
                'sale_price': Decimal('249.00'),
                'sku': 'LOGITECH-MX3S-001',
                'stock_quantity': 80,
                'brand': 'Logitech',
                'model': 'MX Master 3S',
                'condition': 'new',
                'warranty_months': 24,
                'is_featured': False
            },
            {
                'name': 'Microsoft Surface Keyboard',
                'slug': 'microsoft-surface-keyboard',
                'category': data_viz_category,
                'description': 'Microsoft Surface Keyboard with premium typing experience and Bluetooth connectivity, ideal for professional data work.',
                'short_description': 'Microsoft Surface Keyboard with Bluetooth',
                'price': Decimal('199.00'),
                'sale_price': Decimal('159.00'),
                'sku': 'MS-SURFACE-KB-001',
                'stock_quantity': 70,
                'brand': 'Microsoft',
                'model': 'Surface Keyboard',
                'condition': 'new',
                'warranty_months': 12,
                'is_featured': False
            }
        ]
        
        created_count = 0
        for prod_data in real_products:
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            
            if created:
                self.stdout.write(
                    f'✅ Created: {product.name} - {product.price} MAD '
                    f'({"Sale: " + str(product.sale_price) + " MAD" if product.sale_price else "No sale"})'
                )
                created_count += 1
            else:
                self.stdout.write(
                    f'🔄 Updated: {product.name} - {product.price} MAD '
                    f'({"Sale: " + str(product.sale_price) + " MAD" if product.sale_price else "No sale"})'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Successfully processed {len(real_products)} real IT components!')
        )
        
        # Display brand summary
        self.stdout.write('\n🏷️  Brand Distribution:')
        self.stdout.write('=' * 40)
        
        brands = {}
        for product in Product.objects.all():
            brand = product.brand
            if brand in brands:
                brands[brand] += 1
            else:
                brands[brand] = 1
        
        for brand, count in sorted(brands.items()):
            self.stdout.write(f'• {brand}: {count} products')
        
        # Display price ranges
        self.stdout.write('\n💰 Price Ranges by Category:')
        self.stdout.write('=' * 50)
        
        categories = Category.objects.all()
        for category in categories:
            category_products = Product.objects.filter(category=category)
            if category_products.exists():
                prices = [p.price for p in category_products]
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                
                self.stdout.write(f'\n{category.name}:')
                self.stdout.write(f'  • Products: {len(category_products)}')
                self.stdout.write(f'  • Price Range: {min_price} - {max_price} MAD')
                self.stdout.write(f'  • Average: {avg_price:.2f} MAD')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Real IT components catalog updated successfully!')
        )

