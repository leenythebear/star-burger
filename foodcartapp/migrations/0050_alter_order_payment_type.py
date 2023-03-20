# Generated by Django 3.2.15 on 2023-03-20 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('CASH', 'Наличными курьеру'), ('CARD', 'Картой онлайн'), ('NOT_CHOSEN', 'Не выбран')], default='NOT_CHOSEN', max_length=50, verbose_name='Способ оплаты'),
        ),
    ]
