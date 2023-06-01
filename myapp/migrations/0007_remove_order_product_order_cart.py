# Generated by Django 4.1.7 on 2023-05-31 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_order_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='product',
        ),
        migrations.AddField(
            model_name='order',
            name='cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.cart'),
        ),
    ]
