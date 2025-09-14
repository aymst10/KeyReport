from django.core.management.base import BaseCommand
from store.models import Product, ProductImage
from django.core.files import File
import requests
import os
from pathlib import Path
from urllib.parse import urlparse

class Command(BaseCommand):
    help = 'Add reliable product images using better sources'

    def handle(self, *args, **options):
        # More reliable image sources - using publicly accessible images
        reliable_images = {
            # Graphics Cards - Using Unsplash and other reliable sources
            'nvidia geforce rtx 4070': 'https://images.unsplash.com/photo-1591488320449-011701bb6704?w=800&h=600&fit=crop',
            'amd radeon rx 7800 xt': 'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop',
            'rtx 4070': 'https://images.unsplash.com/photo-1591488320449-011701bb6704?w=800&h=600&fit=crop',
            'rx 7800': 'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop',
            
            # Processors
            'intel core i7-12700k': 'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800&h=600&fit=crop',
            'amd ryzen 9 5900x': 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=800&h=600&fit=crop',
            'i7-12700k': 'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800&h=600&fit=crop',
            'ryzen 9 5900x': 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=800&h=600&fit=crop',
            
            # Motherboards
            'asus rog strix b550-f': 'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800&h=600&fit=crop',
            'msi mag b550 tomahawk': 'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800&h=600&fit=crop',
            'rog strix b550': 'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800&h=600&fit=crop',
            'mag b550': 'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800&h=600&fit=crop',
            
            # RAM
            'corsair vengeance lpx': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop',
            'vengeance lpx': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop',
            'ddr4 ram': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop',
            
            # Storage - SSDs
            'samsung 980 pro': 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=800&h=600&fit=crop',
            'wd black sn850': 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=800&h=600&fit=crop',
            '980 pro': 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=800&h=600&fit=crop',
            'sn850': 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=800&h=600&fit=crop',
            
            # Storage - HDDs
            'seagate barracuda': 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=800&h=600&fit=crop',
            'barracuda': 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=800&h=600&fit=crop',
            
            # Monitors
            'samsung 4k monitor': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop',
            'dell p2422h': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop',
            'lg ultrawide': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop',
            'asus rog strix xg27uq': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop',
            '4k monitor': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop',
            'business monitor': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop',
            'ultrawide': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop',
            
            # Keyboards
            'steelseries apex pro': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&h=600&fit=crop',
            'mechanical keyboard': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&h=600&fit=crop',
            'surface keyboard': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&h=600&fit=crop',
            
            # Mice
            'razer deathadder': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&h=600&fit=crop',
            'wireless mouse': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&h=600&fit=crop',
            'mx master': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&h=600&fit=crop',
            
            # Headsets
            'hyperx cloud alpha': 'https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=800&h=600&fit=crop',
            'gaming headset': 'https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=800&h=600&fit=crop',
            
            # Printers
            'canon pixma g6020': 'https://images.unsplash.com/photo-1587560699334-cc4ff634909a?w=800&h=600&fit=crop',
            'hp laserjet pro': 'https://images.unsplash.com/photo-1587560699334-cc4ff634909a?w=800&h=600&fit=crop',
            'pixma g6020': 'https://images.unsplash.com/photo-1587560699334-cc4ff634909a?w=800&h=600&fit=crop',
            'laserjet pro': 'https://images.unsplash.com/photo-1587560699334-cc4ff634909a?w=800&h=600&fit=crop',
            
            # Cameras
            'unifi protect': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop',
            'security camera': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop',
        }
        
        updated_count = 0
        
        for product in Product.objects.all():
            product_name_lower = product.name.lower()
            
            # Find matching image URL
            image_url = None
            for key, url in reliable_images.items():
                if key in product_name_lower:
                    image_url = url
                    break
            
            if image_url:
                try:
                    # Download the image with proper headers
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(image_url, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    # Create filename
                    filename = f"{product.slug}-professional.jpg"
                    
                    # Save the image
                    from django.core.files.base import ContentFile
                    image_file = ContentFile(response.content)
                    
                    # Update main image
                    product.main_image.save(
                        filename,
                        image_file,
                        save=True
                    )
                    
                    # Clear existing gallery images
                    product.images.all().delete()
                    
                    # Create ProductImage entry
                    ProductImage.objects.create(
                        product=product,
                        image=product.main_image,
                        image_type='main',
                        alt_text=f"{product.name} - Professional Image",
                        caption=f"Image professionnelle de {product.name}",
                        sort_order=1,
                        is_active=True
                    )
                    
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated image for {product.name}'
                        )
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error updating image for {product.name}: {e}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'No image URL found for: {product.name}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated images for {updated_count} products'
            )
        )

