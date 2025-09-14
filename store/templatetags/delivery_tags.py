from django import template
from datetime import datetime, date
from django.utils import timezone

register = template.Library()

@register.filter
def days_until_delivery(delivery_date):
    """Calculate days until delivery date"""
    if not delivery_date:
        return None
    
    # Convert to date if it's a datetime
    if isinstance(delivery_date, datetime):
        delivery_date = delivery_date.date()
    
    today = timezone.now().date()
    
    if delivery_date < today:
        return 0  # Already delivered or overdue
    
    return (delivery_date - today).days

@register.filter
def delivery_status_class(delivery_date, order_status):
    """Return CSS class based on delivery status"""
    if not delivery_date:
        return "text-muted"
    
    days = days_until_delivery(delivery_date)
    
    if order_status == 'delivered':
        return "text-success"
    elif days == 0:
        return "text-warning"
    elif days <= 2:
        return "text-info"
    elif days <= 5:
        return "text-primary"
    else:
        return "text-secondary"

@register.filter
def delivery_status_text(delivery_date, order_status):
    """Return status text based on delivery date and order status"""
    if not delivery_date:
        return "Date de livraison non définie"
    
    if order_status == 'delivered':
        return "Livré"
    
    days = days_until_delivery(delivery_date)
    
    if days == 0:
        return "Livraison prévue aujourd'hui"
    elif days == 1:
        return "Livraison prévue demain"
    elif days > 1:
        return f"Livraison dans {days} jours"
    else:
        return "En retard"

@register.filter
def delivery_progress(order_status, delivery_date):
    """Calculate delivery progress percentage"""
    if order_status == 'delivered':
        return 100
    elif order_status == 'shipped':
        return 75
    elif order_status == 'processing':
        return 50
    elif order_status == 'confirmed':
        return 25
    else:
        return 10




















