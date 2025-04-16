import logging

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .forms import OrderForm, DateRangeForm, ProductForm, OrderFilterForm, OrderItemForm
from .models import *
import datetime

logger = logging.getLogger(__name__)


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
            try:
                with transaction.atomic():
                    order = order_form.save(commit=False)
                    if 'status' not in order_form.cleaned_data or not order_form.cleaned_data['status']:
                        order.status = 'unpaid'
                    order.save()  # Сначала сохраняем заказ

                    # Создаём элементы заказа (OrderItem)
                    product_counts = {}
                    for key, value in request.POST.items():
                        if key.startswith('product-'):
                            try:
                                index = key.split('-')[1]
                                product_id = value
                                count = int(request.POST.get(f'count-{index}', 0))

                                if count > 0:
                                    product_counts[product_id] = product_counts.get(product_id, 0) + count
                            except (ValueError, IndexError):
                                continue

                    for product_id, count in product_counts.items():
                        product = Products.objects.get(id=product_id)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            count=count,
                            price=product.price,
                            sum=product.price * count
                        )

                    # Если статус "оплачено", создаём кассовый ордер после создания OrderItem
                    if order.status == 'paid':
                        CashReceiptOrder.objects.create(
                            order=order,
                            sum=order.total_sum()  # Теперь сумма будет правильной
                        )

                    messages.success(request, "Заказ создан!")
                    return redirect('order_list')
            except Exception as e:
                messages.error(request, f"Ошибка: {str(e)}")
    else:
        order_form = OrderForm()

    return render(request, 'directory/create_order.html', {
        'order_form': order_form,
        'products': products,
    })


def edit_order(request, order_id):
    order = get_object_or_404(OrderTable, id=order_id)

    if request.method == 'POST':
        order_form = OrderForm(request.POST, instance=order)
        if order_form.is_valid():
            try:
                with transaction.atomic():
                    # Сохраняем заказ (это вызовет save() модели)
                    order = order_form.save()

                    # Обновляем элементы заказа
                    order.orderitem_set.all().delete()

                    product_counts = {}
                    for key, value in request.POST.items():
                        if key.startswith('product-'):
                            try:
                                index = key.split('-')[1]
                                product_id = value
                                count = int(request.POST.get(f'count-{index}', 0))
                                if count > 0:
                                    product_counts[product_id] = product_counts.get(product_id, 0) + count
                            except (ValueError, IndexError):
                                continue

                    for product_id, count in product_counts.items():
                        product = Products.objects.get(id=product_id)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            count=count,
                            price=product.price,
                            sum=product.price * count
                        )

                    # Явно сохраняем заказ, чтобы триггернулся save()
                    order.save()

                    messages.success(request, "Заказ обновлен!")
                    return redirect('order_list')
            except Exception as e:
                messages.error(request, f"Ошибка: {str(e)}")


@permission_required('orders.view_order', raise_exception=True)
def order_list(request):
    today = timezone.now().date()

    # Инициализация форм с GET-параметрами
    filter_form = OrderFilterForm(request.GET or None)
    date_form = DateRangeForm(request.GET or None, initial={'start_date': today, 'end_date': today})

    # Обработка фильтров
    start_date = today
    end_date = today
    status_filter = None

    if filter_form.is_valid():
        status_filter = filter_form.cleaned_data.get('status')

    if date_form.is_valid():
        start_date = date_form.cleaned_data['start_date']
        end_date = date_form.cleaned_data['end_date']

    # Фильтрация заказов
    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    end_datetime = datetime.datetime.combine(end_date, datetime.time.max)

    orders = OrderTable.objects.filter(
        date__gte=start_datetime,
        date__lte=end_datetime
    ).order_by('-date')

    if status_filter:
        orders = orders.filter(status=status_filter)

    # Аннотация и агрегация
    orders = orders.prefetch_related('orderitem_set').annotate(
        total_sum=Sum('orderitem__sum')
    )
    total_paid_sum = orders.filter(status='paid').aggregate(
        total=Sum('total_sum')
    )['total'] or 0

    # Обработка изменения статуса
    if request.method == 'POST' and 'order_id' in request.POST:
        if not request.user.has_perm('orders.change_order'):
            return HttpResponseForbidden("У вас нет прав на изменение заказов")

        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        if new_status in dict(OrderTable.STATUS_CHOICES).keys():
            order = get_object_or_404(OrderTable, id=order_id)
            order.status = new_status
            order.save()
            return redirect('order_list')

    # Пагинация
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'date_form': date_form,
        'total_order_sum': total_paid_sum,
        'status_choices': OrderTable.STATUS_CHOICES,
    }
    return render(request, 'directory/order_list.html', context)
def mark_order_as_paid(request, order_id):
    try:
        order = get_object_or_404(OrderTable, id=order_id)
        if order.status != 'paid':
            with transaction.atomic():
                order.status = 'paid'
                order.save()
                logger.info(f"Заказ {order_id} оплачен")
                messages.success(request, "Заказ оплачен")
        else:
            messages.warning(request, "Заказ уже оплачен")
    except Exception as e:
        logger.error(f"Ошибка оплаты заказа {order_id}: {str(e)}")
        messages.error(request, "Ошибка оплаты")
    return redirect('order_list')


def cancel_order(request, order_id):
    order = get_object_or_404(OrderTable, id=order_id)
    if order.status == 'paid':
        order.status = 'canceled'
        order.save()
        messages.success(request, "Заказ отменен. ПКО удален.")
    elif order.status == 'unpaid':
        order.status = 'canceled'
        order.save()
        messages.success(request, "Неоплаченный заказ отменен.")
    else:
        messages.warning(request, "Заказ уже отменен.")
    return redirect('order_list')


@ensure_csrf_cookie
@require_POST
def update_order_status(request, order_id):
    if not request.user.has_perm('orders.change_order'):
        return HttpResponseForbidden("У вас нет прав на изменение заказов")

    order = get_object_or_404(OrderTable, id=order_id)
    new_status = request.POST.get('status')

    if new_status not in dict(OrderTable.STATUS_CHOICES).keys():
        return JsonResponse({'error': 'Недопустимый статус'}, status=400)

    order.status = new_status
    order.save()

    return JsonResponse({
        'success': True,
        'new_status': order.get_status_display(),
        'order_id': order_id
    })


def cashreceiptorderviews(request):
    pay_list = CashReceiptOrder.objects.all().order_by('-date')

    # Пагинация
    paginator = Paginator(pay_list, 10)  # 10 элементов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Общая сумма всех ПКО
    total_sum = pay_list.aggregate(total=Sum('sum'))['total'] or 0

    return render(request, 'directory/pko_list.html', {
        'page_obj': page_obj,
        'total_sum': total_sum
    })