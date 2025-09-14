from django.core.management.base import BaseCommand
from store.models import Product, ProductReview
from django.contrib.auth import get_user_model
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Add sample reviews for products'

    def handle(self, *args, **options):
        self.stdout.write('⭐ Adding sample reviews for products...')
        
        # Get all products
        products = Product.objects.all()
        
        # Create a test user if it doesn't exist
        test_user, created = User.objects.get_or_create(
            email='testuser@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write('✅ Created test user: testuser@example.com')
        
        # Sample review data
        sample_reviews = [
            {
                'rating': 5,
                'title': 'Excellent product!',
                'comment': 'This product exceeded my expectations. Great quality and performance. Highly recommended!'
            },
            {
                'rating': 4,
                'title': 'Very good quality',
                'comment': 'Good product overall. Works as expected and good value for money. Would buy again.'
            },
            {
                'rating': 5,
                'title': 'Perfect for my needs',
                'comment': 'Exactly what I was looking for. Easy to use and reliable. Great customer service too.'
            },
            {
                'rating': 3,
                'title': 'Average product',
                'comment': 'It works fine but nothing special. Price is reasonable for what you get.'
            },
            {
                'rating': 4,
                'title': 'Good value',
                'comment': 'Solid product with good build quality. Minor issues but overall satisfied with purchase.'
            },
            {
                'rating': 5,
                'title': 'Outstanding!',
                'comment': 'Amazing product! Fast delivery, excellent quality, and great support. Will definitely order again.'
            },
            {
                'rating': 2,
                'title': 'Could be better',
                'comment': 'Product works but has some issues. Not quite what I expected for the price.'
            },
            {
                'rating': 4,
                'title': 'Recommended',
                'comment': 'Good product with minor flaws. Overall satisfied and would recommend to others.'
            },
            {
                'rating': 5,
                'title': 'Best purchase ever!',
                'comment': 'Absolutely love this product! Great quality, fast shipping, and excellent customer service.'
            },
            {
                'rating': 3,
                'title': 'It\'s okay',
                'comment': 'Product is decent but nothing extraordinary. Does the job but could be improved.'
            }
        ]
        
        # Create multiple test users for reviews
        test_users = [test_user]
        for i in range(1, 5):
            user, created = User.objects.get_or_create(
                email=f'testuser{i}@example.com',
                defaults={
                    'first_name': f'Test{i}',
                    'last_name': 'User',
                    'is_active': True
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            test_users.append(user)
        
        # Add reviews to products
        review_count = 0
        for product in products:
            # Add 2-4 reviews per product
            num_reviews = random.randint(2, 4)
            
            for i in range(num_reviews):
                review_data = random.choice(sample_reviews)
                user = random.choice(test_users)
                
                # Check if user already reviewed this product
                if ProductReview.objects.filter(product=product, user=user).exists():
                    continue
                
                # Create review
                review = ProductReview.objects.create(
                    product=product,
                    user=user,
                    rating=review_data['rating'],
                    title=review_data['title'],
                    comment=review_data['comment'],
                    is_approved=True,
                    is_verified_purchase=random.choice([True, False])
                )
                
                review_count += 1
                self.stdout.write(f'✅ Added review for: {product.name} by {user.email}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Successfully added {review_count} sample reviews!')
        )
        
        # Show summary
        self.stdout.write('\n📊 Review Summary:')
        for product in products:
            if product.total_reviews > 0:
                self.stdout.write(f'  {product.name}: {product.average_rating}/5 ({product.total_reviews} reviews)')
        
        self.stdout.write(f'\n👤 Test user created: testuser@example.com (password: testpass123)')
