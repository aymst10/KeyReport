from django import forms
from .models import Product, Category, ProductReview, Payment, Order
from .payment_gateway import PaymentService


class ProductForm(forms.ModelForm):
    """Form for creating and updating products."""
    
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'category', 'description', 'short_description',
            'price', 'sale_price', 'sku', 'stock_quantity', 'min_stock_level',
            'brand', 'model', 'condition', 'warranty_months',
            'main_image', 'additional_images', 'is_active', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_stock_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'warranty_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'main_image': forms.FileInput(attrs={'class': 'form-control'}),
            'additional_images': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_sale_price(self):
        """Validate sale price is less than regular price."""
        sale_price = self.cleaned_data.get('sale_price')
        price = self.cleaned_data.get('price')
        
        if sale_price and price and sale_price >= price:
            raise forms.ValidationError('Sale price must be less than regular price.')
        
        return sale_price
    
    def clean_stock_quantity(self):
        """Validate stock quantity is non-negative."""
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if stock_quantity < 0:
            raise forms.ValidationError('Stock quantity cannot be negative.')
        return stock_quantity


class CategoryForm(forms.ModelForm):
    """Form for creating and updating categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductSearchForm(forms.Form):
    """Form for product search and filtering."""
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '0.01'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '0.01'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('', 'Sort by'),
            ('newest', 'Newest First'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
            ('name', 'Name A-Z'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        """Validate price range."""
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError('Minimum price cannot be greater than maximum price.')
        
        return cleaned_data


class AddToCartForm(forms.Form):
    """Form for adding products to cart."""
    
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1'
        })
    )


class CheckoutForm(forms.Form):
    """Form for checkout process."""
    
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your shipping address'
        })
    )
    
    shipping_city = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    
    shipping_state = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State/Province'
        })
    )
    
    shipping_zip_code = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ZIP/Postal Code'
        })
    )
    
    shipping_country = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Country'
        })
    )
    
    contact_phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '06XX XXX XXX'
        }),
        help_text='Format: 06XX XXX XXX (numéro marocain)'
    )
    
    contact_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    customer_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes (optional)'
        })
    )
    
    def clean_contact_phone(self):
        """Validate international phone number."""
        phone = self.cleaned_data.get('contact_phone')
        if phone:
            # Remove all non-digit characters
            phone_digits = ''.join(filter(str.isdigit, phone))
            
            # Check if it's a valid phone number (9 digits for Morocco without country code)
            if len(phone_digits) == 9 and (phone_digits.startswith('6') or phone_digits.startswith('7')):
                return phone
            elif len(phone_digits) == 10 and phone_digits.startswith('06'):
                # Remove leading 0 for consistency
                return phone_digits[1:]
            elif len(phone_digits) == 12 and phone_digits.startswith('2126'):
                # Remove country code for consistency
                return phone_digits[3:]
            else:
                raise forms.ValidationError(
                    'Veuillez entrer un numéro de téléphone valide'
                )
        return phone


class PaymentMethodForm(forms.Form):
    """Form for payment method selection."""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Paiement à la Livraison'),
        ('cih_bank', 'CIH Bank'),
        ('attijariwafa', 'Attijariwafa Bank'),
        ('bmce', 'BMCE Bank'),
        ('bank_transfer', 'Virement Bancaire'),
        ('visa', 'Carte Bancaire (Visa)'),
        ('mastercard', 'Carte Bancaire (Mastercard)'),
        ('paypal', 'PayPal'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial='cash'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom styling to radio buttons
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'form-check-input'})


class ProductReviewForm(forms.ModelForm):
    """Form for product reviews."""
    
    class Meta:
        model = ProductReview
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-select',
                'id': 'rating-select'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Give your review a title',
                'maxlength': '200'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this product...',
                'maxlength': '1000'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].choices = [
            ('', 'Select Rating'),
            (5, '★★★★★ Excellent'),
            (4, '★★★★☆ Very Good'),
            (3, '★★★☆☆ Good'),
            (2, '★★☆☆☆ Fair'),
            (1, '★☆☆☆☆ Poor'),
        ]
    
    def clean_comment(self):
        """Validate comment length."""
        comment = self.cleaned_data.get('comment')
        if comment and len(comment.strip()) < 10:
            raise forms.ValidationError('Please provide a more detailed review (at least 10 characters).')
        return comment
    
    def clean_title(self):
        """Validate title length."""
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 3:
            raise forms.ValidationError('Please provide a more descriptive title (at least 3 characters).')
        return title


class PaymentMethodForm(forms.Form):
    """Form for selecting payment method."""
    
    payment_method = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'}),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get available payment methods
        payment_methods = PaymentService.get_payment_methods()
        choices = []
        for method_key, method_data in payment_methods.items():
            if method_data['available']:
                choices.append((method_key, method_data['name']))
        self.fields['payment_method'].choices = choices


class CardPaymentForm(forms.Form):
    """Form for card payment details."""
    
    card_number = forms.CharField(
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'data-mask': '0000 0000 0000 0000'
        })
    )
    
    expiry_date = forms.CharField(
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/AA',
            'pattern': '[0-9]{2}/[0-9]{2}'
        })
    )
    
    cvv = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'data-mask': '000'
        })
    )
    
    cardholder_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cardholder Name'
        })
    )
    
    def clean_card_number(self):
        """Validate and format card number."""
        card_number = self.cleaned_data.get('card_number', '').replace(' ', '')
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            raise forms.ValidationError('Please enter a valid card number.')
        return card_number
    
    def clean_cvv(self):
        """Validate CVV."""
        cvv = self.cleaned_data.get('cvv', '')
        if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
            raise forms.ValidationError('Please enter a valid CVV.')
        return cvv
    
    def clean_expiry_date(self):
        """Validate expiry date format MM/AA."""
        expiry_date = self.cleaned_data.get('expiry_date', '')
        
        if not expiry_date:
            raise forms.ValidationError('Please enter the expiry date.')
        
        # Check format MM/AA
        if len(expiry_date) != 5 or expiry_date[2] != '/':
            raise forms.ValidationError('Please enter expiry date in MM/AA format.')
        
        try:
            month = int(expiry_date[:2])
            year = int('20' + expiry_date[3:])
            
            # Validate month
            if month < 1 or month > 12:
                raise forms.ValidationError('Month must be between 01 and 12.')
            
            # Validate year (not in the past)
            from datetime import datetime
            current_date = datetime.now()
            if year < current_date.year or (year == current_date.year and month < current_date.month):
                raise forms.ValidationError('Card has expired.')
            
            # Check if year is not too far in the future (e.g., 10 years)
            if year > current_date.year + 10:
                raise forms.ValidationError('Expiry year is too far in the future.')
                
        except ValueError:
            raise forms.ValidationError('Please enter valid month and year.')
        
        return expiry_date


class BankTransferForm(forms.Form):
    """Form for bank transfer payment."""
    
    bank_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Bank Name'
        })
    )
    
    account_holder = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Account Holder Name'
        })
    )
    
    reference_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Transaction Reference (Optional)'
        })
    )


class PayPalForm(forms.Form):
    """Form for PayPal payment."""
    
    paypal_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your PayPal Email'
        })
    )


class PaymentMethodForm(forms.Form):
    """Form for selecting payment method."""
    
    PAYMENT_METHOD_CHOICES = [
        # Cartes bancaires
        ('credit_card', '💳 Credit Card'),
        ('debit_card', '💳 Debit Card'),
        ('visa', '💳 Visa'),
        ('mastercard', '💳 Mastercard'),
        
        # Paiements numériques
        ('paypal', '🅿️ PayPal'),
        ('apple_pay', '🍎 Apple Pay'),
        ('google_pay', '📱 Google Pay'),
        
        # Paiement à la livraison
        ('cash_delivery', '💰 Cash on Delivery'),
        
        # Services de paiement marocains
        ('wafacash', '🏦 WafaCash'),
        ('cashplus', '💸 CashPlus'),
        ('baridbanque', '🏛️ Barid Bank'),
        
        # Virements bancaires
        ('bank_transfer', '🏦 Bank Transfer'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True
    )


class PaymentConfirmationForm(forms.Form):
    """Form for payment confirmation."""
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    newsletter_subscription = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class OrderForm(forms.ModelForm):
    """Form for collecting order and shipping information."""
    
    class Meta:
        model = Order
        fields = [
            'shipping_address', 'shipping_city', 'shipping_state', 
            'shipping_zip_code', 'shipping_country', 'contact_phone', 
            'contact_email', 'customer_notes'
        ]
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Adresse complète de livraison'
            }),
            'shipping_city': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ville'
            }),
            'shipping_state': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Région/État'
            }),
            'shipping_zip_code': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Code postal'
            }),
            'shipping_country': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Pays',
                'value': 'Maroc'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+212 6XX XXX XXX'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'votre@email.com'
            }),
            'customer_notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Instructions spéciales pour la livraison (optionnel)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill with user information if available
        if user and user.is_authenticated:
            if not self.instance.pk:  # Only for new orders
                self.fields['contact_email'].initial = user.email
                if hasattr(user, 'phone') and user.phone:
                    self.fields['contact_phone'].initial = user.phone
                if hasattr(user, 'address') and user.address:
                    self.fields['shipping_address'].initial = user.address
    
    def clean_contact_phone(self):
        """Validate phone number format."""
        phone = self.cleaned_data.get('contact_phone', '').strip()
        if not phone:
            raise forms.ValidationError('Le numéro de téléphone est requis pour la livraison.')
        
        # Basic phone validation for Morocco
        if not phone.startswith('+212') and not phone.startswith('0'):
            raise forms.ValidationError('Veuillez entrer un numéro de téléphone marocain valide.')
        
        return phone
    
    def clean_contact_email(self):
        """Validate email format."""
        email = self.cleaned_data.get('contact_email', '').strip()
        if not email:
            raise forms.ValidationError('L\'email de contact est requis pour la livraison.')
        return email
    
    def clean_shipping_address(self):
        """Validate shipping address."""
        address = self.cleaned_data.get('shipping_address', '').strip()
        if not address:
            raise forms.ValidationError('L\'adresse de livraison est requise.')
        if len(address) < 10:
            raise forms.ValidationError('Veuillez fournir une adresse de livraison plus détaillée.')
        return address
