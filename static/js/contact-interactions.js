/**
 * Contact Interactions JavaScript
 * Adds enhanced functionality to contact links
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add click tracking and enhanced interactions for contact links
    const contactLinks = document.querySelectorAll('.contact-link');
    
    contactLinks.forEach(link => {
        // Add click event listener
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            const linkText = this.textContent.trim();
            
            // Track the interaction
            trackContactInteraction(href, linkText);
            
            // Add visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
        
        // Add hover effects
        link.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
        
        // Add tooltip for phone numbers
        if (link.getAttribute('href').startsWith('tel:')) {
            link.setAttribute('title', 'Click to call');
            link.setAttribute('data-bs-toggle', 'tooltip');
        }
        
        // Add tooltip for email addresses
        if (link.getAttribute('href').startsWith('mailto:')) {
            link.setAttribute('title', 'Click to send email');
            link.setAttribute('data-bs-toggle', 'tooltip');
        }
        
        // Add tooltip for maps
        if (link.getAttribute('href').includes('maps.google.com')) {
            link.setAttribute('title', 'Click to open in Google Maps');
            link.setAttribute('data-bs-toggle', 'tooltip');
        }
    });
    
    // Initialize Bootstrap tooltips
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Add copy to clipboard functionality for phone numbers and emails
    contactLinks.forEach(link => {
        link.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            
            const href = this.getAttribute('href');
            let textToCopy = '';
            
            if (href.startsWith('tel:')) {
                textToCopy = href.replace('tel:', '');
            } else if (href.startsWith('mailto:')) {
                textToCopy = href.replace('mailto:', '');
            }
            
            if (textToCopy) {
                copyToClipboard(textToCopy);
                showCopyNotification(textToCopy);
            }
        });
    });
});

/**
 * Track contact interaction for analytics
 */
function trackContactInteraction(href, linkText) {
    // You can integrate with Google Analytics or other tracking services here
    console.log('Contact interaction:', {
        href: href,
        text: linkText,
        timestamp: new Date().toISOString()
    });
    
    // Example: Send to Google Analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', 'contact_click', {
            'contact_type': href.startsWith('tel:') ? 'phone' : 
                           href.startsWith('mailto:') ? 'email' : 'other',
            'contact_value': linkText
        });
    }
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        // Use modern clipboard API
        navigator.clipboard.writeText(text).then(() => {
            console.log('Copied to clipboard:', text);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            fallbackCopyToClipboard(text);
        });
    } else {
        // Fallback for older browsers
        fallbackCopyToClipboard(text);
    }
}

/**
 * Fallback copy to clipboard method
 */
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        console.log('Copied to clipboard (fallback):', text);
    } catch (err) {
        console.error('Failed to copy (fallback): ', err);
    }
    
    document.body.removeChild(textArea);
}

/**
 * Show copy notification
 */
function showCopyNotification(text) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'copy-notification';
    notification.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        Copied: ${text}
    `;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        font-size: 14px;
        font-weight: 500;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}























