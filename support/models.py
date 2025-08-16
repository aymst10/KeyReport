from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from store.models import Product

User = get_user_model()


class SupportTicket(models.Model):
    """Technical support ticket model."""
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    
    STATUS_CHOICES = [
        ('open', _('Open')),
        ('in_progress', _('In Progress')),
        ('waiting_customer', _('Waiting for Customer')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    ]
    
    TICKET_TYPE_CHOICES = [
        ('technical', _('Technical Issue')),
        ('billing', _('Billing Question')),
        ('product', _('Product Support')),
        ('service', _('Service Request')),
        ('general', _('General Inquiry')),
    ]
    
    ticket_number = models.CharField(max_length=20, unique=True, verbose_name=_('Ticket Number'))
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets', verbose_name=_('Customer'))
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tickets',
        verbose_name=_('Assigned To'),
        limit_choices_to={'user_type__in': ['staff', 'admin']}
    )
    
    # Ticket details
    title = models.CharField(max_length=200, verbose_name=_('Ticket Title'))
    description = models.TextField(verbose_name=_('Description'))
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES, default='general', verbose_name=_('Ticket Type'))
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name=_('Priority'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name=_('Status'))
    
    # Related product (if applicable)
    related_product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_('Related Product')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Resolved At'))
    closed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Closed At'))
    
    class Meta:
        verbose_name = _('Support Ticket')
        verbose_name_plural = _('Support Tickets')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['priority', 'status']),
            models.Index(fields=['ticket_type', 'status']),
        ]
    
    def __str__(self):
        return f"Ticket {self.ticket_number}: {self.title}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('support:ticket_detail', kwargs={'pk': self.pk})
    
    def get_priority_display_class(self):
        """Get Bootstrap class for priority display."""
        priority_classes = {
            'low': 'success',
            'medium': 'info',
            'high': 'warning',
            'urgent': 'danger',
        }
        return priority_classes.get(self.priority, 'secondary')
    
    def get_status_display_class(self):
        """Get Bootstrap class for status display."""
        status_classes = {
            'open': 'danger',
            'in_progress': 'primary',
            'waiting_customer': 'warning',
            'resolved': 'success',
            'closed': 'secondary',
        }
        return status_classes.get(self.status, 'secondary')


class TicketResponse(models.Model):
    """Response to a support ticket."""
    
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses', verbose_name=_('Ticket'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Author'))
    message = models.TextField(verbose_name=_('Message'))
    is_internal = models.BooleanField(default=False, verbose_name=_('Internal Note'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Ticket Response')
        verbose_name_plural = _('Ticket Responses')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Response to {self.ticket.ticket_number} by {self.author.email}"


class ServiceRequest(models.Model):
    """Service request for installation, maintenance, etc."""
    
    SERVICE_TYPE_CHOICES = [
        ('installation', _('Installation')),
        ('maintenance', _('Maintenance')),
        ('repair', _('Repair')),
        ('training', _('Training')),
        ('consultation', _('Consultation')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    request_number = models.CharField(max_length=20, unique=True, verbose_name=_('Request Number'))
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests', verbose_name=_('Customer'))
    assigned_technician = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_services',
        verbose_name=_('Assigned Technician'),
        limit_choices_to={'user_type__in': ['staff', 'admin']}
    )
    
    # Service details
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, verbose_name=_('Service Type'))
    title = models.CharField(max_length=200, verbose_name=_('Service Title'))
    description = models.TextField(verbose_name=_('Description'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Status'))
    
    # Location and scheduling
    service_address = models.TextField(verbose_name=_('Service Address'))
    service_city = models.CharField(max_length=100, verbose_name=_('Service City'))
    service_state = models.CharField(max_length=100, verbose_name=_('Service State'))
    service_zip_code = models.CharField(max_length=20, verbose_name=_('Service ZIP Code'))
    
    preferred_date = models.DateField(verbose_name=_('Preferred Date'))
    preferred_time = models.TimeField(verbose_name=_('Preferred Time'))
    
    # Cost and billing
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Estimated Cost'))
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Actual Cost'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Scheduled At'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Completed At'))
    
    class Meta:
        verbose_name = _('Service Request')
        verbose_name_plural = _('Service Requests')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['assigned_technician', 'status']),
            models.Index(fields=['service_type', 'status']),
            models.Index(fields=['preferred_date']),
        ]
    
    def __str__(self):
        return f"Service {self.request_number}: {self.title}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('support:service_detail', kwargs={'pk': self.pk})
    
    def get_status_display_class(self):
        """Get Bootstrap class for status display."""
        status_classes = {
            'pending': 'warning',
            'approved': 'info',
            'scheduled': 'primary',
            'in_progress': 'info',
            'completed': 'success',
            'cancelled': 'danger',
        }
        return status_classes.get(self.status, 'secondary')


class ServiceSchedule(models.Model):
    """Schedule for service appointments."""
    
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='schedule', verbose_name=_('Service Request'))
    technician = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='scheduled_services',
        verbose_name=_('Technician'),
        limit_choices_to={'user_type__in': ['staff', 'admin']}
    )
    
    scheduled_date = models.DateField(verbose_name=_('Scheduled Date'))
    scheduled_time = models.TimeField(verbose_name=_('Scheduled Time'))
    estimated_duration = models.PositiveIntegerField(help_text=_('Duration in minutes'), verbose_name=_('Estimated Duration'))
    
    notes = models.TextField(blank=True, verbose_name=_('Schedule Notes'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Service Schedule')
        verbose_name_plural = _('Service Schedules')
        ordering = ['scheduled_date', 'scheduled_time']
    
    def __str__(self):
        return f"Service {self.service_request.request_number} scheduled for {self.scheduled_date} at {self.scheduled_time}"


class Document(models.Model):
    """Document model for invoices, receipts, service reports, etc."""
    
    DOCUMENT_TYPE_CHOICES = [
        ('invoice', _('Invoice')),
        ('receipt', _('Receipt')),
        ('service_report', _('Service Report')),
        ('warranty', _('Warranty Document')),
        ('manual', _('User Manual')),
        ('other', _('Other')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_('Document Title'))
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, verbose_name=_('Document Type'))
    file = models.FileField(upload_to='documents/', verbose_name=_('Document File'))
    
    # Related objects
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents', verbose_name=_('Customer'))
    related_order = models.ForeignKey(
        'store.Order', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_('Related Order')
    )
    related_ticket = models.ForeignKey(
        SupportTicket, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_('Related Ticket')
    )
    related_service = models.ForeignKey(
        ServiceRequest, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_('Related Service')
    )
    
    description = models.TextField(blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'document_type']),
            models.Index(fields=['document_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_document_type_display()}: {self.title}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('support:document_detail', kwargs={'pk': self.pk})
    
    @property
    def file_extension(self):
        """Get file extension."""
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return ''
    
    @property
    def file_size_mb(self):
        """Get file size in MB."""
        if self.file:
            return round(self.file.size / (1024 * 1024), 2)
        return 0
