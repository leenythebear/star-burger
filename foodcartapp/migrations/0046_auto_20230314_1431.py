# Generated by Django 3.2.15 on 2023-03-14 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_order_responsible_restaurant'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('status',), 'verbose_name': 'заказ', 'verbose_name_plural': 'заказы'},
        ),
        migrations.AlterModelOptions(
            name='orderproducts',
            options={'verbose_name': 'товар в заказе', 'verbose_name_plural': 'товары в заказе '},
        ),
    ]
