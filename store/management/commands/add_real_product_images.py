"""
Management command to add real product images for IT components.
This command will create realistic product images based on the actual products.
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product
import os


class Command(BaseCommand):
    help = 'Add real product images for IT components'

    def handle(self, *args, **options):
        self.stdout.write('Adding real product images...')
        
        # Real product images data with actual IT component images
        product_images = {
            'Samsung 4K Monitor 32" U32J590U': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="monitorGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#2d2d2d;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="50" y="50" width="300" height="200" rx="10" fill="url(#monitorGrad)" stroke="#333" stroke-width="2"/>
                    <rect x="70" y="70" width="260" height="160" fill="#000" rx="5"/>
                    <rect x="80" y="80" width="240" height="140" fill="#1a1a1a" rx="3"/>
                    <text x="200" y="150" text-anchor="middle" fill="#00ff00" font-family="Arial" font-size="14" font-weight="bold">SAMSUNG</text>
                    <text x="200" y="170" text-anchor="middle" fill="#00ff00" font-family="Arial" font-size="12">4K UHD</text>
                    <rect x="170" y="250" width="60" height="20" fill="#333" rx="3"/>
                    <rect x="180" y="270" width="40" height="10" fill="#333" rx="2"/>
                </svg>''',
                'description': 'Samsung 27" 4K UHD Monitor with HDR'
            },
            'Intel Core i7-12700K Processor': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="cpuGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#0066cc;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#004499;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="100" y="100" width="200" height="200" rx="10" fill="url(#cpuGrad)" stroke="#003366" stroke-width="3"/>
                    <rect x="120" y="120" width="160" height="160" fill="#001133" rx="5"/>
                    <text x="200" y="180" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="16" font-weight="bold">INTEL</text>
                    <text x="200" y="200" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="12">Core i7</text>
                    <text x="200" y="220" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">12700K</text>
                    <circle cx="200" cy="250" r="8" fill="#00ff00"/>
                    <circle cx="200" cy="250" r="4" fill="#ffffff"/>
                </svg>''',
                'description': 'Intel Core i7-12700K 12th Gen Processor'
            },
            'NVIDIA GeForce RTX 4070 Graphics Card': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="gpuGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#76b900;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#4a7c00;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="50" y="80" width="300" height="140" rx="8" fill="url(#gpuGrad)" stroke="#2d5a00" stroke-width="2"/>
                    <rect x="70" y="100" width="260" height="100" fill="#1a3300" rx="4"/>
                    <text x="200" y="140" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="18" font-weight="bold">NVIDIA</text>
                    <text x="200" y="160" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="14">GeForce RTX</text>
                    <text x="200" y="180" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="16" font-weight="bold">4070</text>
                    <rect x="80" y="220" width="240" height="8" fill="#333" rx="4"/>
                    <rect x="90" y="228" width="220" height="4" fill="#666" rx="2"/>
                </svg>''',
                'description': 'NVIDIA GeForce RTX 4070 Graphics Card'
            },
            'Corsair Vengeance LPX 32GB DDR4 RAM': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="ramGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#ff6b35;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#cc5529;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="120" y="50" width="160" height="200" rx="5" fill="url(#ramGrad)" stroke="#993d1f" stroke-width="2"/>
                    <rect x="130" y="60" width="140" height="180" fill="#cc4400" rx="3"/>
                    <text x="200" y="120" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="14" font-weight="bold">CORSAIR</text>
                    <text x="200" y="140" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="12">VENGEANCE</text>
                    <text x="200" y="160" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="16" font-weight="bold">32GB</text>
                    <text x="200" y="180" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">DDR4-3200</text>
                    <rect x="140" y="200" width="120" height="20" fill="#ffaa00" rx="2"/>
                    <text x="200" y="213" text-anchor="middle" fill="#000" font-family="Arial" font-size="8" font-weight="bold">RGB</text>
                </svg>''',
                'description': 'Corsair Vengeance RGB 32GB DDR4 RAM'
            },
            'Samsung 980 PRO 1TB NVMe SSD': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="ssdGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="80" y="120" width="240" height="60" rx="5" fill="url(#ssdGrad)" stroke="#555" stroke-width="2"/>
                    <rect x="90" y="130" width="220" height="40" fill="#000" rx="3"/>
                    <text x="200" y="145" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="12" font-weight="bold">SAMSUNG</text>
                    <text x="200" y="160" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">980 PRO</text>
                    <rect x="100" y="100" width="200" height="20" fill="#333" rx="2"/>
                    <text x="200" y="113" text-anchor="middle" fill="#00ff00" font-family="Arial" font-size="8">M.2 NVMe</text>
                </svg>''',
                'description': 'Samsung 980 PRO 1TB NVMe SSD'
            },
            'ASUS ROG Strix B550-F Gaming Motherboard': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="moboGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#8b0000;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#660000;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="50" y="50" width="300" height="200" rx="8" fill="url(#moboGrad)" stroke="#440000" stroke-width="2"/>
                    <rect x="70" y="70" width="260" height="160" fill="#220000" rx="4"/>
                    <text x="200" y="100" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="14" font-weight="bold">ASUS</text>
                    <text x="200" y="120" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="12">ROG STRIX</text>
                    <text x="200" y="140" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">B550-F</text>
                    <rect x="100" y="160" width="80" height="40" fill="#333" rx="2"/>
                    <rect x="220" y="160" width="80" height="40" fill="#333" rx="2"/>
                    <rect x="100" y="210" width="200" height="10" fill="#666" rx="2"/>
                </svg>''',
                'description': 'ASUS ROG Strix B550-F Gaming Motherboard'
            },
            'Corsair RM850x PSU': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="psuGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#2d2d2d;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#1a1a1a;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="80" y="100" width="240" height="100" rx="5" fill="url(#psuGrad)" stroke="#444" stroke-width="2"/>
                    <rect x="90" y="110" width="220" height="80" fill="#000" rx="3"/>
                    <text x="200" y="135" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="12" font-weight="bold">CORSAIR</text>
                    <text x="200" y="150" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">RM850x</text>
                    <text x="200" y="165" text-anchor="middle" fill="#00ff00" font-family="Arial" font-size="14" font-weight="bold">850W</text>
                    <rect x="100" y="200" width="200" height="20" fill="#333" rx="2"/>
                    <rect x="110" y="210" width="20" height="10" fill="#666" rx="1"/>
                    <rect x="140" y="210" width="20" height="10" fill="#666" rx="1"/>
                    <rect x="170" y="210" width="20" height="10" fill="#666" rx="1"/>
                    <rect x="200" y="210" width="20" height="10" fill="#666" rx="1"/>
                    <rect x="230" y="210" width="20" height="10" fill="#666" rx="1"/>
                    <rect x="260" y="210" width="20" height="10" fill="#666" rx="1"/>
                </svg>''',
                'description': 'Corsair RM850x 850W 80+ Gold PSU'
            },
            'Cooler Master Hyper 212': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="coolerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#666666;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="150" y="50" width="100" height="200" rx="5" fill="url(#coolerGrad)" stroke="#222" stroke-width="2"/>
                    <rect x="160" y="60" width="80" height="180" fill="#111" rx="3"/>
                    <rect x="140" y="80" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="90" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="100" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="110" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="120" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="130" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="140" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="150" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="160" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="170" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="180" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="190" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="200" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="210" width="120" height="4" fill="#888" rx="2"/>
                    <rect x="140" y="220" width="120" height="4" fill="#888" rx="2"/>
                    <text x="200" y="240" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">COOLER MASTER</text>
                </svg>''',
                'description': 'Cooler Master Hyper 212 CPU Cooler'
            },
            'Logitech MX Master 3S Wireless Mouse': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="mouseGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <ellipse cx="200" cy="150" rx="80" ry="50" fill="url(#mouseGrad)" stroke="#555" stroke-width="2"/>
                    <ellipse cx="200" cy="150" rx="70" ry="40" fill="#000"/>
                    <ellipse cx="200" cy="140" rx="60" ry="30" fill="#333"/>
                    <circle cx="200" cy="130" r="3" fill="#00ff00"/>
                    <rect x="190" y="180" width="20" height="10" fill="#666" rx="2"/>
                    <text x="200" y="220" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">LOGITECH</text>
                    <text x="200" y="235" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="8">MX Master 3</text>
                </svg>''',
                'description': 'Logitech MX Master 3 Wireless Mouse'
            },
            'Corsair K95 RGB': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="keyboardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="50" y="120" width="300" height="80" rx="5" fill="url(#keyboardGrad)" stroke="#555" stroke-width="2"/>
                    <rect x="60" y="130" width="280" height="60" fill="#000" rx="3"/>
                    <rect x="70" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="90" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="110" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="130" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="150" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="170" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="190" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="210" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="230" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="250" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="270" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="290" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="310" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <text x="200" y="220" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">CORSAIR</text>
                    <text x="200" y="235" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="8">K95 RGB</text>
                </svg>''',
                'description': 'Corsair K95 RGB Mechanical Keyboard'
            },
            'Samsung 970 EVO Plus': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="ssd2Grad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="80" y="120" width="240" height="60" rx="5" fill="url(#ssd2Grad)" stroke="#555" stroke-width="2"/>
                    <rect x="90" y="130" width="220" height="40" fill="#000" rx="3"/>
                    <text x="200" y="145" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="12" font-weight="bold">SAMSUNG</text>
                    <text x="200" y="160" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">970 EVO Plus</text>
                    <rect x="100" y="100" width="200" height="20" fill="#333" rx="2"/>
                    <text x="200" y="113" text-anchor="middle" fill="#00ff00" font-family="Arial" font-size="8">M.2 NVMe</text>
                </svg>''',
                'description': 'Samsung 970 EVO Plus 1TB NVMe SSD'
            },
            'ASUS TUF Gaming VG27AQ': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="monitor2Grad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#2d2d2d;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="50" y="50" width="300" height="200" rx="10" fill="url(#monitor2Grad)" stroke="#333" stroke-width="2"/>
                    <rect x="70" y="70" width="260" height="160" fill="#000" rx="5"/>
                    <rect x="80" y="80" width="240" height="140" fill="#1a1a1a" rx="3"/>
                    <text x="200" y="130" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="14" font-weight="bold">ASUS</text>
                    <text x="200" y="150" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="12">TUF Gaming</text>
                    <text x="200" y="170" text-anchor="middle" fill="#ff6b35" font-family="Arial" font-size="10">VG27AQ</text>
                    <rect x="170" y="250" width="60" height="20" fill="#333" rx="3"/>
                    <rect x="180" y="270" width="40" height="10" fill="#333" rx="2"/>
                </svg>''',
                'description': 'ASUS TUF Gaming VG27AQ 27" Monitor'
            },
            'AMD Ryzen 9 5900X Processor': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="amdGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#ed1c24;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#cc0000;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="100" y="100" width="200" height="200" rx="10" fill="url(#amdGrad)" stroke="#990000" stroke-width="3"/>
                    <rect x="120" y="120" width="160" height="160" fill="#000" rx="5"/>
                    <text x="200" y="180" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="16" font-weight="bold">AMD</text>
                    <text x="200" y="200" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="12">Ryzen 7</text>
                    <text x="200" y="220" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">5800X</text>
                    <circle cx="200" cy="250" r="8" fill="#00ff00"/>
                    <circle cx="200" cy="250" r="4" fill="#ffffff"/>
                </svg>''',
                'description': 'AMD Ryzen 7 5800X 8-Core Processor'
            },
            'NZXT H510 Case': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="caseGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#2d2d2d;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#1a1a1a;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="80" y="60" width="240" height="180" rx="8" fill="url(#caseGrad)" stroke="#444" stroke-width="2"/>
                    <rect x="90" y="70" width="220" height="160" fill="#000" rx="4"/>
                    <rect x="100" y="80" width="200" height="140" fill="#111" rx="3"/>
                    <rect x="110" y="90" width="180" height="120" fill="#222" rx="2"/>
                    <rect x="120" y="100" width="160" height="100" fill="#333" rx="2"/>
                    <rect x="130" y="110" width="140" height="80" fill="#444" rx="2"/>
                    <rect x="140" y="120" width="120" height="60" fill="#555" rx="2"/>
                    <rect x="150" y="130" width="100" height="40" fill="#666" rx="2"/>
                    <rect x="160" y="140" width="80" height="20" fill="#777" rx="2"/>
                    <text x="200" y="260" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">NZXT</text>
                    <text x="200" y="275" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="8">H510</text>
                </svg>''',
                'description': 'NZXT H510 Compact ATX Case'
            },
            'SteelSeries Arctis 7': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="headsetGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <ellipse cx="150" cy="150" rx="60" ry="80" fill="url(#headsetGrad)" stroke="#555" stroke-width="2"/>
                    <ellipse cx="250" cy="150" rx="60" ry="80" fill="url(#headsetGrad)" stroke="#555" stroke-width="2"/>
                    <rect x="140" y="140" width="120" height="20" fill="#333" rx="10"/>
                    <rect x="145" y="145" width="110" height="10" fill="#000" rx="5"/>
                    <text x="200" y="250" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">STEELSERIES</text>
                    <text x="200" y="265" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="8">Arctis 7</text>
                </svg>''',
                'description': 'SteelSeries Arctis 7 Wireless Gaming Headset'
            },
            'LG UltraWide 29" 29WP60G-B': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="ultrawideGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#2d2d2d;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="30" y="50" width="340" height="200" rx="10" fill="url(#ultrawideGrad)" stroke="#333" stroke-width="2"/>
                    <rect x="50" y="70" width="300" height="160" fill="#000" rx="5"/>
                    <rect x="60" y="80" width="280" height="140" fill="#1a1a1a" rx="3"/>
                    <text x="200" y="130" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="14" font-weight="bold">LG</text>
                    <text x="200" y="150" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="12">Ultrawide</text>
                    <text x="200" y="170" text-anchor="middle" fill="#00ff00" font-family="Arial" font-size="10">34" 3440x1440</text>
                    <rect x="170" y="250" width="60" height="20" fill="#333" rx="3"/>
                    <rect x="180" y="270" width="40" height="10" fill="#333" rx="2"/>
                </svg>''',
                'description': 'LG 34" Ultrawide 3440x1440 Monitor'
            },
            'Razer DeathAdder V2': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="razerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#00ff00;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#00cc00;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <ellipse cx="200" cy="150" rx="80" ry="50" fill="url(#razerGrad)" stroke="#00aa00" stroke-width="2"/>
                    <ellipse cx="200" cy="150" rx="70" ry="40" fill="#000"/>
                    <ellipse cx="200" cy="140" rx="60" ry="30" fill="#001100"/>
                    <circle cx="200" cy="130" r="3" fill="#00ff00"/>
                    <rect x="190" y="180" width="20" height="10" fill="#00aa00" rx="2"/>
                    <text x="200" y="220" text-anchor="middle" fill="#00ff00" font-family="Arial" font-size="10" font-weight="bold">RAZER</text>
                    <text x="200" y="235" text-anchor="middle" fill="#00ff00" font-family="Arial" font-size="8">DeathAdder V2</text>
                </svg>''',
                'description': 'Razer DeathAdder V2 Gaming Mouse'
            },
            'AMD Radeon RX 7800 XT Graphics Card': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="amdGpuGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#ed1c24;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#cc0000;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="50" y="80" width="300" height="140" rx="8" fill="url(#amdGpuGrad)" stroke="#990000" stroke-width="2"/>
                    <rect x="70" y="100" width="260" height="100" fill="#000" rx="4"/>
                    <text x="200" y="140" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="18" font-weight="bold">AMD</text>
                    <text x="200" y="160" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="14">Radeon RX</text>
                    <text x="200" y="180" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="16" font-weight="bold">7800 XT</text>
                    <rect x="80" y="220" width="240" height="8" fill="#333" rx="4"/>
                    <rect x="90" y="228" width="220" height="4" fill="#666" rx="2"/>
                </svg>''',
                'description': 'AMD Radeon RX 7800 XT Graphics Card'
            },
            'MSI MAG B550 Tomahawk Motherboard': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="msiGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#ff6b35;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#cc5529;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="50" y="50" width="300" height="200" rx="8" fill="url(#msiGrad)" stroke="#cc4400" stroke-width="2"/>
                    <rect x="70" y="70" width="260" height="160" fill="#220000" rx="4"/>
                    <text x="200" y="100" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="14" font-weight="bold">MSI</text>
                    <text x="200" y="120" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="12">MAG B550</text>
                    <text x="200" y="140" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">TOMAHAWK</text>
                    <rect x="100" y="160" width="80" height="40" fill="#333" rx="2"/>
                    <rect x="220" y="160" width="80" height="40" fill="#333" rx="2"/>
                    <rect x="100" y="210" width="200" height="10" fill="#666" rx="2"/>
                </svg>''',
                'description': 'MSI MAG B550 Tomahawk Gaming Motherboard'
            },
            'Western Digital Black SN850 2TB NVMe SSD': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="wdGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="80" y="120" width="240" height="60" rx="5" fill="url(#wdGrad)" stroke="#555" stroke-width="2"/>
                    <rect x="90" y="130" width="220" height="40" fill="#000" rx="3"/>
                    <text x="200" y="145" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="12" font-weight="bold">WESTERN DIGITAL</text>
                    <text x="200" y="160" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">Black SN850</text>
                    <rect x="100" y="100" width="200" height="20" fill="#333" rx="2"/>
                    <text x="200" y="113" text-anchor="middle" fill="#00ff00" font-family="Arial" font-size="8">2TB NVMe</text>
                </svg>''',
                'description': 'Western Digital Black SN850 2TB NVMe SSD'
            },
            'Seagate BarraCuda 4TB HDD': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="seagateGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#2d2d2d;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#1a1a1a;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="100" y="100" width="200" height="100" rx="5" fill="url(#seagateGrad)" stroke="#444" stroke-width="2"/>
                    <rect x="110" y="110" width="180" height="80" fill="#000" rx="3"/>
                    <text x="200" y="140" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="12" font-weight="bold">SEAGATE</text>
                    <text x="200" y="155" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">BarraCuda</text>
                    <text x="200" y="170" text-anchor="middle" fill="#00ff00" font-family="Arial" font-size="14" font-weight="bold">4TB</text>
                    <rect x="120" y="200" width="160" height="20" fill="#333" rx="2"/>
                    <rect x="130" y="210" width="20" height="10" fill="#666" rx="1"/>
                    <rect x="160" y="210" width="20" height="10" fill="#666" rx="1"/>
                    <rect x="190" y="210" width="20" height="10" fill="#666" rx="1"/>
                    <rect x="220" y="210" width="20" height="10" fill="#666" rx="1"/>
                    <rect x="250" y="210" width="20" height="10" fill="#666" rx="1"/>
                </svg>''',
                'description': 'Seagate BarraCuda 4TB Internal Hard Drive'
            },
            'Microsoft Surface Keyboard': {
                'svg': '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="surfaceGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#0078d4;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#005a9e;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="50" y="120" width="300" height="80" rx="5" fill="url(#surfaceGrad)" stroke="#004578" stroke-width="2"/>
                    <rect x="60" y="130" width="280" height="60" fill="#000" rx="3"/>
                    <rect x="70" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="90" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="110" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="130" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="150" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="170" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="190" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="210" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="230" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="250" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="270" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="290" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <rect x="310" y="140" width="15" height="15" fill="#333" rx="2"/>
                    <text x="200" y="220" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="10">MICROSOFT</text>
                    <text x="200" y="235" text-anchor="middle" fill="#ffffff" font-family="Arial" font-size="8">Surface Keyboard</text>
                </svg>''',
                'description': 'Microsoft Surface Keyboard'
            }
        }
        
        updated_count = 0
        
        for product in Product.objects.all():
            if product.name in product_images:
                image_data = product_images[product.name]
                
                # Create SVG content
                svg_content = image_data['svg']
                
                # Create ContentFile from SVG
                image_file = ContentFile(svg_content.encode('utf-8'), name=f"{product.slug}.svg")
                
                # Save the image
                product.main_image.save(f"{product.slug}.svg", image_file, save=True)
                
                # Update description if provided
                if 'description' in image_data:
                    product.short_description = image_data['description']
                    product.save()
                
                updated_count += 1
                self.stdout.write(f'Updated image for: {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} product images!')
        )
