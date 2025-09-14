from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import uuid
import json
from datetime import datetime

from .models import Order, OrderItem, Payment, Cart, CartItem
from .forms import OrderForm
from .pdf_utils import generate_payment_receipt_response
# from .forms import CardPaymentForm, PayPalForm, CashDeliveryForm


@login_required
def order_form(request, order_id=None):
    """
    Vue pour collecter les informations de livraison
    """
    if order_id:
        # Modifier une commande existante
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        form = OrderForm(request.POST or None, instance=order, user=request.user)
    else:
        # Nouvelle commande depuis le panier
        cart = Cart.objects.get_or_create(user=request.user)[0]
        cart_items = CartItem.objects.filter(cart=cart)
        
        if not cart_items.exists():
            messages.error(request, 'Votre panier est vide.')
            return redirect('store:cart')
        
        # Créer une commande temporaire pour le formulaire
        order = Order(
            customer=request.user,
            order_number=f"TEMP-{uuid.uuid4().hex[:8].upper()}",
            status='pending',
            subtotal=cart.total_price,
            tax_amount=0,
            shipping_cost=0,
            total_amount=cart.total_price
        )
        form = OrderForm(request.POST or None, instance=order, user=request.user)
    
    if request.method == 'POST' and form.is_valid():
        if order_id:
            # Mettre à jour la commande existante
            form.save()
            messages.success(request, 'Informations de livraison mises à jour avec succès!')
            return redirect('store:professional_payment_order', order_id=order.id)
        else:
            # Créer une nouvelle commande
            order = form.save(commit=False)
            order.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            order.save()
            
            # Créer les items de commande
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.price,
                    total_price=cart_item.product.price * cart_item.quantity
                )
            
            # Vider le panier
            cart_items.delete()
            
            messages.success(request, 'Commande créée avec succès!')
            return redirect('store:professional_payment_order', order_id=order.id)
    
    context = {
        'form': form,
        'order': order,
        'is_edit': bool(order_id)
    }
    
    return render(request, 'store/order_form.html', context)


@login_required
def professional_payment(request, order_id=None):
    """
    Vue professionnelle de paiement avec interface moderne
    """
    if order_id:
        # Paiement pour une commande existante
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        
        # Vérifier si la commande a les informations de livraison
        if not order.shipping_address or not order.contact_phone or not order.contact_email:
            messages.warning(request, 'Veuillez d\'abord compléter les informations de livraison.')
            return redirect('store:order_form', order_id=order.id)
    else:
        # Rediriger vers le formulaire de commande pour collecter les informations de livraison
        return redirect('store:order_form')
    
    context = {
        'order': order,
        'order_items': order.items.all(),
        'payment_methods': [
            {'id': 'credit_card', 'name': 'Carte de Crédit', 'icon': 'fas fa-credit-card'},
            {'id': 'paypal', 'name': 'PayPal', 'icon': 'fab fa-paypal'},
            {'id': 'cash_delivery', 'name': 'Paiement à la Livraison', 'icon': 'fas fa-money-bill-wave'},
            {'id': 'bank_transfer', 'name': 'Virement Bancaire', 'icon': 'fas fa-university'},
        ]
    }
    
    return render(request, 'store/payment_professional.html', context)


@login_required
@require_http_methods(["POST"])
def process_professional_payment(request, order_id):
    """
    Traitement du paiement professionnel
    """
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    payment_method = request.POST.get('payment_method')
    
    if not payment_method:
        messages.error(request, 'Veuillez sélectionner un mode de paiement.')
        return redirect('store:professional_payment_order', order_id=order_id)
    
    try:
        # Créer l'enregistrement de paiement
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total_amount,
            status='processing'
        )
        
        # Traitement selon le mode de paiement
        if payment_method == 'credit_card':
            return process_credit_card_payment(request, payment)
        elif payment_method == 'paypal':
            return process_paypal_payment(request, payment)
        elif payment_method == 'cash_delivery':
            return process_cash_delivery_payment(request, payment)
        elif payment_method == 'bank_transfer':
            return process_bank_transfer_payment(request, payment)
        else:
            messages.error(request, 'Mode de paiement non supporté.')
            return redirect('store:professional_payment_order', order_id=order_id)
            
    except Exception as e:
        messages.error(request, f'Erreur lors du traitement du paiement: {str(e)}')
        return redirect('store:professional_payment_order', order_id=order_id)


def process_credit_card_payment(request, payment):
    """
    Traitement du paiement par carte bancaire
    """
    # Validation des données de la carte
    card_number = request.POST.get('card_number', '').replace(' ', '')
    expiry_date = request.POST.get('expiry_date', '')
    cvv = request.POST.get('cvv', '')
    cardholder_name = request.POST.get('cardholder_name', '')
    
    # Validation basique
    if not all([card_number, expiry_date, cvv, cardholder_name]):
        messages.error(request, 'Veuillez remplir tous les champs de la carte.')
        return redirect('store:professional_payment_order', order_id=payment.order.id)
    
    # Validation du numéro de carte (algorithme de Luhn simplifié)
    if not validate_card_number(card_number):
        messages.error(request, 'Numéro de carte invalide.')
        return redirect('store:professional_payment_order', order_id=payment.order.id)
    
    # Validation de la date d'expiration
    if not validate_expiry_date(expiry_date):
        messages.error(request, 'Date d\'expiration invalide.')
        return redirect('store:professional_payment_order', order_id=payment.order.id)
    
    # Simulation du traitement de paiement
    # Dans un vrai système, vous feriez appel à une passerelle de paiement
    payment_status = simulate_payment_gateway(card_number, expiry_date, cvv, payment.amount)
    
    if payment_status['success']:
        # Paiement réussi
        payment.status = 'completed'
        payment.card_last_four = card_number[-4:]
        payment.card_brand = get_card_brand(card_number)
        payment.processed_at = timezone.now()
        payment.save()
        
        # Mettre à jour la commande
        payment.order.status = 'confirmed'
        payment.order.save()
        
        messages.success(request, 'Paiement effectué avec succès!')
        # Automatically generate and return PDF receipt
        return generate_payment_receipt_response(payment, payment.order)
    else:
        # Paiement échoué
        payment.status = 'failed'
        payment.save()
        
        messages.error(request, f'Paiement échoué: {payment_status["message"]}')
        return redirect('store:payment_failed_professional', payment_id=payment.id)


