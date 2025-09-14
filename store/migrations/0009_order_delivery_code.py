# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_alter_payment_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_code',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Delivery Code'),
        ),
    ]

