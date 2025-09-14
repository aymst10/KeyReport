from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from store.admin_views import admin_dashboard


class KeyReportAdminSite(admin.AdminSite):
    """Custom admin site for KeyReport."""
    
    site_header = "KeyReport Analytics Admin"
    site_title = "KeyReport Admin"
    index_title = "Welcome to KeyReport Administration"
    
    def get_urls(self):
        """Add custom URLs to admin."""
        urls = super().get_urls()
        custom_urls = [
            path('store-dashboard/', self.admin_view(admin_dashboard), name='store_dashboard'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        """Custom admin index with dashboard link."""
        extra_context = extra_context or {}
        extra_context['has_store_dashboard'] = True
        return super().index(request, extra_context)


# Create custom admin site instance
admin_site = KeyReportAdminSite(name='keyreport_admin')

# Register models with custom admin site
from django.contrib.auth.models import User, Group
from store.models import Category, Product, Order, OrderItem, Cart, CartItem, Payment, Wishlist, ProductReview

admin_site.register(User)
admin_site.register(Group)
admin_site.register(Category)
admin_site.register(Product)
admin_site.register(Order)
admin_site.register(OrderItem)
admin_site.register(Cart)
admin_site.register(CartItem)
admin_site.register(Payment)
admin_site.register(Wishlist)
admin_site.register(ProductReview)







