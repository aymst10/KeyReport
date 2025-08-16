from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordResetDoneView, 
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
import random
import string

from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordResetForm,
    CustomSetPasswordForm, UserProfileForm, UserUpdateForm, EmailVerificationForm
)
from .models import CustomUser, UserProfile


def generate_verification_code():
    """Generate a random 6-digit verification code."""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(user, verification_code):
    """Send verification email to user."""
    subject = 'Verify Your Email - IT Store'
    message = f"""
    Hello {user.first_name},
    
    Thank you for registering with IT Store! Please use the following verification code to complete your registration:
    
    Verification Code: {verification_code}
    
    This code will expire in 24 hours.
    
    If you didn't request this registration, please ignore this email.
    
    Best regards,
    IT Store Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def signup(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create user but don't save yet
                    user = form.save(commit=False)
                    user.is_verified = False  # Email not verified yet
                    user.save()
                    
                    # Create user profile
                    UserProfile.objects.create(user=user)
                    
                    # Generate verification code
                    verification_code = generate_verification_code()
                    
                    # Store verification code in session (in production, use Redis/database)
                    request.session['verification_code'] = verification_code
                    request.session['user_email'] = user.email
                    
                    # Send verification email
                    if send_verification_email(user, verification_code):
                        messages.success(
                            request, 
                            'Registration successful! Please check your email for verification code.'
                        )
                        return redirect('users:verify_email')
                    else:
                        messages.error(
                            request, 
                            'Registration successful but verification email could not be sent. Please contact support.'
                        )
                        return redirect('users:login')
                        
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                return redirect('users:signup')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/signup.html', {'form': form})


def verify_email(request):
    """Email verification view."""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    user_email = request.session.get('user_email')
    if not user_email:
        messages.error(request, 'No pending verification found. Please register first.')
        return redirect('users:signup')
    
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            verification_code = form.cleaned_data['verification_code']
            stored_code = request.session.get('verification_code')
            
            if verification_code == stored_code:
                try:
                    user = CustomUser.objects.get(email=user_email)
                    user.is_verified = True
                    user.save()
                    
                    # Clear session data
                    del request.session['verification_code']
                    del request.session['user_email']
                    
                    messages.success(
                        request, 
                        'Email verified successfully! You can now log in.'
                    )
                    return redirect('users:login')
                    
                except CustomUser.DoesNotExist:
                    messages.error(request, 'User not found.')
                    return redirect('users:signup')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
    else:
        form = EmailVerificationForm()
    
    return render(request, 'users/verify_email.html', {'form': form, 'email': user_email})


class CustomLoginView(LoginView):
    """Custom login view."""
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        
        return super().form_valid(form)
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('users:dashboard')


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('store:home')


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view."""
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('users:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Custom password reset done view."""
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view."""
    template_name = 'users/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('users:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Custom password reset complete view."""
    template_name = 'users/password_reset_complete.html'


@login_required
def dashboard(request):
    """User dashboard view."""
    user = request.user
    context = {
        'user': user,
        'recent_orders': [],  # You can add order history here
        'support_tickets': [],  # You can add support tickets here
    }
    return render(request, 'users/dashboard.html', context)


@login_required
def profile(request):
    """User profile view."""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    }
    return render(request, 'users/profile.html', context)


class UserProfileDetailView(LoginRequiredMixin, DetailView):
    """User profile detail view."""
    model = UserProfile
    template_name = 'users/profile_detail.html'
    context_object_name = 'profile'
    
    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user)


@login_required
def change_password(request):
    """Change password view."""
    if request.method == 'POST':
        form = CustomSetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('users:profile')
    else:
        form = CustomSetPasswordForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})


def resend_verification(request):
    """Resend verification email view."""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    user_email = request.session.get('user_email')
    if not user_email:
        messages.error(request, 'No pending verification found.')
        return redirect('users:signup')
    
    try:
        user = CustomUser.objects.get(email=user_email)
        verification_code = generate_verification_code()
        request.session['verification_code'] = verification_code
        
        if send_verification_email(user, verification_code):
            messages.success(request, 'Verification code resent successfully!')
        else:
            messages.error(request, 'Failed to send verification email. Please try again.')
            
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('users:signup')
    
    return redirect('users:verify_email')
