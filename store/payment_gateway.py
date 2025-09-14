"""
Payment Gateway Integration for KeyReport IT Store
Supports multiple payment methods including Moroccan banks and international gateways
"""

import json
import hashlib
import hmac
import time
from decimal import Decimal
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from .models import Payment, Order


class PaymentGateway:
    """Base payment gateway class."""
    
    def __init__(self):
        self.gateway_name = "base"
    
    def process_payment(self, payment: Payment, **kwargs) -> Dict[str, Any]:
        """Process a payment through the gateway."""
        raise NotImplementedError("Subclasses must implement process_payment")
    
    def verify_payment(self, payment: Payment, **kwargs) -> Dict[str, Any]:
        """Verify a payment status."""
        raise NotImplementedError("Subclasses must implement verify_payment")
    
    def refund_payment(self, payment: Payment, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Refund a payment."""
        raise NotImplementedError("Subclasses must implement refund_payment")


class StripeGateway(PaymentGateway):
    """Stripe payment gateway integration."""
    
    def __init__(self):
        super().__init__()
        self.gateway_name = "stripe"
        # In production, these would come from settings
        self.publishable_key = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', 'pk_test_...')
        self.secret_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_...')
    
    def process_payment(self, payment: Payment, **kwargs) -> Dict[str, Any]:
        """Process payment through Stripe."""
        try:
            # Simulate Stripe API call
            payment_intent_data = {
                'amount': int(payment.amount * 100),  # Convert to cents
                'currency': 'mad',  # Moroccan Dirham
                'payment_method': kwargs.get('payment_method_id'),
                'confirmation_method': 'manual',
                'confirm': True,
            }
            
            # Simulate successful payment
            if kwargs.get('payment_method_id'):
                payment.status = 'completed'
                payment.processed_at = timezone.now()
                payment.transaction_id = f"pi_{hashlib.md5(str(payment.id).encode()).hexdigest()[:24]}"
                payment.processor_response = {
                    'payment_intent_id': payment.transaction_id,
                    'status': 'succeeded',
                    'amount_received': int(payment.amount * 100),
                    'currency': 'mad'
                }
                payment.save()
                
                return {
                    'success': True,
                    'transaction_id': payment.transaction_id,
                    'status': 'completed',
                    'message': 'Payment processed successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Payment method required',
                    'message': 'Please provide a valid payment method'
                }
                
        except Exception as e:
            payment.status = 'failed'
            payment.processor_response = {'error': str(e)}
            payment.save()
            
            return {
                'success': False,
                'error': str(e),
                'message': 'Payment processing failed'
            }
    
    def verify_payment(self, payment: Payment, **kwargs) -> Dict[str, Any]:
        """Verify payment status with Stripe."""
        # Simulate API call to Stripe
        return {
            'success': True,
            'status': payment.status,
            'transaction_id': payment.transaction_id
        }
    
    def refund_payment(self, payment: Payment, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Refund payment through Stripe."""
        refund_amount = amount or payment.amount
        
        # Simulate refund
        payment.status = 'refunded'
        payment.processor_response['refund'] = {
            'amount': float(refund_amount),
            'status': 'succeeded',
            'refund_id': f"re_{hashlib.md5(str(payment.id).encode()).hexdigest()[:24]}"
        }
        payment.save()
        
        return {
            'success': True,
            'refund_amount': refund_amount,
            'message': 'Refund processed successfully'
        }


class PayPalGateway(PaymentGateway):
    """PayPal payment gateway integration."""
    
    def __init__(self):
        super().__init__()
        self.gateway_name = "paypal"
        self.client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', '')
    
    def process_payment(self, payment: Payment, **kwargs) -> Dict[str, Any]:
        """Process payment through PayPal."""
        try:
            # Simulate PayPal API call
            payment.status = 'processing'
            payment.save()
            
            # Simulate successful payment
            payment.status = 'completed'
            payment.processed_at = timezone.now()
            payment.transaction_id = f"PAYID-{hashlib.md5(str(payment.id).encode()).hexdigest()[:17].upper()}"
            payment.processor_response = {
                'payment_id': payment.transaction_id,
                'state': 'approved',
                'amount': {
                    'total': str(payment.amount),
                    'currency': 'MAD'
                }
            }
            payment.save()
            
            return {
                'success': True,
                'transaction_id': payment.transaction_id,
                'status': 'completed',
                'message': 'PayPal payment processed successfully'
            }
            
        except Exception as e:
            payment.status = 'failed'
            payment.processor_response = {'error': str(e)}
            payment.save()
            
            return {
                'success': False,
                'error': str(e),
                'message': 'PayPal payment failed'
            }
    
    def verify_payment(self, payment: Payment, **kwargs) -> Dict[str, Any]:
        """Verify payment status with PayPal."""
        return {
            'success': True,
            'status': payment.status,
            'transaction_id': payment.transaction_id
        }
    
    def refund_payment(self, payment: Payment, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Refund payment through PayPal."""
        refund_amount = amount or payment.amount
        
        payment.status = 'refunded'
        payment.processor_response['refund'] = {
            'amount': str(refund_amount),
            'status': 'completed',
            'refund_id': f"REF-{hashlib.md5(str(payment.id).encode()).hexdigest()[:17].upper()}"
        }
        payment.save()
        
        return {
            'success': True,
            'refund_amount': refund_amount,
            'message': 'PayPal refund processed successfully'
        }


class MoroccanBankGateway(PaymentGateway):
    """Moroccan bank payment gateway (CIH, Attijariwafa, BMCE)."""
    
    def __init__(self, bank_name: str):
        super().__init__()
        self.gateway_name = f"moroccan_bank_{bank_name.lower()}"
        self.bank_name = bank_name
    
    def process_payment(self, payment: Payment, **kwargs) -> Dict[str, Any]:
        """Process payment through Moroccan bank."""
        try:
            # Simulate bank API call
            payment.status = 'processing'
            payment.save()
            
            # Simulate successful payment
            payment.status = 'completed'
            payment.processed_at = timezone.now()
            payment.transaction_id = f"{self.bank_name.upper()}-{hashlib.md5(str(payment.id).encode()).hexdigest()[:12].upper()}"
            payment.processor_response = {
                'bank': self.bank_name,
                'transaction_id': payment.transaction_id,
                'status': 'approved',
                'amount': float(payment.amount),
                'currency': 'MAD'
            }
            payment.save()
            
            return {
                'success': True,
                'transaction_id': payment.transaction_id,
                'status': 'completed',
                'message': f'{self.bank_name} payment processed successfully'
            }
            
        except Exception as e:
            payment.status = 'failed'
            payment.processor_response = {'error': str(e)}
            payment.save()
            
            return {
                'success': False,
                'error': str(e),
                'message': f'{self.bank_name} payment failed'
            }
    
    def verify_payment(self, payment: Payment, **kwargs) -> Dict[str, Any]:
        """Verify payment status with bank."""
        return {
            'success': True,
            'status': payment.status,
            'transaction_id': payment.transaction_id,
            'bank': self.bank_name
        }
    
    def refund_payment(self, payment: Payment, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Refund payment through bank."""
        refund_amount = amount or payment.amount
        
        payment.status = 'refunded'
        payment.processor_response['refund'] = {
            'amount': float(refund_amount),
            'status': 'completed',
            'refund_id': f"{self.bank_name.upper()}-REF-{hashlib.md5(str(payment.id).encode()).hexdigest()[:8].upper()}"
        }
        payment.save()
        
        return {
            'success': True,
            'refund_amount': refund_amount,
            'message': f'{self.bank_name} refund processed successfully'
        }


class CashOnDeliveryGateway(PaymentGateway):
    """Cash on Delivery payment gateway."""
    
    def __init__(self):
        super().__init__()
        self.gateway_name = "cash_on_delivery"
    
    def process_payment(self, payment: Payment, **kwargs) -> Dict[str, Any]:
        """Process cash on delivery payment."""
        # COD payments are always pending until delivery
        payment.status = 'pending'
        payment.transaction_id = f"COD-{hashlib.md5(str(payment.id).encode()).hexdigest()[:12].upper()}"
        payment.processor_response = {
            'method': 'cash_on_delivery',
            'status': 'pending_confirmation',
            'delivery_instructions': 'Payment to be collected upon delivery'
        }
        payment.save()
        
        return {
            'success': True,
            'transaction_id': payment.transaction_id,
            'status': 'pending',
            'message': 'Cash on delivery order created. Payment will be collected upon delivery.'
        }
    
    def verify_payment(self, payment: Payment, **kwargs) -> Dict[str, Any]:
        """Verify COD payment status."""
        return {
            'success': True,
            'status': payment.status,
            'transaction_id': payment.transaction_id,
            'method': 'cash_on_delivery'
        }
    
    def refund_payment(self, payment: Payment, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Refund COD payment (cancel order)."""
        payment.status = 'refunded'
        payment.processor_response['refund'] = {
            'amount': float(amount or payment.amount),
            'status': 'cancelled',
            'reason': 'Order cancelled before delivery'
        }
        payment.save()
        
        return {
            'success': True,
            'refund_amount': amount or payment.amount,
            'message': 'Cash on delivery order cancelled'
        }


class PaymentGatewayFactory:
    """Factory class to create appropriate payment gateway instances."""
    
    @staticmethod
    def get_gateway(payment_method: str) -> PaymentGateway:
        """Get the appropriate payment gateway for the payment method."""
        gateway_map = {
            # Cartes bancaires
            'credit_card': StripeGateway,
            'debit_card': StripeGateway,
            'visa': StripeGateway,
            'mastercard': StripeGateway,
            
            # Paiements numériques
            'paypal': PayPalGateway,
            'apple_pay': StripeGateway,
            'google_pay': StripeGateway,
            
            # Paiement à la livraison
            'cash_delivery': CashOnDeliveryGateway,
            
            # Services marocains
            'wafacash': lambda: MoroccanBankGateway('WafaCash'),
            'cashplus': lambda: MoroccanBankGateway('CashPlus'),
            'baridbanque': lambda: MoroccanBankGateway('Barid Bank'),
            
            # Virements bancaires
            'bank_transfer': lambda: MoroccanBankGateway('Bank Transfer'),
            'cih_bank': lambda: MoroccanBankGateway('CIH'),
            'attijariwafa': lambda: MoroccanBankGateway('Attijariwafa'),
            'bmce': lambda: MoroccanBankGateway('BMCE'),
            
            # Méthodes legacy
            'cash': CashOnDeliveryGateway,
            'stripe': StripeGateway,
        }
        
        gateway_class = gateway_map.get(payment_method)
        if gateway_class:
            return gateway_class()
        else:
            # Default to Stripe for unknown card payments
            if payment_method in ['visa', 'mastercard', 'apple_pay', 'google_pay', 'credit_card', 'debit_card']:
                return StripeGateway()
            else:
                return CashOnDeliveryGateway()


class MoroccanShippingService:
    """Moroccan shipping service with regional pricing."""
    
    @staticmethod
    def get_shipping_cost(region: str, weight: float = 1.0) -> Decimal:
        """Calculate shipping cost based on Moroccan region."""
        base_costs = {
            'Casablanca-Settat': Decimal('0.00'),  # Free shipping in Casablanca
            'Rabat-Salé-Kénitra': Decimal('15.00'),
            'Fès-Meknès': Decimal('25.00'),
            'Marrakech-Safi': Decimal('30.00'),
            'Tanger-Tétouan-Al Hoceïma': Decimal('35.00'),
            'Oriental': Decimal('40.00'),
            'Béni Mellal-Khénifra': Decimal('30.00'),
            'Souss-Massa': Decimal('45.00'),
            'Guelmim-Oued Noun': Decimal('60.00'),
            'Laâyoune-Sakia El Hamra': Decimal('80.00'),
            'Dakhla-Oued Ed-Dahab': Decimal('100.00'),
            'Drâa-Tafilalet': Decimal('50.00'),
        }
        
        base_cost = base_costs.get(region, Decimal('50.00'))
        
        # Add weight-based pricing (5 MAD per kg)
        weight_cost = Decimal(str(weight)) * Decimal('5.00')
        
        return base_cost + weight_cost
    
    @staticmethod
    def get_delivery_time(region: str) -> str:
        """Get estimated delivery time for Moroccan regions."""
        delivery_times = {
            'Casablanca-Settat': '1-2 jours',
            'Rabat-Salé-Kénitra': '2-3 jours',
            'Fès-Meknès': '3-4 jours',
            'Marrakech-Safi': '3-5 jours',
            'Tanger-Tétouan-Al Hoceïma': '4-5 jours',
            'Oriental': '4-6 jours',
            'Béni Mellal-Khénifra': '3-5 jours',
            'Souss-Massa': '5-7 jours',
            'Guelmim-Oued Noun': '7-10 jours',
            'Laâyoune-Sakia El Hamra': '10-14 jours',
            'Dakhla-Oued Ed-Dahab': '14-21 jours',
            'Drâa-Tafilalet': '6-8 jours',
        }
        
        return delivery_times.get(region, '5-7 jours')


class PaymentService:
    """Service class to handle payment operations."""
    
    @staticmethod
    def process_payment(payment: Payment, **kwargs) -> Dict[str, Any]:
        """Process a payment using the appropriate gateway."""
        gateway = PaymentGatewayFactory.get_gateway(payment.payment_method)
        return gateway.process_payment(payment, **kwargs)
    
    @staticmethod
    def verify_payment(payment: Payment, **kwargs) -> Dict[str, Any]:
        """Verify a payment using the appropriate gateway."""
        gateway = PaymentGatewayFactory.get_gateway(payment.payment_method)
        return gateway.verify_payment(payment, **kwargs)
    
    @staticmethod
    def refund_payment(payment: Payment, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Refund a payment using the appropriate gateway."""
        gateway = PaymentGatewayFactory.get_gateway(payment.payment_method)
        return gateway.refund_payment(payment, amount)
    
    @staticmethod
    def get_payment_methods() -> Dict[str, Dict[str, Any]]:
        """Get available payment methods with their details."""
        return {
            # Cartes bancaires
            'credit_card': {
                'name': 'Credit Card',
                'description': 'Pay with your credit card',
                'icon': 'fas fa-credit-card',
                'available': True,
                'processing_fee': 2.5
            },
            'debit_card': {
                'name': 'Debit Card',
                'description': 'Pay with your debit card',
                'icon': 'fas fa-credit-card',
                'available': True,
                'processing_fee': 2.5
            },
            'visa': {
                'name': 'Visa',
                'description': 'Pay with your Visa card',
                'icon': 'fab fa-cc-visa',
                'available': True,
                'processing_fee': 2.5
            },
            'mastercard': {
                'name': 'Mastercard',
                'description': 'Pay with your Mastercard',
                'icon': 'fab fa-cc-mastercard',
                'available': True,
                'processing_fee': 2.5
            },
            
            # Paiements numériques
            'paypal': {
                'name': 'PayPal',
                'description': 'Pay with your PayPal account',
                'icon': 'fab fa-paypal',
                'available': True,
                'processing_fee': 3.4
            },
            'apple_pay': {
                'name': 'Apple Pay',
                'description': 'Pay with Apple Pay',
                'icon': 'fab fa-apple-pay',
                'available': True,
                'processing_fee': 2.5
            },
            'google_pay': {
                'name': 'Google Pay',
                'description': 'Pay with Google Pay',
                'icon': 'fab fa-google-pay',
                'available': True,
                'processing_fee': 2.5
            },
            
            # Paiement à la livraison
            'cash_delivery': {
                'name': 'Cash on Delivery',
                'description': 'Pay when your order is delivered',
                'icon': 'fas fa-money-bill-wave',
                'available': True,
                'processing_fee': 0
            },
            
            # Services marocains
            'wafacash': {
                'name': 'WafaCash',
                'description': 'Pay with WafaCash service',
                'icon': 'fas fa-university',
                'available': True,
                'processing_fee': 0
            },
            'cashplus': {
                'name': 'CashPlus',
                'description': 'Pay with CashPlus service',
                'icon': 'fas fa-university',
                'available': True,
                'processing_fee': 0
            },
            'baridbanque': {
                'name': 'Barid Bank',
                'description': 'Pay with Barid Bank service',
                'icon': 'fas fa-university',
                'available': True,
                'processing_fee': 0
            },
            
            # Virements bancaires
            'bank_transfer': {
                'name': 'Bank Transfer',
                'description': 'Direct bank transfer',
                'icon': 'fas fa-university',
                'available': True,
                'processing_fee': 0
            },
            'cih_bank': {
                'name': 'CIH Bank',
                'description': 'Pay with your CIH Bank account',
                'icon': 'fas fa-credit-card',
                'available': True,
                'processing_fee': 0
            },
            'attijariwafa': {
                'name': 'Attijariwafa Bank',
                'description': 'Pay with your Attijariwafa Bank account',
                'icon': 'fas fa-credit-card',
                'available': True,
                'processing_fee': 0
            },
            'bmce': {
                'name': 'BMCE Bank',
                'description': 'Pay with your BMCE Bank account',
                'icon': 'fas fa-credit-card',
                'available': True,
                'processing_fee': 0
            },
            
            # Méthodes legacy (pour compatibilité)
            'cash': {
                'name': 'Cash on Delivery',
                'description': 'Pay when your order is delivered',
                'icon': 'fas fa-money-bill-wave',
                'available': True,
                'processing_fee': 0
            },
            'stripe': {
                'name': 'Stripe',
                'description': 'Secure online payment',
                'icon': 'fas fa-shield-alt',
                'available': True,
                'processing_fee': 2.9
            }
        }

