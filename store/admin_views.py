from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Product, Order, OrderItem, ProductReview, Wishlist, Category


@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard with analytics."""
    
    # Time periods
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Basic stats
    total_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    total_reviews = ProductReview.objects.filter(is_approved=True).count()
    total_wishlist_items = Wishlist.objects.count()
    
    # Recent activity
    recent_orders = Order.objects.order_by('-created_at')[:5]
    recent_reviews = ProductReview.objects.filter(is_approved=True).order_by('-created_at')[:5]
    
    # Sales analytics
    orders_this_week = Order.objects.filter(created_at__date__gte=week_ago)
    orders_this_month = Order.objects.filter(created_at__date__gte=month_ago)
    
    weekly_revenue = sum(order.total_amount for order in orders_this_week)
    monthly_revenue = sum(order.total_amount for order in orders_this_month)
    
    # Top products by sales
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]
    
    # Top rated products
    top_rated_products = Product.objects.annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(avg_rating__gte=4.0).order_by('-avg_rating')[:5]
    
    # Category distribution
    category_stats = Category.objects.annotate(
        product_count=Count('products'),
        avg_rating=Avg('products__reviews__rating')
    ).filter(is_active=True)
    
    # Review statistics
    review_stats = {
        'total': ProductReview.objects.count(),
        'approved': ProductReview.objects.filter(is_approved=True).count(),
        'pending': ProductReview.objects.filter(is_approved=False).count(),
        'avg_rating': ProductReview.objects.filter(is_approved=True).aggregate(
            avg=Avg('rating')
        )['avg'] or 0
    }
    
    # Order status distribution
    order_status_stats = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_reviews': total_reviews,
        'total_wishlist_items': total_wishlist_items,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,
        'top_products': top_products,
        'top_rated_products': top_rated_products,
        'category_stats': category_stats,
        'review_stats': review_stats,
        'order_status_stats': order_status_stats,
    }
    
    return render(request, 'admin/store_dashboard.html', context)







