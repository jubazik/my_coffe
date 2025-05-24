from django.contrib import admin
from .models import AdmissionsProducts

@admin.register(AdmissionsProducts)
class AdmissionsProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'counterparty', 'product', 'count')
    list_filter = ('date', 'counterparty', 'product')