def process_paypal_payment(request, payment):
    """
    Traitement du paiement PayPal
    """
    paypal_email = request.POST.get('paypal_email', '')
    
    if not paypal_email:
        messages.error(request, 'Veuillez entrer votre email PayPal.')
        return redirect('store:professional_payment_order', order_id=payment.order.id)
    
    # Simulation du traitement PayPal
    # Dans un vrai système, vous feriez appel à l'API PayPal
    payment_status = simulate_paypal_payment(paypal_email, payment.amount)
    
    if payment_status['success']:
        payment.status = 'completed'
        payment.processed_at = timezone.now()
        payment.save()
        
        payment.order.status = 'confirmed'
        payment.order.save()
        
        messages.success(request, 'Paiement PayPal effectué avec succès!')
        # Automatically generate and return PDF receipt
        return generate_payment_receipt_response(payment, payment.order)
    else:
        payment.status = 'failed'
        payment.save()
        
        messages.error(request, f'Paiement PayPal échoué: {payment_status["message"]}')
        return redirect('store:payment_failed_professional', payment_id=payment.id)


def process_cash_delivery_payment(request, payment):
    """
    Traitement du paiement à la livraison
    """
    # Pour le paiement à la livraison, on marque comme en attente
    payment.status = 'pending'
    payment.processed_at = timezone.now()
    payment.save()
    
    # Mettre à jour la commande
    payment.order.status = 'pending_payment'
    payment.order.save()
    
    messages.success(request, 'Commande confirmée! Vous paierez à la livraison.')
    # Automatically generate and return PDF receipt
    return generate_payment_receipt_response(payment, payment.order)


def process_bank_transfer_payment(request, payment):
    """
    Traitement du paiement par virement bancaire
    """
    # Pour le virement bancaire, on marque comme en attente
    payment.status = 'pending'
    payment.processed_at = timezone.now()
    payment.save()
    
    # Mettre à jour la commande
    payment.order.status = 'pending_payment'
    payment.order.save()
    
    messages.success(request, 'Commande confirmée! Veuillez effectuer le virement bancaire.')
    # Automatically generate and return PDF receipt
    return generate_payment_receipt_response(payment, payment.order)


def payment_success_professional(request, payment_id):
    """
    Page de succès du paiement professionnel
    """
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    
    return render(request, 'store/payment_success_professional.html', context)


@login_required
def download_payment_receipt_pdf(request, payment_id):
    """
    Download PDF receipt for professional payment
    """
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    order = payment.order
    
    # Generate filename
    filename = f"receipt_{payment.id}_{order.order_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # Generate and return PDF response
    return generate_payment_receipt_response(payment, order, filename)


def payment_failed_professional(request, payment_id):
    """
    Page d'échec du paiement professionnel
    """
    payment = get_object_or_404(Payment, id=payment_id, order__customer=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    
    return render(request, 'store/payment_failed_professional.html', context)


# Fonctions utilitaires
def validate_card_number(card_number):
    """
    Validation basique du numéro de carte (algorithme de Luhn)
    """
    if not card_number or len(card_number) < 13:
        return False
    
    # Supprimer les espaces et vérifier que ce sont des chiffres
    card_number = card_number.replace(' ', '')
    if not card_number.isdigit():
        return False
    
    # Algorithme de Luhn
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10
    
    return luhn_checksum(card_number) == 0


def validate_expiry_date(expiry_date):
    """
    Validation de la date d'expiration
    """
    if not expiry_date or len(expiry_date) != 5:
        return False
    
    try:
        month, year = expiry_date.split('/')
        month = int(month)
        year = int('20' + year)
        
        if month < 1 or month > 12:
            return False
        
        current_date = datetime.now()
        if year < current_date.year or (year == current_date.year and month < current_date.month):
            return False
        
        return True
    except:
        return False


def get_card_brand(card_number):
    """
    Détermine la marque de la carte
    """
    card_number = card_number.replace(' ', '')
    
    if card_number.startswith('4'):
        return 'visa'
    elif card_number.startswith(('5', '2')):
        return 'mastercard'
    elif card_number.startswith('3'):
        return 'amex'
    else:
        return 'unknown'


def simulate_payment_gateway(card_number, expiry_date, cvv, amount):
    """
    Simulation d'une passerelle de paiement
    """
    # For testing purposes, always return success
    return {
        'success': True,
        'transaction_id': f"TXN_{uuid.uuid4().hex[:8].upper()}",
        'message': 'Paiement traité avec succès'
    }


def simulate_paypal_payment(email, amount):
    """
    Simulation d'un paiement PayPal
    """
    import random
    
    # 95% de chance de succès pour la démo
    if random.random() < 0.95:
        return {
            'success': True,
            'transaction_id': f"PP_{uuid.uuid4().hex[:8].upper()}",
            'message': 'Paiement PayPal traité avec succès'
        }
    else:
        return {
            'success': False,
            'message': 'Erreur de connexion PayPal'
        }
