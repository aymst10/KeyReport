"""
Django management command to assign professional images to categories.
This command downloads and assigns appropriate images based on category names.
"""

import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Category


class Command(BaseCommand):
    help = 'Assign professional images to categories based on their names'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually downloading images',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Category image mappings with professional Unsplash URLs
        category_images = {
            'business intelligence': {
                'url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=400&fit=crop&crop=center',
                'keywords': ['analytics', 'dashboard', 'data visualization', 'business intelligence']
            },
            'computer accessories': {
                'url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&h=400&fit=crop&crop=center',
                'keywords': ['computer', 'accessories', 'hardware', 'peripherals']
            },
            'data processing': {
                'url': 'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=800&h=400&fit=crop&crop=center',
                'keywords': ['data', 'processing', 'server', 'computing']
            },
            'networking': {
                'url': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=400&fit=crop&crop=center',
                'keywords': ['network', 'routing', 'switching', 'connectivity']
            },
            'security': {
                'url': 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&h=400&fit=crop&crop=center',
                'keywords': ['security', 'cybersecurity', 'protection', 'firewall']
            },
            'storage': {
                'url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=400&fit=crop&crop=center',
                'keywords': ['storage', 'server', 'data center', 'hardware']
            },
            'software': {
                'url': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&h=400&fit=crop&crop=center',
                'keywords': ['software', 'development', 'coding', 'programming']
            },
            'cloud computing': {
                'url': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=400&fit=crop&crop=center',
                'keywords': ['cloud', 'computing', 'server', 'technology']
            },
            'mobile devices': {
                'url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&h=400&fit=crop&crop=center',
                'keywords': ['mobile', 'smartphone', 'tablet', 'device']
            },
            'monitoring': {
                'url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=400&fit=crop&crop=center',
                'keywords': ['monitoring', 'analytics', 'dashboard', 'metrics']
            },
            'printers': {
                'url': 'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&h=400&fit=crop&crop=center',
                'keywords': ['printer', 'printing', 'office equipment']
            },
            'scanners': {
                'url': 'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&h=400&fit=crop&crop=center',
                'keywords': ['scanner', 'scanning', 'document']
            },
            'reporting tools': {
                'url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=400&fit=crop&crop=center',
                'keywords': ['reporting', 'analytics', 'dashboard']
            },
            'test category': {
                'url': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=400&fit=crop&crop=center',
                'keywords': ['test', 'category', 'general']
            }
        }

        categories = Category.objects.filter(is_active=True)
        
        if not categories.exists():
            self.stdout.write(
                self.style.WARNING('No active categories found in the database.')
            )
            return

        self.stdout.write(f'Found {categories.count()} active categories.')
        
        for category in categories:
            category_name_lower = category.name.lower()
            
            # Find matching image
            image_info = None
            for key, info in category_images.items():
                if key in category_name_lower or any(kw in category_name_lower for kw in info['keywords']):
                    image_info = info
                    break
            
            if not image_info:
                # Default image for unmatched categories
                image_info = {
                    'url': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=400&fit=crop&crop=center',
                    'keywords': ['technology', 'default', 'general']
                }
            
            if dry_run:
                self.stdout.write(
                    f'[DRY RUN] Would assign image to "{category.name}": {image_info["url"]}'
                )
                continue
            
            try:
                # Download image
                response = requests.get(image_info['url'], timeout=30)
                response.raise_for_status()
                
                # Create filename
                filename = f"{category.slug}_header.jpg"
                
                # Save image to category
                image_file = ContentFile(response.content, name=filename)
                category.image.save(filename, image_file, save=True)
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Assigned image to "{category.name}"')
                )
                
            except requests.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to download image for "{category.name}": {e}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing "{category.name}": {e}')
                )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS('\n✓ Category image assignment completed!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n[DRY RUN] No images were actually downloaded.')
            )
