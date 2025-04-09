import logging
from django.utils import timezone

from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator

#
class Table(models.Model):
    name = models.CharField(max_length=100, verbose_name='Стол', default='Стол')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Стол'


class Type(models.Model):
    name = models.CharField(max_length=25, unique=True, verbose_name='Тип')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип"
        verbose_name_plural = "Типы"


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование')

    def __str__(self):
        return f'category {self.name}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Products(models.Model):
    name = models.CharField(max_length=150, verbose_name='Наименования')
    description = models.TextField(null=True, blank=True, verbose_name='Описание товара')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', blank=True, null=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE, blank=True, null=True, verbose_name='Категория')
    type = models.ForeignKey('Type', on_delete=models.PROTECT, default="шт", verbose_name='Тип')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = 'Товары'


logger = logging.getLogger(__name__)

class OrderTable(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Оплачено'),
        ('unpaid', 'Неоплачено'),
        ('canceled', 'Отменено'),
    ]

    date = models.DateTimeField(default=timezone.now)
    table = models.ForeignKey('Table', on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')

    def __str__(self):
        return f'Заказ #{self.id}'

    def total_sum(self):
        return self.orderitem_set.aggregate(total=Sum('sum'))['total'] or 0

    def save(self, *args, **kwargs):
        old_status = None
        if self.pk:
            old_status = OrderTable.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        if self.status == 'paid' and old_status != 'paid':
            CashReceiptOrder.objects.create(order=self, sum=self.total_sum())
            logger.info(f"Создан ПКО для заказа {self.id}")
        elif self.status in ['canceled', 'unpaid'] and old_status == 'paid':
            CashReceiptOrder.objects.filter(order=self).delete()
            logger.info(f"Удален ПКО для заказа {self.id}")
class OrderItem(models.Model):
    order = models.ForeignKey(OrderTable, on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Products, on_delete=models.PROTECT, verbose_name='Товар')
    count = models.IntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', editable=False)
    sum = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name='Сумма')

    def __str__(self):
        return f'{self.product.name} в заказе {self.order.id}'

    def save(self, *args, **kwargs):
        self.price = self.product.price
        self.sum = self.price * self.count
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

class CashReceiptOrder(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(OrderTable, on_delete=models.CASCADE, related_name='cash_orders')
    sum = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"ПКО №{self.id} (заказ {self.order.id})"

    class Meta:
        verbose_name = "Приходный кассовый ордер"
        verbose_name_plural = "Приходные кассовые ордера"