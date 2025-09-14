from django.core.management.base import BaseCommand
from store.models import Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Update all product prices to realistic Moroccan Dirham (MAD) amounts'

    def handle(self, *args, **options):
        # Define realistic prices in MAD for different product categories
        price_mapping = {
            # Graphics Cards
            'nvidia': {
                'rtx 4070': Decimal('8999.00'),  # ~$900 USD = ~9000 MAD
                'rtx 4060': Decimal('5999.00'),  # ~$600 USD = ~6000 MAD
                'rtx 3080': Decimal('7999.00'),  # ~$800 USD = ~8000 MAD
            },
            'amd_gpu': {
                'rx 7800': Decimal('7499.00'),   # ~$750 USD = ~7500 MAD
                'rx 6700': Decimal('4999.00'),   # ~$500 USD = ~5000 MAD
            },
            
            # Processors
            'intel': {
                'i7': Decimal('3999.00'),        # ~$400 USD = ~4000 MAD
                'i5': Decimal('2999.00'),        # ~$300 USD = ~3000 MAD
                'i3': Decimal('1999.00'),        # ~$200 USD = ~2000 MAD
            },
            'amd': {
                'ryzen 9': Decimal('4999.00'),   # ~$500 USD = ~5000 MAD
                'ryzen 7': Decimal('3499.00'),   # ~$350 USD = ~3500 MAD
                'ryzen 5': Decimal('2499.00'),   # ~$250 USD = ~2500 MAD
            },
            
            # Motherboards
            'motherboard': Decimal('1999.00'),   # ~$200 USD = ~2000 MAD
            
            # RAM
            'ram': Decimal('1299.00'),           # ~$130 USD = ~1300 MAD
            
            # Storage
            'ssd': {
                '1tb': Decimal('899.00'),        # ~$90 USD = ~900 MAD
                '2tb': Decimal('1599.00'),       # ~$160 USD = ~1600 MAD
                '500gb': Decimal('599.00'),      # ~$60 USD = ~600 MAD
            },
            'hdd': {
                '4tb': Decimal('799.00'),        # ~$80 USD = ~800 MAD
                '2tb': Decimal('499.00'),        # ~$50 USD = ~500 MAD
                '1tb': Decimal('299.00'),        # ~$30 USD = ~300 MAD
            },
            
            # Monitors
            'monitor': {
                '4k': Decimal('2999.00'),        # ~$300 USD = ~3000 MAD
                '2k': Decimal('1999.00'),        # ~$200 USD = ~2000 MAD
                '1080p': Decimal('1299.00'),     # ~$130 USD = ~1300 MAD
            },
            
            # Peripherals
            'keyboard': Decimal('899.00'),       # ~$90 USD = ~900 MAD
            'mouse': Decimal('499.00'),          # ~$50 USD = ~500 MAD
            'headset': Decimal('699.00'),        # ~$70 USD = ~700 MAD
            
            # Printers
            'printer': Decimal('1299.00'),       # ~$130 USD = ~1300 MAD
        }
        
        updated_count = 0
        
        for product in Product.objects.all():
            old_price = product.price
            new_price = None
            
            # Determine new price based on product name and category
            name_lower = product.name.lower()
            category_lower = product.category.name.lower() if product.category else ""
            
            # Graphics Cards
            if 'nvidia' in name_lower or 'rtx' in name_lower or 'geforce' in name_lower:
                if 'rtx 4070' in name_lower or '4070' in name_lower:
                    new_price = price_mapping['nvidia']['rtx 4070']
                elif 'rtx 4060' in name_lower or '4060' in name_lower:
                    new_price = price_mapping['nvidia']['rtx 4060']
                elif 'rtx 3080' in name_lower or '3080' in name_lower:
                    new_price = price_mapping['nvidia']['rtx 3080']
                else:
                    new_price = price_mapping['nvidia']['rtx 4070']  # Default high-end
                    
            elif 'amd' in name_lower or 'radeon' in name_lower or 'rx' in name_lower:
                if '7800' in name_lower:
                    new_price = price_mapping['amd_gpu']['rx 7800']
                elif '6700' in name_lower:
                    new_price = price_mapping['amd_gpu']['rx 6700']
                else:
                    new_price = price_mapping['amd_gpu']['rx 7800']  # Default high-end
            
            # Processors
            elif 'intel' in name_lower and ('i7' in name_lower or 'core i7' in name_lower):
                new_price = price_mapping['intel']['i7']
            elif 'intel' in name_lower and ('i5' in name_lower or 'core i5' in name_lower):
                new_price = price_mapping['intel']['i5']
            elif 'intel' in name_lower and ('i3' in name_lower or 'core i3' in name_lower):
                new_price = price_mapping['intel']['i3']
            elif 'amd' in name_lower and ('ryzen 9' in name_lower or 'r9' in name_lower):
                new_price = price_mapping['amd']['ryzen 9']
            elif 'amd' in name_lower and ('ryzen 7' in name_lower or 'r7' in name_lower):
                new_price = price_mapping['amd']['ryzen 7']
            elif 'amd' in name_lower and ('ryzen 5' in name_lower or 'r5' in name_lower):
                new_price = price_mapping['amd']['ryzen 5']
            
            # Motherboards
            elif 'motherboard' in name_lower or 'motherboard' in category_lower:
                new_price = price_mapping['motherboard']
            
            # RAM
            elif 'ram' in name_lower or 'memory' in name_lower or 'ddr' in name_lower:
                new_price = price_mapping['ram']
            
            # Storage - SSDs
            elif 'ssd' in name_lower or 'nvme' in name_lower:
                if '2tb' in name_lower or '2 tb' in name_lower:
                    new_price = price_mapping['ssd']['2tb']
                elif '1tb' in name_lower or '1 tb' in name_lower:
                    new_price = price_mapping['ssd']['1tb']
                elif '500' in name_lower:
                    new_price = price_mapping['ssd']['500gb']
                else:
                    new_price = price_mapping['ssd']['1tb']  # Default
            
            # Storage - HDDs
            elif 'hdd' in name_lower or 'hard drive' in name_lower:
                if '4tb' in name_lower or '4 tb' in name_lower:
                    new_price = price_mapping['hdd']['4tb']
                elif '2tb' in name_lower or '2 tb' in name_lower:
                    new_price = price_mapping['hdd']['2tb']
                elif '1tb' in name_lower or '1 tb' in name_lower:
                    new_price = price_mapping['hdd']['1tb']
                else:
                    new_price = price_mapping['hdd']['1tb']  # Default
            
            # Monitors
            elif 'monitor' in name_lower or 'display' in name_lower:
                if '4k' in name_lower or 'ultra' in name_lower:
                    new_price = price_mapping['monitor']['4k']
                elif '2k' in name_lower or '1440' in name_lower:
                    new_price = price_mapping['monitor']['2k']
                else:
                    new_price = price_mapping['monitor']['1080p']  # Default
            
            # Keyboards
            elif 'keyboard' in name_lower:
                new_price = price_mapping['keyboard']
            
            # Mice
            elif 'mouse' in name_lower:
                new_price = price_mapping['mouse']
            
            # Headsets
            elif 'headset' in name_lower or 'headphone' in name_lower:
                new_price = price_mapping['headset']
            
            # Printers
            elif 'printer' in name_lower:
                new_price = price_mapping['printer']
            
            # Default fallback based on category
            else:
                if 'graphics' in category_lower or 'gpu' in category_lower:
                    new_price = Decimal('5999.00')  # Default GPU price
                elif 'processor' in category_lower or 'cpu' in category_lower:
                    new_price = Decimal('2999.00')  # Default CPU price
                elif 'motherboard' in category_lower:
                    new_price = price_mapping['motherboard']
                elif 'memory' in category_lower or 'ram' in category_lower:
                    new_price = price_mapping['ram']
                elif 'storage' in category_lower:
                    new_price = price_mapping['ssd']['1tb']
                elif 'monitor' in category_lower or 'display' in category_lower:
                    new_price = price_mapping['monitor']['1080p']
                elif 'accessories' in category_lower or 'peripheral' in category_lower:
                    new_price = Decimal('599.00')  # Default accessory price
                else:
                    new_price = Decimal('1999.00')  # General default price
            
            # Update the product price
            if new_price:
                product.price = new_price
                # Add a small sale price for some products (10-15% discount)
                if updated_count % 3 == 0:  # Every 3rd product gets a sale price
                    product.sale_price = new_price * Decimal('0.85')  # 15% discount
                else:
                    product.sale_price = None
                
                product.save()
                updated_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated {product.name}: {old_price} → {new_price} MAD'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} product prices to MAD currency'
            )
        )
