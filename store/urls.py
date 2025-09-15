from django.urls import path
from . import views
from . import professional_payment_views
from . import views_modern

app_name = 'store'

urlpatterns = [
    # Public views
    path('', views.home, name='home'),
    path('modern/', views_modern.modern_home, name='modern_home'),
    path('dashboard/', views_modern.modern_dashboard, name='modern_dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('contact/', views.contact, name='contact'),
    
    # Categories
    path('categories/', views.categories, name='categories'),
    
    # Staff management views (must come before product/<slug:slug>/)
    # path('product/new/', views.ProductCreateView.as_view(), name='product_create'),
    # path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    # path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Product detail (must come after specific product URLs)
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Cart and checkout
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-cart-item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    # path('process-payment/', views.process_payment, name='process_payment'),
    
    # User orders
    path('orders/', views.order_list, name='order_list'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    
    # Payment confirmation and receipt
    path('payment-confirmation/', views.payment_confirmation, name='payment_confirmation'),
    path('payment-receipt/', views.payment_receipt, name='payment_receipt'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    
    # Reviews
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),
    
    # Payment
    path('payment/', views.payment_method_selection, name='payment_method_selection'),
    path('order/<int:order_id>/payment/', views.payment_method_selection, name='payment_method_selection_order'),
    path('order/<int:order_id>/payment/<str:payment_method>/', views.payment_process, name='payment_process'),
    path('order/<int:order_id>/payment-details/<str:payment_method>/', views.payment_details, name='payment_details'),
    path('order/<int:order_id>/cash-receipt/', views.cash_payment_receipt, name='cash_payment_receipt'),
    path('payment/success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('payment/failed/<int:payment_id>/', views.payment_failed, name='payment_failed'),
    path('payment/refund/<int:payment_id>/', views.refund_payment, name='refund_payment'),
    
    # Order Form
    path('order-form/', professional_payment_views.order_form, name='order_form'),
    path('order-form/<int:order_id>/', professional_payment_views.order_form, name='order_form_edit'),
    
    # Professional Payment System
    path('professional-payment/', professional_payment_views.professional_payment, name='professional_payment'),
    path('professional-payment/<int:order_id>/', professional_payment_views.professional_payment, name='professional_payment_order'),
    path('process-professional-payment/<int:order_id>/', professional_payment_views.process_professional_payment, name='process_professional_payment'),
    path('payment-success/<int:payment_id>/', professional_payment_views.payment_success_professional, name='payment_success_professional'),
    path('payment-failed/<int:payment_id>/', professional_payment_views.payment_failed_professional, name='payment_failed_professional'),
    path('payment-receipt-pdf/<int:payment_id>/', professional_payment_views.download_payment_receipt_pdf, name='download_payment_receipt_pdf'),
    
    # Admin Dashboard
    # path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Contact Demo
    path('contact-demo/', views.contact_demo, name='contact_demo'),
    
    # Category management
    # path('category/new/', views.CategoryCreateView.as_view(), name='category_create'),
    # path('category/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    # path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]