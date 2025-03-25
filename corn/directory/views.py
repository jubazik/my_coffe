from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg
from django.utils import timezone
from django.contrib import messages
from .forms import OrderForm, DateRangeForm, ProductForm
from .models import Products, OrderTable, OrderItem
import datetime


def created_products_list(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Продукт успешно создан")
            return redirect("product_list")
    else:
        form = ProductForm()

    return render(request, "directory/created_products_list.html", {"form": form})


def product_list(request):
    """Отображение списка товаров."""
    products = Products.objects.all()
    return render(request, 'directory/product_list.html', {'products': products})


def create_order(request):
    products = Products.objects.all()
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save()

            # Словарь для хранения товаров и их количества
            product_counts = {}

            # Обработка данных POST
            for key, value in request.POST.items():
                if key.startswith('product-'):
                    try:
                        index = key.split('-')[1]
                        product_id = value
                        count = request.POST.get(f'count-{index}')

                        # Проверка наличия product_id и count
                        if not product_id or not count:
                            messages.error(request, "Не все поля товара заполнены.")
                            continue

                        # Преобразование count в число
                        count = int(count)
                        if count <= 0:
                            messages.error(request, f"Количество товара должно быть больше 0.")
                            continue

                        # Добавление товара в словарь
                        if product_id in product_counts:
                            product_counts[product_id] += count
                        else:
                            product_counts[product_id] = count

                    except (IndexError, ValueError) as e:
                        messages.error(request, f"Ошибка обработки данных: {str(e)}")
                        continue

            # Создание OrderItem для каждого товара
            for product_id, count in product_counts.items():
                try:
                    product = Products.objects.get(id=product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        count=count,
                        price=product.price,
                        sum=product.price * count
                    )
                except Products.DoesNotExist:
                    messages.error(request, f"Товар с ID {product_id} не найден.")

            if not messages.get_messages(request):
                messages.success(request, "Заказ успешно создан.")
                return redirect('order_list')
    else:
        order_form = OrderForm()

    return render(request, 'directory/create_order.html', {
        'order_form': order_form,
        'products': products,
    })


def edit_order(request, order_id):
    # Получаем заказ или возвращаем 404
    order = get_object_or_404(OrderTable, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    products = Products.objects.all()

    if request.method == 'POST':
        order_form = OrderForm(request.POST, instance=order)
        if order_form.is_valid():
            # Сохраняем заказ
            order = order_form.save()

            # Удаляем старые OrderItem
            order_items.delete()

            # Словарь для хранения товаров и их количества
            product_counts = {}

            # Обработка данных POST
            for key, value in request.POST.items():
                if key.startswith('product-'):
                    try:
                        index = key.split('-')[1]
                        product_id = value
                        count = request.POST.get(f'count-{index}')

                        # Проверка наличия product_id и count
                        if not product_id or not count:
                            messages.error(request, "Не все поля товара заполнены.")
                            continue

                        # Преобразование count в число
                        count = int(count)
                        if count <= 0:
                            messages.error(request, f"Количество товара должно быть больше 0.")
                            continue

                        # Добавление товара в словарь
                        if product_id in product_counts:
                            product_counts[product_id] += count
                        else:
                            product_counts[product_id] = count

                    except (IndexError, ValueError) as e:
                        messages.error(request, f"Ошибка обработки данных: {str(e)}")
                        continue

            # Создание OrderItem для каждого товара
            order_items_to_create = []
            for product_id, count in product_counts.items():
                try:
                    product = Products.objects.get(id=product_id)
                    order_items_to_create.append(
                        OrderItem(
                            order=order,
                            product=product,
                            count=count,
                            price=product.price,
                            sum=product.price * count
                        )
                    )
                except Products.DoesNotExist:
                    messages.error(request, f"Товар с ID {product_id} не найден.")

            # Массовое создание OrderItem
            if order_items_to_create:
                OrderItem.objects.bulk_create(order_items_to_create)

            if not messages.get_messages(request):
                messages.success(request, "Заказ успешно обновлен.")
                return redirect('edit_order', order_id=order.id)
    else:
        order_form = OrderForm(instance=order)

    return render(request, 'directory/edit_order.html', {
        'order_form': order_form,
        'products': products,
        'order_items': order_items,
    })


def order_list(request):
    # Получаем текущую дату для предзаполнения формы
    today = timezone.now().date()

    # Инициализируем переменные для фильтрации
    start_date = today
    end_date = today

    # Если форма фильтрации отправлена
    if request.method == 'POST' and 'date_range_form' in request.POST:
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
    else:
        # Если форма фильтрации не отправлена, используем текущую дату
        form = DateRangeForm(initial={'start_date': today, 'end_date': today})

    # Фильтруем заказы по диапазону дат
    orders = OrderTable.objects.filter(date__range=(start_date, end_date)).annotate(total_sum=Sum('orderitem__sum'))
    total_order_sum = orders.aggregate(total=Sum("total_sum"))['total'] or 0

    # Обработка формы редактирования статуса
    if request.method == 'POST' and 'order_id' in request.POST:
        order_id = request.POST.get('order_id')
        order = get_object_or_404(OrderTable, id=order_id)
        new_status = request.POST.get('status')  # Получаем новый статус из формы
        order.status = new_status  # Обновляем статус
        order.save()  # Сохраняем изменения
        return redirect('order_list')  # Перенаправляем на список заказов
    # Перенаправляем на список заказов
    status_choices = OrderTable.STATUS_CHOICES

    return render(request, 'directory/order_list.html', {
        'orders': orders,
        'total_order_sum': total_order_sum,
        'form': form,  # Форма фильтрации по дате
        'start_date': start_date,
        'end_date': end_date,
        'status_choices': status_choices,
    })


def update_order_status(request, order_id, status):
    """Изменение статуса заказа."""
    order = get_object_or_404(OrderTable, id=order_id)
    order.status = status
    order.save()
    return redirect('order_list')

# Create your views here.
