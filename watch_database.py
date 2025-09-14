#!/usr/bin/env python
import os
import sys
import django
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_store.settings')
django.setup()

from users.models import CustomUser
from store.models import Product, Order
from support.models import SupportTicket

def watch_database_changes():
    print("🔍 SURVEILLANCE DE LA BASE DE DONNÉES EN TEMPS RÉEL")
    print("=" * 60)
    print("Appuyez sur Ctrl+C pour arrêter")
    print("=" * 60)
    
    # Initial counts
    last_user_count = CustomUser.objects.count()
    last_product_count = Product.objects.count()
    last_order_count = Order.objects.count()
    last_ticket_count = SupportTicket.objects.count()
    
    print(f"📊 État initial:")
    print(f"   👥 Utilisateurs: {last_user_count}")
    print(f"   🛍️  Produits: {last_product_count}")
    print(f"   📋 Commandes: {last_order_count}")
    print(f"   🎫 Tickets: {last_ticket_count}")
    print("-" * 60)
    
    try:
        while True:
            time.sleep(5)  # Check every 5 seconds
            
            # Current counts
            current_user_count = CustomUser.objects.count()
            current_product_count = Product.objects.count()
            current_order_count = Order.objects.count()
            current_ticket_count = SupportTicket.objects.count()
            
            # Check for changes
            changes = []
            if current_user_count != last_user_count:
                changes.append(f"👥 Utilisateurs: {last_user_count} → {current_user_count}")
                last_user_count = current_user_count
            
            if current_product_count != last_product_count:
                changes.append(f"🛍️  Produits: {last_product_count} → {current_product_count}")
                last_product_count = current_product_count
            
            if current_order_count != last_order_count:
                changes.append(f"📋 Commandes: {last_order_count} → {current_order_count}")
                last_order_count = current_order_count
            
            if current_ticket_count != last_ticket_count:
                changes.append(f"🎫 Tickets: {last_ticket_count} → {current_ticket_count}")
                last_ticket_count = current_ticket_count
            
            # Show changes
            if changes:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"🕐 {timestamp} - CHANGEMENTS DÉTECTÉS:")
                for change in changes:
                    print(f"   ✅ {change}")
                print("-" * 60)
            
    except KeyboardInterrupt:
        print("\n🛑 Surveillance arrêtée par l'utilisateur")
        print("=" * 60)

if __name__ == '__main__':
    watch_database_changes()
















