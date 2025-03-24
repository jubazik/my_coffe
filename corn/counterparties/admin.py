from django.contrib import admin
from .models import Counterparties


class CounterpartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address')
    list_filter = ('name',)



admin.site.register(Counterparties, CounterpartyAdmin)

# Register your models here.
