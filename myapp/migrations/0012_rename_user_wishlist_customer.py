# Generated by Django 4.1.7 on 2023-06-08 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_wishlist'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wishlist',
            old_name='user',
            new_name='customer',
        ),
    ]