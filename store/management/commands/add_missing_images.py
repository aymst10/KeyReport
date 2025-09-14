from django.core.management.base import BaseCommand
from store.models import Product, ProductImage
from django.core.files import File
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Add placeholder images for products that don\'t have images yet'

    def handle(self, *args, **options):
        # Create a simple placeholder image using existing images as fallbacks
        media_dir = Path('media/products')
        
        # Fallback images for different categories
        fallback_images = {
            'printer': 'canon-pixma-g6020-all-in-one-printer.jpg',
            'camera': 'dell-p2422h-24-business-monitor.jpg',  # Using monitor as fallback
            'keyboard': 'microsoft-surface-keyboard.jpg',
            'mouse': 'logitech-mx-master-3s-wireless-mouse.jpg',
            'headset': 'logitech-mx-master-3s-wireless-mouse.jpg',
            'monitor': 'samsung-4k-monitor-32-u32j590u.jpg',
            'graphics': 'nvidia-geforce-rtx-4070-graphics-card.jpg',
            'processor': 'intel-core-i7-12700k-processor.jpg',
            'motherboard': 'asus-rog-strix-b550-f-gaming-motherboard.jpg',
            'ram': 'corsair-vengeance-lpx-32gb-ddr4-ram.jpg',
            'ssd': 'samsung-980-pro-1tb-nvme-ssd.jpg',
            'hdd': 'seagate-barracuda-4tb-hdd.jpg',
        }
        
        updated_count = 0
        
        for product in Product.objects.all():
            # Check if product has a main image
            if not product.main_image or not product.main_image.name:
                product_name_lower = product.name.lower()
                category_name_lower = product.category.name.lower() if product.category else ""
                
                # Determine fallback image based on product name and category
                fallback_image = None
                
                if any(word in product_name_lower for word in ['printer', 'officejet', 'laserjet', 'pixma', 'ecotank']):
                    fallback_image = fallback_images['printer']
                elif any(word in product_name_lower for word in ['camera', 'protect', 'reolink', 'axis', 'dahua', 'hikvision']):
                    fallback_image = fallback_images['camera']
                elif any(word in product_name_lower for word in ['keyboard', 'mechanical', 'surface']):
                    fallback_image = fallback_images['keyboard']
                elif any(word in product_name_lower for word in ['mouse', 'wireless', 'deathadder']):
                    fallback_image = fallback_images['mouse']
                elif any(word in product_name_lower for word in ['headset', 'headphone', 'cloud']):
                    fallback_image = fallback_images['headset']
                elif any(word in product_name_lower for word in ['monitor', 'display', 'ultrawide']):
                    fallback_image = fallback_images['monitor']
                elif any(word in product_name_lower for word in ['graphics', 'rtx', 'rx', 'geforce', 'radeon']):
                    fallback_image = fallback_images['graphics']
                elif any(word in product_name_lower for word in ['processor', 'intel', 'amd', 'core', 'ryzen']):
                    fallback_image = fallback_images['processor']
                elif any(word in product_name_lower for word in ['motherboard', 'rog', 'mag', 'strix']):
                    fallback_image = fallback_images['motherboard']
                elif any(word in product_name_lower for word in ['ram', 'memory', 'ddr', 'vengeance']):
                    fallback_image = fallback_images['ram']
                elif any(word in product_name_lower for word in ['ssd', 'nvme', '980', 'sn850']):
                    fallback_image = fallback_images['ssd']
                elif any(word in product_name_lower for word in ['hdd', 'hard', 'barracuda']):
                    fallback_image = fallback_images['hdd']
                elif 'printer' in category_name_lower:
                    fallback_image = fallback_images['printer']
                elif 'camera' in category_name_lower:
                    fallback_image = fallback_images['camera']
                else:
                    fallback_image = fallback_images['graphics']  # Default fallback
                
                if fallback_image:
                    image_path = media_dir / fallback_image
                    
                    if image_path.exists():
                        try:
                            # Create a unique filename for this product
                            file_extension = image_path.suffix
                            unique_filename = f"{product.slug}-placeholder{file_extension}"
                            
                            # Copy the fallback image
                            with open(image_path, 'rb') as f:
                                django_file = File(f)
                                product.main_image.save(
                                    unique_filename,
                                    django_file,
                                    save=True
                                )
                            
                            # Create ProductImage entry
                            ProductImage.objects.create(
                                product=product,
                                image=product.main_image,
                                image_type='main',
                                alt_text=f"{product.name} - Product Image",
                                caption=f"Image du produit {product.name}",
                                sort_order=1,
                                is_active=True
                            )
                            
                            updated_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Added placeholder image for {product.name}'
                                )
                            )
                            
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'Error adding image for {product.name}: {e}'
                                )
                            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added placeholder images for {updated_count} products'
            )
        )

