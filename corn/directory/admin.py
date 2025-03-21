from django.contrib import admin
from .models import *


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('price', 'sum')

@admin.register(OrderTable)
class OrderTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'table',  'date', 'status')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'count', 'price', 'sum')
    readonly_fields = ('price', 'sum')

admin.site.register(Products)
admin.site.register(Category)
admin.site.register(Type)
admin.site.register(Table)
