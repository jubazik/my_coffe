from django.db import models, transaction
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
        return f'{self.name}'

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
        ('unpaid', 'Не оплачен'),
        ('cash', 'Наличными'),
        ('without_cash', 'Без налич'),
        ('canceled', 'Отменено'),
    ]

    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время')
    table = models.ForeignKey('Table', on_delete=models.PROTECT, verbose_name='Стол')
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='unpaid',
        verbose_name='Статус'
    )

    class Meta:
        verbose_name = 'Стол заказов'
        verbose_name_plural = 'Столы заказов'

    def __str__(self):
        return f'Заказ {self.id} на столе {self.table}'

    def total_sum(self):
        return self.orderitem_set.aggregate(total=Sum('sum'))['total'] or 0

    def products_list(self):
        return ", ".join([item.product.name for item in self.orderitem_set.all()])

    def save(self, *args, **kwargs):
        # Получаем предыдущий статус, если заказ уже существует
        if self.pk:
            old_status = OrderTable.objects.get(pk=self.pk).status
        else:
            old_status = None

        super().save(*args, **kwargs)

        # Обрабатываем изменение статуса
        if old_status != self.status:
            self.handle_status_change(old_status)

    def handle_status_change(self, old_status):
        with transaction.atomic():
            if (self.status == 'cash' or self.status == 'without_cash') and self.orderitem_set.exists():
                self.cashreceiptorder_order.all().delete()
                PaymentOrder.objects.create(
                    order=self,
                    sum=self.total_sum()
                )
                CashReceiptOrder.objects.create(
                    order=self,
                    sum=self.total_sum()
                )
            elif old_status == 'cash':
                self.cashreceiptorder_order.all().delete()

            elif old_status == 'without_cash':
                self.paymentorder_order.all().delete()


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


class PaymentOrder(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    order = models.ForeignKey(OrderTable, on_delete=models.CASCADE, related_name='paymentorder_order',
                              verbose_name='Заказ', editable=False)
    sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма', editable=False)

    def __str__(self):
        return f"Дата:{self.date} стол заказа{self.order} Сумма{self.sum}"

    def save(self, *args, **kwargs):
        # Проверяем что заказ оплачен и есть товары
        if self.order.status != 'without_cash':
            raise ValueError("Платежное поручение можно создать только для оплаченного заказа")

        if not self.order.orderitem_set.exists():
            raise ValueError("Нельзя создать платежное поручение для заказа без товаров")

        # Автоматически считаем сумму
        self.sum = self.order.total_sum()

        # Проверяем что сумма положительная
        if self.sum <= 0:
            raise ValueError("Сумма платежное поручение должна быть больше 0")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Платежное поручение"
        verbose_name_plural = "Платежные поручении"


class CashReceiptOrder(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    order = models.ForeignKey(OrderTable, on_delete=models.CASCADE, related_name='cashreceiptorder_order',
                              verbose_name='Заказ', editable=False)
    sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма", editable=False)

    def __str__(self):
        return f"{self.date}, {self.order}, {self.sum}"

    def save(self, *args, **kwargs):
        # Проверяем что заказ оплачен и есть товары
        if self.order.status != 'cash':
            raise ValueError("Кассовый ордер можно создать только для оплаченного заказа")

        if not self.order.orderitem_set.exists():
            raise ValueError("Нельзя создать кассовый ордер для заказа без товаров")

        # Автоматически считаем сумму
        self.sum = self.order.total_sum()

        # Проверяем что сумма положительная
        if self.sum <= 0:
            raise ValueError("Сумма кассового ордера должна быть больше 0")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Приходный кассовый ордер"
        verbose_name_plural = "Приходные кассовые ордера"
