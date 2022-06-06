# Generated by Django 4.0.5 on 2022-06-05 17:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartproduct',
            name='quantity',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(999)], verbose_name='Quantity'),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='quantity',
            field=models.PositiveSmallIntegerField(verbose_name='Quantity'),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='sold_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Sold price'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99999999)], verbose_name='Sold price'),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock_quantity',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(32000)], verbose_name='Stock quantity'),
        ),
    ]