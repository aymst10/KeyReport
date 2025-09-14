from django.core.management.base import BaseCommand
from store.models import Product, ProductImage
from django.core.files import File
import os
from pathlib import Path
import shutil

class Command(BaseCommand):
    help = 'Assign user-provided photos to products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--photo-dir',
            type=str,
            default='user_photos',
            help='Directory containing user photos (default: user_photos)'
        )

    def handle(self, *args, **options):
        photo_dir = Path(options['photo_dir'])
        media_dir = Path('media/products')
        
        if not photo_dir.exists():
            self.stdout.write(
                self.style.ERROR(
                    f'Photo directory {photo_dir} does not exist. Please create it and add your photos there.'
                )
            )
            return
        
        # Mapping of product keywords to photo filenames
        photo_mapping = {
            # Storage - HDDs
            'seagate barracuda': ['seagate-barracuda', 'barracuda', 'hdd-seagate'],
            'barracuda': ['seagate-barracuda', 'barracuda', 'hdd-seagate'],
            'hdd': ['seagate-barracuda', 'barracuda', 'hdd-seagate'],
            
            # RAM
            'corsair vengeance lpx': ['corsair-vengeance', 'vengeance-lpx', 'corsair-ram'],
            'vengeance lpx': ['corsair-vengeance', 'vengeance-lpx', 'corsair-ram'],
            'ddr4 ram': ['corsair-vengeance', 'vengeance-lpx', 'corsair-ram'],
            'ram': ['corsair-vengeance', 'vengeance-lpx', 'corsair-ram'],
            
            # Keyboards
            'mechanical keyboard': ['keyboard', 'mechanical-kb'],
            'surface keyboard': ['keyboard', 'surface-kb'],
            'keyboard': ['keyboard', 'mechanical-kb'],
            
            # Mice
            'logitech mx master': ['logitech-mx-master', 'mx-master', 'logitech-mouse'],
            'mx master': ['logitech-mx-master', 'mx-master', 'logitech-mouse'],
            'wireless mouse': ['logitech-mx-master', 'mx-master', 'logitech-mouse'],
            'mouse': ['logitech-mx-master', 'mx-master', 'logitech-mouse'],
            
            # Motherboards
            'msi mag b550 tomahawk': ['msi-b550-tomahawk', 'tomahawk', 'msi-motherboard'],
            'mag b550': ['msi-b550-tomahawk', 'tomahawk', 'msi-motherboard'],
            'asus rog strix b550-f': ['asus-rog-strix', 'rog-strix', 'asus-motherboard'],
            'rog strix b550': ['asus-rog-strix', 'rog-strix', 'asus-motherboard'],
            'motherboard': ['msi-b550-tomahawk', 'asus-rog-strix'],
        }
        
        updated_count = 0
        
        for product in Product.objects.all():
            product_name_lower = product.name.lower()
            
            # Find matching photo
            matching_photo = None
            photo_keywords = []
            
            for key, photo_names in photo_mapping.items():
                if key in product_name_lower:
                    photo_keywords = photo_names
                    break
            
            if photo_keywords:
                # Look for photo files that match the keywords
                for photo_file in photo_dir.iterdir():
                    if photo_file.is_file() and photo_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        photo_name_lower = photo_file.name.lower()
                        
                        # Check if photo name contains any of the keywords
                        if any(keyword in photo_name_lower for keyword in photo_keywords):
                            matching_photo = photo_file
                            break
            
            if matching_photo:
                try:
                    # Create a unique filename for this product
                    file_extension = matching_photo.suffix
                    unique_filename = f"{product.slug}-user-photo{file_extension}"
                    new_path = media_dir / unique_filename
                    
                    # Copy the photo
                    shutil.copy2(matching_photo, new_path)
                    
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
                            f'✓ Assigned {matching_photo.name} to {product.name}'
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
                        f'⚠ No matching photo found for: {product.name}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully assigned user photos to {updated_count} products'
            )
        )
        
        # Show available photos
        available_photos = list(photo_dir.glob('*.jpg')) + list(photo_dir.glob('*.jpeg')) + list(photo_dir.glob('*.png'))
        if available_photos:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Available photos in {photo_dir}:'
                )
            )
            for photo in available_photos:
                self.stdout.write(f'  - {photo.name}')

