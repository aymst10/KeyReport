from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SupportTicket, TicketResponse, ServiceRequest, 
    ServiceSchedule, Document
)


class TicketResponseInline(admin.TabularInline):
    """Inline admin for TicketResponse."""
    
    model = TicketResponse
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    """Admin configuration for SupportTicket model."""
    
    list_display = (
        'ticket_number', 'title', 'customer', 'ticket_type', 
        'priority', 'status', 'assigned_to', 'created_at'
    )
    list_filter = (
        'ticket_type', 'priority', 'status', 'assigned_to', 
        'created_at', 'resolved_at'
    )
    search_fields = (
        'ticket_number', 'title', 'customer__email', 
        'customer__first_name', 'customer__last_name'
    )
    readonly_fields = ('ticket_number', 'created_at', 'updated_at')
    list_editable = ('priority', 'status', 'assigned_to')
    
    inlines = [TicketResponseInline]
    
    fieldsets = (
        (None, {
            'fields': ('ticket_number', 'customer', 'assigned_to')
        }),
        ('Ticket Details', {
            'fields': ('title', 'description', 'ticket_type', 'priority', 'status')
        }),
        ('Related Information', {
            'fields': ('related_product',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'customer', 'assigned_to', 'related_product'
        )


@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    """Admin configuration for TicketResponse model."""
    
    list_display = ('ticket', 'author', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('ticket__ticket_number', 'author__email', 'message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('ticket', 'author', 'message', 'is_internal')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    """Admin configuration for ServiceRequest model."""
    
    list_display = (
        'request_number', 'title', 'customer', 'service_type', 
        'status', 'assigned_technician', 'preferred_date', 'estimated_cost'
    )
    list_filter = (
        'service_type', 'status', 'assigned_technician', 
        'preferred_date', 'created_at'
    )
    search_fields = (
        'request_number', 'title', 'customer__email', 
        'customer__first_name', 'customer__last_name'
    )
    readonly_fields = ('request_number', 'created_at', 'updated_at')
    list_editable = ('status', 'assigned_technician')
    
    fieldsets = (
        (None, {
            'fields': ('request_number', 'customer', 'assigned_technician')
        }),
        ('Service Details', {
            'fields': ('service_type', 'title', 'description', 'status')
        }),
        ('Location & Scheduling', {
            'fields': (
                'service_address', 'service_city', 'service_state', 
                'service_zip_code', 'preferred_date', 'preferred_time'
            )
        }),
        ('Cost Information', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'scheduled_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'customer', 'assigned_technician'
        )


@admin.register(ServiceSchedule)
class ServiceScheduleAdmin(admin.ModelAdmin):
    """Admin configuration for ServiceSchedule model."""
    
    list_display = (
        'service_request', 'technician', 'scheduled_date', 
        'scheduled_time', 'estimated_duration'
    )
    list_filter = ('scheduled_date', 'technician', 'created_at')
    search_fields = (
        'service_request__request_number', 'technician__email',
        'technician__first_name', 'technician__last_name'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('service_request', 'technician')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'scheduled_time', 'estimated_duration')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'service_request', 'technician'
        )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin configuration for Document model."""
    
    list_display = (
        'title', 'document_type', 'customer', 'file_info', 
        'related_order', 'related_ticket', 'created_at'
    )
    list_filter = ('document_type', 'created_at')
    search_fields = (
        'title', 'customer__email', 'customer__first_name', 
        'customer__last_name', 'description'
    )
    readonly_fields = ('created_at', 'updated_at', 'file_info')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'document_type', 'file', 'customer')
        }),
        ('Related Objects', {
            'fields': ('related_order', 'related_ticket', 'related_service')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_info(self, obj):
        """Display file information."""
        if obj.file:
            return format_html(
                '<span style="font-family: monospace;">{}</span><br>'
                '<small>Size: {} MB | Type: {}</small>',
                obj.file.name.split('/')[-1],
                obj.file_size_mb,
                obj.file_extension
            )
        return 'No file'
    file_info.short_description = 'File Info'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'customer', 'related_order', 'related_ticket', 'related_service'
        )
