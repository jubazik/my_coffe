from django.db import models
from directory.models import Products


class BalanceReport(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    remainder = models.IntegerField(verbose_name='Остаток')

    def __str__(self):
        return f"Товар: {self.product.name}, Остаток: {self.remainder}, {self.product.types} "

    class Meta:
        verbose_name = "Остаток Товара"
        verbose_name_plural = "Остатки Товаров"
# Create your models here.
