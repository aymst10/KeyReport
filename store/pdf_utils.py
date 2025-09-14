"""
PDF generation utilities for payment receipts using ReportLab
"""
import os
from io import BytesIO
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


def get_payment_method_display(payment_method):
    """Convert payment method code to display name"""
    method_names = {
        'credit_card': 'Carte de Crédit',
        'paypal': 'PayPal',
        'cash_delivery': 'Paiement à la Livraison',
        'bank_transfer': 'Virement Bancaire'
    }
    return method_names.get(payment_method, payment_method)


def get_payment_status_display(status):
    """Convert payment status to display name"""
    status_names = {
        'completed': 'Complété',
        'pending': 'En Attente de Paiement',
        'failed': 'Échoué',
        'processing': 'En Cours de Traitement'
    }
    return status_names.get(status, status)


def generate_payment_receipt_pdf(payment, order):
    """
    Generate a professional PDF receipt for payment
    """
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=30
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles - optimized for single page
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=8,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4
    )
    
    small_style = ParagraphStyle(
        'SmallStyle',
        parent=styles['Normal'],
        fontSize=8,
        spaceAfter=3
    )
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph("REÇU DE PAIEMENT", title_style))
    story.append(Spacer(1, 10))
    
    # Company info
    company_info = [
        [Paragraph("<b>Key Analytics Report</b>", normal_style), ""],
        ["Adresse: Mazola rue 6, Casablanca", ""],
        ["Téléphone: +212 6 04 12 12 83", ""],
        ["Email: contact@keyreport.ma", ""],
        ["", Paragraph(f"<b>Reçu #:</b> {payment.id}", normal_style)],
        ["", Paragraph(f"<b>Date:</b> {payment.created_at.strftime('%d/%m/%Y %H:%M')}", normal_style)],
    ]
    
    company_table = Table(company_info, colWidths=[4*inch, 2*inch])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(company_table)
    story.append(Spacer(1, 12))
    
    # Customer information
    story.append(Paragraph("INFORMATIONS CLIENT", heading_style))
    
    customer_info = [
        [Paragraph("<b>Nom:</b>", normal_style), f"{order.customer.get_full_name() or order.customer.email}"],
        [Paragraph("<b>Email:</b>", normal_style), order.customer.email],
        [Paragraph("<b>Téléphone:</b>", normal_style), order.contact_phone or "Non fourni"],
        [Paragraph("<b>Adresse de livraison:</b>", normal_style), order.shipping_address or "Non fournie"],
    ]
    
    customer_table = Table(customer_info, colWidths=[1.5*inch, 4.5*inch])
    customer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTSIZE', (1, 0), (1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(customer_table)
    story.append(Spacer(1, 12))
    
    # Order information
    story.append(Paragraph("DÉTAILS DE LA COMMANDE", heading_style))
    
    order_info = [
        [Paragraph("<b>Numéro de commande:</b>", normal_style), order.order_number],
        [Paragraph("<b>Date de commande:</b>", normal_style), order.created_at.strftime('%d/%m/%Y %H:%M')],
        [Paragraph("<b>Statut:</b>", normal_style), order.get_status_display()],
    ]
    
    order_table = Table(order_info, colWidths=[1.5*inch, 4.5*inch])
    order_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTSIZE', (1, 0), (1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(order_table)
    story.append(Spacer(1, 12))
    
    # Order items
    story.append(Paragraph("ARTICLES COMMANDÉS", heading_style))
    
    # Table header
    items_data = [["Produit", "Quantité", "Prix unitaire", "Total"]]
    
    # Add order items
    for item in order.items.all():
        items_data.append([
            item.product.name,
            str(item.quantity),
            f"{item.unit_price:.2f} MAD",
            f"{item.total_price:.2f} MAD"
        ])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Product name left-aligned
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Numbers center-aligned
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 20))
    
    # Payment summary
    story.append(Paragraph("RÉSUMÉ DU PAIEMENT", heading_style))
    
    payment_data = [
        [Paragraph("<b>Méthode de paiement:</b>", normal_style), get_payment_method_display(payment.payment_method)],
        [Paragraph("<b>Statut du paiement:</b>", normal_style), get_payment_status_display(payment.status)],
        [Paragraph("<b>Montant total:</b>", normal_style), f"{payment.amount:.2f} MAD"],
    ]
    
    if payment.processed_at:
        payment_data.append([Paragraph("<b>Date de traitement:</b>", normal_style), payment.processed_at.strftime('%d/%m/%Y %H:%M')])
    
    if payment.card_last_four:
        payment_data.append([Paragraph("<b>Derniers 4 chiffres:</b>", normal_style), f"**** **** **** {payment.card_last_four}"])
    
    if payment.card_brand:
        payment_data.append([Paragraph("<b>Type de carte:</b>", normal_style), payment.card_brand.upper()])
    
    payment_table = Table(payment_data, colWidths=[2*inch, 4*inch])
    payment_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTSIZE', (1, 0), (1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(payment_table)
    story.append(Spacer(1, 15))
    
    # Footer with status-specific message
    if payment.status == 'completed':
        footer_text = """
        <para align=center>
        <b>Merci pour votre achat!</b><br/>
        Ce reçu confirme votre paiement et votre commande.<br/>
        Contact: contact@keyreport.ma
        </para>
        """
    elif payment.status == 'pending':
        if payment.payment_method == 'cash_delivery':
            footer_text = """
            <para align=center>
            <b>Commande confirmée!</b><br/>
            Paiement à la livraison. Contact: contact@keyreport.ma
            </para>
            """
        elif payment.payment_method == 'bank_transfer':
            footer_text = """
            <para align=center>
            <b>Commande confirmée!</b><br/>
            Virement bancaire requis. Contact: contact@keyreport.ma
            </para>
            """
        else:
            footer_text = """
            <para align=center>
            <b>Commande confirmée!</b><br/>
            Paiement en cours. Contact: contact@keyreport.ma
            </para>
            """
    else:
        footer_text = """
        <para align=center>
        <b>Merci pour votre commande!</b><br/>
        Contact: contact@keyreport.ma
        </para>
        """
    
    story.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def generate_payment_receipt_response(payment, order, filename=None):
    """
    Generate HTTP response with PDF receipt
    """
    if not filename:
        filename = f"receipt_{payment.id}_{order.order_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    pdf_content = generate_payment_receipt_pdf(payment, order)
    
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Content-Length'] = len(pdf_content)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    response['X-Content-Type-Options'] = 'nosniff'
    
    return response
