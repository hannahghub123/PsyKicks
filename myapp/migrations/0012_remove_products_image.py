# Generated by Django 4.1.7 on 2023-05-27 07:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_rename_image1_products_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='image',
        ),
    ]
