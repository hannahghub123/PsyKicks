# Generated by Django 4.2.2 on 2023-06-22 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_alter_cart_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='status',
            field=models.CharField(choices=[('Publish', 'Publish'), ('Draft', 'Draft')], default=1, max_length=200),
            preserve_default=False,
        ),
    ]
