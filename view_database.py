#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_store.settings')
django.setup()

from users.models import CustomUser
from store.models import Product, Order, Payment
from support.models import SupportTicket, ServiceRequest

def show_database_updates():
    print("=" * 60)
    print("🔍 MISE À JOURS DE LA BASE DE DONNÉES")
    print("=" * 60)
    
    # Users
    print("\n👥 UTILISATEURS:")
    print("-" * 30)
    users = CustomUser.objects.all()
    for user in users:
        print(f"📧 Email: {user.email}")
        print(f"📅 Créé: {user.date_joined}")
        print(f"🖼️  Photo: {user.profile_photo}")
        print(f"✅ Actif: {user.is_active}")
        print("-" * 20)
    
    # Products
    print("\n🛍️ PRODUITS:")
    print("-" * 30)
    products = Product.objects.all()[:5]  # Limite à 5
    for product in products:
        print(f"📦 {product.name} - ${product.price}")
        print(f"📅 Créé: {product.created_at}")
        print("-" * 20)
    
    # Orders
    print("\n📋 COMMANDES:")
    print("-" * 30)
    orders = Order.objects.all()[:5]  # Limite à 5
    for order in orders:
        print(f"🛒 Commande #{order.id} - {order.customer.email}")
        print(f"💰 Total: ${order.total_amount}")
        print(f"📅 Date: {order.created_at}")
        print("-" * 20)
    
    # Tickets
    print("\n🎫 TICKETS SUPPORT:")
    print("-" * 30)
    tickets = SupportTicket.objects.all()[:5]  # Limite à 5
    for ticket in tickets:
        print(f"🎫 #{ticket.ticket_number} - {ticket.title}")
        print(f"👤 Client: {ticket.customer.email}")
        print(f"📊 Statut: {ticket.status}")
        print(f"📅 Créé: {ticket.created_at}")
        print("-" * 20)
    
    print("\n✅ AFFICHAGE TERMINÉ!")
    print("=" * 60)

if __name__ == '__main__':
    show_database_updates()
