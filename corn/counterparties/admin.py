from django.contrib import admin
from .models import Counterpartys


class CounterpartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address')
    list_filter = ('name',)



admin.site.register(Counterpartys, CounterpartyAdmin)

# Register your models here.
