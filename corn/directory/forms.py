from django import forms
from django.core.exceptions import ValidationError
from .models import OrderTable, OrderItem, Products  # Импортируем модели
#
# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = OrderTable  # Указываем модель, с которой связана форма
#         fields = ['table', 'status']  # Поля, которые будут отображаться в форме
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Добавляем CSS-классы для стилизации полей формы (опционально)
#         self.fields['table'].widget.attrs.update({'class': 'form-control'})
#         self.fields['status'].widget.attrs.update({'class': 'form-control'})

class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderTable
        fields = ['table', 'status']
# class OrderItemForm(forms.ModelForm):
#     class Meta:
#         model = OrderItem  # Указываем модель, с которой связана форма
#         fields = ['product', 'count']  # Поля, которые будут отображаться в форме
#
#     def clean_count(self):
#         count = self.cleaned_data['count']
#         if count < 1:
#             raise ValidationError("Количество не может быть меньше 1.")
#         return count
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Добавляем CSS-классы для стилизации полей формы (опционально)
#         self.fields['product'].widget.attrs.update({'class': 'form-control'})
#         self.fields['count'].widget.attrs.update({'class': 'form-control'})