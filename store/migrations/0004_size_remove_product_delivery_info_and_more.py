# Generated by Django 5.1.3 on 2024-12-07 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_product_category_product_delivery_info_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size_label', models.CharField(max_length=10)),
                ('category', models.CharField(choices=[('clothes', 'Clothes'), ('shoes', 'Shoes')], max_length=10)),
            ],
        ),
        migrations.RemoveField(
            model_name='product',
            name='delivery_info',
        ),
        migrations.RemoveField(
            model_name='product',
            name='return_info',
        ),
        migrations.RemoveField(
            model_name='product',
            name='subcategory',
        ),
        migrations.AddField(
            model_name='product',
            name='delivery_returns',
            field=models.TextField(default='No return policy specified.'),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('clothes', 'Clothes'), ('shoes', 'Shoes'), ('books', 'Books'), ('watches', 'Watches')], max_length=10),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(),
        ),
        migrations.RemoveField(
            model_name='product',
            name='sizes',
        ),
        migrations.AddField(
            model_name='product',
            name='sizes',
            field=models.ManyToManyField(blank=True, to='store.size'),
        ),
    ]
