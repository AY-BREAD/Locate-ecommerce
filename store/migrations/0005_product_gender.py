# Generated by Django 5.1.3 on 2024-12-07 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_size_remove_product_delivery_info_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female')], max_length=10, null=True),
        ),
    ]
