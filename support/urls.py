from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # Support tickets
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('ticket/new/', views.ticket_create, name='ticket_create'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:pk>/edit/', views.ticket_update, name='ticket_update'),
    path('ticket/<int:pk>/close/', views.ticket_close, name='ticket_close'),
    
    # Service requests
    path('services/', views.service_list, name='service_list'),
    path('service/new/', views.service_create, name='service_create'),
    path('service/<int:pk>/', views.service_detail, name='service_detail'),
    path('service/<int:pk>/edit/', views.service_update, name='service_update'),
    
    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
    path('document/<int:pk>/download/', views.document_download, name='document_download'),
]
