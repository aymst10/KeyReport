from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
import os

from .models import SupportTicket, ServiceRequest, Document, TicketResponse
from .forms import SupportTicketForm, ServiceRequestForm


def ticket_list(request):
    """List support tickets."""
    if request.user.is_authenticated:
        if request.user.is_staff_member():
            # Staff can see all tickets
            tickets = SupportTicket.objects.all()
        else:
            # Customers can only see their own tickets
            tickets = SupportTicket.objects.filter(customer=request.user)
    else:
        tickets = SupportTicket.objects.none()
    
    # Filtering
    status = request.GET.get('status')
    if status:
        tickets = tickets.filter(status=status)
    
    priority = request.GET.get('priority')
    if priority:
        tickets = tickets.filter(priority=priority)
    
    # Pagination
    paginator = Paginator(tickets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tickets': page_obj,
        'status_filter': status,
        'priority_filter': priority,
    }
    return render(request, 'support/ticket_list.html', context)


@login_required
def ticket_create(request):
    """Create a new support ticket."""
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.customer = request.user
            ticket.ticket_number = f"TKT-{request.user.id}-{int(timezone.now().timestamp())}"
            ticket.save()
            
            messages.success(request, 'Support ticket created successfully!')
            return redirect('support:ticket_detail', pk=ticket.pk)
    else:
        form = SupportTicketForm()
    
    context = {
        'form': form,
        'title': 'Create Support Ticket',
    }
    return render(request, 'support/ticket_form.html', context)


def ticket_detail(request, pk):
    """View ticket details."""
    ticket = get_object_or_404(SupportTicket, pk=pk)
    
    # Check if user has permission to view this ticket
    if not request.user.is_authenticated or (
        not request.user.is_staff_member() and 
        ticket.customer != request.user
    ):
        raise Http404("Ticket not found.")
    
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            TicketResponse.objects.create(
                ticket=ticket,
                author=request.user,
                message=message,
                is_internal=request.user.is_staff_member()
            )
            messages.success(request, 'Response added successfully!')
            return redirect('support:ticket_detail', pk=ticket.pk)
    
    context = {
        'ticket': ticket,
        'responses': ticket.responses.all(),
    }
    return render(request, 'support/ticket_detail.html', context)


@login_required
def ticket_update(request, pk):
    """Update a support ticket."""
    ticket = get_object_or_404(SupportTicket, pk=pk)
    
    # Check permissions
    if not request.user.is_staff_member() and ticket.customer != request.user:
        raise Http404("Permission denied.")
    
    if request.method == 'POST':
        form = SupportTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket updated successfully!')
            return redirect('support:ticket_detail', pk=ticket.pk)
    else:
        form = SupportTicketForm(instance=ticket)
    
    context = {
        'form': form,
        'ticket': ticket,
        'title': 'Edit Support Ticket',
    }
    return render(request, 'support/ticket_form.html', context)


@login_required
def ticket_close(request, pk):
    """Close a support ticket."""
    ticket = get_object_or_404(SupportTicket, pk=pk)
    
    # Check permissions
    if not request.user.is_staff_member() and ticket.customer != request.user:
        raise Http404("Permission denied.")
    
    if request.method == 'POST':
        ticket.status = 'closed'
        ticket.closed_at = timezone.now()
        ticket.save()
        
        messages.success(request, 'Ticket closed successfully!')
        return redirect('support:ticket_detail', pk=ticket.pk)
    
    context = {
        'ticket': ticket,
    }
    return render(request, 'support/ticket_confirm_close.html', context)


def service_list(request):
    """List service requests."""
    if request.user.is_authenticated:
        if request.user.is_staff_member():
            # Staff can see all service requests
            services = ServiceRequest.objects.all()
        else:
            # Customers can only see their own service requests
            services = ServiceRequest.objects.filter(customer=request.user)
    else:
        services = ServiceRequest.objects.none()
    
    # Filtering
    status = request.GET.get('status')
    if status:
        services = services.filter(status=status)
    
    service_type = request.GET.get('service_type')
    if service_type:
        services = services.filter(service_type=service_type)
    
    # Pagination
    paginator = Paginator(services, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'services': page_obj,
        'status_filter': status,
        'service_type_filter': service_type,
    }
    return render(request, 'support/service_list.html', context)


@login_required
def service_create(request):
    """Create a new service request."""
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.customer = request.user
            service.request_number = f"SRV-{request.user.id}-{int(timezone.now().timestamp())}"
            service.save()
            
            messages.success(request, 'Service request created successfully!')
            return redirect('support:service_detail', pk=service.pk)
    else:
        form = ServiceRequestForm()
    
    context = {
        'form': form,
        'title': 'Create Service Request',
    }
    return render(request, 'support/service_form.html', context)


def service_detail(request, pk):
    """View service request details."""
    service = get_object_or_404(ServiceRequest, pk=pk)
    
    # Check if user has permission to view this service request
    if not request.user.is_authenticated or (
        not request.user.is_staff_member() and 
        service.customer != request.user
    ):
        raise Http404("Service request not found.")
    
    context = {
        'service': service,
    }
    return render(request, 'support/service_detail.html', context)


@login_required
def service_update(request, pk):
    """Update a service request."""
    service = get_object_or_404(ServiceRequest, pk=pk)
    
    # Check permissions
    if not request.user.is_staff_member() and service.customer != request.user:
        raise Http404("Permission denied.")
    
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service request updated successfully!')
            return redirect('support:service_detail', pk=service.pk)
    else:
        form = ServiceRequestForm(instance=service)
    
    context = {
        'form': form,
        'service': service,
        'title': 'Edit Service Request',
    }
    return render(request, 'support/service_form.html', context)


def document_list(request):
    """List documents."""
    if request.user.is_authenticated:
        if request.user.is_staff_member():
            # Staff can see all documents
            documents = Document.objects.all()
        else:
            # Customers can only see their own documents
            documents = Document.objects.filter(customer=request.user)
    else:
        documents = Document.objects.none()
    
    # Filtering
    document_type = request.GET.get('document_type')
    if document_type:
        documents = documents.filter(document_type=document_type)
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'documents': page_obj,
        'document_type_filter': document_type,
    }
    return render(request, 'support/document_list.html', context)


def document_detail(request, pk):
    """View document details."""
    document = get_object_or_404(Document, pk=pk)
    
    # Check if user has permission to view this document
    if not request.user.is_authenticated or (
        not request.user.is_staff_member() and 
        document.customer != request.user
    ):
        raise Http404("Document not found.")
    
    context = {
        'document': document,
    }
    return render(request, 'support/document_detail.html', context)


@login_required
def document_download(request, pk):
    """Download a document."""
    document = get_object_or_404(Document, pk=pk)
    
    # Check if user has permission to download this document
    if not request.user.is_staff_member() and document.customer != request.user:
        raise Http404("Document not found.")
    
    if document.file and os.path.exists(document.file.path):
        response = HttpResponse(document.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(document.file.name)}"'
        return response
    else:
        raise Http404("File not found.")
