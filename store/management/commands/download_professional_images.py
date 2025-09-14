from django.core.management.base import BaseCommand
from store.models import Product, ProductImage
from django.core.files import File
import requests
import os
from pathlib import Path
from urllib.parse import urlparse

class Command(BaseCommand):
    help = 'Download professional product images from URLs'

    def handle(self, *args, **options):
        # Professional product image URLs - high quality images
        professional_images = {
            # Graphics Cards
            'nvidia geforce rtx 4070': 'https://images.nvidia.com/aem-dam/en-zz/Solutions/geforce/ada/rtx-4070/geforce-rtx-4070-product-gallery-full-screen-3840-1.jpg',
            'amd radeon rx 7800 xt': 'https://www.amd.com/system/files/2023-08/AMD-Radeon-RX-7800-XT-Desktop-Graphics-Card-1260x709_0.jpg',
            'rtx 4070': 'https://images.nvidia.com/aem-dam/en-zz/Solutions/geforce/ada/rtx-4070/geforce-rtx-4070-product-gallery-full-screen-3840-1.jpg',
            'rx 7800': 'https://www.amd.com/system/files/2023-08/AMD-Radeon-RX-7800-XT-Desktop-Graphics-Card-1260x709_0.jpg',
            
            # Processors
            'intel core i7-12700k': 'https://www.intel.com/content/dam/products/hero/processor/core/i7-12700k/desktop-gaming-processor-core-i7-12700k-hero-16x9.png.rendition.intel.web.1920.1080.png',
            'amd ryzen 9 5900x': 'https://www.amd.com/system/files/2022-05/AMD-Ryzen-9-5900X-Desktop-Processor-1260x709_0.jpg',
            'i7-12700k': 'https://www.intel.com/content/dam/products/hero/processor/core/i7-12700k/desktop-gaming-processor-core-i7-12700k-hero-16x9.png.rendition.intel.web.1920.1080.png',
            'ryzen 9 5900x': 'https://www.amd.com/system/files/2022-05/AMD-Ryzen-9-5900X-Desktop-Processor-1260x709_0.jpg',
            
            # Motherboards
            'asus rog strix b550-f': 'https://www.asus.com/media/global/products/8zJ6nq6QZ7zW6Y9R/P_setting_000_1_90_end_500.png',
            'msi mag b550 tomahawk': 'https://asset.msi.com/resize/image/global/product/product_5_20200316161049_5e6f6b8b2b4a5.png62405b38c58fe0f07fcef2367',
            'rog strix b550': 'https://www.asus.com/media/global/products/8zJ6nq6QZ7zW6Y9R/P_setting_000_1_90_end_500.png',
            'mag b550': 'https://asset.msi.com/resize/image/global/product/product_5_20200316161049_5e6f6b8b2b4a5.png62405b38c58fe0f07fcef2367',
            
            # RAM
            'corsair vengeance lpx': 'https://www.corsair.com/medias/sys_master/images/images/h7e/hc0/9112639602718/-CMK32GX4M2D3200C16-Gallery-Vengeance-LPX-01.png',
            'vengeance lpx': 'https://www.corsair.com/medias/sys_master/images/images/h7e/hc0/9112639602718/-CMK32GX4M2D3200C16-Gallery-Vengeance-LPX-01.png',
            'ddr4 ram': 'https://www.corsair.com/medias/sys_master/images/images/h7e/hc0/9112639602718/-CMK32GX4M2D3200C16-Gallery-Vengeance-LPX-01.png',
            
            # Storage - SSDs
            'samsung 980 pro': 'https://images.samsung.com/is/image/samsung/p6pim/fr/980-pro-pcie-4-0-nvme-m-2-ssd-1tb-mz-v8p1t0bw-frontblack-251012861?$650_519_PNG$',
            'wd black sn850': 'https://www.westerndigital.com/content/dam/store/en-us/assets/products/internal-storage/wd-black-sn850-nvme-ssd/product/gallery/wd-black-sn850-nvme-ssd-1tb-front-right.png',
            '980 pro': 'https://images.samsung.com/is/image/samsung/p6pim/fr/980-pro-pcie-4-0-nvme-m-2-ssd-1tb-mz-v8p1t0bw-frontblack-251012861?$650_519_PNG$',
            'sn850': 'https://www.westerndigital.com/content/dam/store/en-us/assets/products/internal-storage/wd-black-sn850-nvme-ssd/product/gallery/wd-black-sn850-nvme-ssd-1tb-front-right.png',
            
            # Storage - HDDs
            'seagate barracuda': 'https://www.seagate.com/www-content/product-content/barracuda-fam/barracuda-new/en-us/_shared/images/Barracuda-2TB-front.png',
            'barracuda': 'https://www.seagate.com/www-content/product-content/barracuda-fam/barracuda-new/en-us/_shared/images/Barracuda-2TB-front.png',
            
            # Monitors
            'samsung 4k monitor': 'https://images.samsung.com/is/image/samsung/p6pim/fr/ue32j590uuxen/gallery/fr-uhd-4k-monitor-ue32j590uuxen-ue32j590uuxen-251013835?$650_519_PNG$',
            'dell p2422h': 'https://i.dell.com/sites/csdocuments/Business_Content_Manuals/en/documents/dell-p2422h-monitor.png',
            'lg ultrawide': 'https://www.lg.com/us/images/monitors/md05801646/gallery/medium01.jpg',
            'asus rog strix xg27uq': 'https://www.asus.com/media/global/products/6Z9N2k3Q4Q5Q5Q5Q/P_setting_000_1_90_end_500.png',
            '4k monitor': 'https://images.samsung.com/is/image/samsung/p6pim/fr/ue32j590uuxen/gallery/fr-uhd-4k-monitor-ue32j590uuxen-ue32j590uuxen-251013835?$650_519_PNG$',
            'business monitor': 'https://i.dell.com/sites/csdocuments/Business_Content_Manuals/en/documents/dell-p2422h-monitor.png',
            'ultrawide': 'https://www.lg.com/us/images/monitors/md05801646/gallery/medium01.jpg',
            
            # Keyboards
            'steelseries apex pro': 'https://steelseries.com/img/products/apex-pro-tkl/apex-pro-tkl-main.png',
            'mechanical keyboard': 'https://steelseries.com/img/products/apex-pro-tkl/apex-pro-tkl-main.png',
            'surface keyboard': 'https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE4E3rJ?ver=1c95',
            
            # Mice
            'razer deathadder': 'https://assets2.razerzone.com/images/pnx.assets/8a0c667cfd2c98f8b5e2d8b5e2d8b5e2/razer-deathadder-v3-pro-gallery-01.png',
            'wireless mouse': 'https://www.logitech.com/content/dam/logitech/en/products/mice/mx-master-3s/gallery/mx-master-3s-mouse-top-view-grey.png',
            'mx master': 'https://www.logitech.com/content/dam/logitech/en/products/mice/mx-master-3s/gallery/mx-master-3s-mouse-top-view-grey.png',
            
            # Headsets
            'hyperx cloud alpha': 'https://www.hyperxgaming.com/content/dam/hyperx/en-us/headsets/cloud-alpha-s/cloud-alpha-s-gallery-01.png',
            'gaming headset': 'https://www.hyperxgaming.com/content/dam/hyperx/en-us/headsets/cloud-alpha-s/cloud-alpha-s-gallery-01.png',
            
            # Printers
            'canon pixma g6020': 'https://www.canon-europe.com/products/printers/inkjet/pixma-g-series/pixma-g6020/images/pixma-g6020_hero.png',
            'hp laserjet pro': 'https://h20195.www2.hp.com/v2/GetImage.aspx?mediaId=15000',
            'pixma g6020': 'https://www.canon-europe.com/products/printers/inkjet/pixma-g-series/pixma-g6020/images/pixma-g6020_hero.png',
            'laserjet pro': 'https://h20195.www2.hp.com/v2/GetImage.aspx?mediaId=15000',
        }
        
        updated_count = 0
        
        for product in Product.objects.all():
            product_name_lower = product.name.lower()
            
            # Find matching professional image URL
            image_url = None
            for key, url in professional_images.items():
                if key in product_name_lower:
                    image_url = url
                    break
            
            if image_url:
                try:
                    # Download the image
                    response = requests.get(image_url, timeout=30)
                    response.raise_for_status()
                    
                    # Create filename from URL
                    parsed_url = urlparse(image_url)
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
                            f'Downloaded professional image for {product.name}'
                        )
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error downloading image for {product.name}: {e}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'No professional image URL found for: {product.name}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully downloaded professional images for {updated_count} products'
            )
        )

