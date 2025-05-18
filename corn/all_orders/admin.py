from django.contrib import admin
from .models import ExpenseOrder

@admin.register(ExpenseOrder)
class ExpenseOrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'recipient', 'amount', 'status', 'created_by')
    list_filter = ('status', 'date')
    search_fields = ('number', 'recipient', 'basis')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'approved_by')
    fieldsets = (
        (None, {
            'fields': ('number', 'date', 'status')
        }),
        ('Содержание', {
            'fields': ('recipient', 'amount', 'basis', 'comment')
        }),
        ('Системная информация', {
            'fields': ('created_by', 'approved_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)