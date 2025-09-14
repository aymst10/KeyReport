from django.core.management.base import BaseCommand
from store.models import Product, ProductImage
from django.core.files import File
import os
from pathlib import Path
import shutil

class Command(BaseCommand):
    help = 'Directly assign photos to specific products'

    def handle(self, *args, **options):
        photo_dir = Path('user_photos')
        media_dir = Path('media/products')
        
        # Direct mapping of product names to photo files
        direct_mapping = {
            # Exact product name matches
            'MSI MAG B550 Tomahawk Gaming Motherboard': 'msi-tomahawk-motherboard.jpg',
            'ASUS ROG Strix B550-F Gaming Motherboard': 'asus-rog-strix-motherboard.jpg',
            'Corsair Vengeance LPX 32GB DDR4 RAM': 'corsair-vengeance-ram.jpg',
            'Seagate Barracuda 4TB HDD': 'seagate-barracuda-4tb.jpg',
            'Logitech MX Master 3S Wireless Mouse': 'logitech-mx-master-mouse.jpg',
            'Microsoft Surface Keyboard': 'surface-keyboard.jpg',
            'NVIDIA GeForce RTX 4070 Graphics Card': 'nvidia-rtx-4070-graphics.jpg',
            'AMD Radeon RX 7800 XT Graphics Card': 'amd-rx-7800-graphics.jpg',
            'Samsung 980 PRO 1TB NVMe SSD': 'samsung-980-pro-ssd.jpg',
            'Intel Core i7-12700K Processor': 'intel-i7-12700k-processor.jpg',
            
            # Partial matches for similar products
            'MSI MAG B550 Tomahawk Motherboard': 'msi-tomahawk-motherboard.jpg',
            'ASUS ROG Strix B550-F Gaming Motherboard': 'asus-rog-strix-motherboard.jpg',
            'Corsair Vengeance LPX 32GB DDR4 RAM': 'corsair-vengeance-ram.jpg',
            'Seagate Barracuda 4TB HDD': 'seagate-barracuda-4tb.jpg',
            'Seagate BarraCuda 4TB HDD': 'seagate-barracuda-4tb.jpg',
            'Logitech MX Master 3S Wireless Mouse': 'logitech-mx-master-mouse.jpg',
            'Microsoft Surface Keyboard': 'surface-keyboard.jpg',
            'NVIDIA GeForce RTX 4070 Graphics Card': 'nvidia-rtx-4070-graphics.jpg',
            'AMD Radeon RX 7800 XT Graphics Card': 'amd-rx-7800-graphics.jpg',
            'Samsung 980 PRO 1TB NVMe SSD': 'samsung-980-pro-ssd.jpg',
            'Intel Core i7-12700K Processor': 'intel-i7-12700k-processor.jpg',
            'Western Digital Black SN850 2TB NVMe SSD': 'samsung-980-pro-ssd.jpg',  # Use SSD photo as fallback
            'AMD Ryzen 9 5900X Processor': 'intel-i7-12700k-processor.jpg',  # Use processor photo as fallback
        }
        
        updated_count = 0
        
        for product in Product.objects.all():
            product_name = product.name
            
            # Look for exact match first
            photo_filename = direct_mapping.get(product_name)
            
            # If no exact match, look for partial matches
            if not photo_filename:
                for mapped_name, mapped_photo in direct_mapping.items():
                    if mapped_name.lower() in product_name.lower() or product_name.lower() in mapped_name.lower():
                        photo_filename = mapped_photo
                        break
            
            if photo_filename:
                photo_path = photo_dir / photo_filename
                
                if photo_path.exists():
                    try:
                        # Create a unique filename for this product
                        file_extension = photo_path.suffix
                        unique_filename = f"{product.slug}-direct-{photo_filename}"
                        new_path = media_dir / unique_filename
                        
                        # Copy the photo
                        shutil.copy2(photo_path, new_path)
                        
                        # Update the product's main image
                        with open(new_path, 'rb') as f:
                            django_file = File(f)
                            product.main_image.save(
                                unique_filename,
                                django_file,
                                save=True
                            )
                        
                        # Clear existing gallery images and create new ones
                        product.images.all().delete()
                        
                        # Create ProductImage entry
                        ProductImage.objects.create(
                            product=product,
                            image=product.main_image,
                            image_type='main',
                            alt_text=f"{product.name} - Professional Photo",
                            caption=f"Photo professionnelle de {product.name}",
                            sort_order=1,
                            is_active=True
                        )
                        
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Assigned {photo_filename} to {product.name}'
                            )
                        )
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Error assigning photo for {product.name}: {e}'
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Photo file not found: {photo_filename} for {product.name}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ No photo mapping found for: {product.name}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully assigned photos to {updated_count} products'
            )
        )

