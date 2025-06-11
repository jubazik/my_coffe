from django.contrib import admin
from .models import Ak

@admin.register(Ak)
class AkAdmin(admin.ModelAdmin):
    list_display = ('view', 'name_firma', 'inn', 'email', 'director')
    list_filter = ('view', 'inn', 'email', 'director')





# Register your models here.
