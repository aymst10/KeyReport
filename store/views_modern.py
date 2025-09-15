"""
Modern dashboard views for Key Analytics Report
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Product, Order, Payment
from support.models import SupportTicket
from users.models import CustomUser


def modern_home(request):
    """
    Modern home page view
    """
    return render(request, 'store/home_modern.html')

@login_required
def modern_dashboard(request):
    """
    Modern dashboard view with responsive design
    """
    # Get statistics
    stats = {
        'total_products': Product.objects.filter(is_active=True).count(),
        'active_tickets': SupportTicket.objects.filter(status__in=['open', 'in_progress']).count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_users': CustomUser.objects.count(),
    }
    
    # Get recent activity (mock data for now)
    recent_activities = [
        {
            'type': 'order',
            'title': 'New order received',
            'time': '2 minutes ago',
            'icon': 'fas fa-shopping-cart',
            'color': 'success'
        },
        {
            'type': 'user',
            'title': 'New user registered',
            'time': '15 minutes ago',
            'icon': 'fas fa-user-plus',
            'color': 'primary'
        },
        {
            'type': 'ticket',
            'title': 'Support ticket created',
            'time': '1 hour ago',
            'icon': 'fas fa-ticket-alt',
            'color': 'warning'
        },
    ]
    
    context = {
        'stats': stats,
        'recent_activities': recent_activities,
        'user': request.user,
    }
    
    return render(request, 'store/dashboard_modern.html', context)
