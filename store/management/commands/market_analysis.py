from django.core.management.base import BaseCommand
from store.models import Product, Category
from decimal import Decimal

class Command(BaseCommand):
    help = 'Analyze market positioning and pricing strategy for Moroccan market'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Analyzing market positioning and pricing strategy...')
        self.stdout.write('=' * 70)
        
        # Get all products
        products = Product.objects.all().order_by('price')
        total_products = products.count()
        
        # Calculate statistics
        total_value = sum(product.price for product in products)
        avg_price = total_value / total_products if total_products > 0 else 0
        
        # Price ranges
        min_price = min(product.price for product in products)
        max_price = max(product.price for product in products)
        
        # Products with sales
        products_with_sales = [p for p in products if p.sale_price]
        avg_discount = sum(((p.price - p.sale_price) / p.price * 100) for p in products_with_sales) / len(products_with_sales) if products_with_sales else 0
        
        self.stdout.write(f'\n📊 Market Overview:')
        self.stdout.write(f'• Total Products: {total_products}')
        self.stdout.write(f'• Price Range: {min_price} - {max_price} MAD')
        self.stdout.write(f'• Average Price: {avg_price:.2f} MAD')
        self.stdout.write(f'• Products on Sale: {len(products_with_sales)}')
        self.stdout.write(f'• Average Discount: {avg_discount:.1f}%')
        
        # Category analysis
        self.stdout.write(f'\n🏷️  Category Analysis:')
        categories = Category.objects.all()
        
        for category in categories:
            category_products = products.filter(category=category)
            if category_products.exists():
                cat_min = min(p.price for p in category_products)
                cat_max = max(p.price for p in category_products)
                cat_avg = sum(p.price for p in category_products) / len(category_products)
                
                self.stdout.write(f'\n{category.name}:')
                self.stdout.write(f'  • Products: {len(category_products)}')
                self.stdout.write(f'  • Price Range: {cat_min} - {cat_max} MAD')
                self.stdout.write(f'  • Average: {cat_avg:.2f} MAD')
                
                # Show products in category
                for product in category_products:
                    discount_info = f" (Sale: {product.sale_price} MAD)" if product.sale_price else ""
                    self.stdout.write(f'    - {product.name}: {product.price} MAD{discount_info}')
        
        # Market positioning analysis
        self.stdout.write(f'\n🎯 Market Positioning Strategy:')
        self.stdout.write('=' * 50)
        
        # Entry Level (Under 200 MAD)
        entry_products = [p for p in products if p.price < 200]
        self.stdout.write(f'\n🟢 Entry Level (Under 200 MAD) - {len(entry_products)} products')
        self.stdout.write('Target: Startups, Small Businesses, Individual Users')
        self.stdout.write('Price Range: 59-199 MAD')
        for product in entry_products:
            self.stdout.write(f'  • {product.name}: {product.price} MAD')
        
        # Mid Level (200-500 MAD)
        mid_products = [p for p in products if 200 <= p.price < 500]
        self.stdout.write(f'\n🟡 Mid Level (200-500 MAD) - {len(mid_products)} products')
        self.stdout.write('Target: Growing Companies, Medium Businesses')
        self.stdout.write('Price Range: 199-499 MAD')
        for product in mid_products:
            self.stdout.write(f'  • {product.name}: {product.price} MAD')
        
        # Professional Level (500+ MAD)
        pro_products = [p for p in products if p.price >= 500]
        self.stdout.write(f'\n🔴 Professional Level (500+ MAD) - {len(pro_products)} products')
        self.stdout.write('Target: Enterprises, Large Organizations')
        self.stdout.write('Price Range: 499-1899 MAD')
        for product in pro_products:
            self.stdout.write(f'  • {product.name}: {product.price} MAD')
        
        # Competitive analysis
        self.stdout.write(f'\n💼 Competitive Analysis:')
        self.stdout.write('=' * 40)
        
        self.stdout.write(f'\n✅ Strengths:')
        self.stdout.write('• Wide price range (59-1899 MAD) covering all market segments')
        self.stdout.write('• Entry-level products accessible to small businesses')
        self.stdout.write('• Professional solutions for enterprise needs')
        self.stdout.write('• Consistent discount strategy (15-25% off)')
        
        self.stdout.write(f'\n🎯 Market Opportunities:')
        self.stdout.write('• Entry level: High demand from startups and small businesses')
        self.stdout.write('• Mid level: Growing market for expanding companies')
        self.stdout.write('• Professional: Premium positioning for enterprise clients')
        
        self.stdout.write(f'\n💰 Revenue Projections:')
        self.stdout.write('• Entry Level: High volume, lower margin')
        self.stdout.write('• Mid Level: Balanced volume and margin')
        self.stdout.write('• Professional: Lower volume, higher margin')
        
        self.stdout.write(f'\n🚀 Recommendations:')
        self.stdout.write('1. Focus marketing on entry-level products for market penetration')
        self.stdout.write('2. Use mid-level products for customer retention and upselling')
        self.stdout.write('3. Position professional products as premium solutions')
        self.stdout.write('4. Maintain competitive pricing with regular promotions')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Market analysis completed successfully!')
        )

