from django.db import models
from directory.models import Products




class Counterpartys(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.IntegerField(verbose_name='Телефон', blank=True, null=True)
    address = models.CharField(verbose_name='Адрес', blank=True, null=True, max_length=100)

    def __str__(self):
        return f"{self.name}, {self.phone}, {self.address}"
    class Meta:
        verbose_name="Контрагент"
        verbose_name_plural='Контрагенты'


# Create your models here.
