# Generated by Django 5.1.7 on 2025-03-11 07:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0004_alter_ordertable_status_alter_products_price'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ordertable',
            options={'verbose_name': 'Стол заказов', 'verbose_name_plural': 'Столы заказов'},
        ),
        migrations.RemoveField(
            model_name='ordertable',
            name='count',
        ),
        migrations.RemoveField(
            model_name='ordertable',
            name='price',
        ),
        migrations.RemoveField(
            model_name='ordertable',
            name='product',
        ),
        migrations.RemoveField(
            model_name='ordertable',
            name='sum',
        ),
        migrations.AlterField(
            model_name='ordertable',
            name='status',
            field=models.CharField(choices=[('paid', 'Оплачено'), ('unpaid', 'Неоплачено'), ('canceled', 'Отменено')], default='unpaid', max_length=10, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='products',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена'),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(verbose_name='Количество')),
                ('price', models.DecimalField(decimal_places=2, editable=False, max_digits=10, verbose_name='Цена')),
                ('sum', models.DecimalField(decimal_places=2, editable=False, max_digits=10, verbose_name='Сумма')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='directory.ordertable', verbose_name='Заказ')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='directory.products', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Элемент заказа',
                'verbose_name_plural': 'Элементы заказа',
            },
        ),
        migrations.AddField(
            model_name='ordertable',
            name='products',
            field=models.ManyToManyField(through='directory.OrderItem', to='directory.products', verbose_name='Товары'),
        ),
    ]
