#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_store.settings')
django.setup()

from users.models import CustomUser
from store.models import Product, Order
from support.models import SupportTicket

def show_recent_updates():
    print("🕐 DERNIÈRES MISES À JOUR DE LA BASE DE DONNÉES")
    print("=" * 60)
    
    # Last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    
    # Recent users
    recent_users = CustomUser.objects.filter(date_joined__gte=yesterday).order_by('-date_joined')
    print(f"\n👥 NOUVEAUX UTILISATEURS (24h): {recent_users.count()}")
    print("-" * 40)
    for user in recent_users[:5]:
        print(f"📧 {user.email} - {user.date_joined.strftime('%H:%M:%S')}")
    
    # Recent products
    recent_products = Product.objects.filter(created_at__gte=yesterday).order_by('-created_at')
    print(f"\n🛍️  NOUVEAUX PRODUITS (24h): {recent_products.count()}")
    print("-" * 40)
    for product in recent_products[:5]:
        print(f"📦 {product.name} - ${product.price}")
    
    # Recent orders
    recent_orders = Order.objects.filter(created_at__gte=yesterday).order_by('-created_at')
    print(f"\n📋 NOUVELLES COMMANDES (24h): {recent_orders.count()}")
    print("-" * 40)
    for order in recent_orders[:5]:
        print(f"🛒 #{order.id} - {order.customer.email} - ${order.total_amount}")
    
    # Recent tickets
    recent_tickets = SupportTicket.objects.filter(created_at__gte=yesterday).order_by('-created_at')
    print(f"\n🎫 NOUVEAUX TICKETS (24h): {recent_tickets.count()}")
    print("-" * 40)
    for ticket in recent_tickets[:5]:
        print(f"🎫 {ticket.ticket_number} - {ticket.title}")
    
    # Avatar updates
    users_with_photos = CustomUser.objects.exclude(profile_photo__isnull=True).exclude(profile_photo='')
    print(f"\n🖼️  UTILISATEURS AVEC PHOTOS: {users_with_photos.count()}")
    print("-" * 40)
    for user in users_with_photos:
        print(f"📧 {user.email} - {user.profile_photo}")
    
    print("\n✅ RAPPORT TERMINÉ!")
    print("=" * 60)

if __name__ == '__main__':
    show_recent_updates()
















