from django import forms
from django.core.exceptions import ValidationError
from .models import OrderTable, OrderItem, Products  # Импортируем модели
from django.utils import timezone



#

class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderTable
        fields = ['table', 'status']
        widgets = {
            'table': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    from django.utils import timezone

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and not timezone.is_aware(date):
            return timezone.make_aware(date)
        return date


class OrderFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'Все статусы'),
        *OrderTable.STATUS_CHOICES
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)


class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderTable  # Указываем модель, с которой связана форма
        fields = ['table', 'status']  # Поля, которые будут отображаться в форме

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем CSS-классы для стилизации полей формы (опционально)
        self.fields['table'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})


#

class OrderDetailForm(forms.ModelForm):
    class Meta:
        model = OrderTable
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'form-control'})


class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['name', 'description', 'price', 'category', 'type']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['name'].widget.attrs.update({'class': 'form-control'})
            self.fields['description'].widget.attrs.update({'class': 'form-control'})
            self.fields['price'].widget.attrs.update({'class': 'form-control'})
            self.fields['category'].widget.attrs.update({'class': 'form-control'})
            self.fields['type'].widget.attrs.update({'class': 'form-control'})


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem  # Указываем модель, с которой связана форма
        fields = ['product', 'count']  # Поля, которые будут отображаться в форме

    def clean_count(self):
        count = self.cleaned_data['count']
        if count < 1:
            raise ValidationError("Количество не может быть меньше 1.")
        return count

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем CSS-классы для стилизации полей формы (опционально)
        self.fields['product'].widget.attrs.update({'class': 'form-control'})
        self.fields['count'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})
        self.fields['sum'].widget.attrs.update({'class': 'form-control'})


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )
