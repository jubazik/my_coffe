from django.db import models
from directory.models import Products, OrderItem
from counterparties.models import Counterparties


class AdmissionsProducts(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name="Дата")
    counterparty = models.ForeignKey(Counterparties, on_delete=models.PROTECT, verbose_name="Контрагент")
    product = models.ForeignKey(Products, on_delete=models.PROTECT, verbose_name='Товар')
    count = models.IntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    sum = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def __str__(self):
        return f"{self.date}, {self.counterparty}, {self.product}, {self.price}, {self.sum}"

    def save(self, *args, **kwargs):
        self.sum = self.price * self.count
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Поступление"
        # Create your models here.

