from django.db import models
from django.db.models import Sum


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

    date = models.DateField(auto_now_add=True, verbose_name='Дата и время')
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
        # Проверяем, был ли изменён статус на "оплачено"
        if self.status == 'paid':
            # Проверяем, существует ли уже кассовый ордер для этого заказа
            if not hasattr(self, 'cashregister_order'):
                # Создаем кассовый ордер
                CashRegister.objects.create(
                    order=self,
                    sum=self.total_sum()
                )

        super().save(*args, **kwargs)


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

class CashRegister(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name="Дата")
    order = models.ForeignKey(OrderTable, on_delete=models.CASCADE, related_name='cashregister_table',
                             verbose_name='Заказ', editable=False)
    sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма", editable=False)

    def __str__(self):
        return f"{self.date}, {self.order}, {self.sum}"

    def save(self, *args, **kwargs):
        # Проверяем, что статус заказа "оплачено"
        if self.order.status == "paid":
            # Записываем общую сумму заказа
            self.sum = self.order.total_sum()
            super().save(*args, **kwargs)
        else:
            raise ValueError("Кассовый ордер можно создать только для оплаченного заказа.")

    class Meta:
        verbose_name = "Приходный кассовый ордер"
        verbose_name_plural = "Приходные кассовые ордера"