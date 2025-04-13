from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator
from django.utils import timezone

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


class OrderTable(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Оплачено'),
        ('unpaid', 'Неоплачено'),
        ('canceled', 'Отменено'),
    ]

    date = models.DateTimeField(default=timezone.now, verbose_name='Дата и время')
    table = models.ForeignKey(Table, on_delete=models.PROTECT, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='unpaid',
        verbose_name='Статус'
    )
    products = models.ManyToManyField(Products, through='OrderItem', verbose_name='Товары')

    def __str__(self):
        return f'Заказ {self.id} на столе {self.table}'

    def total_sum(self):
        return self.orderitem_set.aggregate(total=Sum('sum'))['total'] or 0

    def products_list(self):
        return ", ".join([item.product.name for item in self.orderitem_set.all()])

    products_list.short_description = 'Товары'

    def save(self, *args, **kwargs):
        # Получаем текущее состояние объекта (если он уже существует)
        if self.pk:
            old_status = OrderTable.objects.get(pk=self.pk).status
        else:
            old_status = None

        # Сохраняем объект
        super().save(*args, **kwargs)

        # Проверяем изменения статуса
        if old_status != self.status:
            if old_status == 'paid' and self.status in ['unpaid', 'canceled']:
                # Удаляем кассовый ордер при изменении статуса с оплачено на неоплачено/отменено
                self.cashreceiptorder_order.all().delete()

    class Meta:
        verbose_name = 'Стол заказов'
        verbose_name_plural = 'Столы заказов'


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
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    order = models.ForeignKey(OrderTable, on_delete=models.CASCADE, related_name='cashreceiptorder_order',
                             verbose_name='Заказ', editable=False)
    sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма", editable=False)

    def __str__(self):
        return f"{self.date}, {self.order}, {self.sum}"

    def save(self, *args, **kwargs):
        if self.order.status != "paid":
            raise ValueError("Кассовый ордер можно создать только для оплаченного заказа.")

        if self.sum <= 0:
            raise ValueError("Сумма кассового ордера должна быть больше 0.")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Приходный кассовый ордер"
        verbose_name_plural = "Приходные кассовые ордера"