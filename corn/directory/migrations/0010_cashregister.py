# Generated by Django 5.1.7 on 2025-03-22 19:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0009_alter_ordertable_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashRegister',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sum', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cashregister_date', to='directory.orderitem', verbose_name='Дата')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cashregister_order', to='directory.orderitem', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': 'Приходный кассовый ордер',
            },
        ),
    ]
