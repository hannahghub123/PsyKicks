# Generated by Django 4.1.7 on 2023-06-12 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_remove_order_order_type_order_payment_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='complete',
        ),
        migrations.RemoveField(
            model_name='order',
            name='product',
        ),
        migrations.RemoveField(
            model_name='order',
            name='quantity',
        ),
        migrations.AddField(
            model_name='order',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('order_pending', 'Order_Pending'), ('order_confirmed', 'Order_Confirmed'), ('delivered', 'Delivered'), ('returned', 'Returned'), ('cancelled', 'Cancelled')], default='ordered', max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('cash_on_delivery', 'Cash_on_Delivery'), ('online_payment', 'Online_payment')], default='cash_on_delivery', max_length=100),
        ),
    ]
